# Hume TTS - Text-to-Speech Audio Generation

A Python-based text-to-speech (TTS) system using the Hume API to generate character voices from scripted dialogue with voice direction controls.

## Features

- **Character-based TTS**: Generate unique voices for different characters (narrator, king, princess, etc.)
- **Voice Direction**: Fine-tune voice characteristics with detailed voice direction instructions
- **Voice Continuity**: Maintain consistent character voices across multiple utterances
- **Audio Processing**: Merge and normalize generated audio files with silence trimming
- **Batch Processing**: Process entire scripts or resume from specific utterances

## Project Structure

```
tts-hume/
   README.md
   pyproject.toml          # Project dependencies
   uv.lock                 # Lock file for dependencies
   process_audio.py        # Main TTS generation script
   merge_audio_files.py    # Audio merging and normalization utility
   resume.py               # Resume processing from specific utterance
   test.py                 # Testing scripts
   test_2.py
   scripts/                # Script files for TTS generation
      dm_ch_1.json       # Death March Chapter 1 script
      fixes.json         # Script fixes/corrections
   test_script.json        # Sample test script
   character_last_gen.json # Character voice generation tracking
   audio_output_*/         # Generated audio output directories
   prev_audio/             # Previous audio generations
   files/                  # Additional resources
```

## Setup

1. Install dependencies:
```bash
uv pip install -r pyproject.toml
```

2. Set up environment variables:
```bash
# Create a .env file and add your Hume API key
HUME_API_KEY=your_api_key_here
```

## Usage

### Generate Audio from Script

Process a script file to generate audio for each utterance:

```bash
python process_audio.py
```

The script will:
- Load dialogue from a JSON script file
- Generate audio for each character's utterance
- Apply voice directions for character-specific speech patterns
- Save individual WAV files for each utterance

### Script Format

Scripts should be JSON files with the following structure:

```json
{
  "script": [
    {
      "character": "NARRATOR",
      "utterance": "The stars twinkled overhead as she approached the castle.",
      "voiceDirection": "Calm, measured pace with a sense of wonder. Slightly hushed tone as if telling a bedtime story."
    },
    {
      "character": "KING",
      "utterance": "Who dares enter my kingdom uninvited?",
      "voiceDirection": "Deep, booming voice with clear authority. Sharp emphasis on 'dares' with a threatening undertone."
    }
  ]
}
```

### Merge Audio Files

Combine multiple audio files into a single normalized output:

```bash
python merge_audio_files.py audio_output_folder/
```

Options:
- `--output`: Output filename (default: merged_normalized.mp3)
- `--target-level`: Target loudness in LUFS (default: -16)
- `--silence-threshold`: Threshold for silence detection (default: -50dB)

### Resume Processing

Resume audio generation from a specific utterance:

```bash
python resume.py
```

## Audio Output

Generated audio files are saved in timestamped directories:
- Individual utterances: `audio_output_[timestamp]/[index]_[character].wav`
- Merged output: `audio_output_[timestamp]/merged_normalized.mp3`

## Requirements

- Python 3.13+
- Hume API key
- FFmpeg (for audio merging and normalization)

## Voice Characters

The system supports multiple character voices with customizable voice directions:
- **NARRATOR**: Storytelling voice with variable tone and pace
- **KING**: Authoritative, deep voice
- **PRINCESS**: Refined, feminine voice
- **SUZUKI**: Character-specific voice
- **DIRECTOR**: Commanding presence

## Notes

- Voice continuity is maintained by tracking generation IDs for each character
- Audio files are generated in WAV format for quality
- Merged files are normalized to -16 LUFS (optimal for speech)
- The system automatically creates output directories with timestamps