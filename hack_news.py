#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# HackNews IRC Bot
# Coded by ins3c7 and Zirou
#
# Coded for Priv8 Server
#
# Thanks xin0x, hc0d3r, HyOgA, idz, chk_, vL, VitaoDoidao, psycco, PoMeRaNo and all the #NOSAFE family.
#
# Let's Rock! ;D
#
#

import json, os, socket, time, base64, sys, threading, random, urllib2
import unidecode, requests, BeautifulSoup, tweepy, facebook
from imgurpython import ImgurClient

import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

reload(sys)
sys.setdefaultencoding('Cp1252')

os.system('clear')

class HackNews:

	def __init__(self, server, port, nick, name, email, channel, ajoin, admin, prefix, verbose, banner, xplAlive, owner, Imgur):

		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.s.connect((server, port))
		except:
			print 'ERRO: Não foi possível conectar ao HOST: {} e PORTA: {}'.format(str(server),str(port))
			time.sleep(5)
			exit(1)

		time.sleep(0.5)
		self.s.recv(4096)
		self.nick = nick
		self.name = name
		self.email = email
		self.channel = channel
		self.ajoin = ajoin
		self.admin = admin
		self.server = server
		self.prefix = prefix
		self.verbose = verbose
		self.banner = banner
		self.xplAlive = xplAlive
		
		self.owner = owner
		self.Imgur = Imgur

		self.portscan_find = False
		self.data = ''
		self.command = None
		self.close = False

		self.log_dir = os.path.abspath('log')

		if not os.path.exists(self.log_dir):
			os.mkdir(self.log_dir)

		print '\nInicializando...\n'

	def SendCommand(self, cmd):
		comm = cmd + '\r\n'
		self.s.send(comm)

	def SendMsg(self, canal, msg):
		msg = msg + '\r\n'
		self.s.send('PRIVMSG ' + canal + ' ' + msg + '\r\n')

	def SendPingResponse(self):
		if self.data.find('PING') != -1:
			self.SendCommand('PONG ' + self.data.split()[1])

	def Logging(self, canal, nick, message):
		if canal == self.nick:
			canal = nick
		canal = canal.upper()
		f = open('log/'+ canal +'.log', 'a')
		f.write(message +'\n')
		f.close()

	def SendAllChans(self, nick, canal, message):
		try:
			for channel in ajoin:
				self.SendMsg(channel, str(message) + ' ')
			self.SendMsg(canal, self.banner + 'Mensagens enviadas. ')
		except:
			self.SendMsg(canal, self.banner + 'Algo deu errado. ')

