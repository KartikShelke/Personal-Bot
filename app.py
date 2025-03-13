import streamlit as st
import os
import time
import datetime
import speech_recognition as sr

# Configure medicine reminder time
medicine_time = "09:00"  # Time to remind for medicine (24-hour format)
story_time = "18:00"  # Time to remind for story (24-hour format)

def speak(text):
    """Displays text in the Streamlit app."""
    st.write(f"*Assistant:* {text}")

def listen():
    """Simulates listening for user input."""
    user_input = st.text_input("You: ", "")
    return user_input.lower() if user_input else None

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

def main():
    st.title("Personal Assistant")
    st.write("Welcome to your personal assistant.")

    # Check for time-based reminders
    remind_medicine()
    tell_story()

    user_input = listen()

    if user_input:
        if "exit" in user_input or "goodbye" in user_input:
            speak("Goodbye! Have a great day.")
        elif "what time is it" in user_input:
            current_time = get_time()
            speak(f"The time is {current_time}.")
        elif "tell me a story" in user_input:
            tell_story()
        elif "play a memory game" in user_input:
            play_memory_game()
        else:
            speak("I'm sorry, I didn't understand that.")

if _name_ == "_main_":
    main()