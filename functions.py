import csv
import copy
import os, errno #for creating direcotry
from time import strftime, localtime
import datetime


import constants as c


def split_random(wifi_users):
	rand = {}
	non_rand = {}
	for key, val in wifi_users.items():
		if val['vendor'] == 'unknown':
			rand[key] = val
		else:
			non_rand[key] = val

	return non_rand, rand

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
	copy_client = copy.deepcopy(my_client_list)
	random_users = sum(1 for client in copy_client.itervalues() if client["vendor"] == "unknown") #sum number of random users
	valid_users = len(my_client_list.keys()) - random_users

	return random_users, valid_users, len(my_ble_list.keys()), len(my_bt_list.keys())


def parse_file(file_path, my_client_list):
	#print "loading from ", file_path
	lines = [line.rstrip('\n') for line in open(file_path[:-1])] #load the file

	load_dict(lines, my_client_list) #manipulate the data // fill the dict

	return my_client_list


def insert_into_dict(my_dict, my_ts, my_mac, my_rssi, my_mac_resolved, is_wifi, is_ble, is_bt):
	if is_wifi:
		my_life = c.LIFE_WIFI
	elif is_bt:
		my_life = c.LIFE_BT
	elif is_ble:
		my_life = c.LIFE_BLE

	if not my_dict.has_key(my_mac):
		my_dict[my_mac] = \
			{"last_ts": my_ts, "times_seen": 1, "last_rssi": [my_rssi], "vendor": mac_resolved, "life":my_life} 
		if is_wifi:
			my_dict[my_mac]["vendor"] = my_mac_resolved
	
	else:
		my_dict[my_mac]["times_seen"] += 1 
		
		print my_ts, addSecs(my_dict[my_mac]["last_ts"], 60)
		if (addSecs(my_dict[my_mac]["last_ts"], 60) < my_ts):
			my_dict[my_mac]["last_rssi"][:] = [] #empty the list
			
		my_dict[my_mac]["last_rssi"].append(my_rssi)
		my_dict[my_mac]["last_rssi"] = my_rssi
		my_dict[my_mac]["last_ts"] = my_ts
		my_dict[my_mac]["life"] = my_life
		#the ssid field is skippable
		#if ssid not in my_client_list[mac_addr]["ssid"]:
		#	my_client_list[mac_addr]["ssid"].append(ssid)
		#	my_client_list[mac_addr]["ssid"] = filter(None, my_client_list[mac_addr]["ssid"]) #delete last field if it's empty (no ssid inside probe)



	return my_dict


'''
	create the dictionary of the client
	one key for each unique mac address
'''
def load_dict(probe_list, my_client_list):
	for probe in probe_list:
		probe = probe.split(';') 	#create the list of single probe
		ts, mac_resolved, mac_addr, rssi= probe #unpack the list 
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

		#convert from string to datetime
		now = datetime.datetime.strptime(ts[13:-15], '%H:%M:%S').time()
		

		#create the mac field
		if not my_client_list.has_key(mac_addr):
				my_client_list[mac_addr] = \
					{"last_ts": now, "times_seen": 1, "last_rssi": [rssi], "vendor": mac_resolved, "life":c.LIFE_WIFI} 
		else:
			my_client_list[mac_addr]["times_seen"] += 1 

			#empty the list
			if (addSecs(my_client_list[mac_addr]["last_ts"], 60) < now):
				my_client_list[mac_addr]["last_rssi"][:] = []
			
			my_client_list[mac_addr]["last_rssi"].append(rssi)

			my_client_list[mac_addr]["last_rssi"].append(rssi)
			my_client_list[mac_addr]["last_ts"] = now
			my_client_list[mac_addr]["life"] = c.LIFE_WIFI
			
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
		now = datetime.datetime.now().time().replace(microsecond=0)

		if not my_list.has_key(mac_addr):
					my_list[mac_addr] = \
						{"last_ts": now, "times_seen": 1, "last_rssi": [rssi], "life":c.LIFE_BT} 
		else:
			my_list[mac_addr]["times_seen"] += 1 
			#here!!! finish
			if (addSecs(my_list[mac_addr]["last_ts"], 60) < now):
				#empty list
				my_list[mac_addr]["last_rssi"][:] = []
				
			my_list[mac_addr]["last_rssi"].append(rssi)

			my_list[mac_addr]["last_ts"] = now
			my_list[mac_addr]["life"] = c.LIFE_BT
	except IndexError:
		pass


	return my_list


#CSV FUNCTIONS
csv_list = ['wifi_non-random', 'wifi_random', 'ble', 'classic_bt']


def create_directory(directory_path):
	try:
		print directory_path
		os.makedirs(directory_path)
	except OSError as e:
		if e.errno != errno.EEXIST:
			raise
	return directory_path

def create_csv():
	day = strftime("%y%m%d", localtime())
	my_path = 'goldmine/'+day+'/'+strftime("%H%M%S", localtime())+'/'
	create_directory(my_path)
	data_path = create_directory('data/'+day)

	with open(my_path+'recap.csv', 'w') as csvfile:
		filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
		filewriter.writerow(['timestamp','valid_wifi', 'random_wifi', 'ble', 'classic_bt'])

	for file in csv_list:
		with open(my_path+file+'.csv', 'w') as csvfile:
			filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
			header = [i for i in range(c.CSV_LOWER, c.CSV_UPPER, c.CSV_STEP)]
			header.insert(0,'ts')
			filewriter.writerow(header)

	return my_path, data_path



def update_csv(my_path, ts, valid_wifi, random_wifi, ble, bt):
	with open(my_path+'recap.csv', 'a') as csvfile:
		filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
		filewriter.writerow([ts,valid_wifi, random_wifi, ble, bt])



def final_csv(my_path, ts, dictionaries):
	rssi_list = []
	empty_rssi = []
	rssi_list.append([i for i in range(c.CSV_LOWER, c.CSV_UPPER, c.CSV_STEP)])
	for i in range (0,len(dictionaries)):
		empty_rssi.append([0 for i in range(c.CSV_LOWER, c.CSV_UPPER, c.CSV_STEP)])
	rssi_list = rssi_list[0]
	#empty_rssi = empty_rssi[0]

	for main_index, single_dict in enumerate(dictionaries):
		for key, val in single_dict.items():
			rssi = sum(map(int, val['last_rssi']))/len(val['last_rssi']) #average of the list and round, check the rounding
			if rssi not in rssi_list:
				if rssi < c.CSV_LOWER: #-100
					rssi = c.CSV_LOWER
				elif rssi > c.CSV_UPPER-1: #-29
					rssi = c.CSV_UPPER-1
				else:
					rssi += 1

			#less equal than!!
			#check if the rssi is less than the index, for each index of the rssi list. if yes increase it, else the val remains the same
			empty_rssi[main_index] = [item+1 if index <= rssi_list.index(rssi) else item for index, item in enumerate(empty_rssi[main_index])] 
		
	for csv_name, vals in zip(csv_list, empty_rssi):
		payload = copy.deepcopy(vals)
		payload.insert(0,ts)
		with open(my_path+csv_name+'.csv', 'a') as csvfile:
			filewriter = csv.writer(csvfile, delimiter=',',
				quotechar='|', quoting=csv.QUOTE_MINIMAL)
			filewriter.writerow(payload)


def addSecs(tm, secs):
    fulldate = datetime.datetime(100, 1, 1, tm.hour, tm.minute, tm.second)
    fulldate = fulldate + datetime.timedelta(seconds=secs)
    return fulldate.time()
