#!/bin/bash

. "$(dirname "${BASH_SOURCE[0]}")/db-funcs.sh"

PGPASSWORD="$DB_PASSWORD" exec psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" "$@"
