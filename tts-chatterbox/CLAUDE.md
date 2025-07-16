# Chatterbox TTS Project Context

This directory contains experiments with Chatterbox TTS, a cutting-edge text-to-speech system using a 0.5B Llama-based model.

## Project Structure

- `1_test_chatterbox.py` - Basic TTS generation test
- `2_chatterbox_from_file.py` - File-based text processing with smart line splitting
- `3_chatterbox_select_voice.py` - Voice cloning demonstration
- `4_chatterbox_podcast.py` - Multi-voice podcast generation
- `5_chatterbox_streaming.py` - Real-time audio streaming with PyAudio
- `6_chatterbox_streaming_sounddevice.py` - Audio streaming with sounddevice
- `compile_podcast.py` - Audio file compilation utility
- `voices/` - Voice sample files for cloning

## Key Dependencies

- chatterbox-tts - Main TTS engine
- torch, torchaudio - PyTorch for model inference
- peft - Parameter-efficient fine-tuning support
- pyaudio, sounddevice - Audio streaming libraries
- numpy - Array operations

## Common Tasks

When working on audio streaming:
- Use sounddevice over pyaudio when possible (more reliable)
- Test with TEST_MODE=True first to limit processing
- Check audio device availability with `sd.query_devices()`

When processing text files:
- Lines longer than 600 characters are automatically split
- Use speaker tags like `<DEFAULT>` or `<achernar>` for voice switching
- ThreadPoolExecutor handles concurrent file saving

## Testing Commands

```bash
# Test basic TTS
python 1_test_chatterbox.py

# Test streaming (requires audio dependencies)
python 6_chatterbox_streaming_sounddevice.py

# Generate podcast with multiple voices
python 4_chatterbox_podcast.py
```

## Important Notes

- CUDA support is automatically detected and used if available
- The model loads on first run and may take a moment
- Voice cloning requires WAV files (16kHz or higher recommended)
- Streaming examples play audio directly without saving files