# Audio understanding with Gemini  (Week 2, Class 1 — slide 6: "Let it listen")
#
# Feed Gemini a voice memo (or any recording) and ask it to transcribe,
# summarize, or pull out action items. No separate transcription tool needed.
#
# Run it:  python audio_understanding.py
# This uses the sample recording in examples/input.wav so it works out of the box.
# Swap AUDIO_PATH for your own memo.mp3 / interview.wav to try your own audio.

from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

# examples/input.wav ships with this folder — replace with your own file anytime.
AUDIO_PATH = "examples/input.wav"

memo = client.files.upload(file=AUDIO_PATH)

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents=[
        "Transcribe this, then summarize it in 2 sentences.",
        memo,
    ],
)

print(response.text)

# ASK IT TO...
#   • Transcribe a recording word-for-word
#   • Summarize a long voice memo
#   • Pull out action items from a meeting
#   • Detect the tone or mood of a speaker
