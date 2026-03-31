import Link from "next/link";

type ModeEntryHeroProps = {
  currentMode: "chat" | "voice";
};

const PROFILE_LINKS = [
  {
    label: "Resume",
    href: "https://drive.google.com/file/d/1-wvnrjOQn9Q5tWNuoWOuJmWskkuFqwUO/view?usp=sharing",
  },
  {
    label: "LinkedIn",
    href: "https://www.linkedin.com/in/saitejareddyshaga9999/",
  },
  {
    label: "GitHub",
    href: "https://github.com/saitejareddi3636?tab=repositories",
  },
] as const;

export function ModeEntryHero({ currentMode }: ModeEntryHeroProps) {
  return (
    <section className="border-b border-zinc-200/70 bg-[linear-gradient(180deg,rgba(255,255,255,0.94),rgba(248,249,251,0.86))] dark:border-zinc-800 dark:bg-zinc-950">
      <div className="mx-auto flex min-h-[calc(100vh-3.5rem)] max-w-6xl items-center px-4 py-14 sm:px-6 sm:py-18">
        <div className="mx-auto w-full max-w-3xl text-center">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-zinc-700 dark:text-zinc-400">
            AI Portfolio Assistant
          </p>

          <h1 className="mt-4 text-3xl font-semibold tracking-tight text-zinc-950 sm:text-5xl dark:text-zinc-50">
            Talk to Sai&apos;s AI Portfolio Assistant
          </h1>

          <p className="mx-auto mt-4 max-w-2xl text-sm leading-relaxed text-zinc-700 sm:text-base dark:text-zinc-400">
            Explore early-career backend and applied AI experience through a grounded assistant
            designed for real hiring conversations.
          </p>

          <div className="mt-9 flex justify-center">
            <div className="relative grid h-28 w-28 place-items-center rounded-full border border-zinc-200/90 bg-white shadow-[0_16px_36px_-24px_rgba(15,23,42,0.35)] dark:border-zinc-700 dark:bg-zinc-900">
              <div className="absolute inset-0 rounded-full bg-[radial-gradient(circle_at_center,rgba(59,130,246,0.14),transparent_68%)] dark:bg-[radial-gradient(circle_at_center,rgba(250,250,250,0.08),transparent_70%)]" />
              <svg
                aria-hidden="true"
                viewBox="0 0 24 24"
                className="relative h-10 w-10 text-zinc-800 dark:text-zinc-100"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <rect x="8" y="3" width="8" height="12" rx="4" />
                <path d="M5 11a7 7 0 0 0 14 0" />
                <path d="M12 18v3" />
                <path d="M9 21h6" />
              </svg>
            </div>
          </div>

          <div className="mt-9 grid gap-3 sm:grid-cols-2 sm:gap-4">
            <Link
              href="/?mode=chat#chat"
              aria-current={currentMode === "chat" ? "page" : undefined}
              className={`group rounded-xl border px-5 py-4 text-left transition-colors focus-visible:outline-none ${
                currentMode === "chat"
                    ? "border-sky-500/80 bg-sky-600 text-white shadow-[0_16px_32px_-22px_rgba(2,132,199,0.75)]"
                  : "border-zinc-200/90 bg-white/90 text-zinc-900 hover:border-zinc-300 hover:bg-white dark:border-zinc-700 dark:bg-zinc-950 dark:text-zinc-100 dark:hover:border-zinc-500 dark:hover:bg-zinc-900"
              }`}
            >
              <p className="text-sm font-semibold">Chat with Sai&apos;s agent</p>
                  <p className="mt-1 text-xs opacity-95">
                Type questions and review grounded source snippets.
              </p>
            </Link>

            <Link
              href="/?mode=voice#chat"
              aria-current={currentMode === "voice" ? "page" : undefined}
              className={`group rounded-xl border px-5 py-4 text-left transition-colors focus-visible:outline-none ${
                currentMode === "voice"
                    ? "border-sky-500/80 bg-sky-600 text-white shadow-[0_16px_32px_-22px_rgba(2,132,199,0.75)]"
                  : "border-zinc-200/90 bg-white/90 text-zinc-900 hover:border-zinc-300 hover:bg-white dark:border-zinc-700 dark:bg-zinc-950 dark:text-zinc-100 dark:hover:border-zinc-500 dark:hover:bg-zinc-900"
              }`}
            >
              <p className="text-sm font-semibold">Talk with Sai&apos;s agent</p>
              <p className="mt-1 text-xs opacity-95">
                Speak your question and get voice-ready answers with citations.
              </p>
            </Link>
          </div>

          <div className="mt-7 flex flex-wrap items-center justify-center gap-2">
            <span className="text-[11px] font-medium uppercase tracking-wide text-zinc-700 dark:text-zinc-400">
              Profile links
            </span>
            {PROFILE_LINKS.map((link) => (
              <a
                key={link.label}
                href={link.href}
                target="_blank"
                rel="noreferrer"
                className="rounded-full border border-zinc-200/90 bg-white/90 px-3 py-1 text-xs font-medium text-zinc-700 transition-colors hover:border-sky-300 hover:bg-white hover:text-zinc-900 dark:border-zinc-700 dark:bg-zinc-950 dark:text-zinc-200 dark:hover:border-zinc-500 dark:hover:bg-zinc-900"
              >
                {link.label}
              </a>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}