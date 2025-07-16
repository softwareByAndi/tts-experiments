#!/usr/bin/env python3
"""
Simple Piper TTS Test Script

Tests basic Piper text-to-speech functionality with minimal complexity.
Following KISS principles for clarity and maintainability.
"""

import argparse
import sys
import wave
from pathlib import Path

try:
    from piper import PiperVoice
    from piper.config import SynthesisConfig
except ImportError as e:
    print(f"Error: Piper not installed. Run: pip install piper-tts")
    sys.exit(1)

# Available voices (based on files in voices directory)
VOICES = {
    "lessac": "en_US-lessac-medium",
    "lessac-high": "en_US-lessac-high",
    "alba": "en_GB-alba-medium",
    "ljspeech": "en_US-ljspeech-high",
    "semaine": "en_GB-semaine-medium",
    "cori": "en_GB-cori-high",
    "southern": "en_GB-southern_english_female-low",
    "arctic": "en_US-arctic-medium",
    "bryce": "en_US-bryce-medium",
    "norman": "en_US-norman-medium",
    "ryan": "en_US-ryan-high"
}

# Default configuration
DEFAULT_VOICE = VOICES["cori"]
DEFAULT_OUTPUT_DIR = "outputs"
VOICE_DIR = "voices"

# Test texts with settings
TEST_TEXTS = {
    "basic": ("Hello! This is a test of Piper text-to-speech.", {}),
    "slow_quiet": ("This speech is slower and quieter than normal.", 
                   {"volume": 0.5, "length_scale": 1.5}),
    "fast_loud": ("This speech is faster and louder!", 
                  {"volume": 1.5, "length_scale": 0.8}),
    "robotic": ("This speech sounds more robotic.", 
                {"noise_scale": 0.0, "noise_w_scale": 0.0}),
    "expressive": ("This speech has more expression and variation!", 
                   {"noise_scale": 1.0, "noise_w_scale": 1.0}),
}


def load_voice(voice_key):
    """Load Piper voice model."""
    voice_name = VOICES.get(voice_key, voice_key)  # Support both key and full name
    voice_path = Path(VOICE_DIR) / f"{voice_name}.onnx"
    
    if not voice_path.exists():
        print(f"Error: Voice file not found at {voice_path}")
        print(f"Run: python3 -m piper.download {voice_name} --output-dir {VOICE_DIR}")
        return None
    
    try:
        return PiperVoice.load(str(voice_path))
    except Exception as e:
        print(f"Error loading voice: {e}")
        return None


def synthesize_text(voice, text, output_path, config=None):
    """Synthesize text to WAV file."""
    try:
        with wave.open(str(output_path), "wb") as wav_file:
            voice.synthesize_wav(text, wav_file, syn_config=config)
        return True
    except Exception as e:
        print(f"Error synthesizing: {e}")
        return False


def test_streaming(voice, text):
    """Test streaming synthesis."""
    try:
        chunks = list(voice.synthesize(text))
        return len(chunks), sum(len(c.audio_int16_bytes) for c in chunks)
    except Exception as e:
        print(f"Error in streaming: {e}")
        return 0, 0


def main():
    parser = argparse.ArgumentParser(description="Test Piper TTS")
    parser.add_argument("--voice", choices=list(VOICES.keys()), default=DEFAULT_VOICE,
                        help="Voice model to use")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="Output directory")
    parser.add_argument("--test", choices=["all", "basic", "config", "streaming"], 
                        default="all", help="Test type to run")
    args = parser.parse_args()
    
    # Setup
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    voice = load_voice(args.voice)
    if not voice:
        return 1
    
    print(f"Loaded voice: {args.voice}")
    passed = 0
    total = 0
    
    # Run tests
    if args.test in ["all", "basic"]:
        total += 1
        text, _ = TEST_TEXTS["basic"]
        output_path = output_dir / "test_basic.wav"
        
        if synthesize_text(voice, text, output_path):
            size = output_path.stat().st_size
            print(f"✓ Basic synthesis: {size} bytes")
            passed += 1
        else:
            print("✗ Basic synthesis failed")
    
    if args.test in ["all", "config"]:
        for name, (text, settings) in TEST_TEXTS.items():
            if name == "basic":
                continue
                
            total += 1
            output_path = output_dir / f"test_{name}.wav"
            
            config = SynthesisConfig(**settings) if settings else None
            
            if synthesize_text(voice, text, output_path, config):
                print(f"✓ Config test '{name}': success")
                passed += 1
            else:
                print(f"✗ Config test '{name}': failed")
    
    if args.test in ["all", "streaming"]:
        total += 1
        text = "This is a streaming synthesis test. Each chunk contains audio data."
        chunks, total_bytes = test_streaming(voice, text)
        
        if chunks > 0:
            print(f"✓ Streaming: {chunks} chunks, {total_bytes} bytes")
            passed += 1
        else:
            print("✗ Streaming failed")
    
    # Summary
    print(f"\nTotal: {passed}/{total} tests passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())