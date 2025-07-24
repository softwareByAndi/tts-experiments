# Piper TTS Test Suite Schema Documentation

## Overview

This document provides a comprehensive schema for the Piper TTS test suite, detailing the test structure, expected behaviors, and actual outcomes based on empirical testing.

## Test Suite Architecture

### 1. Test Categories

The test suite is organized into 11 distinct categories, each targeting specific aspects of TTS functionality:

```yaml
test_categories:
  baseline_tests:
    purpose: Verify core TTS functionality
    focus: Basic speech synthesis, punctuation handling, intonation
    
  punctuation_tests:
    purpose: Evaluate punctuation interpretation
    focus: Pauses, interruptions, trailing off effects
    
  sentence_silence_tests:
    purpose: Test inter-sentence pause control
    focus: sentence_silence parameter variations (0.1 - 2.0 seconds)
    
  speech_rate_tests:
    purpose: Assess speech speed control
    focus: length_scale parameter (0.5 - 2.0)
    
  natural_speech_patterns:
    purpose: Test conversational elements
    focus: Filler words, hesitations, self-corrections
    
  emotional_expression_attempts:
    purpose: Explore emotional content (expected failures)
    focus: Laughter, sighs, gasps, frustration
    
  emphasis_workarounds:
    purpose: Test emphasis techniques
    focus: ALL CAPS, repetition, punctuation, speech rate
    
  conversational_dialogue:
    purpose: Evaluate dialogue patterns
    focus: Back-and-forth, interruptions, agreements
    
  technical_content:
    purpose: Test technical speech
    focus: Terminology, numbers, acronyms, code-like content
    
  pause_workaround_markers:
    purpose: Test post-processing markers
    focus: Tilde (~), pipe (|), other pause indicators
    
  combined_techniques:
    purpose: Test parameter combinations
    focus: Dramatic speech, urgency, natural conversation
```

### 2. Test Structure

Each test follows a consistent schema:

```python
test_schema = {
    "id": str,           # Unique identifier (e.g., "baseline_1")
    "name": str,         # Descriptive name
    "text": str,         # Input text to synthesize
    "params": dict       # Piper parameters (optional)
}
```

### 3. Parameter Schema

```yaml
piper_parameters:
  sentence_silence:
    type: float
    range: [0.1, 2.0]
    default: 0.2
    effect: Controls pause duration between sentences
    
  length_scale:
    type: float
    range: [0.5, 2.0]
    default: 1.0
    effect: Controls overall speech rate (0.5 = 2x speed, 2.0 = 0.5x speed)
```

## Test Behavior Mapping

### Working Features ✅

| Feature | Implementation | Effectiveness | Notes |
|---------|----------------|---------------|--------|
| Basic punctuation | Period, comma, question mark | High | Natural pauses and intonation |
| Sentence silence | sentence_silence parameter | High | Reliable control over inter-sentence pauses |
| Speech rate | length_scale parameter | High | Consistent speed control |
| ALL CAPS emphasis | Text in capitals | Medium | Slight emphasis, not dramatic |
| Repetition | Repeated words | Medium | Works but sounds unnatural |
| Exclamation marks | ! punctuation | Medium | Slight emphasis effect |
| Basic questions | ? punctuation | High | Natural rising intonation |

### Non-Working Features ❌

| Feature | Expected Behavior | Actual Behavior | Severity |
|---------|-------------------|-----------------|----------|
| Ellipsis (...) | Create pauses | Ignored completely | High |
| Em-dashes (--) | Indicate interruption | Ignored completely | High |
| Filler words (um, uh) | Natural hesitation | Pronounced as separate words | High |
| Bracketed cues [sighs] | Non-verbal sounds | Spoken literally | Critical |
| Asterisk actions *sigh* | Non-verbal sounds | Spoken with "asterisk" | Critical |
| Tilde markers (~) | Pause indicators | Pronounced as "tilde" | High |
| Pipe markers (\|) | Pause indicators | Ignored | Medium |
| Emotional expressions | Natural emotion | Robotic pronunciation | High |
| Parentheses | Aside intonation | Ignored | Medium |

### Mixed Results 🔧

| Feature | Success Rate | Notes |
|---------|--------------|--------|
| Technical content | 50% | Numbers/units work well, terminology sounds robotic |
| Dialogue patterns | 40% | Basic back-and-forth works, interruptions fail |
| Natural speech | 20% | Most conversational elements fail |
| Combined techniques | 60% | Parameter combinations work, text markers fail |

## Test Result Schema

### Success Criteria

```yaml
test_result:
  status: 
    - success: Feature works as intended
    - failure: Feature doesn't work or produces unintended output
    - partial: Some aspects work, others don't
    
  evaluation_criteria:
    - naturalness: How human-like the output sounds
    - functionality: Whether the feature achieves its purpose
    - consistency: Reproducible results across tests
    - usability: Practical for production use
```

### Failure Patterns

1. **Literal Pronunciation**: Special characters or bracketed text spoken as words
2. **Ignored Markers**: Punctuation or symbols having no effect
3. **Robotic Delivery**: Technically correct but lacking natural prosody
4. **Unnatural Pauses**: Filler words creating awkward breaks
5. **Static/Artifacts**: Audio quality issues at extreme parameter values

## Recommended Usage Patterns

### Effective Techniques

```python
# 1. Dramatic emphasis
{
    "text": "This. Is. Important.",
    "params": {"length_scale": 1.5, "sentence_silence": 0.8}
}

# 2. Urgent speech
{
    "text": "Quick! We need to act now!",
    "params": {"length_scale": 0.7, "sentence_silence": 0.1}
}

# 3. Technical clarity
{
    "text": "Set the value to 3.14, then press enter.",
    "params": {"sentence_silence": 0.3}
}
```

### Workaround Strategies

1. **Post-Processing Pipeline**
   - Split text at custom markers
   - Generate segments with different parameters
   - Concatenate with silence files

2. **Text Preprocessing**
   - Replace emotion markers with approximations
   - Convert pause markers to sentence breaks
   - Rewrite filler words as separate sentences

3. **Multi-Voice Simulation**
   - Generate dialogue parts separately
   - Use different parameters for each speaker
   - Combine in post-production

## Production Recommendations

### Best Use Cases
- Technical documentation narration
- Simple instructional content
- Basic dialogue without emotions
- Content with consistent tone

### Avoid For
- Emotional storytelling
- Natural conversation simulation
- Content requiring dynamic prosody
- Interactive dialogue systems

## Test Suite Extension Guide

### Adding New Tests

```python
new_test = {
    "category": "category_name",
    "test": {
        "id": "unique_id",
        "name": "Descriptive Name",
        "text": "Test input text",
        "params": {"parameter": value},
        "expected_outcome": "description",
        "evaluation_metrics": ["naturalness", "functionality"]
    }
}
```

### Validation Schema

```yaml
test_validation:
  required_fields: [id, name, text]
  optional_fields: [params, expected_outcome]
  parameter_validation:
    sentence_silence: [0.1, 2.0]
    length_scale: [0.5, 2.0]
  text_validation:
    max_length: 500
    encoding: UTF-8
```

## Conclusion

The Piper TTS test suite reveals a system optimized for basic, efficient speech synthesis with limited prosody control. Understanding these limitations and working within them, rather than against them, yields the best results. The schema documented here provides a framework for systematic testing and evaluation of TTS capabilities.