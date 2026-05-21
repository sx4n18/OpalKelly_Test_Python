from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QSlider,
    QCheckBox,
    QComboBox,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout
)

from PyQt6.QtCore import Qt

import sys


class DemoWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt6 FPGA Control Demo")
        self.resize(500, 400)

        # =========================
        # Create Widgets
        # =========================

        # Label
        self.status_label = QLabel("Status: Idle")

        # Text Input
        self.exposure_input = QLineEdit()
        self.exposure_input.setPlaceholderText("Enter exposure value")

        # Slider
        self.gain_slider = QSlider(Qt.Orientation.Horizontal)
        self.gain_slider.setMinimum(0)
        self.gain_slider.setMaximum(255)
        self.gain_slider.setValue(128)

        self.slider_value_label = QLabel("Gain = 128")

        # Checkbox
        self.compress_checkbox = QCheckBox("Enable Compression")

        # Dropdown Menu
        self.mode_dropdown = QComboBox()
        self.mode_dropdown.addItems([
            "Mode A",
            "Mode B",
            "Mode C"
        ])

        # Button
        self.apply_button = QPushButton("Apply Settings")

        # =========================
        # Layouts
        # =========================

        main_layout = QVBoxLayout()

        # Exposure Row
        exposure_layout = QHBoxLayout()
        exposure_layout.addWidget(QLabel("Exposure:"))
        exposure_layout.addWidget(self.exposure_input)

        # Gain Row
        gain_layout = QVBoxLayout()
        gain_layout.addWidget(QLabel("Gain Slider"))
        gain_layout.addWidget(self.gain_slider)
        gain_layout.addWidget(self.slider_value_label)

        # Mode Row
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Operating Mode:"))
        mode_layout.addWidget(self.mode_dropdown)

        # Add everything to main layout
        main_layout.addWidget(self.status_label)

        main_layout.addLayout(exposure_layout)

        main_layout.addLayout(gain_layout)

        main_layout.addWidget(self.compress_checkbox)

        main_layout.addLayout(mode_layout)

        main_layout.addWidget(self.apply_button)

        self.setLayout(main_layout)

        # =========================
        # Connect Signals
        # =========================

        self.gain_slider.valueChanged.connect(
            self.slider_changed
        )

        self.apply_button.clicked.connect(
            self.apply_settings
        )

    # ==================================
    # Callback Functions
    # ==================================

    def slider_changed(self, value):

        self.slider_value_label.setText(
            f"Gain = {value}"
        )

    def apply_settings(self):

        exposure = self.exposure_input.text()

        gain = self.gain_slider.value()

        compression_enabled = (
            self.compress_checkbox.isChecked()
        )

        mode = self.mode_dropdown.currentText()

        print("===== SETTINGS =====")
        print(f"Exposure: {exposure}")
        print(f"Gain: {gain}")
        print(f"Compression: {compression_enabled}")
        print(f"Mode: {mode}")

        self.status_label.setText(
            "Status: Settings Applied"
        )


# ==================================
# Main Application
# ==================================

app = QApplication(sys.argv)

window = DemoWindow()

window.show()

app.exec()