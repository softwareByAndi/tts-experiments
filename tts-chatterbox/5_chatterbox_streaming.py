#!/usr/bin/env python3
"""
Chatterbox TTS with real-time audio streaming instead of saving to files.
This example demonstrates streaming generated audio directly to speakers.
"""

import torch
import numpy as np
from chatterbox.tts import ChatterboxTTS
import pyaudio
import threading
import queue
import time

# Constants
VOICE_PATH = "voices/default.wav"
TEST_MODE = True  # Set to False to process all text
CHUNK_SIZE = 1024  # Audio chunk size for streaming

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

def audio_streamer(audio_queue, sample_rate):
    """Stream audio from queue to speakers."""
    p = pyaudio.PyAudio()
    
    # Open audio stream
    stream = p.open(
        format=pyaudio.paFloat32,
        channels=1,
        rate=sample_rate,
        output=True,
        frames_per_buffer=CHUNK_SIZE
    )
    
    print("Audio stream opened. Starting playback...")
    
    try:
        while True:
            # Get audio data from queue
            audio_data = audio_queue.get()
            
            # Check for stop signal
            if audio_data is None:
                break
            
            # Convert to float32 if needed
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            
            # Write to stream
            stream.write(audio_data.tobytes())
            
    finally:
        print("Closing audio stream...")
        stream.stop_stream()
        stream.close()
        p.terminate()

def generate_and_stream(model, text, audio_queue, voice_path=None):
    """Generate audio and add to streaming queue."""
    print(f"Generating audio for: '{text[:50]}...'")
    
    # Generate audio
    wav = model.generate(text, audio_prompt_path=voice_path)
    
    # Convert tensor to numpy array
    if isinstance(wav, torch.Tensor):
        audio_data = wav.cpu().numpy()
    else:
        audio_data = np.array(wav)
    
    # Ensure 1D array
    if len(audio_data.shape) > 1:
        audio_data = audio_data.squeeze()
    
    # Add to queue in chunks
    chunk_samples = CHUNK_SIZE
    for i in range(0, len(audio_data), chunk_samples):
        chunk = audio_data[i:i + chunk_samples]
        audio_queue.put(chunk)
    
    print(f"Audio generated and queued for streaming")

def main():
    # Initialize model
    model = initialize_model()
    
    # Sample texts to generate
    texts = [
        "Hello! This is a test of the Chatterbox text-to-speech system with real-time audio streaming.",
        "Instead of saving audio files, we're playing the generated speech directly through your speakers.",
        "This approach is useful for interactive applications where you want immediate audio feedback.",
        "You can hear each sentence as soon as it's generated, creating a more responsive experience."
    ]
    
    if TEST_MODE:
        texts = texts[:2]  # Only process first 2 sentences in test mode
        print("TEST MODE: Processing only first 2 sentences")
    
    # Create audio queue
    audio_queue = queue.Queue()
    
    # Start audio streaming thread
    stream_thread = threading.Thread(
        target=audio_streamer,
        args=(audio_queue, model.sr),
        daemon=True
    )
    stream_thread.start()
    
    try:
        # Generate and stream each text
        for i, text in enumerate(texts):
            print(f"\n[{i+1}/{len(texts)}] Processing text...")
            generate_and_stream(model, text, audio_queue, VOICE_PATH)
            
            # Small delay between sentences
            time.sleep(0.5)
        
        # Wait for queue to empty
        print("\nWaiting for audio to finish playing...")
        while not audio_queue.empty():
            time.sleep(0.1)
        
        # Add a small final delay
        time.sleep(1.0)
        
    finally:
        # Signal streamer to stop
        audio_queue.put(None)
        stream_thread.join()
    
    print("\nStreaming complete!")

if __name__ == "__main__":
    main()