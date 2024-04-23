#!/bin/bash

cd uweflix-backend && git pull && cd ..
sudo docker container rm uweflix-backend -f
sudo docker rmi uweflix-backend -f

sudo docker build -t uweflix-backend . && \
sudo docker run -itd --restart=always --name uweflix-backend --network host --volume uweflix:/volume  uweflix-backend
