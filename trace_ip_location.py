#!/bin/python

from mpl_toolkits.basemap import Basemap
from matplotlib import pylab as plt
from annonymize import Annonymize
import threading
import multiprocessing
import requests
from requests.exceptions import ProxyError
import argparse
import os
import time
import json
import sys
import re


class ProxyFound(Exception):
	pass


class RequestsClass(Annonymize):
	def __init__(self, url = "", ip_rotate = False):
		super().__init__()
		self.url = url
		self.ip_rotate = ip_rotate
		
	def set_headers(self):
		self.get_user_agent()
		self.headers = {
			'User-Agent': self.user_agent,
			'Accept': 'application/json, text/javascript, */*; q=0.01'
		}
		
	def set_proxy(self):
		self.proxies = {
			'http': self.proxy,
			"https": self.proxy
		}
	
	def send_GET_request(self):
		try:
			self.response = requests.get(
				url = self.url,
				headers = self.headers,
				timeout = 10
			)
			if self.response.status_code != 200:
				print("Something went wrong", self.response.reason)
		except Exception as ex:
			print("Something went wrong", ex.__str__())
	
	
	def send_GET_request_through_proxy(self, proxy, responses):
		try:
			self.proxy = proxy
			self.set_proxy()
			response = requests.get(
				url = self.url,
				headers = self.headers,
				proxies = self.proxies,
				timeout = 10
			)
			if response.status_code == 200:
				responses.append(response)
		except Exception as ex:
			print("{} didn't work...".format(self.proxy))
	
	def threaded_proxy_requests(self):
		proxy_threads = list()
		manager = multiprocessing.Manager()
		responses = manager.list()
		for proxy in self.proxy_list:
			process = multiprocessing.Process(
				target = self.send_GET_request_through_proxy,
				args = (proxy, responses,)
			)
			proxy_threads.append(process)
			process.start()
			
		while True:
			if len(responses[:]) > 0:
				for proc in proxy_threads:
					proc.terminate()
					proc.kill()
				print("\nFound working proxy!!")
				print(proxy)
				break
		self.response = responses[0]
		
	def send_request(self):
		self.set_headers()
		if self.ip_rotate:
			print("Getting proxies...")
			self.get_proxies()
			print("Sending api request...")
			self.threaded_proxy_requests()
		else:
			self.send_GET_request()



class IPTrace(RequestsClass):
	def __init__(self, ip_rotate, ip_address, ipstack_access_key):
		super().__init__(self, ip_rotate)
		self.ipstack_access_key = ipstack_access_key
		self.ip_address = ip_address
	
	def get_url(self):
		self.url = ''.join([
      	"http://api.ipstack.com/",
      	self.ip_address,
			"?access_key=",
			self.ipstack_access_key
		])

	def get_JSON_data(self):
		try:
			if self.response.status_code == 200:
				self.json_data = self.response.json()
		except Exception as ex:
			print(ex.__str__(), self.response.reason)
			sys.exit()
			
	def get_country_name(self):
		self.country = self.json_data.get("country_name")
	
	def get_country_code(self):
		self.country_code = self.json_data.get("country_code")
		
	def get_city(self):
		self.city = self.json_data.get("city")

	def get_region_name(self):
		self.region = self.json_data.get("region_name")

	def get_latitude(self):
		self.latitude = self.json_data.get("latitude")
   
	def get_longitude(self):
		self.longitude = self.json_data.get("longitude")

	def trace_ip_address(self):
		print("Keys added...")
		self.get_url()
		self.get_user_agent()
		self.send_request()
		self.get_JSON_data()
		self.get_country_name()
		self.get_country_code()
		self.get_city()
		self.get_region_name()
		self.get_latitude()
		self.get_longitude()


  
class Map: 
	def __init__(self, latitudes, longitudes, ip_addresses):
		self.base_map_obj = Basemap()	
		self.latitudes = latitudes
		self.longitudes = longitudes
		self.ip_addresses = ip_addresses
	     
	def build_base_map(self):
		 self.base_map_obj.drawmapboundary(fill_color = "aqua")
		 self.base_map_obj.fillcontinents(color = "green", lake_color='aqua')
		 self.base_map_obj.drawcoastlines()
		 self.base_map_obj.drawstates() 
	
	def plot_geo_location(self):
		lat_lon_ip_zipped = zip(
			self.latitudes, self.longitudes, self.ip_addresses
		)
		for latitude, longitude, ip_address in lat_lon_ip_zipped:
			self.base_map_obj.plot(
				longitude, 
				latitude, 
				'rv',
				markersize = 9,
				alpha = .5,
				label = ip_address
			)
		plt.title('Geolocation From IP Address lookup')
		plt.show()


class ArgParser:
	def __init__(self):
		self.parser = argparse.ArgumentParser(
			description = """Trace Location of IP address, and plot on relief map"""
		)
		
	def add_ip_addresses(self):
		self.parser.add_argument(
			"--ip_addresses", 
			help = "server names or ip addresses of host servers",
			required = True
		)
		
	def add_plot(self):
		self.parser.add_argument(
			"--plot",
			help = """\nchoose to plot location of ip address trace (default: False)
						Note: requires Basemap to be installed:
						sudo apt install python3-mpltoolkits.basemap\n""",
			type = bool,
			required = False,
			default = False
		)
	
	def add_ip_stack_key(self):
		self.parser.add_argument(
			"--ip_stack_key",
			help = """the file containing the api key for your ip stack account""",
			type = str,
			required = True
		)
		
	def add_ip_rotate(self):
		self.parser.add_argument(
			"--ip_rotate",
			help = """Decide whether you want to use free proxies (default: False). 
						Note: if False, you must provide your own proxies through a 
						third party source (noord vpn, or tor etc.)""",
			type = bool,
			required = False,
			default = False
		)
		
	def add_args(self):
		self.add_ip_addresses()
		self.add_plot()
		self.add_ip_stack_key()
		self.add_ip_rotate()


if __name__ == "__main__":
	arg_parse_obj = ArgParser()
	arg_parse_obj.add_args()
	args = arg_parse_obj.parser.parse_args()
	
	##get_args
	ip_addresses = args.ip_addresses.split(",")	
	do_plot = args.plot
	ip_rotate = args.ip_rotate
	with open(args.ip_stack_key, "r") as KEY:
		ipstack_access_key = KEY.read()
		ipstack_access_key = ipstack_access_key.strip()
	
	latitudes = list()
	longitudes = list()
	
	for ip_address in ip_addresses:
		ip_trace_obj = IPTrace(
			ip_address = ip_address.strip(), 
			ipstack_access_key = ipstack_access_key,
			ip_rotate = ip_rotate
		)
		ip_trace_obj.trace_ip_address()
		print("\n\nIP address:",ip_trace_obj.ip_address)
		print("Country:", ip_trace_obj.country)
		print("City:", ip_trace_obj.city)
		longitudes.append(ip_trace_obj.longitude)
		latitudes.append(ip_trace_obj.latitude)	
    

	if do_plot:
		map_obj = Map(
			ip_addresses = ip_addresses,
			longitudes = longitudes,
			latitudes = latitudes
		)
		map_obj.build_base_map()
		map_obj.plot_geo_location()
    
   
