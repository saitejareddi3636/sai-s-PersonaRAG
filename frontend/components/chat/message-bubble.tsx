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
            ? "bg-zinc-800 text-white dark:bg-zinc-700"
            : "border border-zinc-200 bg-white text-zinc-800 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
        }`}
      >
        {children}
      </div>
    </div>
  );
}
