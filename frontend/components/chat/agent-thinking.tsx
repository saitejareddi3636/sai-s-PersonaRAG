"use client";

type AgentThinkingProps = {
  /** Voice pipeline: STT + RAG + LLM + optional TTS */
  variant?: "chat" | "voice";
  className?: string;
};

/**
 * Visible feedback while the backend retrieves context and runs the local model.
 */
export function AgentThinking({ variant = "chat", className = "" }: AgentThinkingProps) {
  const title = variant === "voice" ? "Processing your voice" : "Assistant is thinking";
  const lines =
    variant === "voice"
      ? [
          "Transcribing audio with Faster-Whisper…",
          "Retrieving grounded passages from the portfolio index…",
          "Generating an answer with the local model (this can take a few seconds on CPU)…",
        ]
      : [
          "Analyzing your question…",
          "Searching the portfolio knowledge base for relevant passages…",
          "Running the local language model to draft a grounded reply…",
        ];

  return (
    <div
      className={`rounded-xl border border-sky-200/70 bg-gradient-to-br from-sky-50/90 to-white px-4 py-3.5 dark:border-sky-900/50 dark:from-zinc-900/80 dark:to-zinc-950/90 ${className}`}
      role="status"
      aria-live="polite"
      aria-busy="true"
      aria-label={title}
    >
      <div className="flex items-start gap-3">
        <div
          className="mt-0.5 h-5 w-5 shrink-0 animate-spin rounded-full border-2 border-zinc-200 border-t-sky-600 dark:border-zinc-600 dark:border-t-sky-400"
          aria-hidden
        />
        <div className="min-w-0 flex-1 space-y-2">
          <p className="text-sm font-semibold text-zinc-800 dark:text-zinc-100">{title}</p>
          <ul className="space-y-1.5 text-xs leading-relaxed text-zinc-600 dark:text-zinc-400">
            {lines.map((line) => (
              <li key={line} className="flex gap-2">
                <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-sky-500/80 dark:bg-sky-400/80" />
                <span>{line}</span>
              </li>
            ))}
          </ul>
          <p className="text-[11px] text-zinc-500 dark:text-zinc-500">
            No response yet — this is normal while the model works. Please wait.
          </p>
        </div>
      </div>
    </div>
  );
}
