#!/usr/bin/python
import threading
import subprocess
from time import strftime, localtime

#my imports
import functions as f
import constants as c


class WifiThread(threading.Thread):
	def __init__(self, queue, path):
		threading.Thread.__init__(self)
		self.queue = queue
		self.is_running = True
		self.client_list = {}
		self.path = path


	def run(self):
		print "Ok WIFI"
		while self.is_running:
			print self.path
			self.wifi_path = subprocess.check_output(['./tools/tshark.sh', self.path, str(c.TIMEOUT)])
			print "finish wifi"
			self.client_list = f.parse_file(self.wifi_path, self.client_list)
			self.queue.put(self.client_list)

			self.client_list = f.decrease_life(self.client_list)

	def stop(self):
		print "close wifi"
		self.is_running = False
		subprocess.Popen(['killall', 'tshark'])

	
