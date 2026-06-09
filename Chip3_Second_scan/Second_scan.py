####################################################################
## This is to test the second scan of the design example. The design example has the following endpoints:
## WireIn 0x00
## [11:0]  PARA_FEED
## [12]    PARAIN_EN
## [13]    OK_SCAN_IN
## [14]    rstn_ok
## [15]    PLL_PDN
## [16]    PLL_TEST
## [17]    FRANGE
## [18]    PLL_NMSX_SEL
## [19]    LVDS_ser_data_ctrl
## [20]    ctrlB
## WireOut 0x20
## [11:0]   OK_LED_WIREOUT_EP
## [12]     SDO_from_chip
## [13]     OK_SCAN_OUT
## [25:14]  SDO_PARA_DATA
## [31:26]  Reserved
## TriggerIn 0x40
## [0]    SE
## [1]    clk_LVDS


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
result = dev.ConfigureFPGA("Top_scan_Test.bit")

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

PARA_FEED = 0xFFF
PARAIN_EN = 1
OK_SCAN_IN = 1
rstn_ok = 1
PLL_PDN = 1
PLL_TEST = 1
FRANGE = 1
PLL_NMSX_SEL = 1
LVDS_ser_data_ctrl = 1
ctrlB = 1

WIREIN00 = ctrlB << 20 | LVDS_ser_data_ctrl << 19 | PLL_NMSX_SEL << 18 | FRANGE << 17 | PLL_TEST << 16 | PLL_PDN << 15 | rstn_ok << 14 | OK_SCAN_IN << 13 | PARAIN_EN << 12 | PARA_FEED
dp.SetWireInValue(0x00, WIREIN00)
dp.UpdateWireIns()


# ------------------------------------------------------------------
# GUI development
# ------------------------------------------------------------------

