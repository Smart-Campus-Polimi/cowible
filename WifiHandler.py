#!/usr/bin/python

import threading
import subprocess
from time import strftime, localtime

#my imports
import functions as f
import constants as c



'''
	FUNCTIONS
'''
def parse_file(file_path, my_client_list):
	#print "loading from ", file_path
	lines = [line.rstrip('\n') for line in open(file_path[:-1])] #load the file

	load_dict(lines, my_client_list) #manipulate the data // fill the dict

	return my_client_list

'''
	create the dictionary of the client
	one key for each unique mac address
'''
def load_dict(probe_list, my_client_list):
	for probe in probe_list:
		probe = probe.split(';') 	#create the list of single probe
		ts, mac_resolved, mac_addr, rssi, ssid = probe #unpack the list 
		try:
			rssi = int(rssi)
		except ValueError as e:
			print e, rssi
			continue

		#remove LAP in vendor
		if ":" in mac_resolved[:-9]:
			mac_resolved = "unknown"
		else: 
			mac_resolved = mac_resolved[:-9]

		#create the mac field
		if not my_client_list.has_key(mac_addr):
				my_client_list[mac_addr] = \
					{"last_ts": ts[13:-15], "times_seen": 1, "last_rssi": rssi, "vendor": mac_resolved, "ssid": [ssid], "life":c.LIFE_WIFI} 
		else:
			my_client_list[mac_addr]["times_seen"] += 1 
			my_client_list[mac_addr]["last_rssi"] = rssi
			my_client_list[mac_addr]["last_ts"] = ts[13:-15]
			my_client_list[mac_addr]["life"] = c.LIFE_WIFI
			#the ssid field is skippable
			if ssid not in my_client_list[mac_addr]["ssid"]:
				my_client_list[mac_addr]["ssid"].append(ssid)
				my_client_list[mac_addr]["ssid"] = filter(None, my_client_list[mac_addr]["ssid"]) #delete last field if it's empty (no ssid inside probe)

	return my_client_list

class WifiThread(threading.Thread):
	def __init__(self, queue):
		threading.Thread.__init__(self)
		self.queue = queue
		self.is_running = True
		self.client_list = {}


	def run(self):
		print "asd"
		while self.is_running:
			self.wifi_path = subprocess.check_output(['./tools/tshark.sh', strftime("%y%m%d", localtime()), str(c.TIMEOUT)])
			print self.wifi_path
			self.client_list = parse_file(self.wifi_path, self.client_list)
			self.queue.put(self.client_list)
			self.client_list = f.decrease_life(self.client_list)

	def stop(self):
		print "close wifi"
		self.is_running = False
		subprocess.Popen(['killall', 'tshark'])

	