# Chatterbox Audio Streaming Examples

This directory contains examples of streaming Chatterbox TTS audio directly to speakers instead of saving to files.

## Requirements

Install additional dependencies for audio streaming:

```bash
pip install pyaudio sounddevice
```

Note: On macOS, you might need to install PortAudio first:
```bash
brew install portaudio
```

## Streaming Examples

### 6_chatterbox_streaming_sounddevice.py
- Uses sounddevice library (simpler alternative to PyAudio)
- Includes two modes:
  - Simple blocking playback
  - Continuous non-blocking streaming with callback
- Shows available audio devices

## Usage

Run either script:

```bash
python 5_chatterbox_streaming.py
# or
python 6_chatterbox_streaming_sounddevice.py
```

## Key Differences from File-Based Approach

1. **Real-time playback**: Audio plays immediately as it's generated
2. **No file storage**: Audio is streamed directly to speakers
3. **Lower latency**: Suitable for interactive applications
4. **Memory efficient**: No need to store entire audio files

## Customization

- Change `VOICE_PATH` to use different voice samples
- Adjust `CHUNK_SIZE` or `BUFFER_SIZE` for streaming performance
- Set `TEST_MODE = False` to process all example texts
- Modify the `texts` list to stream your own content

## Troubleshooting

If you encounter audio issues:
1. Check your audio output device is properly configured
2. Try the sounddevice version if PyAudio has issues
3. Ensure your system volume is not muted
4. Check that no other application is using the audio device