# -*- coding: utf-8 -*-
"""
Módulo: audio_activation

Este módulo implementa a funcionalidade de detecção de palavra-chave usando a biblioteca Porcupine.
Ele configura e gerencia a entrada de áudio para detectar uma palavra-chave específica.

Autor: Stefano Gysin - StefanoGysin@hotmail.com
Data: 20/10/2024 15:12 (horário de Zurique)
"""

import pvporcupine
import pyaudio
import logging
import traceback
import numpy as np
import signal
import sys
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração global de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def initialize_audio(porcupine):
    # Função para inicializar o PyAudio e configurar o stream de áudio
    pa = pyaudio.PyAudio()
    if pa.get_device_count() == 0:
        raise RuntimeError("Nenhum dispositivo de entrada de áudio encontrado. Certifique-se de que um microfone está conectado.")
    
    default_device_index = pa.get_default_input_device_info().get("index", None)
    if default_device_index is None:
        raise RuntimeError("Não foi possível obter o dispositivo de entrada padrão.")
    
    logging.info(f"Usando dispositivo de entrada padrão: {default_device_index}")
    
    stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length,  # Use o frame_length do Porcupine
        input_device_index=default_device_index
    )
    return pa, stream

def cleanup_audio(pa, stream, porcupine):
    # Função para encerrar o stream de áudio e liberar recursos
    if stream is not None:
        stream.stop_stream()
        stream.close()
    if pa is not None:
        pa.terminate()
    if porcupine is not None:
        porcupine.delete()

def signal_handler(sig, frame):
    logging.info("Interrupção recebida, limpando recursos...")
    cleanup_audio(pa, stream, porcupine)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def detect_wake_word():
    global pa, stream, porcupine
    porcupine = None
    pa = None
    stream = None
    
    try:
        # Carrega a chave de acesso do Porcupine do arquivo .env
        access_key = os.getenv('PORCUPINE_ACCESS_KEY')
        if not access_key:
            raise ValueError("A chave de acesso Porcupine não foi encontrada nas variáveis de ambiente.")
        
        # Inicializa o Porcupine com a palavra-chave desejada
        porcupine = pvporcupine.create(access_key=access_key, keywords=["jarvis"])
        pa, stream = initialize_audio(porcupine)
        
        logging.info("Aguardando a palavra-chave...")

        while True:
            try:
                pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
                pcm = np.frombuffer(pcm, dtype=np.int16)
                result = porcupine.process(pcm)
                if result >= 0:
                    logging.info("Palavra-chave detectada!")
                    return True
            except IOError as e:
                logging.error(f"Erro de E/S durante leitura do áudio: {e}. Tentando continuar...")
                continue
    except RuntimeError as e:
        logging.error(f"Erro de dispositivo: {e}. Verifique se o microfone está conectado corretamente e se as permissões de microfone estão habilitadas.")
    except pvporcupine.PorcupineError as e:
        logging.error(f"Erro do Porcupine: {e}. Verifique a inicialização do Porcupine e se a palavra-chave está correta.")
    except Exception as e:
        logging.error(f"Ocorreu um erro inesperado: {e}. {traceback.format_exc()}")
    finally:
        cleanup_audio(pa, stream, porcupine)
    return False