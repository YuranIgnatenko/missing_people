import requests
from bs4 import BeautifulSoup
import pyshorteners	
from random import randint
import sys, json

from config import Config
import tools

class Parser():
	def __init__(self, conf:Config) -> None:
		self.conf_base = conf
		self.conf_categories = Config(self.conf_base.get("file_categories"))
		self.name_categories = self.conf_base.data.keys()

	def shorten_url(self, url:str) -> str:
		return tools.shorten_url(url)

	def get_random_number_page(self, max_page:int) -> int:
		return tools.get_random_number_page(max_page)

	def build_url_page_image(self, category_name:str, num_page:int=0) -> str:
		return tools.build_url_page_image(self, category_name, num_page)

	def get_count_pages(self, category_name:str) -> int:
		url = self.build_url_page_image(category_name)
		try: response = requests.get(url)
		except Exception: return 10
		soup = BeautifulSoup(response.text, 'html.parser')
		temp_links = []
		for link in soup.find_all('a'):
			href = link.get('href')
			if href and href.startswith('http'):
				if href.find('/p') != -1:
					temp_links.append(href)
		max_num_page = int(temp_links[-1].split('/')[-2][1:])
		return max_num_page

	def get_url_random_page_from_category(self, category_name:str) -> str:
		max_page_category = self.get_count_pages(category_name)-1
		try:
			random_page = randint(1,max_page_category)
			return self.get_image_from_params(category_name, random_page)
		except Exception:
			return self.get_image_from_params(category_name, random_page)

	def get_image_from_params(self, category_name:str, num_page:int) -> str:
		temp_url = self.build_url_page_image(category_name, num_page)
		response = requests.get(temp_url)
		soup = BeautifulSoup(response.text, 'html.parser')
		tmp = []
		for link in soup.find_all('a'):
			href = link.get('href')
			if href and href.startswith('http'):
				if href.find('/view') != -1:
					response = requests.get(href)
					soup = BeautifulSoup(response.text, 'html.parser')
					tmp_d = []
					for link in soup.find_all('a'):
						href = link.get('href')
						if href and href.startswith('http'):
							if href.find("download") != -1:
								tmp_d.append(href) 
										
					if len(tmp_d) == 0: continue
					tmp.append(tmp_d[-1].replace("jpg","png"))
		res = tmp[0]
		return res
