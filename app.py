import streamlit as st
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
from gtts import gTTS
import os
import base64
import tempfile
import google.generativeai as genai

GEMINI_API_KEY = st.secrets['gemini']['GEMINI_API_KEY']

genai.configure(api_key=GEMINI_API_KEY)

def main():
    st.title("🎤 English Voice Chatbot 💬🤖")
    st.subheader('Record your voice and get a response from the "AI Voicebot"', divider='rainbow')

    st.sidebar.header("About English Voice Chatbot", divider='rainbow')
    st.sidebar.write('''This is an English voice chatbot created using Streamlit. It takes English voice input and responds in English voice.''')
    
    st.sidebar.info('''Development process includes these steps:  
    1️⃣ Convert voice into text using Google's Speech Recognition API.  
    2️⃣ Pass the text to an LLM (Gemini) to generate a response.  
    3️⃣ Convert the LLM-generated text into speech using Google TTS API.  
    And boom, 🚀 ''')
    
    st.sidebar.write("")
    st.sidebar.write("")
    st.sidebar.write("")
    st.sidebar.write("")

    st.sidebar.write("Developed by [Mubeen F.] (https://mubeenf.com)")

    english_recorder = audio_recorder(text='Speak', icon_size="2x", icon_name="microphone-lines", key="english_recorder")

    if english_recorder is not None:
        with st.container():
            col1, col2 = st.columns(2)

            with col2:
                st.header('🧑')
                st.audio(english_recorder)

                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_english_recording:
                    temp_english_recording.write(english_recorder)
                    temp_english_recording_path = temp_english_recording.name

                text = audio_to_text(temp_english_recording_path)
                st.success(text)

                os.remove(temp_english_recording_path)

        response_text = llm_model_response(text)

        with st.container():
            col1, col2 = st.columns(2)

            with col1:
                response_audio_html = text_to_audio(response_text)

                st.header('🤖')
                st.markdown(response_audio_html, unsafe_allow_html=True)

                st.info(response_text)

def audio_to_text(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        recorded_voice = recognizer.record(source)
        try:
            text = recognizer.recognize_google(recorded_voice, language="en")
            return text
        except sr.UnknownValueError:
            return "Could not understand your voice."
        except sr.RequestError:
            return "Sorry, the speech service is currently unavailable."

def text_to_audio(text, lang='en'):
    tts = gTTS(text=text, lang=lang)
    tts_audio_path = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False).name
    tts.save(tts_audio_path)

    audio_base64 = get_audio_base64(tts_audio_path)

    audio_html = f"""
    <audio controls autoplay>
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        Your browser does not support the audio element.
    </audio>
    """
    return audio_html

def get_audio_base64(file_path):
    with open(file_path, "rb") as audio_file:
        audio_bytes = audio_file.read()
    return base64.b64encode(audio_bytes).decode()

def llm_model_response(text):
    prompt = f"""Kindly answer this question in English language. 
    Do not use any words or characters from other languages.
    Use polite English phrases at the beginning and end of your answer related to the question. 
    Keep your answer short. 
    You can also ask a related question at the end.
    If you don't know the answer or don't understand the question, 
    Respond with 'I did not understand what you spoke, please try again' in English.
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
