FROM python:alpine3.24

WORKDIR /opt/irc3
COPY ./setup.py ./
COPY plugins /opt/irc3/plugins
RUN set -eux; \
    pip install --root-user-action=ignore --no-cache-dir --compile .; \
    python -m compileall plugins; \
    mkdir cache; \
    chmod a+rw cache; \
    pip freeze | tee requirements.txt

ENV LANG=C.UTF-8
ENV TZ=Europe/Berlin
CMD ["irc3", "--logdate", "config.ini"]
