import ok
from PyQt6.QtWidgets import *
import sys

dev = ok.okCFrontPanel()
dev.OpenBySerial("")
dev.ConfigureFPGA("Top.bit")

def led_on():
    dev.SetWireInValue(0x00, 0x0000)
    dev.UpdateWireIns()

def led_off():
    dev.SetWireInValue(0x00, 0x0001)
    dev.SetWireInValue(0x01, 0x0001)
    dev.UpdateWireIns()

app = QApplication(sys.argv)

window = QWidget()

layout = QVBoxLayout()

btn_on = QPushButton("LED ON")
btn_off = QPushButton("LED OFF")

btn_on.clicked.connect(led_on)
btn_off.clicked.connect(led_off)

layout.addWidget(btn_on)
layout.addWidget(btn_off)

window.setLayout(layout)

window.show()

app.exec()