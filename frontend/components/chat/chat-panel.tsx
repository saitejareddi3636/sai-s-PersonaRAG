"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import type { ChatResponse } from "@/lib/api";
import { ChatApiError, sendChatMessage } from "@/lib/api";

import { AssistantMessage } from "./assistant-message";
import { ChatLoadingSkeleton } from "./chat-loading";
import { ChatInput } from "./chat-input";
import { MessageBubble } from "./message-bubble";
import { QuestionPackPicker } from "./question-pack-picker";

export type UserMessage = {
  id: string;
  role: "user";
  content: string;
};

export type AssistantChatMessage = {
  id: string;
  role: "assistant";
  payload: ChatResponse;
};

export type ChatMessage = UserMessage | AssistantChatMessage;

function nextId() {
  return crypto.randomUUID();
}

type ChatPanelProps = {
  className?: string;
};

export function ChatPanel({ className = "" }: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = useCallback(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading, scrollToBottom]);

  const reset = useCallback(() => {
    setMessages([]);
    setSessionId(null);
    setError(null);
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
        });
        if (res.session_id) setSessionId(res.session_id);
        const assistantMsg: AssistantChatMessage = {
          id: nextId(),
          role: "assistant",
          payload: res,
        };
        setMessages((prev) => [...prev, assistantMsg]);
      } catch (e) {
        const msg =
          e instanceof ChatApiError
            ? e.message
            : "Something went wrong. Check that the API is running.";
        setError(msg);
      } finally {
        setLoading(false);
      }
    },
    [sessionId],
  );

  return (
    <section
      className={`flex flex-col rounded-2xl border border-zinc-200/90 bg-white shadow-sm dark:border-zinc-800 dark:bg-zinc-950 ${className}`}
      aria-labelledby="chat-heading"
    >
      <div className="flex items-start justify-between gap-3 border-b border-zinc-100 px-4 py-4 sm:px-5 dark:border-zinc-800">
        <div>
          <h2 id="chat-heading" className="text-lg font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
            Ask the assistant
          </h2>
          <p className="mt-0.5 text-xs text-zinc-500 dark:text-zinc-400">
            Grounded on portfolio data · cite sources below each reply
          </p>
        </div>
        <button
          type="button"
          onClick={reset}
          disabled={loading}
          className="shrink-0 rounded-lg border border-zinc-200 bg-white px-3 py-1.5 text-xs font-medium text-zinc-700 transition-colors hover:bg-zinc-50 disabled:opacity-40 dark:border-zinc-600 dark:bg-zinc-900 dark:text-zinc-200 dark:hover:bg-zinc-800"
        >
          Reset chat
        </button>
      </div>

      <div className="border-b border-zinc-100 px-4 py-4 sm:px-5 dark:border-zinc-800">
        <QuestionPackPicker disabled={loading} onSelect={(text) => void send(text)} />
      </div>

      <div className="min-h-[min(22rem,45vh)] max-h-[min(28rem,50vh)] space-y-4 overflow-y-auto px-4 py-4 sm:px-5">
        {messages.length === 0 && !loading && (
          <p className="text-sm leading-relaxed text-zinc-600 dark:text-zinc-400">
            Start with a suggested prompt or type your own question. Answers are generated from
            indexed materials—verify specifics on the resume when it matters.
          </p>
        )}
        {messages.map((m) =>
          m.role === "user" ? (
            <MessageBubble key={m.id} role="user">
              <p className="whitespace-pre-wrap text-sm leading-relaxed">{m.content}</p>
            </MessageBubble>
          ) : (
            <div key={m.id} className="flex justify-start">
              <AssistantMessage payload={m.payload} />
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

      <div className="border-t border-zinc-100 p-4 sm:p-5 dark:border-zinc-800">
        <ChatInput onSend={(text) => void send(text)} disabled={loading} />
      </div>
    </section>
  );
}
