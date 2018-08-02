import os, time

# Connect to TP Link plug
print("Copying TPLink .conf file...")
os.system("sudo cp /home/pi/Documents/wpa_supplicant_TP.conf /etc/wpa_supplicant/wpa_supplicant.conf")
time.sleep(1)
os.system("sudo wpa_cli -i wlan0 reconfigure")

# Wait for IP
return_txt = ''
while return_txt == '':
    fin, fout = os.popen4("ifconfig | grep 192.168.0.")
    return_txt = fout.read()
    time.sleep(1)


# Turn on plug
os.system("python /home/pi/Documents/tplink-smartplug/tplink_smartplug.py -t 192.168.0.1 -c on")

time.sleep(2.5)
# Back to AirYorkPLUS
print("Copying AirYorkPLUS .conf file...")
os.system("sudo cp /home/pi/Documents/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf")
time.sleep(10)
os.system("sudo wpa_cli -i wlan0 reconfigure")


