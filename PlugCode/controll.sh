# Connect to TP Link plug
echo "Copying TPLink .conf file..."
sudo cp /home/pi/Documents/wpa_supplicant_TP.conf /etc/wpa_supplicant/wpa_supplicant.conf
sleep 1
sudo wpa_cli -i wlan0 reconfigure
sleep 10

# Turn on plug
echo "Sending command to plug..."
python /home/pi/Documents/tplink-smartplug/tplink_smartplug.py -t 192.168.0.1 -c $1
sleep 1

# Back to AirYorkPLUS
echo "Copying AirYorkPLUS .conf file..."
sudo cp /home/pi/Documents/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf
sleep 1
sudo wpa_cli -i wlan0 reconfigure



