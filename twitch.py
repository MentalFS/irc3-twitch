# -*- coding: utf-8 -*-
from irc3.plugins.command import command
import irc3

@irc3.plugin
class Twitch:

	def __init__(self, bot):
		self.bot = bot

	def connection_made(self):
		self.bot.send('CAP REQ :twitch.tv/membership')
		self.bot.send('CAP REQ :twitch.tv/tags')
		self.bot.send('CAP REQ :twitch.tv/commands')
