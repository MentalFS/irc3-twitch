# Ideas for future development

## twitch.py
- command guard based on mod/vip/sub
- move api calls to `twitch.py` to provide data to `apilogger.py`
  - and later on data for command replacements
  - only call the API when the endpoint is needed (event registration)

## apilogger.py
- remove `view_count` from user delta
- dont't write delta when it's empty/`None` and increase poll interval
- only log endpoints when live
- add channel endpoint
- alerts (push to Discord webhook) on change of `type` or `broadcaster_type`

## rawlogger.py
- rework filters to blacklist by IRC message type
- enable blacklisting IRC message types by channel (list)

## other ideas
- configurable commands that reply a fixed text
  - replacements: https://docs.python.org/3/tutorial/inputoutput.html#the-string-format-method
  - timed commands or messsages
- automatically join in when people spam certain words/patterns like "!play" or "nice"

## general
- provide example `config.ini` file
- cleanup or migration of old logs (before deltas were used)
- tools to analyze `apilogger.py` logs
