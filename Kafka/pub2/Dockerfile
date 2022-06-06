FROM python:3

ADD pub2.py /pub2/

WORKDIR /pub2/

RUN pip install requests
RUN pip install kafka-python
RUN pip freeze
RUN pip uninstall bson
RUN pip install pymongo