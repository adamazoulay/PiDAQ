import piplates.DAQCplate as DAQC
import time, math, os
import Gpib

# Define constants
B = 3892  # From data sheet of NTCs
R0 = 10000  # (Ohms)
addHV = 1  # GPIB address, set on device

inst = Gpib.Gpib(0, addHV)

# Starting string
inst.write(":DISP:WIND:TEXT:STAT ON")
inst.write(":DISP:WIND2:TEXT:STAT ON")


# Main temp checking loop
while True:

    # Get the temperature from the NTC thermistor
    Vs = DAQC.getADC(0, 8)  # Supply voltage (V)
    # This get the potential from channel 0 on the analog input (V)
    pot = DAQC.getADC(0, 0)

    Rn = R0 * (Vs/pot - 1)  # Derive from KVL, (Ohms)

    # Steinhart equation
    steinhart = Rn / R0  # (R/Ro)
    steinhart = math.log(steinhart)  # ln(R/R0)
    steinhart /= B
    steinhart += 1.0 / (25 + 273.15)  # + (1/T0)
    steinhart = 1.0 / steinhart  # Invert
    steinhart -= 273.15  # Convert to C

    temp = steinhart

    temp_formatted = '%.2f' % temp

    # Display on HV screen
    inst.write(":DISP:WIND2:TEXT:DATA '" + str(temp_formatted) + "'")


    if temp > 30:
    	inst.write(":DISP:WIND:TEXT:DATA 'TOO HOT!!!'")
    else:
    	inst.write(":DISP:WIND:TEXT:DATA 'Help! I'm stuck in a power supply!'")


    time.sleep(0.5) # (s)
