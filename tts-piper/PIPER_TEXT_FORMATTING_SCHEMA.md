# Piper TTS Text Formatting Schema

## Overview
This schema provides comprehensive guidelines for formatting text to achieve optimal results with Piper TTS, based on extensive testing and empirical results.

## Core Principles
1. **Piper accepts plain text only** - No SSML or markup support
2. **Limited prosody control** - Focus on what actually works
3. **Post-processing required** - For advanced effects, segment and combine audio

## Effective Formatting Techniques

### 1. Punctuation-Based Control ✅

**Working Punctuation:**
```
. (period)         → Natural sentence ending with pause
, (comma)          → Short pause within sentence
? (question mark)  → Rising intonation
! (exclamation)    → Emphatic tone
; (semicolon)      → Medium pause
: (colon)          → Medium pause with continuation tone
```

**Non-Working Punctuation:**
```
... (ellipsis)     → Ignored completely
-- (em-dash)       → Ignored completely
() (parentheses)   → Ignored completely
```

### 2. Emphasis Techniques ✅

**ALL CAPS Method:**
```
Input: "This is REALLY important"
Result: Natural emphasis on "REALLY"
```

**Exclamation Points:**
```
Input: "Amazing! Incredible! Wow!"
Result: Each word gets emphatic tone
```

**Repetition:**
```
Input: "Never, never, never give up"
Result: Building emphasis through repetition
```

### 3. Speech Rate Control ✅

**Parameter: length_scale**
```
0.5  → Double speed (very fast)
0.7  → Fast speech (urgent)
1.0  → Normal speed (default)
1.5  → Slow speech (deliberate)
2.0  → Very slow (may introduce artifacts)
```

**Best Practices:**
- Use 0.6-0.8 for urgent/excited speech
- Use 1.2-1.5 for thoughtful/dramatic speech
- Avoid values below 0.5 or above 1.8

### 4. Sentence Silence Control ✅

**Parameter: sentence_silence (in seconds)**
```
0.1  → Rapid-fire delivery
0.2  → Default natural pace
0.5  → Thoughtful pace
1.0  → Dramatic pauses
2.0  → Very long pauses
```

## Formatting Patterns

### Natural Dialogue
```
# Good Pattern:
"Really? Yes, really. Are you sure? Absolutely certain."
- Short sentences with appropriate punctuation
- Natural question/answer flow

# Avoid:
"I was saying-- no wait-- let me rephrase"
- Dashes are ignored, interruptions don't work
```

### Technical Content
```
# Good Pattern:
"The API returns JSON data, with a 200 status code."
- Use commas for natural pauses
- Spell out technical terms clearly

# Format Numbers:
"Set to 3.14159, approximately 22,050 hertz"
- Use commas in large numbers for pauses
```

### Lists and Instructions
```
# Good Pattern:
"First, prepare the data. Second, run the analysis. Finally, review results."
- Use ordinal markers with commas
- Clear sentence boundaries
```

## Workaround Strategies

### Creating Custom Pauses
Since Piper ignores `...`, `--`, and pause markers, use audio segmentation:

**Text Preparation:**
```python
segments = [
    "Let me think about this",
    "PAUSE_1S",
    "The answer is forty-two"
]
```

**Processing:**
1. Generate audio for each text segment
2. Create silence files for PAUSE markers
3. Concatenate with sox or ffmpeg

### Simulating Natural Speech

**Instead of:** `"Um, let me think, uh, about that"`

**Use:** Multiple segments with sentence_silence:
```
Text 1: "Let me think."
Text 2: "About that particular issue."
Parameters: {"sentence_silence": 0.8}
```

### Emphasis Through Speed Variation

**For single word emphasis:**
```python
# Generate normally
"The algorithm processes"

# Generate emphasized word slowly
"THOUSANDS" (length_scale=1.5)

# Generate normally
"of data points"

# Combine audio files
```

## Schema Summary

### Input Format
```json
{
  "text": "Plain text with punctuation only",
  "parameters": {
    "length_scale": 1.0,      // 0.5-2.0
    "sentence_silence": 0.2   // 0.0-2.0
  }
}
```

### Text Preprocessing Rules
1. **Remove:** Ellipsis (...), dashes (--), brackets, special markers
2. **Convert:** 
   - Multiple periods to single period
   - Filler words to separate sentences
   - Emphasis words to ALL CAPS
3. **Add:** Commas for natural pauses
4. **Split:** At major pause points for segment processing

### Quality Guidelines

**DO:**
- Use sentence boundaries for pauses
- Apply ALL CAPS for emphasis
- Leverage punctuation effectively
- Keep sentences concise
- Use commas liberally for rhythm

**DON'T:**
- Expect ellipsis or dashes to work
- Use filler words (um, uh)
- Attempt emotional sounds
- Rely on special characters
- Create overly long sentences

## Production Recommendations

### Best Use Cases
1. **Narration:** Clear, well-punctuated text
2. **Instructions:** Step-by-step with clear pauses
3. **Announcements:** Short, emphatic statements
4. **Technical docs:** With proper formatting

### Avoid For
1. **Natural conversation:** Limited expressiveness
2. **Emotional content:** No laugh/sigh support
3. **Dynamic dialogue:** No interruption support
4. **Character voices:** Single voice only

## Example Implementation

### Basic Usage
```bash
echo "Welcome! This is IMPORTANT. Please listen carefully." | \
  piper --model en_US-amy-medium \
        --length_scale 1.0 \
        --sentence_silence 0.3 > output.wav
```

### Advanced Segmented Approach
```python
def format_for_piper(text):
    # Replace problem punctuation
    text = text.replace("...", ".")
    text = text.replace("--", ",")
    
    # Mark emphasis
    text = re.sub(r'\*(\w+)\*', lambda m: m.group(1).upper(), text)
    
    # Split on pause markers
    segments = text.split(" ~ ")
    
    return segments
```

## Validation Checklist
- [ ] Text uses only supported punctuation
- [ ] Emphasis uses ALL CAPS or exclamation points
- [ ] Pauses use sentence boundaries or commas
- [ ] No ellipsis, dashes, or special markers
- [ ] Appropriate length_scale for desired effect
- [ ] Suitable sentence_silence for pacing