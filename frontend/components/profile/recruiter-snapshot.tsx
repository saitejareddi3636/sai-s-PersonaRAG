import { PROFILE_HIGHLIGHTS } from "@/lib/profile-highlights";

type RecruiterSnapshotProps = {
  className?: string;
};

export function RecruiterSnapshot({ className = "" }: RecruiterSnapshotProps) {
  const p = PROFILE_HIGHLIGHTS;
  return (
    <aside
      className={`rounded-2xl border border-zinc-200/80 bg-white/92 p-5 shadow-[0_18px_34px_-24px_rgba(15,23,42,0.28)] dark:border-zinc-800 dark:bg-zinc-950 ${className}`}
      aria-label="Profile highlights"
    >
      <p className="text-[11px] font-semibold uppercase tracking-widest text-zinc-500 dark:text-zinc-400">
        At a glance
      </p>
      <h2 className="mt-1 text-base font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
        {p.headline}
      </h2>

      <section className="mt-5">
        <h3 className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Education</h3>
        <ul className="mt-2 space-y-1.5 text-sm leading-snug text-zinc-800 dark:text-zinc-200">
          <li>{p.education.school}</li>
          <li>{p.education.degree}</li>
          <li>{p.education.graduation}</li>
          <li>GPA {p.education.gpa}</li>
        </ul>
      </section>

      <section className="mt-5 border-t border-zinc-200/70 pt-5 dark:border-zinc-800">
        <h3 className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Best-fit roles</h3>
        <ul className="mt-2 space-y-1.5 text-sm leading-snug text-zinc-800 dark:text-zinc-200">
          {p.bestFitRoles.map((role) => (
            <li key={role} className="leading-snug">
              {role}
            </li>
          ))}
        </ul>
      </section>

      <section className="mt-5 border-t border-zinc-200/70 pt-5 dark:border-zinc-800">
        <h3 className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Strongest areas</h3>
        <ul className="mt-2 space-y-1.5 text-sm leading-snug text-zinc-800 dark:text-zinc-200">
          {p.strongestAreas.map((s) => (
            <li key={s} className="flex gap-2">
              <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-zinc-400 dark:bg-zinc-500" />
              {s}
            </li>
          ))}
        </ul>
      </section>

      <section className="mt-5 border-t border-zinc-200/70 pt-5 dark:border-zinc-800">
        <h3 className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Core tools</h3>
        <ul className="mt-2 space-y-1.5 text-sm leading-snug text-zinc-700 dark:text-zinc-300">
          {p.coreTools.map((toolLine) => (
            <li key={toolLine}>{toolLine}</li>
          ))}
        </ul>
      </section>

      <section className="mt-5 border-t border-zinc-200/70 pt-5 dark:border-zinc-800">
        <h3 className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Key projects</h3>
        <ul className="mt-2 space-y-3">
          {p.projects.map((proj) => (
            <li key={proj.title}>
              <p className="text-sm font-medium text-zinc-900 dark:text-zinc-100">{proj.title}</p>
              <p className="mt-0.5 text-xs leading-relaxed text-zinc-600 dark:text-zinc-400">
                {proj.blurb}
              </p>
            </li>
          ))}
        </ul>
      </section>
    </aside>
  );
}
