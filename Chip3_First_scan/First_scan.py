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


dev = ok.okCFrontPanel()
dev.OpenBySerial("")
'''TODO: Change this into the real bitstream file'''
dev.ConfigureFPGA("TOP_FEEDER.bit")

## Set the inital state for All the WireIns
dev.SetWireInValue(0x00, 0x1FFFFF)  # set all control signals to 1 in total 21 bits.
dev.UpdateWireIns()
## The LED should be all lit up now because Para_feed = 0xFFF and parain_en = 1
print("Initial state set, all LEDs should be ON now")

## disable the parain_en to disable the parallel loading mode and also set ok_scan_in to 0 to make sure it is ready for scan chain shift.
dev.SetWireInValue(0x00, 0x1FCFFF)  # set parain_en = 0, ok_scan_in = 0. [11:0] = FFF, [15:12] = 1100 = C, [20:16] = 11111 = 1F
dev.UpdateWireIns()
print("Parallel loading mode disabled.")

curr_wirein_value = 0x1FCFFF

## Create a simple GUI with 4 buttons and 12 LEDs to display the scan chain output
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

        # add a button to reset the scan chain
        self.reset_button = QPushButton("Reset Scan Chain")
        self.reset_button.clicked.connect(self.reset_scan_chain)
        layout.addWidget(self.reset_button)

        # add a button to set scan in value
        self.scan_in_button = QPushButton("Set Scan In High")
        self.scan_in_button.setCheckable(True)
        self.scan_in_button.clicked.connect(self.set_scan_in)
        layout.addWidget(self.scan_in_button)

        self.scan_button = QPushButton("Scan Chain Shift")
        self.scan_button.clicked.connect(self.OK_scan_chain_shift)
        layout.addWidget(self.scan_button)

        # add individual checkboxes and text boxes to control each bit of the WireIn for less mistakes and easier debugging.
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

        wire_in_layout = QHBoxLayout()
        # add 10 labels to show the current WireIn value for debugging
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

        # add a button to update the WireIn value for debugging
        self.update_wirein_button = QPushButton("Update WireIn Value")
        self.update_wirein_button.clicked.connect(self.update_wirein_value)
        layout.addWidget(self.update_wirein_button)

        wire_out_layout = QHBoxLayout()
        # add 3 labels to show the current WireOut value for debugging
        self.ok_led_wireout_label = QLabel("Current ok_LED_wireout_ep : 000")
        self.sdo_from_chip_label = QLabel("Current sdo_from_chip : 0")
        self.ok_scan_out_label = QLabel("Current ok_scan_out : 0")
        wire_out_layout.addWidget(self.ok_led_wireout_label)
        wire_out_layout.addWidget(self.sdo_from_chip_label)
        wire_out_layout.addWidget(self.ok_scan_out_label)
        layout.addLayout(wire_out_layout)


        # add a button to update the WireOut value for debugging
        self.update_wireout_button = QPushButton("Update WireOut Value")
        self.update_wireout_button.clicked.connect(self.update_wireout_value)
        layout.addWidget(self.update_wireout_button)

        self.setLayout(layout)

        ## refresh the LED status every 100 ms
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_leds)
        self.timer.start(100)

    def OK_scan_chain_shift(self):
        ## set a trigger in to enable the scan chain shifting
        dev.ActivateTriggerIn(0x40, 0)  # set ok_scan_enable = 1


    def update_leds(self):
        ## read the scan chain output from WireOut 0x20
        dev.UpdateWireOuts()
        scan_out = dev.GetWireOutValue(0x20) & 0xFFF  # only 12 bits are used
        for i in range(12):
            self.leds[12-1-i].setState((scan_out >> i) & 0x1 == 1)

    def set_scan_in(self):
        if self.scan_in_button.isChecked():
            ## only change the ok_scan_in bit to 1, keep other bits unchanged

            dev.SetWireInValue(0x00, 0x1FE000)  # [11:0] = 000, [15:12] = 1110 = E, [20:16] = 11111 = 1F
        else:
            ## only change the ok_scan_in bit to 0, keep other bits unchanged

            dev.SetWireInValue(0x00, 0x1FC000)  # [11:0] = 000, [15:12] = 1100 = C, [20:16] = 11111 = 1F
        dev.UpdateWireIns()

    def reset_scan_chain(self):
        ## ok_rstn_ok is active low, so we set it to 0 to reset the scan chain and then set it back to 1

        ## only set the rstn_ok bit to 0, keep other bits unchanged
        set_Wire00_val = 0x1FCFFF & ~(1 << 14)  # set bit 14 to 0, which is rstn_ok
        dev.SetWireInValue(0x00, set_Wire00_val)  # 0x1FCFFF
        dev.UpdateWireIns()
        dev.SetWireInValue(0x00, 0x1FCFFF)  # set rstn_ok back to 1
        dev.UpdateWireIns()

    def update_wirein_value(self):
        # collect the values from the input fields and checkboxes to form the WireIn value
        para_feed_value = int(self.para_feed_input.text(), 16) & 0xFFF
        parain_en_value = 1 if self.parain_en_input.isChecked() else 0
        ok_scan_in_value = 1 if self.ok_scan_in_input.isChecked() else 0
        rstn_ok_value = 1 if self.rstn_ok_input.isChecked() else 0
        pll_pdn_value = 1 if self.pll_pdn_input.isChecked() else 0
        pll_test_value = 1 if self.pll_test_input.isChecked() else 0
        frange_value = 1 if self.frange_input.isChecked() else 0
        pll_nmsx_sel_value = 1 if self.pll_nmsx_sel_input.isChecked() else 0
        lvds_ser_data_ctrl_value = 1 if self.lvds_ser_data_ctrl_input.isChecked() else 0
        ctrlB_value = 1 if self.ctrlB_input.isChecked() else 0
        wirein_value = (ctrlB_value << 20) | (lvds_ser_data_ctrl_value << 19) | (pll_nmsx_sel_value << 18) | (frange_value << 17) | (pll_test_value << 16) | (pll_pdn_value << 15) | (rstn_ok_value << 14) | (ok_scan_in_value << 13) | (parain_en_value << 12) | para_feed_value
        dev.SetWireInValue(0x00, wirein_value)
        # read back from the current WireIn value and update the label
        dev.UpdateWireIns()
        curr_wirein_value = dev.GetWireInValue(0x00)[1]
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
        self.para_feed_label.setText(f"Para_feed: {para_feed_value:03X}")
        self.parain_en_label.setText(f"parain_en: {parain_en_value}")
        self.ok_scan_in_label.setText(f"ok_scan_in: {ok_scan_in_value}")
        self.rstn_ok_label.setText(f"rstn_ok: {rstn_ok_value}")
        self.pll_pdn_label.setText(f"pll_pdn: {pll_pdn_value}")
        self.pll_test_label.setText(f"pll_test: {pll_test_value}")
        self.frange_label.setText(f"frange: {frange_value}")
        self.pll_nmsx_sel_label.setText(f"pll_nmsx_sel: {pll_nmsx_sel_value}")
        self.lvds_ser_data_ctrl_label.setText(f"lvds_ser_data_ctrl: {lvds_ser_data_ctrl_value}")
        self.ctrlB_label.setText(f"ctrlB: {ctrlB_value}")

    def update_wireout_value(self):
        # read back from the current WireOut value and update the label
        dev.UpdateWireOuts()
        wireout_value = dev.GetWireOutValue(0x20)
        ok_led_wireout_value = wireout_value & 0xFFF
        sdo_from_chip_value = (wireout_value >> 12) & 0x1
        ok_scan_out_value = (wireout_value >> 13) & 0x1
        self.ok_led_wireout_label.setText(f"ok_LED_wireout_ep: {ok_led_wireout_value:03X}")
        self.sdo_from_chip_label.setText(f"sdo_from_chip: {sdo_from_chip_value}")
        self.ok_scan_out_label.setText(f"ok_scan_out: {ok_scan_out_value}")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = FirstDemo()
    demo.show()
    sys.exit(app.exec())