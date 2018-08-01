from influxdb import InfluxDBClient
import time, math, os, datetime 
filename = "ntc_2018-7-20_13-6.out" 
start = "2018-07-20T"
hours = 13
mins = 6
sec = 0

with open(filename, 'r') as file:
    # Connect to DB, us admin, pw '', db 'temps'
    client = InfluxDBClient('localhost', 8086, 'admin', '', 'readings')

    for line in file:
        line = line.split(',')
        time = float(line[0])
        min_add = math.floor(time/60)
        sec_add = time%60
        time_str = str(hours)+":"+str(mins + min_add)+":"+str(sec + sec_add) + "Z"
        final = start + time_str
        
        
        # Write temps to DB for grafana
        json_body = [
            {
                "measurement": "ntcs",
                "tags": {
                    "type": "temperature"
                },
                "time": final,
                "fields": {
                    "ntc1": float(line[1]),
                    "ntc2": float(line[2]),
                    "ntc3": float(line[3]),
                    "ntc4": float(line[4]),
                    "ntc5": float(line[5]),
                    "dewpoint": float(line[7])
                }
            }
        ]

        status = client.write_points(json_body)
        print(status)
