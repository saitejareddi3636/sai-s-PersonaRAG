import type { Metadata } from "next";

import { ChatPanel } from "@/components/chat/chat-panel";
import { ChatShell } from "@/components/chat/chat-shell";

export const metadata: Metadata = {
  title: "Chat",
};

export default function ChatPage() {
  return (
    <main className="border-t border-zinc-200/80 bg-zinc-50/50 px-4 py-10 dark:border-zinc-800 dark:bg-zinc-950/30 sm:px-6">
      <div className="mx-auto max-w-6xl">
        <header className="mb-8">
          <h1 className="text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
            Conversation
          </h1>
          <p className="mt-1 max-w-xl text-sm text-zinc-600 dark:text-zinc-400">
            Focused view with profile highlights—ideal for sharing or recording a quick demo.
          </p>
        </header>
        <ChatShell>
          <ChatPanel />
        </ChatShell>
      </div>
    </main>
  );
}
