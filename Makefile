NAME = irc3-twitch

.PHONY: build pull release
SHELL := /bin/bash

build:
	docker build -t $(NAME):build .

pull:
	docker build --pull .

release:
	docker build --pull -t $(NAME):latest .

test:
	python3 -m venv venv
	pip install -r requirements.txt
	source venv/bin/activate
	bin/irc3-bot test --test
