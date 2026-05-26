from gtts import gTTS
import os


def text_to_speech(text, output_path="response.mp3"):

    tts = gTTS(text=text)

    tts.save(output_path)

    return output_path