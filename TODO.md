# Ideas for future development

## `plugins.twitch`
- command guard based on mod/vip/sub
- warning if a joined channel gets no `ROOMSTATE`

## `plugins.apilogger`
- alerts (push to Discord webhook) on change of `type` or `broadcaster_type`
- alerts (push to Discord webhook) on `NOTICE` with `msg-id=tos_ban` or `msg-id=invalid_user`

## other ideas
- automatically join in when people spam certain words/patterns like "!play" or "nice"

## general
- rebuild the shell scripts as python scripts and make them entrypoints
- tools to analyze `plugins.apilogger` logs
