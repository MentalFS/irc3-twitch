# Ideas for future development

## twitch.py
- command guard based on mod/vip/sub
- move api calls to `twitch.py` (or an own plugin) to provide data to `apilogger.py`
  - and later on data for command replacements
  - only call the API when the endpoint is needed (event registration or own plugins per endpoint)
- warning if a joined channel gets no `ROOMSTATE`

## apilogger.py
- alerts (push to Discord webhook) on change of `type` or `broadcaster_type`

## other ideas
- configurable commands that reply a fixed text
  - replacements: https://docs.python.org/3/tutorial/inputoutput.html#the-string-format-method
  - timed commands or messsages
- automatically join in when people spam certain words/patterns like "!play" or "nice"

## general
- tools to analyze `apilogger.py` logs
- provide example `config.ini` file
