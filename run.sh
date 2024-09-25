#!/bin/bash

# to stop on first error
set -e

# Delete older .pyc files
# find . -type d \( -name env -o -name venv  \) -prune -false -o -name "*.pyc" -exec rm -rf {} \;

# Run required migrations
export FLASK_APP=core/server.py

# flask db init -d core/migrations/
# flask db migrate -m "Initial migration." -d core/migrations/
# flask db upgrade -d core/migrations/

# Run server
nohup gunicorn -c gunicorn_config.py core.server:app &

pytest -vvv -s tests/*.py
# pytest --cov
pytest --cov=core --cov-report=html
xdg-open htmlcov/index.html