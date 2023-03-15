# ToDos and Notes

## twitchdumper.py
- gather follower counts (currently missing in user info)
- `view_count` is deprecated: https://discuss.dev.twitch.tv/t/get-users-api-endpoint-view-count-deprecation/37777
- dont write anything when nothing was changed on user endpoint
  - then increase user poll interval to every 10 minutes
- split up into modules per endpoint (user, stream, follows?)
- consider switching to sqlite databases per user/month
  - in a test phase parallel to file logging
  - dynamically add new fields and search for a way to store only deltas
  - alternatively only select fields that are of interest

## twitch.py
- command guard based on mod/vip/sub
- move token maintenance here
- provide requests session (see session in feeds.py or search.py)
  - https://stackoverflow.com/questions/42601812/python-requests-url-base-in-session
- move pulling of stream/user info here
- reorganize to a folder structure

## other ideas
- autojoin all followed channels
- autojoin streamers playing a certain game (minimum viewer amount configurable)
- Alerts (optional push to Discord)
  - when a streamer goes live (filters for channels, games or title keywords)
  - on change of `broadcaster_type`
  - when channel can't be found anymore/is banned or deleted
- execute command when someone enters chat (with cooldown)
  - `bot.get_plugin(command.Commands)`.`on_command('put', mask, mask.nick, data='xx yy')`
- Automatically join in when people spam certain words/patterns like "!play" or "nice"
- configurable commands that reply a fixed text
  - optional storage.py support with configuration commands (guarded)
  - https://docs.python.org/3/tutorial/inputoutput.html#the-string-format-method

## tools
- cleanup or migration of old logs (before deltas were used)
- tools to analyze `twitchdumper.py` logs
