# api/openai_stt.py

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def transcribe_audio(audio_file_path, language='pt'):
    """
    Transcreve um arquivo de áudio usando a API Whisper da OpenAI.

    :param audio_file_path: Caminho para o arquivo de áudio a ser transcrito.
    :param language: Código do idioma no formato ISO-639-1 (padrão: 'pt').
    :return: Texto transcrito.
    """
    try:
        with open(audio_file_path, 'rb') as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language
            )
        return transcript.text
    except Exception as e:
        print(f"Erro na transcrição: {e}")
        return ""