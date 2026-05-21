## This will be the script to create a simple python version of the official First demonstration exampole that
## can be found on FrontPanel SDK examples. The original example can be found here:
## https://docs.opalkelly.com/fpsdk/samples-and-tools/sample-first/
##
## Update: This example has been taken down by FrontPanel SDK.

## The design example has the following endpoints:
## WireIn 0x00: LED control (1 = ON, 0 = OFF), the total data is 32-bit wide, but only the LSB 8 bits are used.
## WireIn 0x01: Sum input A, only LSB 16 bits are used.
## WireIn 0x02: Sum input B, only LSB 16 bits are used.
## WireOut 0x20: Random number output, only 4 bits will be displayed on an LED.
## WireOut 0x21: Sum output, only LSB 16 bits are used.

## The GUI should first have 8 buttons to control the 8 LEDs.
## Then there should be 4 "LED" to display the random number output.
## Finally, there should be 2 input fields to input the sum inputs A and B, with a min value of 0 and a max value of 65535, and a button to trigger the sum operation. The sum output should be displayed in a label. Everything should be in Hexadecimal format.

import ok
from PyQt6.QtWidgets import *
import sys
from PyQt6.QtCore import QTimer

dev = ok.okCFrontPanel()
dev.OpenBySerial("")
dev.ConfigureFPGA("First.bit")

from PyQt6.QtGui import QPainter, QColor

# -------------------------------------------------------------------
# Simple LED widget
# -------------------------------------------------------------------

from PyQt6.QtWidgets import QWidget


class LedWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.state = False
        self.setFixedSize(30, 30)

    def setState(self, on: bool):
        self.state = on
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        if self.state:
            color = QColor(0, 255, 0)     # bright green
        else:
            color = QColor(40, 60, 40)    # dim green

        painter.setBrush(color)
        painter.drawEllipse(2, 2, 26, 26)


class FirstDemo(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("First Demo")
        self.resize(400, 300)

        layout = QVBoxLayout()

        # LED Control buttons
        led_layout = QHBoxLayout()
        self.led_buttons = []
        for i in range(8):
            btn = QPushButton(f"LED {i}")
            btn.setCheckable(True)
            # Whenever the button is clicked, update the LEDs based on the current state of all buttons
            btn.clicked.connect(self.update_leds)
            self.led_buttons.append(btn)
            led_layout.addWidget(btn)
        layout.addLayout(led_layout)


        # LED Display for Random Number Output
        LED_widget_layout = QHBoxLayout()
        self.led_widgets = []
        for i in range(4):
            led = LedWidget()
            self.led_widgets.append(led)
            LED_widget_layout.addWidget(led)
        layout.addLayout(LED_widget_layout)

        # Sum Inputs, only accept hexadecimal input
        sum_layout = QHBoxLayout()
        self.input_a = QLineEdit()
        self.input_a.setPlaceholderText("Input A (0-FFFF)")
        self.input_b = QLineEdit()
        self.input_b.setPlaceholderText("Input B (0-FFFF)")
        sum_layout.addWidget(self.input_a)
        sum_layout.addWidget(self.input_b)
        layout.addLayout(sum_layout)

        # Sum Output
        self.sum_output_label = QLabel("Sum Output: 0x0000")
        layout.addWidget(self.sum_output_label)
        # Another output in decimal format for easier reading
        self.sum_output_decimal_label = QLabel("Sum Output (Decimal): 0")
        layout.addWidget(self.sum_output_decimal_label)

        # Sum Button
        sum_button = QPushButton("Calculate Sum")
        sum_button.clicked.connect(self.calculate_sum)
        layout.addWidget(sum_button)

        self.setLayout(layout)

        # Update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_random_output_LED)
        self.timer.start(100)

        self.counter = 0


    def update_leds(self):
        led_value = 0
        for i, btn in enumerate(self.led_buttons):
            if btn.isChecked():
                led_value |= (1 << i)
        # bit extend to 32 bits
        led_value = led_value & 0xFF
        dev.SetWireInValue(0x00, led_value)
        dev.UpdateWireIns()

    def calculate_sum(self):
        try:
            a = int(self.input_a.text(), 16)
            b = int(self.input_b.text(), 16)
            if a < 0 or a > 65535 or b < 0 or b > 65535:
                raise ValueError("Inputs must be between 0 and FFFF")
            # bit extend to 32 bits
            a = a & 0xFFFF
            b = b & 0xFFFF
            dev.SetWireInValue(0x01, a)
            dev.SetWireInValue(0x02, b)
            dev.UpdateWireIns()

            dev.UpdateWireOuts()
            sum_output = dev.GetWireOutValue(0x21) & 0xFFFF
            self.sum_output_label.setText(f"Sum Output: 0x{sum_output:04X}")
            self.sum_output_decimal_label.setText(f"Sum Output (Decimal): {sum_output}")

        except ValueError as e:
            QMessageBox.warning(self, "Invalid Input", str(e))
            return

    def update_random_output_LED(self):
        dev.UpdateWireOuts()
        random_value = dev.GetWireOutValue(0x20) & 0xF
        for i in range(4):
            self.led_widgets[i].setState((random_value >> i) & 0x1 == 1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FirstDemo()
    window.show()
    app.exec()