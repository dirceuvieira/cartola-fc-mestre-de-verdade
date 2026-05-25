#!/usr/bin/env bash
# Apply Supabase migration using psql CLI (Unix)
# Usage:
#   export SUPABASE_DB_HOST=... SUPABASE_DB_PORT=5432 SUPABASE_DB_NAME=postgres SUPABASE_DB_USER=postgres SUPABASE_DB_PASSWORD=...
#   ./scripts/apply_supabase_migration.sh

set -euo pipefail

MIGRATION_PATH=${1:-db/supabase_migration.sql}

if [ ! -f "$MIGRATION_PATH" ]; then
  echo "Migration file not found: $MIGRATION_PATH" >&2
  exit 1
fi

HOST=${SUPABASE_DB_HOST:-${PGHOST:-}}
PORT=${SUPABASE_DB_PORT:-${PGPORT:-5432}}
DB=${SUPABASE_DB_NAME:-${PGDATABASE:-}}
USER=${SUPABASE_DB_USER:-${PGUSER:-}}
PASS=${SUPABASE_DB_PASSWORD:-${PGPASSWORD:-}}

if [ -z "$HOST" ] || [ -z "$DB" ] || [ -z "$USER" ] || [ -z "$PASS" ]; then
  echo "Missing DB credentials. Set SUPABASE_DB_HOST/NAME/USER/PASSWORD or PGHOST/PGDATABASE/PGUSER/PGPASSWORD" >&2
  exit 2
fi

if ! command -v psql >/dev/null 2>&1; then
  echo "psql not found in PATH. Install PostgreSQL client." >&2
  exit 3
fi

export PGPASSWORD="$PASS"
psql -h "$HOST" -p "$PORT" -U "$USER" -d "$DB" -f "$MIGRATION_PATH"

unset PGPASSWORD

echo "Migration applied successfully."