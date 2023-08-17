FROM alpine:3.18.3 AS python3-alpine
RUN apk add --no-cache python3 py3-pip ca-certificates tzdata

FROM python3-alpine AS build
WORKDIR /opt/irc3
COPY ./requirements.txt ./
RUN PIP_ROOT_USER_ACTION=ignore pip install --no-cache-dir -r requirements.txt
COPY *.py ./
RUN python -m compileall ./ && irc3 --version && mkdir cache && chmod a+rw cache

ENV LANG=C.UTF-8
ENV TZ=Europe/Berlin
ENV IRC3_LOGGING="--logdate"
ENV IRC3_CONFIG="config.ini"
CMD irc3 "${IRC3_LOGGING}" "${IRC3_CONFIG}"
