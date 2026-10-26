# /// script
# requires-python = ">=3.10"
# dependencies = ["faster-whisper", "numpy"]
# ///
"""Usage: transcribe.py <16 kHz mono wav> [model]. Prints a timestamped transcript to stdout."""
import sys
import wave

import numpy as np
from faster_whisper import WhisperModel

# The server extracts the audio with ffmpeg: faster-whisper's own decoder (PyAV) breaks with some av versions
with wave.open(sys.argv[1]) as w:
    audio = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
name = sys.argv[2] if len(sys.argv) > 2 else "small"


def run(device):
    segments, info = WhisperModel(name, device=device, compute_type="int8").transcribe(audio, vad_filter=True)
    return list(segments), info


try:
    segments, info = run("auto")
except RuntimeError:  # a GPU is visible but its CUDA libraries (cublas, cudnn) are missing
    segments, info = run("cpu")
lines = [f"[{int(s.start) // 60:02d}:{int(s.start) % 60:02d}] {s.text.strip()}" for s in segments]
print(f"(Whisper, language: {info.language})")
print("\n".join(lines) or "(no speech detected)")
