- https://github.com/OHF-Voice/piper1-gpl


# initialization
``` bash
cd tts-piper
mkdir outputs # if not already exists
mkdir voices  # if not already exists
deactivate    # deactivate any virtual environments if currently in one
pyenv install 3.10.12
pyenv local 3.10.12
python -m venv venv-piper
source venv-piper/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python3 -m piper.download_voices en_US-lessac-medium --data-dir voices
```

more voices
``` bash
python3 -m piper.download_voices \
--data-dir voices \
en_US-lessac-medium \
en_US-lessac-high \
en_US-arctic-medium \
en_US-bryce-medium \
en_US-norman-medium \
en_US-ryan-high \

en_GB-alba-medium \
en_US-ljspeech-high \
en_GB-semaine-medium \
en_GB-cori-high \
en_GB-southern_english_female-low
```

# example Python
- https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/API_PYTHON.md

``` python
import wave
from piper import PiperVoice

voice = PiperVoice.load("/path/to/en_US-lessac-medium.onnx")
syn_config = SynthesisConfig(
    volume=0.5,         # half as loud
    length_scale=2.0,   # twice as slow
    noise_scale=1.0,    # more audio variation
    noise_w_scale=1.0,  # more speaking variation
    normalize_audio=False, # use raw audio from voice
)
with wave.open("test.wav", "wb") as wav_file:
    voice.synthesize_wav(
        "Welcome to the world of speech synthesis!", 
        wav_file, 
        syn_config=syn_config # optional - adjusts synthesis
        use_cuda=True         # optional - uses GPU (requires onnxruntime-gpu)
    )
```

for streaming 
``` python
for chunk in voice.synthesize("..."):
    set_audio_format(chunk.sample_rate, chunk.sample_width, chunk.sample_channels)
    write_raw_data(chunk.audio_int16_bytes)
```