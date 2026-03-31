import Link from "next/link";

export function Header() {
  return (
    <header className="sticky top-0 z-40 border-b border-zinc-200/70 bg-white/75 backdrop-blur-xl dark:border-zinc-800 dark:bg-zinc-950/75">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between gap-4 px-4 sm:px-6">
        <Link
          href="/"
          className="text-sm font-semibold tracking-tight text-zinc-900 dark:text-zinc-50"
        >
          AI Portfolio Assistant
        </Link>
        <nav className="flex items-center gap-4 text-sm text-zinc-600 dark:text-zinc-400">
          <Link href="/#intro" className="transition-colors hover:text-zinc-900 dark:hover:text-zinc-200">
            Overview
          </Link>
          <Link href="/#chat" className="transition-colors hover:text-zinc-900 dark:hover:text-zinc-200">
            Chat
          </Link>
          <Link href="/chat" className="transition-colors hover:text-zinc-900 dark:hover:text-zinc-200">
            Focused chat
          </Link>
        </nav>
      </div>
    </header>
  );
}
