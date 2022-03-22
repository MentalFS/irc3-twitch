# Plans and ToDos

## Plugins

### tweets.py
- add reload capability
- BUG: a Twitter account can't be configured twice (with diferent filters and webhooks for example)

### rawlogger.py
- add reload capability

### twitchdumper.py
- add reload capability
- rename to streamlogger or twitchlogger
- consider removing user.log or only writing when stream is active

### twitch.py
- add reload capability
- move token maintenance here
- centralize checks for streams/users and make them events or pollable
- repeat outgoing NOTICE as PRIVMSG or CTCP ACTION to make built in commands work

## other plugin ideas
- check if channels become partner/affiliate with webhook
- periodically call /mods and /vips
- autojoin all followed channels

## general
- configure logfiles
- better documentation/examples
- restructure project to look more Python-esque
