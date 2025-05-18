#!/usr/bin/env bash

MODULE_NAME=app.main
VARIABLE_NAME=${VARIABLE_NAME:-app}
export APP_MODULE=${APP_MODULE:-"$MODULE_NAME:$VARIABLE_NAME"}

export PYTHONPATH=$PYTHONPATH:/appuser

HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
LOG_LEVEL=${LOG_LEVEL:-info}

trap 'kill "${child_pid}"; wait "${child_pid}"' INT TERM SIGTERM

case "$1" in
  "start")
    echo "Running migrations..."
    alembic upgrade head

    echo "Starting web server with uvicorn..."
    uvicorn ${APP_MODULE} --host ${HOST} --port ${PORT} --log-level ${LOG_LEVEL} --proxy-headers &
    ;;
  "migrate")
    echo "Running migrations..."
    alembic upgrade head
    ;;
  "start-reload")
    echo "Running migrations..."
    alembic upgrade head

    echo "Starting reload server ${HOST}:${PORT}..."
    uvicorn --reload --host ${HOST} --port ${PORT} --log-level ${LOG_LEVEL} "$APP_MODULE" &
    ;;
  *)
    exec ${@}
    ;;
esac

child_pid=$!
wait "${child_pid}"