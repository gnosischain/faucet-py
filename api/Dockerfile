FROM python:3.10-alpine

ENV PYTHONUNBUFFERED 1
WORKDIR /api

COPY requirements.txt ./

# Signal handling for PID1 https://github.com/krallin/tini
RUN apk add --update --no-cache tini libpq && \
    apk add --no-cache --virtual .build-dependencies alpine-sdk libffi-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del .build-dependencies && \
    find /usr/local \
        \( -type d -a -name test -o -name tests \) \
        -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
        -exec rm -rf '{}' +

COPY . .

ENTRYPOINT ["/sbin/tini", "--"]