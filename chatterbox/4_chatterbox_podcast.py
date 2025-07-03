#!/usr/bin/env python3
"""
Chatterbox TTS from file - reads text from input file and splits long lines
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
INPUT_FILE = "inputs/test.md"  # Default input file
OUTPUT_DIR = "outputs/file_test_1"  # Default output file
MAX_LINE_LENGTH = 600  # Maximum characters per line before splitting
VOICE_PATHS = {
    'DEFAULT': "inputs/voice_clone_samples/default.wav",
    'achernar': "inputs/voice_clone_samples/achernar.wav"
}

def split_long_line(line, max_length=MAX_LINE_LENGTH):
    """Split a line if it's longer than max_length, preferring punctuation breaks."""
    if len(line) <= max_length:
        return [line]
    
    # Find punctuation marks to split on
    punctuation_pattern = r'[.!?;:]'
    matches = list(re.finditer(punctuation_pattern, line))
    
    if not matches:
        # No punctuation found, split at halfway point
        mid = len(line) // 2
        return [line[:mid].strip(), line[mid:].strip()]
    
    # Find the punctuation mark closest to the middle
    mid = len(line) // 2
    best_split = min(matches, key=lambda m: abs(m.end() - mid))
    split_pos = best_split.end()
    
    # Split at the best punctuation mark
    part1 = line[:split_pos].strip()
    part2 = line[split_pos:].strip()
    
    # Recursively split if parts are still too long
    result = []
    result.extend(split_long_line(part1, max_length))
    result.extend(split_long_line(part2, max_length))
    
    return result

def process_text_file(filepath):
    """Read and process text file, splitting long lines."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    processed_lines = []
    for line in lines:
        line = line.strip()
        if line:  # Skip empty lines
            split_lines = split_long_line(line)
            processed_lines.extend(split_lines)
    
    return processed_lines

def main():
    # Use command line args if provided, otherwise use defaults
    input_file = sys.argv[1] if len(sys.argv) > 1 else INPUT_FILE
    output_dir = sys.argv[2] if len(sys.argv) > 2 else OUTPUT_DIR
    
    # Process text file
    print(f"Reading text from: {input_file}")
    text_lines = process_text_file(input_file)
    
    if not text_lines:
        print("Error: No text found in file.")
        sys.exit(1)
    
    print(f"Processed {len(text_lines)} lines of text")
    print(f"Total text length: {len(" ".join(text_lines))} characters")
    
    # Load model
    print("\nLoading Chatterbox TTS...")
    device = "cuda" if hasattr(ta, 'cuda') and ta.cuda.is_available() else "cpu"
    model = ChatterboxTTS.from_pretrained(device=device)
    print(f"Device: {device}")
    
    # Generate speech
    print("\nGenerating speech...")
    if not os.path.exists(output_dir):
      os.makedirs(output_dir)
    
    # Create a queue for saving files asynchronously
    save_queue = queue.Queue()
    
    def save_audio(filepath, wav_data, sample_rate):
        """Save audio file in background."""
        ta.save(filepath, wav_data, sample_rate)
        print(f"✓ Saved: {os.path.basename(filepath)}")
    
    # Use thread pool for asynchronous file saving
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = []
        
        user = 'DEFAULT'
        for i, line in enumerate(text_lines):
            if line[0] == '<':
                user = line[1:-1]
                continue
            if i < 10:
                print(f"[{i+1}/{len(text_lines)}] Generating audio for line {i}...")
                wav = model.generate(line, audio_prompt_path=VOICE_PATHS[user])
                
                # Submit save task to thread pool
                filepath = f"{output_dir}/{i}.wav"
                future = executor.submit(save_audio, filepath, wav, model.sr)
                futures.append(future)
                
                print(f"→ Submitted save task for {os.path.basename(filepath)}")
        
        # Wait for all saves to complete
        print("\nWaiting for all saves to complete...")
        for future in futures:
            future.result()
    
    print(f"\nDone! All {len(text_lines)} audio files saved to {output_dir}")

if __name__ == "__main__":
    main()