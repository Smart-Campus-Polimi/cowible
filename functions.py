import csv
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

def count_users(my_client_list, my_ble_list):
	random_users = sum(1 for client in my_client_list.itervalues() if client["vendor"] == "unknown") #sum number of random users
	valid_users = len(my_client_list.keys()) - random_users

	return random_users, valid_users, len(my_ble_list.keys()), len(my_bt_list.keys())

def create_csv():
	with open('recap.csv', 'w') as csvfile:
		filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
		filewriter.writerow(['timestamp','valid_wifi', 'random_wifi', 'ble', 'classic_bt'])

def update_csv(ts, valid_wifi, random_wifi, ble):
	with open('recap.csv', 'a') as csvfile:
		filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
		filewriter.writerow([ts,valid_wifi, random_wifi, ble, ' '])


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
					{"last_ts": ts[13:-15], "times_seen": 1, "last_rssi": rssi, "vendor": mac_resolved, "ssid": ssid, "life":c.LIFE_WIFI} 
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
		print mac_addr, rssi
		if not my_list.has_key(mac_addr):
					my_list[mac_addr] = \
						{"last_ts": strftime("%H%M%S", localtime()), "times_seen": 1, "last_rssi": rssi, "life":1} 
		else:
			my_list[mac_addr]["times_seen"] += 1 
			my_list[mac_addr]["last_rssi"] = rssi
			my_list[mac_addr]["last_ts"] = strftime("%H%M%S", localtime())
			my_list[mac_addr]["life"] = 1
	except IndexError:
		pass


	return my_list