import { getApiBaseUrl } from "./config";

export type ChatRequest = {
  question: string;
  session_id?: string | null;
  include_tts?: boolean;
};

export type AudioMetadata = {
  audio_url?: string | null;
  audio_path?: string | null;
  duration_ms?: number | null;
  provider: string;
};

export type RetrievalHit = {
  id: string;
  score: number;
  content_type: string;
  source_file: string;
  section_title: string;
  section_level: number;
  text_preview: string;
  metadata: Record<string, unknown>;
};

export type SourceCitation = {
  chunk_id: string;
  source_file: string;
  section_title: string;
  content_type: string;
  score: number;
  excerpt: string;
};

export type ChatResponse = {
  answer: string;
  confidence: "high" | "medium" | "low";
  grounding_note?: string | null;
  sources: SourceCitation[];
  session_id?: string | null;
  audio?: AudioMetadata | null;
  /** Present when Voice mode asked for TTS but synthesis failed */
  tts_error?: string | null;
  retrieval?: RetrievalHit[];
  retrieval_error?: string | null;
};

export type VoiceChatResponse = ChatResponse & {
  transcript: string;
  stt_provider: string;
  stt_language?: string | null;
};

export type VoiceChunkTranscriptResponse = {
  transcript: string;
  stt_provider: string;
  stt_language?: string | null;
};

export class ChatApiError extends Error {
  constructor(
    message: string,
    public status?: number,
  ) {
    super(message);
    this.name = "ChatApiError";
  }
}

