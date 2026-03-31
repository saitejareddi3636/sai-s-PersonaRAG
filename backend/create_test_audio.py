#!/usr/bin/env python3
import struct
import os

os.makedirs("tests/fixtures", exist_ok=True)

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
wav_data.extend(struct.pack('<H', 1))
wav_data.extend(struct.pack('<H', num_channels))
wav_data.extend(struct.pack('<I', sample_rate))
wav_data.extend(struct.pack('<I', sample_rate * num_channels * bytes_per_sample))
wav_data.extend(struct.pack('<H', num_channels * bytes_per_sample))
wav_data.extend(struct.pack('<H', 16))
wav_data.extend(b'data')
wav_data.extend(struct.pack('<I', subchunk2_size))
wav_data.extend(b'\x00' * subchunk2_size)

with open('tests/fixtures/test_audio.wav', 'wb') as f:
    f.write(wav_data)

print(f'✓ Test audio created: {len(wav_data)} bytes (16kHz mono, 500ms silence)')
