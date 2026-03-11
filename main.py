import sys
from PyQt5.QtWidgets import QApplication
from file_encryption_tool import FileEncryptionTool

def main():
    app = QApplication(sys.argv)
    
    # Optional: Set application-wide font or style here
    
    window = FileEncryptionTool()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
