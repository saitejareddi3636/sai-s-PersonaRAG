"use client";

import { useRef, useState } from "react";
import type { AudioMetadata } from "@/lib/api";

type AudioPlayerProps = {
  audio: AudioMetadata;
};

export function AudioPlayer({ audio }: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const handlePlayClick = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
      } else {
        audioRef.current.play();
        setIsPlaying(true);
      }
    }
  };

  const handleEnded = () => {
    setIsPlaying(false);
  };

  if (!audio?.audio_url) {
    return null;
  }

  const duration = audio.duration_ms ? Math.round(audio.duration_ms / 1000) : 0;
  const durationLabel = duration ? `${duration}s` : "";

  return (
    <div className="mt-3 flex items-center gap-2 rounded-lg border border-zinc-200/80 bg-white/60 px-3 py-2.5 dark:border-zinc-700/80 dark:bg-zinc-900/30">
      <button
        onClick={handlePlayClick}
        className="flex h-8 w-8 items-center justify-center rounded-full bg-zinc-200/80 text-zinc-700 transition-colors hover:bg-zinc-300 dark:bg-zinc-700/80 dark:text-zinc-100 dark:hover:bg-zinc-600"
        title={isPlaying ? "Pause" : "Play"}
        aria-label={isPlaying ? "Pause audio" : "Play audio"}
      >
        {isPlaying ? (
          <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
            <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
          </svg>
        ) : (
          <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
            <path d="M8 5v14l11-7z" />
          </svg>
        )}
      </button>

      <audio
        ref={audioRef}
        src={audio.audio_url}
        onEnded={handleEnded}
        crossOrigin="anonymous"
      />

      <span className="text-xs font-medium text-zinc-600 dark:text-zinc-400">
        {isPlaying ? "Playing" : "Listen"} {durationLabel}
      </span>
    </div>
  );
}
