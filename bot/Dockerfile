FROM python:3.9-slim-buster
MAINTAINER radeox "dawid.weglarz95@gmail.com"

ENV PYTHONUNBUFFERED 1

RUN apt update && apt install gcc locales -y && rm -rf /var/lib/apt/lists/*
RUN sed -i -e 's/# it_IT.UTF-8 UTF-8/it_IT.UTF-8 UTF-8/' /etc/locale.gen && locale-gen
COPY requirements.txt /
RUN pip install --no-cache-dir -r requirements.txt
WORKDIR /app/
