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

### twitch.py
- add reload capability
- move token maintenance here
- centralize checks for streams/users and make them events (as own plugins)
- repeat outgoing NOTICE as PRIVMSG or CTCP ACTION to make built in commands work

## other plugin ideas
- autojoin all followed channels
- check if channels become partner/affiliate and send notification to webhook or channel

## general
- configure logfiles
- better documentation/examples
- restructure project to look more Python-esque
