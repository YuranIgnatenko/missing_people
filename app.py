from flask import Flask, request, render_template
from parser_service import *

class WebApp():
	def __init__(self) -> None:
		self.app = Flask(__name__)

		self.parser_sledkom = ParserSledcom()
		self.parser_mvd = ParserMvd()
		self.parser_lizaalert = ParserLizaAlert()

		self.collection_missing_people = self.parser_sledkom.get_array_people(DICT_URLS_SLEDCOM["ПОГИБШИЕ"])

		self.status_count_missing_people = self.format_status_missing_people()
		self.count_max_items_in_page = 5
		self.active_number_page = 0
		self.setup_routes()

	def get_active_index_collection(self) -> int:
		return self.active_number_page * self.count_max_items_in_page

	def get_slice_collection_for_page(self) -> list[MissingPeople]:
		if self.active_number_page >= len(self.collection_missing_people) or self.active_number_page < 0:
			return self.collection_missing_people[:self.count_max_items_in_page]
		if len(self.collection_missing_people) <= self.active_number_page * self.count_max_items_in_page: 
			return self.collection_missing_people[:self.count_max_items_in_page]

		if len(self.collection_missing_people) <= self.active_number_page * self.count_max_items_in_page + self.count_max_items_in_page:
			return self.collection_missing_people[self.get_active_index_collection():]
		else:
			return self.collection_missing_people[self.get_active_index_collection():self.get_active_index_collection()+self.count_max_items_in_page]

	def format_status_page(self) -> str:
		value = int(len(self.collection_missing_people) / self.count_max_items_in_page)
		return f"Index Page: {self.active_number_page} / {value}"

	def format_status_missing_people(self) -> str:
		return f"Missing People: {len(self.collection_missing_people)}"

	def setup_routes(self) -> str:
		@self.app.route('/')
		def index():
			return render_template('index.html',
			collection_missing_people=self.get_slice_collection_for_page(),
			status_count_missing_people=self.status_count_missing_people, 
			status_page=self.format_status_page())

		@self.app.route('/next')
		def index_next():
			if self.active_number_page < int(len(self.collection_missing_people) / self.count_max_items_in_page):
				self.active_number_page += 1
			return render_template('index.html',
			collection_missing_people=self.get_slice_collection_for_page(),
			status_count_missing_people=self.status_count_missing_people, 
			status_page=self.format_status_page())

		@self.app.route('/prev')
		def index_prev():
			if self.active_number_page > 1:
				self.active_number_page -= 1
			return render_template('index.html',
			collection_missing_people=self.get_slice_collection_for_page(),
			status_count_missing_people=self.status_count_missing_people, 
			status_page=self.format_status_page())

		@self.app.route('/reparsing')
		def index_reparsing():
			self.active_number_page = 0
			self.collection_missing_people = self.parser_sledkom.get_array_people(DICT_URLS_SLEDCOM["БЕЗ ВЕСТИ"])
			self.status_count_missing_people = self.format_status_missing_people()
			return render_template('index.html',
			collection_missing_people=self.get_slice_collection_for_page(),
			status_count_missing_people=self.status_count_missing_people, 
			status_page=self.format_status_page())

		@self.app.route('/view/<id>')
		def view_id(id):
			for people in self.collection_missing_people:
				if people.id == id:					
					if people.url_html_page.find(URL_SITE_LIZAALERT_FORUM) != -1:
						return render_template('single.html', people = people )
					if people.url_html_page.find(URL_SITE_MVD) != -1:
						return render_template('single.html', people = people )

					temp_missing_people_profile = self.parser_sledkom.get_profile_people(people.url_html_page)
					return render_template('single.html', people = temp_missing_people_profile )

			return render_template('index.html',
			collection_missing_people=self.get_slice_collection_for_page(),
			status_count_missing_people=self.status_count_missing_people, 
			status_page=self.format_status_page())

		@self.app.route('/missing_people_child')
		def missing_people_child():
			self.collection_missing_people = self.parser_sledkom.get_array_people(DICT_URLS_SLEDCOM["ДЕТИ"])
			return render_template('index.html',
			collection_missing_people=self.get_slice_collection_for_page(),
			status_count_missing_people=self.status_count_missing_people, 
			status_page=self.format_status_page())
  

		@self.app.route('/missing_people_die')
		def missing_people_die():
			self.collection_missing_people = self.parser_sledkom.get_array_people(DICT_URLS_SLEDCOM["ПОГИБШИЕ"])
			return render_template('index.html',
			collection_missing_people=self.get_slice_collection_for_page(),
			status_count_missing_people=self.status_count_missing_people, 
			status_page=self.format_status_page())

		
		@self.app.route('/missing_people_unidentify')
		def missing_people_unidentify():
			self.collection_missing_people = self.parser_sledkom.get_array_people(DICT_URLS_SLEDCOM["БЕЗ ВЕСТИ"])
			return render_template('index.html',
			collection_missing_people=self.get_slice_collection_for_page(),
			status_count_missing_people=self.status_count_missing_people, 
			status_page=self.format_status_page())


		@self.app.route('/missing_people_alert')
		def missing_people_alert():
			self.collection_missing_people = self.parser_sledkom.get_array_people(DICT_URLS_SLEDCOM["ПОДОЗРЕВАЕМЫЕ"])
			return render_template('index.html',
			collection_missing_people=self.get_slice_collection_for_page(),
			status_count_missing_people=self.status_count_missing_people, 
			status_page=self.format_status_page())
			
		@self.app.route('/missing_people_mvd')
		def missing_people_mvd():
			self.collection_missing_people = self.parser_mvd.get_array_people(URL_SITE_MVD)
			return render_template('index.html',
			collection_missing_people=self.get_slice_collection_for_page(),
			status_count_missing_people=self.status_count_missing_people, 
			status_page=self.format_status_page())

		@self.app.route('/missing_people_lizaalert')
		def missing_people_lizaalert():
			self.collection_missing_people = self.parser_lizaalert.get_array_people(URL_SITE_LIZAALERT)
			return render_template('index.html',
			collection_missing_people=self.get_slice_collection_for_page(),
			status_count_missing_people=self.status_count_missing_people, 
			status_page=self.format_status_page())

		@self.app.route('/settings')
		def settings():
			return render_template('settings.html')

	def start_app(self) -> None:
		self.app.run(debug=False)


def main() -> None:
	webapp = WebApp()
	webapp.start_app()

if __name__ == "__main__":
	main()




# <div class='container'>
# 	{% for item in collection_missing_people: %}
# 	<div class="card">
# 		<img src="{{ item.url_image }}" alt="Avatar" style="width:100%">
# 		<div class="container">
# 		  <h4><b>{{ item.date_create }}</b></h4> 
# 		  <p>{{ item.url_html_page }}</p> 
# 		  <P>{{ item.description }}</P>
# 		</div>
# 	  </div>
# 	{% endfor %}
# </div>  
