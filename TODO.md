# Plans and ToDos

## Plugins

### tweets.py
- BUG: a Twitter account can't be configured twice (with diferent filters and webhooks for example)

### twitchdumper.py
- gather follower counts (currently missing in user info)

### twitch.py
- move token maintenance here
- provide requests session (see session in feeds.py or search.py)
  - https://stackoverflow.com/questions/42601812/python-requests-url-base-in-session

## other plugin ideas
- autojoin all followed channels
- check if channels become partner/affiliate and send notification to webhook or channel
- replace twitchdumper.py with database plugin (sqlite files per channel/month)
  - only save meaningful fields, split out volatile data, save end of stream timestamp
  - provide migration path from old files

## general
- tools to analyse/visualize logs
- docker compose scripts
- better documentation/examples
