#!/bin/bash

sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3.11-venv -y

python3 -m venv venv
. ./venv/bin/activate
pip install -r requirements.txt