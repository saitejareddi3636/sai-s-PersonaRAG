# clean-tts — Local Coqui XTTS v2 (Mac M2)

This folder lives **inside the PersonaRAG repo**: `sai-s-PersonaRAG/clean-tts/`.  
From the repo root, run `cd clean-tts` before the commands below.

Minimal offline-capable TTS after the first model download: zero-shot clone from `samples/voice.wav`.

## PersonaRAG integration

1. Start this service (default **http://127.0.0.1:8010** — see `app/main.py` / `uvicorn`).
2. In the **PersonaRAG** backend `.env`, set `TTS_PROVIDER=clean-xtts` and `CLEAN_TTS_URL=http://127.0.0.1:8010` (or match your port).
3. In the web UI, choose **Voice** in the chat header so replies include synthesized audio (Text chat stays text-only).

## Requirements

- macOS on **Apple Silicon** (M1/M2/M3)
- **Python 3.10 or 3.11** (recommended; avoid 3.12 if you hit Coqui issues)
- **Free disk space: at least ~8–15 GB** before `pip install` (PyTorch + Coqui + SpaCy/Transformers are large). **Models add more** after first run.
- A short reference WAV: `samples/voice.wav`

### If install failed with “No space left on device”

1. **Check space:** `df -h ~`
2. **Free several GB** (Empty Trash, remove old Xcode simulators, large `~/Downloads`, Docker images, etc.).
3. **Optional reclaim pip cache:** `pip cache purge`
4. **Remove broken partial venv and retry** (from PersonaRAG repo root):
   ```bash
   cd clean-tts
   rm -rf .venv
   chmod +x scripts/bootstrap.sh
   ./scripts/bootstrap.sh
   ```
   Or follow the manual steps below (same as bootstrap).

## 1) Create venv (from this folder)

**Automated (checks free disk first):**

```bash
cd clean-tts
chmod +x scripts/bootstrap.sh
./scripts/bootstrap.sh
```

**Manual:**

```bash
cd clean-tts
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip wheel setuptools
# Optional: avoids occasional gruut-lang-es build races
pip install gruut-lang-es gruut-lang-fr
pip install -r requirements.txt
```

If `torch` fails to install, use the official PyTorch instructions for macOS, then install the rest:

```bash
pip install torch torchaudio
pip install TTS fastapi uvicorn soundfile numpy
```

## 2) Verify environment

```bash
source .venv/bin/activate
python scripts/verify_env.py
```

You should see `MPS available: True` or `False` (CPU still works, slower).

Check XTTS is listed:

```bash
tts --list_models | grep -i xtts
```

## 3) Reference audio (`sai_audio.m4a`)

Your clip can stay at the **PersonaRAG repo root** as `sai_audio.m4a` — `clean-tts` picks it up automatically.

**Optional (recommended):** convert to WAV for fewer codec issues:

```bash
cd clean-tts
python scripts/prepare_reference.py   # requires `ffmpeg` on PATH
```

Or copy any short WAV to `clean-tts/samples/voice.wav` (takes priority over the m4a).

## 4) One-shot test (writes `outputs/demo.wav`)

```bash
source .venv/bin/activate
python scripts/synthesize_once.py
afplay outputs/demo.wav
```

First run downloads the model (network required once).

**Quick smoke test (no HTTP server):**

```bash
python scripts/quick_test_tts.py
```

Writes `outputs/quick_test.wav`. If `uvicorn` is already on port 8010: `scripts/quick_test_http.sh`.

## 5) HTTP API

Startup **warms the model and caches speaker latents** by default (faster first real `/tts`). To skip (faster boot, slower first request):

```bash
export CLEAN_TTS_WARMUP=0
```

```bash
source .venv/bin/activate
cd clean-tts
# First-time model download may take a while. CPML: https://coqui.ai/cpml
export COQUI_TOS_AGREED=1
uvicorn app.main:app --host 0.0.0.0 --port 8010
```

(`app/engine.py` sets `COQUI_TOS_AGREED` by default so the server is non-interactive; export explicitly if you prefer.)

Logs use prefixes `xtts_timing` (conditioning, generation, WAV encode) and `chat_timing` / `portfolio_tts_proxy` on the PersonaRAG API when you use it.

Health:

```bash
curl -s http://127.0.0.1:8010/health
```

Synthesize (JSON body):

```bash
curl -s -X POST http://127.0.0.1:8010/tts \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello from XTTS.","language":"en"}' \
  --output outputs/api.wav
afplay outputs/api.wav
```

## MPS issues

```bash
export PYTORCH_ENABLE_MPS_FALLBACK=1
```

## Layout

```text
clean-tts/
  app/           # engine + FastAPI
  scripts/       # verify_env, synthesize_once
  samples/       # voice.wav (you provide)
  outputs/       # generated audio
  requirements.txt
  README.md
```

## Note on sample rate

`app/main.py` uses **24000 Hz** for WAV encoding. If playback sounds wrong, check Coqui’s output rate for your `TTS` version and adjust `SAMPLE_RATE_HZ` in `app/main.py`.
