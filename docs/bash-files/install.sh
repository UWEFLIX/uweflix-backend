sudo apt update && sudo apt upgrade
apt install python3.10-venv

cd /home/usr/uweflix-backend/uweflix-backend
python3 -m venv .venv
. ./.venv/bin/activate
pip install -r requirements.txt
