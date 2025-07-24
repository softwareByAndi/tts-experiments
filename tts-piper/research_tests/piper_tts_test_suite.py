#!/usr/bin/env python3
"""
Comprehensive Piper-TTS Test Suite
Tests various non-verbal cues, prosody features, and workarounds
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path

# Test categories with descriptions and test cases
TEST_SUITE = {
    "baseline_tests": {
        "description": "Basic functionality tests",
        "tests": [
            {
                "id": "baseline_1",
                "name": "Simple sentence",
                "text": "Hello, this is a simple test of Piper TTS.",
                "params": {}
            },
            {
                "id": "baseline_2", 
                "name": "Multiple sentences",
                "text": "This is the first sentence. This is the second sentence. And this is the third.",
                "params": {}
            },
            {
                "id": "baseline_3",
                "name": "Question intonation",
                "text": "Is this working correctly? I hope it sounds natural.",
                "params": {}
            },
            {
                "id": "baseline_4",
                "name": "Exclamation",
                "text": "This is amazing! I can't believe how well it works!",
                "params": {}
            }
        ]
    },
    
    "punctuation_tests": {
        "description": "Testing punctuation handling and natural pauses",
        "tests": [
            {
                "id": "punct_1",
                "name": "Comma pauses",
                "text": "First, we need to understand, that commas, create natural pauses.",
                "params": {}
            },
            {
                "id": "punct_2",
                "name": "Ellipsis trailing off",
                "text": "I'm not sure... maybe we could... well, let me think...",
                "params": {}
            },
            {
                "id": "punct_3",
                "name": "Em-dash interruption",
                "text": "I was going to say-- wait, that's not right-- let me start over.",
                "params": {}
            },
            {
                "id": "punct_4",
                "name": "Semicolon and colon",
                "text": "Here's the thing; it's complicated. Consider this: timing is everything.",
                "params": {}
            },
            {
                "id": "punct_5",
                "name": "Multiple periods for longer pause",
                "text": "Let me think about that... ... ... Yes, I understand now.",
                "params": {}
            },
            {
                "id": "punct_6",
                "name": "Parenthetical asides",
                "text": "The algorithm (which is quite complex) processes the data efficiently.",
                "params": {}
            }
        ]
    },
    
    "sentence_silence_tests": {
        "description": "Testing sentence_silence parameter variations",
        "tests": [
            {
                "id": "silence_1",
                "name": "Default sentence silence",
                "text": "First sentence ends here. Second sentence starts here. Third sentence.",
                "params": {"sentence_silence": 0.2}
            },
            {
                "id": "silence_2",
                "name": "Short sentence silence",
                "text": "Quick statement. Another one. And another. Keep it flowing.",
                "params": {"sentence_silence": 0.1}
            },
            {
                "id": "silence_3",
                "name": "Long sentence silence",
                "text": "This needs emphasis. Take your time. Let it sink in.",
                "params": {"sentence_silence": 1.0}
            },
            {
                "id": "silence_4",
                "name": "Very long sentence silence", 
                "text": "Dramatic pause coming. Wait for it. There it is.",
                "params": {"sentence_silence": 2.0}
            }
        ]
    },
    
    "speech_rate_tests": {
        "description": "Testing length_scale parameter for speech rate",
        "tests": [
            {
                "id": "rate_1",
                "name": "Normal speed",
                "text": "This is spoken at normal speed for comparison purposes.",
                "params": {"length_scale": 1.0}
            },
            {
                "id": "rate_2",
                "name": "Fast speech",
                "text": "This is spoken quickly to convey urgency or excitement!",
                "params": {"length_scale": 0.7}
            },
            {
                "id": "rate_3",
                "name": "Very fast speech",
                "text": "This is very fast speech, almost rushed!",
                "params": {"length_scale": 0.5}
            },
            {
                "id": "rate_4",
                "name": "Slow speech",
                "text": "This... is... spoken... slowly... for... emphasis.",
                "params": {"length_scale": 1.5}
            },
            {
                "id": "rate_5",
                "name": "Very slow speech",
                "text": "This. Is. Very. Slow. And. Deliberate.",
                "params": {"length_scale": 2.0}
            }
        ]
    },
    
    "natural_speech_patterns": {
        "description": "Testing natural conversational patterns",
        "tests": [
            {
                "id": "natural_1",
                "name": "Hesitation with um",
                "text": "Let me think, um, I believe the answer is, um, forty-two.",
                "params": {}
            },
            {
                "id": "natural_2",
                "name": "Hesitation with uh",
                "text": "So, uh, what I'm trying to say is, uh, it's complicated.",
                "params": {}
            },
            {
                "id": "natural_3",
                "name": "Thinking sounds",
                "text": "Hmm, that's interesting. Hmm... let me consider that.",
                "params": {}
            },
            {
                "id": "natural_4",
                "name": "Mixed fillers",
                "text": "Well, um, you see, uh, it's like, hmm, how do I explain this?",
                "params": {}
            },
            {
                "id": "natural_5",
                "name": "False starts",
                "text": "The algorithm tries-- no wait, let me rephrase-- it attempts to optimize.",
                "params": {}
            },
            {
                "id": "natural_6",
                "name": "Self-correction",
                "text": "It's treating data like tex-- actually, think of it like Netflix.",
                "params": {}
            },
            {
                "id": "natural_7",
                "name": "Trailing thoughts",
                "text": "I wonder if we could... no, that wouldn't work... unless...",
                "params": {}
            }
        ]
    },
    
    "emotional_expression_attempts": {
        "description": "Testing emotional expressions (expected to fail)",
        "tests": [
            {
                "id": "emotion_1",
                "name": "Laughter attempt",
                "text": "That's hilarious, haha! Oh my goodness, hehe.",
                "params": {}
            },
            {
                "id": "emotion_2",
                "name": "Sigh attempt",
                "text": "Hahhh... well, that's disappointing. *sigh* What can we do?",
                "params": {}
            },
            {
                "id": "emotion_3",
                "name": "Surprise gasp",
                "text": "What?! No way! That's-- that's incredible!",
                "params": {}
            },
            {
                "id": "emotion_4",
                "name": "Frustration",
                "text": "Ugh, this is so frustrating! Argh! Why won't it work?!",
                "params": {}
            },
            {
                "id": "emotion_5",
                "name": "Bracketed cues (will be spoken)",
                "text": "[sighs] I wish this worked. [laughs] But it doesn't. [breathing heavily]",
                "params": {}
            }
        ]
    },
    
    "emphasis_workarounds": {
        "description": "Testing emphasis through various techniques",
        "tests": [
            {
                "id": "emphasis_1",
                "name": "ALL CAPS emphasis",
                "text": "This is REALLY important. I mean REALLY, REALLY important!",
                "params": {}
            },
            {
                "id": "emphasis_2",
                "name": "Repetition for emphasis",
                "text": "Never, never, never give up. It's important, so important.",
                "params": {}
            },
            {
                "id": "emphasis_3",
                "name": "Slow rate for emphasis",
                "text": "Listen. Very. Carefully. This. Is. Critical.",
                "params": {"length_scale": 1.8}
            },
            {
                "id": "emphasis_4",
                "name": "Punctuation emphasis",
                "text": "This! Is! Amazing! Each! Word! Matters!",
                "params": {}
            }
        ]
    },
    
    "conversational_dialogue": {
        "description": "Testing dialogue and conversation patterns",
        "tests": [
            {
                "id": "dialogue_1",
                "name": "Back and forth",
                "text": "Really? Yes, really. Are you sure? Absolutely certain.",
                "params": {}
            },
            {
                "id": "dialogue_2",
                "name": "Interruption pattern",
                "text": "As I was saying-- Wait, what? You heard me-- No, I didn't!",
                "params": {}
            },
            {
                "id": "dialogue_3",
                "name": "Agreement and disagreement",
                "text": "Exactly! That's what I meant. Well... I'm not so sure about that.",
                "params": {}
            },
            {
                "id": "dialogue_4",
                "name": "Overlapping speech marker",
                "text": "--flexibility! Right, because there are multiple paths!",
                "params": {}
            }
        ]
    },
    
    "technical_content": {
        "description": "Testing technical and complex content",
        "tests": [
            {
                "id": "tech_1",
                "name": "Technical terminology",
                "text": "The API endpoint returns JSON data with a 200 OK status.",
                "params": {}
            },
            {
                "id": "tech_2",
                "name": "Code-like content",
                "text": "Call model.generate() with text parameter and audio_prompt_path.",
                "params": {}
            },
            {
                "id": "tech_3",
                "name": "Numbers and units",
                "text": "Set the value to 3.14159, approximately 22,050 hertz at 16-bit depth.",
                "params": {}
            },
            {
                "id": "tech_4",
                "name": "Acronyms and abbreviations",
                "text": "Use TTS for text-to-speech, API for application programming interface.",
                "params": {}
            }
        ]
    },
    
    "pause_workaround_markers": {
        "description": "Testing text markers for post-processing pauses",
        "tests": [
            {
                "id": "marker_1",
                "name": "Tilde markers for pauses",
                "text": "Let me think ~ about this ~ for a moment ~ please.",
                "params": {}
            },
            {
                "id": "marker_2",
                "name": "Multiple tildes for long pause",
                "text": "And the answer is ~~~ forty-two.",
                "params": {}
            },
            {
                "id": "marker_3",
                "name": "Pipe markers alternative",
                "text": "First part | pause here | second part | another pause | final part.",
                "params": {}
            }
        ]
    },
    
    "combined_techniques": {
        "description": "Combining multiple techniques",
        "tests": [
            {
                "id": "combined_1",
                "name": "Slow dramatic speech",
                "text": "This... is... the most... important... thing... you'll hear... today.",
                "params": {"length_scale": 1.5, "sentence_silence": 0.8}
            },
            {
                "id": "combined_2",
                "name": "Fast urgent speech",
                "text": "Quick! We need to go! Now! There's no time!",
                "params": {"length_scale": 0.6, "sentence_silence": 0.1}
            },
            {
                "id": "combined_3",
                "name": "Natural conversation with pauses",
                "text": "So, um... I was thinking... maybe we could-- no, wait... yes, let's do it!",
                "params": {"sentence_silence": 0.5}
            },
            {
                "id": "combined_4",
                "name": "Technical explanation with emphasis",
                "text": "The algorithm... now pay attention... processes THOUSANDS of iterations.",
                "params": {"length_scale": 1.2, "sentence_silence": 0.6}
            }
        ]
    }
}

def generate_audio(text, output_file, model="voices/en_US-lessac-medium", **params):
    """Generate audio using Piper TTS with specified parameters"""
    # Check if we're in a virtual environment and use the correct piper path
    piper_cmd = "piper"
    venv_piper = "./venv-piper/bin/piper"
    if os.path.exists(venv_piper):
        piper_cmd = venv_piper
    
    cmd = [piper_cmd, "--model", model, "-f", output_file]
    
    # Add optional parameters
    if "sentence_silence" in params:
        cmd.extend(["--sentence_silence", str(params["sentence_silence"])])
    if "length_scale" in params:
        cmd.extend(["--length_scale", str(params["length_scale"])])
    
    # Run Piper with text input
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate(input=text.encode())
    
    if process.returncode != 0:
        print(f"Error generating audio: {stderr.decode()}")
        return False
    return True

def run_test_suite(output_dir="test_outputs", model="voices/en_US-lessac-medium"):
    """Run the complete test suite"""
    # Create output directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_dir = Path(output_dir) / f"piper_tests_{timestamp}"
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Create results log
    results_file = test_dir / "test_results.md"
    with open(results_file, "w") as f:
        f.write(f"# Piper TTS Test Results\n\n")
        f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Model**: {model}\n\n")
        
        # Run each test category
        for category_key, category_data in TEST_SUITE.items():
            print(f"\n{'='*60}")
            print(f"Running {category_key}: {category_data['description']}")
            print(f"{'='*60}")
            
            f.write(f"\n## {category_key}\n")
            f.write(f"*{category_data['description']}*\n\n")
            
            # Create category subdirectory
            category_dir = test_dir / category_key
            category_dir.mkdir(exist_ok=True)
            
            # Run each test in category
            for test in category_data['tests']:
                test_id = test['id']
                test_name = test['name']
                test_text = test['text']
                test_params = test['params']
                
                print(f"\n[{test_id}] {test_name}")
                print(f"Text: {test_text[:50]}..." if len(test_text) > 50 else f"Text: {test_text}")
                print(f"Params: {test_params}")
                
                # Generate audio file
                output_file = category_dir / f"{test_id}_{test_name.replace(' ', '_')}.wav"
                success = generate_audio(test_text, str(output_file), model, **test_params)
                
                if success:
                    print(f"✓ Generated: {output_file.name}")
                    f.write(f"### [{test_id}] {test_name}\n")
                    f.write(f"- **Text**: `{test_text}`\n")
                    f.write(f"- **Parameters**: `{test_params}`\n")
                    f.write(f"- **Output**: `{output_file.name}`\n")
                    f.write(f"- **Status**: ✓ Success\n\n")
                else:
                    print(f"✗ Failed to generate audio")
                    f.write(f"### [{test_id}] {test_name}\n")
                    f.write(f"- **Status**: ✗ Failed\n\n")
        
        # Add summary
        f.write(f"\n## Summary\n")
        f.write(f"Test suite completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Output directory: `{test_dir}`\n")
    
    print(f"\n{'='*60}")
    print(f"Test suite complete!")
    print(f"Results saved to: {results_file}")
    print(f"Audio files saved to: {test_dir}")
    print(f"{'='*60}")
    
    return test_dir

if __name__ == "__main__":
    # Check if Piper is available
    piper_cmd = "piper"
    venv_piper = "./venv-piper/bin/piper"
    if os.path.exists(venv_piper):
        piper_cmd = venv_piper
    
    try:
        # Piper doesn't have --version, so check with --help
        result = subprocess.run([piper_cmd, "--help"], capture_output=True)
        if result.returncode != 0 and "usage: piper" not in result.stderr.decode():
            raise FileNotFoundError
    except FileNotFoundError:
        print("Error: Piper TTS is not installed or not in PATH")
        print("Install from: https://github.com/rhasspy/piper")
        exit(1)
    
    # Run the test suite
    print("Starting Piper TTS Comprehensive Test Suite")
    print("This will generate multiple audio files for review")
    
    output_dir = run_test_suite()
    
    print(f"\nNext steps:")
    print(f"1. Review the audio files in: {output_dir}")
    print(f"2. Check test_results.md for the complete test log")
    print(f"3. Note which techniques work well and which don't")
    print(f"4. Consider post-processing options for unsupported features")