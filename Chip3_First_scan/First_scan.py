## This is to build a very simple scan chain check script for opal kelly board
## In the designed Opal kelly hardware the following endpoints are defined:
## + WireIn end point at 0x00
##   + [11:0] Para_feed; [12] parain_en; [13] ok_scan_in; [14] rstn_ok; [15] pll_pdn; [16] pll_test; [17] frange; [18] pll_nmsx_sel; [19] lvds_ser_data_ctrl; [20] ctrlB
## + WireOut end point at 0x20
##   + [11:0] ok_LED_wireout_ep; [12] sdo_from_chip; [13] ok_scan_out
## + TriggerIn end point at 0x40
##   + [0] ok_scan_enable; [1] SE
## There is a scan chain written in RTL in OpalKelly board that can be crammed in with parallel data of 12-bits from para_feed, or work in shift mode from ok_scan_in to ok_scan_out.
## This ok_scan_out will be connected to the real chip's SDI and read back by OpalKelly (not implemented yet)
##
## The script will first load the bitstream file into the board and then do a simple scan chain test by shifting in a pulse into the opal kelly
## and then read it from ok_scan_out. This should take 12 clock cycles, aka 12 TriggerIn event of ok_scan_enable

import ok
from PyQt6.QtWidgets import *
import sys
from custom_widg.Custom_widget import LedWidget
from PyQt6.QtCore import QTimer

# -------------------------------------------------------------------
# FrontPanel 6.0 Initialization
# -------------------------------------------------------------------

devices = ok.FrontPanelDevices()

dev = devices.Open()

if dev is None:
    raise RuntimeError("Failed to open FrontPanel device")

'''TODO: Change this into the real bitstream file'''
result = dev.ConfigureFPGA("TOP_FEEDER.bit")

if result != ok.ErrorCode.NoError:
    raise RuntimeError(
        f"FPGA configuration failed: {dev.GetErrorMessage(result)}"
    )

if not dev.IsFrontPanelEnabled():
    raise RuntimeError("FrontPanel support is not enabled")

# FP6 Classic Data Port
dp = dev.GetFPGADataPortClassic()

# -------------------------------------------------------------------
# Initial WireIn State
# -------------------------------------------------------------------

dp.SetWireInValue(0x00, 0x1FFFFF)
dp.UpdateWireIns()

print("Initial state set, all LEDs should be ON now")

dp.SetWireInValue(0x00, 0x1FCFFF)
dp.UpdateWireIns()

print("Parallel loading mode disabled.")

curr_wirein_value = 0x1FCFFF

# -------------------------------------------------------------------
# GUI
# -------------------------------------------------------------------


