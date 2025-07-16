import json
import os
import asyncio
import base64
import time
from pathlib import Path
import aiofiles
from dotenv import load_dotenv
from hume import AsyncHumeClient
from hume.tts import PostedUtterance, PostedUtteranceVoiceWithName, PostedContextWithGenerationId

# Load environment variables
load_dotenv()
api_key = os.getenv("HUME_API_KEY")
if not api_key:
    raise EnvironmentError("HUME_API_KEY not found in environment variables")

# Initialize Hume client
hume = AsyncHumeClient(api_key=api_key)

# Create output directory
timestamp = int(time.time())
output_dir = Path(f"./audio_output_{timestamp}")
output_dir.mkdir(parents=True, exist_ok=True)

async def write_audio_to_file(base64_encoded_audio: str, filename: str) -> None:
    """Write base64 encoded audio to a WAV file"""
    file_path = output_dir / f"{filename}.wav"
    audio_data = base64.b64decode(base64_encoded_audio)
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(audio_data)
    print(f"Wrote {file_path}")

async def generate_audio_from_script(script_file: str, maintain_character_continuity: bool = True) -> None:
    """Generate audio for each utterance in the provided script file"""
    # Load script from file
    with open(script_file, 'r') as f:
        script_data = json.load(f)
    
    script_lines = script_data.get("script", [])
    
    # Dictionary to keep track of the last generation_id for each character
    # This helps maintain voice continuity
    character_last_gen = {}
    
    # Process each utterance in the script
    for i, line in enumerate(script_lines):
        character = line.get("character", "UNKNOWN")
        utterance = line.get("utterance", "")
        voice_direction = line.get("voiceDirection", "")
        
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
        
        # Save audio file
        filename = f"{i:03d}_{character.lower().replace(' ', '_')}"
        await write_audio_to_file(response.generations[0].audio, filename)

def get_voice_for_character(character: str) -> str:

    # return "Vince Douglas"
    # return "Texan Narrator"

    """Map character names to voice names available in Hume's library"""
    # This is a simple mapping - customize this with your preferred voices
    voice_mapping = {
        "NARRATOR": "Old School Radio Announcer",
        "KING": "Wise Wizard",
        "PRINCESS": "Blunt Female Voice",
        "DEFAULT": "Charming Cowboy"
    }
    
    # Return the mapped voice or a default one
    return voice_mapping.get(character, voice_mapping["DEFAULT"])

async def main():
    """Main function to run the script"""
    # Check if script file was provided as argument
    import sys
    if len(sys.argv) > 1:
        script_file = sys.argv[1]
    else:
        script_file = "test_script.json"
    
    # Check if script file exists
    if not Path(script_file).exists():
        # If not, create a sample script for testing
        sample_script = {
            "script": [
                {
                    "character": "NARRATOR",
                    "utterance": "The stars twinkled overhead as she approached the castle.",
                    "voiceDirection": "Calm, measured pace with a sense of wonder. Slightly hushed tone as if telling a bedtime story. Emphasis on 'twinkled' with a hint of mysticism."
                },
                {
                    "character": "KING",
                    "utterance": "Who dares enter my kingdom uninvited?",
                    "voiceDirection": "Deep, booming voice with clear authority. Slightly elevated volume that resonates. Sharp emphasis on 'dares' with a threatening undertone. End with a downward inflection suggesting danger."
                },
                {
                    "character": "NARRATOR",
                    "utterance": "Princess Elara stepped forward, her golden cloak billowing in the night breeze.",
                    "voiceDirection": "Moderate pace with subtle tension. Quiet confidence in tone, with slight emphasis on 'golden' to highlight its importance."
                },
                {
                    "character": "PRINCESS",
                    "utterance": "I am Elara, daughter of the Eastern Realms. I seek audience with the Court of Stars.",
                    "voiceDirection": "Clear, refined feminine voice with quiet determination. Formal tone that conveys nobility. Slight musical quality to the words, especially on 'Eastern Realms'."
                }
            ]
        }
        
        with open(script_file, 'w') as f:
            json.dump(sample_script, f, indent=2)
        
        print(f"Created sample script file: {script_file}")
    
    print(f"Reading script from {script_file}")
    print(f"Output will be saved to {output_dir}")
    
    await generate_audio_from_script(script_file)
    print("Audio generation complete!")

if __name__ == "__main__":
    asyncio.run(main())