#!/usr/bin/env python3
"""
Batch processing Chatterbox TTS - groups by voice to minimize switching
"""

import os
import sys
from collections import defaultdict
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS

INPUT_FILE = "inputs/test.md"
OUTPUT_DIR = "outputs/batch_by_voice"
VOICE_PATHS = {
    'DEFAULT': "inputs/voice_clone_samples/default.wav",
    'achernar': "inputs/voice_clone_samples/achernar.wav"
}

def parse_dialogue(filepath):
    """Parse dialogue file and group lines by speaker"""
    speakers_lines = defaultdict(list)
    current_speaker = 'DEFAULT'
    line_order = []  # Track original order
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('<') and line.endswith('>'):
                current_speaker = line[1:-1]
            else:
                speakers_lines[current_speaker].append((i, line))
                line_order.append((i, current_speaker, line))
    
    return speakers_lines, line_order

def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else INPUT_FILE
    output_dir = sys.argv[2] if len(sys.argv) > 2 else OUTPUT_DIR
    
    # Parse dialogue
    print(f"Parsing dialogue from: {input_file}")
    speakers_lines, line_order = parse_dialogue(input_file)
    
    print(f"\nFound {len(speakers_lines)} speakers:")
    for speaker, lines in speakers_lines.items():
        print(f"  {speaker}: {len(lines)} lines")
    
    # Load model
    print("\nLoading Chatterbox TTS...")
    device = "cuda" if hasattr(ta, 'cuda') and ta.cuda.is_available() else "cpu"
    model = ChatterboxTTS.from_pretrained(device=device)
    print(f"Device: {device}")
    
    # Create output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Process each speaker's lines in batch
    audio_cache = {}
    
    for speaker, lines in speakers_lines.items():
        voice_path = VOICE_PATHS.get(speaker, VOICE_PATHS['DEFAULT'])
        print(f"\nProcessing {speaker} ({len(lines)} lines)...")
        
        for idx, (line_num, text) in enumerate(lines):
            print(f"  [{idx+1}/{len(lines)}] Line {line_num}")
            wav = model.generate(text, audio_prompt_path=voice_path)
            audio_cache[line_num] = wav
    
    # Save in original order
    print("\nSaving audio files in original order...")
    for i, (line_num, speaker, text) in enumerate(line_order):
        if line_num in audio_cache:
            filepath = f"{output_dir}/{i:03d}_{speaker}.wav"
            ta.save(filepath, audio_cache[line_num], model.sr)
            print(f"✓ Saved: {os.path.basename(filepath)}")
    
    print(f"\nDone! Audio files saved to {output_dir}")

if __name__ == "__main__":
    main()