from PyQt6.QtWidgets import *
import sys

def button_pressed():
    print("Button clicked")

app = QApplication(sys.argv)

window = QWidget()

layout = QVBoxLayout()

button = QPushButton("Click Me")

button.clicked.connect(button_pressed)

layout.addWidget(button)

window.setLayout(layout)

window.show()

app.exec()