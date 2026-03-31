"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import type { ChatResponse } from "@/lib/api";
import {
  ChatApiError,
  sendChatMessage,
  sendVoiceMessage,
  transcribeVoiceChunk,
} from "@/lib/api";
import { getApiBaseUrl } from "@/lib/config";

import { AssistantMessage } from "./assistant-message";
import { ChatLoadingSkeleton } from "./chat-loading";
import { ChatInput } from "./chat-input";
import { MessageBubble } from "./message-bubble";

const CHAT_EMPTY_STATE_STARTERS = [
  "Give me a quick summary of Sai for a backend hiring manager.",
  "What production AI and backend systems experience stands out most?",
  "What roles and team environments is Sai targeting right now?",
] as const;

const VOICE_EMPTY_STATE_PROMPTS = [
  "Give me a quick summary of your background.",
  "What backend and AI projects are most relevant for this role?",
  "What kind of teams and roles is Sai targeting next?",
] as const;

export type UserMessage = {
  id: string;
  role: "user";
  content: string;
};

export type AssistantChatMessage = {
  id: string;
  role: "assistant";
  payload: ChatResponse;
  /** Voice mode: audio is fetched after chat returns (faster perceived reply). */
  voicePending?: boolean;
  voiceError?: string | null;
};

export type ChatMessage = UserMessage | AssistantChatMessage;

function nextId() {
  return crypto.randomUUID();
}

type ChatPanelProps = {
  className?: string;
  initialMode?: InteractionMode;
};

type InteractionMode = "chat" | "voice";

