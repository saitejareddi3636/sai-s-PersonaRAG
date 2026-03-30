"use client";

import { useEffect, useRef, useState } from "react";
import type { AudioMetadata } from "@/lib/api";

type AudioPlayerProps = {
  audio: AudioMetadata;
  /** Start playback as soon as the clip is ready (user already interacted by sending a message). */
  autoPlay?: boolean;
};

export function AudioPlayer({ audio, autoPlay = true }: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  /**
   * Revoke the previous blob URL when `audio_url` changes — not on unmount.
   * Revoking in effect cleanup breaks React Strict Mode (dev): fake unmount revokes
   * the URL while state still references it → remount sees a dead blob → NotSupportedError.
   */
  const prevBlobUrlRef = useRef<string | null>(null);
  useEffect(() => {
    const u = audio.audio_url;
    if (!u?.startsWith("blob:")) {
      prevBlobUrlRef.current = u ?? null;
      return;
    }
    const prev = prevBlobUrlRef.current;
    if (prev && prev.startsWith("blob:") && prev !== u) {
      URL.revokeObjectURL(prev);
    }
    prevBlobUrlRef.current = u;
  }, [audio.audio_url]);

  useEffect(() => {
    const url = audio.audio_url;
    if (!url) return;

    const el = audioRef.current;
    if (!el) return;

    el.load();
    if (autoPlay) {
      void el.play().catch(() => {
        /* Autoplay blocked, unsupported source, or decode error — user can tap Play */
      });
    }
  }, [audio.audio_url, autoPlay]);

  const handlePlayClick = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
      } else {
        void audioRef.current.play().catch(() => setIsPlaying(false));
      }
    }
  };

  const handleEnded = () => {
    setIsPlaying(false);
  };

  const handlePlay = () => {
    setIsPlaying(true);
  };

  const handlePause = () => {
    setIsPlaying(false);
  };

  if (!audio?.audio_url) {
    return null;
  }

  const duration = audio.duration_ms ? Math.round(audio.duration_ms / 1000) : 0;
  const durationLabel = duration ? `${duration}s` : "";

  /** `crossOrigin` on blob/data URLs breaks decoding in some browsers (NotSupportedError). Only use for remote http(s). */
  const needsCrossOrigin =
    audio.audio_url.startsWith("http://") || audio.audio_url.startsWith("https://");

  return (
    <div className="mt-3 flex items-center gap-2 rounded-lg border border-zinc-200/80 bg-white/60 px-3 py-2.5 dark:border-zinc-700/80 dark:bg-zinc-900/30">
      <button
        type="button"
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
        preload="auto"
        onEnded={handleEnded}
        onPlay={handlePlay}
        onPause={handlePause}
        {...(needsCrossOrigin ? { crossOrigin: "anonymous" as const } : {})}
      />

      <span className="text-xs font-medium text-zinc-600 dark:text-zinc-400">
        {isPlaying ? "Playing" : "Listen"} {durationLabel}
      </span>
    </div>
  );
}
