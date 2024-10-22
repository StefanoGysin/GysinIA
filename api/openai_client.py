# -*- coding: utf-8 -*-
"""
Módulo: OpenAIClient

Este módulo implementa um cliente para interação com a API da OpenAI,
permitindo a geração de texto e imagens.

Autor: Stefano Gysin - StefanoGysin@hotmail.com
Data: 20/10/2024 15:12 (horário de Zurique)
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

class OpenAIClient:
    """
    Cliente para interação com a API da OpenAI.
    """

    def __init__(self):
        """
        Inicializa o cliente OpenAI.

        Raises:
            ValueError: Se a chave da API não for encontrada nas variáveis de ambiente.
        """
        # Obtém a chave da API das variáveis de ambiente
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("A chave da API OpenAI não foi encontrada nas variáveis de ambiente.")
        
        # Inicializa o cliente OpenAI
        self.client = OpenAI(api_key=self.api_key)

    def get_response(self, prompt, max_tokens=150):
        """
        Gera uma resposta a partir de um prompt usando a API da OpenAI.

        Args:
            prompt (str): O texto de entrada para o qual a resposta deve ser gerada.
            max_tokens (int, optional): Número máximo de tokens na resposta gerada. Padrão é 150.

        Returns:
            str: Texto gerado pela API da OpenAI ou mensagem de erro.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é uma assistente virtual chamada Gysin IA, desenvolvida para ser útil, criativa e amigável."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Erro ao gerar texto com a API OpenAI: {e}")
            return "Desculpe, ocorreu um erro ao processar sua solicitação."

    def generate_image(self, prompt):
        """
        Gera uma imagem a partir de um prompt dado usando a API da OpenAI.

        Args:
            prompt (str): Descrição da imagem a ser gerada.

        Returns:
            str: URL da imagem gerada ou None em caso de erro.
        """
        try:
            response = self.client.images.generate(
                prompt=prompt,
                n=1,
                size="1024x1024"
            )
            image_url = response.data[0].url
            return image_url
        except Exception as e:
            print(f"Erro ao gerar imagem com a API OpenAI: {e}")
            return None