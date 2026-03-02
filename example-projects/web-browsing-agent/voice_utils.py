from google import genai
from google.genai import types
import wave
import os
import subprocess
import base64
from dotenv import load_dotenv

load_dotenv()

def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)

def generate_gemini_response(prompt: str, model: str = "gemini-2.5-flash-preview-tts"):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=f"You are answering user encyclopedia questions. In a youthful but news oriented voice, say: {prompt}",
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name='Kore',
                    )
                )
            ),
        )
    )

    data = response.candidates[0].content.parts[0].inline_data.data
    file_name = 'out.wav'
    wave_file(file_name, data)
    
    return file_name

def speech_to_text_gemini(audio_file_path: str, model: str = "gemini-2.5-flash") -> str:
    """
    Convert audio file to text using Gemini 2.5 Flash
    """
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    # Read the audio file
    with open(audio_file_path, "rb") as audio_file:
        audio_data = audio_file.read()
    
    # Create the request with audio data
    audio_b64 = base64.b64encode(audio_data).decode('utf-8')
    response = client.models.generate_content(
        model=model,
        contents=[
            {
                "parts": [
                    {"inline_data": {"mime_type": "audio/wav", "data": audio_b64}},
                    {"text": "Please transcribe this audio to text."}
                ]
            }
        ]
    )
    
    return response.text or ""