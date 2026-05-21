import ok


## Create Front Panel object
dev = ok.okCFrontPanel()

# Open first detected device
if dev.OpenBySerial("") != 0:
    print("Failed to open device")
    exit()

print("Device opened")

# Configure FPGA (optional if already configured)
dev.ConfigureFPGA("Top.bit")

print("LED ON")

# Turn LED ON
dev.SetWireInValue(0x00, 0x0001)
dev.SetWireInValue( 0x01, 0x0001)

# Push WireIns into FPGA
dev.UpdateWireIns()

print("LED now should be off")

input("Press Enter to turn LED BACK ON...")

# Turn LED OFF
dev.SetWireInValue(0x00, 0x0000)
dev.UpdateWireIns()

print("LED should be back ON")