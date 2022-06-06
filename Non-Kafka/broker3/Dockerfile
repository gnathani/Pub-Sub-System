FROM python:3

ADD . /broker3/

WORKDIR /broker3/

RUN pip install -r requirements.txt

RUN export FLASK_APP=broker3

RUN export FLASK_ENV=development