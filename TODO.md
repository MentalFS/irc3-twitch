# ToDos and Notes

## tweets.py
- a Twitter account can't be configured twice (with diferent filters and webhooks for example)
- Delete this module if the API becomes useless

## twitchdumper.py
- gather follower counts (currently missing in user info)
- `view_count` is deprecated: https://discuss.dev.twitch.tv/t/get-users-api-endpoint-view-count-deprecation/37777
- dont write anything when nothing was changed on user endpoint
- increase user poll interval to every 10 minutes

## twitch.py
- command guard based on mod/vip/sub
- move token maintenance here
- provide requests session (see session in feeds.py or search.py)
  - https://stackoverflow.com/questions/42601812/python-requests-url-base-in-session
- move pulling of stream/user info here

## other ideas
- autojoin all followed channels
- autojoin streamers playing a certain game (minimum viewer amount configurable)
- Generate RSS feed with current and past stream per streamer (optional push to Discord)
- Generate RSS feed with user states (partner/affiliate/pleb/not found) (optional push to Discord)
- Automatically join in when people spam certain words/patterns like "!play" or "nice"
- configurable commands that reply a fixed text
  - optional storage.py support with configuration commands (guarded)
  - https://docs.python.org/3/tutorial/inputoutput.html#the-string-format-method

## tools
- cleanup of old logs (before deltas were used)
- tools to analyze `twitchdumper.py` logs

## limitations
- I think when API auth is neccessary, a different library than `irc3` should be used
