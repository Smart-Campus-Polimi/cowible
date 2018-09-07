#!/usr/bin/python
from __future__ import print_function

from time import strftime, sleep, localtime
from bluepy.btle import Scanner, DefaultDelegate, BTLEException
import threading
import pprint as pp
import sys

global ble_list
ble_list = {}

LIFE = 2

def decrease_life(my_client_list):
	print("decrease users' life")
	for key, val in my_client_list.items():
		val["life"] -= 1

		if val["life"] < 0:
			try:
				my_client_list.pop(key)
			except KeyError as e:
				print(e)


	return my_client_list

class ScanDelegate(DefaultDelegate):

	def handleDiscovery(self, dev, isNewDev, isNewData):
		ts = strftime("%H:%M:%S", localtime())

		global ble_list
		if not ble_list.has_key(dev.addr):
				ble_list[dev.addr] = \
					{"last_ts": ts, "times_seen": 1, "last_rssi": str(dev.rssi),"life":LIFE} 
		else:
			ble_list[dev.addr]["times_seen"] += 1 
			ble_list[dev.addr]["last_rssi"] = str(dev.rssi)
			ble_list[dev.addr]["last_ts"] = ts
			ble_list[dev.addr]["life"] = LIFE
			
		#sys.stdout.flush()

class BleThread(threading.Thread):

	def __init__(self, queue):
		threading.Thread.__init__(self)
		scanner = Scanner().withDelegate(ScanDelegate())


	def run:
		while True:
			# listen for ADV_IND packages for 10s, then exit
			scanner.scan(10.0, passive=True)

			print("lol")
			pp.pprint(ble_list)
			ble_list = decrease_life(ble_list)