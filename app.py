import streamlit as st
import os
import time
import datetime
import speech_recognition as sr
import google.generativeai as genai

# Configure Gemini API key
API_KEY = "AIzaSyCKdsk-0yZG9FSzyj51sq6ZzVLlOhOO95o"  # <- Make sure to keep it secret in production!
genai.configure(api_key=API_KEY)

# Voice configuration
voice_language = "en"  # Language code: 'en' for English, 'hi' for Hindi, etc.
voice_gender = "f"     # 'm' for male, 'f' for female

# Streamlit App
st.title("🎙️ Personal Voice Assistant")
st.write("Your personal AI assistant is ready! Click the button below to start listening.")

# Voice Functions
def speak(text):
    """Converts text to speech using eSpeak."""
    st.text(f"🧠 AI: {text}")  # Display text on Streamlit
    os.system(f'espeak -v {voice_language}+{voice_gender} -p 50 -s 120 "{text}"')

def listen():
    """Listens for user input and returns recognized text."""
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            st.text("🎤 Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            st.text("🎧 Processing audio...")
            text = recognizer.recognize_google(audio)
            return text.lower()

    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that.")
        return None
    except sr.RequestError:
        speak("Speech service unavailable.")
        return None
    except sr.WaitTimeoutError:
        speak("You didn't say anything.")
        return None
    except Exception as e:
        speak(f"Microphone error: {str(e)}")
        return None

def generate_response(prompt):
    """Uses Gemini AI to generate a smart response."""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception:
        speak("There was an error generating the response.")
        return None

# Main app logic
if st.button("🎤 Start Listening"):
    while True:
        user_input = listen()
        if user_input:
            if "exit" in user_input or "goodbye" in user_input:
                speak("Goodbye! Have a great day.")
                break
            elif "what time is it" in user_input:
                current_time = datetime.datetime.now().strftime("%H:%M")
                speak(f"The time is {current_time}.")
            else:
                response = generate_response(user_input)
                if response:
                    speak(response)
            time.sleep(10)  # Pause before next listen
