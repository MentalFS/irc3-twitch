# Plans and ToDos

## Plugins

### tweets.py
- a Twitter account can't be configured twice (with diferent filters and webhooks for example)
  - will require a larger refactoring
- Delete this module if Space Karen actually kills the API

### twitchdumper.py
- gather follower counts (currently missing in user info)

### twitch.py
- move token maintenance here
- provide requests session (see session in feeds.py or search.py)
  - https://stackoverflow.com/questions/42601812/python-requests-url-base-in-session
- command guard based on mod/vip/sub

## other plugin ideas
- autojoin all followed channels
- check if channels become partner/affiliate and send notification to webhook or channel
- Marbles on Stream autoplayer
- replace twitchdumper.py with database plugin (sqlite files per channel/month)
  - only save meaningful fields, split out volatile data, save end of stream timestamp
  - provide migration path from old files
- configurable commands that reply a fixed text
  - possibility to autotrigger/timer
  - optional storage.py support with configuration commands (guarded)
- "standard" Twitch commands like !followage and maybe game/title change (guarded)
- counters per game and/or channel

## general
- tools to analyse/visualize logs
- better logging (logging.getLogger)
- docker compose scripts
- better documentation/examples