####################

	def imgur(self, link):
		return self.Imgur.upload_from_url(link, config=None, anon=True)['link']
			
	def migre(self, url):
		return requests.get('http://migre.me/api.txt?url='+ url).text

	def face(self, canal, msg, attachment):
		token = ''
		graph = facebook.GraphAPI(token)

		graph.put_wall_post(message=msg, attachment=attachment)

	def tweet(self, canal, msg):
		try:
			cfg = json.load(open(os.path.abspath('')+'/cfg.conf'))
			api = self.tweet_auth(cfg)
			status = api.update_status(status=msg)

		except Exception, e:
			print str(e)
			self.SendMsg('ins3c7', 'DEF TWEET: '+ str(e))

	def marketing(self, banner, ajoin):
		while not self.close:
			for x in range(700):
				if not self.close:
					time.sleep(1)
			self.SendMsg(random.choice(ajoin), banner + 'Follow us on Twitter: 4https://twitter.com/nosafe_')

	def tweet_auth(self, cfg):
		auth = tweepy.OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
		auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
		
		return tweepy.API(auth)

	def news(self, banner, canal):

		url = 'http://thehackernews.com/'
		data = requests.get(url)

		soup = BeautifulSoup.BeautifulSoup(data.text)

		url_site = url.split('//')[1].split('/')[0]

		count = 1

		for post in soup.findAll('a', href=True, attrs= {'class':'url entry-title'}):
			if count < 4:
				self.SendMsg(canal, banner + '[14{}] {}'.format('NEWS', post.text))
				self.SendMsg(canal, banner + '[14{}] 4{} from 14thehackernews'.format('NEWS', self.migre(post['href'])))
			count += 1

	def news_(self):
		url = 'http://thehackernews.com/'
		data = requests.get(url)
		soup = BeautifulSoup.BeautifulSoup(data.text)

		base = []

		for post in soup.findAll('a', href=True, attrs= {'class':'url entry-title'}):
			base.append([post.text, post['href']])

		return base


	def news_mon(self, banner, ajoin):

		old = self.news_()

		self.SendMsg('ins3c7', self.banner + '[14{}] {}'.format('thehackernews.com', 'Initialized! Monitoring...'))

		while not self.close:
			print 'Checando THEHACKERNEWS..'
			try:
				new = self.news_()
				if new[0][0] != old[0][0]:
					for canal in ajoin:
						self.SendMsg(canal, banner + '[14{}] {}'.format('EXPLOIT', 'New Post!'))
						self.SendMsg(canal, banner + '[14{}] {}'.format('EXPLOIT', new[0][0]))
						self.SendMsg(canal, banner + '[14{}] 4{}'.format('EXPLOIT', new[0][1]))
					self.tweet(canal, new[0][0] +'\n\n'+ self.migre(new[0][1]))
					old = new
				print 'THEHACKERNEWS.. OK'
				
				for x in range(180):
					if not self.close:
						time.sleep(1)
			except Exception, e:
				print 'THEHACKERNEWS ERROR:', str(e)			

	def xpl(self, names):
		headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
		data = requests.get('https://www.exploit-db.com/', headers=headers)
		soup = BeautifulSoup.BeautifulSoup(data.text)
		
		y = 0
		base = {}


		for table in soup.findAll('table', attrs={'class':'exploit_list bootstrap-wrapper'}):

			base[names[y]] = []

			for x in range(7):
				date = table.findAll('td', attrs={'class':'date'})[x].text
				author = table.findAll('td', attrs={'class':'author'})[x].text
				description = table.findAll('td', attrs={'class':'description'})[x].text
				link = str(table.findAll('td', attrs={'class':'description'})[x]).split('href="')[1].split('">')[0]

				base[names[y]].append([date, author, description, link])

		 	y += 1

		return base

	def xlp_mon(self, banner, ajoin):
		categories = ['Remote Exploits', 'Web Application Exploits', \
				'Local & Privilege Escalation Exploits', 'PoC & Denial of Service Exploits', \
				'Exploit Shellcode Archive', 'Archived Security Papers']

		old = self.xpl(categories)

		# self.SendMsg('ins3c7', self.banner + '[14{}] {}'.format('exploit-db.com', 'Initialized! Monitoring...'))
		
		while not self.close:
			# print 'Checando EXPLOIT-DB..'
			try:
				new = self.xpl(categories)
				for category in categories:
					if new[category][0][2] != old[category][0][2]:
						for canal in ajoin:
							self.SendMsg(canal, banner + '[14{}] {}'.format('EXPLOIT', 'New exploit available!'))
							self.SendMsg(canal, banner + '[14{}] Title: 15{}'.format('EXPLOIT', new[category][0][2]))
							self.SendMsg(canal, banner + '[14{}] Author: 15{} / Date: 15{}'.format('EXPLOIT', new[category][0][1], new[category][0][0]))
							self.SendMsg(canal, banner + '[14{}] Link: 4{}'.format('EXPLOIT', new[category][0][3]))
						self.tweet(canal, 'New exploit:\n'+ category +'\n'+ new[category][0][2] +'\n\n'+ self.migre(new[category][0][3]))
						old = new
				# print 'EXPLOIT-DB.. OK'
				
				for x in range(180):
					if not self.close:
						time.sleep(1)
			except Exception, e:
				print 'EXPLOIT-DB ERROR:', str(e)

	def ycombinator(self):
		url = 'https://news.ycombinator.com/newest'
		data = requests.get(url)
		soup = BeautifulSoup.BeautifulSoup(data.text)
		base = []

		for post in soup.findAll('td', attrs={'class':'title'}):
			try:
				title = unidecode.unidecode(post.text)
				link = str(post).split('href="')[1].split('"')[0]
				base.append([title, link])
			except:
				pass

		return base

	def ycombinator_mon(self, banner, ajoin):
		old = self.ycombinator()
		self.SendMsg('ins3c7', self.banner + '[14{}] {}'.format('ycombinator.com', 'Initialized! Monitoring...'))

		while not self.close:
			print 'Checando YCOMBINATOR...'
			try:
				new = self.ycombinator()
				if new[0][0] != old[0][0]:
					for canal in ajoin:
						self.SendMsg(canal, banner + '[14{}] {}'.format('NEWS', new[0][0]))
						self.SendMsg(canal, banner + '[14{}] 4{} from 14ycombinator'.format('NEWS', self.migre(new[0][1])))
					self.tweet(canal, str(new[0][0])[0:50] +'...\n@'+ random.choice(followed) +'\n\n'+ self.migre(new[0][1]))
					old = new

				print 'YCOMBINATOR... OK'
				for x in range(10):
					if not self.close:
						time.sleep(1)
			except Exception, e:
				print 'YCOMBINATOR ERROR:', str(e)

	def ycomb0(self, banner, ajoin):
		url = 'https://news.ycombinator.com/'
		while not self.close:
			data = requests.get(url)
			soup = BeautifulSoup.BeautifulSoup(data.text)
			x=0;base = []
			for post in soup.findAll('td', attrs={'class':'title'}):
				if len(post.text) > 5:
					title = unidecode.unidecode(post.text)
					link = str(post).split('href="')[1].split('"')[0]
					base.append([title, link])
					x+=1
					if x > 30:
						break
			print 'CHECKING YCOMB0...'
			title, link = random.choice(base)
			posted_file = open('news.txt', 'r').readlines()
			if (title+'\n') not in posted_file:
				link = self.migre(link)
				for canal in ajoin:
					self.SendMsg(canal, banner + '[14{}] {}'.format('NEWS', title))
					self.SendMsg(canal, banner + '[14{}] 4{} from 14ycombinator'.format('NEWS', link))
				attachment =  {
				    'name': title,
				    'link': link,
				    }
				try:
					self.face(canal, title, attachment)
				except Exception, e:
					self.SendMsg('ins3c7', 'YCOMB0: '+ str(e))
				self.tweet(canal, str(title)[0:50] +'...\n@'+ random.choice(self.followers) +'\n\n'+ link)
				
				post_ap = open('news.txt', 'a')
				post_ap.write(title+'\n')
				post_ap.close()

				# print 'CHECKING YCOMB0... OK'
			else:
				# print 'CHECKING YCOMB0... OK (N0THING)'
				for x in range(10):
					if not self.close:
						time.sleep(1)	
				continue
			for x in range(888):
				if not self.close:
					time.sleep(1)

	def hckrnews(self, banner, ajoin):
		url = 'https://hckrnews.com/'
		while not self.close:
			data = requests.get(url)
			soup = BeautifulSoup.BeautifulSoup(data.text)
			x=0;base = []
			for post in soup.findAll('li', attrs={'class':'entry row'}):
				if len(post.text) > 5:
					title = unidecode.unidecode(post.text.replace('&nbsp;', '').replace('&apos;', "'")).lstrip('0123456789')
					link = 'http://'+ str(post.findAll('a')[1]).split('//')[1].split('">')[0]
					base.append([title, link])
					x+=1
					if x > 20:
						break

			# print 'CHECKING HCKRNEWS...'

			get_title, link = random.choice(base)
			posted_file = open('news.txt', 'r').readlines()

			title_from = get_title[::-1].split('(')[0][::-1].rstrip(')')
			title = get_title.replace(get_title[::-1].split('(')[0][::-1].rstrip(')'), '').rstrip('()')

			if (title+'\n') not in posted_file:
				link = self.migre(link)
				
				title_pt = str((requests.get('http://api.mymemory.translated.net/get?q={}&langpair=en|pt'.format(title)).json())['responseData']['translatedText']).encode('utf-8')
				
				for canal in ajoin:
					self.SendMsg(canal, banner + '[14{}] {}'.format('NEWS', title))
					self.SendMsg(canal, banner + '[14{}] 4{} from 14{}'.format('NEWS', link, title_from))
				
				attachment =  {'name': title,'link': link,}

				try:
					print '...'
					#self.face(canal, '', attachment)
					#self.tweet(canal, str(title)[0:50] +'...\n@'+ random.choice(self.followers) +'\n\n'+ link)
				except Exception, e:
					self.SendMsg('ins3c7', 'HCKRNEWS: '+ str(e))
				
				post_ap = open('news.txt', 'a')
				post_ap.write(title+'\n')
				post_ap.close()

				# print 'CHECKING HCKRNEWS... OK'
			else:
				# print 'CHECKING HCKRNEWS... OK (N0THING)'
				for x in range(10):
					if not self.close:
						time.sleep(1)	
				continue
			
			for x in range(7800):
				if not self.close:
					time.sleep(1)

	def Parse(self, banner, canal, user, cmd):
		tmp = cmd.split()
		numargs = len(tmp)
		fmt = []

		if (len(str(cmd).split()) == 0):
			return
			
		command = cmd
		command = command.split()

		# for i in range(numargs):
		# 	fmt.append(tmp[i] + ' ')

		# if user in self.admin:

		########## FUNCOES
		
		if len(command) == 1:
			if canal != self.nick:
				if command[0] == 'help' or command[0] == 'ajuda':
					self.SendMsg(canal, banner + 'Bot under construction....')

			if command[0] == 'rehash':
				if user == self.owner:
					time.sleep(1)
					self.SendCommand('QUIT Like #NoSafe -> https://fb.com/NoSafe.Priv8 ')
					self.s.close()
					self.close = True
					exit(1)
				else:
					self.SendMsg(canal, banner + '4Você não tem permissão.')


			if command[0] == 'news':
				if user in self.admin:
					try:
						self.news(banner, canal)
					except Exception, e:
						self.SendMsg(canal, banner + 'Wrong!')
						print str(e)
						self.SendMsg('ins3c7', 'command news'+ str(e))
				else:
					self.SendMsg(canal, banner + '4Você não tem permissão.')

		else:

			if command[0] == 'join':
				if user in self.admin:
					if command[1][0] == '#':
						join_channel = command[1]
					else:
						join_channel = '#' + command[1]
					self.SendCommand('JOIN %s' % join_channel)
				else:
					self.SendMsg(canal, banner + '4Você não tem permissão.')

			if command[0] == 'part':
				if user in self.admin:
					if command[1][0] == '#':
						part_channel = command[1]
					else:
						part_channel = '#' + command[1]
					self.SendCommand('PART %s Let\'s Rock!' % part_channel)
				else:
					self.SendMsg(canal, banner + '4Você não tem permissão.')

			if command[0] == 'cmd':
				if user == self.owner:
					self.SendCommand(' '.join(command[1:]))
				else:
					self.SendMsg(canal, banner + '4Você não tem permissão.')

			if command[0] == 'tweet':
				if user in self.admin:
					msg = ' '.join(command[1:]) + '\n\nPosted by ' + user + ' from ' + canal 
					try:
						self.tweet(canal, msg)
						print canal, self.banner + 'Tweet posted in 4https://twitter.com/nosafe_'
						self.SendMsg(canal, self.banner + 'Tweet posted in 4https://twitter.com/nosafe_')
					except Exception, e:
						self.SendMsg('ins3c7', 'if command[0] == tweet:'+ str(e))
						pass
				else:
					self.SendMsg(canal, banner + '4Você não tem permissão.')

			if command[0] == 'fb':
				if user in self.admin:
					msg = ' '.join(command[1:])
					try:
						if msg.find('///') != -1:
							token = ''
							graph = facebook.GraphAPI(token)
							link = msg.split('///')[1].lstrip()
							
							if link.find('imgur') == -1:
								if link.find('.gif') == -1:
									link = self.imgur(link)

							msg = msg.split('///')[0] + '\n\nPosted by ' + user + ' from ' + canal
							picture = urllib2.urlopen(link)
							graph.put_photo(picture, message=msg)
							self.SendMsg(canal, self.banner + 'Posted in FACEBOOK 4https://fb.com/NoSafe.Priv8/')
						
						elif msg.find('###') != -1:
							link = msg.split('###')[1].lstrip()
							msg = msg.split('###')[0] + '\n\nPosted by ' + user + ' from ' + canal
							self.face(canal, msg, attachment={'link':link})
							self.SendMsg(canal, self.banner + 'Posted in FACEBOOK 4https://fb.com/NoSafe.Priv8/')
						
						else:
							self.face(canal, msg, attachment={})
							self.SendMsg(canal, self.banner + 'Posted in FACEBOOK 4https://fb.com/NoSafe.Priv8/')
					except:
						self.SendMsg('ins3c7', 'if command[0] == face'+ str(e))
						pass
				else:
					self.SendMsg(canal, banner + '4Você não tem permissão.')					

			if command[0] == 'social':
				if user in self.admin:
					msg = ' '.join(command[1:]) + '\n\nPosted by ' + user + ' from ' + canal + '\n\nhttp://priv8.jp'
					try:
						self.face(canal, msg, attachment={})
						self.tweet(canal, msg)
						self.SendMsg(canal, self.banner + 'Posted in Facebook and Twitter.')
					except:
						self.SendMsg('ins3c7', 'if command[0] == face'+ str(e))
						pass
				else:
					self.SendMsg(canal, banner + '4Você não tem permissão.')	

	def run(self):

		self.SendCommand('NICK ' + self.nick)
		self.SendCommand('USER ' + self.nick + ' ' + self.name + 
			' ' + self.email + ' :' +
			base64.b16decode(''))

		joined = False
		self.xplAlive = False

		version_check = False

		while not self.close:

			self.data = self.s.recv(4096)
			
			if self.verbose:
				print self.data

			if str(self.data).find('VERSION') != -1:
				exit(1)

			self.SendPingResponse()
			
			time.sleep(0.5)
			
			for channel in ajoin:self.s.send('JOIN {}\r\n'.format(channel))


			if str(self.data).find('PRIVMSG') != -1: # Confere se o dado recebido foi uma mensagem private ou para algum canal
				
				msg_time  = time.strftime('%H:%M:%S')		# Define a hora da mensagem
				user_nick = self.data.split('!')[0][1:] 	# Filtra o nick
				try:
					user_host = self.data.split()[0].split('@')[1] # Tenta filtrar o host (Variável ainda não usada)
				except:
					pass
				
				pre_user_msg	= self.data[1:].split('PRIVMSG')[1].split()[1:]	# Trabalha a mensagem bruta
				user_msg 		= ' '.join(pre_user_msg).lstrip(':') 					# Filtra apenas a mensagem
				user_channel 	= str(self.data.split('PRIVMSG')[1].split()[0])	# Filtra o canal

				print '[%s] %s %s: %s' % (str(msg_time), str(user_channel), str(user_nick), str(user_msg)) # Imprime a mensagem na tela do bot

				text_log = '[{}] {}: {}'.format(str(msg_time), str(user_nick), str(user_msg)) # Filtra o a mensagem para a função Logging()

				
				self.Logging(str(user_channel), str(user_nick), str(text_log)) # Grava os logs

				# Banner oficial:
				banner = '9(hACk4NeWs9) '

				try:
					if (str(user_msg)[0] == str(self.prefix)):
						self.Parse(banner, user_channel, user_nick, user_msg.lstrip(str(self.prefix))) # Chama a função Parse que gera todas as outras funções
				except:
					continue

			
			''' THREADS '''

			# market = threading.Thread(target=self.marketing, args=(self.banner, self.ajoin))
			# newsmon = threading.Thread(target=self.news_mon, args=(self.banner, self.ajoin))
			xplmon = threading.Thread(target=self.xlp_mon, args=(self.banner, self.ajoin))
			ycommon = threading.Thread(target=self.ycomb0, args=(self.banner, self.ajoin))
			hckr = threading.Thread(target=self.hckrnews, args=(self.banner, self.ajoin))
			
			if not self.xplAlive and joined:
				try:
					self.xplAlive = True
					# market.start()
					# newsmon.start()
					# ycommon.start()
					xplmon.start()
					hckr.start()

				except Exception, e:
					print str(e)
					self.SendMsg('ins3c7', 'THREADINGS START: '+ str(e))
				except KeyboardInterrupt:
					print 'INTERROMPIDO PELO USUÁRIO'
					self.close = True

			''' END/THREADS '''


#			self.SendCommand('NICK ' + self.nick)

			
if __name__ == '__main__':

	servidor = 'irc.priv8.jp'
	porta = 6667
	nick = 'HACKNEWS'
	nome = '#nosafe'
	email = 'hacknews@priv8.jp'
	canal_principal = '#netsplit' # Canal de comando do bot
	ajoin = [canal_principal, '#nosafe', '#priv8', '#1984']
	owner = 'ins3c7'
	admin = ['ins3c7', 'Zirou', 'xin0x', 'vL', 'hc0d3r'] # Nicks para acessos à funções especiais do bot
	prefix = '.'
	verbose = False
	xplAlive = False

	conf = json.load(open(os.path.abspath('')+'/config.conf'))
	Imgur = ImgurClient(conf['imgur_client_id'], conf['imgur_client_secret'], conf['imgur_access_token'], conf['imgur_refresh_token'])

	simple_banner = '9(hACk4NeWs9) '


bot = HackNews(servidor, porta, nick, nome, email, canal_principal, ajoin, admin, prefix, verbose, simple_banner, xplAlive, owner, Imgur)
bot.run()
