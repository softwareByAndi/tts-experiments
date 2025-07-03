#!/usr/bin/env python3
"""
Multiple Chatterbox model instances - one per voice (memory intensive!)
"""

import os
import sys
import torch
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS

INPUT_FILE = "inputs/test.md"
OUTPUT_DIR = "outputs/multi_model"
VOICE_PATHS = {
    'DEFAULT': "inputs/voice_clone_samples/default.wav",
    'achernar': "inputs/voice_clone_samples/achernar.wav"
}

class MultiVoiceChatterbox:
    """Manages multiple Chatterbox instances with different voices"""
    
    def __init__(self, device='cuda'):
        self.device = device
        self.models = {}
        self.sample_rate = None
        
    def load_voice(self, voice_name, voice_path=None):
        """Load a model instance for a specific voice"""
        if voice_name not in self.models:
            print(f"Loading model for voice: {voice_name}")
            model = ChatterboxTTS.from_pretrained(device=self.device)
            self.models[voice_name] = {
                'model': model,
                'voice_path': voice_path
            }
            if self.sample_rate is None:
                self.sample_rate = model.sr
            # Clear GPU cache after loading
            if self.device == 'cuda':
                torch.cuda.empty_cache()
    
    def generate(self, text, voice_name):
        """Generate speech with specific voice model"""
        if voice_name not in self.models:
            raise ValueError(f"Voice {voice_name} not loaded")
        
        model_info = self.models[voice_name]
        model = model_info['model']
        voice_path = model_info['voice_path']
        
        if voice_path:
            return model.generate(text, audio_prompt_path=voice_path)
        else:
            return model.generate(text)

def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else INPUT_FILE
    output_dir = sys.argv[2] if len(sys.argv) > 2 else OUTPUT_DIR
    
    # Check available memory
    if torch.cuda.is_available():
        gpu_mem = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"GPU Memory: {gpu_mem:.1f} GB")
        if gpu_mem < 8:
            print("WARNING: Multiple models may exceed GPU memory!")
    
    # Initialize multi-voice system
    device = "cuda" if torch.cuda.is_available() else "cpu"
    multi_voice = MultiVoiceChatterbox(device=device)
    
    # Pre-load voices
    print("\nPre-loading voice models...")
    for voice_name, voice_path in VOICE_PATHS.items():
        multi_voice.load_voice(voice_name, voice_path)
    
    # Process text
    print(f"\nProcessing text from: {input_file}")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    current_voice = 'DEFAULT'
    output_idx = 0
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('<') and line.endswith('>'):
                current_voice = line[1:-1]
                continue
            
            print(f"Generating with {current_voice}: {line[:50]}...")
            wav = multi_voice.generate(line, current_voice)
            
            filepath = f"{output_dir}/{output_idx:03d}_{current_voice}.wav"
            ta.save(filepath, wav, multi_voice.sample_rate)
            print(f"✓ Saved: {os.path.basename(filepath)}")
            
            output_idx += 1
            
            if output_idx >= 10:  # Limit for demo
                break
    
    print(f"\nDone! Audio files saved to {output_dir}")

if __name__ == "__main__":
    main()