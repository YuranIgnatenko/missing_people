from flask import Flask, request, render_template
from parser_service import Parser, URL_SITE, URL_SITE_ALERT_SEARCH

class WebApp():
	def __init__(self) -> None:
		self.app = Flask(__name__)
		self.parser_service = Parser()
		# self.collection_missing_people = self.parser_service.get_array_missing_people_from_all_pages(URL_SITE_MISSING_PEOPLE)
		self.collection_missing_people = self.parser_service.get_array_missing_people_from_url(URL_SITE, URL_SITE_ALERT_SEARCH)
		self.setup_routes()

	def setup_routes(self) -> str:
		@self.app.route('/')
		def index():
			for item in self.collection_missing_people:
				print()
				print(item.url_image)
			return render_template('index.html', collection_missing_people=self.collection_missing_people)

	def start_app(self) -> None:
		self.app.run(debug=False)


def main() -> None:
	webapp = WebApp()
	webapp.start_app()

if __name__ == "__main__":
	main()