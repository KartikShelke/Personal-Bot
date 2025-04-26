import streamlit as st
import av
import numpy as np
import queue
import time
import datetime
import google.generativeai as genai
import os

from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, ClientSettings, WebRtcMode
import speech_recognition as sr

# Configure Gemini API key
API_KEY = "AIzaSyCKdsk-0yZG9FSzyj51sq6ZzVLlOhOO95o"
genai.configure(api_key=API_KEY)

# Voice configuration
voice_language = "en"  # Language code
voice_gender = "f"     # 'm' for male, 'f' for female

# Set up Streamlit app
st.title("🎙️ WebRTC Voice Assistant")
st.write("Talk to your personal AI assistant through your browser mic! 🎤")

# Queue to receive audio frames
audio_queue = queue.Queue()

# Custom Audio Processor
class AudioProcessor(AudioProcessorBase):
    def recv_audio(self, frame: av.AudioFrame) -> av.AudioFrame:
        audio_data = frame.to_ndarray()
        audio_queue.put(audio_data)
        return frame

# Function to recognize speech
def recognize_from_queue():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)

    audio_data = []
    start_time = time.time()

    # Collect audio frames for 5 seconds
    while time.time() - start_time < 5:
        try:
            frame = audio_queue.get(timeout=1)
            audio_data.append(frame)
        except queue.Empty:
            break

    if not audio_data:
        return None

    # Concatenate frames
    audio_data = np.concatenate(audio_data, axis=1).flatten()

    # Create AudioData object
    sample_rate = 48000  # default for WebRTC
    sample_width = 2     # 16 bits

    audio = sr.AudioData(audio_data.tobytes(), sample_rate, sample_width)

    try:
        text = recognizer.recognize_google(audio)
        return text.lower()
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        return None

# Function to speak
def speak(text):
    st.text(f"🧠 AI: {text}")  # Display text
    os.system(f'espeak -v {voice_language}+{voice_gender} -p 50 -s 120 "{text}"')

# Function to generate AI response
def generate_response(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception:
        return "Sorry, I couldn't generate a response."

# Start WebRTC microphone streamer
webrtc_ctx = webrtc_streamer(
    key="speech",
    mode=WebRtcMode.SENDONLY,  # <<< CORRECT WAY (use Enum)
    audio_receiver_size=256,
    client_settings=ClientSettings(
        media_stream_constraints={"audio": True, "video": False},
    ),
    audio_processor_factory=AudioProcessor,
)

# Start button
if st.button("🎤 Start Talking"):
    st.info("Speak something! Listening for 5 seconds...")

    user_input = recognize_from_queue()

    if user_input:
        st.success(f"✅ You said: {user_input}")

        if "exit" in user_input or "goodbye" in user_input:
            speak("Goodbye! Have a great day.")
        elif "what time is it" in user_input:
            current_time = datetime.datetime.now().strftime("%H:%M")
            speak(f"The time is {current_time}.")
        else:
            response = generate_response(user_input)
            if response:
                speak(response)
    else:
        st.warning("❌ Didn't catch that. Please try again.")
