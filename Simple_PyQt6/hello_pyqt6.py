from PyQt6.QtWidgets import QApplication, QWidget
import sys

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("My First GUI")
window.resize(400, 200)

window.show()

app.exec()