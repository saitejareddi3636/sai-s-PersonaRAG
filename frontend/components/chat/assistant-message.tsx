import type { ChatResponse } from "@/lib/api";
import { AudioPlayer } from "./audio-player";

type AssistantMessageProps = {
  payload: ChatResponse;
  voicePending?: boolean;
  voiceError?: string | null;
};

const confidenceLabel: Record<ChatResponse["confidence"], string> = {
  high: "High confidence",
  medium: "Moderate confidence",
  low: "Limited context",
};

export function AssistantMessage({
  payload,
  voicePending = false,
  voiceError = null,
}: AssistantMessageProps) {
  const { answer, confidence, grounding_note, sources, retrieval_error, audio, tts_error } = payload;
  const hasSources = sources && sources.length > 0;

  return (
    <div
      className="max-w-[min(100%,40rem)] rounded-2xl border border-zinc-200/90 bg-zinc-50/50 px-4 py-3.5 shadow-sm dark:border-zinc-700/80 dark:bg-zinc-900/40"
      role="article"
      aria-label="Assistant message"
    >
      <div className="flex flex-wrap items-center gap-2 border-b border-zinc-200/80 pb-2.5 dark:border-zinc-700/80">
        <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Assistant</span>
        <span
          className={`rounded-md px-2 py-0.5 text-[11px] font-medium ${
            confidence === "high"
              ? "bg-zinc-200/90 text-zinc-800 dark:bg-zinc-700 dark:text-zinc-100"
              : confidence === "medium"
                ? "bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300"
                : "border border-zinc-300/80 bg-white text-zinc-600 dark:border-zinc-600 dark:bg-zinc-950 dark:text-zinc-400"
          }`}
        >
          {confidenceLabel[confidence]}
        </span>
      </div>

      <div className="pt-3 text-[15px] leading-relaxed text-zinc-900 dark:text-zinc-100">
        <p className="whitespace-pre-wrap">{answer}</p>
      </div>

      {voicePending && !audio?.audio_url ? (
        <p className="mt-3 text-xs text-zinc-500 dark:text-zinc-400" role="status">
          Generating voice…
        </p>
      ) : null}

      {audio?.audio_url && <AudioPlayer audio={audio} />}

      {(voiceError ?? "").trim() ? (
        <p
          className="mt-3 rounded-lg border border-amber-200/90 bg-amber-50/90 px-3 py-2 text-xs text-amber-950 dark:border-amber-800/80 dark:bg-amber-950/40 dark:text-amber-100"
          role="status"
        >
          Voice: {voiceError}
        </p>
      ) : null}

      {tts_error?.trim() ? (
        <p
          className="mt-3 rounded-lg border border-amber-200/90 bg-amber-50/90 px-3 py-2 text-xs text-amber-950 dark:border-amber-800/80 dark:bg-amber-950/40 dark:text-amber-100"
          role="status"
        >
          Voice: {tts_error}
        </p>
      ) : null}

      {retrieval_error ? (
        <p
          className="mt-3 rounded-lg border border-zinc-200 bg-zinc-100/80 px-3 py-2 text-xs text-zinc-800 dark:border-zinc-600 dark:bg-zinc-900 dark:text-zinc-200"
          role="status"
        >
          Index: {retrieval_error}
        </p>
      ) : null}

      {grounding_note?.trim() ? (
        <p className="mt-3 text-xs leading-relaxed text-zinc-600 dark:text-zinc-400">{grounding_note}</p>
      ) : null}

      {hasSources ? (
        <div className="mt-4 border-t border-zinc-200/80 pt-3 dark:border-zinc-700/80">
          <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
            Based on
          </p>
          <ul className="mt-2 space-y-2">
            {sources.map((s, idx) => (
              <li
                key={`source-${idx}`}
                className="rounded-lg border border-zinc-200/60 bg-white/80 px-3 py-2 text-xs dark:border-zinc-700/60 dark:bg-zinc-950/50"
              >
                {s.excerpt ? (
                  <p className="leading-relaxed text-zinc-700 dark:text-zinc-300">{s.excerpt}</p>
                ) : null}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  );
}
