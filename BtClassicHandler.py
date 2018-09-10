#!/usr/bin/python

import threading
import subprocess
from bluetooth import *

#my imports
import functions as f
import constants as c



class BtClassicThread(threading.Thread):
	def __init__(self, queue):
		threading.Thread.__init__(self)
		self.queue = queue
		self.is_running = True
		self.bt_list = {}
		#open hcidump > txt
		self.file_path = "test.txt"
		with open(self.file_path, "w") as dump_file:
			subprocess.Popen(['hcidump', '-i', 'hci0', 'hci'], shell=False, stdout = dump_file)



	def run(self):
		print "esd"
		while self.is_running:
			for i in range(0,1):
				discover_devices(lookup_names = True)
			
			self.bt_list = f.parse_hcidump(self.file_path, self.bt_list) #parse hcidump -> store mac address in dict

			print self.bt_list
			open(self.file_path, 'w').close() #clean txt file

			self.queue.put(self.bt_list)
			self.bt_list = f.decrease_life(self.bt_list)

	def stop(self):
		print "close bt scan"
		self.is_running = False

	

#open hcidump > txt
#for n iterations
	#bt scan
	#parse hcidump -> store mac address in dict
	#clean txt file
#send data in queue

