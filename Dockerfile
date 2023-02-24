FROM python:3-alpine

WORKDIR /opt/irc3
RUN python -m venv /opt/venv
COPY ./requirements.txt ./
RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt
COPY *.py ./
RUN /opt/venv/bin/python -m compileall ./

ENV LANG=C.UTF-8
ENV TZ=Europe/Berlin
ENV IRC3_LOGGING="--logdate"
ENV IRC3_CONFIG="/etc/irc3/config.ini"
ENTRYPOINT /opt/venv/bin/python
CMD irc3 "${IRC3_LOGGING}" "${IRC3_CONFIG}"
