import { getApiBaseUrl } from "./config";

export type ChatRequest = {
  question: string;
  session_id?: string | null;
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
  retrieval?: RetrievalHit[];
  retrieval_error?: string | null;
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
