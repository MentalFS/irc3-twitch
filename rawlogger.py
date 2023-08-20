# -*- coding: utf-8 -*-
import codecs
import os
from datetime import datetime

import irc3
from irc3.utils import as_list
from tzlocal import get_localzone

__doc__ = '''
=============================================
:mod:`rawlogger.py` Channel raw logger plugin
=============================================

Log channels in raw format

..
	>>> from irc3.testing import IrcBot

Usage::

	>>> bot = IrcBot(**{
	...	 'rawlogger': {
	...		 'handler': 'rawlogger.file_handler',
	...	 },
	... })
	>>> bot.include('rawlogger')


Available handlers:

.. autoclass:: file_handler
'''


class file_handler:
	"""Write logs to file in ~/.irc3/logs"""

	def __init__(self, bot):
		config = {
			'filename': '~/.irc3/logs/{host}/{channel}-{date:%Y-%m-%d}.raw.log',
			'formatter': '{date:%Y-%m-%dT%H:%M:%S.%f%z} {raw}',
		}
		config.update(bot.config.get(__name__, {}))
		self.filename = config['filename']
		self.encoding = bot.encoding
		self.formatter = config['formatter']

	def __call__(self, event):
		filename = self.filename.format(**event)
		if not os.path.isfile(filename):
			dirname = os.path.dirname(filename)
			if not os.path.isdir(dirname):  # pragma: no cover
				os.makedirs(dirname, exist_ok=True)
		with codecs.open(filename, 'a+', self.encoding) as fd:
			fd.write(self.formatter.format(**event) + '\r\n')


@irc3.plugin
class RawLogger:
	"""Logger plugin. Use the :class:~file_handler handler by default"""

	def message_ignored(self, command, message):
		if not self.message_ignores:
			return False

		if command in self.message_ignores:
			self.bot.log.debug('Filtered: %s' % message)
			return True

		return False

	def __init__(self, bot):
		self.bot = bot
		self.config = bot.config.get(__name__, {})

		handler = irc3.utils.maybedotted(self.config.get('handler', file_handler))
		self.bot.log.debug('%s Handler: %s %s', self.__module__, handler.__module__, handler.__name__)
		self.handler = handler(bot)

		self.message_ignores = []
		for message_ignore in as_list(self.config.get('ignore')):
			self.message_ignores.append(message_ignore)

	def process(self, **kwargs):
		if self.message_ignored(kwargs['command'], kwargs['raw']):
			return

		kw = dict(host=self.bot.config.host, channel='#%s' % kwargs['channelname'], date=datetime.now(get_localzone()), **kwargs)
		self.handler(kw)

	@irc3.event('(?P<pre>(@\S+ )?:\S+ (?P<command>\S+) #)(?P<channelname>\S+)(?P<post>.*)')
	def on_input(self, pre, command, channelname, post, **kwargs):
		raw = pre + channelname + post
		self.process(command=command, channelname=channelname, raw=raw, **kwargs)

	@irc3.event('(?P<pre>(@\S+ )?(?P<command>\S+) #)(?P<channelname>\S+)(?P<post>.*)', iotype='out')
	def on_output(self, pre, command, channelname, post, **kwargs):
		raw = pre + channelname + post
		self.process(command=command, channelname=channelname, raw=raw, **kwargs)
