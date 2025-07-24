# Piper TTS Test Results

**Date**: 2025-07-23 22:16:00
**Model**: voices/en_US-lessac-medium


## baseline_tests
*Basic functionality tests*

### [baseline_1] Simple sentence
- **Text**: `Hello, this is a simple test of Piper TTS.`
- **Parameters**: `{}`
- **Output**: `baseline_1_Simple_sentence.wav`
- **Status**: ✓ Success

### [baseline_2] Multiple sentences
- **Text**: `This is the first sentence. This is the second sentence. And this is the third.`
- **Parameters**: `{}`
- **Output**: `baseline_2_Multiple_sentences.wav`
- **Status**: ✓ Success

### [baseline_3] Question intonation
- **Text**: `Is this working correctly? I hope it sounds natural.`
- **Parameters**: `{}`
- **Output**: `baseline_3_Question_intonation.wav`
- **Status**: ✓ Success

### [baseline_4] Exclamation
- **Text**: `This is amazing! I can't believe how well it works!`
- **Parameters**: `{}`
- **Output**: `baseline_4_Exclamation.wav`
- **Status**: ✓ Success


## punctuation_tests
*Testing punctuation handling and natural pauses*

### [punct_1] Comma pauses
- **Text**: `First, we need to understand, that commas, create natural pauses.`
- **Parameters**: `{}`
- **Output**: `punct_1_Comma_pauses.wav`
- **Status**: ✓ Success

### [punct_2] Ellipsis trailing off
- **Text**: `I'm not sure... maybe we could... well, let me think...`
- **Parameters**: `{}`
- **Output**: `punct_2_Ellipsis_trailing_off.wav`
- **Status**: FAILURE - Ellipsis were ignored and treated as if they weren't there


### [punct_3] Em-dash interruption
- **Text**: `I was going to say-- wait, that's not right-- let me start over.`
- **Parameters**: `{}`
- **Output**: `punct_3_Em-dash_interruption.wav`
- **Status**: FAILURE - dashes were ignored and treated as if they weren't there


### [punct_4] Semicolon and colon
- **Text**: `Here's the thing; it's complicated. Consider this: timing is everything.`
- **Parameters**: `{}`
- **Output**: `punct_4_Semicolon_and_colon.wav`
- **Status**: ✓ Success

### [punct_5] Multiple periods for longer pause
- **Text**: `Let me think about that... ... ... Yes, I understand now.`
- **Parameters**: `{}`
- **Output**: `punct_5_Multiple_periods_for_longer_pause.wav`
- **Status**: FAILURE - Ellipsis were ignored and treated as if they weren't there

### [punct_6] Parenthetical asides
- **Text**: `The algorithm (which is quite complex) processes the data efficiently.`
- **Parameters**: `{}`
- **Output**: `punct_6_Parenthetical_asides.wav`
- **Status**: FAILURE - () were ignored and treated as if they weren't there


## sentence_silence_tests
*Testing sentence_silence parameter variations*

### [silence_1] Default sentence silence
- **Text**: `First sentence ends here. Second sentence starts here. Third sentence.`
- **Parameters**: `{'sentence_silence': 0.2}`
- **Output**: `silence_1_Default_sentence_silence.wav`
- **Status**: ✓ Success

### [silence_2] Short sentence silence
- **Text**: `Quick statement. Another one. And another. Keep it flowing.`
- **Parameters**: `{'sentence_silence': 0.1}`
- **Output**: `silence_2_Short_sentence_silence.wav`
- **Status**: ✓ Success

### [silence_3] Long sentence silence
- **Text**: `This needs emphasis. Take your time. Let it sink in.`
- **Parameters**: `{'sentence_silence': 1.0}`
- **Output**: `silence_3_Long_sentence_silence.wav`
- **Status**: ✓ Success

### [silence_4] Very long sentence silence
- **Text**: `Dramatic pause coming. Wait for it. There it is.`
- **Parameters**: `{'sentence_silence': 2.0}`
- **Output**: `silence_4_Very_long_sentence_silence.wav`
- **Status**: ✓ Success


## speech_rate_tests
*Testing length_scale parameter for speech rate*

### [rate_1] Normal speed
- **Text**: `This is spoken at normal speed for comparison purposes.`
- **Parameters**: `{'length_scale': 1.0}`
- **Output**: `rate_1_Normal_speed.wav`
- **Status**: ✓ Success

