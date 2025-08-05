from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from titlebar import TitleBar
from PyQt5.QtCore import QTimer
import requests

class DMWindow(QWidget):
    def __init__(self, token):
        super().__init__()
        self.token = token
        self.user_id = None
        self.channel_id = None

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(500, 600)
        self.setWindowIcon(QIcon("anyom.png"))
        self.setStyleSheet("""
            QWidget {
                background-color: #F4F4F7;
                font-family: 'Plus Jakarta Sans';
                font-size: 14px;
                color: #333;
                border-radius: 12px;
            }
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #CCC;
                border-radius: 8px;
                padding: 8px;
            }
            QTextEdit {
                background-color: #FFFFFF;
                border: 1px solid #CCC;
                border-radius: 8px;
                padding: 8px;
            }
            QPushButton {
                background-color: #5865F2;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4752C4;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.title_bar = TitleBar(self)
        layout.addWidget(self.title_bar)

        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(12)
        self.poll_timer = QTimer()
        self.poll_timer.setInterval(3000)  # 3 seconds
        self.poll_timer.timeout.connect(self.poll_messages)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Enter user ID")
        form_layout.addWidget(self.user_input)

        self.load_button = QPushButton("Load Conversation")
        self.load_button.clicked.connect(self.load_dm)
        form_layout.addWidget(self.load_button)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        form_layout.addWidget(self.chat_display)

        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_dm)
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)

        form_layout.addLayout(input_layout)
        layout.addLayout(form_layout)

    def discord_request(self, method, endpoint, **kwargs):
        headers = {
            "Authorization": f"Bot {self.token}",
            "Content-Type": "application/json"
        }
        url = f"https://discord.com/api/v10/{endpoint}"
        response = requests.request(method, url, headers=headers, **kwargs)
        if response.status_code >= 400:
            QMessageBox.critical(self, "Discord API Error", f"{response.status_code}: {response.text}")
        return response.json()

    def load_dm(self):
        self.user_id = self.user_input.text().strip()
        if not self.user_id:
            QMessageBox.warning(self, "Missing Info", "Enter a user ID.")
            return



        response = self.discord_request("POST", "users/@me/channels", json={"recipient_id": self.user_id})
        self.channel_id = response.get("id")
        if not self.channel_id:
            return

        # Load messages
        messages = self.discord_request("GET", f"channels/{self.channel_id}/messages", params={"limit": 20})
        styled = ""
        for msg in reversed(messages):
            author = msg["author"]["username"]
            content = msg["content"]
            styled += f"""
            <div style="margin-bottom:12px; padding-bottom:12px; border-bottom:1px solid #DDD;">
                <div style="font-weight:bold; color:#5865F2; margin-bottom:4px;">{author}</div>
                <div style="color:#333;">{content}</div>
            </div>
            """
        self.chat_display.setHtml(f"<div style='font-family: Plus Jakarta Sans; font-size:14px;'>{styled}</div>")
        self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())
        self.poll_timer.start()


    def send_dm(self):
        if not self.channel_id:
            QMessageBox.warning(self, "Missing Channel", "Load a conversation first.")
            return

        message = self.message_input.text().strip()
        if not message:
            return

        payload = {"content": message}
        self.discord_request("POST", f"channels/{self.channel_id}/messages", json=payload)
        self.message_input.clear()
        self.load_dm()

    def poll_messages(self):
        if not self.channel_id:
            return

        try:
            messages = self.discord_request("GET", f"channels/{self.channel_id}/messages", params={"limit": 20})
        except Exception:
            return  # Silently fail if Discord API is unreachable

        styled = ""
        for msg in reversed(messages):
            author = msg["author"]["username"]
            content = msg["content"]
            styled += f"""
            <div style="margin-bottom:12px; padding-bottom:12px; border-bottom:1px solid #DDD;">
                <div style="font-weight:bold; color:#5865F2; margin-bottom:4px;">{author}</div>
                <div style="color:#333;">{content}</div>
            </div>
            """
        self.chat_display.setHtml(f"<div style='font-family: Plus Jakarta Sans; font-size:14px;'>{styled}</div>")
        self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())

    def closeEvent(self, event):
        self.poll_timer.stop()
        event.accept()
