export function Intro() {
  return (
    <section
      id="intro"
      className="scroll-mt-16 border-b border-zinc-200 bg-zinc-50/80 dark:border-zinc-800 dark:bg-zinc-900/40"
    >
      <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6 sm:py-16">
        <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">How this helps</h2>
        <div className="mt-4 max-w-3xl space-y-4 text-sm leading-relaxed text-zinc-700 dark:text-zinc-300">
          <p>
            I am an early-career software engineer with a strong tilt toward backend and applied AI
            systems: shipping reliable APIs, integrating models into product workflows, and keeping
            latency and observability in mind. This site pairs a concise overview with an assistant
            you can query like a first pass on my experience.
          </p>
          <p>
            Responses are meant to be practical for hiring: scope of ownership, technical choices,
            and what I am looking for next. For anything contractual or time-sensitive, use the
            materials linked from my resume or reach out directly.
          </p>
        </div>
      </div>
    </section>
  );
}
