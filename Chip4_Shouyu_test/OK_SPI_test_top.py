## This is the STEP 1 of the whole chip test where we simply will send address and data
## using SPI protocol and check what we have received is correct.
##
## We have the following Wire in and out to the DUT:
## 0x00 WireIn:
## [7:0] data_in: data to be sent to the SPI slave
## [15:8] addr: address to be sent to the SPI slave
## [16]: rstn_ok: reset signal for the SPI master
##
## 0x20 WireOut:
## [7:0] data_out: data received from the SPI slave
## [8]: done: indicates that the SPI transaction is done
##
## 0x40 TriggerIn:
## [0]: send_SPI: trigger to start the SPI transaction


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

'''
devices = ok.FrontPanelDevices()
dev = devices.Open()

if dev is None:
    raise RuntimeError("Failed to open FrontPanel device")

result = dev.ConfigureFPGA("OK_SPI_test_top.bit")

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

## initialise the WireIn 0x00 with the following values
## [7:0] data_in: 0x00
## [15:8] addr: 0x00
## [16]: rstn_ok: 0x0

dp.SetWireInValue(0x00, 0x00000000)  # rstn_ok = 0, addr = 0x00, data_in = 0x00

dp.UpdateWireIns()

## finish reset of the FPGA by setting rstn_ok = 1
dp.SetWireInValue(0x00, 0x00010000)  # rstn_ok = 1, addr = 0x00, data_in = 0x00

dp.UpdateWireIns()
'''

