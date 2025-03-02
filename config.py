import json
import tools

class Config():
	def __init__(self, namefile:str) -> None:
		self.namefile = namefile
		try:
			with open(namefile, 'r', encoding='utf-8') as file:
				self.data = json.load(file)
		except json.decoder.JSONDecodeError:
			with open(namefile, 'w', encoding='utf-8') as file:
				file.write("[]")
				self.data = []

	def to_collect_images(self) -> list[tools.CollectImageItem]:
		result = []
		for item_str in self.data:
			item_str = f"{item_str}".replace("'","\"")				
			item_json = json.loads(item_str)
			result.append(tools.CollectImageItem(item_json["index"], item_json["url"]))
		return result

	def to_dict(self) -> dict:
		return self.data
		
	def to_str(self) -> str:
		with open(self.namefile, "r", encoding='utf-8') as temp_file: return temp_file.read()

	def get(self, key:str) -> str:
		return f"{self.data[key]}"
	
	def rewrite_from_collect_image_item(self, collect_image_item:list[tools.CollectImageItem]) -> None:
		temp_array = []
		with open(self.namefile, 'w', encoding='utf-8') as file:
			for item in collect_image_item:
				temp_dict = { "index":str(item.index),"url":str(item.url)}
				temp_array.append(temp_dict)
			json.dump(temp_array, file, ensure_ascii=False, indent=4)

	def rewrite_from_str(self, str_data:str) -> None:
		dict_data = json.loads(str_data)
		with open(self.namefile, 'w', encoding='utf-8') as f:
			json.dump(dict_data, f, ensure_ascii=False, indent=4)

	def rewrite_from_dict(self, dict_data:dict) -> None:
		with open(self.namefile, 'w', encoding='utf-8') as f:
			json.dump(dict_data, f, ensure_ascii=False, indent=4)

	def resave(self) -> None:
		with open(self.namefile, 'w', encoding='utf-8') as f:
			json.dump(self.data, f, ensure_ascii=False, indent=4)

	def rewrite_user_category(self, id_user:str, category:str) -> None:
		c = 0
		for user in self.data:
			if str(self.data[c]["chat_id"]) == str(id_user):
				self.data[c]["category"] = category
				self.resave()
				self.rewrite_from_dict(self.data)
			c+=1




