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
## Optional: Automatically join & leave channels
auto_join_and_part = true
auto_part_time = 180

## Optional: default channel
tweet_channel = #channel

## Optional: customize message in channel
tweet_format = "@{screen_name}: {text}"

## Optional: status output
status_channels = #status_channel
status_notification_format = {message}
status_tweet_format = "@{screen_name}: {text}"


## some twitter feeds:
identifier = @screen_name
identifier.channels = #channel1 #channel2
[...]

'''

@irc3.plugin
class Plugin:
	requires = [
		'irc3.plugins.social',
	]

	def __init__(self, bot):
		self.bot = bot
		self.twitter_channels = {}
		self.twitter_stream = bot.get_social_connection(id='twitter_stream')
		self.twitter_api = self.bot.get_social_connection(id='twitter')
		self.config = self.bot.config.get(__name__, {})

		self.auto_join_and_part = self.config.get('auto_join_and_part', False)
		self.auto_part_time = self.config.get('auto_part_time', 180)
		self.tweet_channels = as_list(self.config.get('tweet_channels'))
		self.tweet_format = self.config.get('tweet_format', '@{screen_name}: {text}')
		self.status_channels = as_list(self.config.get('status_channels'))
		self.status_notification_format = self.config.get('status_notification_format', '{message}')
		self.status_tweet_format = self.config.get('status_tweet_format')
		self.status_reply_format = self.config.get('status_reply_format')

	def connection_made(self):
		self.bot.log.info('Connected')
		twitter_ids = []
		for config_key, config_value in self.config.items():
			if config_value and str(config_value).startswith('@') and not config_key.endswith('_format'):
				screen_name = config_value[1:]
				details = self.twitter_api.users.show(screen_name=screen_name)
				twitter_ids.append(details["id_str"])
				self.twitter_channels[screen_name.lower()] = self.tweet_channels
				if self.config.get(config_key + '.channels'):
					self.twitter_channels[screen_name.lower()] = as_list(self.config.get(config_key+'.channels'))
		threading.Thread(target=self.receive_stream, kwargs={'ids': twitter_ids}).start()

	def receive_stream(self, ids):
		if not ids: return
		exception_count = 0;
		while True:
			try:
				follow = ','.join(ids)
				stream = self.twitter_stream.statuses.filter(follow=follow)
				self.bot.log.info('Stream connected: ' + follow)
				self.send_status('Stream connected.')
				for tweet in stream:
					self.bot.loop.run_in_executor(None, self.handle_data, tweet)
				self.bot.log.critical('Stream Connection lost')
				self.send_status('Stream Connection lost')
			except Exception as e:
				exception_count = exception_count + 1;
				self.bot.log.critical('Stream EXCEPTION ' + exception_count)
				self.bot.log.exception(e)
				self.send_status('Stream EXCEPTION ' + exception_count);
				time.sleep(120 if conversation else 150)
			finally:
				time.sleep(60)
				self.bot.log.info('Stream connection retrying...')
				self.send_status('Stream connection retrying...')

	def send_status(self, status):
		if self.status_channels:
			for status_channel in self.status_channels:
				self.bot.privmsg(status_channel, self.status_notification_format.format(message=status))

	def handle_data(self, data):
		if data is None:
			 self.bot.log.info('Stream data: None')
		elif data is Timeout:
			self.bot.log.info('Stream data: Timeout')
		elif data is Hangup:
			self.bot.log.info('Stream data: Heartbeat Timeout')
		elif 'retweeted_status' in data:
			self.bot.log.debug('Stream data: Retweet ' + data['id_str'])
			self.bot.log.debug(str(data))
		elif 'text' in data:
			self.bot.log.debug('Stream data: Tweet @' + data['user']['screen_name'] + '/' + data['id_str'] )
			self.bot.log.debug(str(data))
			self.handle_tweet(data)
		elif 'delete' in data:
			self.bot.log.info('Stream data: Deleted tweet ' + data['delete']['status']['id_str'] )
			self.bot.log.debug(str(data))
		elif 'limit' in data:
			self.bot.log.critical('Stream data: LIMIT NOTICE')
			self.bot.log.debug(str(data))
		else:
			self.bot.log.info('Stream data: unknown')
			self.bot.log.info(str(data))

	def handle_tweet(self, tweet):
			screen_name = tweet['user']['screen_name']
			url = 'https://twitter.com/' + screen_name + '/status/' + tweet['id_str']
			text = html.unescape(tweet['text'])
			if 'extended_tweet' in tweet and 'full_text' in tweet['extended_tweet']:
				text = html.unescape(tweet['extended_tweet']['full_text'])
			user = tweet['user']['screen_name'].lower()

			processed_channels = []
			user_tweet = user in self.twitter_channels
			user_no_reply = user_tweet and \
				(tweet['in_reply_to_screen_name'] == None or tweet['in_reply_to_screen_name'].lower() == user) and \
				(not text.startswith('@') or text.lower().startswith('@' + user))

			if user_tweet and user_no_reply:
				for tweet_channel in self.twitter_channels[user]:
					if not tweet_channel in processed_channels:
						if self.auto_join_and_part:
							self.bot.join(tweet_channel)
						self.bot.privmsg(tweet_channel,
							self.tweet_format.format(screen_name=screen_name, text=text, url=url))
						if self.auto_join_and_part and not tweet_channel in self.status_channels:
							self.bot.loop.call_later(self.auto_part_time, self.bot.part, tweet_channel)
						processed_channels.append(tweet_channel)
			if user_tweet and self.status_channels:
				message = None
				if user_no_reply:
					if self.status_tweet_format:
							message = self.status_tweet_format.format(screen_name=screen_name, text=text, url=url)
				else:
					if self.status_reply_format:
							message = self.status_reply_format.format(screen_name=screen_name, text=text, url=url)
				if message:
					for status_channel in self.status_channels:
						if not status_channel in processed_channels:
							self.bot.privmsg(status_channel, message)
							processed_channels.append(status_channel)

