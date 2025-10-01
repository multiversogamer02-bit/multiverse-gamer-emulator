# ui/community_window.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QLineEdit, QPushButton

class CommunityWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Amigos en línea")
        layout = QVBoxLayout(self)
        
        self.friends_list = QListWidget()
        layout.addWidget(self.friends_list)
        
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Escribe un mensaje...")
        layout.addWidget(self.chat_input)
        
        invite_btn = QPushButton("Invitar a jugar")
        invite_btn.clicked.connect(self.send_invite)
        layout.addWidget(invite_btn)