FROM python:3.12.2-alpine

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
