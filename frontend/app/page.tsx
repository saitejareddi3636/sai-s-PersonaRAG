import { ChatPanel } from "@/components/chat/chat-panel";
import { ChatShell } from "@/components/chat/chat-shell";
import { Hero } from "@/components/sections/hero";
import { Intro } from "@/components/sections/intro";
import { QuickFacts } from "@/components/sections/quick-facts";
import { SuggestedQuestionsCta } from "@/components/sections/suggested-questions-cta";

export default function HomePage() {
  return (
    <>
      <Hero />
      <Intro />
      <QuickFacts />
      <SuggestedQuestionsCta />
      <div id="chat" className="scroll-mt-16 border-t border-zinc-200/80 bg-zinc-50/50 dark:border-zinc-800 dark:bg-zinc-950/30">
        <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6 sm:py-16">
          <div className="mb-8 max-w-2xl">
            <h2 className="text-sm font-semibold uppercase tracking-widest text-zinc-500 dark:text-zinc-400">
              Live conversation
            </h2>
            <p className="mt-2 text-lg font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
              Chat with the portfolio assistant
            </p>
            <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
              Same experience you&apos;d demo in a screen—grounded answers and visible sources.
            </p>
          </div>
          <ChatShell>
            <ChatPanel />
          </ChatShell>
        </div>
      </div>
      <footer className="border-t border-zinc-200 bg-white py-8 dark:border-zinc-800 dark:bg-zinc-950">
        <div className="mx-auto max-w-5xl px-4 text-center text-xs text-zinc-500 sm:px-6">
          Portfolio assistant · answers are grounded on provided materials; verify specifics as needed.
        </div>
      </footer>
    </>
  );
}
