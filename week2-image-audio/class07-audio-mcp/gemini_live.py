# Push-to-talk Gemini Live Audio Chat
# Install dependencies: pip install librosa soundfile sounddevice pynput pygame python-dotenv
import asyncio
import io
import os
from pathlib import Path
import wave
import threading
import queue
import time
import numpy as np
from google import genai
from google.genai import types
import soundfile as sf
import librosa
import sounddevice as sd
from pynput import keyboard
import pygame
from dotenv import load_dotenv

# Load environment variables from class1/.env
load_dotenv('../class1/.env')

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'), http_options={'api_version': 'v1alpha'})

# Native audio output model:
model = "gemini-2.5-flash-exp-native-audio-thinking-dialog"

config = {
  "response_modalities": ["AUDIO"],
  "system_instruction": "You are a helpful assistant and answer in a friendly tone. Keep responses concise and conversational.",
}

# Audio recording configuration
CHANNELS = 1
RATE = 16000
DTYPE = np.int16

# Global variables for recording control
is_recording = False
is_space_pressed = False
audio_queue = queue.Queue()
recording_frames = []

# Initialize pygame mixer for audio playback
pygame.mixer.init(frequency=24000, size=-16, channels=1, buffer=1024)

def on_key_press(key):
    """Handle key press events"""
    global is_space_pressed, is_recording, recording_frames
    if key == keyboard.Key.space and not is_space_pressed:
        is_space_pressed = True
        is_recording = True
        recording_frames = []  # Clear previous recording
        print("🎤 Recording started... (release space to stop)")

def on_key_release(key):
    """Handle key release events"""
    global is_space_pressed, is_recording, recording_frames
    if key == keyboard.Key.space and is_space_pressed:
        is_space_pressed = False
        is_recording = False
        frames_count = len(recording_frames)
        duration = frames_count / RATE if frames_count > 0 else 0
        print(f"⏹️  Recording stopped. Captured {frames_count} frames ({duration:.2f}s)")
    elif key == keyboard.Key.esc:
        print("Exiting...")
        return False

def record_audio():
    """Record audio from microphone in a separate thread"""
    global recording_frames, is_recording
    
    print("🎧 Audio system ready. Hold SPACE to record, ESC to quit.")
    
    def audio_callback(indata, frames, time, status):
        """Callback function for audio recording"""
        if status:
            print(f"⚠️  Audio status: {status}")
        if is_recording:
            # Check if we're getting audio data
            audio_level = np.max(np.abs(indata)) if len(indata) > 0 else 0
            if audio_level > 0.01:  # Only show if there's significant audio
                print(f"🎵 Audio level: {audio_level:.3f}")
            recording_frames.extend(indata.copy())
    
    try:
        with sd.InputStream(
            samplerate=RATE,
            channels=CHANNELS,
            dtype=DTYPE,
            callback=audio_callback,
            blocksize=1024
        ):
            while True:
                if not is_recording and recording_frames:
                    # Convert numpy array to bytes for compatibility
                    audio_data = np.array(recording_frames, dtype=DTYPE)
                    audio_queue.put(audio_data)
                    recording_frames = []
                
                time.sleep(0.01)
                
    except Exception as e:
        print(f"Recording error: {e}")

def play_audio_from_bytes(audio_data):
    """Play audio data using pygame"""
    try:
        # Create a temporary wave file in memory
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)
            wf.writeframes(audio_data)
        
        buffer.seek(0)
        pygame.mixer.music.load(buffer)
        pygame.mixer.music.play()
        
        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)
    except Exception as e:
        print(f"Playback error: {e}")

async def process_audio_with_gemini(audio_data):
    """Process recorded audio with Gemini and play response"""
    try:
        # Convert numpy array to proper format
        audio_float = audio_data.astype(np.float32) / 32768.0  # Convert to float32 range [-1, 1]
        
        # Use soundfile to convert to proper format
        audio_buffer = io.BytesIO()
        sf.write(audio_buffer, audio_float, RATE, format='RAW', subtype='PCM_16')
        audio_buffer.seek(0)
        processed_audio_bytes = audio_buffer.read()
        
        print(f"🤖 Sending to Gemini... (audio size: {len(processed_audio_bytes)} bytes)")
        
        # Send to Gemini and collect response with timeout
        try:
            async with client.aio.live.connect(model=model, config=config) as session:
                print("✅ Connected to Gemini Live")
                
                await asyncio.wait_for(
                    session.send_realtime_input(
                        audio=types.Blob(data=processed_audio_bytes, mime_type="audio/pcm;rate=16000")
                    ),
                    timeout=5.0
                )
                print("📤 Audio sent, waiting for response...")
                
                response_audio = b""
                response_count = 0
                start_time = time.time()
                
                async with asyncio.timeout(30.0):  # 15 second timeout for response
                    async for response in session.receive():
                        response_count += 1
                        elapsed = time.time() - start_time
                        print(f"📥 Response chunk {response_count} received ({elapsed:.1f}s)")
                        
                        if response.data is not None:
                            response_audio += response.data
                            print(f"🎵 Audio data: {len(response.data)} bytes")
                        
                        # Print response details for debugging
                        if hasattr(response, 'text') and response.text:
                            print(f"📝 Text: {response.text}")
                        if hasattr(response, 'error') and response.error:
                            print(f"❌ Error in response: {response.error}")
                            
                if response_audio:
                    print(f"🔊 Playing response... ({len(response_audio)} bytes)")
                    play_audio_from_bytes(response_audio)
                else:
                    print("⚠️  No audio response received.")
                    
        except asyncio.TimeoutError:
            print("⏰ Timeout: Gemini Live took too long to respond (>30s)")
        except ConnectionError as e:
            print(f"🔌 Connection error: {e}")
        except Exception as api_error:
            print(f"🚨 Gemini API error: {api_error}")
                
    except Exception as e:
        print(f"💥 Error processing audio: {type(e).__name__}: {e}")
        import traceback
        print(f"🔍 Full traceback: {traceback.format_exc()}")

async def main():
    """Main function that sets up push-to-talk recording"""
    print("🎙️  Push-to-Talk Gemini Live Audio Chat")
    print("=" * 40)
    print("Controls:")
    print("• Hold SPACE to record")
    print("• Release SPACE to send to Gemini")
    print("• Press ESC to quit")
    print("=" * 40)
    
    # Start keyboard listener
    listener = keyboard.Listener(
        on_press=on_key_press,
        on_release=on_key_release
    )
    listener.start()
    
    # Start audio recording in a separate thread
    recording_thread = threading.Thread(target=record_audio, daemon=True)
    recording_thread.start()
    
    try:
        # Main loop to process recorded audio
        while True:
            if not audio_queue.empty():
                audio_frames = audio_queue.get()
                await process_audio_with_gemini(audio_frames)
            
            await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    finally:
        listener.stop()

if __name__ == "__main__":
    asyncio.run(main())