# To run this code you need to install the following dependencies:
# pip install google-genai

import base64
import mimetypes
import os
import re
import struct
from google import genai
from google.genai import types


def save_binary_file(file_name, data):
    f = open(file_name, "wb")
    f.write(data)
    f.close()
    print(f"File saved to to: {file_name}")


def generate():
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-2.5-pro-preview-tts"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""Speaker 1 - Speech Style:
Mid-30s to early-40s software engineer. Speaks with a mix of experience and vulnerability - confident technical knowledge but genuine concern about the future. Conversational pace with occasional faster sections when anxious or excited. Uses humor as a coping mechanism, particularly dry wit and self-deprecating jokes. Voice softens slightly when asking worried questions, settles when making sarcastic observations. Natural pauses for effect before punchlines. Authentic \"thinking out loud\" quality.
Speaker 2 - Speech Style:
Enthusiastic tech researcher/analyst in their 30s. Speaks with infectious curiosity and optimism without being patronizing. Clear, well-paced delivery that speeds up when sharing exciting data points. Natural storyteller who uses \"So...\" and \"Get this...\" to build anticipation. Warm, reassuring tone when addressing concerns. Genuine laughter at good jokes. Emphasizes key statistics and findings with slight pauses. Academic expertise delivered in an accessible, friendly manner. Think \"favorite professor who actually makes the subject interesting.\"

