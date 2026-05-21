from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout
)

import sys

app = QApplication(sys.argv)

window = QWidget()

layout = QVBoxLayout()

button = QPushButton("Turn LED ON")

layout.addWidget(button)

window.setLayout(layout)

window.show()

app.exec()