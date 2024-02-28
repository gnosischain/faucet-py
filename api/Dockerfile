FROM python:3.8-alpine

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY . /api
WORKDIR /api

ENTRYPOINT ["/sbin/tini", "--"]