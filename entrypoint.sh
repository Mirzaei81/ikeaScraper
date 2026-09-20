#!/bin/sh
set -e

# The UID/GID the app should run as (match your host user!)
APP_UID="${APP_UID:-1000}"
APP_GID="${APP_GID:-1000}"
mkdir -p /data
# The directory that needs to be read/writable
DATA_DIR="${DATA_DIR:-/data}"

echo "🔧 Fixing permissions on ${DATA_DIR} for ${APP_UID}:${APP_GID}"

# Only do this if we're starting as root
if [ "$(id -u)" = "0" ]; then
    # Ensure the data dir exists and is owned by the app user
    mkdir -p "$DATA_DIR"
    chown -R "${APP_UID}:${APP_GID}" "$DATA_DIR"
    chmod -R u+rwX "$DATA_DIR"

    # Drop privileges and exec the command as the app user
    exec gosu "${APP_UID}:${APP_GID}" "$@"
else
    # Already running as non-root, just exec
    exec "$@"
fi