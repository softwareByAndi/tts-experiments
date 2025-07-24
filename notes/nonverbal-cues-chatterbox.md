# Chatterbox TTS Non-Verbal Cues Guide

## Overview
This guide documents best practices for presenting non-verbal cues in Chatterbox TTS based on research into available features and community practices.

## Native Support

### 1. Pause Tags
- **Feature**: `[pause:xx]` tags for inserting silence
- **Status**: Recently added via PR #164
- **Implementation**: Uses `parse_pause_tags` function in the generate method
- **Note**: Duration units (seconds/milliseconds) not clearly documented

### 2. Emotion Control Parameters
Chatterbox is the first open source TTS with emotion exaggeration control:
- **Parameter**: `emotion_exaggeration`
- **Range**: 0-2 (0=flat/monotone, 0.5=neutral default, 1=normal, 2=exaggerated)
- **Related Parameter**: `cfg_weight` (affects pacing)
- **Default Settings**: `exaggeration=0.5, cfg_weight=0.5`

## Limitations

### Non-Supported Bracketed Tags
The following tags are **NOT** natively supported and will be spoken as text:
- `[sighs]`
- `[laughs]` 
- `[breathing]`
- `[clears throat]`
- `[gasps]`
- `[music]`
- Any other bracketed non-verbal cues

## Best Practices

### 1. Using Pause Tags
```python
# Insert pauses for dramatic effect
text = "Let me think... [pause:2] Yes, that makes sense."
text = "Wait, what? [pause:1] You're telling me... [pause:0.5] this changes everything!"
```

### 2. Emotion Control for Expression
```python
# For dramatic/expressive speech
wav = model.generate(
    text, 
    audio_prompt_path=voice_path,
    exaggeration=0.8,  # Increase for more emotion
    cfg_weight=0.3     # Lower to compensate for faster pacing
)

# For neutral/calm speech
wav = model.generate(
    text,
    audio_prompt_path=voice_path,
    exaggeration=0.3,  # Lower for flatter delivery
    cfg_weight=0.5     # Standard pacing
)
```

### 3. Workarounds for Non-Verbal Sounds

#### A. Descriptive Direction
```python
# Instead of bracketed tags, use natural expressions
# Bad: "I can't believe it [laughs]"
# Good: "I can't believe it-- haha!"
# Good: "I can't believe it... heh."

# For sighs
# Bad: "[sighs] Well, that's disappointing"
# Good: "*sigh* Well, that's disappointing"
# Good: "Hahhh... well, that's disappointing"
```

#### B. Strategic Punctuation
```python
# Interruptions
text = "But I thought--"
text = "Wait, so you're saying that--"

# Trailing off
text = "I don't know..."
text = "Maybe we could..."

# Hesitation
text = "Well... I mean... it's complicated"
```

#### C. Thinking Sounds
```python
# Natural filler words work well
text = "Um... let me think about that"
text = "Uh, I'm not sure that's right"
text = "Hmm... interesting point"
text = "Er... could you repeat that?"
```

### 4. Multi-Voice Conversations

For podcast-style dialogues:
```python
# Use speaker tags
text_lines = [
    "<achernar>",
    "[overlapping] Sorry, sorry. I just-- [pause:0.5] Okay.",
    "<DEFAULT>", 
    "Wait, what? Alex, you lost me.",
    "<achernar>",
    "[exhales] Let me back up..."
]

# Process each speaker with different voices
for line in text_lines:
    if line.startswith('<'):
        current_speaker = line[1:-1]
        continue
    wav = model.generate(line, audio_prompt_path=VOICE_PATHS[current_speaker])
```

### 5. Natural Conversation Techniques

Based on the nanite podcast refactoring:
```python
# False starts
text = "The algorithm tries... um, thousands of possible simplifications"

# Self-corrections  
text = "It's treating geometric data like tex-- actually, you know what? Think of it like Netflix"

# Overlapping speech markers
text = "[overlapping] --flexibility! Right, because there are multiple paths!"

# Environmental cues
text = "[rustling papers] I've got this screenshot from ZBrush..."
```

## Recommended Workflow

1. **Plan Non-Verbal Elements**: Identify where pauses, emotion changes, and other cues are needed
2. **Use Native Features**: Apply `[pause:xx]` tags and emotion parameters
3. **Natural Language**: Replace unsupported tags with descriptive text or punctuation
4. **Test and Iterate**: Generate samples with different emotion settings
5. **Post-Process if Needed**: Add sound effects or splice audio clips for complex effects

## Parameter Guidelines

### For Different Moods:
- **Excited/Energetic**: `exaggeration=0.8-1.0, cfg_weight=0.3`
- **Neutral/Informative**: `exaggeration=0.5, cfg_weight=0.5` (default)
- **Calm/Soothing**: `exaggeration=0.3-0.4, cfg_weight=0.6`
- **Dramatic/Theatrical**: `exaggeration=1.0-1.5, cfg_weight=0.2-0.3`

### Tips:
- Higher exaggeration speeds up speech - compensate with lower cfg_weight
- Test with your specific voice samples as they affect the output
- Combine pause tags with emotion changes for maximum effect

## Community Extensions

- **Chatterbox-TTS-Extended**: Adds configurable sound word removal/replacement
- Custom mapping example: `"zzz=>sigh"` for automatic replacements

## Future Considerations

As Chatterbox TTS evolves, watch for:
- Extended bracketed tag support
- More granular emotion controls
- Native non-verbal sound generation
- Real-time emotion modulation

## Example Implementation

```python
# Complete example with multiple techniques
def generate_expressive_dialogue(model, text, speaker, scene_emotion="neutral"):
    # Set emotion parameters based on scene
    emotion_settings = {
        "neutral": {"exaggeration": 0.5, "cfg_weight": 0.5},
        "tense": {"exaggeration": 0.7, "cfg_weight": 0.4},
        "excited": {"exaggeration": 0.9, "cfg_weight": 0.3},
        "thoughtful": {"exaggeration": 0.4, "cfg_weight": 0.6}
    }
    
    settings = emotion_settings.get(scene_emotion, emotion_settings["neutral"])
    
    # Process text with natural cues
    text = text.replace("[sighs]", "*sigh*")
    text = text.replace("[laughs]", "haha")
    text = text.replace("[thinking]", "hmm...")
    
    # Generate with appropriate voice and emotion
    wav = model.generate(
        text,
        audio_prompt_path=f"voices/{speaker}.wav",
        **settings
    )
    
    return wav
```

## Resources

- [Chatterbox GitHub Repository](https://github.com/resemble-ai/chatterbox)
- [PR #164 - Pause Tag Implementation](https://github.com/resemble-ai/chatterbox/pull/164)
- [Chatterbox-TTS-Extended](https://github.com/petermg/Chatterbox-TTS-Extended)
- [Natural Dialogue Refactoring Guide](../nanite-podcast-refactoring-plan.md)