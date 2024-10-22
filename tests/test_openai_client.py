import unittest
from api.openai_client import OpenAIClient

class TestOpenAIClient(unittest.TestCase):
    
    def setUp(self):
        """Configuração do ambiente de teste."""
        self.client = OpenAIClient()

    def test_generate_text(self):
        """Teste para o método generate_text."""
        prompt = "Teste de integração API"
        response = self.client.generate_text(prompt, max_tokens=50)
        
        # Verifica se a resposta não é nula
        self.assertIsNotNone(response, "A resposta da geração de texto deve ser não nula")
        
        # Verifica se a resposta contém o tipo esperado de conteúdo
        self.assertTrue(isinstance(response, str) and len(response) > 0, "A resposta deve ser uma string não vazia")
        
        # Mensagem detalhada para sucesso
        print("Teste de geração de texto bem-sucedido: resposta não nula e válida.")

    def test_generate_text_empty_prompt(self):
        """Teste para verificar o comportamento com prompt vazio."""
        prompt = ""
        response = self.client.generate_text(prompt, max_tokens=50)
        self.assertIsNotNone(response, "Mesmo com prompt vazio, a resposta não deve ser nula")
        print("Teste com prompt vazio bem-sucedido.")

    def test_generate_text_large_tokens(self):
        """Teste para verificar o comportamento com um número alto de tokens."""
        prompt = "Teste de limite de tokens"
        response = self.client.generate_text(prompt, max_tokens=1000)
        self.assertIsNotNone(response, "A resposta não deve ser nula mesmo com muitos tokens")
        print("Teste com muitos tokens bem-sucedido.")

if __name__ == '__main__':
    unittest.main()