class FirstDemo(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("First Scan Chain Test")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        self.leds = [LedWidget() for _ in range(12)]

        led_layout = QHBoxLayout()

        for led in self.leds:
            led_layout.addWidget(led)

        layout.addLayout(led_layout)

        # Reset button
        self.reset_button = QPushButton("Reset Scan Chain")
        self.reset_button.clicked.connect(self.reset_scan_chain)
        layout.addWidget(self.reset_button)

        # Scan input button
        self.scan_in_button = QPushButton("Set Scan In High")
        self.scan_in_button.setCheckable(True)
        self.scan_in_button.clicked.connect(self.set_scan_in)
        layout.addWidget(self.scan_in_button)

        # Shift button
        self.scan_button = QPushButton("Scan Chain Shift")
        self.scan_button.clicked.connect(self.OK_scan_chain_shift)
        layout.addWidget(self.scan_button)

        # -------------------------------------------------------------
        # WireIn Controls
        # -------------------------------------------------------------

        WireIn_setup_layout = QHBoxLayout()

        self.para_feed_input = QLineEdit("FFF")

        self.parain_en_input = QCheckBox("parain_en")
        self.ok_scan_in_input = QCheckBox("ok_scan_in")
        self.rstn_ok_input = QCheckBox("rstn_ok")
        self.pll_pdn_input = QCheckBox("pll_pdn")
        self.pll_test_input = QCheckBox("pll_test")
        self.frange_input = QCheckBox("frange")
        self.pll_nmsx_sel_input = QCheckBox("pll_nmsx_sel")
        self.lvds_ser_data_ctrl_input = QCheckBox("lvds_ser_data_ctrl")
        self.ctrlB_input = QCheckBox("ctrlB")

        WireIn_setup_layout.addWidget(QLabel("Para_feed:"))
        WireIn_setup_layout.addWidget(self.para_feed_input)

        WireIn_setup_layout.addWidget(self.parain_en_input)
        WireIn_setup_layout.addWidget(self.ok_scan_in_input)
        WireIn_setup_layout.addWidget(self.rstn_ok_input)
        WireIn_setup_layout.addWidget(self.pll_pdn_input)
        WireIn_setup_layout.addWidget(self.pll_test_input)
        WireIn_setup_layout.addWidget(self.frange_input)
        WireIn_setup_layout.addWidget(self.pll_nmsx_sel_input)
        WireIn_setup_layout.addWidget(self.lvds_ser_data_ctrl_input)
        WireIn_setup_layout.addWidget(self.ctrlB_input)

        layout.addLayout(WireIn_setup_layout)

        # -------------------------------------------------------------
        # WireIn Labels
        # -------------------------------------------------------------

        wire_in_layout = QHBoxLayout()

        self.para_feed_label = QLabel("Para_feed : FFF")
        self.parain_en_label = QLabel("parain_en : 1")
        self.ok_scan_in_label = QLabel("ok_scan_in : 0")
        self.rstn_ok_label = QLabel("rstn_ok : 1")
        self.pll_pdn_label = QLabel("pll_pdn : 1")
        self.pll_test_label = QLabel("pll_test : 1")
        self.frange_label = QLabel("frange : 1")
        self.pll_nmsx_sel_label = QLabel("pll_nmsx_sel : 1")
        self.lvds_ser_data_ctrl_label = QLabel("lvds_ser_data_ctrl : 1")
        self.ctrlB_label = QLabel("ctrlB : 1")

        wire_in_layout.addWidget(self.para_feed_label)
        wire_in_layout.addWidget(self.parain_en_label)
        wire_in_layout.addWidget(self.ok_scan_in_label)
        wire_in_layout.addWidget(self.rstn_ok_label)
        wire_in_layout.addWidget(self.pll_pdn_label)
        wire_in_layout.addWidget(self.pll_test_label)
        wire_in_layout.addWidget(self.frange_label)
        wire_in_layout.addWidget(self.pll_nmsx_sel_label)
        wire_in_layout.addWidget(self.lvds_ser_data_ctrl_label)
        wire_in_layout.addWidget(self.ctrlB_label)

        layout.addLayout(wire_in_layout)

        # Update WireIn button
        self.update_wirein_button = QPushButton("Update WireIn Value")
        self.update_wirein_button.clicked.connect(
            self.update_wirein_value
        )

        layout.addWidget(self.update_wirein_button)

        # -------------------------------------------------------------
        # WireOut Labels
        # -------------------------------------------------------------

        wire_out_layout = QHBoxLayout()

        self.ok_led_wireout_label = QLabel(
            "Current ok_LED_wireout_ep : 000"
        )

        self.sdo_from_chip_label = QLabel(
            "Current sdo_from_chip : 0"
        )

        self.ok_scan_out_label = QLabel(
            "Current ok_scan_out : 0"
        )

        wire_out_layout.addWidget(self.ok_led_wireout_label)
        wire_out_layout.addWidget(self.sdo_from_chip_label)
        wire_out_layout.addWidget(self.ok_scan_out_label)

        layout.addLayout(wire_out_layout)

        # Update WireOut button
        self.update_wireout_button = QPushButton(
            "Update WireOut Value"
        )

        self.update_wireout_button.clicked.connect(
            self.update_wireout_value
        )

        layout.addWidget(self.update_wireout_button)

        self.setLayout(layout)

        # Refresh LED status every 100 ms
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_leds)
        self.timer.start(100)

    # -------------------------------------------------------------
    # FPGA Operations
    # -------------------------------------------------------------

    def OK_scan_chain_shift(self):
        dp.ActivateTriggerIn(0x40, 0)

    def update_leds(self):
        dp.UpdateWireOuts()

        scan_out = dp.GetWireOutValue(0x20) & 0xFFF

        for i in range(12):
            self.leds[12 - 1 - i].setState(
                ((scan_out >> i) & 0x1) == 1
            )

    def set_scan_in(self):

        if self.scan_in_button.isChecked():
            dp.SetWireInValue(0x00, 0x1FE000)
        else:
            dp.SetWireInValue(0x00, 0x1FC000)

        dp.UpdateWireIns()

    def reset_scan_chain(self):

        set_Wire00_val = 0x1FCFFF & ~(1 << 14)

        dp.SetWireInValue(0x00, set_Wire00_val)
        dp.UpdateWireIns()

        dp.SetWireInValue(0x00, 0x1FCFFF)
        dp.UpdateWireIns()

    def update_wirein_value(self):

        para_feed_value = int(
            self.para_feed_input.text(), 16
        ) & 0xFFF

        parain_en_value = (
            1 if self.parain_en_input.isChecked() else 0
        )

        ok_scan_in_value = (
            1 if self.ok_scan_in_input.isChecked() else 0
        )

        rstn_ok_value = (
            1 if self.rstn_ok_input.isChecked() else 0
        )

        pll_pdn_value = (
            1 if self.pll_pdn_input.isChecked() else 0
        )

        pll_test_value = (
            1 if self.pll_test_input.isChecked() else 0
        )

        frange_value = (
            1 if self.frange_input.isChecked() else 0
        )

        pll_nmsx_sel_value = (
            1 if self.pll_nmsx_sel_input.isChecked() else 0
        )

        lvds_ser_data_ctrl_value = (
            1 if self.lvds_ser_data_ctrl_input.isChecked()
            else 0
        )

        ctrlB_value = (
            1 if self.ctrlB_input.isChecked() else 0
        )

        wirein_value = (
            (ctrlB_value << 20)
            | (lvds_ser_data_ctrl_value << 19)
            | (pll_nmsx_sel_value << 18)
            | (frange_value << 17)
            | (pll_test_value << 16)
            | (pll_pdn_value << 15)
            | (rstn_ok_value << 14)
            | (ok_scan_in_value << 13)
            | (parain_en_value << 12)
            | para_feed_value
        )

        dp.SetWireInValue(0x00, wirein_value)

        dp.UpdateWireIns()

        # Verify FP6 GetWireInValue return type
        curr_wirein_value = dp.GetWireInValue(0x00)[1]

        para_feed_value = curr_wirein_value & 0xFFF
        parain_en_value = (curr_wirein_value >> 12) & 0x1
        ok_scan_in_value = (curr_wirein_value >> 13) & 0x1
        rstn_ok_value = (curr_wirein_value >> 14) & 0x1
        pll_pdn_value = (curr_wirein_value >> 15) & 0x1
        pll_test_value = (curr_wirein_value >> 16) & 0x1
        frange_value = (curr_wirein_value >> 17) & 0x1
        pll_nmsx_sel_value = (curr_wirein_value >> 18) & 0x1
        lvds_ser_data_ctrl_value = (curr_wirein_value >> 19) & 0x1
        ctrlB_value = (curr_wirein_value >> 20) & 0x1

        self.para_feed_label.setText(
            f"Para_feed: {para_feed_value:03X}"
        )

        self.parain_en_label.setText(
            f"parain_en: {parain_en_value}"
        )

        self.ok_scan_in_label.setText(
            f"ok_scan_in: {ok_scan_in_value}"
        )

        self.rstn_ok_label.setText(
            f"rstn_ok: {rstn_ok_value}"
        )

        self.pll_pdn_label.setText(
            f"pll_pdn: {pll_pdn_value}"
        )

        self.pll_test_label.setText(
            f"pll_test: {pll_test_value}"
        )

        self.frange_label.setText(
            f"frange: {frange_value}"
        )

        self.pll_nmsx_sel_label.setText(
            f"pll_nmsx_sel: {pll_nmsx_sel_value}"
        )

        self.lvds_ser_data_ctrl_label.setText(
            f"lvds_ser_data_ctrl: "
            f"{lvds_ser_data_ctrl_value}"
        )

        self.ctrlB_label.setText(
            f"ctrlB: {ctrlB_value}"
        )

    def update_wireout_value(self):

        dp.UpdateWireOuts()

        wireout_value = dp.GetWireOutValue(0x20)

        ok_led_wireout_value = wireout_value & 0xFFF
        sdo_from_chip_value = (wireout_value >> 12) & 0x1
        ok_scan_out_value = (wireout_value >> 13) & 0x1

        self.ok_led_wireout_label.setText(
            f"ok_LED_wireout_ep: "
            f"{ok_led_wireout_value:03X}"
        )

        self.sdo_from_chip_label.setText(
            f"sdo_from_chip: {sdo_from_chip_value}"
        )

        self.ok_scan_out_label.setText(
            f"ok_scan_out: {ok_scan_out_value}"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    demo = FirstDemo()
    demo.show()

    sys.exit(app.exec())