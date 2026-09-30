## This is the testing script for Steve's SPI interface with the provided GUI with the following endpoints:
## WireIn 0x00:
## [2:0] parallel_data_range
## [3]   nglobals
## -----------------
## [4]   para_load     system infra signals
## [5]   ok_rstn
## [7:6] mosi_sel
## [8]   Latch
## [9]   SH
## -----------------
## WireIn 0x01:
## [9:0] parallel_data_addr
## [10]  nCS
## WireIn 0x02:
## [2] nine_eight_cfg
## [1] en_adc_res_cfg
## [0] clk_doub_cfg
## [3] nclk_set
## WireIn 0x03:
## [0] AutoHold_cfg
## [1] offctrl_cfg
## [2] en_general_cfg
## [3] FixRef_cfg
## [4] en_offset_amp_cfg
## [9:5] offset_cfg
## [10] node_sw
##
## WireOut 0x20:
## [2:0] shift_reg_range_out
## WireOut 0x21:
## [9:0] shift_reg_addr_out
## WireOut 0x22:
## [2:0] shift_reg_clkcfg_out
## WireOut 0x23:
## [9:0] shift_reg_nodecfg_out
##
## TriggerIn 0x40:
## [0] SE0
## [1] SE1
## [2] SE2
## [3] SE3
## [4] spi_clk

# import related package
import ok
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
import sys
from PyQt6.QtCore import QTimer
from custom_widg.Custom_widget import LedWidget
import time


# -------------------------------------------------------------------
# FrontPanel 6.0 Initialization
# -------------------------------------------------------------------


devices = ok.FrontPanelDevices()
dev = devices.Open()

if dev is None:
    raise RuntimeError("Failed to open FrontPanel device")

result = dev.ConfigureFPGA("Steve_SPI_ctrl.bit")

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
# initialise WireIn 0x00 with 00_0000_1000
dp.SetWireInValue(0x00, 0x00000008)

# initialise WireIn 0x01 with 100_0000_0000
dp.SetWireInValue(0x01, 0x00000400)

# initialise WireIn 0x02 with 1000
dp.SetWireInValue(0x02, 0x00000008)

# initialise WireIn 0x03 with 0000_0000_0000
dp.SetWireInValue(0x03, 0x00000000)

dp.UpdateWireIns()



#-------------------------------------------------------------------
# define the main window class
#-------------------------------------------------------------------


