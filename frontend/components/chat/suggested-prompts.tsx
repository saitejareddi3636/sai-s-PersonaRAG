"use client";

type SuggestedPromptsProps = {
  prompts: string[];
  onSelect: (text: string) => void;
  disabled?: boolean;
  title?: string;
  variant?: "default" | "compact";
};

export function SuggestedPrompts({
  prompts,
  onSelect,
  disabled,
  title = "Suggested questions",
  variant = "default",
}: SuggestedPromptsProps) {
  const compact = variant === "compact";
  return (
    <div className={compact ? "space-y-2" : "space-y-2"}>
      <p
        className={`font-medium uppercase tracking-wide text-zinc-500 dark:text-zinc-400 ${
          compact ? "text-[10px]" : "text-xs"
        }`}
      >
        {title}
      </p>
      <ul className={`flex flex-wrap gap-2 ${compact ? "gap-1.5" : ""}`}>
        {prompts.map((text) => (
          <li key={text}>
            <button
              type="button"
              disabled={disabled}
              onClick={() => onSelect(text)}
              className={`rounded-full border border-zinc-200 bg-zinc-50 text-left text-zinc-800 transition-colors hover:border-zinc-300 hover:bg-white disabled:cursor-not-allowed disabled:opacity-40 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-200 dark:hover:border-zinc-600 dark:hover:bg-zinc-800 ${
                compact ? "px-2.5 py-1 text-xs" : "px-3 py-1.5 text-sm"
              }`}
            >
              {text}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
