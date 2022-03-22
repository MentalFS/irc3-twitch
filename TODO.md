# Plans and ToDos

## Plugins

### tweets.py
- add reload capability
- BUG: a Twitter account can't be configured twice (with diferent filters and webhooks for example)
- command to process a specific tweet without filtering

### rawlogger.py
- add reload capability

### twitchdumper.py
- add reload capability
- rename to streamlogger or twitchlogger
- only write user.log when streaming (and at stream start) OR OMIT USER.LOG
- log or insert more data (game info, metadata)
- look for more `helix` data (tags, followers)

### twitch.py
- add reload capability
- make membership and commands capacity optional
- move token maintenance here
- offer shortcut methods for requests with cachable results
- centralize checks for streams and make them events
- repeat outgoing NOTICE as PRIVMSG or CTCP ACTION to make built in commands work
- or override `IrcConnection: whisper/notice/query translation for commands

## other plugin ideas
- check if channels become partner/affiliate with webhook
- periodically call /mods and /vips
- autojoin all followed channels
- autojoin followed channels when they stream
- autopart offline channels (not the autojoins, with timeout)
- autojoin channels from list when they stream
- autojoin raided or hosted channels (with restrictions)

## general
- configure logfiles
- better documentation/examples
- restructure project to look more Python-esque
- some kind of testing might be nice
