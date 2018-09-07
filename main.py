#!/usr/bin/python

import signal
import time
import sys
import os
import subprocess
import threading
import Queue
import csv
import sched, time
import pprint as pp

#my imports
import WifiHandler

'''
	CONSTANTS
'''
BUF_SIZE = 200
LIFE = 2

'''
	FUNCTIONS
'''
def signal_handler(signal, frame):
	print "Exit!"

	t_wifi.stop()

	
	sys.exit(0)


def decrease_life(my_client_list):
	print "decrease users' life"
	for key, val in client_list.items():
		val["life"] -= 1

		if val["life"] < 0:
			try:
				my_client_list.pop(key)
			except KeyError as e:
				print e


	return my_client_list


def create_csv():
	with open('recap.csv', 'w') as csvfile:
		filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
		filewriter.writerow(['timestamp','valid_wifi', 'random_wifi', 'ble', 'classic_bt'])

def update_csv(ts, valid_wifi, random_wifi):
	with open('recap.csv', 'a') as csvfile:
		filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
		filewriter.writerow([ts,valid_wifi, random_wifi, ' ', ' '])


def count_users(my_client_list):
	total_users = len(my_client_list.keys())
	random_users = sum(1 for client in my_client_list.itervalues() if client["vendor"] == "unknown") #sum number of random users
	valid_users = total_users - random_users

	print "Total users: ", total_users
	print "Random users: ", random_users
	print "Valid users: ", valid_users

	return total_users, random_users, valid_users

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
			print e, "and the motherfucker is ", rssi
			continue

		#remove LAP in vendor
		if ":" in mac_resolved[:-9]:
			mac_resolved = "unknown"
		else: 
			mac_resolved = mac_resolved[:-9]

		#create the mac field
		if not my_client_list.has_key(mac_addr):
				my_client_list[mac_addr] = \
					{"last_ts": ts[13:-15], "times_seen": 1, "last_rssi": rssi, "vendor": mac_resolved, "ssid": [ssid], "life":LIFE} 
		else:
			my_client_list[mac_addr]["times_seen"] += 1 
			my_client_list[mac_addr]["last_rssi"] = rssi
			my_client_list[mac_addr]["last_ts"] = ts[13:-15]
			my_client_list[mac_addr]["life"] = LIFE
			#the ssid field is skippable
			if ssid not in my_client_list[mac_addr]["ssid"]:
				my_client_list[mac_addr]["ssid"].append(ssid)
				my_client_list[mac_addr]["ssid"] = filter(None, my_client_list[mac_addr]["ssid"]) #delete last field if it's empty (no ssid inside probe)

	return my_client_list

def parse_file(file_path, my_client_list):
	print "loading from ", file_path
	lines = [line.rstrip('\n') for line in open(file_path[:-1])] #load the file

	load_dict(lines, my_client_list) #manipulate the data // fill the dict

	return my_client_list

#### MAIN ####
if __name__ == "__main__":
	signal.signal(signal.SIGINT, signal_handler)
	print "COWIBLI v1.0"
	
	create_csv()

	q_wifi_probe = Queue.Queue(BUF_SIZE)
	t_wifi = WifiHandler.WifiThread(q_wifi_probe)
	#t_wifi.setDaemon(False)
	t_wifi.start() 

	client_list = {}

	while True:
		if not q_wifi_probe.empty():
			new_wifi_path = q_wifi_probe.get()
			print new_wifi_path
			client_list = parse_file(new_wifi_path, client_list)

			#pp.pprint(client_list)

			total_wifi, random_wifi, valid_wifi = count_users(client_list)
			update_csv(new_wifi_path[17:-5], valid_wifi, random_wifi)

			client_list = decrease_life(client_list)
