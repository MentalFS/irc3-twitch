# -*- coding: utf-8 -*-
import codecs
import collections
import json
import os
import threading
from datetime import datetime

import irc3
import requests
from irc3.plugins.cron import cron
from tzlocal import get_localzone

__doc__ = '''
==============================================
:mod:`twitchdumper.py` Twitch statistics plugin
==============================================

Log statistics for twitch channels in raw json format

..
	>>> from irc3.testing import IrcBot

Usage::

	>>> bot = IrcBot(**{
	...	 'twitchdumper': {
	...		 'handler': 'twitchdumper.file_handler',
	...	 },
	... })
	>>> bot.include('twitchdumper')

Configuration::
	>>> [twitchdumper]
	... client-id=<Client ID> (mandatory)
	... client-secret=<Client Secret> (mandatory)
	... chunk-size=<Maximum channels per request> (optional)
	... filename=<Path like in other log modules>


Available handlers:

.. autoclass:: file_handler
'''


class file_handler:
	"""Write logs to file in ~/.irc3/logs
	"""

	requires = [
		'twitch',
	]

	def __init__(self, bot):
		config = {
			'filename': '~/.irc3/logs/{host}/{channel}-{date:%Y-%m-%d}.{endpoint}.log',
			'data_formatter': '{date:%Y-%m-%dT%H:%M:%S.%f%z} {api} {data_json}',
			'delta_formatter': '{date:%Y-%m-%dT%H:%M:%S.%f%z} {api} @{reference:%Y-%m-%dT%H:%M:%S.%f%z} {delta_json}'
		}
		config.update(bot.config.get(__name__, {}))
		self.filename = config['filename']
		self.data_formatter = config['data_formatter']
		self.delta_formatter = config['delta_formatter']

		self.encoding = bot.encoding
		self.base_json = {}
		self.base_date = {}
		self.base_file = {}

	def __call__(self, api, endpoint, channelname, data, delta={}):
		channel = '#%s' % channelname
		date = datetime.now(get_localzone())
		event = dict(api=api, endpoint=endpoint, channelname=channelname,
			data=data, delta=delta, channel=channel, date=date)

		filename = self.filename.format(**event)
		if not os.path.isfile(filename):
			dirname = os.path.dirname(filename)
			if not os.path.isdir(dirname):  # pragma: no cover
				os.makedirs(dirname, exist_ok=True)

		key = channel+'|'+endpoint+'|'+api
		base_json = json.dumps(data)
		is_delta = key in self.base_json and self.base_file[key] == filename and self.base_json[key] == base_json

		with codecs.open(filename, 'a+', self.encoding) as fd:
			if is_delta:
				delta_json = json.dumps(delta)
				fd.write(self.delta_formatter.format(reference=self.base_date[key],
					delta_json=delta_json, json=delta_json, **event) + '\r\n')
			else:
				self.base_json[key] = base_json
				self.base_date[key] = date
				self.base_file[key] = filename
				self.merge(data, delta)
				data_json = json.dumps(data)
				fd.write(self.data_formatter.format(data_json=data_json, json=data_json, **event) + '\r\n')

	def merge(self, data, delta):
		for k, v in delta.items():
			if (k in data and isinstance(data[k], dict) and isinstance(delta[k], collections.Mapping)):
				self.merge(data[k], delta[k])
			else:
				data[k] = delta[k]


@cron('0 * * * *')
def poll_user(bot):
	bot.poll_user()

@cron('* * * * *')
def poll_stream(bot):
	bot.check_token(60)
	bot.poll_stream()


