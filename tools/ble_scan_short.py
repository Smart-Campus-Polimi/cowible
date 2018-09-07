#!/usr/bin/python
from __future__ import print_function

from time import strftime, sleep, localtime
from bluepy.btle import Scanner, DefaultDelegate, BTLEException
import pprint as pp
import sys

global ble_list
ble_list = {}

LIFE = 2

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
			
		sys.stdout.flush()

scanner = Scanner().withDelegate(ScanDelegate())

# listen for ADV_IND packages for 10s, then exit
scanner.scan(10.0, passive=True)

print("lol")
pp.pprint(ble_list)