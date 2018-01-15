# -*- coding: utf-8 -*-
import irc3, requests, multiprocessing, json
import os, logging, codecs, pytz
from irc3.plugins.cron import cron
from tzlocal import get_localzone
from datetime import datetime
__doc__ = '''
==============================================
:mod:`twitchstats.py` Twitch statistics plugin
==============================================

Log statistics for twitch channels in raw json format

..
	>>> from irc3.testing import IrcBot

Usage::

	>>> bot = IrcBot(**{
	...	 'twitchstats': {
	...		 'handler': 'twitchstats.file_handler',
	...	 },
	... })
	>>> bot.include('twitchstats')


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
		manager = multiprocessing.Manager()
		self.last_json = manager.dict()
		self.last_date = manager.dict()

	def __call__(self, event):
		key = event['channel']+'|'+event['endpoint']+'|'+event['api']
		duplicate = key in self.last_json and self.last_json[key] == event['json']

		filename = self.filename.format(**event)
		if not os.path.isfile(filename):
			dirname = os.path.dirname(filename)
			if not os.path.isdir(dirname):  # pragma: no cover
				os.makedirs(dirname)
			duplicate = False

		with codecs.open(filename, 'a+', self.encoding) as fd:
			if duplicate:
				fd.write(self.duplicate_formatter.format(reference=self.last_date[key], **event) + '\r\n')
			else:
				self.last_json[key] = event['json']
				self.last_date[key] = event['date']
				fd.write(self.formatter.format(**event) + '\r\n')

@cron('0,10,20,30,40,50 * * * *')
def schedule_twitchstats_full(bot):
	bot.on_schedule(True)

@cron('1-9,11-19,21-29,31-39,41-49,51-59 * * * *')
def schedule_twitchstats_partial(bot):
	bot.on_schedule(False)


@irc3.plugin
class TwitchStats:
	"""Logger plugin. Use the :class:~file_handler handler by default
	"""

	def __init__(self, bot):
		self.bot = bot
		self.config = bot.config.get(__name__, {})
		hdl = irc3.utils.maybedotted(self.config.get('handler', file_handler))
		self.bot.log.debug('Handler: %s', hdl.__name__)
		self.handler = hdl(bot)
		config = {
			'chunk-size': 20,
			'client-id': 'deh0rnosabytmgde2jtn13k8mo899ye',
		}
		config.update(bot.config.get(__name__, {}))
		self.chunkSize = min(100, max(1, config['chunk-size']))
		self.headers = {
			'Client-ID': config['client-id'],
			'Accept': 'application/vnd.twitchtv.v5+json',
		}
		self.connection_lost()

	def process(self, **kwargs):
		kw = dict(host=self.bot.config.host, channel='#%s' % kwargs['channelname'], date=datetime.now(get_localzone()), **kwargs)
		self.handler(kw)

	def poll(self, full, chunk):
		channelnames = {}
		helix_users = requests.get('https://api.twitch.tv/helix/users', params={'login': chunk}, headers=self.headers)
		self.bot.log.debug(helix_users.url)
		if helix_users.status_code != 200:
			self.bot.log.error('{r.url} - {r.status_code}\n{r.text}'.format(r=helix_users))
		else:
			for helix_user in helix_users.json()['data']:
				channelnames[helix_user['id']] = helix_user['login']
				channelname = helix_user['login']
				if full:
					self.process(channelname=channelname, endpoint='user', api='helix', json=json.dumps(helix_user))

		helix_streams = requests.get('https://api.twitch.tv/helix/streams', params={'user_login': chunk, 'first': 100}, headers=self.headers)
		self.bot.log.debug(helix_streams.url)
		if helix_streams.status_code != 200:
			self.bot.log.error('{r.url} - {r.status_code}\n{r.text}'.format(r=helix_streams))
		else:
			for helix_stream in helix_streams.json()['data']:
				channelname = channelnames[helix_stream['user_id']]
				if not channelname:
					self.bot.log.bot.error('unassignable: %s' % json.dumps(helix_stream))
				else:
					self.process(channelname=channelname, endpoint='stream', api='helix', json=json.dumps(helix_stream))

		user_ids = []
		kraken_users = requests.get('https://api.twitch.tv/kraken/users', params={'login': ','.join(chunk)}, headers=self.headers)
		self.bot.log.debug(kraken_users.url)
		if kraken_users.status_code != 200:
			self.bot.log.error('{r.url} - {r.status_code}\n{r.text}'.format(r=kraken_users))
		else:
			for kraken_user in kraken_users.json()['users']:
				user_ids.append(kraken_user['_id'])
				channelname = kraken_user['name']
				if full:
					self.process(channelname=channelname, endpoint='user', api='kraken', json=json.dumps(kraken_user))

		kraken_streams = requests.get('https://api.twitch.tv/kraken/streams', params={'channel': ','.join(user_ids), 'limit': 100}, headers=self.headers)
		self.bot.log.debug(kraken_streams.url)
		if kraken_streams.status_code != 200:
			self.bot.log.error('{r.url} - {r.status_code}\n{r.text}'.format(r=kraken_streams))
		else:
			for kraken_stream in kraken_streams.json()['streams']:
				channelname = kraken_stream['channel']['name']
				self.process(channelname=channelname, endpoint='stream', api='kraken', json=json.dumps(kraken_stream))


	@irc3.extend
	def on_schedule(self, full):
		channels = list(self.channels)

		channel_count = len(channels)
		if (channel_count != self.channel_count):
			self.bot.log.info('Polling %d channels' % channel_count)
			self.channel_count = channel_count

		chunks = [channels[i:i+self.chunkSize] for i in range(0, len(channels), self.chunkSize)]
		for chunk in chunks:
			multiprocessing.Process(target=self.poll, args=(full, chunk)).start()

	# Keep set of channels
	@irc3.event('(@\S+ )?JOIN #(?P<channelname>\S+)( :.*)?', iotype='out')
	@irc3.event('(@\S+ )?:\S+ JOIN #(?P<channelname>\S+)( :.*)?', iotype='in')
	def on_join_channel(self, channelname):
		if (channelname in self.channels): return
		self.bot.log.debug('JOIN: #%s' % channelname)
		self.channels.add(channelname)

	@irc3.event('(@\S+ )?PART #(?P<channelname>\S+)( :.*)?', iotype='out')
	def on_part_channel(self, channelname):
		self.bot.log.debug('PART: #%s' % channelname)
		self.channels.remove(channelname)

	def connection_lost(self):
		self.channels = set()
		self.channel_count = -1