@irc3.plugin
class TwitchLogger:
	"""Logger plugin. Use the :class:~file_handler handler by default
	"""

	def poll_user_chunk(self, *chunk):
		try:
			helix_users = requests.get('https://api.twitch.tv/helix/users',
				params={'id': chunk}, headers=self.headers, timeout=30)
			self.bot.log.debug(helix_users.url)

			if helix_users.status_code != 200:
				self.bot.log.error('https://api.twitch.tv/helix/users - {r.status_code}\n{r.text}'.format(r=helix_users))
				self.channel_count = -1
			else:
				for helix_user in helix_users.json()['data']:
					delta = {}
					if 'view_count' in helix_user:
						delta['view_count'] = helix_user['view_count']
						del helix_user['view_count']

					self.process(api='helix', endpoint='user',
						channelname=helix_user['login'], data=helix_user, delta=delta)
		except Exception as e:
			self.bot.log.error(e, stack_info=self.channel_count<0)
			self.channel_count = -1

	def poll_stream_chunk(self, *chunk):
		try:
			helix_streams = requests.get('https://api.twitch.tv/helix/streams',
				params={'user_id': chunk, 'first': 100}, headers=self.headers, timeout=30)
			self.bot.log.debug(helix_streams.url)
			if helix_streams.status_code != 200:
				self.bot.log.error('https://api.twitch.tv/helix/streams - {r.status_code}\n{r.text}'.format(r=helix_streams))
				self.channel_count = -1
			else:
				for helix_stream in helix_streams.json()['data']:
					channelname = self.bot.twitch.channels[helix_stream['user_id']]

					if 'community_ids' in helix_stream: del helix_stream['community_ids']
					if 'tag_ids' in helix_stream and isinstance(helix_stream['tag_ids'], list):
						helix_stream['tag_ids'].sort()
					if 'thumbnail_url' in helix_stream: del helix_stream['thumbnail_url']

					delta = {}
					if 'viewer_count' in helix_stream:
						delta['viewer_count'] = helix_stream['viewer_count']
						del helix_stream['viewer_count']

					self.process(api='helix', endpoint='stream',
						channelname=channelname, data=helix_stream, delta=delta)
		except Exception as e:
			self.bot.log.error(e, stack_info=self.channel_count<0)
			self.channel_count = -1


	def __init__(self, bot):
		self.bot = bot
		self.config = bot.config.get(__name__, {})
		handler = irc3.utils.maybedotted(self.config.get('handler', file_handler))
		self.bot.log.debug('%s Handler: %s %s', self.__module__, handler.__module__, handler.__name__)
		self.process = handler(bot)

		config = {
			'chunk-size': 99,
			'client-id': '1u66z1u96b69spbutvthgach2rbcd0',
			'client-secret': None,
		}
		config.update(bot.config.get(__name__, {}))
		self.chunk_size = min(100, max(1, config['chunk-size']))
		self.api_token = None
		self.api_token_ttl = -1
		self.client_id = config['client-id']
		self.client_secret = config['client-secret']

		self.headers = {
			'Client-ID': config['client-id'],
			'Accept': 'application/vnd.twitchtv.v5+json',
		}

		self.connection_made()

	@irc3.extend
	def check_token(self, seconds_passed):
		if not self.client_secret:
			self.bot.log.warn('No client secret set - API access might be rejected!')
			return
		self.api_token_ttl = self.api_token_ttl  - 2 * seconds_passed # refresh after half of the TTL
		if self.api_token_ttl > 0:
			self.bot.log.debug('API token TTL: %d' % self.api_token_ttl)
			return

		try:
			token = requests.post('https://id.twitch.tv/oauth2/token', timeout=30,
				params={'client_id': self.client_id, 'client_secret': self.client_secret, 'grant_type': 'client_credentials'})
			self.bot.log.debug(token.url)
			if token.status_code != 200:
				self.bot.log.error('https://id.twitch.tv/oauth2/token - {r.status_code}\n{r.text}'.format(r=token))
				self.channel_count = -1
			else:
				data = token.json()
				self.api_token = data['access_token']
				self.api_token_ttl = data['expires_in']

				self.headers['Authorization'] = 'Bearer %s' % self.api_token

				self.bot.log.info('Refreshed API token')

		except Exception as e:
			self.bot.log.error(e, stack_info=self.channel_count<0)
			self.channel_count = -1

	@irc3.extend
	def poll_user(self):
		for chunk in self.chunk_channels():
			threading.Thread(target=self.poll_user_chunk, args=(chunk)).start()

	@irc3.extend
	def poll_stream(self):
		for chunk in self.chunk_channels():
			threading.Thread(target=self.poll_stream_chunk, args=(chunk)).start()

	def chunk_channels(self):
		channel_count = len(self.bot.twitch.channels)
		if (channel_count != self.channel_count):
			self.bot.log.info('Polling %d channels' % channel_count)
			self.channel_count = channel_count
		channels = list(self.bot.twitch.channels.keys())
		return [channels[i:i+self.chunk_size] for i in range(0, len(channels), self.chunk_size)]

	def connection_made(self):
		self.channel_count = -1
		self.check_token(0)
