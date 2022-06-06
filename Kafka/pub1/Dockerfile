FROM python:3

ADD pub1.py /pub1/

WORKDIR /pub1/

RUN pip install requests
RUN pip install kafka-python
RUN pip freeze
RUN pip uninstall bson
RUN pip install pymongo
