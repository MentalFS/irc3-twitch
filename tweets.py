# -*- coding: utf-8 -*-
import irc3, asyncio, venusian
import threading, html, time, traceback
import requests, json
from irc3.utils import as_list
from twitter.stream import Timeout, HeartbeatTimeout, Hangup
from irc3.plugins.command import command

__doc__ = '''
==========================================
:mod:`tweets` Feeds plugin
==========================================

Post Twitter Updates into channels.

You must configure `irc3.plugins.social` properly.

Additionally, your config has to contain something like this:

[tweets]
## Optional: default channel
tweet_channels = #channel

## Optional: customize message in channel
tweet_format = "@{screen_name}: {text}"

## some twitter feeds:
identifier.account = screen_name
identifier.channels = #channel1 #channel2

## these are just for Discord
webhook_username = Username shown as bot name
webhook_avatar = https://... (URL ro an avatar image)
identifier.webhook = https://discordapp.com/api/webhooks/...
[...]

'''

@irc3.plugin
class Tweets:
	requires = [
		'irc3.plugins.social',
	]

	def __init__(self, bot):
		self.bot = bot
		self.twitter_channels = {}
		self.twitter_ids = {}
		self.twitter_webhooks = {}
		self.twitter_stream = bot.get_social_connection(id='twitter_stream')
		self.twitter_api = self.bot.get_social_connection(id='twitter')
		self.config = self.bot.config.get(__name__, {})

		self.tweet_channels = as_list(self.config.get('tweet_channels'))
		self.tweet_format = self.config.get('tweet_format', '@{screen_name}: {text}')
		self.webhook_username = self.config.get('webhook_username')
		self.webhook_avatar = self.config.get('webhook_avatar')

		self.twitter_connected = False

	def connect_twitter(self):
		for config_key, config_value in self.config.items():
			if config_value and str(config_key).endswith('.account'):
				screen_name = config_value
				details = self.twitter_api.users.show(screen_name=screen_name)
				self.twitter_ids[details["id_str"]] = screen_name

				self.twitter_channels[screen_name.lower()] = self.tweet_channels
				config_id = config_key[:-8]
				if self.config.get(config_id + '.channels'):
					self.twitter_channels[screen_name.lower()] = as_list(self.config.get(config_id+'.channels'))
				self.twitter_webhooks[screen_name.lower()] = self.config.get(config_id+'.webhook')

		threading.Thread(target=self.receive_stream).start()

	def receive_stream(self):
		exception_count = 0
		loop_count = 0
		while True:
			try:
				follow = ','.join(self.twitter_ids.keys())
				stream = self.twitter_stream.statuses.filter(follow=follow)
				self.twitter_connected = True
				self.bot.log.info('Twitter connected')
				self.bot.log.info('IDs: %s' % follow)
				for tweet in stream:
					self.bot.loop.run_in_executor(None, self.handle_data, tweet)
				self.bot.log.info('Twitter disconnected')
			except Exception as e:
				self.bot.log.info('Twitter connection lost')
				exception_count = exception_count + 1
				self.bot.log.info('Twitter EXCEPTION %d' % exception_count)
				self.bot.log.exception(e)
				time.sleep(10 * exception_count)
			finally:
				loop_count = loop_count + 1
				time.sleep(20 + loop_count)
				self.bot.log.info('Twitter connection retrying')
		self.twitter_connected = False

	def handle_data(self, data):
		if data is None:
			 self.bot.log.info('Twitter sent no data')
		elif data is Timeout:
			self.bot.log.info('Twitter sent a timeout')
		elif data is Hangup:
			self.bot.log.info('Twitter sent a hangup')
		elif data is HeartbeatTimeout:
			self.bot.log.info('Twitter sent a heartbeat timeout')
		elif 'retweeted_status' in data:
			self.bot.log.debug('Twitter sent retweet %s' % data['id_str'])
		elif 'delete' in data:
			delete_user = data['delete']['status']['user_id_str']
			if delete_user in self.twitter_ids:
				delete_user = '@%s' % self.twitter_ids[delete_user]
			self.bot.log.debug('Twitter sent deletion %s/%s' % (delete_user, data['delete']['status']['id_str']))
		elif 'limit' in data:
			self.bot.log.critical('Twitter sent LIMIT NOTICE')
			self.bot.log.info(json.dumps(data))
		elif 'text' in data:
			self.bot.log.debug('Twitter sent tweet @%s/%s' % (data['user']['screen_name'], data['id_str']) )
			self.handle_tweet(data)
			#self.bot.log.debug(json.dumps(data))
		else:
			self.bot.log.warn('Twitter sent unknown data')
			self.bot.log.info(json.dumps(data))

	def handle_tweet(self, tweet):
			screen_name = tweet['user']['screen_name']
			user_name = tweet['user']['name']
			url = 'https://twitter.com/%s/status/%s' % (screen_name, tweet['id_str'])
			text = html.unescape(tweet['text'])
			if 'extended_tweet' in tweet and 'full_text' in tweet['extended_tweet']:
				text = html.unescape(tweet['extended_tweet']['full_text'])
			user = tweet['user']['screen_name'].lower()

			user_tweet = (user in self.twitter_channels or user in self.twitter_webhooks)  \
				and (tweet['in_reply_to_screen_name'] == None or tweet['in_reply_to_screen_name'].lower() == user) \
				and (not text.startswith('@') or text.lower().startswith('@' + user))

			if user_tweet:
				if user in self.twitter_channels:
					# text = text.replace('\r', '').replace('\n', ' ')
					for tweet_channel in self.twitter_channels[user]:
						self.bot.privmsg(tweet_channel,
							self.tweet_format.format(
								screen_name=screen_name, user_name=user_name, text=text, tweet=tweet, url=url))
					self.bot.log.debug('Sent tweet %s to %s' % (url, ' '.join(self.twitter_channels[user])))
				if self.twitter_webhooks[user]:
					self.send_webhook(self.twitter_webhooks[user], screen_name, user_name, text, tweet, url)
			else:
				self.bot.log.debug('Ignored reply %s' % url)

	def send_webhook(self, webhook, screen_name, user_name, text, tweet, url):
		try:
			message = {'embeds': []}
			if self.webhook_username:
				message['username'] = self.webhook_username
			if self.webhook_avatar:
				message['avatar_url'] = self.webhook_avatar

			text_message = {
				'description': text,
				'url': url,
				'title': '@%s' % screen_name,
				'color': 33972, #alternative: 44269
				'thumbnail': {
					'url': tweet['user']['profile_image_url_https']
				}
			}
			message['embeds'].append(text_message)

			if 'extended_entities' in tweet and 'media' in tweet['extended_entities']:
				for medium in tweet['extended_entities']['media']:
					media_message = {'url': url }
					if 'media_url' in medium:
						media_message['image'] = { 'url': medium['media_url'] }
					if 'media_url_https' in medium:
						media_message['image'] = { 'url': medium['media_url_https'] }
					# Videos are not supported yet, but who knows?
					if 'video_info' in medium and 'variants' in medium['video_info'] \
							and len(medium['video_info']['variants']) > 0 \
							and 'url' in medium['video_info']['variants'][0]:
						media_message['video'] = {'url': medium['video_info']['variants'][0]['url']}
					# Until then at least mark the videos
					if medium['type'] != 'photo':
						if medium['type'] == 'animated_gif':
							media_message['footer'] = {'text': '🎞️ GIF'}
						elif medium['type'] == 'video':
							media_message['footer'] = {'text': '🎞️ Video'}
						else:
							media_message['footer'] = {'text': '🎞️ ?'}
					message['embeds'].append(media_message)

			reply = requests.post(webhook, json=message)
			if reply.status_code != 204:
				self.bot.log.info(webhook)
				self.bot.log.info(json_message)
				self.bot.log.info(reply)
			self.bot.log.debug('Sent tweet %s to %s' % (url, webhook))
			#self.bot.log.debug(json.dumps(tweet))
			#self.bot.log.debug(json.dumps(message))
		except Exception as e:
			self.bot.log.exception(e)

	def connection_made(self):
		if not self.twitter_connected:
			self.connect_twitter()

	@command(permission='admin', venusian_category='irc3.debug')
	def reload_tweet(self, mask, target, args):
		"""Handle a specific tweet (again)

            %%reload_tweet <id>
        """
		status = args['<id>']
		self.bot.log.info('Fetching and handling tweet: %s' % status)
		tweet = self.twitter_api.statuses.show(id=status, include_entities="true", tweet_mode="extended")
		tweet['text'] = tweet['full_text']
		self.handle_tweet(tweet)
