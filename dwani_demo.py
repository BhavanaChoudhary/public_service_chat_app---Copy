import os
from dotenv import load_dotenv
import dwani

# Load credentials from .env file
load_dotenv()
dwani.api_key = os.getenv("DWANI_API_KEY")
dwani.api_base = os.getenv("DWANI_API_BASE_URL")

# === Features ===

def run_chat(prompt, src_lang="eng_Latn", tgt_lang="kan_Knda"):
    response = dwani.Chat.create(prompt=prompt, src_lang=src_lang, tgt_lang=tgt_lang)
    return response

def describe_image(file_path, query="Describe this image", src_lang="eng_Latn", tgt_lang="kan_Knda"):
    response = dwani.Vision.caption(file_path=file_path, query=query, src_lang=src_lang, tgt_lang=tgt_lang)
    return response

def transcribe_audio(file_path, language="kannada"):
    response = dwani.ASR.transcribe(file_path=file_path, language=language)
    return response

def text_to_speech(input_text, file_name="output.mp3"):
    try:
        response = dwani.Audio.speech(input=input_text, response_format="mp3")
        with open(file_name, "wb") as f:
            f.write(response)
        return file_name
    except Exception as e:
        print(f"Error in text_to_speech: {e}")
        raise

# === Example Usage ===

if __name__ == "__main__":
    # 💬 Chat
    # chat_result = run_chat("Hello! How are you?")
    # print("Chat Result:", chat_result)

    # 🖼️ Vision
    vision_result = describe_image("images.jpg", query="Describe this logo")
    print("Vision Result:", vision_result)

    # 🗣️ ASR
    # asr_result = transcribe_audio("kannada_sample.wav")
    # print("ASR Result:", asr_result)

    # 🔊 TTS
    # audio_file = text_to_speech("ಕರ್ನಾಟಕದ ರಾಜಧಾನಿ ಯಾವುದು")
    # print(f"TTS saved to {audio_file}")