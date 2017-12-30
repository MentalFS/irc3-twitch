# -*- coding: utf-8 -*-
import irc3
import os, logging, codecs, pytz
from tzlocal import get_localzone
from datetime import datetime
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
	"""Write logs to file in ~/.irc3/logs
	"""

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
				os.makedirs(dirname)
		with codecs.open(filename, 'a+', self.encoding) as fd:
			fd.write(self.formatter.format(**event) + '\r\n')


@irc3.plugin
class RawLogger:
	"""Logger plugin. Use the :class:~file_handler handler by default
	"""

	def __init__(self, bot):
		self.bot = bot
		self.config = bot.config.get(__name__, {})
		hdl = irc3.utils.maybedotted(self.config.get('handler', file_handler))
		self.bot.log.debug('Handler: %s', hdl.__name__)
		self.handler = hdl(bot)

	def process(self, **kwargs):
		kw = dict(host=self.bot.config.host, channel='#%s' % kwargs['channelname'], date=datetime.now(get_localzone()), **kwargs)
		self.handler(kw)

	@irc3.event('(?P<pre>(@\S+ )?:\S+ \S+ #)(?P<channelname>\S+)(?P<post>.*)')
	def on_input(self, pre, channelname, post, **kwargs):
		raw = pre + channelname + post
		self.process(channelname=channelname, raw=raw, **kwargs)

	@irc3.event('(?P<pre>(@\S+ )?\S+ #)(?P<channelname>\S+)(?P<post>.*)', iotype='out')
	def on_output(self, pre, channelname, post, **kwargs):
		raw = pre + channelname + post
		self.process(channelname=channelname, raw=raw, **kwargs)