Speaker 1: Okay, I've got to get this off my chest. I've been a senior software engineer for like 15 years, and I'm starting to freak out about all these AI coding tools. Am I going to be obsolete in five years? Should I be learning to drive a truck or something?
Speaker 2: [laughs] Hold on, before you get your CDL, let me share some research I've been digging into. It's actually pretty fascinating. So Anthropic did this study on Claude Code, and they found that 79% of conversations were pure automation - like, the AI just doing the work directly, not even collaborating with humans.
Speaker 1: See! That's exactly what I'm talking about! We're toast!
Speaker 2: But wait, wait - here's the interesting part. GitHub surveyed developers, and 57% said AI tools actually helped them develop their coding skills. Plus, developers using Copilot were finishing 26% more tasks. So it's not replacing them, it's making them faster.
Speaker 1: Okay, but what about code quality? I've seen some of the garbage that AI spits out.
Speaker 2: Oh, you're gonna love this. GitClear analyzed 153 million lines of code changes and found that copy-pasted code is increasing way faster than actually updated or refactored code. So yeah, AI might be creating more... let's call it \"technical debt.\"
Speaker 1: [groans] Great, so we'll still have jobs, but we'll just be cleaning up AI's mess?
Speaker 2: Well, let's look at the job market data. This is where it gets really interesting. AI research scientists and ML engineers - their job openings grew by 80% and 70%. But mobile engineers, frontend engineers, data engineers? They all dropped more than 20%.
Speaker 1: Wait, what about backend engineers?
Speaker 2: Only dropped 14%! Compared to 24% for frontend. The theory is companies need stable backend infrastructure to actually deploy all these ML models.
Speaker 1: Huh. So backend is safer than frontend? Plot twist!
Speaker 2: Right? And get this - Gartner predicts that by 2027, 50% of software engineering orgs will use these AI platforms. But here's the kicker - they also say 80% of programming jobs will remain human-centric.
Speaker 1: Okay, but what exactly can't AI do? Because it feels like it's getting better at everything.
Speaker 2: This is where it gets really interesting. Complex problem solving, especially with ambiguous or novel situations? AI struggles hard. Like, it can't understand context the way we do. And don't even get me started on emotional intelligence and ethics.
Speaker 1: Oh god, imagine AI trying to navigate office politics or understand why the CEO's \"quick favor\" is actually a three-month project.
Speaker 2: [laughs] Exactly! And there's this thing engineers are calling the \"last mile\" problem. AI can generate like 70% of a plausible solution, but that final 30% - handling edge cases, refining architecture, making it actually maintainable? That needs serious human expertise.
Speaker 1: Okay, so I'm not completely doomed. But what should I actually be doing to stay relevant?
Speaker 2: Alright, so based on all this research, there are some clear strategies. First, develop AI-adjacent skills. Not saying you need to become an ML engineer, but understanding the fundamentals helps. And prompt engineering is becoming a real skill.
Speaker 1: Prompt engineering? You mean knowing how to talk to ChatGPT?
Speaker 2: It's more sophisticated than that! It's about effectively communicating with AI models to maximize productivity and accuracy. Think of it as a new programming language, but for AI.
Speaker 1: Okay, what else?
Speaker 2: Focus on high-level skills. System architecture, business acumen - and I mean really understanding OKRs, KPIs, company strategy. The magic happens when you connect engineering to business outcomes.
Speaker 1: So basically become more of a business person?
Speaker 2: More like a translator between business and tech. Also, lean into uniquely human stuff. Ethical AI development is huge. Companies need someone who can ensure their AI isn't accidentally discriminating against people or doing something sketchy.
Speaker 1: True. \"The AI did it\" isn't going to hold up in court.
Speaker 2: Exactly! And here's a mindset shift - it's not \"AI will replace me,\" it's \"humans with AI will replace humans without AI.\" Think of AI as a force multiplier.
Speaker 1: Like Iron Man's suit?
Speaker 2: Perfect analogy! Tony Stark is still valuable - the suit just makes him more powerful. Also, consider specializing in complex domains. Security, distributed systems, performance optimization. Areas that need deep, deep expertise.
Speaker 1: What about the stuff that's not in the research? Like, what's your take on why senior engineers will still matter?
Speaker 2: Oh man, I've been thinking about this a lot. First - trust and accountability. When systems fail or there's a security breach, companies need humans who can be held accountable. AI can't testify in court or explain decisions to angry customers.
Speaker 1: \"Your honor, the AI told me to do it\" isn't a great defense.
Speaker 2: [laughs] Right? And innovation versus iteration. AI is amazing at iterating on existing patterns, but true innovation? The next breakthrough algorithm or creative business solution? That's still human territory.
Speaker 1: Plus, have you ever tried to get AI to understand vague requirements? \"Make it pop more\" or \"It should feel more enterprise-y\"?
Speaker 2: Oh god, yes! Context switching and ambiguity - that's our superpower. We can read between the lines, understand what stakeholders really need versus what they say they want. Navigate office politics, implicit requirements...
Speaker 1: \"The CEO wants it to be 'faster' but what he really means is he wants to show it off at the board meeting next week.\"
Speaker 2: Exactly! And technical debt management. AI can generate code quickly, but knowing when to refactor versus rebuild? Predicting future needs? That takes years of experience seeing how systems evolve.
Speaker 1: Not to mention crisis management. When production crashes at 3 AM...
Speaker 2: Yes! You need someone who can think creatively under pressure, understand complex system interactions, make quick decisions with incomplete information. AI can assist, but human judgment in high-stakes situations? Irreplaceable.
Speaker 1: So basically, I should stop panicking?
Speaker 2: Look, your concern is totally valid. But the evidence suggests AI will transform our roles, not replace them. The key is viewing AI as a powerful tool that amplifies your expertise. Handle the routine stuff with AI, focus your energy on the complex, creative, strategic aspects that drive real business value.
Speaker 1: Human expertise plus AI capabilities.
Speaker 2: Exactly. The future belongs to engineers who can seamlessly blend both. Use AI for the boring stuff, save your brain for the hard problems that actually matter.
Speaker 1: Alright, I'm feeling better about this. Still might learn to drive a truck though. You know, as a backup.
Speaker 2: [laughs] Hey, always good to have options! But I think you'll be debugging code, not hauling cargo, for a long time to come.
Speaker 1: As long as I'm not debugging the AI's code that's debugging other AI's code. That's when I draw the line.
Speaker 2: Deal. When we hit that level of inception, we'll both become truck drivers."""),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=1.7,
        response_modalities=[
            "audio",
        ],
        speech_config=types.SpeechConfig(
            multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                speaker_voice_configs=[
                    types.SpeakerVoiceConfig(
                        speaker="Speaker 1",
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name="Enceladus"
                            )
                        ),
                    ),
                    types.SpeakerVoiceConfig(
                        speaker="Speaker 2",
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name="Aoede"
                            )
                        ),
                    ),
                ]
            ),
        ),
    )

    file_index = 0
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if (
            chunk.candidates is None
            or chunk.candidates[0].content is None
            or chunk.candidates[0].content.parts is None
        ):
            continue
        if chunk.candidates[0].content.parts[0].inline_data and chunk.candidates[0].content.parts[0].inline_data.data:
            file_name = f"ENTER_FILE_NAME_{file_index}"
            file_index += 1
            inline_data = chunk.candidates[0].content.parts[0].inline_data
            data_buffer = inline_data.data
            file_extension = mimetypes.guess_extension(inline_data.mime_type)
            if file_extension is None:
                file_extension = ".wav"
                data_buffer = convert_to_wav(inline_data.data, inline_data.mime_type)
            save_binary_file(f"{file_name}{file_extension}", data_buffer)
        else:
            print(chunk.text)

