import sys, requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout,
    QTextEdit, QPushButton, QTreeWidget, QMessageBox, QDialog, QDialogButtonBox,
    QSpacerItem, QSizePolicy, QTreeWidgetItem
)
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import Qt
from titlebar import TitleBar 
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QGraphicsDropShadowEffect

class TokenDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(520, 250)
        self.setWindowIcon(QIcon("anyom.png"))
        self.setStyleSheet("""
            QDialog {
                background-color: #F4F4F7;
                font-family: 'Plus Jakarta Sans';
                border-radius: 12px;
            }
            QLabel {
                font-size: 15px;
                color: #333;
                padding-bottom: 6px;
            }
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #CCC;
                border-radius: 8px;
                padding: 10px;
                font-size: 15px;
            }
            QPushButton {
                background-color: #5865F2;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-size: 15px;
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
        form_layout.setContentsMargins(24, 24, 24, 24)
        form_layout.setSpacing(12)

        form_layout.addWidget(QLabel("Enter your Discord bot token"))
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Bot token")
        form_layout.addWidget(self.token_input)

        self.ok_button = QPushButton("Continue")
        self.ok_button.clicked.connect(self.accept)
        form_layout.addWidget(self.ok_button)

        layout.addLayout(form_layout)

    def get_token(self):
        return self.token_input.text().strip()


class Anyom(QWidget):
    def __init__(self, token):
        super().__init__()
        self.token = token
        self.channel_map = {} 

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setMinimumSize(800, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #F6F5F3;
                font-family: 'Plus Jakarta Sans';
                font-size: 14px;
                color: #333;
                border-radius: 12px;
            }
            QTreeWidget {
                background-color: #E3E1DF;
                border: none;
                padding: 8px;
                border-radius: 8px;
            }
            QTextEdit {
                background-color: #FFFFFF;
                border: 1px solid #CCC;
                border-radius: 8px;
                padding: 8px;
            }
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #CCC;
                border-radius: 8px;
                padding: 6px;
            }
            QPushButton {
                background-color: #AAB4F5;
                border: none;
                border-radius: 8px;
                padding: 6px 12px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8F9FEF;
            }
        """)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.title_bar = TitleBar(self)
        layout.addWidget(self.title_bar)

        content = QHBoxLayout()
        content.setContentsMargins(20, 20, 20, 20)
        content.setSpacing(20)

        self.guild_tree = QTreeWidget()
        self.guild_tree.setHeaderHidden(True)
        self.guild_tree.setFixedWidth(250)
        self.guild_tree.itemClicked.connect(self.on_channel_selected)
        content.addWidget(self.guild_tree)

        chat_layout = QVBoxLayout()
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        chat_layout.addWidget(self.chat_display)

        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)

        chat_layout.addLayout(input_layout)
        content.addLayout(chat_layout)

        layout.addLayout(content)

        self.load_guilds_and_channels()

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

    def load_guilds_and_channels(self):
        self.guild_tree.clear()
        self.channel_map.clear()

        guilds = self.discord_request("GET", "users/@me/guilds")
        for guild in guilds:
            guild_id = guild["id"]
            guild_name = guild["name"]
            guild_item = QTreeWidgetItem([guild_name])
            self.guild_tree.addTopLevelItem(guild_item)

            channels = self.discord_request("GET", f"guilds/{guild_id}/channels")
            for ch in channels:
                if ch["type"] == 0:
                    channel_name = ch["name"]
                    channel_id = ch["id"]
                    channel_item = QTreeWidgetItem([channel_name])
                    guild_item.addChild(channel_item)
                    self.channel_map[(guild_name, channel_name)] = channel_id

    def on_channel_selected(self, item, column):
        parent = item.parent()
        if not parent:
            return  

        guild_name = parent.text(0)
        channel_name = item.text(0)
        channel_id = self.channel_map.get((guild_name, channel_name))
        if not channel_id:
            return

        messages = self.discord_request("GET", f"channels/{channel_id}/messages", params={"limit": 20})
        self.chat_display.clear()

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
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )

        self.selected_channel_id = channel_id

    def send_message(self):
        message = self.message_input.text().strip()
        if not hasattr(self, "selected_channel_id") or not message:
            QMessageBox.warning(self, "Missing Info", "Select a channel and enter a message.")
            return

        payload = {"content": message}
        self.discord_request("POST", f"channels/{self.selected_channel_id}/messages", json=payload)
        self.message_input.clear()

        # Refresh messages
        for i in range(self.guild_tree.topLevelItemCount()):
            guild_item = self.guild_tree.topLevelItem(i)
            for j in range(guild_item.childCount()):
                channel_item = guild_item.child(j)
                if self.channel_map.get((guild_item.text(0), channel_item.text(0))) == self.selected_channel_id:
                    self.on_channel_selected(channel_item, 0)
                    return

if __name__ == "__main__":
    app = QApplication(sys.argv)

    dialog = TokenDialog()
    if dialog.exec_() == QDialog.Accepted:
        token = dialog.get_token()
        if token:
            window = Anyom(token) 
            window.show()
            sys.exit(app.exec_())
        else:
            QMessageBox.warning(None, "Missing Token", "Bot token is required.")
    else:
        sys.exit()