class SPI_Test_Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SPI Test")
        self.setGeometry(100, 100, 400, 300)

        # Create a vertical layout
        overall_layout = QVBoxLayout()

        # PLL and LVDS config boxes on a horizontal layout
        config_layout = QHBoxLayout()
        ####################################
        ## create a group box for PLL config
        pll_group_box = QGroupBox("PLL Config")
        pll_layout = QVBoxLayout()
        ## 3 tick boxes for PLL config
        pll_tick_box_layout = QHBoxLayout()
        self.pll_test_checkbox = QCheckBox("PLL Test Mode")
        self.pll_frange_checkbox = QCheckBox("PLL Frequency Range")
        self.pll_enable_checkbox = QCheckBox("Enable PLL")
        pll_tick_box_layout.addWidget(self.pll_test_checkbox)
        pll_tick_box_layout.addWidget(self.pll_frange_checkbox)
        pll_tick_box_layout.addWidget(self.pll_enable_checkbox)

        pll_layout.addLayout(pll_tick_box_layout)
        ## create a horizontal layout for MS and NS value input
        pll_ms_ns_value_layout = QHBoxLayout()
        self.pll_ms_label = QLabel("MS Value:")
        self.pll_ms_input = QLineEdit()
        self.pll_ns_label = QLabel("NS Value:")
        self.pll_ns_input = QLineEdit()
        pll_ms_ns_value_layout.addWidget(self.pll_ms_label)
        pll_ms_ns_value_layout.addWidget(self.pll_ms_input)
        pll_ms_ns_value_layout.addWidget(self.pll_ns_label)
        pll_ms_ns_value_layout.addWidget(self.pll_ns_input)

        pll_layout.addLayout(pll_ms_ns_value_layout)

        ## add a button to set the PLL config
        self.pll_set_button = QPushButton("Set PLL Config")
        self.pll_set_button.clicked.connect(self.set_pll_config_spi)
        pll_layout.addWidget(self.pll_set_button)

        pll_group_box.setLayout(pll_layout)
        config_layout.addWidget(pll_group_box)

        ####################################
        ## create a group box for LVDS config
        lvds_group_box = QGroupBox("LVDS Config")
        lvds_layout = QVBoxLayout()

        ## create a horizontal layout for LVDS tick boxes config
        lvds_tick_box_layout = QHBoxLayout()
        self.lvds_RS_checkbox = QCheckBox("LVDS Test Mode")
        self.lvds_enable_checkbox = QCheckBox("Enable LVDS")
        lvds_tick_box_layout.addWidget(self.lvds_RS_checkbox)
        lvds_tick_box_layout.addWidget(self.lvds_enable_checkbox)

        ## add a button to set the LVDS config
        self.lvds_set_button = QPushButton("Set LVDS Config")
        self.lvds_set_button.clicked.connect(self.set_lvds_config_spi)
        lvds_layout.addLayout(lvds_tick_box_layout)
        lvds_layout.addWidget(self.lvds_set_button)

        lvds_group_box.setLayout(lvds_layout)
        config_layout.addWidget(lvds_group_box)

        ## update the overall window layout
        overall_layout.addLayout(config_layout)


        # move on to the channel config boxes on a horizontal layout
        channel_config_layout = QHBoxLayout()

        #####################################
        ## channel 0 config box
        channel0_group_box = QGroupBox("Channel 0 Config")
        channel0_layout = QVBoxLayout()

        # horizontal layout for channel 0 tick box and mask value input
        channel0_tick_mask_layout = QHBoxLayout()
        self.channel0_enable_checkbox = QCheckBox("Channel 0 enable")
        self.channel0_mask_20_to_16_label = QLabel("Mask(20-16):")
        self.channel0_mask_20_to_16_input = QLineEdit()
        self.channel0_mask_15_to_11_label = QLabel("Mask(15-11):")
        self.channel0_mask_15_to_11_input = QLineEdit()
        self.channel0_mask_10_to_6_label = QLabel("Mask(10-6):")
        self.channel0_mask_10_to_6_input = QLineEdit()
        self.channel0_mask_5_to_1_label = QLabel("Mask(5-1):")
        self.channel0_mask_5_to_1_input = QLineEdit()
        channel0_tick_mask_layout.addWidget(self.channel0_enable_checkbox)
        channel0_tick_mask_layout.addWidget(self.channel0_mask_20_to_16_label)
        channel0_tick_mask_layout.addWidget(self.channel0_mask_20_to_16_input)
        channel0_tick_mask_layout.addWidget(self.channel0_mask_15_to_11_label)
        channel0_tick_mask_layout.addWidget(self.channel0_mask_15_to_11_input)
        channel0_tick_mask_layout.addWidget(self.channel0_mask_10_to_6_label)
        channel0_tick_mask_layout.addWidget(self.channel0_mask_10_to_6_input)
        channel0_tick_mask_layout.addWidget(self.channel0_mask_5_to_1_label)
        channel0_tick_mask_layout.addWidget(self.channel0_mask_5_to_1_input)

        channel0_layout.addLayout(channel0_tick_mask_layout)

        # add a horizontal layout for channel 0 FIFO status
        channel0_fifo_status_layout = QHBoxLayout()
        self.channel0_fifo_empty_label = QLabel("Channel 0 FIFO Empty:")
        ## text box to display the FIFO empty value
        self.channel0_fifo_empty_value = QLineEdit()
        self.channel0_fifo_empty_value.setReadOnly(True)
        self.channel0_fifo_full_label = QLabel("Channel 0 FIFO Full:")
        ## text box to display the FIFO full value
        self.channel0_fifo_full_value = QLineEdit()
        self.channel0_fifo_full_value.setReadOnly(True)
        channel0_fifo_status_layout.addWidget(self.channel0_fifo_empty_label)
        channel0_fifo_status_layout.addWidget(self.channel0_fifo_empty_value)
        channel0_fifo_status_layout.addWidget(self.channel0_fifo_full_label)
        channel0_fifo_status_layout.addWidget(self.channel0_fifo_full_value)

        channel0_layout.addLayout(channel0_fifo_status_layout)

        ## add 2 buttons to set the channel 0 config and read the channel 0 FIFO status
        self.channel0_set_button = QPushButton("Set Channel 0 Config")
        self.channel0_set_button.clicked.connect(self.set_channel0_config_spi)
        self.channel0_read_fifo_button = QPushButton("Read Channel 0 FIFO Status")
        self.channel0_read_fifo_button.clicked.connect(self.read_channel0_fifo_status_spi)
        channel0_layout.addWidget(self.channel0_set_button)
        channel0_layout.addWidget(self.channel0_read_fifo_button)

        channel0_group_box.setLayout(channel0_layout)
        # this includes the channel 0 config box and also the 60-bit counter config box
        channel_config_layout.addWidget(channel0_group_box)

        #####################################
        ## 60-bit counter config box
        stimuli_cnt_box = QGroupBox("60-bit counter driver Config")

        stimuli_box_layout = QVBoxLayout()
        ## get 3 boxes to input values for STEP, MIN and MAX
        input_value_boxes_layout = QHBoxLayout()
        self.CNT_STEP_LABEL = QLabel("Inc step:")
        self.CNT_STEP_VALUE = QLineEdit()
        self.CNT_MIN_LABEL = QLabel("Inc MIN:")
        self.CNT_MIN_VALUE = QLineEdit()
        self.CNT_MAX_LABEL = QLabel("Inc MAX:")
        self.CNT_MAX_VALUE = QLineEdit()
        input_value_boxes_layout.addWidget(self.CNT_STEP_LABEL)
        input_value_boxes_layout.addWidget(self.CNT_STEP_VALUE)
        input_value_boxes_layout.addWidget(self.CNT_MIN_LABEL)
        input_value_boxes_layout.addWidget(self.CNT_MIN_VALUE)
        input_value_boxes_layout.addWidget(self.CNT_MAX_LABEL)
        input_value_boxes_layout.addWidget(self.CNT_MAX_VALUE)

        ## get a tick box for modulo enable and a button for freeze
        stimuli_tick_and_button_layout = QHBoxLayout()
        self.modulo_enable_tick_box = QCheckBox("Modulo enable:")
        self.freeze_button = QPushButton("FREEZE")
        self.freeze_button.setCheckable(True)
        self.freeze_button.setChecked(False)
        self.freeze_button.clicked.connect(self.freeze_increment_spi)
        stimuli_tick_and_button_layout.addWidget(self.modulo_enable_tick_box)
        stimuli_tick_and_button_layout.addWidget(self.freeze_button)

        stimuli_box_layout.addLayout(input_value_boxes_layout)
        stimuli_box_layout.addLayout(stimuli_tick_and_button_layout)
        ## add a button to apply the 60-bit counter config
        self.apply_stimuli_config_button = QPushButton("Apply 60-bit counter config")
        self.apply_stimuli_config_button.clicked.connect(self.apply_stimuli_config_spi)
        stimuli_box_layout.addWidget(self.apply_stimuli_config_button)
        stimuli_cnt_box.setLayout(stimuli_box_layout)

        channel_config_layout.addWidget(stimuli_cnt_box)

        ## update overall layout
        overall_layout.addLayout(channel_config_layout)

        ## a simple horizontal layout for 3 boxes to display ADDR and DATA out and DATA in
        ADDR_DATA_layout =  QHBoxLayout()
        self.ADDR_from_SPI_label = QLabel("ADDR:")
        ## text box to display the FIFO empty value
        self.ADDR_from_SPI_value = QLineEdit()
        self.ADDR_from_SPI_value.setReadOnly(True)
        ADDR_DATA_layout.addWidget(self.ADDR_from_SPI_label)
        ADDR_DATA_layout.addWidget(self.ADDR_from_SPI_value)
        ## data to be sent to SPI
        self.DATAOUT_from_SPI_label = QLabel("DATAOUT:")
        self.DATAOUT_from_SPI_value = QLineEdit()
        self.DATAOUT_from_SPI_value.setReadOnly(True)
        ADDR_DATA_layout.addWidget(self.DATAOUT_from_SPI_label)
        ADDR_DATA_layout.addWidget(self.DATAOUT_from_SPI_value)
        ## data read in from SPI
        self.DATAIN_from_SPI_label = QLabel("DATAIN:")
        self.DATAIN_from_SPI_value = QLineEdit()
        self.DATAIN_from_SPI_value.setReadOnly(True)
        ADDR_DATA_layout.addWidget(self.DATAIN_from_SPI_label)
        ADDR_DATA_layout.addWidget(self.DATAIN_from_SPI_value)

        ## update overall layout
        overall_layout.addLayout(ADDR_DATA_layout)

        #####################################
        ## A very simple box to list chip info
        CHIP_INFO_BOX =  QGroupBox("Chip Info")
        CHIP_INFO_BOX_layout = QHBoxLayout()
        self.chip_id_label =  QLabel("Chip ID:")
        self.chip_id_value = QLineEdit()
        self.chip_id_value.setReadOnly(True)
        self.chip_signature_label = QLabel("Chip Signature:")
        self.chip_signature_value = QLineEdit()
        self.chip_signature_value.setReadOnly(True)
        CHIP_INFO_BOX_layout.addWidget(self.chip_id_label)
        CHIP_INFO_BOX_layout.addWidget(self.chip_id_value)
        CHIP_INFO_BOX_layout.addWidget(self.chip_signature_label)
        CHIP_INFO_BOX_layout.addWidget(self.chip_signature_value)
        CHIP_INFO_BOX.setLayout(CHIP_INFO_BOX_layout)

        ## update overall layout
        overall_layout.addWidget(CHIP_INFO_BOX)


        self.setLayout(overall_layout)



    def send_SPI_command(self, addr:int, data: int):
        ## both addr and data should be bytes
        ## set 0x00 WireIn [15:0] with addr and data
        ## TODO: uncomment the following lines when the FPGA is ready to receive SPI commands
        WireInValue =  (addr << 8) | data
        print(f"Sending SPI command: addr = {addr:#04x}, data = {data:#04x}, WireInValue = {WireInValue:#06x}")
        ## check if the SPI module is ready to receive and send the command, if not, wait for a while and check again
        ## check WIreOut 0x20 [8] done bit, if it is 1, then the SPI module is ready to receive and send the command
        '''
        dp.UpdateWireOuts()
        done_bit = dp.GetWireOutValue(0x20) & 0x100
        ## set a timeout for waiting for the SPI module to be ready, if it is not ready after 1 second, raise an error
        timeout = 1.0
        start_time = time.time()
        while done_bit == 0:
            dp.UpdateWireOuts()
            done_bit = dp.GetWireOutValue(0x20) & 0x100
            if time.time() - start_time > timeout:
                raise RuntimeError("Timeout waiting for SPI module to be ready")
        print("SPI module is ready")
        
        ## only update the lsb 16
        dp.SetWireInValue(0x00, WireInValue, 0xFFFF)
        ## update wire in ports
        dp.UpdateWireIns()
        ## send a trigger to start the sequence
        dp.ActivateTriggerIn(0x40, 0)
        '''

    def read_SPI_response(self, addr:int):
        ## TODO: uncomment the following lines when the FPGA is ready to receive SPI commands
        ## read the response from the SPI module, but we need to send the addr first
        ## addr[7] = 1 for read
        self.send_SPI_command(addr | 0x80, 0)
        ## check WIreOut 0x20 [8] done bit, if it is 1, then the SPI module is ready to send the response
        '''
        dp.UpdateWireOuts()
        done_bit = dp.GetWireOutValue(0x20) & 0x100
        ## set a timeout for waiting for the SPI module to be ready, if it is not ready after 1 second, raise an error
        timeout = 1.0
        start_time = time.time()
        while done_bit == 0:
            dp.UpdateWireOuts()
            done_bit = dp.GetWireOutValue(0x20) & 0x100
            if time.time() - start_time > timeout:
                raise RuntimeError("Timeout waiting for SPI module to be ready")
        print("SPI module is ready to send response")
        ## read the response from WireOut 0x20 [7:0]
        dp.UpdateWireOuts()
        data_out = dp.GetWireOutValue(0x20) & 0xFF
        print(f"Received SPI response: addr = {addr:#04x}, data = {data_out:#04x}")
        return data_out
        '''

    def set_pll_config_spi(self):
        ## To set PLL config, we need both addr and data, first of all addr[7] = 0, addr[6:3] = 0001
        ## Set the overall config at addr [2:0] = 000
        pll_test_setting = self.pll_test_checkbox.isChecked()
        pll_frange_setting =  self.pll_frange_checkbox.isChecked()
        pll_enable_setting = self.pll_enable_checkbox.isChecked()
        pll_bypass = 0
        ## set up pll config with only the low 4 bits, set the high 4 bits with 0
        pll_cfg_dat = (pll_test_setting << 3) | (pll_frange_setting << 2) | (pll_bypass << 1) | (pll_enable_setting) | 0x00
        pll_cfg_addr = 0x08
        self.send_SPI_command(pll_cfg_addr, pll_cfg_dat)
        ## set up the MS value at 0000_1001 ==> 0x09
        MS_value = int(self.pll_ms_input.text())
        ## sanity check for MS value to be in the range of 0-63
        if MS_value <= 0 or MS_value > 63:
            QMessageBox.warning(self, "Warning", "MS value should be in the range of 0-63")
            return
        MS_value = MS_value | 0x00 ## make sure it is 8 bits
        self.send_SPI_command(0x09, MS_value)
        ## set up the NS value at 0000_1010 ==> 0x0A
        NS_value = int(self.pll_ns_input.text())
        ## sanity check for NS value to be in the range of 0-63
        if NS_value <= 0 or NS_value > 63:
            QMessageBox.warning(self, "Warning", "NS value should be in the range of 0-63")
            return
        NS_value = NS_value | 0x00 ## make sure it is 8 bits
        self.send_SPI_command(0x0A, NS_value)



    def set_lvds_config_spi(self):
        # Similarly to PLL config, we only need to set the addr[7] = 0, addr[6:3] = 0010, and addr[2:0] = 000 for overall config
        lvds_RS_setting = self.lvds_RS_checkbox.isChecked()
        lvds_enable_setting = self.lvds_enable_checkbox.isChecked()
        lvds_cfg_dat = (lvds_RS_setting << 1) | (lvds_enable_setting) | 0x00
        lvds_cfg_addr = 0x10
        self.send_SPI_command(lvds_cfg_addr, lvds_cfg_dat)



    def set_channel0_config_spi(self):
        # Channel 0 address is addr[7] = 0, addr[6:3] = 1000, addr[2:0] = 000 for channel enable
        # addr [2:0] = 001 for mask[7:0], addr [2:0] = 010 for mask[15:8], addr [2:0] = 011 for mask[19:16]
        channel0_enable_setting = self.channel0_enable_checkbox.isChecked()
        channel0_enable_addr = 0x20
        channel0_enable_dat = channel0_enable_setting & 0x01
        self.send_SPI_command(channel0_enable_addr, channel0_enable_dat)
        # set the mask by sequence of 3 SPI commands
        channel0_mask_20_to_16 = int(self.channel0_mask_20_to_16_input.text())
        channel0_mask_15_to_11 = int(self.channel0_mask_15_to_11_input.text())
        channel0_mask_10_to_6 = int(self.channel0_mask_10_to_6_input.text())
        channel0_mask_5_to_1 = int(self.channel0_mask_5_to_1_input.text())
        ## sanity check for mask values to be in the range of 0-31
        if channel0_mask_20_to_16 < 0 or channel0_mask_20_to_16 > 31 or channel0_mask_15_to_11 < 0 or channel0_mask_15_to_11 > 31 or channel0_mask_10_to_6 < 0 or channel0_mask_10_to_6 > 31 or channel0_mask_5_to_1 < 0 or channel0_mask_5_to_1 > 31:
            QMessageBox.warning(self, "Warning", "Mask values should be in the range of 0-31")
            return
        # Send the mask values as SPI commands
        concat_mask = (channel0_mask_20_to_16 << 15) | (channel0_mask_15_to_11 << 10) | (channel0_mask_10_to_6 << 5) | (channel0_mask_5_to_1)
        mask_19_16 = (concat_mask >> 16) & 0x0F
        mask_15_8 = (concat_mask >> 8) & 0xFF
        mask_7_0 = concat_mask & 0xFF
        self.send_SPI_command(0x21, mask_7_0)
        self.send_SPI_command(0x22, mask_15_8)
        self.send_SPI_command(0x23, mask_19_16)


    def read_channel0_fifo_status_spi(self):
        # for channel 0 fifo status, the addr[6:3] = 1000, addr[2:0] = 100.
        FIFO_stats = self.read_SPI_response(0x24)
        ## top 4 bits of the returned data is fifo empty and low 4 bits is fifo full.
        fifo_empty = (FIFO_stats >> 4) & 0x0F
        fifo_full = FIFO_stats & 0x0F
        ## update the text boxes to display the fifo empty and full values
        self.channel0_fifo_empty_value.setText(str(fifo_empty))
        self.channel0_fifo_full_value.setText(str(fifo_full))

    def apply_stimuli_config_spi(self):
        # for 60-bit counter config, the addr[6:3] = 1010
        step_value = int(self.CNT_STEP_VALUE.text())
        min_value = int(self.CNT_MIN_VALUE.text())
        max_value = int(self.CNT_MAX_VALUE.text())
        modulo_enable = self.modulo_enable_tick_box.isChecked()
        ## sanity check for step, min and max values to be in the range of 0-63
        if step_value < 0 or step_value > 63 or min_value < 0 or min_value > 63 or max_value < 0 or max_value > 63:
            QMessageBox.warning(self, "Warning", "Step, Min and Max values should be in the range of 0-63")
            return
        ## concat the step, min and max into a single 20-bit value, step[19:14], module_enable[13], min[12:7], max[6:1], 1[0]
        stimuli_config = (step_value << 14) | (modulo_enable << 13) | (min_value << 7) | (max_value << 1) | 0x01
        ## the addr[2:0] = 001 for stimuli_config[7:0], addr[2:0] = 010 for stimuli_config[15:8], addr[2:0] = 011 for stimuli_config[19:16]
        stimuli_config_7_0 = stimuli_config & 0xFF
        stimuli_config_15_8 = (stimuli_config >> 8) & 0xFF
        stimuli_config_19_16 = (stimuli_config >> 16) & 0x0F
        self.send_SPI_command(0x29, stimuli_config_7_0)
        self.send_SPI_command(0x2A, stimuli_config_15_8)
        self.send_SPI_command(0x2B, stimuli_config_19_16)


    def freeze_increment_spi(self):
        # for freeze increment, it only takes one bit in stimuli_config[0]
        # so we should first read the current stimuli_config[7:0] from addr 0x29, then set the bit 0 to 1 for freeze, and write it back to addr 0x29
        stimuli_config_7_0 = self.read_SPI_response(0x29)
        if self.freeze_button.isChecked():
            stimuli_config_7_0 |= 0x01
        else:
            stimuli_config_7_0 &= 0xFE
        self.send_SPI_command(0x29, stimuli_config_7_0)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SPI_Test_Window()
    window.show()
    sys.exit(app.exec())