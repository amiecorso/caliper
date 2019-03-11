# Dockerfile for do-nothing tp python for Sawtooth
# (based on Dockerfile for simple tp python for Sawtooth)
# ------------------------------------------------------------------------------

# Description:
#   Builds an image of a do-nothing TP for Sawtooth in Python  installed from
#   local debs.
#
# Build:
#   This image should be built using `build_all installed`.
#
# Run:
#   $ docker run sawtooth-do-nothing-tp-python

FROM ubuntu:xenial

ARG DEBIAN_FRONTEND=noninteractive

RUN echo "deb http://repo.sawtooth.me/ubuntu/ci xenial universe" >> /etc/apt/sources.list \
 && (apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 8AA7AF1F1091A5FD \
 || apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 8AA7AF1F1091A5FD)
RUN apt-get update \
 && apt-get install -y -q --allow-downgrades \
    git \
    python3 \
    python3-stdeb \
    python3-pip
RUN pip3 install --upgrade pip
RUN pip3 install grpcio \
 && pip3 install grpcio-tools \
 && pip3 install protobuf \
 && pip3 install sawtooth-sdk \
 && pip3 install sawtooth-signing \
 && apt-get install -y -q --allow-downgrades \
    python3-cbor \
    python3-colorlog \
    python3-toml \
    python3-yaml \
    python3-zmq \
    software-properties-common \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /project/src/contract/sawtooth/do_nothing/do_nothing_python
#WORKDIR /project/src/contract/sawtooth/simple/simple_python

ENV PATH "$PATH:/project/:/project/src/contract/sawtooth/do_nothing/do_nothing_python:."
#ENV PATH "$PATH:/project/:/project/src/contract/sawtooth/simple/simple_python:."

RUN echo "$PATH"
RUN echo "`pwd`"
EXPOSE 4004/tcp

CMD unset PYTHONPATH && python3 setup.py clean --all && python3 setup.py build
