FROM python:3.8-alpine

ENV DEBUG=0 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /online_store

COPY . .

RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql-dev \
    && pip install psycopg2 \
    && apk del build-deps \
    && pip install -r requirements.txt \
    && adduser -D online_store

USER online_store

CMD gunicorn online_store.wsgi:application --bind 0.0.0.0:$PORT
