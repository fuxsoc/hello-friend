#!/bin/python

import random
import requests
from bs4 import BeautifulSoup

class Annonymize:
	def __init__(self):
		self.proxy_list_url = "https://free-proxy-list.net/"
		self.proxy_list = list()

	def send_get_request(self):
		self.response = requests.get(self.proxy_list_url)

	def parse_html(self):
		self.parser = BeautifulSoup(
			markup = self.response.text,
			features = "lxml"
		)

	def get_table(self):
		self.table = self.parser.find_all("tr")

	def get_cells(self):
		self.cells = self.row.find_all("td")

	def check_if_secure(self):
		self.is_secure = self.row.find("td", {"class":"hx"}).text.strip()

	def get_elite_proxies(self):
		for row in self.table:
			self.row = row
			if "elite proxy" in row.text:
				self.get_cells()
				self.check_if_secure()
				if self.is_secure == "yes":
					proxy_ip = self.cells[0].text.strip()
					proxy_port = self.cells[1].text.strip()
					proxy = ':'.join([proxy_ip, proxy_port])
					self.proxy_list.append(proxy)

	def get_user_agent(self):
		with open("user_agents.txt", "r") as FILE:
			user_agents = FILE.readlines()
		self.user_agent = random.choice(user_agents).strip()
	
	def get_proxies(self):
		self.send_get_request()
		self.parse_html()
		self.get_table()
		self.get_elite_proxies()
		self.get_user_agent()
		
		 
		


