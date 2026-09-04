#!/usr/bin/env bash
# Run attrition analytics against the local SQLite database.
#
# Setup / reset schema + reload data:
#   sqlite3 data/processed/attrition.db < sql/schema.sql
#   python3 src/etl_pipeline.py
#
# Analytics only (this script):
set -euo pipefail
cd "$(dirname "$0")/.."

DB="data/processed/attrition.db"
if [[ ! -f "$DB" ]]; then
  echo "Missing $DB — run: python3 src/etl_pipeline.py" >&2
  exit 1
fi

sqlite3 -header -column "$DB" < sql/queries.sql
