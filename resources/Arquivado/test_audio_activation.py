# tests/test_audio_activation.py

import unittest
from utils.audio_activation import detect_wake_word

class TestAudioActivation(unittest.TestCase):
    def test_wake_word_detection(self):
        # Este teste requer interação manual
        print("Diga 'Jarvis' para ativar o assistente.")
        result = detect_wake_word()
        self.assertTrue(result, "A palavra-chave não foi detectada.")

if __name__ == '__main__':
    unittest.main()