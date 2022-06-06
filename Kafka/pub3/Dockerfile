FROM python:3

ADD pub3.py /pub3/

WORKDIR /pub3/

RUN pip install requests
RUN pip install kafka-python
RUN pip freeze
RUN pip uninstall bson
RUN pip install pymongo
