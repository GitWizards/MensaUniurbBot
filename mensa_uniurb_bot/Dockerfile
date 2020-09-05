FROM python:3.7-slim-buster
MAINTAINER radeox "dawid.weglarz95@gmail.com"

ENV PYTHONUNBUFFERED 1

RUN apt update && apt install gcc libffi-dev libssl-dev -y && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /
RUN pip install --no-cache-dir -r requirements.txt
WORKDIR /app/
