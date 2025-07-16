#!/usr/bin/env python3
"""
Chatterbox TTS with real-time audio streaming using sounddevice.
This provides a simpler alternative to pyaudio for audio streaming.
"""

import torch
import numpy as np
from chatterbox.tts import ChatterboxTTS
import sounddevice as sd
import queue
import threading
import time

# Constants
VOICE_PATH = "voices/default.wav"
TEST_MODE = True  # Set to False to process all text
BUFFER_SIZE = 0.1  # Buffer size in seconds

def initialize_model():
    """Initialize the ChatterboxTTS model."""
    print("Initializing ChatterboxTTS model...")
    
    if torch.cuda.is_available():
        print("CUDA available! Loading model on GPU...")
        device = "cuda"
    else:
        print("Loading model on CPU...")
        device = "cpu"
    
    model = ChatterboxTTS.from_pretrained(device=device)
    
    print("Model loaded successfully!")
    return model

def stream_audio(audio_data, sample_rate):
    """Stream audio data directly using sounddevice."""
    print(f"Streaming audio at {sample_rate}Hz...")
    
    # Play audio blocking
    sd.play(audio_data, sample_rate)
    sd.wait()  # Wait until playback is finished

def generate_and_stream_immediate(model, text, voice_path=None):
    """Generate audio and stream immediately."""
    print(f"Generating: '{text[:50]}...'")
    
    # Generate audio
    wav = model.generate(text, audio_prompt_path=voice_path)
    
    # Convert to numpy array
    if isinstance(wav, torch.Tensor):
        audio_data = wav.cpu().numpy()
    else:
        audio_data = np.array(wav)
    
    # Ensure 1D array and float32
    if len(audio_data.shape) > 1:
        audio_data = audio_data.squeeze()
    
    if audio_data.dtype != np.float32:
        audio_data = audio_data.astype(np.float32)
    
    # Stream the audio
    stream_audio(audio_data, model.sr)

def continuous_streaming_demo(model):
    """Demonstrate continuous streaming with a queue-based approach."""
    print("\n=== Continuous Streaming Demo ===")
    
    texts = [
        "This demonstrates continuous audio streaming.",
        "Each sentence is generated and played seamlessly.",
        "The queue ensures smooth playback without gaps."
    ]
    
    if TEST_MODE:
        texts = texts[:2]
    
    audio_queue = queue.Queue()
    
    def audio_callback(outdata, frames, time_info, status):
        """Callback for continuous audio streaming."""
        if status:
            print(f"Stream status: {status}")
        
        try:
            data = audio_queue.get_nowait()
            if len(data) < frames:
                # Pad with zeros if needed
                outdata[:len(data)] = data.reshape(-1, 1)
                outdata[len(data):] = 0
            else:
                outdata[:] = data[:frames].reshape(-1, 1)
                # Put remaining data back
                if len(data) > frames:
                    audio_queue.put(data[frames:])
        except queue.Empty:
            outdata.fill(0)
    
    # Start output stream
    with sd.OutputStream(
        samplerate=model.sr,
        channels=1,
        callback=audio_callback,
        blocksize=int(model.sr * BUFFER_SIZE)
    ):
        for text in texts:
            print(f"Generating: '{text[:40]}...'")
            
            # Generate audio
            wav = model.generate(text, audio_prompt_path=VOICE_PATH)
            
            # Convert to numpy
            if isinstance(wav, torch.Tensor):
                audio_data = wav.cpu().numpy()
            else:
                audio_data = np.array(wav)
            
            if len(audio_data.shape) > 1:
                audio_data = audio_data.squeeze()
            
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            
            # Add to queue
            audio_queue.put(audio_data)
            
            # Wait a bit for processing
            time.sleep(0.1)
        
        # Wait for queue to empty
        while not audio_queue.empty():
            time.sleep(0.1)
        
        # Final wait for audio to finish
        time.sleep(0.5)

def main():
    # Initialize model
    model = initialize_model()
    
    # Check audio devices
    print("\nAvailable audio devices:")
    print(sd.query_devices())
    print(f"\nDefault output device: {sd.query_devices(kind='output')['name']}")
    
    # Simple streaming demo
    print("\n=== Simple Streaming Demo ===")
    texts = [
        "Welcome to the Chatterbox streaming demo!",
        "This version uses sounddevice for audio playback.",
        "It's simpler and more reliable than pyaudio."
    ]
    
    if TEST_MODE:
        texts = texts[:2]
    
    for i, text in enumerate(texts):
        print(f"\n[{i+1}/{len(texts)}]")
        generate_and_stream_immediate(model, text, VOICE_PATH)
        time.sleep(0.3)  # Small pause between sentences
    
    # Continuous streaming demo
    print("\n" + "="*50)
    user_input = input("Run continuous streaming demo? (y/n): ")
    if user_input.lower() == 'y':
        continuous_streaming_demo(model)
    
    print("\nDemo complete!")

if __name__ == "__main__":
    main()