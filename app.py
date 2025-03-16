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

# Configure Gemini API key
API_KEY = os.getenv("GENAI_API_KEY", "AIzaSyCKdsk-0yZG9FSzyj51sq6ZzVLlOhOO95o")  # Replace with your API key if not set
genai.configure(api_key=API_KEY)

# Configure medicine reminder time
medicine_time = "09:00"  # Time to remind for medicine (24-hour format)
story_time = "18:00"  # Time to remind for story (24-hour format)

# Initialize speech recognition and text-to-speech engine
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()
tts_engine.setProperty("rate", 150)  # Set speech rate
tts_engine.setProperty("volume", 1)  # Set volume

# Function to convert text to speech
def speak(text):
    """Converts text to speech."""
    st.write(f"**AI:** {text}")  # Display AI response
    tts_engine.say(text)  # Speak out loud
    tts_engine.runAndWait()

# Function to listen to user's voice input
def listen():
    """Listens to the user's voice and converts it to text."""
    with sr.Microphone() as source:
        st.write("🎤 Listening... Please speak.")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            user_input = recognizer.recognize_google(audio)  # Convert speech to text
            st.write(f"**You:** {user_input}")
            return user_input
        except sr.UnknownValueError:
            st.warning("Could not understand the audio. Please try again.")
            return None
        except sr.RequestError:
            st.error("Speech recognition service is unavailable.")
            return None

# AI response generation function
def generate_response(prompt):
    """Uses Gemini AI to generate responses."""
    st.write(f"🔍 Generating AI response for: {prompt}")
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        response_lines = response.text.split("\n", 1)
        return response_lines[0] + "\n" + response_lines[1] if len(response_lines) > 1 else response_lines[0]
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None

# Function to get the current time
def get_time():
    """Returns the current time."""
    return datetime.datetime.now().strftime("%H:%M")

# Reminder functions
def remind_medicine():
    """Remind to take medicine."""
    if get_time() == medicine_time:
        speak("Now it's time to take your medicine.")

def tell_story():
    """Tells grandpa to share a story."""
    if get_time() == story_time:
        speak("Grandpa, tell me a story, I'm getting bored!")

def play_memory_game():
    """Tells grandpa to play a memory game."""
    speak("Grandpa, let's play a memory game together!")

# Main function
def main():
    st.title("🗣️ Personal Assistant with Voice")

    # Medicine and Story Reminders
    remind_medicine()
    tell_story()

    # Voice or text input option
    st.subheader("Choose Input Mode:")
    input_mode = st.radio("Select input type:", ("🎤 Voice", "⌨️ Text"))

    if input_mode == "🎤 Voice":
        if st.button("Start Listening"):
            user_input = listen()  # Capture voice input
    else:
        user_input = st.text_input("You:", key="user_input")

    if user_input:
        if "exit" in user_input.lower() or "goodbye" in user_input.lower():
            speak("Goodbye! Have a great day.")
        elif "what time is it" in user_input.lower():
            current_time = get_time()
            speak(f"The time is {current_time}.")
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
