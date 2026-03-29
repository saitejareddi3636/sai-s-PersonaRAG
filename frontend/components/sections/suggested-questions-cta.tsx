import Link from "next/link";

const CTAS = [
  { label: "Ask about projects", href: "#chat" },
  { label: "Ask about backend experience", href: "#chat" },
  { label: "Ask about ML systems", href: "#chat" },
  { label: "Ask about what roles I am targeting", href: "#chat" },
];

export function SuggestedQuestionsCta() {
  return (
    <section className="border-b border-zinc-200 bg-zinc-50/80 dark:border-zinc-800 dark:bg-zinc-900/40">
      <div className="mx-auto max-w-5xl px-4 py-12 sm:px-6 sm:py-14">
        <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
          Recruiter-style prompts
        </h2>
        <p className="mt-2 max-w-2xl text-sm text-zinc-600 dark:text-zinc-400">
          Jump into the chat with a typical line of inquiry. You can refine or combine topics in the
          same thread.
        </p>
        <ul className="mt-6 flex flex-wrap gap-2">
          {CTAS.map((c) => (
            <li key={c.label}>
              <Link
                href={c.href}
                className="inline-flex rounded-md border border-zinc-200 bg-white px-3 py-2 text-sm font-medium text-zinc-800 hover:border-zinc-300 hover:bg-zinc-50 dark:border-zinc-700 dark:bg-zinc-950 dark:text-zinc-200 dark:hover:border-zinc-600 dark:hover:bg-zinc-900"
              >
                {c.label}
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
