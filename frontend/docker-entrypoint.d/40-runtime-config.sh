#!/bin/sh
set -eu

: "${APP_ENVIRONMENT:=production}"
: "${API_BASE_URL:=http://127.0.0.1:8000}"
: "${REGIONS_DATA_URL:=/regions.json}"
: "${SURVEY_ENABLED:=false}"

envsubst '${APP_ENVIRONMENT} ${API_BASE_URL} ${REGIONS_DATA_URL} ${SURVEY_ENABLED}' \
    < /opt/runtime-config/runtime-config.template.js \
    > /usr/share/nginx/html/runtime-config.js
