FROM python:3

ADD . /app

WORKDIR /app

RUN pip install -r requirements.txt

RUN export FLASK_APP=app

RUN export FLASK_ENV=development
