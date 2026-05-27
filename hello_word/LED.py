import ok

# -------------------------------------------------------------------
# FrontPanel 6.0 Initialization
# -------------------------------------------------------------------

devices = ok.FrontPanelDevices()

# Open first detected device
dev = devices.Open()

if dev is None:
    print("Failed to open device")
    exit()

print("Device opened")

# Configure FPGA
result = dev.ConfigureFPGA("Top.bit")

if result != ok.ErrorCode.NoError:
    print(f"FPGA configuration failed: {dev.GetErrorMessage(result)}")
    exit()

# Check FrontPanel support
if not dev.IsFrontPanelEnabled():
    print("FrontPanel support is not enabled")
    exit()

# Obtain FP6 Classic Data Port
dp = dev.GetFPGADataPortClassic()

print("LED ON")

# Turn LED ON
dp.SetWireInValue(0x00, 0x0001)
dp.SetWireInValue(0x01, 0x0001)

# Push WireIns into FPGA
dp.UpdateWireIns()

print("LED now should be off")

input("Press Enter to turn LED BACK ON...")

# Turn LED OFF
dp.SetWireInValue(0x00, 0x0000)
dp.UpdateWireIns()

print("LED should be back ON")