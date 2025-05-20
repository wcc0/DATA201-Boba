import sys
from PyQt5.QtWidgets import QApplication
from boba_window import BobaWindow

app = QApplication(sys.argv)
window = BobaWindow()
app.exec_()