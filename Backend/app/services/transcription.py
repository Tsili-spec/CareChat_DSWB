import speech_recognition as sr

def transcribe_audio(audio_path: str, language: str = "en-US") -> str:
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
        # You can map language codes as needed
        text = recognizer.recognize_google(audio, language=language)
        return text
    except Exception:
        return ""
