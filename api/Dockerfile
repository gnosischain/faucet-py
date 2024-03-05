FROM python:3.8-alpine

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY . /api
WORKDIR /api

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "api:create_app()"]