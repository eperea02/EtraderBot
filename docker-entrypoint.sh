#!/bin/bash
set -e
set -u

RUN() {
    ( PS4='# ' && set -x && "$@" )
}

export FLASK_APP=ETradeBot
export FLASK_ENV=production

# RUN flask init-db # Apply database migrations

# Start Gunicorn processes
echo Starting Gunicorn.
RUN exec gunicorn "EtradeBot:app" \
    --name=ECServiceCheck \
    --bind=0.0.0.0:8000 \
    --workers="${GUNICORN_WORKERS:-1}" \
    --worker-class="${GUNICORN_WORKER_CLASS:-"sync"}" \
    --threads="${GUNICORN_THREADS:-1}" \
    --log-level="${GUNICORN_LOG_LEVEL:-info}" \
    --log-file='-' \
    --error-logfile='-' \
    --access-logfile='-' \
    --access-logformat="${GUNICORN_ACCESSLOG_FORMAT:-%(t)s access [${SWISS_CLOUD_PLATFORM_METADATA_APPLICATION:--},${SWISS_CLOUD_PLATFORM_METADATA_SPACE:--},ECServiceCheck,${INSTANCE_ID:--}] [%({TraceId\}o)s] %(h)s %(u)s %(r)s %(U)s %(s)s %(D)s}" \
    "$@"


