# Image understanding with Gemini  (Week 2, Class 1 — slide 5: "Show it a picture")
#
# The idea: give Gemini *senses*. Same API you've used for text all course —
# we just add an image to the `contents` list and ask a question about it.
#
# Run it:  python image_understanding.py
# (Make sure you've copied .env.example -> .env and added your GEMINI_API_KEY.)

from google import genai
from dotenv import load_dotenv

load_dotenv()  # reads GEMINI_API_KEY from the .env in this folder

client = genai.Client()  # picks up GEMINI_API_KEY automatically

# Point this at any photo, screenshot, diagram, or handwriting sample.
IMAGE_PATH = "my_photo.jpg"

# Upload your image once. After this you can ask as many questions as you
# want about it in the same `contents` list — no need to re-upload.
photo = client.files.upload(file=IMAGE_PATH)

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents=["What's happening here? Describe it in detail.", photo],
)

print(response.text)

# ASK IT TO...
#   • Describe a photo in detail
#   • Read handwriting or a screenshot (OCR)
#   • Identify objects, or count them
#   • Explain a chart or diagram
#   • Compare two images side by side  ->  contents=[question, photo_a, photo_b]
