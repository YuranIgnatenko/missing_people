import requests
from bs4 import BeautifulSoup
import sys, json, argparse

URL_SITE = "https://moscow.sledcom.ru/"
URL_SITE_ALERT_SEARCH = "https://moscow.sledcom.ru/attention/Vnimanie_Propal_rebenok" # "https://moscow.sledcom.ru/folder/918943"

class MissingPeople():
	def __init__(self, url_image:str, date_create:str, url_html_page:str, description:str) -> None:
		self.url_image = url_image
		self.date_create = date_create 
		self.url_html_page = url_html_page
		self.description =  description
	def get_id(self):
		return self.url_html_page.split("/")[-2]

class MissingPeopleProfile():
	def __init__(self, url_image:str, date_create:str, url_html_page:str, description:str, title:str) -> None:
		self.url_image = url_image
		self.date_create = date_create 
		self.url_html_page = url_html_page
		self.description =  description
		self.title = title
	def get_id(self):
		return self.url_html_page.split("/")[-2]



def MissingPeopleFromSoup(url_site_prefix:str, item_div_people_info:BeautifulSoup) -> MissingPeople:
	try:
		date_create = item_div_people_info.find("div",class_="bl-item-date").text
	except:
		date_create = "no date create"

	try:
		description = item_div_people_info.find("div",class_="bl-item-text").text
	except:
		try:
			description = item_div_people_info.find("p").text
		except:
			try:
				description = item_div_people_info.find("h4").text
			except:
				description = "no description"

	url_html_page = url_site_prefix+item_div_people_info.find("a").get('href')
	
	try:
		url_image = url_site_prefix+item_div_people_info.find("img").get('src')
	except:
		url_image = "static/img/alert.jpg"
	return MissingPeople(url_image,date_create,url_html_page,description)

class Parser():
	def __init__(self) -> None:
		self.headers = { 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
		self.cookies  = {
			"bh" : "EkwiTm90IEEoQnJhbmQiO3Y9IjgiLCJDaHJvbWl1bSI7dj0iMTMyIiwiWWFCcm93c2VyIjt2PSIyNS4yIiwiWW93c2VyIjt2PSIyLjUiGgN4ODYiCjI1LjIuMS44ODcqAj8wOgdXaW5kb3dzQgYxMC4wLjBKAjY0UmMiTm90IEEoQnJhbmQiO3Y9IjguMC4wLjAiLCJDaHJvbWl1bSI7dj0iMTMyLjAuNjgzNC44ODciLCJZYUJyb3dzZXIiO3Y9IjI1LjIuMS44ODciLCJZb3dzZXIiO3Y9IjIuNSJaAj8wYKzMkb4G",
			"Session_id":"3:1740876007.5.0.1724784552353:BagZXg:b90d.1.2:1|306336913.-1.2.2:14232801.3:1739017353|3:10303801.65629.QO_tI8IucN_7U7GEGmXGoNfWDZ4",
			"yandex_login":"Yuran.Ignatenko",
			"yandexuid":"2083661171724784397"
		}

	def get_profile_missing_people(self, missing_people:MissingPeople) -> MissingPeopleProfile:
		response = requests.get(missing_people.url_html_page, headers=self.headers, cookies=self.cookies)
		soup = BeautifulSoup(response.text, 'html.parser')

		word_for_split = r'Официальная группа Главного следственного управления в социальной сети "ВКонтакте"'
		temp_array_peoples = []
		temp_description = ""
		temp_url_image = ""
		temp_date_create = ""
		temp_url_html_page = ""
		temp_title = ""

		for soup_p in soup.find_all('p'):
			temp_description += soup_p.text
		
		temp_url_image = URL_SITE+soup.find('img', class_="img_left").get('src')
		temp_title = soup.find('h1', class_="b-topic t-h1 m_b4").text
		temp_description = temp_description.split(word_for_split)[0]
		temp_date_create = missing_people.date_create
		temp_url_html_page = missing_people.url_html_page

		print()
		print(temp_url_image)
		return MissingPeopleProfile(temp_url_image,temp_date_create,temp_url_html_page,temp_description, temp_title)

	def get_array_missing_people_from_all_pages(self, url_site:str, url:str) -> list[MissingPeople]:
		temp_array_missing_people = []
		for html_page_url in self.get_array_html_pages_urls(url):
			temp_array_missing_people += self.get_array_missing_people_from_url(url_site, html_page_url)
		return temp_array_missing_people

	def get_array_missing_people_from_url(self, url_site:str, url_alsert_search:str) -> list[MissingPeople]:
		response = requests.get(url_alsert_search, headers=self.headers, cookies=self.cookies)
		soup = BeautifulSoup(response.text, 'html.parser')
		temp_array_peoples = []
		for divs in soup.find_all('div', class_="bl-item clearfix"):
			temp_array_peoples.append(MissingPeopleFromSoup(url_site, divs))
		return temp_array_peoples

	def get_number_count_html_pages(self, url:str) -> int:
		response = requests.get(url, headers=self.headers, cookies=self.cookies)
		soup = BeautifulSoup(response.text, 'html.parser')
		temp_array_peoples = []
		for divs in soup.find_all('div', class_="b-pagination"):
			for div in divs:
				div_str = str(div)
				if div_str.startswith(r'<a href="/folder/'):
					temp_array_peoples.append(div_str)
		last_item = temp_array_peoples[-1]
		count_number_page = int(last_item.split("/")[3])
		return count_number_page

	def get_array_html_pages_urls(self, url:str) -> list[str]:
		response = requests.get(url, headers=self.headers, cookies=self.cookies)
		soup = BeautifulSoup(response.text, 'html.parser')
		temp_array_peoples = []
		for divs in soup.find_all('div', class_="b-pagination"):
			for div in divs:
				div_str = str(div)
				if div_str.startswith(r'<a href="/folder/'):
					temp_url_page = url+div_str.split('="')[1].split('">')[0]
					temp_url_page = temp_url_page.replace("/folder/918943/folder/918943", "/folder/918943")
					temp_array_peoples.append(temp_url_page)
		return temp_array_peoples

def main() -> None:
	parser = Parser()
	parser.get_array_missing_people_from_all_pages(URL_SITE_ALERT_SEARCH)


if __name__ == "__main__":
	main()