from flask import Flask, request, render_template

import argparse

import logging
import threading
import queue
import random

from telegram_bot_service import TelegramBotService, ParserSpcs
from parser_service import Parser
from config import Config
import tools

class WebApp():
	def __init__(self, chan:queue.Queue, conf_base:Config, bot_service:TelegramBotService, parser_service:ParserSpcs) -> None:
		self.app = Flask(__name__)
		
		self.conf_base = conf_base
		self.conf_log = self.read_file_log()
		self.conf_users = Config(self.conf_base.get("file_users"))
		self.conf_categories = Config(self.conf_base.get("file_categories"))
		self.conf_cache_collect_images = Config(self.conf_base.get("file_cache_collect_images"))

		self.category_value = self.conf_base.get("category_value")
		self.count_pic_value = self.conf_base.get("count_pic_value")

		self.parser_service = parser_service
		self.bot_service = bot_service
		
		self.collect_images = []
		
		self.flagLaunchBot = False
		self.flagIsLoadedImagesFromCache = False

		self.setup_routes()
		self.setup_images_cache()

	def setup_images_cache(self) -> None:
		if self.flagIsLoadedImagesFromCache == False:
			self.collect_images = self.conf_cache_collect_images.to_collect_images()
			self.flagIsLoadedImagesFromCache =  True

	def read_file_log(self) -> str:
		with open(self.conf_base.get("file_log")) as file:
			data_file = file.read().split("\n")[::-1]
			result = ''.join(f"{line}\n\n" for line in data_file)
			return result
			

	def receiver_chan_status_bot(self, chan:queue.Queue) -> None:
		logging.info("start receiver channel")
		while True:
			try:
				chan_vlaue = chan.get()
			except Exceptiona as e:
				continue
			else:
				if chan_vlaue == "start":
					flagLaunchBot = True
				elif chan_vlaue == "abort":
					flagLaunchBot = False
				chan.task_done()


	def render_settings(self) -> str:
			return render_template('settings.html', 
		var_api_key_bot = self.conf_base.get("bot_token"),
		var_name_bot = self.conf_base.get("bot_name"),
		var_status_bot = self.flagLaunchBot,
		var_last_started_bot = self.conf_base.get("bot_last_started"))

	def setup_routes(self) -> str:

		@self.app.route('/get_data')
		def get_data():

			return jsonify({'content': 'Это динамически обновленный контент.'})

		@self.app.route('/settings')
		def settings() -> str:
			return self.render_settings()

		@self.app.route('/settings_apply', methods=['POST'])
		def settings_apply() -> str:
				self.conf_base.bot_token = request.form['bot_token']
				self.conf_base.bot_name = request.form['bot_name']
				self.conf_base.bot_last_started = request.form['bot_last_started']
				self.conf_base.bot_status = request.form['bot_status']
				self.conf_base.resave()
				return self.render_settings()

		@self.app.route('/dash_panel')
		def dash_panel() -> str:
			return render_template('dash_panel.html')

		@self.app.route('/desk_space_random_pic')
		def desk_space_random_pic() -> str:
			self.collect_images +=  self.get_collect_image_random_categories()
			self.conf_cache_collect_images.rewrite_from_collect_image_item(self.collect_images)
			return render_template('desk_space.html', collect_images=self.collect_images[::-1], category_value=self.category_value, count_pic_value=self.count_pic_value)
		

		@self.app.route('/desk_space_clear_conf')
		def desk_space_clear_conf() -> str:
			self.collect_images = []
			self.conf_cache_collect_images.data = []
			category_value = "human"
			count_pic_value = "1"
			return render_template('desk_space.html', collect_images=self.collect_images[::-1], category_value=self.category_value, count_pic_value=self.count_pic_value)

		@self.app.route('/desk_space_apply_conf', methods=['POST'])
		def desk_space_apply_conf():
			form = request.form
			self.category_value = form['category_value']
			self.count_pic_value = int(form['count_pic_value'])
			self.collect_images += self.get_collect_image()
			self.conf_cache_collect_images.rewrite_from_collect_image_item(self.collect_images)
			return render_template('desk_space.html', collect_images=self.collect_images[::-1], category_value=self.category_value, count_pic_value=self.count_pic_value)
		
		@self.app.route('/')
		def app_root() -> str:
			return render_template('desk_space.html')
		
		@self.app.route('/desk_space')
		def desk_space() -> str:
			return render_template('desk_space.html', collect_images=self.collect_images[::-1], category_value=self.category_value, count_pic_value=self.count_pic_value)

		@self.app.route('/logs')
		def logs():
			return render_template('logs.html', logs_text=self.conf_log)

		@self.app.route('/users')
		def users():
			return render_template('users.html', conf_users=self.conf_users.to_str())

		@self.app.route('/users_apply', methods=['POST'])
		def users_apply():
			data_str = request.form['text']
			self.conf_users.rewrite_from_str(data_str)
			return render_template('users.html', conf_users=self.conf_users.to_str())


		@self.app.route('/parser')
		def parser():
			return render_template('parser.html',conf_parser=self.conf_categories.to_str())

		@self.app.route('/parser_apply', methods=['POST'])
		def parser_apply():
			data_str = request.form['text']
			self.conf_categories.rewrite_from_str(data_str)
			return render_template('parser.html',conf_parser=self.conf_categories.to_str())

	def get_collect_image(self) -> list[tools.CollectImageItem]:
		temp_collect_images = []
		for index in range(int(self.count_pic_value)):
			url_image = self.parser_service.get_url_random_page_from_category(self.category_value)
			temp_collect_images.append(tools.CollectImageItem(len(self.collect_images)+len(temp_collect_images)-1,url_image))		
		return temp_collect_images

	def get_collect_image_random_categories(self) -> list[tools.CollectImageItem]:
		temp_collect_images = []
		for index in range(int(self.count_pic_value)):
			categories = list(self.conf_categories.data.keys())
			self.category_value = categories[random.randint(0,len(categories)-1)]
			url_image = self.parser_service.get_url_random_page_from_category(self.category_value)
			temp_collect_images.append(tools.CollectImageItem(len(self.collect_images)+len(temp_collect_images)-1,url_image))		
		return temp_collect_images

	def start_app(self, chan:queue.Queue) -> None:
		logging.info("start web app")
		self.app.run(debug=False)

	def start_bot(self, chan:queue.Queue) -> None:
		logging.info("start bot telegram")
		self.bot_service.polling()


def main() -> None:
	arg_namefile_config = argparse.ArgumentParser()
	arg_namefile_config.add_argument("-c", "--config", help="path file config", required=str)
	params = arg_namefile_config.parse_args()

	conf_base = Config(params.config)

	logging.basicConfig(filename=conf_base.get("file_log"), level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

	chan_signal_work_status = queue.Queue()
	
	bot_service = TelegramBotService(chan_signal_work_status, conf_base)
	parser_service = ParserSpcs(conf_base)

	webapp = WebApp(chan_signal_work_status, conf_base, bot_service, parser_service)

	def launch_threads() -> None:
		thread_web_app = threading.Thread(target=webapp.start_app, args=(chan_signal_work_status,))
		thread_tg_bot = threading.Thread(target=webapp.start_bot, args=(chan_signal_work_status,))
		thread_receiver_chan = threading.Thread(target=webapp.receiver_chan_status_bot, args=(chan_signal_work_status,))

		thread_web_app.start()
		thread_tg_bot.start()
		thread_receiver_chan.start()

		thread_web_app.join()
		thread_tg_bot.join()
		thread_receiver_chan.join()

	launch_threads()


if __name__ == "__main__":main()