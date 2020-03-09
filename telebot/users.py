from . import error
import time
from .database import Database

class cannotRemoveAdminError(RuntimeError):
	def __init__(self, arg): self.args = arg


class Users:
	# __db = Database('')

	def __init__(self, cb_getFirstAdmin = None, db_name = 'users', db_file = 'database.db'):
		self.__db = Database(db_name,db_file,{'users':{},'admins':{},'mods':{},'banned':{}})
		if not 'admins' in self.__db() or not self.__db()['admins']:
			if not callable(cb_getFirstAdmin):
				error("parameter cb_getFirstAdmin must be function")
			firstadmin = cb_getFirstAdmin()
			self.add(firstadmin)
			self.makeAdmin(firstadmin)
			self.__db.saveFile()

	def add(self,userid):
		userid = str(userid)
		if not userid in self.__db()['users']:
			self.__db()['users'][userid] = {'join_time' : int(time.time())}
			self.__db.saveFile()
			return True
		return False

	def remove(self,userid):
		userid = str(userid)
		if userid in self.__db()['users']:
			del self.__db()['users'][userid]
			self.__db.saveFile()
			return True
		return False

	def makeAdmin(self,userid):
		userid = str(userid)
		if not userid in self.__db()['admins']:
			self.__db()['admins'][userid] = True
			self.__db.saveFile()
			return True
		return False

	def isAdmin(self,userid):
		userid = str(userid)
		return userid in self.__db()['admins']

	def removeAdmin(self,userid):
		userid = str(userid)
		if userid in self.__db()['admins']:
			if 1>=len(self.__db()['admins']):
				print('Cannot remove the last admin')
				return False
			del self.__db()['admins'][userid]
			self.__db.saveFile()
			return True
		return False

	def makeMod(self,userid):
		userid = str(userid)
		if not userid in self.__db()['mods']:
			self.__db()['mods'][userid] = True
			self.__db.saveFile()
			return True
		return False

	def isMod(self,userid):
		userid = str(userid)
		return userid in self.__db()['mods']

	def removeMod(self,userid):
		userid = str(userid)
		if userid in self.__db()['mods']:
			del self.__db()['mods'][userid]
			self.__db.saveFile()
			return True
		return False

	def ban(self,userid):
		userid = str(userid)
		if not userid in self.__db()['banned']:
			self.__db()['banned'][userid] = True
			self.__db.saveFile()
			return True
		return False

	def isBanned(self,userid):
		userid = str(userid)
		return userid in self.__db()['banned']

	def unban(self,userid):
		userid = str(userid)
		if userid in self.__db()['banned']:
			del self.__db()['banned'][userid]
			self.__db.saveFile()
			return True
		return False

	def getAllUsers(self):
		return dict(self.__db()['users'])
	
	def dump(self):
		return dict(self.__db())