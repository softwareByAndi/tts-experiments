
- https://github.com/OHF-Voice/piper1-gpl

## favorite voices
#### female
- en_GB-alba-medium
- en_US-ljspeech-high
- en_GB-semaine-medium
- en_GB-cori-high
- en_GB-southern_english_female-low

#### male
- en_US-lessac-high
- en_US-arctic-medium
- en_US-bryce-medium
- en_US-norman-medium
- en_US-ryan-high

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

# download voices
``` bash
# list voices
python3 -m piper.download_voices

# download specific voice
python3 -m piper.download_voices en_US-lessac-medium --data-dir voices
```

# generate tts
``` bash
cat inputs/hello_world.txt | piper \
--data-dir voices \
--model en_US-lessac-medium \
#--model en_US-amy-low \
--output_file outputs/welcome.wav
```

- there's also an option to run using a GPU

