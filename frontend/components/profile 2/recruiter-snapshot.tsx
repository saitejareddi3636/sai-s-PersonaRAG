import { PROFILE_HIGHLIGHTS } from "@/lib/profile-highlights";

type RecruiterSnapshotProps = {
  className?: string;
};

export function RecruiterSnapshot({ className = "" }: RecruiterSnapshotProps) {
  const p = PROFILE_HIGHLIGHTS;
  return (
    <aside
      className={`rounded-2xl border border-zinc-200/90 bg-white p-5 shadow-sm dark:border-zinc-800 dark:bg-zinc-950 ${className}`}
      aria-label="Profile highlights"
    >
      <p className="text-[11px] font-semibold uppercase tracking-widest text-zinc-500 dark:text-zinc-400">
        At a glance
      </p>
      <h2 className="mt-1 text-base font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
        {p.headline}
      </h2>

      <section className="mt-5">
        <h3 className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Strongest skills</h3>
        <ul className="mt-2 space-y-1.5 text-sm leading-snug text-zinc-800 dark:text-zinc-200">
          {p.skills.map((s) => (
            <li key={s} className="flex gap-2">
              <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-zinc-400 dark:bg-zinc-500" />
              {s}
            </li>
          ))}
        </ul>
      </section>

      <section className="mt-5 border-t border-zinc-100 pt-5 dark:border-zinc-800">
        <h3 className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Experience</h3>
        <p className="mt-2 text-sm leading-relaxed text-zinc-700 dark:text-zinc-300">{p.experience}</p>
      </section>

      <section className="mt-5 border-t border-zinc-100 pt-5 dark:border-zinc-800">
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

      <section className="mt-5 border-t border-zinc-100 pt-5 dark:border-zinc-800">
        <h3 className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Target roles</h3>
        <ul className="mt-2 space-y-1.5 text-sm text-zinc-800 dark:text-zinc-200">
          {p.targetRoles.map((r) => (
            <li key={r} className="leading-snug">
              {r}
            </li>
          ))}
        </ul>
      </section>
    </aside>
  );
}
