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

async def create_voice(voice_name: str, voice_description: str) -> None:
    """Create a voice with the given name and description"""
    print(f"Creating voice '{voice_name}' with description: {voice_description}")
    
    # Generate initial speech with the description
    sample_text = "This is a sample text to create a new voice."
    speech = await hume.tts.synthesize_json(
        utterances=[
            PostedUtterance(
                voice={ "name": voice_name, "provider": "HUME_AI" },
                description=voice_description,
                text=sample_text,
            )
        ]
    )
    
    # Save the voice to the library with the specified name
    generation_id = speech.generations[0].generation_id
    
    try:
        await hume.tts.voices.create(
            name=voice_name,
            generation_id=generation_id
        )
        print(f"Successfully created voice '{voice_name}'")
    except Exception as e:
        # If there's an error (like the voice already exists), just log it and continue
        print(f"Note: Couldn't create voice '{voice_name}': {str(e)}")
        print(f"Continuing with existing voice or proceeding without it...")

async def generate_audio_from_script(script_file: str, maintain_character_continuity: bool = True) -> None:
    """Generate audio for each utterance in the provided script file"""
    # Load script from file
    with open(script_file, 'r') as f:
        script_data = json.load(f)
    
    script_lines = script_data.get("script", [])
    
    # Dictionary to keep track of the last generation_id for each character
    # This helps maintain voice continuity
    character_last_gen = {}
    
    # Set of characters we've already processed
    processed_characters = set()
    
    # Process each utterance in the script
    for i, line in enumerate(script_lines):
        character = line.get("character", "UNKNOWN")
        utterance = line.get("utterance", "")
        voice_direction = line.get("voiceDirection", "")
        
        # If this is the first time we're seeing this character, create their voice
        if character not in processed_characters:
            voice_name, description = get_voice_description(character)
            try:
                await create_voice(voice_name, description)
            except Exception as e:
                print(f"Warning: Could not create voice for {character}: {str(e)}")
            processed_characters.add(character)
        
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
        try:
            # First try with a named voice
            response = await hume.tts.synthesize_json(
                utterances=[
                    PostedUtterance(
                        voice=PostedUtteranceVoiceWithName(name=voice_name),
                        description=voice_direction,  # Acts as "acting instructions"
                        text=utterance,
                    )
                ],
                context=context,
                num_generations=1
            )
        except Exception as e:
            print(f"Warning: Could not use named voice. Falling back to description: {str(e)}")
            # Fall back to using just the description if the named voice doesn't work
            voice_name, description = get_voice_description(character)
            full_description = description
            if voice_direction:
                full_description = f"{description}. {voice_direction}"
                
            response = await hume.tts.synthesize_json(
                utterances=[
                    PostedUtterance(
                        description=full_description,
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

def get_voice_description(character: str) -> tuple:
    """Get the voice name and description for a character"""
    voice_descriptions = {
        "NARRATOR": ("Vince Douglas", "A warm, authoritative storyteller with clear articulation"),
        "DIRECTOR": ("Scottish Guy", "An assertive, Scottish director with commanding presence"),
        "SUZUKI": ("Vince Douglas", "A professional, slightly formal Japanese accent with perfect pronunciation"),
        "DEFAULT": ("Wise Wizard", "A wise, patient voice with a hint of mystery")
    }
    
    return voice_descriptions.get(character, voice_descriptions["DEFAULT"])

def get_voice_for_character(character: str) -> str:
    """Map character names to voice names in our library"""
    voice_name, _ = get_voice_description(character)
    return voice_name

async def main():
    """Main function to run the script"""
    # Check if script file was provided as argument
    import sys
    if len(sys.argv) > 1:
        script_file = sys.argv[1]
    else:
        script_file = "script.json"  # Default script file
        print(f"No script file provided, using default: {script_file}")
    
    print(f"Reading script from {script_file}")
    print(f"Output will be saved to {output_dir}")
    
    await generate_audio_from_script(script_file)
    print("Audio generation complete!")

if __name__ == "__main__":
    asyncio.run(main())