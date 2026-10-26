# /// script
# requires-python = ">=3.10"
# dependencies = ["faster-whisper"]
# ///
"""Usage: transcribe.py <video> [model]. Prints a timestamped transcript to stdout."""
import sys

from faster_whisper import WhisperModel

model = WhisperModel(sys.argv[2] if len(sys.argv) > 2 else "small", device="auto", compute_type="int8")
segments, info = model.transcribe(sys.argv[1], vad_filter=True)
lines = [f"[{int(s.start) // 60:02d}:{int(s.start) % 60:02d}] {s.text.strip()}" for s in segments]
print(f"(Whisper, language: {info.language})")
print("\n".join(lines) or "(no speech detected)")
