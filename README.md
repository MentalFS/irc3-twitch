# IRC3 Plugins

## Overview
This is a repository with [irc3](https://github.com/gawel/irc3) plugins for my personal use. IRC3 is a nice IRCv3 complient framework using Python. 

They are mostly centered around usage on the [Twitch network](https://dev.twitch.tv/docs/irc), which does'n exactly behave like other networks. I'm trying to make modules that don't have *twitch* in their name work on regular IRC networks though.

## Plugins

### tweets.py
Connects to the [Twitter streaming API](https://developer.twitter.com/en/docs/tweets/filter-realtime/api-reference/post-statuses-filter) and posts new tweets of users into a definable set of channels. Also hat the capability to post to a [Discord Webhook](https://discordapp.com/developers/docs/resources/webhook).
* Requires [twitter](https://pypi.org/project/twitter/) and [requests](https://pypi.org/project/requests/).

### rawlogger.py
Logs messages (only to channels) as raw IRC lines to files.
* Requires [tzlocal](https://pypi.org/project/tzlocal/) / [pytz](https://pypi.org/project/pytz/).

### twitch.py
Enables IRCv3 capabilities on the Twitch network and does some basic handling.

### twitchdumper.py
Logs [JSON API requests](https://dev.twitch.tv/docs/api) about the Twitch channels the client is joined to. Those can become quite large, so they only write a timestamp when the JSON object didn't change.
* Requires [tzlocal](https://pypi.org/project/tzlocal/) / [pytz](https://pypi.org/project/pytz/) and [requests](https://pypi.org/project/requests/).

## Scripts

### irc3-bot
A starter script that I use to keep IRC bots running via cron.
