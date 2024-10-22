# -*- coding: utf-8 -*-
"""
Módulo: MainWindow

Este módulo implementa a janela principal da aplicação Gysin IA, que oferece uma interface
de chat interativa com integração de IA, síntese de voz e detecção de palavra-chave.

Autor: Stefano Gysin - StefanoGysin@hotmail.com
Data: 20/10/2024 15:12 (horário de Zurique)
"""

# Importações necessárias
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLineEdit, QApplication, QLabel, QCheckBox
)
from PySide6.QtCore import Qt, Slot, QTimer, Signal
from PySide6.QtGui import QFont, QIcon, QTextCursor
from api.openai_client import OpenAIClient
from dotenv import load_dotenv
from api.openai_tts import text_to_speech
from api.openai_stt import transcribe_audio as openai_transcribe_audio
from utils.audio_utils import record_audio
from gui.language_utils import detect_language
from utils.audio_activation import detect_wake_word
import threading
import vlc
import os

# Carrega as variáveis de ambiente
load_dotenv()

class MainWindow(QMainWindow):
    """Classe principal que representa a janela da aplicação Gysin IA."""

    # Sinal para detecção de palavra-chave
    wake_word_detected = Signal()

    # Constantes para cores de fundo das mensagens
    BACKGROUND_USER = "#E6F3FF"
    BACKGROUND_AI = "#F0FFF0"
    BACKGROUND_SYSTEM = "#444444"
    FONT_SIZE = 12

    def __init__(self):
        """Inicializa a janela principal e configura a interface do usuário."""
        super().__init__()
        self.setWindowTitle("Gysin IA")
        self.setMinimumSize(1080, 720)
        self.setup_ui()
        self.openai_client = OpenAIClient()
        self.add_message("Sistema", "Bem-vindo ao Gysin IA! Como posso ajudar você hoje?", self.BACKGROUND_SYSTEM)
        self.initialize_wake_word_detection()

    # Configuração da Interface do Usuário
    def setup_ui(self):
        """Configura todos os elementos da interface do usuário."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.setup_chat_display(main_layout)
        self.setup_typing_label(main_layout)
        self.setup_audio_checkbox(main_layout)
        self.setup_input_area(main_layout)

        self.connect_signals()

    def setup_chat_display(self, layout):
        """Configura a área de exibição do chat."""
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Arial", self.FONT_SIZE))
        self.chat_display.setStyleSheet("background-color: #393737;")
        layout.addWidget(self.chat_display)

    def setup_typing_label(self, layout):
        """Configura o label que indica que a IA está digitando."""
        self.typing_label = QLabel("Gysin IA está digitando...")
        self.typing_label.hide()
        layout.addWidget(self.typing_label)

    def setup_audio_checkbox(self, layout):
        """Configura a checkbox para habilitar respostas por áudio."""
        self.audio_response_checkbox = QCheckBox("Habilitar respostas por áudio")
        self.audio_response_checkbox.setChecked(True)
        layout.addWidget(self.audio_response_checkbox)

    def setup_input_area(self, layout):
        """Configura a área de entrada de texto e botões."""
        input_layout = QVBoxLayout()

        self.user_input = QLineEdit()
        self.user_input.setFont(QFont("Arial", self.FONT_SIZE))
        self.user_input.setPlaceholderText("Digite sua mensagem aqui...")
        input_layout.addWidget(self.user_input)

        self.send_button = QPushButton("Enviar")
        icon_path = "resources/icons/cil-cursor.png"
        if os.path.exists(icon_path):
            self.send_button.setIcon(QIcon(icon_path))
        input_layout.addWidget(self.send_button)

        self.record_button = QPushButton("Gravar Áudio")
        input_layout.addWidget(self.record_button)

        layout.addLayout(input_layout)

    def connect_signals(self):
        """Conecta os sinais aos slots correspondentes."""
        self.send_button.clicked.connect(self.send_message)
        self.user_input.returnPressed.connect(self.send_message)
        self.record_button.clicked.connect(self.send_audio_message)

    # Detecção de Palavra-Chave
    # Detecção de Palavra-Chave
    def initialize_wake_word_detection(self):
        """Inicializa a detecção da palavra-chave em uma thread separada."""
        self.wake_word_thread = threading.Thread(target=self.run_wake_word_detection, daemon=True)
        self.wake_word_thread.start()
        self.wake_word_detected.connect(self.on_wake_word_detected)

    def run_wake_word_detection(self):
        """Executa a detecção de palavra-chave continuamente."""
        while True:
            if detect_wake_word():
                self.wake_word_detected.emit()

    @Slot()
    def on_wake_word_detected(self):
        """Manipula a detecção da palavra-chave."""
        self.play_activation_sound()
        QTimer.singleShot(500, self.send_audio_message)

    # Funcionalidades de Áudio
    def play_activation_sound(self):
        """Reproduz um som de ativação pré-gravado com volume ajustado para 10%."""
        audio_file = "resources/audios/activation_sound.mp3"
        if os.path.exists(audio_file):
            player = vlc.MediaPlayer(audio_file)
            
            # Ajusta o volume para 10%
            player.audio_set_volume(80)
            
            player.play()
            print("Áudio de ativação reproduzido com volume ajustado para 50%.")
        else:
            print("Arquivo de áudio de ativação não encontrado.")

    @Slot()
    def send_audio_message(self):
        """Grava e envia uma mensagem de áudio do usuário."""
        try:
            audio_filename = "user_audio.wav"
            record_audio(audio_filename)
            
            last_message = self.chat_display.toPlainText().split('\n')[-1]
            detected_language = detect_language(last_message)
            language_code = self.get_language_code(detected_language)
            
            user_text = openai_transcribe_audio(audio_filename, language=language_code)
            if user_text:
                self.add_message("Você", user_text, self.BACKGROUND_USER)
                self.get_ai_response(user_text)
            else:
                raise ValueError("Transcrição vazia.")
        except Exception as e:
            self.add_message("Sistema", f"Erro durante a transcrição de áudio: {str(e)}", self.BACKGROUND_SYSTEM)

    # Processamento de Mensagens
    @Slot()
    def send_message(self):
        """Envia a mensagem do usuário e solicita resposta da IA."""
        user_text = self.user_input.text().strip()
        if not user_text:
            return

        self.add_message("Você", user_text, self.BACKGROUND_USER)
        self.user_input.clear()
        self.user_input.setEnabled(False)
        self.send_button.setEnabled(False)
        self.typing_label.show()
        QApplication.setOverrideCursor(Qt.WaitCursor)

        QTimer.singleShot(100, lambda: self.get_ai_response(user_text))

    def get_ai_response(self, user_text):
        """Obtém a resposta da IA e a exibe."""
        try:
            response = self.openai_client.get_response(user_text)
            self.add_message("Gysin IA", response, self.BACKGROUND_AI)
            
            detected_language = detect_language(response)
            language_code = self.get_language_code(detected_language)
            
            if self.audio_response_checkbox.isChecked():
                self.generate_and_play_audio(response, language_code)
                
        except Exception as e:
            self.add_message("Sistema", f"Erro: {str(e)}", self.BACKGROUND_SYSTEM)
        finally:
            self.reset_ui_state()

    # Utilitários
    def get_language_code(self, detected_language):
        """Mapeia o idioma detectado para o código de idioma correspondente no formato ISO-639-1."""
        language_map = {'pt': 'pt', 'en': 'en', 'de': 'de', 'es': 'es'}
        return language_map.get(detected_language, 'pt')

    def generate_and_play_audio(self, text, language_code):
        """Gera e reproduz o áudio da resposta."""
        audio_file = "response_audio.mp3"
        text_to_speech(text, audio_file, language_code=language_code)
        self.play_audio(audio_file)

    def reset_ui_state(self):
        """Reseta o estado da UI após processar a resposta."""
        self.user_input.setEnabled(True)
        self.send_button.setEnabled(True)
        self.typing_label.hide()
        QApplication.restoreOverrideCursor()

    def add_message(self, sender, message, background_color):
        """Adiciona uma mensagem à área de chat."""
        self.chat_display.append(f'<div style="background-color: {background_color}; padding: 5px; margin: 5px 0;">'
                                 f'<b>{sender}:</b> {message}</div>')
        self.chat_display.moveCursor(QTextCursor.End)
        self.chat_display.ensureCursorVisible()

    def closeEvent(self, event):
        """Manipula o evento de fechamento da janela."""
        event.accept()

    def play_audio(self, audio_file):
        """Reproduz um arquivo de áudio."""
        try:
            player = vlc.MediaPlayer(audio_file)
            player.play()
        except Exception as e:
            self.add_message("Erro", f"Erro ao reproduzir áudio: {str(e)}", self.BACKGROUND_SYSTEM)