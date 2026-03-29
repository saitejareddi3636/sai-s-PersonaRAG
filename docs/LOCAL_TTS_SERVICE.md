# Local TTS Service Integration

This document describes how to integrate a local Text-to-Speech (TTS) service like F5-TTS with PersonaRAG.

## Overview

PersonaRAG supports optional audio synthesis of chat answers through a local TTS service. The integration is:

- **Optional**: Chat works fine without TTS (graceful fallback)
- **Decoupled**: TTS service runs separately; no tight coupling
- **Graceful**: If TTS fails, text response still works
- **Simple**: Clean HTTP contract, easy to debug

## Local TTS Service Contract

### Expected Interface

The local TTS service must provide:

**Endpoint**: `POST /synthesize`

**Base URL**: `http://localhost:9000` (configurable via `TTS_SERVICE_URL` env var)

**Request Body**:
```json
{
  "text": "Tell me about your experience with Python",
  "voice_id": null
}
```

**Response (Success - 200)**:
```json
{
  "success": true,
  "audio_url": "file:///cache/audio/output_12345.wav",
  "duration_ms": 4500,
  "format": "wav"
}
```

**Response (Error - 5xx)**:
```json
{
  "success": false,
  "error": "Model failed to generate audio"
}
```

### Health Check

The backend also expects:

**Endpoint**: `GET /health`

**Response (200)**:
```json
{
  "status": "ok"
}
```

(This is optional but recommended for service discovery)

## How It Works

### Flow

```
User Question with include_tts=true
    │
    ├─> Backend generates text answer (RAG)
    │
    ├─> If include_tts and TTS_PROVIDER="local-service":
    │   │
    │   └─> Call LocalTTSClient.synthesize(answer_text)
    │       │
    │       ├─> POST http://localhost:9000/synthesize
    │       │
    │       ├─> If 200: Extract audio metadata
    │       │   └─> Return ChatResponse with audio field
    │       │
    │       └─> If error/timeout:
    │           └─> Log warning, return ChatResponse with audio=null
    │
    └─> Return ChatResponse (text always present, audio optional)

Frontend receives response:
    ├─> Display text answer (always)
    ├─> If audio present:
    │   └─> Show "Listen" button
    └─> If no audio:
        └─> Show text-only answer
```

### Request/Response Flow (Chat with Audio)

**Frontend sends**:
```json
{
  "question": "Tell me about your ML projects",
  "session_id": "abc123",
  "include_tts": true
}
```

**Backend attempts**:
1. Generate answer via RAG (text always works)
2. If `include_tts=true`:
   - Call `/api/tts` internally (or use TTS backend directly)
   - Synthesize answer audio via local service
3. Return both text and audio metadata

**Response**:
```json
{
  "answer": "I've worked on several ML projects including...",
  "confidence": "high",
  "sources": [...],
  "session_id": "abc123",
  "audio": {
    "audio_url": "file:///cache/audio/output.wav",
    "duration_ms": 5200,
    "provider": "local-f5-tts"
  },
  "retrieval": [...]
}
```

If audio synthesis fails:
```json
{
  "answer": "I've worked on several ML projects including...",
  "confidence": "high",
  "sources": [...],
  "session_id": "abc123",
  "audio": null,
  "retrieval": [...]
}
```

## Configuration

### Backend Environment Variables

**`backend/.env`**:

```bash
# TTS Configuration
TTS_PROVIDER=local-service              # "mock", "local-service", or "f5-tts"
TTS_SERVICE_URL=http://localhost:9000   # URL to local TTS service
```

### Docker Compose

To run local TTS alongside PersonaRAG:

**`docker-compose.yml`** (add to services):

```yaml
services:
  backend:
    # ... existing config ...
    environment:
      - TTS_PROVIDER=local-service
      - TTS_SERVICE_URL=http://tts-service:9000
    depends_on:
      - tts-service

  tts-service:
    # Example: F5-TTS service container
    image: f5-tts:latest
    container_name: personarag-tts
    ports:
      - "9000:9000"
    environment:
      - PORT=9000
    volumes:
      - ./cache/audio:/app/cache/audio
      - ./models/f5-tts:/app/models
```

## Implementing a Local TTS Service

### Minimal Example (Python)

