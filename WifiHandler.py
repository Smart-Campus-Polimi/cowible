#!/usr/bin/python

import threading
import subprocess
from time import strftime, localtime

class WifiThread(threading.Thread):
	def __init__(self, queue):
		threading.Thread.__init__(self)
		self.queue = queue
		self.is_running = True


		
	def run(self):
		print "asd"
		while self.is_running:
			starting_day = strftime("%y%m%d", localtime())
			wifi_path = subprocess.check_output(['./tools/tshark.sh', starting_day])
			print wifi_path
			self.queue.put(wifi_path)

	def stop(self):
		self.is_running = False
		subprocess.Popen(['killall', 'tshark'])

	