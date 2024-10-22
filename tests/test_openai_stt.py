# tests/test_openai_STT.py

import unittest
import os
from api.openai_stt import transcribe_audio

class TestOpenAISTT(unittest.TestCase):
    def test_transcribe_audio(self):
        # Caminho para um arquivo de áudio de teste
        test_audio_path = "resources/audios/test_audio.wav"
        
        # Verifique se o arquivo de teste existe
        self.assertTrue(os.path.exists(test_audio_path), "Arquivo de áudio de teste não encontrado")
        
        # Teste a transcrição
        transcription = transcribe_audio(test_audio_path)
        
        # Verifique se a transcrição não está vazia
        self.assertTrue(transcription, "A transcrição não deve estar vazia")
        
        # Teste com diferentes idiomas
        languages = ['en', 'de', 'es', 'pt']
        for lang in languages:
            transcription = transcribe_audio(test_audio_path, language=lang)
            self.assertTrue(transcription, f"A transcrição para {lang} não deve estar vazia")

if __name__ == '__main__':
    unittest.main()