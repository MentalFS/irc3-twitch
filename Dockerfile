# Wait for release 1.1.8
FROM python:3.9-alpine
#FROM python:alpine

RUN addgroup --system irc3 \
    && adduser --system --ingroup irc3 irc3 \
    && mkdir /data \
    && chown irc3:irc3 /data

WORKDIR irc3
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY *.py .

USER irc3
ENV IRC3_CONFIG=config.ini
ARG IRC3_ARGS="--logdate"
ENTRYPOINT irc3 ${IRC3_ARGS} /data/${IRC3_CONFIG}
VOLUME /data