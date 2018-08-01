#-------------
# 1) Run ntc.py from thr Raspberry Pi to generate ntc_single.out
# 2) Run this script from another machine to produce live plot
#-----------
import paramiko
import sys
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import numpy as np

# Define constants
sleep_time = 0.5  # (sec)
xWindow=60 # (sec)
yWindow=5 # (C)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
		client.connect('yorkdaq.hopto.org', username='pi', password='YorkDAQ')
except paramiko.SSHException:
		print("Connection Failed")
		quit()

sftp_client = client.open_sftp()

remote_file = sftp_client.open('./NTCCode/ntc_single.out')
last_line = remote_file.readline()
scale = last_line.split(',')
xs = float(scale[0])

fig, ax = plt.subplots()
x, y1, y2, y3, y4, y5, hr,dp = [],[],[],[],[],[],[],[]
scy1 = ax.scatter(x,y1,s=5,c='royalblue', marker='o',label='NTC#1')
scy2 = ax.scatter(x,y2,s=5,c='darkgreen', marker='^',label='NTC#2')
scy3 = ax.scatter(x,y3,s=5,c='gold', marker='8',label='NTC#3')
scy4 = ax.scatter(x,y4,s=5,c='m', marker='>',label='NTC#4')

scy5 = ax.scatter(x,y5,s=5,c='silver', marker='s',label='Amb.')
scy7 = ax.scatter(x,dp,s=5,c='black', marker='*',label='dewpoint') #Dewpoint


plt.title('NTC')
plt.ylabel('Temp. [C$^\circ$]')
plt.xlabel('Time [Sec.]')
plt.grid(True)

lgnd=plt.legend(handles=[scy1,scy2,scy3,scy4,scy5,scy7])
lgnd.legendHandles[0]._sizes = [30]
lgnd.legendHandles[1]._sizes = [30]
lgnd.legendHandles[2]._sizes = [30]
lgnd.legendHandles[3]._sizes = [30]
lgnd.legendHandles[4]._sizes = [30]
lgnd.legendHandles[5]._sizes = [30]


# -- Set initial plot's limit
xmin=xs
xmax = xs+100
ymin = -50
ymax = 35
plt.xlim(xmin,xmax)
plt.ylim(ymin,ymax)

def checkPlotLim(x): # this function changes the plot ranges according to the live data
	global xmin, xmax
	if x > xmax-10:
		print("range changed")
		xmax += 1
		xmin += 1
		plt.xlim(xmin,xmax)



def animate(i):
	remote_file = sftp_client.open('./NTCCode/ntc_single.out')
	last_line = remote_file.readline()
	scale = last_line.split(',')
	scale = [float(i) for i in scale]
	xs = scale[0]
	y1s = scale[1]
	y2s = scale[2]
	y3s = scale[3]
	y4s = scale[4]
	y5s = scale[5]
	y7s = scale[7]
	x.append(xs)
	y1.append(y1s)
	y2.append(y2s)
	y3.append(y3s)
	y4.append(y4s)
	y5.append(y5s)
	dp.append(y7s)
	scy1.set_offsets(np.c_[x,y1])
	scy2.set_offsets(np.c_[x,y2])
	scy3.set_offsets(np.c_[x,y3])
	scy4.set_offsets(np.c_[x,y4])
	scy5.set_offsets(np.c_[x,y5])

	scy7.set_offsets(np.c_[x,dp])
	checkPlotLim(xs)

ani = animation.FuncAnimation(fig, animate, frames=2, interval=1000, repeat=True)
plt.show()
