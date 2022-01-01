#!/bin/sh

docker build -t apply .
docker run -it --cap-add=NET_ADMIN -p 8888:80 --rm apply:latest
