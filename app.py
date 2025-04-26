import streamlit as st
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
from gtts import gTTS
import os
import base64
import tempfile
import google.generativeai as genai

# Directly add the API key here
GEMINI_API_KEY = "your-api-key-here"  # Replace with your actual API key

genai.configure(api_key=GEMINI_API_KEY)

def main():
    st.title("🎤 :blue[English Voice Chatbot] 💬🤖")
    st.subheader('Record your voice and get a response from the "AI Voice Bot"', divider='rainbow')

    st.sidebar.header("About English Voice Chatbot", divider='rainbow')
    st.sidebar.write(f'''This is an English voice chatbot created using Streamlit. It takes in English voice input and responds in English voice''')
    
    st.sidebar.info(f'''Development process includes these steps.  
    1️⃣ Convert Voice into text, using Google's speech recognition API.  
    2️⃣ Give text to LLM (I used Gemini), and generate a response.
    3️⃣ Convert LLM-generated text into speech by using Google TTS API.  
    And boom, 🚀 ''')

    st.sidebar.write("")  # Adds one line of space
    st.sidebar.write("")  # Adds one line of space
    st.sidebar.write("")  # Adds one line of space
    st.sidebar.write("")  # Adds one line of space

    st.sidebar.write("Developed by [Mubeen F.] (https://mubeenf.com)")

    english_recorder = audio_recorder(text='Speak', icon_size="2x", icon_name="microphone-lines", key="english_recorder")

    if english_recorder is not None:
        with st.container():
            col1, col2 = st.columns(2)

            with col2:
                # Display the audio file
                st.header('🧑')
                st.audio(english_recorder)

                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_english_recording:
                    temp_english_recording.write(english_recorder)
                    temp_english_recording_path = temp_english_recording.name

                # Convert audio file to text
                text = audio_to_text(temp_english_recording_path)
                st.success(text)

                # Remove the temporary file
                os.remove(temp_english_recording_path)

        response_text = llmModelResponse(text)

        with st.container():
            col1, col2 = st.columns(2)

            with col1:
                # Convert the response text to speech
                response_audio_html = response_to_audio(response_text)

                st.header('🤖')
                st.markdown(response_audio_html, unsafe_allow_html=True)

                st.info(response_text)


def audio_to_text(temp_english_recording_path):
    # Speech Recognition
    recognizer = sr.Recognizer()
    with sr.AudioFile(temp_english_recording_path) as source:
        english_recoded_voice = recognizer.record(source)
        try:
            text = recognizer.recognize_google(english_recoded_voice, language="en")
            return text
        except sr.UnknownValueError:
            return "I couldn't understand your voice"
        except sr.RequestError:
            return "Sorry, my speech service is down"

def response_to_audio(text, lang='en'):
    tts = gTTS(text=text, lang=lang)
    tts_audio_path = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False).name
    tts.save(tts_audio_path)

    # Get the base64 string of the audio file
    audio_base64 = get_audio_base64(tts_audio_path)

    # Autoplay audio using HTML and JavaScript
    audio_html = f"""
    <audio controls autoplay>
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        Your browser does not support the audio element.
    </audio>
    """
    return audio_html

# Function to encode the audio file to base64
def get_audio_base64(file_path):
    with open(file_path, "rb") as audio_file:
        audio_bytes = audio_file.read()
    return base64.b64encode(audio_bytes).decode()

def llmModelResponse(text):
    prompt = f"""Kindly answer this question in English language. 
    Don't use any other language or characters from other languages.
    Keep your answer short and relevant. 
    If you don't understand the question or don't know the answer, 
    Respond with 'I did not get what you speak, please try again' in English.
    Question: {text}"""

    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )

    chat_session = model.start_chat()
    response = chat_session.send_message(prompt)

    return response.text


if __name__ == "__main__":
    main()
