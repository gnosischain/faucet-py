FROM python:3.8-slim-buster

WORKDIR api

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ['gunicorn', '-b', '0.0.0.0', 'api:create_app()']