export function ChatPanel({ className = "", initialMode = "chat" }: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mode, setMode] = useState<InteractionMode>(initialMode);
  const [isRecording, setIsRecording] = useState(false);
  const [isVoiceSubmitting, setIsVoiceSubmitting] = useState(false);
  const [liveTranscript, setLiveTranscript] = useState("");
  const [isTranscribingLive, setIsTranscribingLive] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);
  const liveChunkQueueRef = useRef(Promise.resolve());
  const bottomRef = useRef<HTMLDivElement>(null);
  const chatInputRef = useRef<HTMLTextAreaElement>(null);
  const voiceActionButtonRef = useRef<HTMLButtonElement>(null);

  const scrollToBottom = useCallback(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading, scrollToBottom]);

  useEffect(() => {
    return () => {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
        mediaRecorderRef.current.stop();
      }
      streamRef.current?.getTracks().forEach((t) => t.stop());
    };
  }, []);

  useEffect(() => {
    setMode(initialMode);
  }, [initialMode]);

  useEffect(() => {
    if (mode !== "chat") return;
    if (typeof window === "undefined") return;
    if (window.location.hash !== "#chat") return;

    const timer = window.setTimeout(() => {
      chatInputRef.current?.focus();
    }, 120);

    return () => {
      window.clearTimeout(timer);
    };
  }, [mode, messages.length]);

  useEffect(() => {
    if (mode !== "voice") return;
    if (typeof window === "undefined") return;
    if (window.location.hash !== "#chat") return;

    const timer = window.setTimeout(() => {
      voiceActionButtonRef.current?.focus();
    }, 140);

    return () => {
      window.clearTimeout(timer);
    };
  }, [mode]);

  const voiceStateLabel = isVoiceSubmitting
    ? "Processing"
    : isRecording
      ? isTranscribingLive
        ? "Listening (live transcript)"
        : "Listening"
      : "Idle";

  const voiceStateHelp = isVoiceSubmitting
    ? "Transcribing and generating a grounded response."
    : isRecording
      ? "Speak naturally. Press the mic again when you finish speaking."
      : "Tap the mic to start talking.";

  const reset = useCallback(() => {
    setMessages([]);
    setSessionId(null);
    setError(null);
    setLiveTranscript("");
  }, []);

  const send = useCallback(
    async (question: string) => {
      setError(null);
      const userMsg: UserMessage = { id: nextId(), role: "user", content: question };
      setMessages((prev) => [...prev, userMsg]);
      setLoading(true);

      try {
        const res = await sendChatMessage({
          question,
          session_id: sessionId,
          include_tts: false,
        });
        if (res.session_id) setSessionId(res.session_id);
        const assistantMsg: AssistantChatMessage = { id: nextId(), role: "assistant", payload: res };
        setMessages((prev) => [...prev, assistantMsg]);
      } catch (e) {
        const msg =
          e instanceof ChatApiError
            ? e.message
            : e instanceof Error
              ? `${e.message} (API: ${getApiBaseUrl()})`
              : `Something went wrong. Check that the API is running at ${getApiBaseUrl()}.`;
        setError(msg);
      } finally {
        setLoading(false);
      }
    },
    [sessionId],
  );

  const startVoiceCapture = useCallback(async () => {
    if (loading || isVoiceSubmitting || isRecording) return;
    setError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const recorder = new MediaRecorder(stream);
      chunksRef.current = [];
      recorder.ondataavailable = (event: BlobEvent) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
          const chunk = event.data;
          liveChunkQueueRef.current = liveChunkQueueRef.current.then(async () => {
            setIsTranscribingLive(true);
            try {
              const live = await transcribeVoiceChunk(chunk);
              const text = (live.transcript || "").trim();
              if (text) {
                setLiveTranscript((prev) => (prev ? `${prev} ${text}` : text));
              }
            } catch {
              // Ignore intermittent chunk failures; final transcript still runs at stop.
            } finally {
              setIsTranscribingLive(false);
            }
          });
        }
      };
      recorder.start(1200);
      mediaRecorderRef.current = recorder;
      setIsRecording(true);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Microphone permission denied.";
      setError(`Voice capture failed: ${msg}`);
      streamRef.current?.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
  }, [isRecording, isVoiceSubmitting, loading]);

  const stopVoiceCaptureAndSend = useCallback(async () => {
    const recorder = mediaRecorderRef.current;
    if (!recorder || recorder.state === "inactive") {
      return;
    }

    setIsVoiceSubmitting(true);

    const blobPromise = new Promise<Blob>((resolve) => {
      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: recorder.mimeType || "audio/webm" });
        resolve(blob);
      };
    });

    recorder.stop();
    setIsRecording(false);
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;

    try {
      const audioBlob = await blobPromise;
      await liveChunkQueueRef.current;
      const res = await sendVoiceMessage(audioBlob, sessionId);

      if (res.session_id) setSessionId(res.session_id);

      const userMsg: UserMessage = {
        id: nextId(),
        role: "user",
        content: res.transcript || liveTranscript,
      };
      const assistantMsg: AssistantChatMessage = {
        id: nextId(),
        role: "assistant",
        payload: res,
        voicePending: false,
        voiceError: res.tts_error ?? null,
      };
      setMessages((prev) => [...prev, userMsg, assistantMsg]);
    } catch (e) {
      const msg =
        e instanceof ChatApiError
          ? e.message
          : e instanceof Error
            ? `${e.message} (API: ${getApiBaseUrl()})`
            : `Voice request failed. Check API at ${getApiBaseUrl()}.`;
      setError(msg);
    } finally {
      setIsVoiceSubmitting(false);
      mediaRecorderRef.current = null;
      chunksRef.current = [];
      setLiveTranscript("");
      setIsTranscribingLive(false);
      liveChunkQueueRef.current = Promise.resolve();
    }
  }, [sessionId, liveTranscript]);

  return (
    <section
      className={`flex flex-col rounded-2xl border border-zinc-200/80 bg-white/92 shadow-[0_24px_40px_-28px_rgba(15,23,42,0.28)] dark:border-zinc-800 dark:bg-zinc-950 ${className}`}
      aria-labelledby="chat-heading"
    >
      <div className="flex flex-col gap-3 border-b border-zinc-200/70 px-4 py-4 sm:flex-row sm:items-start sm:justify-between sm:px-5 dark:border-zinc-800">
        <div className="min-w-0 flex-1">
          <h2 id="chat-heading" className="text-lg font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
            {mode === "voice" ? "Talk with the assistant" : "Ask the assistant"}
          </h2>
          <p className="mt-0.5 text-xs text-zinc-500 dark:text-zinc-400">
            {mode === "voice"
              ? "Voice workflow: speak your question, then receive grounded text and audio response."
              : "Grounded on portfolio data · cite sources below each reply"}
          </p>
          <div
            className="mt-3 inline-flex rounded-full border border-zinc-200/90 bg-zinc-100/80 p-1 dark:border-zinc-700 dark:bg-zinc-900"
            role="group"
            aria-label="Interaction mode"
          >
            <button
              type="button"
              onClick={() => setMode("chat")}
              disabled={loading || isRecording || isVoiceSubmitting}
              className={`rounded-full px-3.5 py-1.5 text-xs font-semibold transition-colors ${
                mode === "chat"
                  ? "bg-white text-zinc-900 shadow-sm ring-1 ring-sky-200 dark:bg-zinc-800 dark:text-zinc-50"
                  : "text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100"
              }`}
            >
              Text chat
            </button>
            <button
              type="button"
              onClick={() => setMode("voice")}
              disabled={loading || isVoiceSubmitting}
              className={`rounded-full px-3.5 py-1.5 text-xs font-semibold transition-colors ${
                mode === "voice"
                  ? "bg-white text-zinc-900 shadow-sm ring-1 ring-sky-200 dark:bg-zinc-800 dark:text-zinc-50"
                  : "text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100"
              }`}
            >
              Voice
            </button>
          </div>
        </div>
        <button
          type="button"
          onClick={reset}
          disabled={loading || isRecording || isVoiceSubmitting}
          className="shrink-0 rounded-lg border border-zinc-200/90 bg-white px-3 py-1.5 text-xs font-medium text-zinc-700 transition-colors hover:border-sky-300 hover:bg-sky-50/60 disabled:opacity-40 dark:border-zinc-600 dark:bg-zinc-900 dark:text-zinc-200 dark:hover:bg-zinc-800"
        >
          Reset chat
        </button>
      </div>

      <div className="min-h-[min(22rem,45vh)] max-h-[min(28rem,50vh)] space-y-4 overflow-y-auto px-4 py-4 sm:px-5">
        {messages.length === 0 && !loading && (
          mode === "chat" ? (
            <div className="rounded-xl border border-zinc-200/80 bg-zinc-50/75 p-4 shadow-[0_12px_24px_-22px_rgba(15,23,42,0.32)] dark:border-zinc-700/80 dark:bg-zinc-900/40">
              <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
                First question
              </p>
              <p className="mt-1 text-sm leading-relaxed text-zinc-700 dark:text-zinc-300">
                Ask one focused question to get a concise summary first, then drill into
                projects, scope, and impact.
              </p>
              <div className="mt-3 flex flex-wrap gap-2">
                {CHAT_EMPTY_STATE_STARTERS.map((starter) => (
                  <button
                    key={starter}
                    type="button"
                    onClick={() => void send(starter)}
                    className="rounded-full border border-zinc-200/90 bg-white px-3 py-1.5 text-xs font-medium text-zinc-700 transition-colors hover:border-sky-300 hover:bg-sky-50/70 dark:border-zinc-600 dark:bg-zinc-950 dark:text-zinc-200 dark:hover:border-zinc-500 dark:hover:bg-zinc-900"
                  >
                    {starter}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="rounded-xl border border-zinc-200/80 bg-zinc-50/75 p-4 shadow-[0_12px_24px_-22px_rgba(15,23,42,0.32)] dark:border-zinc-700/80 dark:bg-zinc-900/40">
              <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
                First voice question
              </p>
              <p className="mt-1 text-sm leading-relaxed text-zinc-700 dark:text-zinc-300">
                Tap the mic and ask one concise question. You will get a transcript,
                grounded answer, and voice playback when available.
              </p>
              <ul className="mt-3 space-y-1.5 text-xs text-zinc-600 dark:text-zinc-400">
                {VOICE_EMPTY_STATE_PROMPTS.map((prompt) => (
                  <li key={prompt} className="rounded-lg border border-zinc-200/80 bg-white/95 px-3 py-2 dark:border-zinc-700/80 dark:bg-zinc-950/50">
                    {prompt}
                  </li>
                ))}
              </ul>
            </div>
          )
        )}
        {mode === "voice" && isRecording ? (
            <div className="rounded-xl border border-sky-200/80 bg-sky-50/60 px-4 py-3 shadow-[0_14px_30px_-24px_rgba(14,116,144,0.5)] dark:border-zinc-700/80 dark:bg-zinc-950/70">
            <p className="text-[11px] font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
                You are speaking
            </p>
            {liveTranscript ? (
              <MessageBubble role="user">
                <p className="whitespace-pre-wrap text-sm leading-relaxed">{liveTranscript}</p>
                <p className="mt-1 text-[11px] opacity-70">
                  {isTranscribingLive ? "Live transcribing..." : "Listening..."}
                </p>
              </MessageBubble>
            ) : (
              <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-300">Listening... transcript will appear here.</p>
            )}
          </div>
        ) : null}
        {messages.map((m) =>
          m.role === "user" ? (
            <MessageBubble key={m.id} role="user">
              <p className="whitespace-pre-wrap text-sm leading-relaxed">{m.content}</p>
            </MessageBubble>
          ) : (
            <div key={m.id} className="flex justify-start">
              <AssistantMessage
                payload={m.payload}
                voicePending={m.role === "assistant" ? m.voicePending : false}
                voiceError={m.role === "assistant" ? m.voiceError : null}
                hideAudioControls={mode === "voice"}
              />
            </div>
          ),
        )}
        {loading && (
          <div className="flex justify-start">
            <ChatLoadingSkeleton />
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {error && (
        <p className="border-t border-zinc-100 px-4 py-2 text-sm text-red-700 dark:border-zinc-800 dark:text-red-400 sm:px-5" role="alert">
          {error}
        </p>
      )}

      <div className="border-t border-zinc-200/70 p-4 sm:p-5 dark:border-zinc-800">
        {mode === "chat" ? (
          <ChatInput
            onSend={(text) => void send(text)}
            disabled={loading || isVoiceSubmitting}
            autoFocus={mode === "chat" && messages.length === 0}
            textareaRef={chatInputRef}
          />
        ) : (
          <div className="flex items-center justify-between gap-3 rounded-xl border border-zinc-200/90 bg-zinc-50/75 p-3 shadow-[0_12px_24px_-22px_rgba(15,23,42,0.3)] dark:border-zinc-700/80 dark:bg-zinc-900/40">
            <div className="min-w-0">
              <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
                Voice mode
              </p>
              <p className="mt-0.5 text-sm font-medium text-zinc-900 dark:text-zinc-100">{voiceStateLabel}</p>
              <p className="mt-0.5 text-xs text-zinc-600 dark:text-zinc-400">{voiceStateHelp}</p>
            </div>
            <div className="flex items-center gap-2">
              <button
                ref={voiceActionButtonRef}
                type="button"
                onClick={() => {
                  if (isRecording) {
                    void stopVoiceCaptureAndSend();
                  } else {
                    void startVoiceCapture();
                  }
                }}
                disabled={loading || isVoiceSubmitting}
                className={`flex h-10 w-10 items-center justify-center rounded-full text-white disabled:opacity-40 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-500 ${
                  isRecording ? "bg-red-600 hover:bg-red-500" : "bg-sky-600 hover:bg-sky-500"
                }`}
                aria-label={isRecording ? "Stop recording" : "Start recording"}
              >
                {isRecording ? (
                  <svg className="h-4 w-4" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                    <rect x="7" y="7" width="10" height="10" rx="1.5" />
                  </svg>
                ) : (
                  <svg className="h-4 w-4" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                    <path d="M12 15a3 3 0 0 0 3-3V7a3 3 0 0 0-6 0v5a3 3 0 0 0 3 3Z" />
                    <path d="M5 11a1 1 0 1 1 2 0 5 5 0 0 0 10 0 1 1 0 1 1 2 0 7 7 0 0 1-6 6.92V21h2a1 1 0 1 1 0 2H9a1 1 0 1 1 0-2h2v-3.08A7 7 0 0 1 5 11Z" />
                  </svg>
                )}
              </button>
              <span className="text-xs text-zinc-500 dark:text-zinc-400">
                {isVoiceSubmitting
                  ? "Processing audio and drafting response..."
                  : isRecording
                    ? isTranscribingLive
                      ? "Recording + transcribing live..."
                      : "Recording..."
                      : "Tap mic to speak"}
              </span>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
