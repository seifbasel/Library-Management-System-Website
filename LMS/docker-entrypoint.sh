#!/bin/sh
# Runs on every container start, before the actual server process (see
# Dockerfile's CMD). Keeps a fresh deployment always on the latest schema
# and static files without a separate manual "release" step.
set -e

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

exec "$@"
