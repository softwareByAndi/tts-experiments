#!/usr/bin/env python3
"""
Simple Chatterbox TTS test - just make it talk
Requires: pip install chatterbox-tts torch torchaudio
"""

import torchaudio as ta
from chatterbox.tts import ChatterboxTTS

OUTPUT_PATH = "outputs/output_custom_voice.wav"

# Load model
print("Loading Chatterbox TTS...")
device = "cuda" if hasattr(ta, 'cuda') and ta.cuda.is_available() else "cpu"
model = ChatterboxTTS.from_pretrained(device=device)

print(f"device: {device}")

# Generate speech
text = """
Welcome to Tech Talk Today. I'm your host, and today we're diving into ARM architecture. You've probably heard this term thrown around, especially when talking about smartphones, tablets, and even some laptops. But what exactly is ARM, and why should you care? Let's break it down in simple terms.
"""

print(f"Generating speech: {text}")

# Generate with default voice
# wav = model.generate(text)
# ta.save(OUTPUT_PATH, wav, model.sr)

# Generate with custom voice using audio reference
# Uncomment and provide a voice sample path:
# VOICE_SAMPLE_PATH = "../voice_samples/voice_sample_kore.wav"
VOICE_SAMPLE_PATH = "voices/achernar.wav"
wav = model.generate(text, audio_prompt_path=VOICE_SAMPLE_PATH)
ta.save(OUTPUT_PATH, wav, model.sr)

print(f"Done! Audio saved to {OUTPUT_PATH}")