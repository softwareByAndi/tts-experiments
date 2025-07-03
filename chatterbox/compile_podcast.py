#!/usr/bin/env python3
import os
import sys
import torch
import torchaudio as ta
from pathlib import Path

DEFAULT_GAP_SECONDS = -0.5
INPUT_DIR = "outputs/nanite-podcast"
OUTPUT_FILE = "outputs/nanite-podcast-compiled.wav"
OVERLAP_FADE = 0.9

def compile_audio_files(input_dir, output_file, gap_seconds=0.5):
    """
    Compile multiple WAV files with gaps or overlaps between them.
    
    Args:
        input_dir: Directory containing WAV files
        output_file: Output compiled WAV file
        gap_seconds: Gap/overlap in seconds between files (default 0.5)
                        Positive values create gaps, negative values create overlaps
    """
    # Get all WAV files and sort them numerically
    wav_files = []
    for filename in os.listdir(input_dir):
        if filename.endswith('.wav'):
            # Extract number from filename for proper sorting
            num = int(filename.replace('.wav', ''))
            wav_files.append((num, filename))
    
    # Sort by number
    wav_files.sort(key=lambda x: x[0])
    wav_files = [f[1] for f in wav_files]
    
    print(wav_files)
    
    if not wav_files:
        print("No WAV files found in the directory")
        return
    
    print(f"Found {len(wav_files)} WAV files to compile")
    
    # Read first file to get audio parameters
    first_file = os.path.join(input_dir, wav_files[0])
    waveform, sample_rate = ta.load(first_file)
    
    # Get number of channels
    num_channels = waveform.shape[0]
    
    # Calculate overlap in samples (negative for overlap, positive for gap)
    gap_samples = int(gap_seconds * sample_rate)
    
    # Load all audio files first
    audio_segments = []
    for i, filename in enumerate(wav_files):
        filepath = os.path.join(input_dir, filename)
        print(f"Loading {i+1}/{len(wav_files)}: {filename}")
        
        # Load audio file
        waveform, file_sample_rate = ta.load(filepath)
        
        # Verify parameters match
        if file_sample_rate != sample_rate or waveform.shape[0] != num_channels:
            print(f"Warning: {filename} has different audio parameters, skipping")
            continue
        
        audio_segments.append(waveform)
    
    if not audio_segments:
        print("No valid audio segments found")
        return
    
    # Calculate total length needed
    total_length = 0
    for i, segment in enumerate(audio_segments):
        if i == 0:
            total_length += segment.shape[1]
        else:
            # Add length minus overlap
            total_length += segment.shape[1] - max(0, -gap_samples)
    
    # Create output tensor
    compiled_audio = torch.zeros(num_channels, total_length)
    
    # Place audio segments with overlaps
    current_pos = 0
    prev_segment_length = 0
    for i, segment in enumerate(audio_segments):
        segment_length = segment.shape[1]
        
        if i == 0:
            print(f"{i} : ({segment_length}) {current_pos} - begin")
            # First segment starts at beginning
            compiled_audio[:, :segment_length] = segment
            current_pos = segment_length
        else:
            # Calculate start position based on overlap
            start_pos = current_pos + gap_samples
            end_pos = start_pos + segment_length
            if prev_segment_length <= (gap_samples * 2):
                print(f"{i} : ({segment_length}) {current_pos} - gapless append")
                # No actual overlap, just place the segment
                end_pos = current_pos + segment_length
                compiled_audio[:, current_pos:end_pos] = segment
            elif gap_samples >= 0:
                # Positive overlap - gap between segments
                compiled_audio[:, start_pos:end_pos] = segment
            else:
                # Negative gap = overlap between segments
                # Calculate how much the segments overlap
                overlap_samples = -gap_samples
                overlap_length = min(overlap_samples, segment_length) # incase segment is shorter than overlap
                
                print(f"{i} : ({segment_length}) {current_pos} - ({overlap_samples}) {overlap_length}")
        
                if overlap_length <= 0 or prev_segment_length < gap_samples:
                    # No actual overlap, just place the segment
                    compiled_audio[:, start_pos:end_pos] = segment
                else:
                    # Blend the overlapping portions (50/50 mix)
                    overlap_pos = current_pos - overlap_length
                    compiled_audio[:, overlap_pos:current_pos] = (
                        compiled_audio[:, overlap_pos:current_pos] * OVERLAP_FADE +
                        segment[:, :overlap_length] * OVERLAP_FADE
                    )
                    
                    # Add the rest of the segment after the overlap
                    if overlap_length < segment_length:
                        remaining_audio = segment[:, overlap_length:]
                        remaining_length = remaining_audio.shape[1]
                        end_pos = current_pos + remaining_length
                        compiled_audio[:, current_pos:end_pos] = remaining_audio
            
            current_pos = end_pos
        
        prev_segment_length = segment_length
    
    # Save compiled audio
    ta.save(output_file, compiled_audio, sample_rate)
    
    print(f"\nSuccessfully compiled {len(wav_files)} files into {output_file}")
    
    # Calculate total duration
    duration = compiled_audio.shape[1] / float(sample_rate)
    minutes = int(duration // 60)
    seconds = duration % 60
    print(f"Total duration: {minutes}:{seconds:05.2f}")

if __name__ == "__main__":
    # Use command line args if provided, otherwise use defaults
    input_directory = sys.argv[1] if len(sys.argv) > 1 else INPUT_DIR
    output_filename = sys.argv[2] if len(sys.argv) > 2 else OUTPUT_FILE
    gap_seconds     = float(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_GAP_SECONDS
    
    # Use negative value for overlap (e.g., -0.5 for 0.5 second overlap)
    # Use positive value for gap (e.g., 0.5 for 0.5 second gap)
    compile_audio_files(input_directory, output_filename, gap_seconds)