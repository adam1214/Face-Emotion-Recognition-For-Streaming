FROM python:3.7
MAINTAINER Josip Janzic <josip@jjanzic.com>

RUN apt-get update \
    && apt-get install -y \
        cmake \
        git \
        vim \
    && rm -rf /var/lib/apt/lists/*

RUN pip --no-cache-dir install \
    tornado \
    nest_asyncio \
    opencv-python==4.1.1.26

COPY ./kaldi-gstreamer-server/kaldigstserver/client_example.py ./
COPY ./example_wav/Test.mp4 ./