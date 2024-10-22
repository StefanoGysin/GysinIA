# -*- coding: utf-8 -*-
"""
Módulo: openai_audio_activation

Este módulo implementa a funcionalidade de detecção de palavra-chave usando a API da OpenAI.
Ele grava áudio continuamente e verifica se a palavra-chave foi dita.

Autor: Stefano Gysin - StefanoGysin@hotmail.com
Data: 20/10/2024 15:12 (horário de Zurique)
"""

import os
import pyaudio
import wave
import tempfile
from openai import OpenAI
import logging
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração global de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Inicializa o cliente OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Configurações de áudio
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 3
WAKE_WORD = "bom dia"

def record_audio():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    logging.info("Gravando áudio...")
    frames = []

    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    logging.info("Gravação finalizada.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    return frames

def save_audio(frames):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
        wf = wave.open(temp_audio.name, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        return temp_audio.name

def transcribe_audio(audio_file):
    with open(audio_file, "rb") as file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=file,
            language="pt"
        )
    return transcript.text.lower()

def detect_wake_word():
    try:
        while True:
            frames = record_audio()
            audio_file = save_audio(frames)
            
            transcription = transcribe_audio(audio_file)
            logging.info(f"Transcrição: {transcription}")

            if WAKE_WORD in transcription:
                logging.info("Palavra-chave detectada!")
                os.remove(audio_file)
                return True

            os.remove(audio_file)

    except Exception as e:
        logging.error(f"Ocorreu um erro: {e}")
        return False

if __name__ == "__main__":
    detect_wake_word()