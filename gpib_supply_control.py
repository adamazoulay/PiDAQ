import Gpib

# Helper functions
def query(inst, cmd):
    inst.write(cmd)
    print(inst.read(1024))

def get_vi(inst, channel_num):
    voltages = []
    currents = []
    for channel in range(1, channel_num + 1):
        inst.write("INSTrument:SELect CH" + str(channel))
        inst.write("MEASure:VOLTage?")
        v = inst.read(1024)
        v = float(v.strip('\n'))

        inst.write("MEASure:CURRent?")
        i = inst.read(1024)
        i = float(i.strip('\n'))

        voltages.append(v)
        currents.append(i)

    return [voltages, currents]

def set_vi(inst, voltages, currents):
    for channel in range(1, len(voltages) + 1):
        inst.write("INSTrument:SELect CH" + str(channel))
        inst.write("APPly CH" + str(channel) + "," +
                    str(voltages[channel - 1]) + "," + str(currents[channel - 1]))


# Define constants
addr = 1  # GPIB address, set on device
line_break = "____________________________________"

inst = Gpib.Gpib(0, addr)

# Get device identification and print as debug
query(inst, "*IDN?")

# Set to remote mode
inst.write("SYSTem:REMote")

# Set output to on
inst.write("OUTPUT OFF")

set_vi(inst, ['max','max',0], ['max','max',0])

voltages = get_vi(inst, 3)
print(voltages)

# Turn off output
#inst.write("OUTPUT OFF")
#inst.write("SYSTem:BEEPer")
inst.write("SYSTem:LOCal")
