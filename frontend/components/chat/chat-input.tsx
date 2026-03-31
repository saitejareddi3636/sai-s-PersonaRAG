"use client";

import { useCallback, useState } from "react";
import type { RefObject } from "react";

type ChatInputProps = {
  onSend: (text: string) => void;
  disabled?: boolean;
  placeholder?: string;
  autoFocus?: boolean;
  textareaRef?: RefObject<HTMLTextAreaElement | null>;
};

export function ChatInput({
  onSend,
  disabled,
  placeholder = "Ask about experience, projects, backend scope, or role fit…",
  autoFocus = false,
  textareaRef,
}: ChatInputProps) {
  const [value, setValue] = useState("");

  const submit = useCallback(() => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
  }, [value, disabled, onSend]);

  return (
    <div className="flex flex-col gap-2">
      <label htmlFor="chat-input" className="sr-only">
        Message
      </label>
      <div className="flex gap-2 rounded-lg border border-zinc-200/90 bg-zinc-50/75 p-1.5 shadow-[0_10px_20px_-18px_rgba(15,23,42,0.35)] dark:border-zinc-700 dark:bg-zinc-900">
        <textarea
          id="chat-input"
          ref={textareaRef}
          rows={2}
          value={value}
          disabled={disabled}
          autoFocus={autoFocus}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
          placeholder={placeholder}
          className="min-h-[2.75rem] flex-1 resize-none bg-transparent px-2 py-2 text-sm text-zinc-900 placeholder:text-zinc-400 focus:outline-none disabled:opacity-60 dark:text-zinc-100 dark:placeholder:text-zinc-500"
        />
        <button
          type="button"
          onClick={submit}
          disabled={disabled || !value.trim()}
          className="shrink-0 self-end rounded-md bg-sky-600 px-3 py-2 text-sm font-medium text-white transition-colors hover:bg-sky-500 disabled:cursor-not-allowed disabled:opacity-40 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
        >
          Send
        </button>
      </div>
      <p className="text-xs text-zinc-500 dark:text-zinc-500">
        Enter to send · Shift+Enter for a new line · grounded responses
      </p>
    </div>
  );
}
