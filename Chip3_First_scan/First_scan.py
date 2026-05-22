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

dev = ok.okCFrontPanel()
dev.OpenBySerial("")
'''TODO: Change this into the real bitstream file'''
dev.ConfigureFPGA("Top.bit")