```python
# app.py (TTS service)
from fastapi import FastAPI
from pydantic import BaseModel
import torch
from f5_tts import F5TTS

app = FastAPI()
model = F5TTS.load("model.pth")

class SynthesizeRequest(BaseModel):
    text: str
    voice_id: str | None = None

@app.post("/synthesize")
async def synthesize(req: SynthesizeRequest):
    try:
        # Generate audio
        audio = model.synthesize(req.text, voice_id=req.voice_id)
        
        # Save to cache
        path = f"cache/audio/{uuid.uuid4()}.wav"
        audio.save(path)
        
        return {
            "success": True,
            "audio_url": f"file://{os.path.abspath(path)}",
            "duration_ms": int(len(audio) / sample_rate * 1000),
            "format": "wav"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }, 500

@app.get("/health")
async def health():
    return {"status": "ok"}

# Run: uvicorn app:app --port 9000
```

### Integration Points

When implementing your TTS service:

1. **Accept `voice_id`** for future multi-voice support
2. **Return audio file path or URL** (not base64 audio in response)
3. **Include `duration_ms`** for UI (progress bars, etc.)
4. **Handle errors gracefully** (return 5xx, not crash)
5. **Include `/health` endpoint** for discovery
6. **Make synthesis fast** (ideally <10s for typical answers)

## Client Error Handling

The backend client (`LocalTTSClient`) handles:

- **Connection errors** (service not running): Returns None → audio=null in response
- **Timeouts** (synthesis takes too long): Returns None → audio=null in response
- **Invalid responses**: Logs warning → audio=null in response
- **5xx errors**: Logs error → audio=null in response

**All errors gracefully degrade**: Text response works regardless.

## Debugging

### Check TTS Service Health

```bash
curl http://localhost:9000/health
```

Expected: `{"status":"ok"}`

### Test Synthesis Manually

```bash
curl -X POST http://localhost:9000/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello world","voice_id":null}'
```

### View Backend Logs

```bash
# Docker
docker compose logs -f backend

# Direct
grep "TTS synthesis" backend/app.log
```

### Enable Debug Logging

**`backend/.env`**:
```bash
LOG_LEVEL=DEBUG
```

Then check logs for `LocalTTSClient` debug messages.

## Frontend Integration

To show "Listen" button in chat UI:

```typescript
// Check if audio is available
if (response.audio?.audio_url) {
  // Show "Listen" button
  <button onClick={() => playAudio(response.audio.audio_url)}>
    🔊 Listen ({response.audio.duration_ms / 1000}s)
  </button>
} else {
  // Text-only (normal)
}
```

Audio playback can use HTML5 `<audio>` element or Web Audio API.

## Performance Considerations

| Metric | Target | Notes |
|--------|--------|-------|
| Synthesis latency | <5s | For typical 50-word answer |
| Max answer length | 500 words | May take 30-60s |
| Model memory | <2GB VRAM | Adjust batch size if needed |
| Audio format | WAV or MP3 | Stream to client or serve via HTTP |

### Optimization Tips

- **Cache**: Store (text, voice_id) → audio mappings to avoid re-synthesis
- **Streaming**: Return chunked audio during generation (HTTP 206)
- **Batching**: Queue multiple synthesis requests if high throughput
- **Format**: Use MP3 for smaller files if bandwidth is constrained

## Future Enhancements

- [ ] **Multi-voice profiles**: Map voice_id → pre-loaded voice embeddings
- [ ] **Voice cloning**: Accept reference audio → clone voice on-the-fly
- [ ] **Emotion control**: Add `emotion` parameter to synthesize different tones
- [ ] **Streaming synthesis**: Return audio while generating (lower latency perception)
- [ ] **Caching layer**: Redis-backed cache for (text, voice) → audio URL
- [ ] **Audio format negotiation**: Let frontend request WAV, MP3, OGG, etc.

## Troubleshooting

**"Local TTS service unavailable"**
- Check service is running: `curl http://localhost:9000/health`
- Check `TTS_SERVICE_URL` matches service URL
- Check firewall/network allows connection

**"Timeout synthesizing audio"**
- Service may be slow; increase timeout in `LocalTTSClient`
- Or: Implement async/queued synthesis on server side

**"No audio in response, but service is running"**
- Check backend logs: `docker compose logs backend | grep TTS`
- Verify service returns valid JSON with `audio_url` field
- Test service directly: `curl -X POST http://localhost:9000/synthesize`

**"Audio plays but is garbled/silent"**
- Check audio file format (WAV, MP3, OGG)
- Verify file path is accessible from client
- Check frontend audio player supports the format

## References

- **F5-TTS**: https://github.com/SWivlda/F5-TTS
- **FastAPI**: https://fastapi.tiangolo.com/
- **Audio Formats**: WAV, MP3, OGG, FLAC
- **Web Audio API**: https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API
