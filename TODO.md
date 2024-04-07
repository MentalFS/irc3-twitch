# Ideas for future development

## `plugins.twitch`
- command guard based on mod/vip/sub
- move api calls to `plugins.twitch` (or an own plugin) to provide data to `plugins.apilogger`
  - and later on data for command replacements
  - only call the API when the endpoint is needed (event registration or own plugins per endpoint)
- warning if a joined channel gets no `ROOMSTATE`

## `plugins.apilogger`
- alerts (push to Discord webhook) on change of `type` or `broadcaster_type`

## other ideas
- configurable commands that reply a fixed text
  - replacements: https://docs.python.org/3/tutorial/inputoutput.html#the-string-format-method
  - timed commands or messsages
- automatically join in when people spam certain words/patterns like "!play" or "nice"

## general
- rebuild the shell scripts as python scripts and make them entrypoints
- tools to analyze `plugins.apilogger` logs
- provide example `config.ini` file
