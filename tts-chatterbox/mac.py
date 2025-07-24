import torch
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS
import warnings

# Detect device (Mac with M1/M2/M3/M4)
device = "mps" if torch.backends.mps.is_available() else "cpu"
map_location = torch.device(device)

# Monkey patch torchaudio resampling to use CPU for MPS workaround
if device == "mps":
    import torchaudio.functional as F
    _original_apply_sinc_resample_kernel = F._apply_sinc_resample_kernel
    
    def patched_apply_sinc_resample_kernel(waveform, orig_freq, new_freq, gcd, kernel, width):
        # Check if this would exceed MPS limits
        if waveform.device.type == 'mps' and kernel.shape[0] > 65536:
            # Move to CPU for this operation
            waveform_cpu = waveform.cpu()
            kernel_cpu = kernel.cpu()
            result = _original_apply_sinc_resample_kernel(waveform_cpu, orig_freq, new_freq, gcd, kernel_cpu, width)
            # Move back to MPS
            return result.to('mps')
        else:
            return _original_apply_sinc_resample_kernel(waveform, orig_freq, new_freq, gcd, kernel, width)
    
    F._apply_sinc_resample_kernel = patched_apply_sinc_resample_kernel

torch_load_original = torch.load
def patched_torch_load(*args, **kwargs):
    if 'map_location' not in kwargs:
        kwargs['map_location'] = map_location
    return torch_load_original(*args, **kwargs)

torch.load = patched_torch_load

model = ChatterboxTTS.from_pretrained(device=device)
text = "Today is the day. I want to move like a titan at dawn, sweat like a god forging lightning. No more excuses. From now on, my mornings will be temples of discipline. I am going to work out like the gods… every damn day."

# If you want to synthesize with a different voice, specify the audio prompt
AUDIO_PROMPT_PATH = "voices/achernar.wav"
wav = model.generate(
    text, 
    audio_prompt_path=AUDIO_PROMPT_PATH,
    exaggeration=0.5,
    cfg_weight=0.5
    )
ta.save("outputs/test-2.wav", wav, model.sr)