def convert_to_wav(audio_data: bytes, mime_type: str) -> bytes:
    """Generates a WAV file header for the given audio data and parameters.

    Args:
        audio_data: The raw audio data as a bytes object.
        mime_type: Mime type of the audio data.

    Returns:
        A bytes object representing the WAV file header.
    """
    parameters = parse_audio_mime_type(mime_type)
    bits_per_sample = parameters["bits_per_sample"]
    sample_rate = parameters["rate"]
    num_channels = 1
    data_size = len(audio_data)
    bytes_per_sample = bits_per_sample // 8
    block_align = num_channels * bytes_per_sample
    byte_rate = sample_rate * block_align
    chunk_size = 36 + data_size  # 36 bytes for header fields before data chunk size

    # http://soundfile.sapp.org/doc/WaveFormat/

    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",          # ChunkID
        chunk_size,       # ChunkSize (total file size - 8 bytes)
        b"WAVE",          # Format
        b"fmt ",          # Subchunk1ID
        16,               # Subchunk1Size (16 for PCM)
        1,                # AudioFormat (1 for PCM)
        num_channels,     # NumChannels
        sample_rate,      # SampleRate
        byte_rate,        # ByteRate
        block_align,      # BlockAlign
        bits_per_sample,  # BitsPerSample
        b"data",          # Subchunk2ID
        data_size         # Subchunk2Size (size of audio data)
    )
    return header + audio_data

def parse_audio_mime_type(mime_type: str) -> dict[str, int | None]:
    """Parses bits per sample and rate from an audio MIME type string.

    Assumes bits per sample is encoded like "L16" and rate as "rate=xxxxx".

    Args:
        mime_type: The audio MIME type string (e.g., "audio/L16;rate=24000").

    Returns:
        A dictionary with "bits_per_sample" and "rate" keys. Values will be
        integers if found, otherwise None.
    """
    bits_per_sample = 16
    rate = 24000

    # Extract rate from parameters
    parts = mime_type.split(";")
    for param in parts: # Skip the main type part
        param = param.strip()
        if param.lower().startswith("rate="):
            try:
                rate_str = param.split("=", 1)[1]
                rate = int(rate_str)
            except (ValueError, IndexError):
                # Handle cases like "rate=" with no value or non-integer value
                pass # Keep rate as default
        elif param.startswith("audio/L"):
            try:
                bits_per_sample = int(param.split("L", 1)[1])
            except (ValueError, IndexError):
                pass # Keep bits_per_sample as default if conversion fails

    return {"bits_per_sample": bits_per_sample, "rate": rate}


if __name__ == "__main__":
    generate()
