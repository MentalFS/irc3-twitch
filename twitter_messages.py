# -*- coding: utf-8 -*-
import irc3, asyncio, threading, html
from twitter.stream import Timeout, HeartbeatTimeout, Hangup

__doc__ = '''
==========================================
:mod:`twitter_messages` Feeds plugin
==========================================

Post Twitter Updates into channels.

You must configure `irc3.plugins.social` properly.

Additionally, your config has to contain something like this:

[twitter_messages]
# Optional: customize message in channel
tweet_format = "@{screen_name}: {text}"

# some feeds: @screen_name = #channel
@twitch = #twitch

'''

#TODO file logs wit JSON data
#TODO enable posting to multiple channels

#TODO expanding URLs and media attachments

#NOTE consider two streams: one for full conversations, one to filter by screen_name
#		pro: it would be possible to exclude from conversation_channel by screen_name
#		con: possibly a more complicated configuration file

#NOTE consider not using social plugin, this could enable the use of better stream endpoints

#NOTE command to add/remove/configure twitter channels - check if writing to config is possible

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
		self.twitter_ids = []
		self.channels = {}
		self.tweet_format = self.config.get('tweet_format', '@{screen_name}: {text}')
		self.conversation_channel = self.config.get('conversation_channel')
		self.conversation_format = self.config.get('conversation_format', '@{screen_name}: {text}')

	def connection_made(self):
		self.bot.log.info('connected')
		channel_count = 0
		for config_entry, channel in self.config.items():
			if config_entry and config_entry.startswith('@'):
				screen_name = config_entry[1:]
				details = self.twitter_api.users.show(screen_name=screen_name)
				self.twitter_ids.append(details["id_str"])
				if channel.startswith('#'):
					self.channels[screen_name.lower()] = channel
					channel_count = channel_count + 1
		threading.Thread(target=self.receive_stream).start()
		self.bot.log.info(str(channel_count) + ' channels streaming')

	def receive_stream(self):
		while True:
			if not self.twitter_ids: return
			follow = ','.join(self.twitter_ids)
			stream = self.twitter_stream.statuses.filter(follow=follow)
			for tweet in stream:
				self.bot.loop.run_in_executor(None, self.handle_tweet, tweet)
			self.bot.log.critical('Twitter Stream: Connection lost')

	def handle_tweet(self, tweet):
		if tweet is None:
			 self.bot.log.info('Twitter Stream: None')
		elif tweet is Timeout:
			self.bot.log.info('Twitter Stream: Timeout')
		elif tweet is Hangup:
			self.bot.log.info('Twitter Stream: Heartbeat Timeout')
		elif 'retweeted_status' in tweet:
			self.bot.log.info('Twitter Stream: Retweet')
			# self.bot.log.debug(str(tweet))
		elif 'text' in tweet:
			self.bot.log.info('Twitter Stream: Tweet @' + tweet['user']['screen_name'] + '/' + tweet['id_str'] )
			# self.bot.log.debug(str(tweet))
			text = html.unescape(tweet['text'])
			if 'extended_tweet' in tweet and 'full_text' in tweet['extended_tweet']:
				text = html.unescape(tweet['extended_tweet']['full_text'])
			user = tweet['user']['screen_name'].lower()
			if user in self.channels and self.channels[user] != self.conversation_channel:
				reply_to = tweet['in_reply_to_screen_name']
				if reply_to == None or reply_to == user:
					self.bot.privmsg(self.channels[user], 
						self.tweet_format.format(screen_name=tweet['user']['screen_name'], text=text))
			if self.conversation_channel:
				self.bot.privmsg(self.conversation_channel,
					self.conversation_format.format(screen_name=tweet['user']['screen_name'], text=text))
		else:
			self.bot.log.info('Twitter Stream: Data')
			# self.bot.log.debug(str(tweet))

