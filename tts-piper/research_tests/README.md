# Piper TTS Comprehensive Test Suite

This test suite explores the capabilities and limitations of Piper TTS for non-verbal cues and prosody control.

## Overview

The test suite includes 70+ tests across 11 categories:

1. **baseline_tests** - Basic functionality tests
2. **punctuation_tests** - Testing punctuation handling and natural pauses
3. **sentence_silence_tests** - Testing sentence_silence parameter variations
4. **speech_rate_tests** - Testing length_scale parameter for speech rate
5. **natural_speech_patterns** - Testing natural conversational patterns
6. **emotional_expression_attempts** - Testing emotional expressions (expected to fail)
7. **emphasis_workarounds** - Testing emphasis through various techniques
8. **conversational_dialogue** - Testing dialogue and conversation patterns
9. **technical_content** - Testing technical and complex content
10. **pause_workaround_markers** - Testing text markers for post-processing pauses
11. **combined_techniques** - Combining multiple techniques

## Requirements

- Python 3.6+
- Piper TTS installed and in PATH
- A Piper voice model (default: en_US-amy-medium)

## Quick Start

```bash
# Run all tests
python3 piper_tts_test_suite.py

# Or use the convenient runner script
./run_tests.sh

# Run quick baseline tests only
./run_tests.sh -q

# Run specific category
./run_tests.sh -c natural_speech_patterns

# List all categories
./run_tests.sh -l

# Use different voice model
./run_tests.sh -m en_GB-alan-low
```

## Test Structure

Each test includes:
- **ID**: Unique identifier
- **Name**: Descriptive name
- **Text**: The input text to synthesize
- **Parameters**: Piper parameters to apply (sentence_silence, length_scale)

## Expected Results

### What Should Work
- Basic punctuation pauses (commas, periods)
- Question intonation
- Sentence silence control
- Overall speech rate control
- Natural filler words (um, uh, hmm)

### What Won't Work
- Bracketed cues like [sighs], [laughs]
- Dynamic speech rate changes
- Word-level emphasis
- Emotional expressions
- Custom pause lengths within text

### Workarounds Tested
- Multiple periods for longer pauses
- Em-dashes for interruptions
- Ellipses for trailing off
- ALL CAPS for emphasis
- Text markers (~ or |) for post-processing
- Strategic punctuation placement

## Output Structure

```
test_outputs/
└── piper_tests_YYYYMMDD_HHMMSS/
    ├── test_results.md          # Complete test log
    ├── baseline_tests/          # Category folders
    │   ├── baseline_1_Simple_sentence.wav
    │   └── ...
    ├── punctuation_tests/
    │   └── ...
    └── ...
```

## Post-Processing Options

For features not supported by Piper, consider:

1. **Audio Concatenation**
   ```bash
   # Split at markers and insert silence
   sox file1.wav silence.wav file2.wav output.wav
   ```

2. **Speed Variation**
   ```bash
   # Generate emphasized words separately
   echo "important" | piper --length_scale 1.5 > emphasis.wav
   ```

3. **Silence Generation**
   ```bash
   # Create custom silence files
   sox -n -r 22050 -c 1 silence_1s.wav trim 0.0 1.0
   ```

## Reviewing Results

1. Listen to each category's audio files
2. Note which techniques produce natural results
3. Identify patterns that work well for your use case
4. Consider combining techniques for best results

## Next Steps

Based on test results:
- Implement post-processing scripts for unsupported features
- Create templates for common speech patterns
- Build automated pipeline for complex productions
- Consider alternative TTS engines for advanced features