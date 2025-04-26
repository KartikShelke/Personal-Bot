import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, ClientSettings
import speech_recognition as sr
import queue
import av
import numpy as np
import time
import datetime
import google.generativeai as genai

# Configure Gemini API key
API_KEY = "AIzaSyCKdsk-0yZG9FSzyj51sq6ZzVLlOhOO95o"  # Replace with your own
genai.configure(api_key=API_KEY)

# Streamlit UI
st.title("🎙️ Voice Assistant (WebRTC)")
st.write("Speak into your mic. The assistant will listen and respond using Gemini AI.")

# Audio queue for streaming
audio_queue = queue.Queue()

# Custom audio processor
class AudioProcessor:
    def recv(self, frame: av.AudioFrame):
        audio = frame.to_ndarray()
        audio_queue.put(audio)
        return frame

# Function to recognize speech from the audio queue
def recognize_from_queue():
    recognizer = sr.Recognizer()

    audio_data = []
    start_time = time.time()

    # Collect audio for 5 seconds
    while time.time() - start_time < 5:
        try:
            frame = audio_queue.get(timeout=1)
            audio_data.append(frame)
        except queue.Empty:
            break

    if not audio_data:
        return None

    # Convert to flat audio buffer
    audio_data = np.concatenate(audio_data, axis=1).flatten()

    # Create AudioData object
    audio = sr.AudioData(audio_data.tobytes(), 48000, 2)

    try:
        text = recognizer.recognize_google(audio)
        return text.lower()
    except sr.UnknownValueError:
        return "Sorry, I didn't catch that."
    except sr.RequestError:
        return "Speech service unavailable."

# Generate Gemini response
def generate_response(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception:
        return "Sorry, I couldn't generate a response."

# Start WebRTC
webrtc_ctx = webrtc_streamer(
    key="speech",
    mode=WebRtcMode.SENDONLY,
    in_audio_enabled=True,
    client_settings=ClientSettings(
        media_stream_constraints={"audio": True, "video": False},
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    ),
    audio_processor_factory=AudioProcessor,
)

# Run assistant loop
if webrtc_ctx.state.playing:
    st.info("Listening... Speak now!")

    if st.button("🗣️ Process Speech"):
        user_input = recognize_from_queue()
        if user_input:
            st.markdown(f"**You said:** {user_input}")
            if "exit" in user_input or "goodbye" in user_input:
                st.success("Goodbye! Have a great day.")
            elif "time" in user_input:
                now = datetime.datetime.now().strftime("%H:%M")
                st.markdown(f"🕒 Current time: **{now}**")
            else:
                ai_reply = generate_response(user_input)
                st.markdown(f"**AI says:** {ai_reply}")
