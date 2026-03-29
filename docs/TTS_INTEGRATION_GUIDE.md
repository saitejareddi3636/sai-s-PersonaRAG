# TTS Integration Guide

**Status**: Architecture prepared; mock backend ready; F5-TTS integration pending

---

## Current Implementation (Mock)

### Files Created/Modified

```
backend/
├── app/
│   ├── main.py                          (added tts router import)
│   ├── core/config.py                   (added TTS_PROVIDER setting)
│   ├── api/routes/
│   │   └── tts.py                       ✨ NEW: POST /api/tts endpoint
│   ├── schemas/
│   │   └── tts.py                       ✨ NEW: TTSRequest, TTSResponse models
│   └── services/
│       └── tts_service.py               ✨ NEW: Backend abstraction + Mock impl
└── docs/
    └── architecture.md                  (added TTS Architecture section)

README.md                                (added "Future voice support" section)
```

### API Contract

**POST /api/tts**

Request:
```json
{
  "text": "Tell me more about your experience with machine learning projects.",
  "voice_profile_id": null
}
```

Response (success):
```json
{
  "success": true,
  "audio_url": "/api/audio/mock-2026-03-28T14:30:00.123456.mp3",
  "audio_path": "cache/audio/mock-2026-03-28T14:30:00.123456.mp3",
  "duration_ms": 4500,
  "provider": "mock",
  "message": "Mocked audio synthesis (15 words, voice=default)"
}
```

Response (validation error):
```json
{
  "success": false,
  "audio_url": null,
  "audio_path": null,
  "duration_ms": null,
  "provider": "mock",
  "message": "Empty text not allowed"
}
```

### Mock Behavior

- Word count → duration estimation (~150 words/minute)
- Deterministic mock URLs with timestamps
- No external dependencies
- Ready for frontend UI development

### Configuration

```bash
# Default (mock backend)
TTS_PROVIDER=mock

# Future (when F5-TTS is ready)
TTS_PROVIDER=f5-tts
```

---

## Future F5-TTS Integration Steps

### Phase 1: Model Setup

1. **Download F5-TTS Model**
   ```bash
   # Create cache directory
   mkdir -p backend/cache/models/f5-tts
   
   # Download model (size/source TBD)
   # e.g., from HuggingFace: huggingface-hub library
   ```

2. **Update requirements.txt**
   ```bash
   # Add F5-TTS dependencies
   # e.g., f5-tts or similar
   # torch, torchaudio
   # numpy
   ```

### Phase 2: Backend Implementation

1. **Implement F5TTSBackend class** in `backend/app/services/tts_service.py`

   ```python
   class F5TTSBackend(TTSBackend):
       """Real F5-TTS synthesis backend."""
       
       def __init__(self, model_path: str):
           # Load model from disk
           self.model = load_f5_tts_model(model_path)
       
       async def synthesize(self, text: str, voice_profile_id: str | None = None) -> dict:
           # 1. Validate text
           # 2. Load voice profile (default or specified)
           # 3. Call model.synthesize(text, voice)
           # 4. Save audio to cache/audio/{unique_id}.wav
           # 5. Return metadata dict
           pass
   ```

2. **Load model in app startup**

   Update `backend/app/main.py` lifespan event:
   ```python
   @asynccontextmanager
   async def lifespan(_: FastAPI):
       logger.info("starting %s", settings.app_name)
       
       # Load TTS model if provider is f5-tts
       if settings.tts_provider == "f5-tts":
           initialize_f5_tts_model(settings)
       
       warm_retrieval_index(settings)
       yield
   ```

3. **Add voice profiles** (optional)

   Example structure in `backend/app/services/voice_profiles.py`:
   ```python
   VOICE_PROFILES = {
       "default": {"model_path": "...", "sample_rate": 22050},
       "formal": {"model_path": "...", "sample_rate": 24000},
   }
   ```

### Phase 3: Audio Serving

1. **Create audio serving route** in `backend/app/api/routes/audio.py`

   ```python
   @router.get("/audio/{audio_id}")
   async def get_audio(audio_id: str):
       # Stream audio file from cache/audio/{audio_id}
       # Set appropriate Content-Type, Content-Length headers
       # Use FileResponse or StreamingResponse
   ```

2. **Optional: Audio caching layer**

   ```python
   class AudioCache:
       """Cache synthesized audio to avoid re-synthesis."""
       
       def get_or_synthesize(self, text: str, voice_id: str) -> str:
           # Hash (text, voice_id)
           # Check if cached
           # If not, synthesize and store
           # Return audio path
   ```

### Phase 4: Frontend Integration

1. **Create audio player component** (`frontend/components/chat/audio-player.tsx`)

   ```tsx
   export function AudioPlayer({ audioUrl, duration }: Props) {
     const audioRef = useRef<HTMLAudioElement>(null);
     
     return (
       <div className="flex items-center gap-2">
         <button onClick={() => audioRef.current?.play()}>
           Play Audio
         </button>
         <audio ref={audioRef} src={audioUrl} />
         <span>{Math.round(duration / 1000)}s</span>
       </div>
     );
   }
   ```

