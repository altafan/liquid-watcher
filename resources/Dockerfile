FROM ubuntu:18.04

RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip3 install virtualenv

ADD . /liquid-watcher

WORKDIR /liquid-watcher

RUN virtualenv -p python3 .venv
