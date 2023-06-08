# Ideas for future development

## twitch.py
- command guard based on mod/vip/sub
- provide requests session (see session in feeds.py or search.py)
  - https://stackoverflow.com/questions/42601812/python-requests-url-base-in-session
- move token maintenance here

## apilogger.py
- remove `view_count` from delta - delta will be empty
- read current log to determine delta base
- alerts (push to Discord webhook)
  - on change of `type` or `broadcaster_type`
  - when channel can't be found anymore/is banned or deleted

## other ideas
- configurable commands that reply a fixed text
  - replacements: https://docs.python.org/3/tutorial/inputoutput.html#the-string-format-method
  - timed commands or messsages
- automatically join in when people spam certain words/patterns like "!play" or "nice"

## general
- cleanup or migration of old logs (before deltas were used)
- tools to analyze `apilogger.py` logs
