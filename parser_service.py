import requests
from bs4 import BeautifulSoup
import sys, json, argparse

URL_SITE = "https://moscow.sledcom.ru/"
URL_SITE_ALERT_SEARCH = "https://moscow.sledcom.ru/folder/918943"

class MissingPeople():
	def __init__(self, url_image:str, date_create:str, url_html_page:str, description:str) -> None:
		self.url_image = url_image
		self.date_create = date_create 
		self.url_html_page = url_html_page
		self.description =  description

def MissingPeopleFromSoup(url_site_prefix:str, item_div_people_info:BeautifulSoup) -> MissingPeople:
	date_create = item_div_people_info.find("div",class_="bl-item-date").text
	description = item_div_people_info.find("p").text
	url_html_page = url_site_prefix+item_div_people_info.find("a").get('href')
	url_image = url_site_prefix+item_div_people_info.find("img").get('src')
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

	def get_array_missing_people_from_all_pages(self, url:str) -> list[MissingPeople]:
		temp_array_missing_people = []
		for html_page_url in self.get_array_html_pages_urls(url):
			temp_array_missing_people += self.get_array_missing_people_from_url(html_page_url)
		print(len(temp_array_missing_people))

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
					temp_array_peoples.append(temp_url_page)
		return temp_array_peoples



def main() -> None:
	parser = Parser()
	parser.get_array_missing_people_from_all_pages(URL_SITE_ALERT_SEARCH)


if __name__ == "__main__":
	main()