# syntax=docker/dockerfile:1
FROM python:buster
WORKDIR /usr/src/app
COPY ./. .
ENV PYTHONUNBUFFERED=1
RUN pip3 install -r requirements.txt
