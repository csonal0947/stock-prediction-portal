#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Populate stock data if database is empty
python manage.py add_sample_stocks
python manage.py fetch_exchange_listings || true
