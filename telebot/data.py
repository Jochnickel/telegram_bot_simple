
class Data:
	__data = {}
	def __init__(self):
		# print("new instance")
		pass
	def __call__(self, key, value = None ):
		if None!=value:
			self.__data[key] = value
			return value
		if not key in self.__data:
			self.__data[key] = Data()
		return self.__data[key]