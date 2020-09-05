FROM python:3.7-slim-buster
MAINTAINER radeox "dawid.weglarz95@gmail.com"

ENV PYTHONUNBUFFERED 1

RUN apt update && apt install locales -y && rm -rf /var/lib/apt/lists/*

# RUN locale-gen it_IT.UTF-8

RUN sed -i -e 's/# it_IT.UTF-8 UTF-8/it_IT.UTF-8 UTF-8/' /etc/locale.gen && locale-gen
ENV LANG it_IT.UTF-8
ENV LANGUAGE it_IT.UTF-8
ENV LC_ALL it_IT.UTF-8
# RUN touch /usr/share/locale/locale.alias

COPY requirements.txt /
RUN pip install --no-cache-dir -r requirements.txt
WORKDIR /app/
