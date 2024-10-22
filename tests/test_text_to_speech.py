# tests/test_text_to_speech.py

import sys
import os
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.openai_tts import text_to_speech

class TestTextToSpeech(unittest.TestCase):

    def test_text_to_speech_multilingual(self):
        texts = {
            'pt-BR': "Olá, este é um teste em Português Brasileiro.",
            'en-US': "Hello, this is a test in English.",
            'de-DE': "Hallo, dies ist ein Test auf Deutsch.",
            'es-ES': "Hola, esta es una prueba en Español."
        }

        for lang_code, text in texts.items():
            output_file = f"test_audio_{lang_code}.mp3"
            text_to_speech(text, output_file, language_code=lang_code)
            self.assertTrue(os.path.exists(output_file), f"Arquivo de áudio não foi criado para {lang_code}")
            os.remove(output_file)  # Limpa o arquivo de teste após a verificação

if __name__ == '__main__':
    unittest.main()