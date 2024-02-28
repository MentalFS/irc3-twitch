# -*- coding: utf-8 -*-
import irc3
import signal, time


@irc3.plugin
class Sigterm:
	def __init__(self, bot):
		self.bot = bot
		try:
			self.bot.loop.add_signal_handler(signal.SIGTERM, self.SIGTERM)
		except (RuntimeError, NotImplementedError):
			pass

	def SIGTERM(self):
		self.bot.log.info('Shutdown')
		self.bot.notify('SIGINT')
		if getattr(self.bot, 'protocol', None):
			self.bot.quit('TERM')
			time.sleep(1)
		self.bot.loop.stop()
