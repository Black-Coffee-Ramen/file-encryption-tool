import sys
import os
import json
import base64
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                             QWidget, QPushButton, QFileDialog, QFrame, 
                             QHBoxLayout, QProgressBar, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, pyqtProperty
from PyQt5.QtGui import QColor, QFont, QPalette, QLinearGradient, QBrush

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.fernet import Fernet

class ModernButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: 1px solid #3D3D3D;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #3D3D3D;
                border: 1px solid #505050;
            }
            QPushButton:pressed {
                background-color: #1E1E1E;
            }
            QPushButton:disabled {
                background-color: #1A1A1A;
                color: #555555;
            }
        """)

class GlassCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(45, 45, 45, 180);
                border: 1px solid rgba(255, 255, 255, 10);
                border-radius: 15px;
            }
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.setGraphicsEffect(shadow)

class FileEncryptionTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Matrix Vault")
        self.setFixedSize(500, 650)
        
        self.private_key_pem = None
        self.public_key_pem = None
        self.file_path = None
        
        self.init_ui()

    def init_ui(self):
        # Apply dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
            QLabel {
                color: #E0E0E0;
                font-family: 'Inter', sans-serif;
            }
        """)

        central_widget = QWidget()
        self.layout = QVBoxLayout(central_widget)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(20)

        # Header
        header_label = QLabel("Matrix Vault")
        header_label.setStyleSheet("font-size: 28px; font-weight: 800; color: #FFFFFF;")
        header_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(header_label)

        sub_header = QLabel("Secure Hybrid Encryption Tool")
        sub_header.setStyleSheet("font-size: 14px; color: #888888; margin-bottom: 20px;")
        sub_header.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(sub_header)

        # Main Card
        card = GlassCard()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(15)

        # Buttons
        self.gen_key_btn = ModernButton("Generate New Keys")
        self.gen_key_btn.clicked.connect(self.generate_keys)
        card_layout.addWidget(self.gen_key_btn)

        self.load_pub_btn = ModernButton("Load Public Key")
        self.load_pub_btn.clicked.connect(self.load_public_key)
        card_layout.addWidget(self.load_pub_btn)

        self.load_priv_btn = ModernButton("Load Private Key")
        self.load_priv_btn.clicked.connect(self.load_private_key)
        card_layout.addWidget(self.load_priv_btn)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #3D3D3D; height: 1px; margin: 10px 0;")
        card_layout.addWidget(line)

        self.select_file_btn = ModernButton("Select File to Process")
        self.select_file_btn.clicked.connect(self.select_file)
        card_layout.addWidget(self.select_file_btn)

        self.encrypt_btn = ModernButton("Encrypt File")
        self.encrypt_btn.setStyleSheet(self.gen_key_btn.styleSheet().replace("#2D2D2D", "#1A5F7A"))
        self.encrypt_btn.clicked.connect(self.encrypt_file)
        card_layout.addWidget(self.encrypt_btn)

        self.decrypt_btn = ModernButton("Decrypt File")
        self.decrypt_btn.setStyleSheet(self.gen_key_btn.styleSheet().replace("#2D2D2D", "#7A2D1A"))
        self.decrypt_btn.clicked.connect(self.decrypt_file)
        card_layout.addWidget(self.decrypt_btn)

        self.layout.addWidget(card)

        # Status Section
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #00FF9C; font-size: 12px; font-weight: 600;")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.status_label)

        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("color: #666666; font-size: 11px;")
        self.file_label.setAlignment(Qt.AlignCenter)
        self.file_label.setWordWrap(True)
        self.layout.addWidget(self.file_label)

        self.setCentralWidget(central_widget)

    def update_status(self, text, type="normal"):
        color = "#00FF9C" if type == "success" else "#FF4B4B" if type == "error" else "#888888"
        self.status_label.setText(text.upper())
        self.status_label.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: 600;")

    def generate_keys(self):
        try:
            private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
            self.private_key_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            public_key = private_key.public_key()
            self.public_key_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )

            folder = QFileDialog.getExistingDirectory(self, "Select Folder to Save Keys")
            if folder:
                with open(os.path.join(folder, "private_key.pem"), "wb") as f:
                    f.write(self.private_key_pem)
                with open(os.path.join(folder, "public_key.pem"), "wb") as f:
                    f.write(self.public_key_pem)
                self.update_status("Keys generated and saved", "success")
            else:
                self.update_status("Key generation cancelled")
        except Exception as e:
            self.update_status(f"Key generation failed: {str(e)}", "error")

    def load_public_key(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Public Key", "", "PEM Files (*.pem)")
        if path:
            with open(path, "rb") as f:
                self.public_key_pem = f.read()
            self.update_status("Public key loaded", "success")

    def load_private_key(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Private Key", "", "PEM Files (*.pem)")
        if path:
            with open(path, "rb") as f:
                self.private_key_pem = f.read()
            self.update_status("Private key loaded", "success")

    def select_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select File to Process")
        if path:
            self.file_path = path
            self.file_label.setText(os.path.basename(path))
            self.update_status("File selected")

    def encrypt_file(self):
        if not self.file_path or not self.public_key_pem:
            self.update_status("Selection missing", "error")
            return

        try:
            # 1. Generate AES session key
            aes_key = Fernet.generate_key()
            fernet = Fernet(aes_key)

            # 2. Encrypt file with AES
            with open(self.file_path, "rb") as f:
                plaintext = f.read()
            encrypted_data = fernet.encrypt(plaintext)

            # 3. Encrypt AES key with RSA public key
            public_key = serialization.load_pem_public_key(self.public_key_pem)
            encrypted_aes_key = public_key.encrypt(
                aes_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            # 4. Save combined data
            output_path, _ = QFileDialog.getSaveFileName(self, "Save Encrypted File", self.file_path + ".vault")
            if output_path:
                payload = {
                    "key": base64.b64encode(encrypted_aes_key).decode('utf-8'),
                    "data": base64.b64encode(encrypted_data).decode('utf-8')
                }
                with open(output_path, "w") as f:
                    json.dump(payload, f)
                self.update_status("Encryption successful", "success")
        except Exception as e:
            self.update_status(f"Encryption failed: {str(e)}", "error")

    def decrypt_file(self):
        if not self.file_path or not self.private_key_pem:
            self.update_status("Selection missing", "error")
            return

        try:
            # 1. Load payload
            with open(self.file_path, "r") as f:
                payload = json.load(f)
            
            encrypted_aes_key = base64.b64decode(payload["key"])
            encrypted_data = base64.b64decode(payload["data"])

            # 2. Decrypt AES key with RSA private key
            private_key = serialization.load_pem_private_key(self.private_key_pem, password=None)
            aes_key = private_key.decrypt(
                encrypted_aes_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            # 3. Decrypt data with AES
            fernet = Fernet(aes_key)
            decrypted_data = fernet.decrypt(encrypted_data)

            # 4. Save decrypted file
            default_name = self.file_path.replace(".vault", "")
            output_path, _ = QFileDialog.getSaveFileName(self, "Save Decrypted File", default_name)
            if output_path:
                with open(output_path, "wb") as f:
                    f.write(decrypted_data)
                self.update_status("Decryption successful", "success")
        except Exception as e:
            self.update_status(f"Decryption failed: {str(e)}", "error")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FileEncryptionTool()
    window.show()
    sys.exit(app.exec_())
