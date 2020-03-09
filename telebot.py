import asyncio
import time
import threading
import random
import sys
import os
import traceback
from users import Users
from tickets import Tickets
from telegram_api import Api, UnsubscribedError
import logging

logging.basicConfig(filename='log.txt',level=logging.DEBUG)

def __pass(*args): pass

class Bot:
	welcomeMessage	= "Welcome!"
	byeMessage		= "See you!"
	loopInterval	= 1
	newCommand_warning = True

	def __init__(self, apiKey: str):
		self.__api = Api(apiKey)
		self.__users = Users(cb_getFirstAdmin = self.__getFirstAdmin)
		self.__tickets = Tickets()
		def background():
			while True:
				try:
					for u in self.__api.newUpdates():
						self.__onUpdate(u)
						u_id = u['update_id']
						msg = 'message' in u and u['message']
						iq = 'inline_query' in u and u['inline_query']
						if msg:
							m_id = msg['message_id']
							date = msg['date']
							chat = msg['chat']
							from_ = 'from' in msg and msg['from']
							text = 'text' in msg and msg['text']
							entities = 'entities' in msg and msg['entities'] or []
							for e in entities:
								type = e['type']
								offset = e['offset']
								length = e['length']
								if 'bot_command'==type:
									cmd = text[offset:(offset+length)]
									param = text[(offset+length+1):]
									self.__onCommand(cmd,param,e,u)
									# just one Command per message
									break
							self.__onMessage(u)
						if iq:
							iq_id = iq['id']
							from_ = iq['from']
							query = iq['query']
							offset = iq['offset']
							location = 'location' in iq and iq['location']
							self.__onInlineQuery(u)
					time.sleep(self.loopInterval)
				except Exception as e:
					s = ""
					for a in traceback.format_stack(): s += a
					logging.warning("%s %s\n"%(s,e))

		threading.Thread(target = background).start()
		# def console():
		print("Bot loaded! CTRL+C to terminate.\n")
		# threading.Thread(target = console).start()
		

	def __getFirstAdmin(self):
		secret = '/admin %s'%random.randint(10000,99999)
		print("write %s to the Bot to register as admin!"%(secret))
		while True:
			for u in self.__api.newUpdates():
				msg = 'message' in u and u['message']
				if msg and ('text' in msg) and ('from' in msg) and secret==msg['text']:
					i = msg['from']['id']
					self.sendMessage(i,"Success! Print your commands with /cmd")
					print("Success!")
					return i
				elif ('from' in msg):
					input("Bad message from %s. Press Enter to continue"%msg['from']['id'])
			time.sleep(1)

	__commands = {
		'/start'	: { 'run' : lambda self, userid, param: self.__addUser(userid = userid) },
		'/stop'		: { 'run' : lambda self, userid, param: self.__delUser(userid = userid) },

		'/ping'		: { 'run' : lambda self, userid, param: self.sendMessage(userid = userid, msg = '/pong') },
		'/pong'		: { 'run' : lambda self, userid, param: self.sendMessage(userid = userid, msg = '/ping') },

		'/ban'		: { 'run' : lambda self, userid, param: self.__setBan(userid, param.split() and param.split()[0], True), 'mustbe' : 'mod' },
		'/unban'	: { 'run' : lambda self, userid, param: self.__setBan(userid, param.split() and param.split()[0], False), 'mustbe' : 'mod' },

		'/mod'		: { 'run' : lambda self, userid, param: self.__setMod(userid, param.split() and param.split()[0], True), 'mustbe' : 'admin' },
		'/unmod'	: { 'run' : lambda self, userid, param: self.__setMod(userid, param.split() and param.split()[0], False), 'mustbe' : 'admin' },
		
		'/admin'	: { 'run' : lambda self, userid, param: self.__setAdmin(userid, param.split() and param.split()[0], True), 'mustbe' : 'admin' },
		'/deladmin'	: { 'run' : lambda self, userid, param: self.__setAdmin(userid, param.split() and param.split()[0], False), 'mustbe' : 'admin' },

		'/listusers': { 'run' : lambda self, userid, param: self.__printUsers(userid), 'mustbe' : 'admin' },
		'/errorlog'	: { 'run' : lambda self, userid, param: self.__printErrors(userid, *param.split(' ',1)), 'mustbe' : 'admin' },
		
		'/msg'		: { 'run' : lambda self, userid, param: self.__msg(userid, *param.split(' ',1)), 'mustbe' : 'mod'},

		'/cmd'		: { 'run' : lambda self, userid, param: self.__printCommands(userid, *param.split(' ',1)), 'mustbe' : 'mod'},

		'/tickets'	: { 'run' : lambda self, userid, param: self.__cmdTickets(userid, param), 'mustbe' : 'mod'},
		'/supp'		: { 'run' : lambda self, userid, param: self.__addTicket(userid, param) },
	}

	def newCommand(self, name: str, cb_func):
		if '/'!=name[0]: name = '/' + name
		if name in self.__commands: raise RuntimeError("Command already exists")
		if not callable(cb_func): raise RuntimeError("No function provided")
		self.__commands[name] = { 'run' : cb_func }
		if self.newCommand_warning:
			print("Command %s registered.\nMake sure the callback function looks like foo(self,cmd,params)!\n%s.newCommand_warning = True"%(name,self))

	def __printErrors(self,userid, clear = False):
		try:
			fd = open('log.txt','r')
			self.sendMessage(userid,fd.read() or "Empty log")
		except:
			self.sendMessage(userid,"No log file")
		fd.close()
		if 'clear'==clear: os.remove('log.txt')

	def __printUsers(self,userid):
		self.sendMessage(userid,str(self.__users.dump()))

	def __cmdTickets(self,userid,p):
		userid = str(userid)
		if not p: return self.__printListTickets(userid)
		cmd, *param = p.split(' ',1)
		if 'assign'==cmd:
			if param:
				self.__assignTicket(userid, ticket_id = param[0])
			else:
				self.__printListTickets(userid, filter_assigned = True)
		elif 'unassign'==cmd and param:
			self.__unassignTicket(userid, ticket_id = param[0])
		elif 'resolve'==cmd and param:
			self.__resolveTicket(userid, ticket_id = param[0])

	def __assignTicket(self,userid,ticket_id):
		if self.__tickets.assign(ticket_id,userid):
			self.sendMessage(userid,'Assigned to ticket %s.\nResolve ticket with /tickets resolve %s,\nwithdraw from assignment with /tickets unassign %s'%(ticket_id,ticket_id,ticket_id))
		else:
			self.sendMessage(userid,"Can't assign to ticket %s."%(ticket_id))

	def __unassignTicket(self,userid,ticket_id):
		s = self.__tickets.unassign(ticket_id,userid) and 'Unassigned' or "Can't unassign"
		self.sendMessage(userid,'%s to ticket %s'%(s,ticket_id))

	def __resolveTicket(self,userid,ticket_id):
		r = self.__tickets.resolve(ticket_id,userid) and 'Resolved' or "Can't resolve"
		self.sendMessage(userid,'%s ticket %s'%(r,ticket_id))

	def __addTicket(self,userid: int,txt: str):
		if txt:
			self.__tickets.add(userid,txt)
			self.sendMessage(userid,'Message received 👍. Please wait for an answer.')
		else:
			self.sendMessage(userid,'Please write a text after /supp')
		return False

	def __printListTickets(self,userid,filter_assigned = False):
		l = self.__tickets.list()
		for t in l:
			if filter_assigned and not ('assignee' in l[t] and str(userid)==l[t]['assignee']): continue
			self.sendMessage(userid, str(l[t]))
		if not filter_assigned:
			self.sendMessage(userid, l and 'assign to a ticket with /tickets assign <id>' or 'No Tickets!')

	def __canUserUseComm(self,userid,cmd):
		# TODO: unuglify
		cmd = (cmd in self.__commands) and (cmd) or ('/'+cmd)
		c = cmd in self.__commands and 'run' in self.__commands[cmd] and True
		return c and ( self.__users.isAdmin(userid) or (not 'mustbe' in c) or ('mod'==c['mustbe'] and self.__users.isMod(userid)) )

	def __printCommands(self, userid, param):
		if ""==param:
			text = "Availiable commmands:\n"
			for c in self.__commands:
				if self.__canUserUseComm(userid,c):
					text += "%s \n"%(c)
			self.sendMessage(userid,text)
		elif param and self.__canUserUseComm(userid,param):
			self.sendMessage(userid,param)

	def __onCommand(self,cmd,param,ent,upd):
		userid = upd['message']['from']['id']
		print(userid,cmd,param)
		if self.__canUserUseComm(userid, cmd):
			self.__commands[cmd]['run'](self, userid, param)
			if callable(self.onCommand):
				self.onCommand(upd)

	def __onInlineQuery(self,u):
		if callable(self.onInlineQuery):
			self.onInlineQuery(u)

	def __onMessage(self,u):
		if callable(self.onMessage):
			self.onMessage(u)

	def __onUpdate(self,u):
		if callable(self.onUpdate):
			self.onUpdate(u)

	def onInlineQuery(self,*f): print("Bot.onInlineQuery() placeholder",f)
	def onMessage(self,*f): print("Bot.onMessage() placeholder",f)
	def onCommand(self,*f): print("Bot.onCommand() placeholder",f)
	def onUpdate(self,*f): print("Bot.onUpdate() placeholder",f)

	def sendMessage(self,userid,msg):
		try: self.__api.sendMessage(userid, msg)
		except UnsubscribedError: print("Can't message %s: unsubscribed"%(userid))
		except Exception as e:
			traceback.print_stack(limit = -1)
			print("Error [Bot.sendMessage]:",e)

	def __msg(self,from_id,to_id,msg = None):
		if None==msg: return
		toAll = 'all'==to_id
		if (toAll or not self.__users.isMod(from_id)) and not self.__users.isAdmin(from_id): return
		to = toAll and self.__users.getAllUsers() or {to_id : True}
		for u in to:
			self.sendMessage(u,msg)

	def __addUser(self,userid):
		userid = str(userid)
		if self.__users.add(userid):
			self.sendMessage(userid,self.welcomeMessage)

	def __delUser(self,userid):
		userid = str(userid)
		if self.__users.remove(userid):
			self.sendMessage(userid,self.byeMessage)

	def __setMod(self,from_id,to_id,yes):
		if []==from_id: return
		if not self.__users.isAdmin(from_id): return print("%s attempted admin command"%(from_id))
		if []==to_id: return self.sendMessage(from_id,'Usage: /%s <id>'%(yes and 'mod' or 'unmod'))
		if yes and self.__users.makeMod(to_id):
			self.sendMessage(to_id,'You are now a Mod! List your commands with /cmd')
			self.sendMessage(from_id,'👍👍')
		elif not yes and self.__users.removeMod(to_id):
			self.sendMessage(to_id,'You are not a mod anymore!')
			self.sendMessage(from_id,'👍👍')
		else:
			self.sendMessage(from_id,'Usage: /mod <id>')

	def __setAdmin(self,from_id,to_id,yes):
		if []==from_id: return
		if not self.__users.isAdmin(from_id): return print("%s attempted admin command"%(from_id))
		if []==to_id: return self.sendMessage(from_id,'Usage: /%s <id>'%(yes and 'admin' or 'unadmin'))
		if yes and self.__users.makeAdmin(to_id):
				self.sendMessage(to_id,'You are now an Admin 🥳! List your commands with /cmd')
				self.sendMessage(from_id,'👍👍')
		elif not yes and self.__users.removeAdmin(to_id):
			self.sendMessage(to_id,'You are not admin anymore!')
			self.sendMessage(from_id,'👍👍')
		else: self.sendMessage(from_id,"Couldn't remove last admin")

	def __setBan(self,from_id,to_id,yes):
		if []==from_id: return
		if not self.__users.isMod(from_id) and not self.__users.isAdmin(from_id): return print("%s attempted mod command"%(from_id))
		if []==to_id: return self.sendMessage(from_id,'Usage: /%s <id>'%(yes and 'ban' or 'unban'))
		if yes and self.__users.ban(to_id):
				self.sendMessage(to_id,'You are banned for some reason..! You can contact support with /supp help')
				self.sendMessage(from_id,'👍👍')
		elif not yes and self.__users.unban(to_id):
			self.sendMessage(to_id,'You are not banned anymore!')
			self.sendMessage(from_id,'👍👍')
		else: self.sendMessage(from_id,"Couldn't ban user")