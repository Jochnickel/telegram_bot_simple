import urllib.request
import urllib.parse
import json

url = 'https://api.telegram.org/'

class NetworkError(RuntimeError):
	def __init__(self, arg): self.args = arg

class TokenError(RuntimeError):
	def __init__(self): self.args = 'Token not valid'

class UnsubscribedError(RuntimeError):
	def __init__(self): self.args = 'User unsubscribed'

class ApiError(RuntimeError): pass
class UserNotFoundError(RuntimeError): pass

class Api:
	
	def __init__(self, token):
		self.__offset = 0
		try:
			urllib.request.urlopen('%sbot%s/getMe'%(url,token))
			self.__token = token
		except urllib.error.URLError as e: raise NetworkError(e)
		except: raise TokenError()

	def newUpdates(self):
		try:
			r = json.loads(urllib.request.urlopen('%sbot%s/getUpdates?offset=%s'%(url,self.__token,self.__offset)).read().decode('utf-8'))
			if ('result' in r) and r['result']:
				self.__offset = r['result'][-1]['update_id']+1
				return r['result']
			return []
		except urllib.error.URLError: raise NetworkError('No Internet Connection')

	def sendMessage(self,chat_id,msg):
		if not msg: return
		msg = urllib.parse.quote(msg)
		try: urllib.request.urlopen('%sbot%s/sendMessage?chat_id=%s&text=%s'%(url,self.__token,chat_id,msg))
		except urllib.error.HTTPError as e:
			if 403==e.code: raise UnsubscribedError("User has unsubscribed.")
			if 400==e.code: raise UserNotFoundError("User not found")
			raise ApiError("Other sendMessage HTTP Error:",e)
		except urllib.error.URLError as e: raise NetworkError(e)

	def answerInlineQueryEZ(self,inline_query_id,title,text):
		arr = [{'type':'article','message_text':text,'title':title}]
		arr[0]['id'] = id(arr)
		self.answerInlineQuery(inline_query_id,arr)

	def answerInlineQuery(self,inline_query_id,results):
		try:
			results = urllib.parse.quote(json.dumps(results, separators = (',', ':')),safe="[{:,}]")
			url_ = '%sbot%s/answerInlineQuery?inline_query_id=%s&results=%s'%(url,self.__token,inline_query_id,results)
			print(url_)
			u = urllib.request.urlopen(url_)

			return True
		except Exception as e:
			print('ERROR',e)
			return False