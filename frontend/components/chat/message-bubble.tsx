import type { ReactNode } from "react";

type Role = "user" | "assistant";

type MessageBubbleProps = {
  role: Role;
  children: ReactNode;
};

export function MessageBubble({ role, children }: MessageBubbleProps) {
  const isUser = role === "user";
  return (
    <div
      className={`flex w-full ${isUser ? "justify-end" : "justify-start"}`}
      role="article"
      aria-label={isUser ? "Your message" : "Assistant message"}
    >
      <div
        className={`max-w-[min(100%,36rem)] rounded-lg px-3.5 py-2.5 text-sm leading-relaxed ${
          isUser
            ? "bg-gradient-to-br from-sky-600 to-sky-700 text-white shadow-[0_12px_24px_-18px_rgba(2,132,199,0.8)]"
            : "border border-zinc-200/80 bg-white/95 text-zinc-800 shadow-[0_10px_20px_-18px_rgba(15,23,42,0.35)] dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
        }`}
      >
        {children}
      </div>
    </div>
  );
}
