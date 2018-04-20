# -*- coding: utf-8 -*-
import irc3, requests, threading, json
import os, logging, codecs, pytz
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

	def __init__(self, bot):
		config = {
			'filename': '~/.irc3/logs/{host}/{channel}-{date:%Y-%m-%d}.{endpoint}.log',
			'formatter': '{date:%Y-%m-%dT%H:%M:%S.%f%z} {api} {json}',
			'duplicate_formatter': '{date:%Y-%m-%dT%H:%M:%S.%f%z} {api} @{reference:%Y-%m-%dT%H:%M:%S.%f%z}'
		}
		config.update(bot.config.get(__name__, {}))
		self.filename = config['filename']
		self.encoding = bot.encoding
		self.formatter = config['formatter']
		self.duplicate_formatter = config['duplicate_formatter']
		self.last_json = {}
		self.last_date = {}
		self.last_file = {}

	def __call__(self, event):

		filename = self.filename.format(**event)
		if not os.path.isfile(filename):
			dirname = os.path.dirname(filename)
			if not os.path.isdir(dirname):  # pragma: no cover
				os.makedirs(dirname)

		key = event['channel']+'|'+event['endpoint']+'|'+event['api']
		duplicate = key in self.last_json and self.last_file[key] == filename and self.last_json[key] == event['json']

		with codecs.open(filename, 'a+', self.encoding) as fd:
			if duplicate:
				fd.write(self.duplicate_formatter.format(reference=self.last_date[key], **event) + '\r\n')
			else:
				self.last_json[key] = event['json']
				self.last_date[key] = event['date']
				self.last_file[key] = filename
				fd.write(self.formatter.format(**event) + '\r\n')


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
		helix_users = requests.get('https://api.twitch.tv/helix/users', params={'id': chunk}, headers=self.headers)
		self.bot.log.debug(helix_users.url)

		if helix_users.status_code != 200:
			self.bot.log.error('{r.url} - {r.status_code}\n{r.text}'.format(r=helix_users))
		else:
			for helix_user in helix_users.json()['data']:
				if 'offline_image_url' in helix_user: del helix_user['offline_image_url']
				if 'profile_image_url' in helix_user: del helix_user['profile_image_url']
				if 'view_count' in helix_user: del helix_user['view_count']
				self.process(channelname=helix_user['login'], endpoint='user', api='helix', json=json.dumps(helix_user))

		kraken_users = requests.get('https://api.twitch.tv/kraken/users', params={'id': ','.join(chunk)}, headers=self.headers)
		self.bot.log.debug(kraken_users.url)
		if kraken_users.status_code != 200:
			self.bot.log.error('{r.url} - {r.status_code}\n{r.text}'.format(r=kraken_users))
		else:
			for kraken_user in kraken_users.json()['users']:
				if 'logo' in kraken_user: del kraken_user['logo']
				if 'updated_at' in kraken_user: del kraken_user['updated_at']
				self.process(channelname=kraken_user['name'], endpoint='user', api='kraken', json=json.dumps(kraken_user))


	def poll_stream_chunk(self, *chunk):
		helix_streams = requests.get('https://api.twitch.tv/helix/streams', params={'user_id': chunk, 'first': 100}, headers=self.headers)
		self.bot.log.debug(helix_streams.url)
		if helix_streams.status_code != 200:
			self.bot.log.error('{r.url} - {r.status_code}\n{r.text}'.format(r=helix_streams))
		else:
			for helix_stream in helix_streams.json()['data']:
				channelname = self.bot.twitch.channels[helix_stream['user_id']]
				if 'thumbnail_url' in helix_stream: del helix_stream['thumbnail_url']
				if not channelname:
					self.bot.log.bot.error('unassignable: %s' % json.dumps(helix_stream))
				else:
					self.process(channelname=channelname, endpoint='stream', api='helix', json=json.dumps(helix_stream))

		kraken_streams = requests.get('https://api.twitch.tv/kraken/streams', params={'channel': ','.join(chunk), 'limit': 100}, headers=self.headers)
		self.bot.log.debug(kraken_streams.url)
		if kraken_streams.status_code != 200:
			self.bot.log.error('{r.url} - {r.status_code}\n{r.text}'.format(r=kraken_streams))
		else:
			for kraken_stream in kraken_streams.json()['streams']:
				channelname = kraken_stream['channel']['name']
				if 'channel' in kraken_stream:
					if 'created_at' in kraken_stream['channel']: del kraken_stream['channel']['created_at']
					if 'logo' in kraken_stream['channel']: del kraken_stream['channel']['logo']
					if 'description' in kraken_stream['channel']: del kraken_stream['channel']['description']
					if 'partner' in kraken_stream['channel']: del kraken_stream['channel']['partner']
					if 'profile_banner' in kraken_stream['channel']: del kraken_stream['channel']['profile_banner']
					if 'profile_banner_background_color' in kraken_stream['channel']:
						del kraken_stream['channel']['profile_banner_background_color']
					if 'url' in kraken_stream['channel']: del kraken_stream['channel']['url']
					if 'updated_at' in kraken_stream['channel']: del kraken_stream['channel']['updated_at']
					if 'video_banner' in kraken_stream['channel']: del kraken_stream['channel']['video_banner']
					# if 'views' in kraken_stream['channel']: del kraken_stream['channel']['views']
				if 'community_id' in kraken_stream: del kraken_stream['community_id']
				if 'preview' in kraken_stream: del kraken_stream['preview']
				self.process(channelname=channelname, endpoint='stream', api='kraken', json=json.dumps(kraken_stream))


	def __init__(self, bot):
		self.bot = bot
		self.config = bot.config.get(__name__, {})
		hdl = irc3.utils.maybedotted(self.config.get('handler', file_handler))
		self.bot.log.debug('Handler: %s', hdl.__name__)
		self.handler = hdl(bot)
		config = {
			'chunk-size': 99,
			'client-id': 'deh0rnosabytmgde2jtn13k8mo899ye',
		}
		config.update(bot.config.get(__name__, {}))
		self.chunkSize = min(100, max(1, config['chunk-size']))
		self.headers = {
			'Client-ID': config['client-id'],
			'Accept': 'application/vnd.twitchtv.v5+json',
		}
		self.connection_made()

	def process(self, **kwargs):
		kw = dict(host=self.bot.config.host, channel='#%s' % kwargs['channelname'], date=datetime.now(get_localzone()), **kwargs)
		self.handler(kw)

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
