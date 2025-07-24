# Piper-TTS Non-Verbal Cues Guide

## Overview

Piper is a fast, local neural text-to-speech system that prioritizes speed and low resource requirements. However, it has very limited support for non-verbal cues and prosody control.

## Input Format
- **Accepts**: Plain text only
- **Does NOT accept**: SSML or any markup languages
- Uses espeak-ng internally for text-to-phoneme conversion

## What Works

### Basic Features
- **Sentence pauses**: Controlled via `--sentence_silence` flag (default 0.2 seconds)
- **Overall speech rate**: Via `--length_scale` parameter (1 = normal, 0.5 = double speed, 2 = half speed)
- **Natural punctuation**: Basic recognition of periods, commas, and question marks

## What Doesn't Work
- ❌ Custom pause lengths within text
- ❌ Sighs, laughs, or breathing sounds
- ❌ Hesitations (um, uh, hmm)
- ❌ Emotional expressions
- ❌ Word-level emphasis/stress
- ❌ Dynamic speech rate variations
- ❌ SSML tags like `<break>`, `<emphasis>`, `<prosody>`
- ❌ Direct phonetic input (IPA)

## Workarounds and Best Practices

### 1. Audio Post-Processing Approach
```bash
# Generate segments separately
piper --model en_US-amy-medium --output speech1.wav < part1.txt
piper --model en_US-amy-medium --output speech2.wav < part2.txt

# Create silence file
sox -n -r 22050 -c 1 silence.wav trim 0.0 1.0  # 1 second silence

# Concatenate with sox
sox speech1.wav silence.wav speech2.wav output.wav
```

### 2. Text Marker System
Community solution using markers (like ~) in text:
1. Mark pause locations with ~
2. Split text into segments
3. Generate audio for each segment
4. Insert silence.wav files at marker positions
5. Merge all audio files

### 3. Sentence Boundary Control
```bash
# Increase pause between sentences
piper --sentence_silence 1.5 --model en_US-amy-medium < input.txt > output.wav
```

### 4. Speed Variation for Emphasis
```bash
# Generate emphasized word separately at slower speed
echo "important" | piper --length_scale 1.5 --model en_US-amy-medium > emphasis.wav
```

## Workaround Summary Table

| Need | Workaround |
|------|------------|
| Custom pauses | Split text and insert silence files |
| Emphasis | Generate word separately with different speed |
| Long pauses | Multiple sentence endings or audio editing |
| Hesitations | Pre-process text to spell out "um", "uh" |
| Emotional tone | Choose different voice models |
| Breathing | Not possible - requires audio editing |

## Alternatives
If you need advanced prosody control, consider:
- **Mimic3**: Piper's predecessor with SSML support
- **Commercial TTS**: AWS Polly, Google Cloud TTS (with SSML)
- **Audio editing**: Post-process with Audacity or sox

## Development Status
Development has moved to https://github.com/OHF-Voice/piper1-gpl. Future versions may add more features, but Piper remains focused on being fast and lightweight rather than full-featured.