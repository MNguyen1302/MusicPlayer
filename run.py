from main import MusicPlayer
from PyQt5.QtWidgets import QApplication
import sys

app = QApplication(sys.argv) 

window = MusicPlayer()
sys.exit(app.exec())