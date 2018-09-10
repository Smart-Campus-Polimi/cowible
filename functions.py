import csv

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

	return random_users, valid_users, len(my_ble_list.keys())

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

