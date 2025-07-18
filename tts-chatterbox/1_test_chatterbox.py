#!/usr/bin/env python3
"""
Simple Chatterbox TTS test - just make it talk
Requires: pip install chatterbox-tts torch torchaudio
"""

import torchaudio as ta
from chatterbox.tts import ChatterboxTTS

OUTPUT_PATH = "outputs/output_test_1.wav"

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

wav = model.generate(text)
ta.save(OUTPUT_PATH, wav, model.sr)

print("Done! Audio saved to output.wav")