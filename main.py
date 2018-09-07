#!/usr/bin/python

import signal
import sys
import os
import subprocess
import threading
import Queue
import pprint as pp
from time import strftime,localtime

#my imports
import WifiHandler
import BleHandler
import functions as f


'''
	CONSTANTS
'''
BUF_SIZE = 200
LIFE = 2
thread_list = []

'''
	FUNCTIONS
'''
def signal_handler(signal, frame):
	print "Exit!"

	for thread in thread_list:
		thread.stop()
	
	sys.exit(0)


#### MAIN ####
if __name__ == "__main__":
	signal.signal(signal.SIGINT, signal_handler)
	print "COWIBLI v1.0"
	
	f.create_csv()

	q_wifi_probe = Queue.Queue(BUF_SIZE)
	q_ble_advertising = Queue.Queue(BUF_SIZE)

	t_wifi = WifiHandler.WifiThread(q_wifi_probe)
	t_wifi.start() 
	thread_list.append(t_wifi)

	t_ble = BleHandler.BleThread(q_ble_advertising)
	t_ble.start()
	thread_list.append(t_ble)

	client_list = {}
	ble_list = {}


	wifi_flag = False
	ble_flag = False

	while True:
		if not q_wifi_probe.empty():
			client_list = q_wifi_probe.get()
			wifi_flag = True


		if not q_ble_advertising.empty():
			ble_list = q_ble_advertising.get()
			ble_flag = True

		if(wifi_flag and ble_flag):
			random_wifi, valid_wifi, ble_devices = f.count_users(client_list, ble_list)
			print "Random users: ", random_wifi
			print "Valid users: ", valid_wifi
			print "Ble devices: ", ble_devices
			f.update_csv(strftime("%H:%M:%S", localtime()), valid_wifi, random_wifi, ble_devices)

			wifi_flag = False
			ble_flag = False