export async function sendChatMessage(body: ChatRequest): Promise<ChatResponse> {
  const base = getApiBaseUrl();
  const res = await fetch(`${base}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question: body.question,
      session_id: body.session_id ?? undefined,
      include_tts: body.include_tts === true,
    }),
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const text = await res.text();
      if (text) detail = text.slice(0, 200);
    } catch {
      /* ignore */
    }
    throw new ChatApiError(detail || "Request failed", res.status);
  }

  return res.json() as Promise<ChatResponse>;
}

/** Readable assistant text while the model is still streaming JSON (`"answer":"...`). */
function streamingDisplayFromPartialJson(buffer: string): string {
  const m = /"answer"\s*:\s*"/.exec(buffer);
  if (!m) return "";
  let i = m.index + m[0].length;
  let out = "";
  let escaped = false;
  for (; i < buffer.length; i++) {
    const c = buffer[i];
    if (escaped) {
      if (c === "n") out += "\n";
      else if (c === "t") out += "\t";
      else if (c === "r") out += "\r";
      else if (c === '"') out += '"';
      else if (c === "\\") out += "\\";
      else out += c;
      escaped = false;
      continue;
    }
    if (c === "\\") {
      escaped = true;
      continue;
    }
    if (c === '"') break;
    out += c;
  }
  return out;
}

export function streamingAssistantPreview(rawBuffer: string): string {
  const t = rawBuffer.trimStart();
  if (t.startsWith("{")) return streamingDisplayFromPartialJson(rawBuffer);
  return rawBuffer;
}

function normalizeStreamCompletePayload(raw: unknown): ChatResponse {
  if (!raw || typeof raw !== "object") {
    throw new ChatApiError("Invalid stream response");
  }
  const o = raw as Record<string, unknown>;
  const conf = o.confidence;
  const confidence: ChatResponse["confidence"] =
    conf === "high" || conf === "medium" || conf === "low" ? conf : "medium";
  return {
    answer: String(o.answer ?? ""),
    confidence,
    grounding_note: (o.grounding_note as string | null | undefined) ?? null,
    sources: (o.sources as ChatResponse["sources"]) ?? [],
    session_id: (o.session_id as string | null | undefined) ?? null,
    audio: (o.audio as ChatResponse["audio"]) ?? null,
    tts_error: (o.tts_error as string | null | undefined) ?? null,
    retrieval: (o.retrieval as ChatResponse["retrieval"]) ?? [],
    retrieval_error: (o.retrieval_error as string | null | undefined) ?? null,
  };
}

export type ChatStreamHandlers = {
  onPreview: (visibleText: string) => void;
  onComplete: (response: ChatResponse) => void;
  onError: (message: string) => void;
  signal?: AbortSignal;
};

export async function sendChatMessageStream(
  body: ChatRequest,
  handlers: ChatStreamHandlers,
): Promise<void> {
  const base = getApiBaseUrl();
  const res = await fetch(`${base}/api/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
    body: JSON.stringify({
      question: body.question,
      session_id: body.session_id ?? undefined,
      include_tts: body.include_tts === true,
    }),
    signal: handlers.signal,
  });

  if (!res.ok || !res.body) {
    let detail = res.statusText;
    try {
      const text = await res.text();
      if (text) detail = text.slice(0, 200);
    } catch {
      /* ignore */
    }
    throw new ChatApiError(detail || "Request failed", res.status);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let sseBuffer = "";
  let rawAccumulated = "";

  const processEvent = (rawEvent: string): boolean => {
    const dataLine = rawEvent.split("\n").find((l) => l.startsWith("data:"));
    if (!dataLine) return false;
    const jsonText = dataLine.replace(/^data:\s?/, "").trim();
    if (!jsonText) return false;
    let data: Record<string, unknown>;
    try {
      data = JSON.parse(jsonText) as Record<string, unknown>;
    } catch {
      handlers.onError("Bad SSE payload from API");
      return true;
    }

    if (data.error != null && data.done) {
      handlers.onError(String(data.error));
      return true;
    }

    if (typeof data.token === "string") {
      rawAccumulated += data.token;
      handlers.onPreview(streamingAssistantPreview(rawAccumulated));
    }

    if (data.done === true) {
      try {
        handlers.onComplete(normalizeStreamCompletePayload(data));
      } catch (e) {
        handlers.onError(e instanceof Error ? e.message : "Stream completion failed");
      }
      return true;
    }
    return false;
  };

  for (;;) {
    const { done, value } = await reader.read();
    if (done) {
      throw new ChatApiError("Stream ended before completion");
    }
    sseBuffer += decoder.decode(value, { stream: true });
    for (;;) {
      const sep = sseBuffer.indexOf("\n\n");
      if (sep < 0) break;
      const rawEvent = sseBuffer.slice(0, sep);
      sseBuffer = sseBuffer.slice(sep + 2);
      if (processEvent(rawEvent)) {
        return;
      }
    }
  }
}

export async function sendVoiceMessage(
  audioBlob: Blob,
  sessionId?: string | null,
): Promise<VoiceChatResponse> {
  const base = getApiBaseUrl();
  const form = new FormData();
  form.append("audio", audioBlob, "voice-input.webm");
  if (sessionId) {
    form.append("session_id", sessionId);
  }

  const res = await fetch(`${base}/api/voice/chat`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const maybeJson = (await res.json()) as { detail?: string };
      if (maybeJson?.detail) detail = maybeJson.detail;
    } catch {
      /* ignore */
    }
    throw new ChatApiError(detail || "Voice request failed", res.status);
  }

  return res.json() as Promise<VoiceChatResponse>;
}

export async function transcribeVoiceChunk(
  audioBlob: Blob,
): Promise<VoiceChunkTranscriptResponse> {
  const base = getApiBaseUrl();
  const form = new FormData();
  form.append("audio", audioBlob, "voice-chunk.webm");

  const res = await fetch(`${base}/api/voice/transcribe`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const maybeJson = (await res.json()) as { detail?: string };
      if (maybeJson?.detail) detail = maybeJson.detail;
    } catch {
      /* ignore */
    }
    throw new ChatApiError(detail || "Chunk transcription failed", res.status);
  }

  return res.json() as Promise<VoiceChunkTranscriptResponse>;
}

/** Max characters sent to TTS to keep voice replies responsive. Full answer still shown in UI. */
export const TTS_VOICE_CHAR_BUDGET = 500;

export function textForVoiceTts(full: string): string {
  const t = full.trim();
  if (t.length <= TTS_VOICE_CHAR_BUDGET) return t;
  return `${t.slice(0, TTS_VOICE_CHAR_BUDGET - 1)}…`;
}

export async function synthesizeTts(text: string): Promise<AudioMetadata | null> {
  const base = getApiBaseUrl();
  const res = await fetch(`${base}/api/tts`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "audio/wav",
    },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) {
    return null;
  }
  const ct = (res.headers.get("content-type") || "").toLowerCase();

  // JSON metadata path (mock / legacy / Accept not honored). Must branch before reading body as WAV.
  if (ct.includes("application/json")) {
    const data = (await res.json()) as {
      success: boolean;
      audio_url?: string | null;
      audio_path?: string | null;
      duration_ms?: number | null;
      provider?: string;
    };
    if (!data.success) return null;
    return {
      audio_url: data.audio_url ?? null,
      audio_path: data.audio_path ?? null,
      duration_ms: data.duration_ms ?? null,
      provider: data.provider ?? "unknown",
    };
  }

  // Raw WAV bytes — always attach an explicit audio MIME so <audio> accepts the blob (empty type → NotSupportedError).
  const buf = await res.arrayBuffer();
  if (buf.byteLength === 0) {
    return null;
  }
  const mimeFromHeader = ct.split(";")[0].trim();
  const blobType =
    mimeFromHeader.startsWith("audio/") || mimeFromHeader === "application/octet-stream"
      ? mimeFromHeader === "application/octet-stream"
        ? "audio/wav"
        : mimeFromHeader
      : "audio/wav";
  const blob = new Blob([buf], { type: blobType });
  const url = URL.createObjectURL(blob);
  return {
    audio_url: url,
    audio_path: null,
    duration_ms: null,
    provider: "wav-binary",
  };
}