### [rate_2] Fast speech
- **Text**: `This is spoken quickly to convey urgency or excitement!`
- **Parameters**: `{'length_scale': 0.7}`
- **Output**: `rate_2_Fast_speech.wav`
- **Status**: ✓ Success

### [rate_3] Very fast speech
- **Text**: `This is very fast speech, almost rushed!`
- **Parameters**: `{'length_scale': 0.5}`
- **Output**: `rate_3_Very_fast_speech.wav`
- **Status**: ✓ Success

### [rate_4] Slow speech
- **Text**: `This... is... spoken... slowly... for... emphasis.`
- **Parameters**: `{'length_scale': 1.5}`
- **Output**: `rate_4_Slow_speech.wav`
- **Status**: ✓ Success - Ellipsis were ignored and treated as if they weren't there

### [rate_5] Very slow speech
- **Text**: `This. Is. Very. Slow. And. Deliberate.`
- **Parameters**: `{'length_scale': 2.0}`
- **Output**: `rate_5_Very_slow_speech.wav`
- **Status**: ✓ Success - Periods created downward inflection and increased pauses between words. The audio file had static attributed to the very slow audio rate, but was still intelligible.


## natural_speech_patterns
*Testing natural conversational patterns*

### [natural_1] Hesitation with um
- **Text**: `Let me think, um, I believe the answer is, um, forty-two.`
- **Parameters**: `{}`
- **Output**: `natural_1_Hesitation_with_um.wav`
- **Status**: ✓ FAILURE - "um" was not pronounced as a natural filler word, but rather as a separate word with a pause before and after it.

### [natural_2] Hesitation with uh
- **Text**: `So, uh, what I'm trying to say is, uh, it's complicated.`
- **Parameters**: `{}`
- **Output**: `natural_2_Hesitation_with_uh.wav`
- **Status**: ✓ FAILURE - "uh" was not pronounced as a natural filler word, but rather as a separate word with a pause before and after it.

### [natural_3] Thinking sounds
- **Text**: `Hmm, that's interesting. Hmm... let me consider that.`
- **Parameters**: `{}`
- **Output**: `natural_3_Thinking_sounds.wav`
- **Status**: ✓ FAILURE - "Hmm" was rushed. It was pronounced as a single syllable with no natural pause or inflection, making it sound more like a word than a thinking sound.

### [natural_4] Mixed fillers
- **Text**: `Well, um, you see, uh, it's like, hmm, how do I explain this?`
- **Parameters**: `{}`
- **Output**: `natural_4_Mixed_fillers.wav`
- **Status**: ✓ FAILURE - very unnatural. The fillers were pronounced as separate words with pauses before and after, rather than as natural conversational fillers.

### [natural_5] False starts
- **Text**: `The algorithm tries-- no wait, let me rephrase-- it attempts to optimize.`
- **Parameters**: `{}`
- **Output**: `natural_5_False_starts.wav`
- **Status**: ✓ FAILURE - the -- were ignored and treated as if they weren't there. there was no pause or change in intonation to indicate a false start, making it sound like a normal sentence without interruption.

### [natural_6] Self-correction
- **Text**: `It's treating data like tex-- actually, think of it like Netflix.`
- **Parameters**: `{}`
- **Output**: `natural_6_Self-correction.wav`
- **Status**: ✓ FAILURE - the -- were ignored and treated as if they weren't there. there was no pause or change in intonation to indicate a false start, making it sound like a normal sentence without interruption.

### [natural_7] Trailing thoughts
- **Text**: `I wonder if we could... no, that wouldn't work... unless...`
- **Parameters**: `{}`
- **Output**: `natural_7_Trailing_thoughts.wav`
- **Status**: ✓ FAILURE - the ... were ignored and treated as if they weren't there. there was no pause or change in intonation to indicate a trailing thought, making it sound like a normal sentence without interruption.


## emotional_expression_attempts
*Testing emotional expressions (expected to fail)*

### [emotion_1] Laughter attempt
- **Text**: `That's hilarious, haha! Oh my goodness, hehe.`
- **Parameters**: `{}`
- **Output**: `emotion_1_Laughter_attempt.wav`
- **Status**: ✓ FAILURE - "haha" and "hehe" were pronounced as normal words, not as natural laughter sounds. There was only a very slight change in intonation or rhythm to indicate laughter.

