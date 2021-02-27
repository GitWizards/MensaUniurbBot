FROM python:3.9-slim-buster
MAINTAINER radeox "dawid.weglarz95@gmail.com"

ENV PYTHONUNBUFFERED 1

COPY requirements.txt /
RUN pip install --no-cache-dir -r requirements.txt
WORKDIR /app/
