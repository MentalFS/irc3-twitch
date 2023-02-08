FROM python:3-alpine

ENV LANG=C.UTF-8
ENV TZ=Europe/Berlin

WORKDIR irc3
COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY *.py ./
RUN python -m compileall ./

RUN mkdir -p /data/logs && chown 1000:1000 /data -R
RUN ln -s /data/config.ini && ln -s /data/logs/
USER 1000
VOLUME /data

ENV IRC3_LOGGING="--logdate"
ENTRYPOINT irc3 "${IRC3_LOGGING}" config.ini