### [emotion_2] Sigh attempt
- **Text**: `Hahhh... well, that's disappointing. *sigh* What can we do?`
- **Parameters**: `{}`
- **Output**: `emotion_2_Sigh_attempt.wav`
- **Status**: ✓ FAILURE - "Hahhh..." was rushed and pronounced as a single syllable with no natural pause or inflection, making it sound more like a word than a sigh. The "*sigh*" was spoken literally, spelling out "asterisk sigh asterisk" as if it were a normal word.

### [emotion_3] Surprise gasp
- **Text**: `What?! No way! That's-- that's incredible!`
- **Parameters**: `{}`
- **Output**: `emotion_3_Surprise_gasp.wav`
- **Status**: ✓ FAILURE - "What?!" was pronounced as a normal question, without the expected rising intonation or gasp. "that's incredible!" had a slight change in intonation, but was not natural or expressive enough to convey surprise.

### [emotion_4] Frustration
- **Text**: `Ugh, this is so frustrating! Argh! Why won't it work?!`
- **Parameters**: `{}`
- **Output**: `emotion_4_Frustration.wav`
- **Status**: ✓ FAILURE - "Ugh" and "Argh" were pronounced as normal words, not as natural expressions of frustration.

### [emotion_5] Bracketed cues (will be spoken)
- **Text**: `[sighs] I wish this worked. [laughs] But it doesn't. [breathing heavily]`
- **Parameters**: `{}`
- **Output**: `emotion_5_Bracketed_cues_(will_be_spoken).wav`
- **Status**: ✓ FAILURE - [] were ignored and treated as if they weren't there. The text inside the brackets was spoken literally, spelling out "sighs" and "laughs" and "breathing heavily" rather than being interpreted as cues for natural sounds.


## emphasis_workarounds
*Testing emphasis through various techniques*

### [emphasis_1] ALL CAPS emphasis
- **Text**: `This is REALLY important. I mean REALLY, REALLY important!`
- **Parameters**: `{}`
- **Output**: `emphasis_1_ALL_CAPS_emphasis.wav`
- **Status**: ✓ Success

### [emphasis_2] Repetition for emphasis
- **Text**: `Never, never, never give up. It's important, so important.`
- **Parameters**: `{}`
- **Output**: `emphasis_2_Repetition_for_emphasis.wav`
- **Status**: ✓ Success

### [emphasis_3] Slow rate for emphasis
- **Text**: `Listen. Very. Carefully. This. Is. Critical.`
- **Parameters**: `{'length_scale': 1.8}`
- **Output**: `emphasis_3_Slow_rate_for_emphasis.wav`
- **Status**: ✓ Success - a little too slow (the 1.8 rate generated some static) but the emphasis was clear.

### [emphasis_4] Punctuation emphasis
- **Text**: `This! Is! Amazing! Each! Word! Matters!`
- **Parameters**: `{}`
- **Output**: `emphasis_4_Punctuation_emphasis.wav`
- **Status**: ✓ Success


## conversational_dialogue
*Testing dialogue and conversation patterns*

### [dialogue_1] Back and forth
- **Text**: `Really? Yes, really. Are you sure? Absolutely certain.`
- **Parameters**: `{}`
- **Output**: `dialogue_1_Back_and_forth.wav`
- **Status**: ✓ Success

### [dialogue_2] Interruption pattern
- **Text**: `As I was saying-- Wait, what? You heard me-- No, I didn't!`
- **Parameters**: `{}`
- **Output**: `dialogue_2_Interruption_pattern.wav`
- **Status**: ✓ FAILURE - the -- were ignored and treated as if they weren't there, the interruptions were not natural enough to be interpreted as interruptions. If they were in different voices, it would have been more natural.

### [dialogue_3] Agreement and disagreement
- **Text**: `Exactly! That's what I meant. Well... I'm not so sure about that.`
- **Parameters**: `{}`
- **Output**: `dialogue_3_Agreement_and_disagreement.wav`
- **Status**: ✓ Success

### [dialogue_4] Overlapping speech marker
- **Text**: `--flexibility! Right, because there are multiple paths!`
- **Parameters**: `{}`
- **Output**: `dialogue_4_Overlapping_speech_marker.wav`
- **Status**: ✓ Success - text will need to be pre-processed to identify and handle these cases, but the speech itself was generated correctly. the -- were ignored.


## technical_content
*Testing technical and complex content*

