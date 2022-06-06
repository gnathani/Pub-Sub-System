FROM python:3

ADD . /broker2/

WORKDIR /broker2/

RUN pip install -r requirements.txt

RUN export FLASK_APP=broker2

RUN export FLASK_ENV=development