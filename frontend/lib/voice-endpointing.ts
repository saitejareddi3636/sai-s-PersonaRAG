/**
 * Browser-side silence detection on the mic stream so voice mode can auto-stop
 * after the user pauses (no second tap). Uses RMS energy + hysteresis; this is
 * separate from Faster-Whisper's Silero VAD, which runs on the server at STT time.
 */

export type VoiceSilenceEndpointOptions = {
  /** RMS above this (float samples) counts as "speech" after debounce. */
  speechRmsThreshold?: number;
  /** RMS below this counts as silence (should be ≤ speech threshold). */
  silenceRmsThreshold?: number;
  /** Consecutive loud frames before we consider speech started (~60fps). */
  minLoudFrames?: number;
  /** How long quiet must hold after speech to fire end (ms). */
  silenceHoldMs?: number;
  /** Minimum time after speech start before we allow auto-end (ms). */
  minUtteranceMs?: number;
  /** Hard cap on recording length (ms). */
  maxRecordingMs?: number;
};

const DEFAULTS: Required<VoiceSilenceEndpointOptions> = {
  speechRmsThreshold: 0.035,
  silenceRmsThreshold: 0.022,
  minLoudFrames: 5,
  silenceHoldMs: 1100,
  minUtteranceMs: 480,
  maxRecordingMs: 120_000,
};

function rmsFloat(data: Float32Array): number {
  let s = 0;
  for (let i = 0; i < data.length; i++) {
    const x = data[i]!;
    s += x * x;
  }
  return Math.sqrt(s / data.length);
}

/**
 * Monitors `stream` and calls `onUtteranceEnd` once after speech + sustained silence
 * (or when maxRecordingMs is hit). Returns a dispose function to stop monitoring.
 */
export function attachVoiceSilenceEndpoint(
  stream: MediaStream,
  onUtteranceEnd: () => void,
  options?: VoiceSilenceEndpointOptions,
): () => void {
  const o = { ...DEFAULTS, ...options };
  let disposed = false;
  let rafId = 0;

  const dispose = () => {
    if (disposed) return;
    disposed = true;
    cancelAnimationFrame(rafId);
    try {
      source.disconnect();
    } catch {
      /* ignore */
    }
    try {
      analyser.disconnect();
    } catch {
      /* ignore */
    }
    void ctx.close();
  };

  const ctx = new AudioContext();
  const source = ctx.createMediaStreamSource(stream);
  const analyser = ctx.createAnalyser();
  analyser.fftSize = 512;
  analyser.smoothingTimeConstant = 0.88;
  source.connect(analyser);
  const buf = new Float32Array(analyser.fftSize);

  let loudStreak = 0;
  let speechStarted = false;
  let speechStartTime = 0;
  let silenceStart: number | null = null;
  const t0 = performance.now();

  const tick = () => {
    if (disposed) return;

    analyser.getFloatTimeDomainData(buf);
    const r = rmsFloat(buf);
    const now = performance.now();

    if (now - t0 >= o.maxRecordingMs) {
      dispose();
      onUtteranceEnd();
      return;
    }

    if (!speechStarted) {
      if (r >= o.speechRmsThreshold) {
        loudStreak++;
        if (loudStreak >= o.minLoudFrames) {
          speechStarted = true;
          speechStartTime = now;
          silenceStart = null;
        }
      } else {
        loudStreak = 0;
      }
      rafId = requestAnimationFrame(tick);
      return;
    }

    if (now - speechStartTime < o.minUtteranceMs) {
      silenceStart = null;
      rafId = requestAnimationFrame(tick);
      return;
    }

    if (r <= o.silenceRmsThreshold) {
      if (silenceStart === null) silenceStart = now;
      else if (now - silenceStart >= o.silenceHoldMs) {
        dispose();
        onUtteranceEnd();
        return;
      }
    } else {
      silenceStart = null;
    }

    rafId = requestAnimationFrame(tick);
  };

  void ctx.resume().then(() => {
    if (!disposed) rafId = requestAnimationFrame(tick);
  });

  return dispose;
}
