FROM ubuntu:18.04

RUN apt-get update && apt-get install -y \
python3 \
python3-pip \
git \
build-essential \
automake \
libtool \
swig

RUN pip3 install virtualenv

RUN git clone https://github.com/ElementsProject/libwally-core.git \
  && cd libwally-core \
  && ./tools/build_python_wheels.sh python3