2. **Integrate into chat** (`frontend/components/chat/assistant-message.tsx`)

   ```tsx
   export function AssistantMessage({ message, audioUrl, duration }: Props) {
     return (
       <div className="flex flex-col gap-2">
         <p>{message.answer}</p>
         {audioUrl && (
           <AudioPlayer audioUrl={audioUrl} duration={duration} />
         )}
       </div>
     );
   }
   ```

3. **Call TTS endpoint from chat** (optional)

   ```tsx
   // Option A: Call /api/tts after receiving text
   const ttsResponse = await fetch("/api/tts", {
     method: "POST",
     body: JSON.stringify({ text: answer.answer })
   });
   
   // Option B: Backend returns TTS data in chat response
   // (if chat route is updated to include optional tts_metadata)
   ```

---

## Design Decisions & Rationale

### 1. **Service Abstraction (TTSBackend base class)**
   - Allows swapping implementations without changing routes/schemas
   - Future-proof: other TTS providers can be added (e.g., ElevenLabs API)
   - Clean separation of concerns

### 2. **Mocked First**
   - Frontend dev doesn't block on model availability
   - Fast feedback loop
   - Easy to test without GPU

### 3. **Config-driven Provider Selection**
   - Runtime switching between mock/real backends
   - No code changes needed to deploy with different provider
   - Env var `TTS_PROVIDER` is simple and explicit

### 4. **No Breaking API Changes**
   - `/api/tts` route stays the same
   - Response schema is identical (mock vs real)
   - Frontend code doesn't need updates when switching backends

### 5. **Audio Served Separately**
   - Keep chat response lean (no binary data)
   - Audio metadata (`audio_url`, `duration_ms`) points frontend to fetch audio
   - Enables caching, streaming, and optional async synthesis

---

## Testing Strategy

### Unit Tests (Backend)

```python
# tests/test_tts_mock.py
@pytest.mark.asyncio
async def test_tts_mock_backend_success():
    backend = MockTTSBackend()
    result = await backend.synthesize("Hello, world!")
    assert result["success"] is True
    assert result["duration_ms"] > 0

@pytest.mark.asyncio
async def test_tts_endpoint_validation():
    # POST /api/tts with empty text should fail
    response = client.post("/api/tts", json={"text": ""})
    assert response.status_code == 422  # Validation error

@pytest.mark.asyncio
async def test_tts_endpoint_mock():
    response = client.post("/api/tts", json={"text": "Test message"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["provider"] == "mock"
```

### Integration Tests (When F5-TTS Ready)

```python
# tests/test_tts_f5.py
@pytest.mark.asyncio
async def test_tts_f5_backend_quality():
    # Load actual model
    # Verify synthesis produces valid audio
    # Check output format (wav, mp3, etc.)
```

### Frontend Tests (Optional)

```tsx
// frontend/__tests__/audio-player.test.tsx
test("AudioPlayer plays audio when button clicked", async () => {
  const { getByText } = render(
    <AudioPlayer audioUrl="mock.mp3" duration={5000} />
  );
  fireEvent.click(getByText("Play Audio"));
  // Verify audio.play() was called
});
```

---

## Performance Considerations

| Aspect | Mock | F5-TTS | Notes |
|--------|------|--------|-------|
| Latency | <1ms | ~2-5s | Depends on text length & GPU |
| Memory | <10MB | ~1-2GB | Model weights in VRAM |
| Storage | None | ~500MB | Model + cache |
| Scalability | ∞ (instant) | Limited by GPU | May need queue/worker for many requests |

**Recommendations**:
- Add request timeout (e.g., 30s max for synthesis)
- Implement audio caching to avoid re-synthesis
- Consider async job queue (Celery, etc.) if request volume grows
- Monitor GPU memory if running locally

---

## Environment Variables (Updated)

```bash
# .env (backend)

# TTS Configuration
TTS_PROVIDER=mock              # "mock" (default) or "f5-tts" (future)
TTS_CACHE_DIR=cache/audio      # Directory for cached synthesized audio
TTS_MODEL_PATH=cache/models/f5-tts  # Model artifacts path (F5-TTS only)
```

---

## Rollout Checklist

- [ ] F5-TTS model downloaded and tested locally
- [ ] Dependencies added to `requirements.txt`
- [ ] `F5TTSBackend` implemented and unit tested
- [ ] Audio serving route created (`/api/audio/{audio_id}`)
- [ ] Voice profiles defined (if multi-voice)
- [ ] Frontend audio player component built
- [ ] End-to-end test (chat → TTS → playback)
- [ ] Performance benchmarked (latency, memory)
- [ ] Documentation updated
- [ ] Staging deployment tested
- [ ] Production rollout with feature flag (`TTS_PROVIDER=mock` initially, then `f5-tts`)

---

## References & Resources

- **F5-TTS**: [GitHub link TBD]
- **Audio formats**: WAV (uncompressed), MP3 (compressed), OGG (modern)
- **FastAPI file serving**: https://fastapi.tiangolo.com/advanced/custom-response/#other-file-types
- **WebAudio API**: https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API

---

## Questions & Decisions Pending

1. **Which audio format** should F5-TTS output? (WAV, MP3, OGG)
2. **Multi-voice support**? (default voice only vs. multiple profiles)
3. **Audio caching expiry**? (keep indefinitely or cleanup old files?)
4. **Streaming synthesis**? (get audio while generating, or wait for full synthesis?)
5. **Accessibility**: Alt text / transcript for audio?
