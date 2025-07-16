import json
import os
import asyncio
import base64
import time
import re
from pathlib import Path
import aiofiles
from dotenv import load_dotenv
from hume import AsyncHumeClient
from hume.tts import PostedUtterance, PostedUtteranceVoiceWithName, PostedContextWithGenerationId
from typing import List, Dict, Any, Optional

# Load environment variables
load_dotenv()
api_key = os.getenv("HUME_API_KEY")
if not api_key:
    raise EnvironmentError("HUME_API_KEY not found in environment variables")

# Initialize Hume client
hume = AsyncHumeClient(api_key=api_key, timeout=300)

generation_context_file = 'generation_context.json'


def filter_completed_script_entries(script_file: str, audio_dir: str) -> List[Dict[str, Any]]:
    """
    Filter out script entries that already have corresponding audio files.
    
    Args:
        script_file: Path to the JSON script file
        audio_dir: Directory containing previously generated audio files
        
    Returns:
        List of script entries that need to be processed (those without audio files)
    """
    # Load script from file
    with open(script_file, 'r') as f:
        script_data = json.load(f)
    
    script_lines = script_data.get("script", [])
    
    # Get list of existing audio files
    audio_path = Path(audio_dir)
    if not audio_path.exists() or not audio_path.is_dir():
        print(f"Warning: Audio directory {audio_dir} not found. Processing all script entries.")
        return script_lines
    
    # Get all WAV files in the directory
    existing_files = [f.name for f in audio_path.glob("*.wav")]
    
    # Extract indices from filenames using regex pattern
    # Format is assumed to be: 000_character_name.wav
    completed_indices = set()
    pattern = r"^(\d{3})_.*\.wav$"
    
    for filename in existing_files:
        match = re.match(pattern, filename)
        if match:
            index = int(match.group(1))
            completed_indices.add(index)
    
    # Filter out script entries that already have audio files
    filtered_script = []
    for i, line in enumerate(script_lines):
        if i not in completed_indices:
            # Add original index so we maintain consistent filenames
            line["originalIndex"] = i
            filtered_script.append(line)
        else:
            print(f"Skipping entry {i}: '{line.get('utterance', '')[:30]}...' (already processed)")
    
    print(f"Found {len(script_lines)} total entries, {len(filtered_script)} remaining to process")
    
    return filtered_script


async def generate_audio_from_script(
    script_file: str, 
    output_dir: Path,
    previous_audio_dir: Optional[str] = None, 
    maintain_character_continuity: bool = True,
    _character_last_gen: Dict[str, any] = {}
) -> None:
    """Generate audio for each utterance in the provided script file"""
    # Load script from file
    with open(script_file, 'r') as f:
        script_data = json.load(f)
    
    script_lines = script_data.get("script", [])
    
    # Filter out already processed entries if previous_audio_dir is provided
    if previous_audio_dir:
        script_lines = filter_completed_script_entries(script_file, previous_audio_dir)
        if not script_lines:
            print("All script entries have already been processed. Nothing to do.")
            return
    
    # Dictionary to keep track of the last generation_id for each character
    character_last_gen = _character_last_gen.copy()
    
    # Process each utterance in the script
    for line in script_lines:
        character = line.get("character", "UNKNOWN")
        utterance = line.get("utterance", "")
        voice_direction = line.get("voiceDirection", "")
        
        # Get original index from script for filename consistency
        original_index = line.get("originalIndex", script_lines.index(line))
        
        # Get voice for character
        voice_name = get_voice_for_character(character)
        
        print(f"Generating audio for {character}: '{utterance[:30]}...'")
        
        # Prepare context if we have previous generations for this character
        context = None
        if maintain_character_continuity and character in character_last_gen:
            context = PostedContextWithGenerationId(
                generation_id=character_last_gen[character]
            )
        
        # Call Hume TTS API
        await asyncio.sleep(2) # rate-limit calls to the api
        response = await hume.tts.synthesize_json(
            utterances=[
                PostedUtterance(
                    voice={ "name": voice_name, "provider": "HUME_AI" },
                    description=voice_direction,
                    text=utterance,
                )
            ],
            context=context,
            num_generations=1
        )
        
        # Store the generation_id for future utterances from this character
        character_last_gen[character] = response.generations[0].generation_id
        with open('character_last_gen.json', 'w') as f:
            json.dump(character_last_gen, f, indent=2)
        
        # Save audio file
        filename = f"{original_index:03d}_{character.lower().replace(' ', '_')}"
        await write_audio_to_file(response.generations[0].audio, output_dir, filename)


async def write_audio_to_file(base64_encoded_audio: str, output_dir: Path, filename: str) -> None:
    """Write base64 encoded audio to a WAV file"""
    file_path = output_dir / f"{filename}.wav"
    audio_data = base64.b64decode(base64_encoded_audio)
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(audio_data)
    print(f"Wrote {file_path}")


def get_voice_for_character(character: str) -> str:

    # return "Vince Douglas"
    # return "Texan Narrator"

    """Map character names to voice names available in Hume's library"""
    # This is a simple mapping - customize this with your preferred voices
    voice_mapping = {
        "NARRATOR": "Vince Douglas",
        "DIRECTOR": "Scottish Guy",
        "SUZUKI": "Vince Douglas",
        "DEFAULT": "Wise Wizard"
    }
    
    # Return the mapped voice or a default one
    return voice_mapping.get(character, voice_mapping["DEFAULT"])
async def main():
    """Main function to run the script"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate audio from script JSON file")
    parser.add_argument("script_file", help="Path to the JSON script file")
    parser.add_argument("--previous-dir", "-p", help="Path to directory with previously generated audio files")
    
    args = parser.parse_args()
    
    # Create output directory
    timestamp = int(time.time())
    output_dir = Path(f"./audio_output_{timestamp}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Reading script from {args.script_file}")
    print(f"Output will be saved to {output_dir}")
    
    if args.previous_dir:
        print(f"Checking for previously generated files in {args.previous_dir}")
        
    try:
        with open('character_last_gen.json', 'r') as f:
            character_last_gen = json.loads(f.read())
    except:
        character_last_gen = {}
        
    print(character_last_gen)
    
    await generate_audio_from_script(
        args.script_file, 
        output_dir,
        args.previous_dir, 
        character_last_gen
    )
    
    print("Audio generation complete!")


if __name__ == "__main__":
    asyncio.run(main())