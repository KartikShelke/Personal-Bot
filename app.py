import google.generativeai as genai
import os
import time
import datetime
import speech_recognition as sr

# Configure Gemini API key
API_KEY = "AIzaSyCKdsk-0yZG9FSzyj51sq6ZzVLlOhOO95o"
genai.configure(api_key=API_KEY)

# Configure medicine reminder time
medicine_time = "09:00"  # Time to remind for medicine (24-hour format)
story_time = "18:00"  # Time to remind for story (24-hour format)

# Voice configuration (change language and gender)
voice_language = "en"  # Options: 'en' for English, 'hn' for Hindi, 'es' for Spanish, etc.
voice_gender = "f"  # 'm' for male, 'f' for female


def speak(text):
    """Converts text to speech using eSpeak with adjusted pitch and speed."""
    print(f"AI: {text}")  # Debug print
    os.system(f'espeak -v {voice_language}+{voice_gender} -p 50 -s 120 "{text}"')


def listen():
    """Listens for user input and returns the recognized text."""
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("🎤 Listening...")  # Debug print
        recognizer.adjust_for_ambient_noise(source, duration=1)

        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            print("🎧 Processing audio...")  # Debug print
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
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


def generate_response(prompt):
    """Uses Gemini AI to generate responses like ChatGPT."""
    print(f"🔍 Generating AI response for: {prompt}")  # Debug print
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        response_lines = response.text.split('\n', 1)
        return response_lines[0] + "\n" + response_lines[1] if len(response_lines) > 1 else response_lines[0]
    except Exception as e:
        print(f"❌ Error: {e}")
        speak("There was an error generating the response.")
        return None


def get_time():
    """Returns the current time."""
    now = datetime.datetime.now()
    return now.strftime("%H:%M")


def remind_medicine():
    """Remind to take medicine."""
    current_time = get_time()
    if current_time == medicine_time:
        speak("Now it's time to take your medicine.")


def tell_story():
    """Tells grandpa to share a story."""
    current_time = get_time()
    if current_time == story_time:
        speak("Grandpa, tell me a story, I'm getting bored!")


def play_memory_game():
    """Tells grandpa to play a memory game."""
    speak("Grandpa, let's play a memory game together!")


if __name__ == "__main__":
    speak("Good morning!")  # Greet the user

    while True:
        remind_medicine()
        tell_story()

        user_input = listen()

        if user_input:
            if "exit" in user_input or "goodbye" in user_input:
                speak("Goodbye! Have a great day.")
                break
            elif "what time is it" in user_input:
                current_time = get_time()
                speak(f"The time is {current_time}.")
            elif "tell me a story" in user_input:
                tell_story()
            elif "play a memory game" in user_input:
                play_memory_game()
            else:
                response = generate_response(user_input)
                if response:
                    speak(response)

        time.sleep(10)
