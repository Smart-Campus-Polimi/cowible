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
import BtClassicHandler
import functions as f
import constants as c


'''
	CONSTANTS
'''
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
	
	path = f.create_csv()

	q_wifi_probe = Queue.Queue(c.BUF_SIZE)
	q_ble_advertising = Queue.Queue(c.BUF_SIZE)
	q_bt_inquiry = Queue.Queue(c.BUF_SIZE)

	t_wifi = WifiHandler.WifiThread(q_wifi_probe)
	t_wifi.start() 
	thread_list.append(t_wifi)

	t_ble = BleHandler.BleThread(q_ble_advertising)
	t_ble.start()
	thread_list.append(t_ble)

	t_bt = BtClassicHandler.BtClassicThread(q_bt_inquiry)
	t_bt.start()
	thread_list.append(t_bt)

	client_list = {}
	ble_list = {}
	bt_list = {}


	wifi_flag = False
	ble_flag = False
	bt_flag = False

	while True:
		if not q_wifi_probe.empty():
			client_list = q_wifi_probe.get()
			wifi_flag = True


		if not q_ble_advertising.empty():
			ble_list = q_ble_advertising.get()
			ble_flag = True

		if not q_bt_inquiry.empty():
			bt_list = q_bt_inquiry.get()
			bt_flag = True

		if(wifi_flag and ble_flag and bt_flag):
			random_wifi, valid_wifi, ble_devices, bt_devices = f.count_users(client_list, ble_list, bt_list)
			print "Random users: ", random_wifi
			print "Valid users: ", valid_wifi
			print "Ble devices: ", ble_devices
			print "Classic BT devices: ", bt_devices
			
			non_random_wifi, random_wifi = f.split_random(client_list)
			timestamp = strftime("%H:%M:%S", localtime())

			f.final_csv(path, timestamp, [non_random_wifi, random_wifi, ble_list, bt_list])
			f.update_csv(path, timestamp, valid_wifi, random_wifi, ble_devices, bt_devices)

			wifi_flag = False
			ble_flag = False
			bt_flag = False