### [tech_1] Technical terminology
- **Text**: `The API endpoint returns JSON data with a 200 OK status.`
- **Parameters**: `{}`
- **Output**: `tech_1_Technical_terminology.wav`
- **Status**: ✓ FAILURE - robotic, with no natural inflection, emphasis, or rhythm. The technical terms were pronounced correctly, but the overall delivery was flat and lacked expressiveness, making the content difficult to understand and engage with.

### [tech_2] Code-like content
- **Text**: `Call model.generate() with text parameter and audio_prompt_path.`
- **Parameters**: `{}`
- **Output**: `tech_2_Code-like_content.wav`
- **Status**: ✓ FAILURE - robotic. better pauses than tech_1 and the code-like content was pronounced correctly, but the overall delivery was flat and lacked expressiveness, making the content difficult to understand and engage with.

### [tech_3] Numbers and units
- **Text**: `Set the value to 3.14159, approximately 22,050 hertz at 16-bit depth.`
- **Parameters**: `{}`
- **Output**: `tech_3_Numbers_and_units.wav`
- **Status**: ✓ Success - good pauses and natural rhythm. The numbers and units were pronounced correctly, with appropriate pauses between them (the commas helped), making the content clear and understandable.

### [tech_4] Acronyms and abbreviations
- **Text**: `Use TTS for text-to-speech, API for application programming interface.`
- **Parameters**: `{}`
- **Output**: `tech_4_Acronyms_and_abbreviations.wav`
- **Status**: ✓ Success


## pause_workaround_markers
*Testing text markers for post-processing pauses*

### [marker_1] Tilde markers for pauses
- **Text**: `Let me think ~ about this ~ for a moment ~ please.`
- **Parameters**: `{}`
- **Output**: `marker_1_Tilde_markers_for_pauses.wav`
- **Status**: ✓ FAILURE - the ~ were pronounced as normal words, not as natural pauses.

### [marker_2] Multiple tildes for long pause
- **Text**: `And the answer is ~~~ forty-two.`
- **Parameters**: `{}`
- **Output**: `marker_2_Multiple_tildes_for_long_pause.wav`
- **Status**: ✓ FAILURE - the ~ were pronounced as normal words, not as natural pauses. multiple tildes were each spoken aloud.

### [marker_3] Pipe markers alternative
- **Text**: `First part | pause here | second part | another pause | final part.`
- **Parameters**: `{}`
- **Output**: `marker_3_Pipe_markers_alternative.wav`
- **Status**: ✓ FAILURE - the | were ignored and treated as if they weren't there. The text was spoken without any pauses, making it sound like a continuous sentence without breaks. the text will need to be pre-processed to identify and handle these cases.


## combined_techniques
*Combining multiple techniques*

### [combined_1] Slow dramatic speech
- **Text**: `This... is... the most... important... thing... you'll hear... today.`
- **Parameters**: `{'length_scale': 1.5, 'sentence_silence': 0.8}`
- **Output**: `combined_1_Slow_dramatic_speech.wav`
- **Status**: ✓ Success - 1.5 is a good speed for a slow and dramatic effect. the ... were ignored.

### [combined_2] Fast urgent speech
- **Text**: `Quick! We need to go! Now! There's no time!`
- **Parameters**: `{'length_scale': 0.6, 'sentence_silence': 0.1}`
- **Output**: `combined_2_Fast_urgent_speech.wav`
- **Status**: ✓ A little bit rushed, the urgency was not conveyed well. the exclamation points created pauses that subtracted from the urgency of the speech.

### [combined_3] Natural conversation with pauses
- **Text**: `So, um... I was thinking... maybe we could-- no, wait... yes, let's do it!`
- **Parameters**: `{'sentence_silence': 0.5}`
- **Output**: `combined_3_Natural_conversation_with_pauses.wav`
- **Status**: ✓ FAILURE - see notes for the individual tests.

### [combined_4] Technical explanation with emphasis
- **Text**: `The algorithm... now pay attention... processes THOUSANDS of iterations.`
- **Parameters**: `{'length_scale': 1.2, 'sentence_silence': 0.6}`
- **Output**: `combined_4_Technical_explanation_with_emphasis.wav`
- **Status**: ✓ Success


## Summary
Test suite completed at 2025-07-23 22:16:39
Output directory: `test_outputs/piper_tests_20250723_221600`
