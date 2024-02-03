FROM python:3.10-alpine

RUN mkdir code
WORKDIR code

RUN apk update && apk upgrade && \
    apk --no-cache add \
    gcc \
    curl

RUN pip install --upgrade pip

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

ADD . /code/

CMD python main.py