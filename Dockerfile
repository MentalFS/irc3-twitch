FROM alpine:3.19.0 AS python3-alpine

RUN apk add --no-cache python3 py3-pip ca-certificates tzdata
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

FROM python3-alpine AS build
WORKDIR /opt/irc3
COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt;

COPY *.py ./
RUN set -eux; \
    python -m compileall ./; \
    irc3 --version; \
    mkdir cache; \
    chmod a+rw cache

ENV LANG=C.UTF-8
ENV TZ=Europe/Berlin
ENV IRC3_LOGGING="--logdate"
ENV IRC3_CONFIG="config.ini"
CMD irc3 "${IRC3_LOGGING}" "${IRC3_CONFIG}"
