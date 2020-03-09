from telebot.telebot import Bot
import time

b = Bot(open('token.txt','r').read())
b.newCommand_info = False

def helloWorld(bot,userid,params):
	bot.sendMessage(userid,"Hello User")

# b.sendMessage("1","Bot started")

b.newCommand('/helloworld',helloWorld)

def oIQ(update, answer):
	answer[0]['title'] = "helloo"
	# return update['inline_query']['query']

b.onMessage = None
b.onCommand = None
b.onUpdate = None
b.answerInlineQuery = oIQ



# print("main loaded")
