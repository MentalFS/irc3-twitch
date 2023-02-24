NAME = irc3-bot

.PHONY: build build-pull pull release

build:
	docker build -t $(NAME):build .

build-pull:
	docker build --pull -t $(NAME):build .

pull:
	docker build --pull .

release:
	docker build --pull -t $(NAME):latest .
