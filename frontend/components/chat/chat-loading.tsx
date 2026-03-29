export function ChatLoadingSkeleton() {
  return (
    <div
      className="max-w-[min(100%,40rem)] rounded-2xl border border-zinc-200/90 bg-zinc-50/50 px-4 py-3.5 dark:border-zinc-700/80 dark:bg-zinc-900/40"
      aria-busy="true"
      aria-label="Generating answer"
    >
      <div className="mb-3 flex items-center gap-2">
        <span className="h-2 w-2 animate-pulse rounded-full bg-zinc-400 dark:bg-zinc-500" />
        <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Generating answer…</span>
      </div>
      <div className="space-y-2">
        <div className="h-3 w-[92%] animate-pulse rounded bg-zinc-200/90 dark:bg-zinc-700/80" />
        <div className="h-3 w-[78%] animate-pulse rounded bg-zinc-200/90 dark:bg-zinc-700/80" />
        <div className="h-3 w-[85%] animate-pulse rounded bg-zinc-200/80 dark:bg-zinc-700/70" />
      </div>
    </div>
  );
}
