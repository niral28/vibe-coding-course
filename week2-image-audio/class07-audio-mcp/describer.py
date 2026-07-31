# THE DESCRIBER  (Week 2, Class 1 — slide 8: "It's all the same code")
#
# The big realization: image, audio, and video understanding are the SAME code.
# Upload a file, ask a question, print the answer. Gemini figures out the file
# type on its own — you don't change anything.
#
# Run it:  python describer.py
# Try it on a photo, then a voice memo (examples/input.wav), then a video clip.
#
# Stretch (done below): it loops so you can analyze several files in a row.

from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()


def describe_file(file_path: str, question: str) -> str:
    """Upload any file (image / audio / video) and ask Gemini about it."""
    uploaded = client.files.upload(file=file_path)
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=[question, uploaded],
    )
    return response.text


def main():
    print("The Describer — analyze any image, audio, or video with Gemini.")
    print("Press Enter on an empty 'File to analyze' prompt to quit.\n")

    while True:
        file_path = input("File to analyze: ").strip()
        if not file_path:
            print("Goodbye!")
            break

        question = input("What do you want to know? ").strip()
        if not question:
            question = "Describe this in detail."

        try:
            print("\n" + describe_file(file_path, question) + "\n")
        except Exception as e:
            # VIBE CODING MOMENT: if you hit a file-size or format error, paste
            # it into Cursor's AI and ask what's wrong — big files sometimes need
            # a different upload method, which is a great thing to have AI explain.
            print(f"\n⚠️  Something went wrong: {e}\n")


if __name__ == "__main__":
    main()
