## This script will serve as a test script to carry out some basic tests on Steve's opto sides of the chip.
## The tests will be carried out on the following endpoints:
##
## WireIn 0x00
##
## [31:0]  para_in34 [31:0]
##
## WireIn 0x01
##
## [1:0]  para_in34 [33:32]   
## [2]    samp_hold
## [3]    rstn_ok
##
## WireOut 0x20
##
## [31:0]  SR34_out_to_ep[31:0]
##
## WireOut 0x21
##
## [1:0]   SR34_out_to_ep[33:32]
##
## TriggerIn 0x40
##
## [0]    shif_clk
## [1]    SR34_SE
## [2]    para_enable


## import necessary dependencies including ok and PyQt6
import ok
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
import sys
from PyQt6.QtCore import QTimer
from custom_widg.Custom_widget import LedWidget

# -------------------------------------------------------------------
# FrontPanel 6.0 Initialization
# -------------------------------------------------------------------

devices = ok.FrontPanelDevices()
dev = devices.Open()

if dev is None:
    raise RuntimeError("Failed to open FrontPanel device")

result = dev.ConfigureFPGA("top_test_simple_shift.bit")

if result != ok.ErrorCode.NoError:
    raise RuntimeError(
        f"FPGA configuration failed: {dev.GetErrorMessage(result)}"    )

if not dev.IsFrontPanelEnabled():
    raise RuntimeError("FrontPanel support is not enabled in FPGA")

#-------------------------------------------------------------------
# FP6 Classic Data Port
#-------------------------------------------------------------------

dp = dev.GetFPGADataPortClassic()

#-------------------------------------------------------------------
# initialise the FPGA with the following values
#-------------------------------------------------------------------

## WireIn 0x00 = 0x00000000
dp.SetWireInValue(0x00, 0x00000000)

## WireIn 0x01 = 0x00000000
dp.SetWireInValue(0x01, 0x00000000)


## release reset
dp.SetWireInValue(0x01, 0x0008)

dp.UpdateWireIns()


para_in34_string = [
'En0',
'Mux0',
'En1',
'Mux1',
'En2',
'Mux2',
'En3',
'Mux3',
'En4',
'Mux4',
'En5',
'Mux5',
'En6',
'Mux6',
'En7',
'Mux7',
'En8',
'Mux8',
'En9',
'Mux9',
'En10',
'Mux10',
'En11',
'Mux11',
'En12',
'Mux12',
'En13',
'Mux13',
'En14',
'Mux14',
'En15',
'Mux15',
'En_HF',
'En_LPF'
]


## Develop GUI to display the controls and the LED status

