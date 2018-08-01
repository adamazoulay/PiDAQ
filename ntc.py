import piplates.DAQCplate as DAQC
import time, math, os, datetime
import RPi.GPIO as GPIO
import dht11
import dewpoint_cal
from influxdb import InfluxDBClient

# initialize GPIO
#GPIO.setwarnings(False)
#GPIO.setmode(GPIO.BCM)
#GPIO.cleanup()

# Define constants
B = 3892  # From data sheet of NTCs
R0 = 10000  # (Ohms)
sleep_time = 1  # (s)
steinhart = 0  # (degrees C)
dew_point = 0
t0 = time.time()

# read data using pin 17 (this is GPIO pin name!!)
instance = dht11.DHT11(pin=17)

now = datetime.datetime.now()
year = now.year
month = now.month
day = now.day
hour = now.hour
min = now.minute
sec = now.second

out_subdir = "outputs"
try:
    os.mkdir(out_subdir)
except Exception:
    pass

output_file_single = 'ntc_single.out'
output_file = 'ntc_%d-%d-%d_%d-%d.out' % (year, month, day, hour, min)

# Connect to DB, us admin, pw '', db 'temps'
client = InfluxDBClient('localhost', 8086, 'admin', '', 'readings')

result = instance.read()
humidity_old = result.humidity

# Start main loop
while True:
    Vs = DAQC.getADC(0, 8)  # Supply voltage (V)
    pot1 = DAQC.getADC(0, 0)  # This get the potential from channel 0 on the analog input (V)
    pot2 = DAQC.getADC(0, 1)
    pot3 = DAQC.getADC(0, 2)
    pot4 = DAQC.getADC(0, 3)
    pot5 = DAQC.getADC(0, 4)

    pots = [pot1, pot2, pot3, pot4, pot5]
    temps = []

    for pot in pots:
        Rn = R0 * (Vs/pot - 1)  # Derive from KVL, (Ohms)

        # Steinhart equation
        steinhart = Rn / R0  # (R/Ro)
        steinhart = math.log(steinhart)  # ln(R/R0)
        steinhart /= B
        steinhart += 1.0 / (25 + 273.15)  # + (1/T0)
        steinhart = 1.0 / steinhart  # Invert
        steinhart -= 273.15  # Convert to C

        temp = steinhart
        temps.append(temp)

    now = time.time()
    result = instance.read()
    if result.humidity == 0:
        result.humidity = humidity_old
    else:
        result_old = result.humidity
	

    ambient_temp = temps[4]
    dew_point_old = dew_point
    dew_point = dewpoint_cal.dewpoint_approximation(ambient_temp, result.humidity)
    if dew_point == 999:
        dew_point = dew_point_old

    with open(os.path.join(out_subdir,output_file), 'a', buffering=20*(1024**2)) as outFile:
        outFile.write("%5.1f,%5.1f,%5.1f,%5.1f,%5.1f, %5.1f,%5.1f,%5.1f \n" % (now-t0,temps[0], temps[1], temps[2], temps[3], temps[4], result.humidity, dew_point))
    with open(output_file_single, 'w') as out_file_single:
        out_file_single.write("%5.1f,%5.1f,%5.1f,%5.1f,%5.1f,%5.1f,%5.1f,%5.1f " % (now-t0,temps[0], temps[1], temps[2], temps[3], temps[4], result.humidity, dew_point))

    print("%5.1f,%5.1f,%5.1f,%5.1f,%5.1f,%5.1f, rh.:%5.0f %%, Dp.:%5.1f C" % (now-t0,temps[0], temps[1], temps[2], temps[3], temps[4], result.humidity, dew_point))

    # Write temps to DB for grafana
    json_body = [
        {
            "measurement": "ntcs",
            "tags": {
                "type": "temperature"
            },
            "time": datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
            "fields": {
                "ntc1": float(temps[0]),
                "ntc2": float(temps[1]),
                "ntc3": float(temps[2]),
                "ntc4": float(temps[3]),
                "ntc5": float(temps[4]),
                "dewpoint": float(dew_point),
		"humidity": float(result.humidity)
            }
        }
    ]
    status = client.write_points(json_body)
    print(status)
    time.sleep(sleep_time)
