import requests
from bs4 import BeautifulSoup
import sys, json, argparse

URL_SITE = "https://moscow.sledcom.ru/"
URL_SITE_ALERT_SEARCH = "https://moscow.sledcom.ru/attention/Vnimanie_Propal_rebenok" # "https://moscow.sledcom.ru/folder/918943"
URLS = {
	"ДЕТИ":"https://moscow.sledcom.ru/attention/Vnimanie_Propal_rebenok",
	"ПОГИБШИЕ":"https://moscow.sledcom.ru/attention/Neopoznannye-trupy",
	"ПОДОЗРЕВАЕМЫЕ":"https://moscow.sledcom.ru/attention/Podozrevaemie_v_sovershenii_prestuplenij",
	"БЕЗ ВЕСТИ":"https://moscow.sledcom.ru/folder/918943",
}

class MissingPeople():
	def __init__(self, title:str, url_image:str, date_create:str, url_html_page:str, description:str, id:str) -> None:
		self.url_image = url_image
		self.date_create = date_create 
		self.url_html_page = url_html_page
		self.description =  description
		self.title = title
		self.id = id
	def get_id(self):
		return self.url_html_page.split("/")[-2]


def MissingPeopleFromSoup(url_site_prefix:str, soup_section:BeautifulSoup) -> MissingPeople:

	try:
		temp_title = soup_section.find("div", class_="bl-item-holder").find("div", class_="bl-item-title").find("a").text
	except:
		# try:
		temp_title = soup_section.find("div", class_="bl-item-holder").find("div", class_="bl-item-title").find("a").text

	try:
		url_image = URL_SITE+soup_section.find("div", class_="bl-item-image").find("a").find("img").get("src")
	except:
		url_image = "/static/img/alert.jpg"

	try:
		description = soup_section.find("div", class_="bl-item-holder").find("div", class_="bl-item-text")
		description = "\n".join([t.find("span").text for t in description.find_all("p")])
	except:
		description = soup_section.find("div", class_="bl-item-holder").find("div", class_="bl-item-text")
		description = "\n".join([t.text for t in description.find_all("p")])

	try:
		url_html_page = soup_section.find("div", class_="bl-item-title").find("a").get("href")
	except:
		url_html_page = soup_section.find("div", class_="bl-item-title").find("a").get("href")


	id = f"{url_html_page.split("/")[-2]}"

	return MissingPeople(temp_title, url_image,temp_title,url_html_page,description, id)


class Parser():
	def __init__(self) -> None:
		self.headers = { 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
		self.cookies  = {
			"bh" : "EkwiTm90IEEoQnJhbmQiO3Y9IjgiLCJDaHJvbWl1bSI7dj0iMTMyIiwiWWFCcm93c2VyIjt2PSIyNS4yIiwiWW93c2VyIjt2PSIyLjUiGgN4ODYiCjI1LjIuMS44ODcqAj8wOgdXaW5kb3dzQgYxMC4wLjBKAjY0UmMiTm90IEEoQnJhbmQiO3Y9IjguMC4wLjAiLCJDaHJvbWl1bSI7dj0iMTMyLjAuNjgzNC44ODciLCJZYUJyb3dzZXIiO3Y9IjI1LjIuMS44ODciLCJZb3dzZXIiO3Y9IjIuNSJaAj8wYKzMkb4G",
			"Session_id":"3:1740876007.5.0.1724784552353:BagZXg:b90d.1.2:1|306336913.-1.2.2:14232801.3:1739017353|3:10303801.65629.QO_tI8IucN_7U7GEGmXGoNfWDZ4",
			"yandex_login":"Yuran.Ignatenko",
			"yandexuid":"2083661171724784397"
		}

	def get_profile_people(self, html_page_url:str) -> MissingPeople:
		response = requests.get(URL_SITE+html_page_url, headers=self.headers, cookies=self.cookies)
		soup = BeautifulSoup(response.text, 'html.parser')

		soup_section = soup.find('section', class_="b-container-center")

		
		temp_title = soup_section.find("h1", class_="b-topic").text

		try:
			url_image = URL_SITE+soup_section.find("article", class_="c-detail").find("img", class_="img_left").get("src")
		except:
			url_image = "/static/img/alert.jpg"

		try:
			description = soup_section.find("article", class_="c-detail")
			description = "\n".join([t.find("span").text for t in description.find_all("p")])
		except:
			description = soup_section.find("article", class_="c-detail")
			description = "\n".join([t.text for t in description.find_all("p")])

		temp_url_page = URL_SITE+html_page_url


		id = f"{temp_url_page.split("/")[-2]}"

		return MissingPeople(temp_title, url_image,temp_title,temp_url_page,description, id)



	def get_array_people(self, url_directory:str) -> list[MissingPeople]:
		url_clean_web_site = URL_SITE
		temp_array_missing_people = []
		for html_page_url in self.get_url_pages(url_directory):
			html_page_url = "/".join(list(dict.fromkeys(html_page_url.split("/"))))+"/"
			response = requests.get(html_page_url, headers=self.headers, cookies=self.cookies)
			soup = BeautifulSoup(response.text, 'html.parser')

			for item_people in soup.find('section', class_="b-container-center").find_all("div", class_="bl-item clearfix"):
				temp_array_missing_people.append(MissingPeopleFromSoup(URL_SITE, item_people))

	
		return temp_array_missing_people


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

	def get_url_pages(self, url:str) -> list[str]:
		response = requests.get(url, headers=self.headers, cookies=self.cookies)
		soup = BeautifulSoup(response.text, 'html.parser')
		temp_array_peoples = []
		for divs in soup.find_all('div', class_="b-pagination"):
			for div in divs:
				div_str = str(div)
				if div_str.startswith(r'<a href="/'):
					temp_url_page = url+div_str.split('="')[1].split('">')[0]
					temp_array_peoples.append(temp_url_page)
		if len(temp_array_peoples) == 0:
			temp_array_peoples.append(url)
		return temp_array_peoples

def main() -> None:
	print("start")
	parser = Parser()
	ar1 = parser.get_array_people(URLS["БЕЗ ВЕСТИ"])
	for people in ar1:
		print("GET ARRAY PEOPLE",people.date_create, people.url_image, people.description)


if __name__ == "__main__":
	main()