#!/usr/bin/env bash

set -euo pipefail

if [ -z "${POSTGRES_USER:-}" ]; then
  echo "ERROR: POSTGRES_USER is required." >&2
  exit 1
fi

if [ -z "${POSTGRES_PASSWORD:-}" ]; then
  echo "ERROR: POSTGRES_PASSWORD is required." >&2
  exit 1
fi

if [ "${POSTGRES_USER}" = "postgres" ]; then
  echo "ERROR: POSTGRES_USER must not be the default value 'postgres'." >&2
  exit 1
fi

if [ "${POSTGRES_PASSWORD}" = "postgres" ]; then
  echo "ERROR: POSTGRES_PASSWORD must not be the default value 'postgres'." >&2
  exit 1
fi

if [ "${#POSTGRES_PASSWORD}" -lt 8 ]; then
  echo "ERROR: POSTGRES_PASSWORD must be at least 8 characters." >&2
  exit 1
fi

exec docker-entrypoint.sh "$@"
