NAME = irc3-twitch

.PHONY: build pull release

build:
	docker build -t $(NAME):build .

pull:
	docker build --pull .

release:
	docker build --pull -t $(NAME):latest .
