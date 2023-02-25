# ToDos and Notes

## tweets.py
- a Twitter account can't be configured twice (with diferent filters and webhooks for example)
  - will require a larger refactoring, might be a reason to look for alternative library
- Delete this module if the API becomes useless

## twitchdumper.py
- gather follower counts (currently missing in user info)

## twitch.py
- command guard based on mod/vip/sub
- move token maintenance here
- provide requests session (see session in feeds.py or search.py)
  - https://stackoverflow.com/questions/42601812/python-requests-url-base-in-session
- move pulling of stream/user info here

## other ideas
- autojoin all followed channels
- check if channels become partner/affiliate/reset/banned and send notification to webhook or channel
- configurable commands that reply a fixed text
  - possibility to autotrigger/timer
  - optional storage.py support with configuration commands (guarded)
- "standard" Twitch commands like !followage and maybe game/title change (guarded)
- counters per game and/or channel
