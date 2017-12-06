#!/usr/bin/env python
#
#

import sys
import requests
from bs4 import BeautifulSoup
import time
import datetime 

circuit_ids = ["RAILLOAD0","RAILLOAD1","RAILLOAD2","RAILLOAD3","RAILLOAD4"]
circuit_stat_ids = ["RAILENA0","RAILENA1","RAILENA2","RAILENA3","RAILENA4"]

class circuit():
	def __init__(self,cktname):
		self.updatetime = None
		self.cktname = cktname
		self.status = 0
		self.voltage = 0.0
		self.current = 0.0

	def power(self):
		return self.voltage * self.current

	def print_data(self):
		print("%s,%s,%s,%s,%s,%s" % (datetime.datetime.fromtimestamp(self.updatetime).isoformat(),self.updatetime,self.cktname,self.status,self.voltage,self.current))

	def print_log(self,logfile):
		logfile.write("%s,%s,%s,%s,%s,%s\n" % (datetime.datetime.fromtimestamp(self.updatetime).isoformat(),self.updatetime,self.cktname,self.status,self.voltage,self.current))
		
class west_mountain_radio():

	def __init__(self,ip_address):
		self.url = "http://" + ip_address 
		self.circuits = []

	def get_names(self):

		# We use Beautiful soup to get the node names from the front page.
		r = requests.get(self.url)
		#r = requests.get("http://192.168.100.212")
		bs = BeautifulSoup(r.text)
		table = bs.find("table", attrs={"class":"info_table"})
		rows = table.find_all("tr")
		for row in rows:
			cols = row.find_all("td")
			if cols:
				rowname = str(cols[0].text.strip())
				if rowname != "Power Supply" and rowname != "":
					self.circuits.append(circuit(rowname))

	def get_status(self):
	
		# Gets the status xml page.
		r = requests.get(self.url + "/status.xml")
		#r = requests.get("http://192.168.100.212/status.xml")
		updatetime = time.time()
		bs = BeautifulSoup(r.text)
		items = bs.get_text().split('\n')
		voltage = items[1]
		current = items[2:7]
		status = items[7:]


		for i in range(self.circuits.__len__()):
			self.circuits[i].updatetime = updatetime
			self.circuits[i].voltage = voltage
			self.circuits[i].current = current[i]
			self.circuits[i].status = status[i]

	def print_status(self):
		print ""
		print "Status for " + self.url
		for c in self.circuits:
			c.print_data()

	def print_log(self,logfile):
		for c in self.circuits:
			c.print_log(logfile)	

if __name__ == '__main__':

	if sys.argv[1] == '-h':
		print "Usage:"
		print "  ./west_mountain_radio 192.168.100.224"
		sys.exit()
	if sys.argv[1] == 'log':
		iso = datetime.datetime.utcnow().isoformat().replace(':','-')
		with open('west_mountain_radio_log_' + iso + '.txt','w') as logfile:
			
			while True:
				# FIX THIS		
				wmr12 = west_mountain_radio('192.168.100.212')
				wmr24 = west_mountain_radio('192.168.100.224')
				wmr24.get_names()
				wmr24.get_status()
				wmr24.print_status()
				wmr24.print_log(logfile)
				wmr12.get_names()
				wmr12.get_status()
				wmr12.print_status()
				wmr12.print_log(logfile)
				time.sleep(1)		
	
	else:
		wmr = west_mountain_radio(sys.argv[1])
		wmr.get_names()
		wmr.get_status()
		wmr.print_status()
