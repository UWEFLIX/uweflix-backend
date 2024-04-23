#!/bin/bash

git clone git@github.com:nishaalnaseer/uweflix-backend.git && \
sudo docker volume create uweflix && \
sudo docker build -t uweflix-backend . && \
sudo docker run -itd --restart=always --name uweflix-backend --network host --volume uweflix:/volume  uweflix-backend