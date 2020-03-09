from telebot.telebot import Bot
import time

b = Bot(open('token.txt','r').read())
b.newCommand_warning = False

def helloWorld(bot,userid,params):
	bot.sendMessage(userid,"Hello User")

# b.sendMessage("1","Bot started")

b.newCommand('/helloworld',helloWorld)

def oIQ(b,c):
	print("asokd")
	print(b,c)

b.onMessage = None
b.onCommand = None
# b.onUpdate = None
# b.onInlineQuery = oIQ



# print("main loaded")
