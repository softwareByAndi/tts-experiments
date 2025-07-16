import os
import sys
import subprocess
from pathlib import Path
import tempfile
import json

def normalize_trim_merge_audio(input_folder, output_file="merged_normalized.mp3", 
                             buffer_duration=0, silence_threshold="-50dB", 
                             min_silence_duration=0, target_level=-16):
    """
    Trim silence first, then normalize and merge audio files.
    
    Args:
        input_folder (str): Path to the folder containing audio files
        output_file (str): Name of the output file (default: merged_normalized.mp3)
        buffer_duration (float): Duration of the buffer in seconds (default: 0 seconds)
        silence_threshold (str): Threshold for silence detection (default: -50dB)
        min_silence_duration (float): Minimum silence duration to trim (default: 0 seconds)
        target_level (int): Target loudness level in LUFS (default: -16 LUFS, good for speech)
    """
    # Convert input folder to Path object
    input_path = Path(input_folder)
    
    # Check if the folder exists
    if not input_path.exists() or not input_path.is_dir():
        print(f"Error: '{input_folder}' is not a valid directory")
        return
    
    # Create output file path
    if not output_file.endswith('.mp3'):
        output_file += '.mp3'
    output_path = input_path / output_file
    
    # Get all audio files in the directory
    audio_extensions = {'.wav', '.mp3', '.ogg', '.flac', '.aac'}
    audio_files = [f for f in input_path.iterdir() 
                  if f.is_file() and f.suffix.lower() in audio_extensions]
    
    # Sort files by name
    audio_files.sort()
    
    if not audio_files:
        print(f"No audio files found in '{input_folder}'")
        return
    
    print(f"Found {len(audio_files)} audio files to process")
    
    # Create a temporary directory for processed files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create silence file if buffer is needed
        silence_path = temp_path / "silence.wav"
        if buffer_duration > 0:
            subprocess.run([
                "ffmpeg", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo", 
                "-t", str(buffer_duration), 
                str(silence_path)
            ], check=True, stderr=subprocess.PIPE)
        
        # Process each audio file
        print("\nProcessing audio files...")
        processed_files = []
        
        for i, audio_file in enumerate(audio_files):
            print(f"Processing [{i+1}/{len(audio_files)}]: {audio_file.name}")
            
            # Step 1: Trim silence first
            trimmed_file = temp_path / f"trim_{i:03d}_{audio_file.name}"
            subprocess.run([
                "ffmpeg", "-i", str(audio_file),
                "-af", f"silenceremove=start_periods=1:start_threshold={silence_threshold}:"
                       f"start_silence={min_silence_duration}:detection=peak,"
                       f"areverse,silenceremove=start_periods=1:start_threshold={silence_threshold}:"
                       f"start_silence={min_silence_duration}:detection=peak,areverse",
                "-ar", "44100", "-y", str(trimmed_file)
            ], check=True, stderr=subprocess.PIPE)
            
            # Step 2: Normalize the trimmed file
            normalized_file = temp_path / f"norm_{i:03d}_{audio_file.name}"
            
            # Measure loudness
            result = subprocess.run([
                "ffmpeg", "-i", str(trimmed_file), "-af", "loudnorm=print_format=json", 
                "-f", "null", "-"
            ], check=True, stderr=subprocess.PIPE, text=True)
            
            # Extract the JSON data from ffmpeg's stderr output
            stderr = result.stderr
            json_start = stderr.rfind('{')
            json_end = stderr.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_data = stderr[json_start:json_end]
                loudness_info = json.loads(json_data)
                
                # Apply normalization with measured values
                subprocess.run([
                    "ffmpeg", "-i", str(trimmed_file),
                    "-af", f"loudnorm=I={target_level}:TP=-1.5:LRA=11:"
                           f"measured_I={loudness_info.get('input_i', '0')}:"
                           f"measured_TP={loudness_info.get('input_tp', '0')}:"
                           f"measured_LRA={loudness_info.get('input_lra', '0')}:"
                           f"measured_thresh={loudness_info.get('input_thresh', '0')}:"
                           f"linear=true:print_format=summary",
                    "-ar", "44100", "-y", str(normalized_file)
                ], check=True, stderr=subprocess.PIPE)
            else:
                # Fallback normalization
                subprocess.run([
                    "ffmpeg", "-i", str(trimmed_file),
                    "-af", f"loudnorm=I={target_level}:TP=-1.5:LRA=11:linear=true",
                    "-ar", "44100", "-y", str(normalized_file)
                ], check=True, stderr=subprocess.PIPE)
            
            processed_files.append(normalized_file)
        
        # Create concat file for ffmpeg
        concat_file = temp_path / "concat_list.txt"
        
        with open(concat_file, "w") as f:
            # Add first file
            f.write(f"file '{processed_files[0].absolute()}'\n")
            
            # Add buffer and subsequent files
            for processed_file in processed_files[1:]:
                if buffer_duration > 0:
                    f.write(f"file '{silence_path.absolute()}'\n")
                f.write(f"file '{processed_file.absolute()}'\n")
        
        # Concatenate everything
        print(f"\nMerging processed files to {output_path}")
        subprocess.run([
            "ffmpeg", "-f", "concat", "-safe", "0", 
            "-i", str(concat_file), "-c:a", "libmp3lame", "-q:a", "2",
            str(output_path)
        ], check=True, stderr=subprocess.PIPE)
        
        print(f"Successfully created {output_path}")


if __name__ == "__main__":
    # Check for command line arguments
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
        
        # Check for optional output filename
        output_filename = "merged_normalized.mp3"
        if len(sys.argv) > 2:
            output_filename = sys.argv[2]
        
        # Parse any additional parameters
        buffer = 0.4  # Default no buffer since it worked for you
        if len(sys.argv) > 3:
            try:
                buffer = float(sys.argv[3])
            except ValueError:
                print(f"Warning: Invalid buffer duration '{sys.argv[3]}', using default 0s")
        
        normalize_trim_merge_audio(folder_path, output_filename, buffer_duration=buffer)
    else:
        # Try to find the most recent audio_output folder
        current_dir = Path(".")
        audio_folders = sorted(
            [
                d for d in current_dir.iterdir()
                if d.is_dir() and d.name.startswith("audio_output_")
            ], 
            key=lambda x: x.stat().st_mtime, 
            reverse=True
        )
        
        if audio_folders:
            folder_to_use = audio_folders[0]
            print(f"Using most recent folder: {folder_to_use}")
            normalize_trim_merge_audio(folder_to_use)
        else:
            print("Usage: python normalize_trim_merge.py [input_folder] [output_filename.mp3] [buffer_seconds]")
            print("No audio_output_* folders found. Please specify an input folder.")