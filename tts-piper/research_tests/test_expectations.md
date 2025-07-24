# Piper TTS Test Expectations & Recommendations

## Expected Test Results

### ✅ Will Work Well

1. **Basic Punctuation**
   - Periods create natural sentence breaks
   - Commas add brief pauses
   - Question marks trigger rising intonation
   - Exclamation marks add slight emphasis

2. **Sentence Silence Control**
   - Adjustable pauses between sentences (0.1 - 2.0 seconds)
   - Useful for pacing and dramatic effect

3. **Overall Speech Rate**
   - length_scale effectively controls speech speed
   - 0.5 = double speed, 2.0 = half speed

4. **Natural Speech Patterns**
   - "Um", "uh", "hmm" sound relatively natural
   - Ellipses (...) create natural trailing off
   - Em-dashes (--) work for interruptions

### ❌ Won't Work

1. **Bracketed Cues**
   - [sighs], [laughs], [breathing] will be spoken as text
   - No SSML support

2. **Dynamic Control**
   - No word-level emphasis
   - No mid-sentence speed changes
   - No emotion variations

3. **Sound Effects**
   - No breathing sounds
   - No laughter generation
   - No sighs or gasps

### 🔧 Workarounds with Mixed Results

1. **Emphasis Attempts**
   - ALL CAPS - may sound slightly different but not true emphasis
   - Repetition - works but sounds unnatural
   - Punctuation (!!) - minimal effect

2. **Emotion Simulation**
   - "Haha" for laughter - sounds robotic
   - "*sigh*" - will be spoken literally
   - "Hahhh..." for sighs - somewhat effective

3. **Pause Markers**
   - Tilde (~) or pipe (|) - requires post-processing
   - Multiple periods - creates longer pauses but sounds odd

## Recommended Approach

### For Basic Needs
```python
# Use natural punctuation and speech patterns
text = "Well, um... let me think about that. It's complicated, you know?"

# Adjust overall pacing
slow_dramatic = {"length_scale": 1.5, "sentence_silence": 1.0}
fast_urgent = {"length_scale": 0.7, "sentence_silence": 0.2}
```

### For Advanced Needs
```bash
# 1. Split text at strategic points
# 2. Generate segments with different parameters
# 3. Insert silence files where needed
# 4. Concatenate with sox or ffmpeg

# Example workflow:
echo "This is" | piper --model en_US-amy-medium > part1.wav
sox -n -r 22050 -c 1 pause.wav trim 0.0 0.5  # 0.5s pause
echo "dramatic!" | piper --length_scale 1.5 > part2.wav
sox part1.wav pause.wav part2.wav output.wav
```

## Key Insights

1. **Piper excels at**: Fast, efficient, natural-sounding basic speech
2. **Piper struggles with**: Emotional expression, dynamic prosody
3. **Best use cases**: Narration, technical content, basic dialogue
4. **Not ideal for**: Dramatic readings, emotional content, complex conversations

## Production Tips

1. **Write for Piper's strengths**
   - Use punctuation strategically
   - Include natural filler words
   - Break complex emotions into multiple sentences

2. **Post-process when needed**
   - Use sox for audio manipulation
   - Create reusable silence files
   - Build scripts for common patterns

3. **Consider alternatives for**
   - Highly emotional content
   - Characters with distinct speech patterns
   - Content requiring SSML features

## Testing Priority

When reviewing outputs, focus on:
1. Natural conversation flow (natural_speech_patterns)
2. Effective use of pauses (punctuation_tests, sentence_silence_tests)
3. Speech rate for different contexts (speech_rate_tests, combined_techniques)
4. Practical workarounds (emphasis_workarounds, pause_workaround_markers)