class SteveSPITest(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Steve SPI Test")
        self.resize(400, 300)

        # Create a layout
        layout = QVBoxLayout()

        ## Create 2 boarder lines for global configs like range and clock settings with a horizontal layout
        global_config_layout = QHBoxLayout()

        # ----------- range box ------------------
        ### range box circumference
        self.range_box = QGroupBox("Data Range")
        range_layout = QVBoxLayout()
        ### create a label and an input box for the range and a load button
        range_cfg_layout = QHBoxLayout()
        self.range_label = QLabel("Range (0-7):")
        self.range_input = QLineEdit()
        self.load_button = QPushButton("SPI Load Range")
        self.load_button.clicked.connect(self.spi_load_range)
        range_cfg_layout.addWidget(self.range_label)
        range_cfg_layout.addWidget(self.range_input)
        range_cfg_layout.addWidget(self.load_button)
        ### add 3 LEDs to indicate the range value in binary
        range_led_layout = QHBoxLayout()
        self.range_leds = []
        for i in range(3):
            led = LedWidget()
            self.range_leds.append(led)
            range_led_layout.addWidget(led)
        ### add range_cfg_layout and range_led_layout to range_layout
        range_layout.addLayout(range_cfg_layout)
        range_layout.addLayout(range_led_layout)
        self.range_box.setLayout(range_layout)
        ### add this box to the global_config_layout
        global_config_layout.addWidget(self.range_box)


        # ----------- clock setting box ------------------
        ### clock setting circumference
        self.clock_box = QGroupBox("Clock Settings")
        clock_set_layout = QVBoxLayout()

        ### create 3 tick boxes for the clock settings
        clk_cfg_tick_layout = QHBoxLayout()
        self.nine_eight_tick = QCheckBox("9/8 Clock")
        self.en_adc_res_tick = QCheckBox("Enable ADC Res")
        self.clk_doub_tick = QCheckBox("Clock Doubler")
        clk_cfg_tick_layout.addWidget(self.nine_eight_tick)
        clk_cfg_tick_layout.addWidget(self.en_adc_res_tick)
        clk_cfg_tick_layout.addWidget(self.clk_doub_tick)
        clock_set_layout.addLayout(clk_cfg_tick_layout)
        self.clock_box.setLayout(clock_set_layout)

        ### add another load button for the clock settings
        self.clock_load_button = QPushButton("SPI Load Clock Settings")
        self.clock_load_button.clicked.connect(self.spi_load_clock_settings)
        clock_set_layout.addWidget(self.clock_load_button)

        ### add 3 LEDs to indicate the clock settings
        clock_led_layout = QHBoxLayout()
        self.clock_leds = []
        for i in range(3):
            led = LedWidget()
            self.clock_leds.append(led)
            clock_led_layout.addWidget(led)
        clock_set_layout.addLayout(clock_led_layout)
        self.clock_box.setLayout(clock_set_layout)
        ### add this box to the global_config_layout
        global_config_layout.addWidget(self.clock_box)

        ## add the global_config_layout to the main layout
        layout.addLayout(global_config_layout)

        # ----------- ADDR box ------------------
        ### ADDR box circumference
        self.addr_box = QGroupBox("Address Settings")
        addr_layout = QVBoxLayout()

        ### create a label and an input box for the address and a load button
        addr_cfg_layout = QHBoxLayout()
        self.addr_label = QLabel("Address (0-1023):")
        self.addr_input = QLineEdit()
        self.addr_load_button = QPushButton("SPI Load Address")
        self.addr_load_button.clicked.connect(self.spi_load_address)
        addr_cfg_layout.addWidget(self.addr_label)
        addr_cfg_layout.addWidget(self.addr_input)
        addr_cfg_layout.addWidget(self.addr_load_button)
        addr_layout.addLayout(addr_cfg_layout)

        ### add 10 LEDs to indicate the address value in binary
        addr_led_layout = QHBoxLayout()
        self.addr_leds = []
        for i in range(10):
            led = LedWidget()
            self.addr_leds.append(led)
            addr_led_layout.addWidget(led)
        addr_layout.addLayout(addr_led_layout)
        self.addr_box.setLayout(addr_layout)

        ## add the addr_box to the main layout
        layout.addWidget(self.addr_box)

        # ----------- Node specific settings box ------------------
        ### Node specific settings circumference
        self.node_box = QGroupBox("Node Specific Settings")
        node_layout = QVBoxLayout()

        ### create 5 tick boxes for the node specific settings
        node_cfg_tick_layout = QHBoxLayout()
        self.auto_hold_tick = QCheckBox("Auto Hold")
        self.offctrl_tick = QCheckBox("Off Control")
        self.en_general_tick = QCheckBox("Enable General")
        self.fix_ref_tick = QCheckBox("Fix Reference")
        self.en_offset_amp_tick = QCheckBox("Enable Offset Amp")
        node_cfg_tick_layout.addWidget(self.auto_hold_tick)
        node_cfg_tick_layout.addWidget(self.offctrl_tick)
        node_cfg_tick_layout.addWidget(self.en_general_tick)
        node_cfg_tick_layout.addWidget(self.fix_ref_tick)
        node_cfg_tick_layout.addWidget(self.en_offset_amp_tick)
        node_layout.addLayout(node_cfg_tick_layout)

        ### add a label and an input box for the offset value and a load button
        offset_cfg_layout = QHBoxLayout()
        self.offset_label = QLabel("Offset (0-31):")
        self.offset_input = QLineEdit()
        self.offset_load_button = QPushButton("SPI Load Node Settings")
        self.offset_load_button.clicked.connect(self.spi_load_node_settings)
        offset_cfg_layout.addWidget(self.offset_label)
        offset_cfg_layout.addWidget(self.offset_input)
        offset_cfg_layout.addWidget(self.offset_load_button)
        node_layout.addLayout(offset_cfg_layout)

        ### add 10 LEDs to indicate the node configuration value in binary
        nodecfg_led_layout = QHBoxLayout()
        self.nodecfg_leds = []
        for i in range(10):
            led = LedWidget()
            self.nodecfg_leds.append(led)
            nodecfg_led_layout.addWidget(led)
        node_layout.addLayout(nodecfg_led_layout)

        self.node_box.setLayout(node_layout)

        ## add the node_box to the main layout
        layout.addWidget(self.node_box)

        # ----------- Just few buttons at the bottom ------------------
        ### button horizontal layout
        button_layout = QHBoxLayout()
        ### add an ok_rstn button to reset the OpalKelly device
        self.ok_rstn_button = QPushButton("Reset OpalKelly")
        ## TODO: connect the button to a function that resets the OpalKelly device
        self.ok_rstn_button.clicked.connect(self.reset_opalkelly)
        button_layout.addWidget(self.ok_rstn_button)

        ### add a para_load button to load the parallel data
        self.para_load_button = QPushButton("Load Parallel Data")
        ## TODO: connect the button to a function that loads the parallel data
        self.para_load_button.clicked.connect(self.load_parallel_data)
        button_layout.addWidget(self.para_load_button)

        ### add a latch button for Steve
        self.latch_button = QPushButton("Latch Data")
        ## TODO: connect the button to a function that latches the data
        self.latch_button.clicked.connect(self.latch_node_data)
        button_layout.addWidget(self.latch_button)

        ### add a SH button that is toggle for Steve
        self.sh_button = QPushButton("Sample/Hold")
        ### TODO: connect the button to a function that shifts the data
        self.sh_button.setCheckable(True)
        self.sh_button.clicked.connect(self.sample_hold)
        button_layout.addWidget(self.sh_button)

        ## add the button_layout to the main layout
        layout.addLayout(button_layout)

        # Set the layout for the main window
        self.setLayout(layout)

        ## add time out to refresh the LED status every 100 ms
        self.timer = QTimer()
        ## TODO: connect the timer to a function that updates the LED status
        self.timer.timeout.connect(self.update_led_status)
        self.timer.start(100)  # Update every 100 ms

    def reset_opalkelly(self):
        # Implementation for resetting OpalKelly device
        ## simply assert ok_rstn to 0 for 100 ms and then deassert it to 1
        # update bit 5 of the WireIn 0x00 to 0 and then back to 1
        dp.SetWireInValue(0x00, 0x00000000, 0x0020 )  # assert ok_rstn to 0
        dp.UpdateWireIns()
        time.sleep(0.1)  # Wait for 100 ms
        dp.SetWireInValue(0x00, 0x00000020, 0x0020 )  # deassert ok_rstn to 1
        dp.UpdateWireIns()


    def load_parallel_data(self):
        # Implementation for loading parallel data
        ## get the range value from the range input box and the address value from the address input box and the offset value from the offset input box
        range_value = int(self.range_input.text())
        if range_value < 0 or range_value > 7:
            QMessageBox.warning(self, "Invalid Input", "Range must be between 0 and 7")
            return
        addr_value = int(self.addr_input.text())
        if addr_value < 0 or addr_value > 1023:
            QMessageBox.warning(self, "Invalid Input", "Address must be between 0 and 1023")
            return
        offset_value = int(self.offset_input.text())
        if offset_value < 0 or offset_value > 31:
            QMessageBox.warning(self, "Invalid Input", "Offset must be between 0 and 31")
            return
        ## get the tick box values for the clock settings and the node specific settings
        nine_eight_value = 1 if self.nine_eight_tick.isChecked() else 0
        en_adc_res_value = 1 if self.en_adc_res_tick.isChecked() else 0
        clk_doub_value = 1 if self.clk_doub_tick.isChecked() else 0
        auto_hold_value = 1 if self.auto_hold_tick.isChecked() else 0
        offctrl_value = 1 if self.offctrl_tick.isChecked() else 0
        en_general_value = 1 if self.en_general_tick.isChecked() else 0
        fix_ref_value = 1 if self.fix_ref_tick.isChecked() else 0
        en_offset_amp_value = 1 if self.en_offset_amp_tick.isChecked() else 0

        ## set the values to the WireIn 0x00 only update bit [2:0]
        dp.SetWireInValue(0x00, range_value, 0x0007)
        ## set the values to the WireIn 0x01 only update bit [9:0]
        dp.SetWireInValue(0x01, addr_value, 0x03FF)
        ## set the values to the WireIn 0x02 only update bit [2:0]
        dp.SetWireInValue(0x02, (nine_eight_value << 2) | (en_adc_res_value << 1) | clk_doub_value, 0x0007)
        ## set the values to the WireIn 0x03 only update bit [10:0]
        dp.SetWireInValue(0x03, (auto_hold_value << 0) | (offctrl_value << 1) | (en_general_value << 2) | (fix_ref_value << 3) | (en_offset_amp_value << 4) | (offset_value << 5), 0x03FF)

        ## simply assert para_load to 1 for 100 ms and then deassert it to 0
        # update bit 4 of the WireIn 0x00 to 1 and then back to 0
        dp.SetWireInValue(0x00, 0x00000010, 0x0010 )  # assert para_load to 1
        dp.UpdateWireIns()
        time.sleep(0.1)  # Wait for 100 ms
        dp.SetWireInValue(0x00, 0x00000000, 0x0010 )  # deassert para_load to 0
        dp.UpdateWireIns()


    def latch_node_data(self):
        # Implementation for latching node data
        ## assert the Latch button to 1 for 100 ms and then deassert it to 0
        ## update bit 8 of the WireIn 0x00 to 1 or 0 based on the button state
        dp.SetWireInValue(0x00, 0x00000100, 0x0100 )  # assert Latch to 1
        dp.UpdateWireIns()
        time.sleep(0.1)
        dp.SetWireInValue(0x00, 0x00000000, 0x0100 )  # deassert Latch to 0
        dp.UpdateWireIns()


    def sample_hold(self):
        # Implementation for sample/hold functionality
        ## get the button state of the SH button, if it is checked, assert SH to 1, otherwise assert SH to 0
        ## update bit 9 of the WireIn 0x00 to 1 or 0 based on the button state
        if self.sh_button.isChecked():
            dp.SetWireInValue(0x00, 0x00000200, 0x0200 )  # assert SH to 1
        else:
            dp.SetWireInValue(0x00, 0x00000000, 0x0200 )  # assert SH to 0
        dp.UpdateWireIns()


    def update_led_status(self):
        # Implementation for updating LED status based on WireOut values
        dp.UpdateWireOuts()
        ## get values from WireOut 0x20, 0x21, 0x22, 0x23 with 3-bit, 10-bit, 3-bit, 10-bit respectively
        shift_reg_range_out = dp.GetWireOutValue(0x20) & 0x07
        shift_reg_addr_out = dp.GetWireOutValue(0x21) & 0x3FF
        shift_reg_clkcfg_out = dp.GetWireOutValue(0x22) & 0x07
        shift_reg_nodecfg_out = dp.GetWireOutValue(0x23) & 0x3FF

        ## update the range LEDs
        for i in range(3):
            self.range_leds[i].setState((shift_reg_range_out >> i) & 0x01)

        ## update the address LEDs
        for i in range(10):
            self.addr_leds[i].setState((shift_reg_addr_out >> i) & 0x01)

        ## update the clock configuration LEDs
        for i in range(3):
            self.clock_leds[i].setState((shift_reg_clkcfg_out >> i) & 0x01)

        ## update the node configuration LEDs
        for i in range(10):
            self.nodecfg_leds[i].setState((shift_reg_nodecfg_out >> i) & 0x01)

    def spi_load_range(self):
        # Implementation for SPI load range
        ## set mosi_sel to 00, mosi_sel is bits 7:6 of WireIn 0x00
        dp.SetWireInValue(0x00, 0x00000000, 0x00C0)
        dp.UpdateWireIns()
        ## lower nglobals to 0, nglobals is bit 3 of WireIn 0x00
        dp.SetWireInValue(0x00, 0x00000000, 0x0008 )
        ## set the range value to WireIn 0x00
        dp.UpdateWireIns()
        ## Activate the trigger of spi_clk
        for i in range(3):
            ## shift in the MOSI one bit
            dp.ActivateTriggerIn(0x40, 4)
            ## update the MOSI value to the next bit SE0
            dp.ActivateTriggerIn(0x40, 0)
        ## finish the SPI load, set nglobals back to 1
        dp.SetWireInValue(0x00, 0x00000008, 0x0008 )
        dp.UpdateWireIns()


    def spi_load_address(self):
        # Implementation for SPI load address
        ## set mosi_sel to 01, mosi_sel is bits 7:6 of WireIn 0x00
        dp.SetWireInValue(0x00, 0x00000040, 0x00C0)
        dp.UpdateWireIns()
        ## lower nCS to 0, nCS is bit 10 of WireIn 0x01
        dp.SetWireInValue(0x01, 0x00000000, 0x0400 )
        dp.UpdateWireIns()

        # Activate the trigger of spi_clk for 10 bits
        for i in range(10):
            ## shift in the MOSI one bit
            dp.ActivateTriggerIn(0x40, 4)
            ## update the MOSI value to the next bit SE1
            dp.ActivateTriggerIn(0x40, 1)
        ## finish the SPI load, set nCS back to 1
        dp.SetWireInValue(0x01, 0x00000400, 0x0400 )
        dp.UpdateWireIns()

    def spi_load_clock_settings(self):
        # Implementation for SPI load clock settings
        ## set mosi_sel to 10, mosi_sel is bits 7:6 of WireIn 0x00
        dp.SetWireInValue(0x00, 0x00000080, 0x00C0)
        dp.UpdateWireIns()
        ## lower nclk_set to 0, nclk_set is bit 3 of WireIn 0x02
        dp.SetWireInValue(0x02, 0x00000000, 0x0008 )
        dp.UpdateWireIns()
        ## Activate the trigger of spi_clk for 3 bits
        for i in range(3):
            ## shift in the MOSI one bit
            dp.ActivateTriggerIn(0x40, 4)
            ## update the MOSI value to the next bit SE2
            dp.ActivateTriggerIn(0x40, 2)
        ## finish the SPI load, set nclk_set back to 1
        dp.SetWireInValue(0x02, 0x00000008, 0x0008 )
        dp.UpdateWireIns()

    def spi_load_nodecfg_settings(self):
        # Implementation for SPI load node configuration settings
        ## set mosi_sel to 11, mosi_sel is bits 7:6 of WireIn 0x00
        dp.SetWireInValue(0x00, 0x000000C0, 0x00C0)
        dp.UpdateWireIns()
        ## raise node_sw to 1, node_sw is bit 10 of WireIn 0x03
        dp.SetWireInValue(0x03, 0x00000400, 0x0400 )
        dp.UpdateWireIns()
        ## Activate the trigger of spi_clk for 10 bits
        for i in range(10):
            ## shift in the MOSI one bit
            dp.ActivateTriggerIn(0x40, 4)
            ## update the MOSI value to the next bit SE3
            dp.ActivateTriggerIn(0x40, 3)
        ## finish the SPI load, set node_sw back to 0
        dp.SetWireInValue(0x03, 0x00000000, 0x0400 )
        dp.UpdateWireIns()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SteveSPITest()
    window.show()
    sys.exit(app.exec())
