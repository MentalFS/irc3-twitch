# -*- coding: utf-8 -*-
from irc3.plugins.command import command
import irc3

class Access(object):
	bot = None
	channels = {}
	users = {}

	def __init__(self, bot):
		self.bot = bot

@irc3.plugin
class Twitch:
	def __init__(self, bot):
		self.bot = bot
		self.access = Access(bot)
		self.bot.twitch = self.access

	def connection_made(self):
		#self.bot.send('CAP REQ :twitch.tv/membership')
		self.bot.send('CAP REQ :twitch.tv/tags')
		self.bot.send('CAP REQ :twitch.tv/commands')
		self.access.channels = {}
		self.access.users = {}


	@irc3.event('@(\S+;)?room-id=(?P<id>\d+)(;\S+)? :\S+ ROOMSTATE #(?P<channelname>\S+)( :.*)?', iotype='in')
	def on_roomstate_channel(self, id, channelname):
		self.bot.log.debug('TWITCH ROOMSTATE: #%s - %s' % (channelname, id))
		self.access.channels[id] = channelname
		self.access.users[channelname] = id

	@irc3.event('(@\S+ )?PART #(?P<channelname>\S+)( :.*)?', iotype='out')
	def on_part_channel(self, channelname):
		self.bot.log.debug('TWITCH PART: #%s' % channelname)
		#self.access.channels = { k:v for k, v in self.access.channels.items() if v != channelname }
		if channelname in self.access.users:
			id = self.access.users[channelname]
			del self.access.users[channelname]
			if id in self.access.channels:
				del self.access.channels[id]

	@irc3.event('(@\S+ )?:(?P<nickname>\S+)!\S+ PART #(?P<channelname>\S+)( :.*)?', iotype='in')
	def on_part_channel_message(self, channelname, nickname):
		if nickname != self.bot.nick: return
		self.on_part_channel(channelname)

	@irc3.event('(@\S+ )?:\S+ RECONNECT( .*)?', iotype='in')
	def on_reconnect_message(self, id, channelname):
		self.bot.log.info('Twitch requested a reconnect.')
		plugin = self.bot.get_plugin(irc3.utils.maybedotted('irc3.plugins.core.Core'))
		self.bot.loop.call_soon(plugin.reconnect)