class OPTO_Test_GUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("OPTO Test GUI")
        self.resize(800, 500)

        ## overall layout should be vertical
        layout = QVBoxLayout()


        ## Create 12 tick boxes for the first 16 bits of para_in34
        ## this will be horizontal layout with just 12 tick boxes
        tick_box_1_layout = QHBoxLayout()
        self.tick_boxes_1 = []
        for i in range(16):
            tick_box = QCheckBox(para_in34_string[i])
            tick_box.stateChanged.connect(self.update_para_in34)
            tick_box_1_layout.addWidget(tick_box)
            self.tick_boxes_1.append(tick_box)
        layout.addLayout(tick_box_1_layout)

        ## create another horizontal layout for the next 16 tick boxes
        tick_box_2_layout = QHBoxLayout()
        self.tick_boxes_2 = []
        for i in range(16, 32):
            tick_box = QCheckBox(para_in34_string[i])
            tick_box.stateChanged.connect(self.update_para_in34)
            tick_box_2_layout.addWidget(tick_box)
            self.tick_boxes_2.append(tick_box)
        layout.addLayout(tick_box_2_layout)

        ## create last 2 tick boxes for En_HF and En_LPF and center them in the layout
        tick_box_3_layout = QHBoxLayout()
        self.tick_boxes_3 = []
        for i in range(32, 34):
            tick_box = QCheckBox(para_in34_string[i])
            tick_box.stateChanged.connect(self.update_para_in34)
            tick_box_3_layout.addWidget(tick_box)
            self.tick_boxes_3.append(tick_box)
        tick_box_3_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(tick_box_3_layout)

        ## add 3 buttons for samp_hold, rstn_ok and para_enable
        ## sample hold and rstn_ok buttons are toggle buttons, while para_enable is a push button to send a trigger to the FPGA
        button_layout = QHBoxLayout()
        self.samp_hold_button = QPushButton("Sample/Hold")
        self.samp_hold_button.setCheckable(True)
        self.samp_hold_button.setChecked(False)
        self.samp_hold_button.clicked.connect(self.update_samp_hold)
        button_layout.addWidget(self.samp_hold_button)

        self.rstn_ok_button = QPushButton("Reset OpalKelly")
        self.rstn_ok_button.setCheckable(True)
        self.rstn_ok_button.setChecked(False)
        self.rstn_ok_button.clicked.connect(self.update_rstn_ok)
        button_layout.addWidget(self.rstn_ok_button)

        self.para_enable_button = QPushButton("Load Parallel Data")
        self.para_enable_button.clicked.connect(self.send_para_enable_trigger)
        button_layout.addWidget(self.para_enable_button)

        layout.addLayout(button_layout)

        ## add a label for leds
        led_label = QLabel("Status of SR34_out_to_ep")
        layout.addWidget(led_label)


        ## add 16 leds using LedWidget to display the status of the 16 bits of SR34_out_to_ep
        led_layout = QHBoxLayout()
        self.leds_1 = []
        for i in range(16):
            led = LedWidget()
            self.leds_1.append(led)
            led_layout.addWidget(led)

        layout.addLayout(led_layout)

        ## add another 16 leds to display the status of the next 16 bits of SR34_out_to_ep
        led_layout_2 = QHBoxLayout()
        self.leds_2 = []
        for i in range(16, 32):
            led = LedWidget()
            self.leds_2.append(led)
            led_layout_2.addWidget(led)
        layout.addLayout(led_layout_2)

        ## add last 2 leds to display the status of the last 2 bits of SR34_out_to_ep
        led_layout_3 = QHBoxLayout()
        self.leds_3 = []
        for i in range(32, 34):
            led = LedWidget()
            self.leds_3.append(led)
            led_layout_3.addWidget(led)
        led_layout_3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(led_layout_3)

        ## add 3 horizontal buttons for auto load, manual shift SR34 and manual send clock pulse
        ## they are all just push buttons, no toggle
        button_layout_2 = QHBoxLayout()
        self.auto_load_button = QPushButton("Auto Load")
        self.auto_load_button.clicked.connect(self.send_auto_load_trigger)
        button_layout_2.addWidget(self.auto_load_button)

        self.manual_shift_button = QPushButton("Manual Shift SR34")
        self.manual_shift_button.clicked.connect(self.send_manual_shift_trigger)
        button_layout_2.addWidget(self.manual_shift_button)

        self.manual_clock_button = QPushButton("Manual Clock Pulse")
        self.manual_clock_button.clicked.connect(self.send_manual_clock_trigger)
        button_layout_2.addWidget(self.manual_clock_button)

        layout.addLayout(button_layout_2)

        ## set the layout
        self.setLayout(layout)

        ## add a timer to update the leds every 100 ms
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_leds)
        self.timer.start(100)






    def update_para_in34(self):
        ## update the 32 bits of para_in34 based on the tick boxes
        para_in34_1st_value = 0
        for i in range(16):
            if self.tick_boxes_1[i].isChecked():
                para_in34_1st_value |= (1 << i)
        for i in range(16):
            if self.tick_boxes_2[i].isChecked():
                para_in34_1st_value |= (1 << (i + 16))
        ## update the 2 bits of para_in34 based on the tick boxes
        para_in34_2nd_value = 0
        for i in range(2):
            if self.tick_boxes_3[i].isChecked():
                para_in34_2nd_value |= (1 << i)

        dp.SetWireInValue(0x00, para_in34_1st_value)
        ## only update the lsb 2 bits of WireIn 0x01, keep the other bits unchanged
        dp.SetWireInValue(0x01, para_in34_2nd_value, 0x0003)
        dp.UpdateWireIns()


    def update_samp_hold(self):
        if self.samp_hold_button.isChecked():
            dp.SetWireInValue(0x01, 0x0004, 0x0004)

        else:
            dp.SetWireInValue(0x01, 0x0000, 0x0004)

        dp.UpdateWireIns()

    def update_rstn_ok(self):
        if self.rstn_ok_button.isChecked():
            dp.SetWireInValue(0x01, 0x0000, 0x0008)
        else:
            dp.SetWireInValue(0x01, 0x0008, 0x0008)
        dp.UpdateWireIns()

    def send_para_enable_trigger(self):
        dp.ActivateTriggerIn(0x40, 2)

    def send_auto_load_trigger(self):
        ## Send one schift clock first to load bit 33
        dp.ActivateTriggerIn(0x40, 0)

        ## loop 33 times to send shift enable and shift clock to load the rest of the bits
        for i in range(33):
            dp.ActivateTriggerIn(0x40, 1)
            dp.ActivateTriggerIn(0x40, 0)

    def send_manual_shift_trigger(self):
        dp.ActivateTriggerIn(0x40, 1)

    def send_manual_clock_trigger(self):
        dp.ActivateTriggerIn(0x40, 0)

    def update_leds(self):
        dp.UpdateWireOuts()
        led_value_1 = dp.GetWireOutValue(0x20) & 0xFFFFFFFF
        led_value_2 = dp.GetWireOutValue(0x21) & 0x00000003

        for i in range(16):
            self.leds_1[i].setState((led_value_1 >> i) & 0x01)
        for i in range(16):
            self.leds_2[i].setState((led_value_1 >> (i + 16)) & 0x01)
        for i in range(2):
            self.leds_3[i].setState((led_value_2 >> i) & 0x01)






if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OPTO_Test_GUI()
    window.show()
    sys.exit(app.exec())
