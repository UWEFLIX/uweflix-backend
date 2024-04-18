#!/bin/bash

echo Creating Service
echo "[Unit]
Description=UWE-Flix Backend

[Service]
ExecStart=/home/usr/uweflix-backend/uweflix-backend/run.sh
Restart=always

[Install]
WantedBy=default.target
" > /etc/systemd/user/uweflix-backend.service
