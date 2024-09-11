NAME = irc3-twitch

.PHONY: build pull release
SHELL := /bin/bash

build:
	docker build -t $(NAME):build --progress=plain .

pull:
	docker build --pull --progress=plain .

release:
	docker build --pull -t $(NAME):latest --progress=plain .

test-docker: build
	docker run --rm -it -v "$(CURDIR)/test.ini:/opt/irc3/test.ini:ro" -e IRC3_CONFIG=test.ini $(NAME):build

test-local:
	python3 -m venv venv; \
	source venv/bin/activate; \
	pip install -r requirements.txt; \
	bin/irc3-bot test --test

test: test-docker

clean:
	rm -rfv venv logs */__pycache__ *.egg-info build
