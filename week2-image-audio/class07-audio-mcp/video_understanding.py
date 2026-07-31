# Video understanding with Gemini  (Week 2, Class 1 — slide 7: "Have it watch")
#
# Gemini can watch a clip and describe what happens — with timestamps. Great for
# auto-generating chapter markers or asking "at what point does X happen?"
# instead of scrubbing through the whole video yourself.
#
# Run it:  python video_understanding.py
# Point VIDEO_PATH at your own .mp4. Large files may take a moment to upload.

import time

from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

VIDEO_PATH = "clip.mp4"

clip = client.files.upload(file=VIDEO_PATH)

# Video files can take a few seconds to finish processing on Google's side.
# Wait until the uploaded file is ACTIVE before asking about it.
while clip.state.name == "PROCESSING":
    print("Processing video...")
    time.sleep(2)
    clip = client.files.get(name=clip.name)

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents=[
        "Summarize this with timestamps in MM:SS format.",
        clip,
    ],
)

print(response.text)

# GOOD TO KNOW
#   • Gemini samples video at ~1 frame/sec
#   • Ask for MM:SS timestamps to get exact moments
#   • Use one video per request for best results
#   • Fast action can lose detail — slower clips help
