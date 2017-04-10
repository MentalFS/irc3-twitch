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
tweet_channels = #channel

## Optional: customize message in channel
tweet_format = "@{screen_name}: {text}"

## Optional: status output
status_channels = #status_channel
status_format = {message}

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
		self.twitter_ids = {}
		self.twitter_stream = bot.get_social_connection(id='twitter_stream')
		self.twitter_api = self.bot.get_social_connection(id='twitter')
		self.config = self.bot.config.get(__name__, {})

		self.auto_join_and_part = self.config.get('auto_join_and_part', False)
		self.auto_part_time = self.config.get('auto_part_time', 180)
		self.tweet_channels = as_list(self.config.get('tweet_channels'))
		self.tweet_format = self.config.get('tweet_format', '@{screen_name}: {text}')
		self.status_channels = as_list(self.config.get('status_channels'))
		self.status_format = self.config.get('status_format', '{message}')
		self.debug_channels = as_list(self.config.get('debug_channels'))
		self.debug_format = self.config.get('debug_format', '{message}')
		self.debug_datacount = self.config.get('debug_datacount', 0)

	def connection_made(self):
		self.bot.log.info('Connected')
		for config_key, config_value in self.config.items():
			if config_value and str(config_value).startswith('@') and not config_key.endswith('_format'):
				screen_name = config_value[1:]
				details = self.twitter_api.users.show(screen_name=screen_name)
				self.twitter_ids[details["id_str"]] = screen_name

				self.twitter_channels[screen_name.lower()] = self.tweet_channels
				if self.config.get(config_key + '.channels'):
					self.twitter_channels[screen_name.lower()] = as_list(self.config.get(config_key+'.channels'))

		threading.Thread(target=self.receive_stream).start()

	def receive_stream(self):
		exception_count = 0
		loop_count = 0
		while True:
			data_count = 0
			try:
				follow = ','.join(self.twitter_ids.keys())
				stream = self.twitter_stream.statuses.filter(follow=follow)
				self.bot.loop.run_in_executor(None, self.send_status, 'Twitter connected.')
				self.bot.log.info('IDs: %s' % follow)
				for tweet in stream:
					self.bot.loop.run_in_executor(None, self.handle_data, tweet)
					data_count = data_count + 1
					if self.debug_datacount and data_count % self.debug_datacount == 0:
						self.bot.loop.run_in_executor(None, self.send_debug, 'Twitter connection received %d packages' % data_count)
				self.bot.loop.run_in_executor(None, self.send_status, 'Twitter connection lost')
			except Exception as e:
				exception_count = exception_count + 1
				self.bot.loop.run_in_executor(None, self.send_status, 'Twitter EXCEPTION %d' % exception_count)
				self.bot.log.exception(e)
				time.sleep(10 * exception_count)
			finally:
				loop_count = loop_count + 1
				time.sleep(20 + loop_count)
				self.bot.loop.run_in_executor(None, self.send_status, 'Twitter connection retrying...')

	def handle_data(self, data):
		if data is None:
			 self.bot.log.info('Twitter sent no data')
		elif data is Timeout:
			self.send_status('Twitter sent a timeout')
			self.bot.log.debug(str(data))
		elif data is Hangup:
			self.send_status('Twitter sent a hangup')
			self.bot.log.debug(str(data))
		elif data is HeartbeatTimeout:
			self.send_status('Twitter sent a heartbeat timeout')
			self.bot.log.debug(str(data))
		elif 'retweeted_status' in data:
			self.bot.log.debug('Twitter sent retweet %s' % data['id_str'])
			self.bot.log.debug(str(data))
		elif 'delete' in data:
			delete_user = data['delete']['status']['user_id_str']
			if delete_user in self.twitter_ids:
				delete_user = '@%s' % self.twitter_ids[delete_user]
			self.send_debug('Twitter sent deletion %s/%s' % (delete_user, data['delete']['status']['id_str']) )
			self.bot.log.debug(str(data))
		elif 'limit' in data:
			self.send_status('Twitter sent LIMIT NOTICE')
			self.bot.log.critical(str(data))
		elif 'text' in data:
			self.bot.log.debug('Twitter sent tweet @%s/%s' % (data['user']['screen_name'], data['id_str']) )
			self.bot.log.debug(str(data))
			self.handle_tweet(data)
		else:
			self.send_status('Twitter sent unknown data')
			self.bot.log.info(str(data))

	def handle_tweet(self, tweet):
			screen_name = tweet['user']['screen_name']
			url = 'https://twitter.com/%s/status/%s' % (screen_name, tweet['id_str'])
			text = html.unescape(tweet['text'])
			if 'extended_tweet' in tweet and 'full_text' in tweet['extended_tweet']:
				text = html.unescape(tweet['extended_tweet']['full_text'])
			user = tweet['user']['screen_name'].lower()

			user_tweet = user in self.twitter_channels \
				and (tweet['in_reply_to_screen_name'] == None or tweet['in_reply_to_screen_name'].lower() == user) \
				and (not text.startswith('@') or text.lower().startswith('@' + user))

			if user_tweet:
				for tweet_channel in self.twitter_channels[user]:
					if self.auto_join_and_part:
						self.bot.join(tweet_channel)
					self.bot.privmsg(tweet_channel,
						self.tweet_format.format(screen_name=screen_name, text=text, url=url))
					if self.auto_join_and_part \
						and not tweet_channel in self.status_channels \
						and not tweet_channel in self.debug_channels:
							self.bot.loop.call_later(self.auto_part_time, self.bot.part, tweet_channel)
				self.send_debug('Sent tweet %s to %s' % (url, ' '.join(self.twitter_channels[user])))
			if user in self.twitter_channels and not user_tweet:
				self.send_debug('Ignored reply %s' % url)


	def send_status(self, status):
		self.bot.log.info(status)
		if self.status_channels:
			for status_channel in self.status_channels:
				self.bot.privmsg(status_channel, self.status_format.format(message=status))

	def send_debug(self, status):
		self.bot.log.debug(status)
		if self.debug_channels:
			for debug_channel in self.debug_channels:
				self.bot.privmsg(debug_channel, self.debug_format.format(message=status))
