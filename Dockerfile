FROM python:3.10-alpine

WORKDIR /opt/irc3
COPY ./requirements.txt ./
RUN PIP_ROOT_USER_ACTION=ignore pip install --no-cache-dir -r requirements.txt
COPY *.py ./
RUN python -m compileall ./ ; irc3 --version

ENV LANG=C.UTF-8
ENV TZ=Europe/Berlin
ENV IRC3_LOGGING="--logdate"
ENV IRC3_CONFIG="config.ini"
CMD irc3 "${IRC3_LOGGING}" "${IRC3_CONFIG}"
