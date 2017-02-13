# -*- coding: utf-8 -*-
import irc3, asyncio
import threading, html, time, traceback
from irc3.utils import as_list
from twitter.stream import Timeout, HeartbeatTimeout, Hangup

__doc__ = '''
==========================================
:mod:`twitter_messages` Feeds plugin
==========================================

Post Twitter Updates into channels.

You must configure `irc3.plugins.social` properly.

Additionally, your config has to contain something like this:

[twitter_messages]
## Optional: default channel
tweet_channel = #channel

## Optional: customize message in channel
tweet_format = "@{screen_name}: {text}"


## some twitter feeds:
identifier = @screen_name
identifier.channels = #channel1 #channel2
[...]

'''

#TODO detecting fake replies
#TODO better self-answer detection

@irc3.plugin
class Plugin:
	requires = [
		'irc3.plugins.social',
	]

	def __init__(self, bot):
		self.bot = bot
		self.twitter_stream = bot.get_social_connection(id='twitter_stream')
		self.twitter_api = self.bot.get_social_connection(id='twitter')
		self.config = self.bot.config.get(__name__, {})
		self.twitter_channels = {}
		self.status_channels = as_list(self.config.get('status_channels'))
		self.tweet_channels = as_list(self.config.get('tweet_channels'))
		self.tweet_format = self.config.get('tweet_format', '@{screen_name}: {text}')
		self.conversation_channels = as_list(self.config.get('conversation_channels'))
		self.conversation_format = self.config.get('conversation_format', '@{screen_name}: {text}')

	def connection_made(self):
		self.bot.log.info('Connected')
		tweet_ids = []
		conversation_ids = []
		for config_key, config_value in self.config.items():
			if config_value and str(config_value).startswith('@') and not config_key.endswith('_format'):
				screen_name = config_value[1:]
				details = self.twitter_api.users.show(screen_name=screen_name)
				if (self.config.get(config_key + '.conversation', False)):
					conversation_ids.append(details["id_str"])
				else:
					tweet_ids.append(details["id_str"])
				self.twitter_channels[screen_name.lower()] = self.tweet_channels
				if self.config.get(config_key + '.channels'):
					self.twitter_channels[screen_name.lower()] = as_list(self.config.get(config_key+'.channels'))
		threading.Thread(target=self.receive_stream, kwargs={'ids': tweet_ids, 'conversation': False}).start()
		threading.Thread(target=self.receive_stream, kwargs={'ids': conversation_ids, 'conversation': True}).start()

	def receive_stream(self, ids, conversation):
		if not ids: return
		if conversation: time.sleep(5)
		output_prefix = 'Conversation stream' if conversation else 'Tweet stream'
		exception_count = 0;
		while True:
			try:
				follow = ','.join(ids)
				stream = self.twitter_stream.statuses.filter(follow=follow)
				self.bot.log.info(output_prefix + ' connected: '+follow)
				self.send_status(output_prefix + ' connected.')
				for tweet in stream:
					self.bot.loop.run_in_executor(None, self.handle_tweet, tweet, conversation)
				self.bot.log.critical(output_prefix + ': Connection lost')
				self.send_status(output_prefix + ': Connection lost')
			except Exception as e:
				exception_count = exception_count + 1;
				self.bot.log.critical(output_prefix + ': EXCEPTION ' + exception_count)
				self.bot.log.exception(e)
				self.send_status(output_prefix + ': EXCEPTION ' + exception_count);
				time.sleep(120 if conversation else 150)
			finally:
				time.sleep(60)
				self.bot.log.info(output_prefix + ' retrying...')
				self.send_status(output_prefix + ' retrying...')

	def send_status(self, status):
		if self.status_channels:
			for status_channel in self.status_channels:
				self.bot.privmsg(status_channel, status)


	def handle_tweet(self, tweet, conversation):
		output_prefix = 'Conversation stream' if conversation else 'Tweet stream'
		if tweet is None:
			 self.bot.log.info(output_prefix + ' data: None')
		elif tweet is Timeout:
			self.bot.log.info(output_prefix + ' data: Timeout')
		elif tweet is Hangup:
			self.bot.log.info(output_prefix + ' data: Heartbeat Timeout')
		elif 'retweeted_status' in tweet:
			self.bot.log.debug(output_prefix + ' data: Retweet ' + tweet['id_str'])
			# + '/' + tweet['retweeted_status']['id_str'])
			self.bot.log.debug(str(tweet))
		elif 'text' in tweet:
			self.bot.log.info(output_prefix + ' data: Tweet @' + tweet['user']['screen_name'] + '/' + tweet['id_str'] )
			self.bot.log.debug(str(tweet))
			screen_name = tweet['user']['screen_name']
			url = 'https://twitter.com/' + screen_name + '/status/' + tweet['id_str']
			text = html.unescape(tweet['text'])
			if 'extended_tweet' in tweet and 'full_text' in tweet['extended_tweet']:
				text = html.unescape(tweet['extended_tweet']['full_text'])
			user = tweet['user']['screen_name'].lower()
			processed_channels = []
			if user in self.twitter_channels:
				reply_to = tweet['in_reply_to_screen_name']
				if reply_to == None or reply_to.lower() == user:
					for tweet_channel in self.twitter_channels[user]:
						if not tweet_channel in processed_channels:
							self.bot.privmsg(tweet_channel,
								self.tweet_format.format(screen_name=screen_name, text=text, url=url))
							processed_channels.append(tweet_channel)
			if conversation and self.conversation_channels:
				for conversation_channel in self.conversation_channels:
					if not conversation_channel in processed_channels:
						self.bot.privmsg(conversation_channel,
							self.conversation_format.format(screen_name=screen_name, text=text, url=url))
						processed_channels.append(conversation_channel)
		elif 'delete' in tweet:
			self.bot.log.info(output_prefix + ' data: Deleted tweet ' + tweet['delete']['status']['id_str'] )
			self.bot.log.debug(str(tweet))
		elif 'limit' in tweet:
			self.bot.log.critical(output_prefix + ' data: LIMIT NOTICE')
			self.bot.log.debug(str(tweet))
		else:
			self.bot.log.info(output_prefix + ' data: unknown')
			self.bot.log.info(str(tweet))

