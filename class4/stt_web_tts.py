
from google import genai
from google.genai import types
import wave
import os
import subprocess
import base64
import threading
import time
import signal
from pynput import keyboard
from dotenv import load_dotenv
load_dotenv()

# Set up the wave file to save the output:
def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
   with wave.open(filename, "wb") as wf:
      wf.setnchannels(channels)
      wf.setsampwidth(sample_width)
      wf.setframerate(rate)
      wf.writeframes(pcm)

def generate_gemini_response(prompt:str, model:str="gemini-2.5-flash-preview-tts"):

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

   file_name='out.wav'
   wave_file(file_name, data) # Saves the file to current directory
   
   # Play the audio through speakers using macOS built-in afplay
   subprocess.Popen(['afplay', file_name])

def speech_to_text_gemini(audio_file_path: str, model: str = "gemini-2.5-flash") -> str:
   """
   Convert audio file to text using Gemini 2.5 Flash
   
   Args:
       audio_file_path: Path to the audio file (supports wav, mp3, etc.)
       model: Gemini model to use for transcription
   
   Returns:
       Transcribed text as string
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

def record_audio_with_spacebar(output_file: str = "input.wav", sample_rate: int = 44100, channels: int = 1) -> str:
   """
   Record audio while spacebar is held down using macOS system tools
   
   Args:
       output_file: Path to save the recorded audio
       sample_rate: Audio sample rate in Hz
       channels: Number of audio channels (1 for mono, 2 for stereo)
   
   Returns:
       Path to the recorded audio file
   """
   print("Hold down the SPACEBAR to record. Release to stop recording.")
   print("Recording will start when you press spacebar...")
   
   # Recording state variables
   recording_process = None
   
   def start_recording():
       nonlocal recording_process
       if recording_process is None:
           print("🎤 Recording started...")
           
           # Remove existing file if it exists
           if os.path.exists(output_file):
               os.remove(output_file)
           
           # Use sox's rec command for recording
           try:
               recording_process = subprocess.Popen([
                   'rec',              # sox record command
                   '-r', str(sample_rate),  # sample rate
                   '-c', str(channels),     # channels  
                   output_file         # output file
               ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
               time.sleep(0.1)  # Give process time to start
               print("✅ Recording process started")
           except FileNotFoundError:
               print("❌ Sox not found. This should not happen since we just installed it.")
               return
   
   def stop_recording():
       nonlocal recording_process
       if recording_process:
           print("🛑 Recording stopped.")
           # Send SIGINT first (graceful termination)
           recording_process.send_signal(signal.SIGINT)
           time.sleep(0.5)  # Give time to finish writing
           
           # If still running, terminate forcefully
           if recording_process.poll() is None:
               recording_process.terminate()
               recording_process.wait()
           
           recording_process = None
           
           # Check if file was created and has content
           if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
               print(f"Audio saved to {output_file} ({os.path.getsize(output_file)} bytes)")
           else:
               print("⚠️ No audio was recorded or file is empty")
   
   def on_press(key):
       if key == keyboard.Key.space:
           start_recording()
   
   def on_release(key):
       if key == keyboard.Key.space:
           stop_recording()
           # Stop the listener by raising an exception
           raise keyboard.Listener.StopException
   
   # Set up keyboard listener
   try:
       with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
           listener.join()
   except keyboard.Listener.StopException:
       pass
   
   return output_file

# generate_gemini_response("Hi good afternoon Niral (pronounced as Knee-Ral), what did you want to search today?")