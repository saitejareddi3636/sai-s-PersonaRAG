const FACTS = [
  {
    title: "Focus areas",
    body: "Backend APIs, data-heavy services, and ML-adjacent product work.",
  },
  {
    title: "Stack",
    body: "Python & TypeScript ecosystems; comfortable across cloud and containers.",
  },
  {
    title: "Working style",
    body: "Clear interfaces, tests where they matter, and pragmatic delivery.",
  },
];

export function QuickFacts() {
  return (
    <section className="border-b border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-950">
      <div className="mx-auto max-w-5xl px-4 py-12 sm:px-6 sm:py-16">
        <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">Quick facts</h2>
        <ul className="mt-6 grid gap-4 sm:grid-cols-3">
          {FACTS.map((item) => (
            <li
              key={item.title}
              className="rounded-lg border border-zinc-200 bg-zinc-50/50 p-4 dark:border-zinc-800 dark:bg-zinc-900/30"
            >
              <h3 className="text-sm font-medium text-zinc-900 dark:text-zinc-100">{item.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-zinc-600 dark:text-zinc-400">
                {item.body}
              </p>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
