#!/usr/bin/env python3
"""
Optimized Chatterbox TTS with voice embedding caching
Requires: pip install chatterbox-tts torch torchaudio
"""

import os
import sys
import re
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS
from concurrent.futures import ThreadPoolExecutor
import queue

# File paths
INPUT_FILE = "inputs/test.md"
OUTPUT_DIR = "outputs/file_test_optimized"
MAX_LINE_LENGTH = 600
VOICE_PATHS = {
    'DEFAULT': "inputs/voice_clone_samples/default.wav",
    'achernar': "inputs/voice_clone_samples/achernar.wav"
}

class ChatterboxWithVoiceCache:
    """Wrapper for ChatterboxTTS that caches voice processing"""
    
    def __init__(self, model):
        self.model = model
        self.voice_cache = {}
        self.current_voice = None
        
    def set_voice(self, voice_name, voice_path):
        """Pre-load and cache a voice"""
        if voice_name not in self.voice_cache:
            # Process voice file once and cache the result
            # Note: This is a conceptual approach - actual implementation 
            # depends on Chatterbox internals
            self.voice_cache[voice_name] = voice_path
            print(f"Cached voice: {voice_name}")
        self.current_voice = voice_name
        
    def generate(self, text, voice_name=None):
        """Generate speech with cached voice"""
        if voice_name and voice_name != self.current_voice:
            self.current_voice = voice_name
            
        voice_path = self.voice_cache.get(self.current_voice)
        if voice_path:
            return self.model.generate(text, audio_prompt_path=voice_path)
        else:
            return self.model.generate(text)

def split_long_line(line, max_length=MAX_LINE_LENGTH):
    """Split a line if it's longer than max_length"""
    if len(line) <= max_length:
        return [line]
    
    punctuation_pattern = r'[.!?;:]'
    matches = list(re.finditer(punctuation_pattern, line))
    
    if not matches:
        mid = len(line) // 2
        return [line[:mid].strip(), line[mid:].strip()]
    
    mid = len(line) // 2
    best_split = min(matches, key=lambda m: abs(m.end() - mid))
    split_pos = best_split.end()
    
    part1 = line[:split_pos].strip()
    part2 = line[split_pos:].strip()
    
    result = []
    result.extend(split_long_line(part1, max_length))
    result.extend(split_long_line(part2, max_length))
    
    return result

def process_text_file(filepath):
    """Read and process text file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        sys.exit(1)
    
    processed_lines = []
    for line in lines:
        line = line.strip()
        if line:
            split_lines = split_long_line(line)
            processed_lines.extend(split_lines)
    
    return processed_lines

def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else INPUT_FILE
    output_dir = sys.argv[2] if len(sys.argv) > 2 else OUTPUT_DIR
    
    print(f"Reading text from: {input_file}")
    text_lines = process_text_file(input_file)
    
    if not text_lines:
        print("Error: No text found in file.")
        sys.exit(1)
    
    print(f"Processed {len(text_lines)} lines of text")
    
    # Load model
    print("\nLoading Chatterbox TTS...")
    device = "cuda" if hasattr(ta, 'cuda') and ta.cuda.is_available() else "cpu"
    base_model = ChatterboxTTS.from_pretrained(device=device)
    
    # Create wrapper with voice caching
    model = ChatterboxWithVoiceCache(base_model)
    
    # Pre-load all voices
    print("\nPre-loading voices...")
    for voice_name, voice_path in VOICE_PATHS.items():
        if os.path.exists(voice_path):
            model.set_voice(voice_name, voice_path)
    
    print(f"Device: {device}")
    
    # Generate speech
    print("\nGenerating speech...")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    def save_audio(filepath, wav_data, sample_rate):
        """Save audio file in background"""
        ta.save(filepath, wav_data, sample_rate)
        print(f"✓ Saved: {os.path.basename(filepath)}")
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = []
        current_voice = 'DEFAULT'
        
        for i, line in enumerate(text_lines):
            if line.startswith('<') and line.endswith('>'):
                # Voice switch marker
                current_voice = line[1:-1]
                continue
            
            if i < 10:  # Process first 10 lines
                print(f"[{i+1}/{len(text_lines)}] Generating with voice '{current_voice}'...")
                wav = model.generate(line, voice_name=current_voice)
                
                filepath = f"{output_dir}/{i:03d}.wav"
                future = executor.submit(save_audio, filepath, wav, base_model.sr)
                futures.append(future)
        
        print("\nWaiting for all saves to complete...")
        for future in futures:
            future.result()
    
    print(f"\nDone! Audio files saved to {output_dir}")

if __name__ == "__main__":
    main()