class OKTESTGUI(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("OKTEST GUI")
        ## set a big window to fit everything in
        self.setGeometry(100, 100, 400, 300)

        ## set up the main layout
        layout = QVBoxLayout()

        ## add 12 LEDs from the custom widget
        '''
        This LED needs refreshing at the back ground
        '''
        ## give these LED names with a text on top
        self.OKLEDTITLE = QLabel("OK scan chain LED that feeds SDI of the chip")
        layout.addWidget(self.OKLEDTITLE)
        self.LED_widgets = [LedWidget() for _ in range(12)]
        LED_layout = QHBoxLayout()
        for led in self.LED_widgets:
            LED_layout.addWidget(led)
        layout.addLayout(LED_layout)

        ## add 4 buttons to flush the scan chain individually with 1 or 0
        scan_chain_flush_layout = QHBoxLayout()
        self.steve_chain_flush_1 = QPushButton("Steve Chain Flush with 1")
        self.steve_chain_flush_1.clicked.connect(lambda :self.steve_chain_flush(1))
        self.steve_chain_flush_0 = QPushButton("Steve Chain Flush with 0")
        self.steve_chain_flush_0.clicked.connect(lambda :self.steve_chain_flush(0))
        self.sho_chain_flush_1 = QPushButton("Sho Chain Flush with 1")
        self.sho_chain_flush_1.clicked.connect(lambda :self.sho_chain_flush(1))
        self.sho_chain_flush_0 = QPushButton("Sho Chain Flush with 0")
        self.sho_chain_flush_0.clicked.connect(lambda :self.sho_chain_flush(0))
        scan_chain_flush_layout.addWidget(self.steve_chain_flush_1)
        scan_chain_flush_layout.addWidget(self.steve_chain_flush_0)
        scan_chain_flush_layout.addWidget(self.sho_chain_flush_1)
        scan_chain_flush_layout.addWidget(self.sho_chain_flush_0)

        layout.addLayout(scan_chain_flush_layout)

        ## add 7 tick boxes to be shifted into Steve's scan chain
        tick_box_layout = QHBoxLayout()
        self.ctrlATB = QCheckBox("ctrlA")
        tick_box_layout.addWidget(self.ctrlATB)
        self.ENTB = QCheckBox("EN")
        tick_box_layout.addWidget(self.ENTB)
        self.RSTB = QCheckBox("RS")
        tick_box_layout.addWidget(self.RSTB)
        self.rstnTB = QCheckBox("rst_n")
        tick_box_layout.addWidget(self.rstnTB)
        self.LVDSSEL1 = QCheckBox("LVDS_sel<1>")
        tick_box_layout.addWidget(self.LVDSSEL1)
        self.LVDSSEL0 = QCheckBox("LVDS_sel<0>")
        tick_box_layout.addWidget(self.LVDSSEL0)
        self.rstnpll = QCheckBox("rst_n_pll")
        tick_box_layout.addWidget(self.rstnpll)
        layout.addLayout(tick_box_layout)

        ## add a button to shift tick boxes values in to the chain
        self.tickbox_shift_btn = QPushButton("Shift Tick Box Values into Steve's Scan Chain")
        self.tickbox_shift_btn.clicked.connect(self.shift_tickbox_into_steve_chain)
        layout.addWidget(self.tickbox_shift_btn)

        ## add 2 boxes for N and M value, and 9 tick boxes for PARAIN_EN, OK_SCAN_IN, rstn_ok, PLL_PDN, PLL_TEST, FRANGE, PLL_NMSX_SEL, LVDS_ser_data_ctrl, ctrlB to be shifted into Sho's scan chain
        shou_config_layout = QHBoxLayout()
        self.NX_VAL_box = QLineEdit()
        self.NX_VAL_box.setPlaceholderText("N for PLL:1-31")
        shou_config_layout.addWidget(self.NX_VAL_box)
        self.MX_VAL_box = QLineEdit()
        self.MX_VAL_box.setPlaceholderText("M for PLL:1-31")
        shou_config_layout.addWidget(self.MX_VAL_box)
        self.PARAIN_EN_TB = QCheckBox("PARAIN_EN")
        shou_config_layout.addWidget(self.PARAIN_EN_TB)
        self.OK_SCAN_IN_TB = QCheckBox("OK_SCAN_IN")
        shou_config_layout.addWidget(self.OK_SCAN_IN_TB)
        self.rstn_ok_TB = QCheckBox("rstn_ok")
        shou_config_layout.addWidget(self.rstn_ok_TB)
        self.PLL_PDN_TB = QCheckBox("PLL_PDN")
        shou_config_layout.addWidget(self.PLL_PDN_TB)
        self.PLL_TEST_TB = QCheckBox("PLL_TEST")
        shou_config_layout.addWidget(self.PLL_TEST_TB)
        self.FRANGE_TB = QCheckBox("FRANGE")
        shou_config_layout.addWidget(self.FRANGE_TB)
        self.PLL_NMSX_SEL_TB = QCheckBox("PLL_NMSX_SEL")
        shou_config_layout.addWidget(self.PLL_NMSX_SEL_TB)
        self.LVDS_ser_data_ctrl_TB = QCheckBox("LVDS_ser_data_ctrl")
        shou_config_layout.addWidget(self.LVDS_ser_data_ctrl_TB)
        self.ctrlB_TB = QCheckBox("ctrlB")
        shou_config_layout.addWidget(self.ctrlB_TB)
        layout.addLayout(shou_config_layout)

        ## add a button to read the config and push data in through wireIN
        self.chip_config_btn = QPushButton("Chip Config")
        self.chip_config_btn.clicked.connect(self.chip_config)
        layout.addWidget(self.chip_config_btn)

        ## add another button simply just shift ok scan chain values into the system
        self.ok_scan_shift_btn = QPushButton("Shift OK Scan Chain")
        self.ok_scan_shift_btn.clicked.connect(self.shift_ok_scan_chain)
        layout.addWidget(self.ok_scan_shift_btn)

        ## add another 12 LEDs for scan chain that picks up output from SDO from chip
        '''
        This LED needs refreshing at the back ground
        '''
        self.SDOCATTITLE = QLabel("OK scan chain LED that picks up SDO from the chip")
        layout.addWidget(self.SDOCATTITLE)
        self.SDO_LED = [LedWidget() for _ in range(12)]
        LED_layout = QHBoxLayout()
        for led in self.SDO_LED:
            LED_layout.addWidget(led)
        layout.addLayout(LED_layout)


        # ------------------------------------------------------
        # Status box
        # ------------------------------------------------------
        status_layout = QFormLayout()
        self.para_feed_status = QLabel("0xFFF")
        self.PARAIN_EN_status = QLabel("1")
        self.OK_SCAN_IN_status = QLabel("1")
        self.rstn_ok_status = QLabel("1")
        self.PLL_PDN_status = QLabel("1")
        self.PLL_TEST_status = QLabel("1")
        self.FRANGE_status = QLabel("1")
        self.PLL_NMSX_SEL_status = QLabel("1")
        self.LVDS_ser_data_ctrl_status = QLabel("1")
        self.ctrlB_status = QLabel("1")
        status_layout.addRow("PARA_FEED:", self.para_feed_status)
        status_layout.addRow("PARAIN_EN:", self.PARAIN_EN_status)
        status_layout.addRow("OK_SCAN_IN:", self.OK_SCAN_IN_status)
        status_layout.addRow("rstn_ok:", self.rstn_ok_status)
        status_layout.addRow("PLL_PDN:", self.PLL_PDN_status)
        status_layout.addRow("PLL_TEST:", self.PLL_TEST_status)
        status_layout.addRow("FRANGE:", self.FRANGE_status)
        status_layout.addRow("PLL_NMSX_SEL:", self.PLL_NMSX_SEL_status)
        status_layout.addRow("LVDS_ser_data_ctrl:", self.LVDS_ser_data_ctrl_status)
        status_layout.addRow("ctrlB:", self.ctrlB_status)

        layout.addLayout(status_layout)

        self.setLayout(layout)

        ## Timer call back to refresh display for WireIn values and WireOut values
        # Refresh LED status every 100 ms
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_LED_and_status)
        self.timer.start(100)






    def steve_chain_flush(self, num):
        ## Steve's chain is simple, we simply set LVDS_ser_data_ctrl to num and activate triggerin @ 0x40's bit 1 for 7 times
        LVDS_ser_data_ctrl_val = num << 19
        dp.SetWireInValue(0x00, LVDS_ser_data_ctrl_val, 1<<19)
        dp.UpdateWireIns()
        for _ in range(7):
            dp.ActivateTriggerIn(0x40, 1)

    def sho_chain_flush(self, num):
        ## Shou's scan chain is slightly different, there is no direct control for SDI, we shall simply enable the parain
        ## and then flush opal kelly scan chain first before activate trigger in @ 0x40 bit 0 for 12 times
        if num == 0:
            para_feed = 0x000
        else:
            para_feed = 0xfff
        dp.SetWireInValue(0x00, para_feed, 0xfff) ## update the least significant 12 bits
        ## enable the para in
        dp.SetWireInValue(0x00, 1<<12, 1<<12)
        ## update wire in
        dp.UpdateWireIns()
        for _ in range(12):
            dp.ActivateTriggerIn(0x40, 0)


    def update_LED_and_status(self):
        ## read the data back from WireIn and WireOut from 0x00 and 0x20 and update the LED status accordingly
        dp.UpdateWireOuts()
        wireout_20 = dp.GetWireOutValue(0x20)
        wirein_00 = dp.GetWireInValue(0x00)[1]
        self.para_feed_status.setText(f"0x{wirein_00 & 0xFFF:03X}")
        self.PARAIN_EN_status.setText(f"{(wirein_00 >> 12) & 0x1}")
        self.OK_SCAN_IN_status.setText(f"{(wirein_00 >> 13) & 0x1}")
        self.rstn_ok_status.setText(f"{(wirein_00 >> 14) & 0x1}")
        self.PLL_PDN_status.setText(f"{(wirein_00 >> 15) & 0x1}")
        self.PLL_TEST_status.setText(f"{(wirein_00 >> 16) & 0x1}")
        self.FRANGE_status.setText(f"{(wirein_00 >> 17) & 0x1}")
        self.PLL_NMSX_SEL_status.setText(f"{(wirein_00 >> 18) & 0x1}")
        self.LVDS_ser_data_ctrl_status.setText(f"{(wirein_00 >> 19) & 0x1}")
        self.ctrlB_status.setText(f"{(wirein_00 >> 20) & 0x1}")
        ## [11:0] for ok_LED
        ok_LED_OUT = wireout_20 & 0xFFF
        ## [25:14] for SDO_LED
        SDO_LED_OUT = (wireout_20 >> 14) & 0xFFF

        for i in range(12):
            self.SDO_LED[11-i].setState((SDO_LED_OUT >> i) & 0x1)
            self.LED_widgets[11-i].setState((ok_LED_OUT >> i) & 0x1)

    def shift_tickbox_into_steve_chain(self):
        # Implementation for shifting tick box values into Steve's scan chain
        # Value should shift in the reverse order of ctrlA, EN, RS, rst_n, LVDS_sel1, LVDS_sel0, rst_n_pll
        ctrlA_val = 1 if self.ctrlATB.isChecked() else 0
        EN_val = 1 if self.ENTB.isChecked() else 0
        RS_val = 1 if self.RSTB.isChecked() else 0
        rst_n_val = 1 if self.rstnTB.isChecked() else 0
        LVDS_sel1_val = 1 if self.LVDSSEL1.isChecked() else 0
        LVDS_sel0_val = 1 if self.LVDSSEL0.isChecked() else 0
        rst_n_pll_val = 1 if self.rstnpll.isChecked() else 0
        shift_in_word = ctrlA_val << 6 | EN_val << 5 | RS_val << 4 | rst_n_val << 3 | LVDS_sel1_val << 2 | LVDS_sel0_val << 1 | rst_n_pll_val
        ## set LVDS_ser_data_ctrl to the least significant bit of shift_in_word and then activate trigger in
        for i in range(7):
            bit_val = (shift_in_word >> i) & 0x1
            dp.SetWireInValue(0x00, bit_val << 19, 1 << 19)
            dp.UpdateWireIns()
            dp.ActivateTriggerIn(0x40, 1)

    def chip_config(self):
        ## read through the values from the config boxes and tick boxes, then update the wire in value at 0x00 accordingly
        try:
            N_val = int(self.NX_VAL_box.text())
            M_val = int(self.MX_VAL_box.text())
            if N_val < 1 or N_val > 31 or M_val < 1 or M_val > 31:
                raise ValueError("N and M values must be between 1 and 31, instead got N: {} and M: {}".format(N_val, M_val))
            ## Another sanity check for N and M, where N/M should be equal or smaller than 15
            if N_val / M_val > 15:
                raise ValueError("The ratio of N/M should be equal or smaller than 15, instead got N: {} and M: {}, ratio: {}".format(N_val, M_val, N_val/M_val))
            PARA_FEED_val = N_val << 6 | M_val
            PARA_IN_EN_val = 1 if self.PARAIN_EN_TB.isChecked() else 0
            OK_SCAN_IN_val = 1 if self.OK_SCAN_IN_TB.isChecked() else 0
            rstn_ok_val = 1 if self.rstn_ok_TB.isChecked() else 0
            PLL_PDN_val = 1 if self.PLL_PDN_TB.isChecked() else 0
            PLL_TEST_val = 1 if self.PLL_TEST_TB.isChecked() else 0
            FRANGE_val = 1 if self.FRANGE_TB.isChecked() else 0
            PLL_NMSX_SEL_val = 1 if self.PLL_NMSX_SEL_TB.isChecked() else 0
            LVDS_ser_data_ctrl_val = 1 if self.LVDS_ser_data_ctrl_TB.isChecked() else 0
            ctrlB_val = 1 if self.ctrlB_TB.isChecked() else 0

            wirein_00_val = PARA_FEED_val | (PARA_IN_EN_val << 12) | (OK_SCAN_IN_val << 13) | (rstn_ok_val << 14) | (PLL_PDN_val << 15) | (PLL_TEST_val << 16) | (FRANGE_val << 17) | (PLL_NMSX_SEL_val << 18) | (LVDS_ser_data_ctrl_val << 19) | (ctrlB_val << 20)
            dp.SetWireInValue(0x00, wirein_00_val, 0x1FFFFF) ## update all 21 bits
            dp.UpdateWireIns()

        except ValueError as e:
            QMessageBox.warning(self, "Invalid Input", str(e))
            return

    def shift_ok_scan_chain(self):
        ## simply activate trigger in @ 0x40 bit 0 for 12 times to shift the ok scan chain
        for _ in range(12):
            dp.ActivateTriggerIn(0x40, 0)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    Test_window = OKTESTGUI()
    Test_window.show()
    sys.exit(app.exec())
