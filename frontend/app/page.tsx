import { ChatPanel } from "@/components/chat/chat-panel";
import { ChatShell } from "@/components/chat/chat-shell";
import { Intro } from "@/components/sections/intro";
import { ModeEntryHero } from "@/components/sections/mode-entry-hero";
import { QuickFacts } from "@/components/sections/quick-facts";
import { SuggestedQuestionsCta } from "@/components/sections/suggested-questions-cta";

type HomePageProps = {
  searchParams?: Promise<{
    mode?: string;
  }>;
};

export default async function HomePage({ searchParams }: HomePageProps) {
  const params = await searchParams;
  const selectedMode = params?.mode === "voice" ? "voice" : "chat";
  const isChatSelected = selectedMode === "chat";
  const isVoiceSelected = selectedMode === "voice";

  return (
    <>
      <ModeEntryHero currentMode={selectedMode} />
      <Intro />
      <QuickFacts />
      <SuggestedQuestionsCta />
      <div id="chat" className="scroll-mt-16 border-t border-zinc-200/70 bg-[linear-gradient(180deg,rgba(247,248,250,0.7),rgba(243,245,248,0.92))] dark:border-zinc-800 dark:bg-zinc-950/30">
        <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6 sm:py-16">
          <div className="mb-8 max-w-3xl">
            <h2 className="text-sm font-semibold uppercase tracking-widest text-zinc-500 dark:text-zinc-400">
              {isChatSelected ? "Chat workspace" : isVoiceSelected ? "Voice workspace" : "Conversation workspace"}
            </h2>
            <p className="mt-2 text-lg font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
              {isChatSelected
                ? "Chat workspace is ready"
                : isVoiceSelected
                  ? "Voice workspace is ready"
                  : "Continue with chat or voice"}
            </p>
            <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
              {isChatSelected
                ? "Ask directly or use a starter question. Replies stay grounded on portfolio materials and include supporting context."
                : isVoiceSelected
                  ? "Use the microphone controls below to ask spoken questions and get grounded responses with transcript plus voice playback."
                  : "Uses the same grounded assistant with source visibility and session continuity."}
            </p>
          </div>
          <ChatShell>
            <ChatPanel initialMode={selectedMode} />
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
