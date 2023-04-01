#!/usr/bin/env bash
# exit on error
set -o errexit

sudo apt install python3.11-dev
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate