# TTS Research - Offline Linux Options (2025)

## Top Recommendations

### 1. Piper TTS - Best Overall Choice
- **Quality**: Neural TTS system with VITS-trained models, "Google TTS quality"
- **Installation**: `pipx install piper-tts`
- **Features**: Fast, local, privacy-respecting, multiple quality levels
- **Hardware**: Optimized for low power devices like Raspberry Pi 4
- **Usage**: `echo 'text' | ./piper --model en_US-lessac-medium.onnx --output_file output.wav`

### 2. Chatterbox - Latest Cutting-Edge
- **Quality**: Built on 0.5B Llama model
- **Status**: #1 trending TTS model on Hugging Face
- **Features**: Small, fast, easy to use
- **Target**: Best for getting started with open-source TTS

### 3. Orpheus - Advanced Features
- **Quality**: Llama-based with multiple parameter versions (150M to 3B)
- **Training**: 100k+ hours of English speech data
- **Features**: Zero-shot voice cloning, guided emotion, realtime streaming
- **Variants**: 3B, 1B, 400M, 150M parameter versions

## Traditional Options (Lower Quality)

### eSpeak NG
- Basic TTS engine, supports 50+ languages
- Lightweight and simple
- Quality: Basic but functional

### Festival
- Comprehensive TTS system from University of Edinburgh
- Modular architecture, extensive customization
- Languages: British English, American English, Spanish, Czech, Italian

### SVOX Pico
- Small but natural-sounding female voice
- Installation: `sudo apt-get install libttspico0 libttspico-utils libttspico-data`
- Good unit recognition and pronunciation

## Commercial High-End Options

### Cepstral
- Professional-grade with exceptional voice quality
- 6 distinct U.S. English voices plus multiple languages
- Proprietary speech synthesis technology

### Coqui TTS
- Production-ready with voice cloning capabilities
- High-quality, directable, emotive voices
- Commercial solution with advanced features

## Key Findings for 2025

- TTS landscape is rapidly evolving with new open-source models monthly
- Quality gap between open-source and commercial solutions is narrowing
- Privacy-focused local solutions are becoming viable alternatives to cloud services
- Hardware requirements are decreasing while quality improves

## Recommendation Summary

For offline Linux TTS in 2025:
1. **Piper TTS** - Best balance of quality, ease of use, and privacy
2. **Chatterbox** - Latest technology for experimental use
3. **Orpheus** - Advanced features and customization options