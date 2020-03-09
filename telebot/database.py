import os
import json
from threading import Lock, Timer
from .data import Data
import zlib

# issues: dbs is exposed

class Database:
	
	lock = Lock()
	dbs = {}		#old
	# dbs = Data()	#new


	def __init__(self, uniqueName: str, filename = 'database.db', new_values = {}):
		self.dbFilename = str(filename)
		self.uniqueName = str(uniqueName)
		self.tmpFilename = '%s.new'%filename
		self.oldFilename = '%s.old'%filename

		with Database.lock:
			if not self.dbFilename in Database.dbs: Database.dbs[self.dbFilename] = {}  #old
			# Database.dbs(self.dbFilename)												#new


		try: self.loadFile()
		except Exception as e: print('Error: %s'%e)

		with Database.lock:
			if not self.uniqueName in Database.dbs[self.dbFilename]:
				Database.dbs[self.dbFilename][self.uniqueName] = new_values

		self.saveFile()											# uncaught

	def __call__(self, value = None):
		if None!=value:
			with Database.lock:
				Database.dbs[self.dbFilename][self.uniqueName] = value
			# try:
			self.saveFile()										# uncaught
			# except Exception as e: print('Error: %s'%e)
		return Database.dbs[self.dbFilename][self.uniqueName]


	def saveFile(self):
		# print("saving %s"%self.uniqueName)
		with Database.lock:
			
			s = json.dumps( Database.dbs[self.dbFilename], separators = (',', ':') )
			z = zlib.compress(bytes(s, 'utf-8'))

			tmp = open(self.tmpFilename,'wb')
			tmp.write(z)
			tmp.close()

			# no File when fresh
			try: os.rename(self.dbFilename, self.oldFilename)
			except FileNotFoundError: pass
			os.rename(self.tmpFilename, self.dbFilename)
			# still no file
			try: os.remove(self.oldFilename)
			except FileNotFoundError: pass

	def loadFile(self):
		with Database.lock:
			try:
				fd = open(self.dbFilename, 'rb')
			except (FileNotFoundError):
				try:
					fd = open(self.oldFilename, 'rb')
					os.rename(self.oldFilename, self.dbFilename)
					print("Database loaded from backup")
				except (FileNotFoundError):
					print("No database foud for %s"%self.dbFilename)
					return
			Database.dbs[self.dbFilename] = json.loads(zlib.decompress(fd.read()))
			fd.close()
