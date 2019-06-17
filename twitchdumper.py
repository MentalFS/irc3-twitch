# -*- coding: utf-8 -*-
import irc3, requests, threading, json
import os, logging, codecs, pytz, collections
from irc3.plugins.cron import cron
from tzlocal import get_localzone
from datetime import datetime
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
	bot.poll_stream()


@irc3.plugin
class TwitchLogger:
	"""Logger plugin. Use the :class:~file_handler handler by default
	"""

	def poll_user_chunk(self, *chunk):
		try:
			helix_users = requests.get('https://api.twitch.tv/helix/users',
				params={'id': chunk}, headers=self.headers)
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

			kraken_users = requests.get('https://api.twitch.tv/kraken/users',
				params={'id': ','.join(chunk)}, headers=self.headers)
			self.bot.log.debug(kraken_users.url)
			if kraken_users.status_code != 200:
				self.bot.log.error('https://api.twitch.tv/kraken/users - {r.status_code}\n{r.text}'.format(r=kraken_users))
				self.channel_count = -1
			else:
				for kraken_user in kraken_users.json()['users']:
					delta = {}
					if 'updated_at' in kraken_user:
						delta['updated_at'] = kraken_user['updated_at']
						del kraken_user['updated_at']
					self.process(api='kraken', endpoint='user',
						channelname=kraken_user['name'], data=kraken_user, delta=delta)
		except Exception as e:
			self.bot.log.exception(e)
			self.channel_count = -1

	def poll_stream_chunk(self, *chunk):
		try:
			helix_streams = requests.get('https://api.twitch.tv/helix/streams',
				params={'user_id': chunk, 'first': 100}, headers=self.headers)
			self.bot.log.debug(helix_streams.url)
			if helix_streams.status_code != 200:
				self.bot.log.error('https://api.twitch.tv/helix/streams - {r.status_code}\n{r.text}'.format(r=helix_streams))
				self.channel_count = -1
			else:
				for helix_stream in helix_streams.json()['data']:
					channelname = self.bot.twitch.channels[helix_stream['user_id']]
					if not channelname:
						self.bot.log.bot.error('unassignable: %s' % json.dumps(helix_stream))
						self.channel_count = -1
					else:
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

			kraken_streams = requests.get('https://api.twitch.tv/kraken/streams',
				params={'channel': ','.join(chunk), 'limit': 100}, headers=self.headers)
			self.bot.log.debug(kraken_streams.url)
			if kraken_streams.status_code != 200:
				self.bot.log.error('https://api.twitch.tv/kraken/streams - {r.status_code}\n{r.text}'.format(r=kraken_streams))
				self.channel_count = -1
			else:
				for kraken_stream in kraken_streams.json()['streams']:
					channelname = kraken_stream['channel']['name']
					if 'channel' in kraken_stream:
						if 'logo' in kraken_stream['channel']:
							del kraken_stream['channel']['logo']
						if 'description' in kraken_stream['channel']:
							del kraken_stream['channel']['description']
						if 'profile_banner' in kraken_stream['channel']:
							del kraken_stream['channel']['profile_banner']
						if 'profile_banner_background_color' in kraken_stream['channel']:
							del kraken_stream['channel']['profile_banner_background_color']
						if 'updated_at' in kraken_stream['channel']:
							del kraken_stream['channel']['updated_at']
						if 'video_banner' in kraken_stream['channel']:
							del kraken_stream['channel']['video_banner']
					if 'community_id' in kraken_stream: del kraken_stream['community_id']
					if 'community_ids' in kraken_stream: del kraken_stream['community_ids']
					if 'preview' in kraken_stream: del kraken_stream['preview']
					delta = {}
					if 'average_fps' in kraken_stream:
						delta['average_fps'] = kraken_stream['average_fps']
						del kraken_stream['average_fps']
					if 'viewers' in kraken_stream:
						delta['viewers'] = kraken_stream['viewers']
						del kraken_stream['viewers']
					if 'channel' in kraken_stream:
						delta['channel'] = {}
						if 'followers' in kraken_stream['channel']:
							delta['channel']['followers'] = kraken_stream['channel']['followers']
							del kraken_stream['channel']['followers']
						if 'views' in kraken_stream['channel']:
							delta['channel']['views'] = kraken_stream['channel']['views']
							del kraken_stream['channel']['views']
					self.process(api='kraken', endpoint='stream',
						channelname=channelname, data=kraken_stream, delta=delta)
		except Exception as e:
			self.bot.log.exception(e)
			self.channel_count = -1


	def __init__(self, bot):
		self.bot = bot
		self.config = bot.config.get(__name__, {})
		handler = irc3.utils.maybedotted(self.config.get('handler', file_handler))
		self.bot.log.debug('Handler: %s', handler.__name__)
		self.process = handler(bot)
		config = {
			'chunk-size': 99,
			'client-id': '1u66z1u96b69spbutvthgach2rbcd0',
		}
		config.update(bot.config.get(__name__, {}))
		self.chunkSize = min(100, max(1, config['chunk-size']))
		self.headers = {
			'Client-ID': config['client-id'],
			'Accept': 'application/vnd.twitchtv.v5+json',
		}
		self.connection_made()

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
		return [channels[i:i+self.chunkSize] for i in range(0, len(channels), self.chunkSize)]

	def connection_made(self):
		self.channel_count = -1
