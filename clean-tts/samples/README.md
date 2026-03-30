# Reference voice

**Default (repo root):** `sai_audio.m4a` next to `clean-tts/` (PersonaRAG root). The engine uses it automatically if `samples/voice.wav` is missing.

**Recommended:** convert to WAV for maximum compatibility:

```bash
cd clean-tts
python scripts/prepare_reference.py   # needs ffmpeg: brew install ffmpeg
```

That writes **`voice.wav`** here (mono, 24 kHz, 16-bit).

- **Length:** about 5–10 seconds of clear speech works best  
- **Format:** WAV preferred; m4a may work if Coqui/librosa + ffmpeg can read it on your system  

First synthesis downloads XTTS weights once (network until cached).
