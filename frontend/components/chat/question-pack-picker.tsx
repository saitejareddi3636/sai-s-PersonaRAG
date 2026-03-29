"use client";

import { QUESTION_PACKS, QUESTION_PACK_ORDER, type QuestionPackId } from "@/lib/question-packs";

const packById = Object.fromEntries(QUESTION_PACKS.map((p) => [p.id, p])) as Record<
  QuestionPackId,
  (typeof QUESTION_PACKS)[number]
>;

type QuestionPackPickerProps = {
  onSelect: (question: string) => void;
  disabled?: boolean;
};

export function QuestionPackPicker({ onSelect, disabled }: QuestionPackPickerProps) {
  return (
    <div className="space-y-4">
      <div>
        <p className="text-[10px] font-medium uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
          Question packs
        </p>
        <p className="mt-1 text-xs text-zinc-600 dark:text-zinc-400">
          Pick a prompt that matches your role—everything is sent to the assistant as-is.
        </p>
      </div>

      <div className="grid gap-5 sm:grid-cols-3">
        {QUESTION_PACK_ORDER.map((id) => {
          const pack = packById[id];
          return (
            <div
              key={pack.id}
              className="rounded-xl border border-zinc-200/90 bg-zinc-50/50 p-3 dark:border-zinc-700/80 dark:bg-zinc-900/30"
            >
              <h3 className="text-xs font-semibold text-zinc-900 dark:text-zinc-50">{pack.label}</h3>
              <p className="mt-0.5 text-[11px] leading-snug text-zinc-500 dark:text-zinc-400">
                {pack.subtitle}
              </p>
              <ul className="mt-3 space-y-1.5">
                {pack.questions.map((q) => (
                  <li key={q}>
                    <button
                      type="button"
                      disabled={disabled}
                      onClick={() => onSelect(q)}
                      className="w-full rounded-lg border border-transparent bg-white px-2.5 py-1.5 text-left text-xs leading-snug text-zinc-800 transition-colors hover:border-zinc-300 hover:bg-zinc-50 disabled:cursor-not-allowed disabled:opacity-40 dark:bg-zinc-950/50 dark:text-zinc-200 dark:hover:border-zinc-600 dark:hover:bg-zinc-900"
                    >
                      {q}
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          );
        })}
      </div>
    </div>
  );
}
