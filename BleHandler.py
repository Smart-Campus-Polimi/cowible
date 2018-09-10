#!/usr/bin/python
from __future__ import print_function
from time import strftime, sleep, localtime
from bluepy.btle import Scanner, DefaultDelegate, BTLEException
import threading
import sys
import pprint as pp

#my imports
import functions as f
import constants as c


global ble_list
ble_list = {}


class ScanDelegate(DefaultDelegate):

	def handleDiscovery(self, dev, isNewDev, isNewData):
		global ble_list
		if not ble_list.has_key(dev.addr):
				ble_list[dev.addr] = \
					{"last_ts": strftime("%H:%M:%S", localtime()), "times_seen": 1, "last_rssi": dev.rssi,"life":c.LIFE_BLE} 
		else:
			ble_list[dev.addr]["times_seen"] += 1 
			ble_list[dev.addr]["last_rssi"] = dev.rssi
			ble_list[dev.addr]["last_ts"] = strftime("%H:%M:%S", localtime())
			ble_list[dev.addr]["life"] = c.LIFE_BLE
			

class BleThread(threading.Thread):

	def __init__(self, queue):
		threading.Thread.__init__(self)
		self.scanner = Scanner().withDelegate(ScanDelegate())
		self.queue = queue
		self.is_running = True



	def run(self):
		while self.is_running:
			# listen for ADV_IND packages for 60.0 (cannot use a variable), then exit
			self.scanner.scan(10.0, passive=True)
			global ble_list
			print("lol")
			#pp.pprint(ble_list)
			self.queue.put(ble_list)
			ble_list = f.decrease_life(ble_list)

	
	def stop(self):
		print("close ble")
		self.is_running = False