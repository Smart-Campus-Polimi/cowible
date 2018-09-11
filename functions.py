import csv
import os, errno #for creating direcotry
from time import strftime, localtime

import constants as c


def decrease_life(my_client_list):
	print("decrease users' life")
	for key, val in my_client_list.items():
		val["life"] -= 1

		if val["life"] < 0:
			try:
				my_client_list.pop(key)
			except KeyError as e:
				print(e)
				print("Error")

	return my_client_list

def count_users(my_client_list, my_ble_list, my_bt_list):
	random_users = sum(1 for client in my_client_list.itervalues() if client["vendor"] == "unknown") #sum number of random users
	valid_users = len(my_client_list.keys()) - random_users

	return random_users, valid_users, len(my_ble_list.keys()), len(my_bt_list.keys())


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
					{"last_ts": ts[13:-15], "times_seen": 1, "last_rssi": rssi, "vendor": mac_resolved, "life":c.LIFE_WIFI} 
		else:
			my_client_list[mac_addr]["times_seen"] += 1 
			my_client_list[mac_addr]["last_rssi"] = rssi
			my_client_list[mac_addr]["last_ts"] = ts[13:-15]
			my_client_list[mac_addr]["life"] = c.LIFE_WIFI
			#the ssid field is skippable
			#if ssid not in my_client_list[mac_addr]["ssid"]:
			#	my_client_list[mac_addr]["ssid"].append(ssid)
			#	my_client_list[mac_addr]["ssid"] = filter(None, my_client_list[mac_addr]["ssid"]) #delete last field if it's empty (no ssid inside probe)

	return my_client_list


##### BLUETOOTH

def parse_hcidump(my_filename, my_list):
	lines = [line.rstrip('\n') for line in open(my_filename)] #load the file

	for text in lines:
		if "rssi" in text:
			load_bt(text, my_list)	

	return my_list	

def load_bt(line_to_parse, my_list):
	line_to_parse = line_to_parse.split(' ')
	try:
		mac_addr = line_to_parse[5]
		rssi = line_to_parse[13]
		if not my_list.has_key(mac_addr):
					my_list[mac_addr] = \
						{"last_ts": strftime("%H%M%S", localtime()), "times_seen": 1, "last_rssi": rssi, "life":c.LIFE_BT} 
		else:
			my_list[mac_addr]["times_seen"] += 1 
			my_list[mac_addr]["last_rssi"] = rssi
			my_list[mac_addr]["last_ts"] = strftime("%H%M%S", localtime())
			my_list[mac_addr]["life"] = c.LIFE_BT
	except IndexError:
		pass


	return my_list


#CSV FUNCTIONS

def create_directory(directory_path):
	try:
		os.makedirs(directory_path)
	except OSError as e:
		if e.errno != errno.EEXIST:
			raise

def create_csv():
	csv_list = ['wifi_non-random', 'wifi_random', 'ble', 'classic_bt']
	my_path = 'goldmine/'+strftime("%y%m%d", localtime())+'/'+strftime("%H%M%S", localtime())+'/'

	create_directory(my_path)

	with open(my_path+'recap.csv', 'w') as csvfile:
		filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
		filewriter.writerow(['timestamp','valid_wifi', 'random_wifi', 'ble', 'classic_bt'])

	for file in csv_list:
		with open(my_path+file+'.csv', 'w') as csvfile:
			filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
			filewriter.writerow([i for i in range(-100, -30, 2)])

	return my_path



def update_csv(my_path, ts, valid_wifi, random_wifi, ble, bt):
	with open(my_path+'recap.csv', 'a') as csvfile:
		filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
		filewriter.writerow([ts,valid_wifi, random_wifi, ble, bt])



def final_csv(my_path, ts, wifi_dict, ble_dict, bt_dict):
	rssi_list = []
	empty_rssi = []
	rssi_list.append([i for i in range(-100, -30, 2)])
	empty_rssi.append([0 for i in range(-100, -30, 2)])
	rssi_list = rssi_list[0]
	empty_rssi = empty_rssi[0]
	print rssi_list
	print empty_rssi


	for key, val in bt_dict.items():
		rssi = int(val['last_rssi'])
		if rssi not in rssi_list:
			rssi += 1

		#check if the rssi is less than the index, for each index of the rssi list. if yes increase it, else the val remain the same
		empty_rssi = [item+1 if index >= rssi_list.index(rssi) else item for index, item in enumerate(empty_rssi)] 
		
	print empty_rssi
		