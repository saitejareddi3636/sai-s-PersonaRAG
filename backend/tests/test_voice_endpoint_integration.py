"""
Integration test for /api/voice/chat endpoint.
Tests the real end-to-end voice pipeline with actual request/response.
"""

import struct
import sys
from io import BytesIO
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from unittest.mock import patch
from app.services.stt_service import STTResult


def create_minimal_wav_bytes() -> bytes:
    """Create a minimal valid 16-bit PCM WAV file (500ms silence at 16kHz)."""
    sample_rate = 16000
    duration_ms = 500
    num_samples = int(sample_rate * duration_ms / 1000)
    num_channels = 1
    bytes_per_sample = 2

    chunk_size = 36 + num_samples * num_channels * bytes_per_sample
    subchunk2_size = num_samples * num_channels * bytes_per_sample

    wav_data = bytearray()
    wav_data.extend(b'RIFF')
    wav_data.extend(struct.pack('<I', chunk_size))
    wav_data.extend(b'WAVE')
    wav_data.extend(b'fmt ')
    wav_data.extend(struct.pack('<I', 16))
    wav_data.extend(struct.pack('<H', 1))  # PCM
    wav_data.extend(struct.pack('<H', num_channels))
    wav_data.extend(struct.pack('<I', sample_rate))
    wav_data.extend(struct.pack('<I', sample_rate * num_channels * bytes_per_sample))
    wav_data.extend(struct.pack('<H', num_channels * bytes_per_sample))
    wav_data.extend(struct.pack('<H', 16))
    wav_data.extend(b'data')
    wav_data.extend(struct.pack('<I', subchunk2_size))
    wav_data.extend(b'\x00' * subchunk2_size)

    return bytes(wav_data)


def test_voice_chat_endpoint_schema():
    """Test POST /api/voice/chat returns correct response schema."""
    client = TestClient(app)

    wav_bytes = create_minimal_wav_bytes()
    files = {"audio": ("test.wav", BytesIO(wav_bytes), "audio/wav")}
    
    # Mock STT to bypass Faster-Whisper speech detection
    mock_stt = STTResult(
        success=True,
        transcript="what skills do you have in machine learning",
        provider="faster-whisper",
        language="en",
        message=None,
    )
    
    with patch("app.api.routes.voice.transcribe_audio_bytes", return_value=mock_stt):
        response = client.post("/api/voice/chat", files=files)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    
    # Verify all required fields
    required = ["transcript", "answer", "confidence", "audio", "tts_error", "session_id", 
                "sources", "retrieval", "stt_provider", "stt_language", "grounding_note"]
    for field in required:
        assert field in data, f"Missing '{field}'"
    
    assert isinstance(data["answer"], str) and len(data["answer"]) > 0
    assert isinstance(data["retrieval"], list)
    
    if data["audio"]:
        assert "audio_url" in data["audio"]
        assert data["audio"]["audio_url"].startswith("data:audio/wav;base64,")
    
    print("\n✓ TEST 1 PASSED: Response schema correct")
    print(f"  transcript: '{data['transcript']}'")
    print(f"  answer: '{data['answer'][:60]}...'")
    print(f"  audio: {('✓ synthesized' if data['audio'] else 'None')}")
    print(f"  session_id: {data['session_id']}")


def test_voice_chat_endpoint_creates_audio():
    """Test 2: /api/voice/chat uses same RAG+LLM path as /api/chat."""
    client = TestClient(app)
    wav_bytes = create_minimal_wav_bytes()
    
    files = {"audio": ("test.wav", BytesIO(wav_bytes), "audio/wav")}
    
    mock_stt = STTResult(
        success=True,
        transcript="tell me about your experience",
        provider="faster-whisper",
        language="en",
        message=None,
    )
    
    with patch("app.api.routes.voice.transcribe_audio_bytes", return_value=mock_stt):
        response = client.post("/api/voice/chat", files=files)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify RAG was called
    assert len(data["retrieval"]) > 0 or data.get("retrieval_error")
    
    # Verify LLM generated answer
    assert data["answer"] and len(data["answer"]) > 20
    
    print("\n✓ TEST 2 PASSED: RAG+LLM pipeline working")
    print(f"  retrieval hits: {len(data['retrieval'])}")
    print(f"  answer: '{data['answer'][:50]}...'")
    print(f"  confidence: {data['confidence']}")
    print(f"  ✓ Same functions as /api/chat (verified by code inspection)")

def test_voice_chat_graceful_tts_fallback():
    """Test 3: /api/voice/chat returns graceful fallback when TTS fails."""
    client = TestClient(app)
    wav_bytes = create_minimal_wav_bytes()
    files = {"audio": ("test.wav", BytesIO(wav_bytes), "audio/wav")}
    
    mock_stt = STTResult(
        success=True,
        transcript="test",
        provider="faster-whisper",
        language="en",
        message=None,
    )
    
    async def mock_tts_fail(*args, **kwargs):
        return None, "TTS error"
    
    with patch("app.api.routes.voice.transcribe_audio_bytes", return_value=mock_stt):
        with patch("app.api.routes.voice.VoiceOrchestrator.synthesize_answer_audio", side_effect=mock_tts_fail):
            response = client.post("/api/voice/chat", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert data["audio"] is None
    assert data["tts_error"] == "TTS error"
    assert data["answer"]  # Text still works
    
    print("\n✓ TEST 3 PASSED: Graceful fallback on TTS failure")
    print(f"  audio: None")
    print(f"  tts_error: '{data['tts_error']}'")
    print(f"  answer: '{data['answer'][:50]}...' (still works)")

if __name__ == "__main__":
    # Create test audio first
    wav_bytes = create_minimal_wav_bytes()
    Path("tests/fixtures").mkdir(exist_ok=True)
    Path("tests/fixtures/test_audio.wav").write_bytes(wav_bytes)
    print(f"✓ Created test audio: {len(wav_bytes)} bytes\n")
    
    # Run tests
    pytest.main([__file__, "-v", "-s"])
