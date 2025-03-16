import streamlit as st
import os
import datetime
import google.generativeai as genai

# Configure Gemini API key
API_KEY = "AIzaSyCKdsk-0yZG9FSzyj51sq6ZzVLlOhOO95o"
import streamlit as st
import os
import datetime
import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
from streamlit_webrtc import webrtc_streamer
import numpy as np
import queue
import av

# ✅ Load API key securely
API_KEY = os.getenv("AIzaSyCKdsk-0yZG9FSzyj51sq6ZzVLlOhOO95o")  # Store this in Streamlit secrets or a .env file
if not API_KEY:
    st.error("API key is missing. Set 'GENAI_API_KEY' as an environment variable.")
    st.stop()

genai.configure(api_key=API_KEY)

# ✅ Configure reminders
MEDICINE_TIME = "09:00"
STORY_TIME = "18:00"

# ✅ Initialize TTS and Speech Recognition
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()
tts_engine.setProperty("rate", 150)
tts_engine.setProperty("volume", 1)

# ✅ Queue for WebRTC audio processing
audio_queue = queue.Queue()

# 🔹 Function: Convert Text to Speech
def speak(text):
    """Converts text to speech and displays it."""
    st.write(f"**AI:** {text}")
    tts_engine.say(text)
    tts_engine.runAndWait()

# 🔹 Function: Listen via WebRTC Microphone
def audio_callback(frame: av.AudioFrame):
    """Receives audio from the user's microphone."""
    audio = np.frombuffer(frame.to_ndarray(), np.int16)
    audio_queue.put(audio)

# 🔹 Function: Recognize Speech from Audio
def recognize_audio():
    """Processes live audio from queue and converts to text."""
    while not audio_queue.empty():
        audio_data = audio_queue.get()
        try:
            audio = sr.AudioData(audio_data.tobytes(), 16000, 2)
            text = recognizer.recognize_google(audio)
            st.write(f"**You:** {text}")
            return text
        except sr.UnknownValueError:
            st.warning("Could not understand audio. Try again.")
        except sr.RequestError:
            st.error("Speech recognition service unavailable.")
    return None

# 🔹 Function: Get AI Response
def generate_response(prompt):
    """Generates AI response using Gemini API."""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text if response else "I'm not sure how to respond."
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# 🔹 Function: Get Current Time
def get_time():
    return datetime.datetime.now().strftime("%H:%M")

# 🔹 Function: Medicine Reminder
def remind_medicine():
    if get_time() == MEDICINE_TIME:
        speak("Now it's time to take your medicine.")

# 🔹 Function: Story Reminder
def tell_story():
    if get_time() == STORY_TIME:
        speak("Grandpa, tell me a story, I'm getting bored!")

# 🔹 Function: Memory Game Prompt
def play_memory_game():
    speak("Grandpa, let's play a memory game together!")

# 🔹 Main App Logic
def main():
    st.title("🗣️ AI Voice Assistant")

    # ✅ Medicine and Story Reminders
    remind_medicine()
    tell_story()

    # ✅ Voice or Text Input
    st.subheader("Choose Input Mode:")
    input_mode = st.radio("Select input type:", ("🎤 Voice", "⌨️ Text"))

    user_input = None
    if input_mode == "🎤 Voice":
        webrtc_ctx = webrtc_streamer(key="speech", audio_receiver_size=1024, audio_processor_factory=audio_callback)
        if webrtc_ctx and webrtc_ctx.state.playing:
            user_input = recognize_audio()
    else:
        user_input = st.text_input("You:", key="user_input")

    if user_input:
        if "exit" in user_input.lower() or "goodbye" in user_input.lower():
            speak("Goodbye! Have a great day.")
        elif "what time is it" in user_input.lower():
            speak(f"The time is {get_time()}.")
        elif "tell me a story" in user_input.lower():
            tell_story()
        elif "play a memory game" in user_input.lower():
            play_memory_game()
        else:
            response = generate_response(user_input)
            if response:
                speak(response)

if __name__ == "__main__":
    main()
