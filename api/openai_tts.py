# utils/openai_tts.py

from pathlib import Path
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def text_to_speech(text, output_filename, language_code='pt'):
    """
    Converte texto em fala usando a API OpenAI TTS.

    :param text: Texto a ser convertido em fala.
    :param output_filename: Nome do arquivo de saída para salvar o áudio.
    :param language_code: Código do idioma no formato ISO-639-1 (padrão: 'pt').
    """
    voice_map = {
        'pt': 'onyx',  # Voz para português
        'en': 'onyx',  # Voz para inglês
        'de': 'onyx',  # Voz para alemão
        'es': 'onyx'   # Voz para espanhol
    }

    voice = voice_map.get(language_code, 'onyx')

    speech_file_path = Path(output_filename)
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text
    )

    response.stream_to_file(speech_file_path)
    print(f"Áudio salvo como {output_filename}")