import ok
from PyQt6.QtWidgets import *
import sys

devices = ok.FrontPanelDevices()
dev = devices.Open()

if dev is None:
    print("Failed to open device")
    exit()

print("Device opened")

# Configure FPGA
result = dev.ConfigureFPGA("Top.bit")


if result != ok.ErrorCode.NoError:
    print(f"FPGA configuration failed: {dev.GetErrorMessage(result)}")
    exit()

# Check FrontPanel support
if not dev.IsFrontPanelEnabled():
    print("FrontPanel support is not enabled")
    exit()

# Obtain FP6 Classic Data Port
dp = dev.GetFPGADataPortClassic()

def led_on():
    dp.SetWireInValue(0x00, 0x0000)
    dp.UpdateWireIns()

def led_off():
    dp.SetWireInValue(0x00, 0x0001)
    dp.SetWireInValue(0x01, 0x0001)
    dp.UpdateWireIns()

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