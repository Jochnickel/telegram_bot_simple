from .database import Database

class Tickets:
	# __db = Database('')

	def __init__(self, db_name: str = 'tickets', db_file: str = 'database.db'):
		self.__db = Database(db_name,db_file,{'i':0})

	def add(self,user: str,txt : str) -> type(None):
		user = str(user)
		t_id = str(self.__db()['i'])
		self.__db()[t_id], self.__db()['i'] = {'id': t_id, 'user' : user, 'txt' : txt}, self.__db()['i']+1
		self.__db.saveFile()

	def list(self) -> dict:
		l = dict(self.__db())
		del l['i']
		return l

	def rem(self,ticket_id: int):
		ticket_id = str(ticket_id)
		if ticket_id in self.__db():
			del self.__db()[ticket_id]
			self.__db.saveFile()
			return True
		return False

	def assign(self,ticket_id: int, moderator):
		ticket_id = str(ticket_id)
		moderator = str(moderator)
		if (ticket_id in self.__db()) and (not 'assignee' in self.__db()[ticket_id]):
			self.__db()[ticket_id]['assignee'] = moderator
			self.__db.saveFile()
			return True
		return False

	def unassign(self,ticket_id: int, moderator):
		ticket_id = str(ticket_id)
		moderator = str(moderator)
		if (ticket_id in self.__db()) and ('assignee' in self.__db()[ticket_id]) and (moderator==self.__db()[ticket_id]['assignee']):
			del self.__db()[ticket_id]['assignee']
			self.__db.saveFile()
			return True
		return False

	def resolve(self,ticket_id: int, moderator):
		ticket_id = str(ticket_id)
		moderator = str(moderator)
		if (ticket_id in self.__db()) and ('assignee' in self.__db()[ticket_id]) and (moderator==self.__db()[ticket_id]['assignee']):
			return self.rem(ticket_id)
		return False