# -*- coding: utf-8 -*-
import irc3
from irc3.plugins.command import Commands


class Access(object):
	bot = None
	channels = {}
	users = {}

	def __init__(self, bot):
		self.bot = bot


@irc3.plugin
class Twitch:
	requires = [Commands.__module__]

	def __init__(self, bot):
		self.bot = bot
		self.access = Access(bot)
		self.bot.twitch = self.access

	def connection_made(self):
		self.bot.send('CAP REQ :twitch.tv/membership')
		self.bot.send('CAP REQ :twitch.tv/tags')
		self.bot.send('CAP REQ :twitch.tv/commands')
		self.access.channels = {}
		self.access.users = {}


	@irc3.event('@(\S+;)?room-id=(?P<user>\d+)(;\S+)? :\S+ ROOMSTATE #(?P<channelname>\S+)( :.*)?', iotype='in')
	def on_roomstate_channel(self, user, channelname):
		self.bot.log.debug('TWITCH ROOMSTATE: #%s - %s' % (channelname, user))
		self.access.channels[user] = channelname
		self.access.users[channelname] = user

	@irc3.event('(@\S+ )?PART #(?P<channelname>\S+)( :.*)?', iotype='out')
	def on_part_channel(self, channelname):
		self.bot.log.debug('TWITCH PART: #%s' % channelname)
		if channelname in self.access.users:
			user = self.access.users[channelname]
			del self.access.users[channelname]
			if user in self.access.channels and self.access.channels[user] == channelname:
				del self.access.channels[user]

	@irc3.event('(@\S+ )?:(?P<nickname>\S+)!\S+ PART #(?P<channelname>\S+)( :.*)?', iotype='in')
	def on_part_channel_message(self, channelname, nickname):
		if nickname != self.bot.nick: return
		self.on_part_channel(channelname)


	@irc3.event('(@\S+ )?:\S+ RECONNECT( .*)?', iotype='in')
	def on_reconnect_message(self):
		self.bot.log.info('Twitch requested a reconnect.')
		plugin = self.bot.get_plugin(irc3.utils.maybedotted('irc3.plugins.core.Core'))
		self.bot.loop.call_soon(plugin.reconnect)


	@irc3.event((r'(@(?P<tags>\S+) )?:(?P<mask>\S+) WHISPER (?P<target>\S+) '
				 r':{re_cmd}(?P<cmd>[\w-]+)(\s+(?P<data>\S.*)|(\s*$))'))
	def on_whisper_command(self, cmd, mask=None, target=None, client=None, **kw):
		self.bot.log.debug('Received WHISPER COMMAND: %s' % cmd)
		commands = self.bot.get_plugin(Commands)
		commands.on_command(cmd, mask=mask, target=target, client=client, **kw)

	@irc3.event('(@\S+ )?NOTICE (?P<target>\S+) :(?P<data>.*)', iotype='out')
	def on_send_notice(self, target, data):
		self.bot.log.debug('Repeated NOTICE as PRIVMSG: %s %s' % (target, data))
		if target.startswith('#'):
			self.bot.privmsg(target, data)
		else:
			self.bot.privmsg('#%s' % target, "/w %s %s" % (target, data))

	@irc3.event('(@\S+ )?PRIVMSG (?P<user>[^#]\S+) :(?P<data>.*)', iotype='out')
	def on_send_whisper(self, user, data):
		self.bot.log.debug('Repeated PRIVMSG as WHISPER: /w %s %s' % (user, data))
		self.bot.privmsg('#%s' % user, "/w %s %s" % (user, data))