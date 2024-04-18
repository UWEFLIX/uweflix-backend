#!/bin/bash

echo Creating Service
echo "[Unit]
Description=Dashboard frontend

[Service]
ExecStart=/home/pi/Desktop/dashboard/run.sh
Restart=always

[Install]
WantedBy=default.target
" > /etc/systemd/user/dashboard.service
