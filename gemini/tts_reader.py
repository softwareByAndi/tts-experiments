#!/usr/bin/env python3
"""
TTS script to read markdown files aloud using Google Gemini TTS API.
Usage: python tts_reader.py <markdown_file>
Requires GEMINI_API_KEY environment variable to be set.
"""

import sys
import os
import re
import tempfile
import subprocess
import wave
import base64
from pathlib import Path

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Error: Google Gemini AI library not installed.")
    print("Install with: pip install -q -U google-genai")
    sys.exit(1)

def clean_markdown_for_tts(text):
    """Remove markdown formatting and make text more TTS-friendly."""
    # Remove markdown headers
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
    
    # Remove markdown emphasis
    text = re.sub(r'\*\*(.*?)\**', r'\1', text)  # Bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)     # Italic
    text = re.sub(r'_(.*?)_', r'\1', text)       # Underscore italic
    
    # Remove markdown links but keep text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # Remove code blocks and inline code
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # Remove HTML-style comments
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    
    # Clean up extra whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = text.strip()
    
    return text

def load_api_key():
    """Load API key from secrets/gemini.api_key file or environment variable."""
    # Try loading from file first
    secrets_path = Path("secrets/gemini.api_key")
    if secrets_path.exists():
        try:
            with open(secrets_path, 'r', encoding='utf-8') as f:
                api_key = f.read().strip()
                if api_key:
                    return api_key
        except Exception as e:
            print(f"Warning: Could not read API key from {secrets_path}: {e}")
    
    # Fall back to environment variable
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        return api_key
    
    # No API key found
    print("Error: No API key found.")
    print("Either:")
    print("1. Create secrets/gemini.api_key file with your API key, or")
    print("2. Set GEMINI_API_KEY environment variable")
    print("Get your API key from: https://aistudio.google.com/app/apikey")
    sys.exit(1)

def generate_speech_with_gemini(text, voice_name="Kore"):
    """Generate speech from text using Google Gemini TTS API."""
    api_key = load_api_key()
    
    try:
        client = genai.Client(api_key=api_key)
        
        print(f"Generating speech with Gemini TTS (voice: {voice_name})...")
        
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice_name,
                        )
                    )
                ),
            )
        )
        
        # Get the audio data from the response
        audio_data = response.candidates[0].content.parts[0].inline_data.data
        return audio_data
        
    except Exception as e:
        print(f"Error generating speech: {e}")
        sys.exit(1)

def save_audio_data(audio_data, output_file):
    """Save audio data to a WAV file with proper formatting."""
    try:
        # Gemini TTS returns base64-encoded PCM data
        # Decode the base64 data
        if isinstance(audio_data, str):
            pcm_data = base64.b64decode(audio_data)
        else:
            pcm_data = audio_data
        
        # Gemini TTS audio specifications
        sample_rate = 24000
        channels = 1
        sample_width = 2  # 16-bit = 2 bytes
        
        # Create WAV file with proper header
        with wave.open(output_file, 'wb') as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(sample_width)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(pcm_data)
        
        print(f"Audio saved to: {output_file}")
        
    except Exception as e:
        print(f"Error saving audio: {e}")
        print(f"Audio data type: {type(audio_data)}")
        sys.exit(1)

def read_file_with_tts(filename, voice_name="Kore", output_file=None):
    """Read a markdown file and convert it to speech using Gemini TTS API."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Clean the content for TTS
        clean_content = clean_markdown_for_tts(content)
        
        # Check if content is too long (Gemini has token limits)
        if len(clean_content) > 30000:  # Conservative limit
            print("Warning: Content is very long. Consider splitting into smaller sections.")
        
        print(f"Converting {filename} to speech...")
        
        # Generate speech using Gemini TTS
        audio_data = generate_speech_with_gemini(clean_content, voice_name)
        
        # Generate output filename if not provided
        if not output_file:
            input_path = Path(filename)
            output_file = input_path.with_suffix('.wav').name
        
        # Save the generated audio
        save_audio_data(audio_data, output_file)
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nStopped processing.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def generate_voice_samples():
    """Generate test audio samples for all available voices."""
    # Available Gemini TTS voices
    voices = [
        "Kore",      # Balanced, natural
        "Puck",      # Upbeat, energetic
        "Charon",    # Informative, clear
        "Zephyr",    # Bright, cheerful
        "Aoede",     # Warm, expressive
        "Fenrir",    # Deep, authoritative
        "Bellona",   # Strong, confident
        "Coral",     # Gentle, soothing
        "Helios",    # Bold, dynamic
        "Neptune"    # Calm, steady
    ]
    
    test_text = """Maya Chen's fingers traced the stress calculations for the hundredth time. 
    The metamaterial cables were revolutionary in theory, but in practice, they kept developing 
    micro-fractures at resonance points that shouldn't exist. This was supposed to be her masterpiece."""
    
    print("Generating voice samples...")
    print(f"Test text: {test_text[:50]}...")
    
    for voice in voices:
        try:
            print(f"\nGenerating sample for {voice} voice...")
            output_file = f"voice_sample_{voice.lower()}.wav"
            
            # Generate speech using Gemini TTS
            audio_data = generate_speech_with_gemini(test_text, voice)
            
            # Save the generated audio
            save_audio_data(audio_data, output_file)
            
        except Exception as e:
            print(f"Error generating sample for {voice}: {e}")
            continue
    
    print("\nVoice samples generation complete!")
    print("Files generated:")
    for voice in voices:
        sample_file = f"voice_sample_{voice.lower()}.wav"
        if os.path.exists(sample_file):
            print(f"  - {sample_file}")
    
    print("\nListen to the samples to choose your preferred voice for the full audiobook.")

def main():
    # Check for special commands
    if len(sys.argv) == 2 and sys.argv[1] == "--voices":
        generate_voice_samples()
        return
    
    if len(sys.argv) < 2 or len(sys.argv) > 4:
        print("Usage: python tts_reader.py <markdown_file> [voice_name] [output_file]")
        print("       python tts_reader.py --voices  (generate voice samples)")
        print()
        print("Examples:")
        print("  python tts_reader.py chapter-01-opening.md")
        print("  python tts_reader.py chapter-01-opening.md Puck")
        print("  python tts_reader.py chapter-01-opening.md Kore chapter-01.wav")
        print("  python tts_reader.py --voices")
        print()
        print("Available voices: Kore, Puck, Charon, Zephyr, Aoede, Fenrir, Bellona, Coral, Helios, Neptune")
        print("Output file defaults to input filename with .wav extension")
        print("API key loaded from secrets/gemini.api_key or GEMINI_API_KEY env var.")
        sys.exit(1)
    
    filename = sys.argv[1]
    voice_name = sys.argv[2] if len(sys.argv) >= 3 else "Kore"
    output_file = sys.argv[3] if len(sys.argv) == 4 else None
    
    read_file_with_tts(filename, voice_name, output_file)

if __name__ == "__main__":
    main()
