from config import Config

class StorageJson():
	def __init__(self, namefile:str) -> None:
		self.namefile = namefile
		self.conf = Config(self.namefile)
	def get(self, key:str) -> dict:
		return self.data[key]
		
	def get_array(self, key_filter:str) -> list[dict]:
		array = []
		for _ in self.data:
			array.append(self.data[key_filter])

	def add(self, dict_data:dict) -> None:
		self.conf.data.append(dict_data)
		self.conf.resave(self)

	def add_user(self, name:any, chat_id:any, category:str) -> None:
		self.conf.data.append({
			"name":str(name),
			"chat_id":str(chat_id),
			"category":category,
			"last_started":"none",
		})
		self.conf.resave()

	def find_item_as_str(self, key:any, value:any) -> bool:
		for item_data in self.conf.data:
			if str(key) in item_data:
				if str(item_data[key]) == str(value):
					return True
		return False
