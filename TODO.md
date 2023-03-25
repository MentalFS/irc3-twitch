# ToDos and Notes

## twitchdumper.py
- `view_count` is deprecated: https://discuss.dev.twitch.tv/t/get-users-api-endpoint-view-count-deprecation/37777
- detect missing users in responses
- dont write anything when nothing was changed on user endpoint
  - then increase user poll interval to every 10 minutes
- gather follower count (needs user token)
  - add that info to user endpoint files

## twitch.py
- command guard based on mod/vip/sub
- provide requests session (see session in feeds.py or search.py)
  - https://stackoverflow.com/questions/42601812/python-requests-url-base-in-session
- move token maintenance here
- move pulling of stream/user info here, with cache
- user token with https://dev.twitch.tv/docs/authentication/getting-tokens-oauth/#implicit-grant-flow

## other ideas
- Alerts (optional push to Discord)
  - on change of `broadcaster_type`
  - when channel can't be found anymore/is banned or deleted
  - when a streamer goes live
- autojoin all followed channels (needs user token)
- autojoin streamers playing a certain game (minimum viewer amount configurable)
- Automatically join in when people spam certain words/patterns like "!play" or "nice"
- configurable commands that reply a fixed text
  - replacements: https://docs.python.org/3/tutorial/inputoutput.html#the-string-format-method
  - timed commands or messsages

## general
- helper hooks for feeds.py to strip html from description
- reorganize to a folder structure
- cleanup or migration of old logs (before deltas were used)
- tools to analyze `twitchdumper.py` logs
- consider using sqlite databases instead of json files for stats
  - https://www.sqlite.org/json1.html
