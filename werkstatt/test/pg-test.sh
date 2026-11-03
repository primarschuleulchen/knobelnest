#!/bin/bash
# Prüft supabase/schema.sql in einer Wegwerf-Datenbank (lokales PostgreSQL mit nachgebauten Supabase-Teilen).
# Aufruf im Repo-Hauptordner: bash werkstatt/test/pg-test.sh      (braucht PostgreSQL 14+, z. B. apt-get install postgresql)
set -e
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BIN=$(ls -d /usr/lib/postgresql/*/bin 2>/dev/null | sort -V | tail -1)
[ -n "$BIN" ] || { echo "PostgreSQL nicht gefunden (apt-get install -y postgresql)"; exit 1; }
D=/tmp/kn-pg; PORT=5499
if [ ! -d "$D/data" ]; then
  mkdir -p $D && chown postgres $D
  su postgres -c "$BIN/initdb -D $D/data -A trust >/dev/null"
fi
rm -f $D/.s.PGSQL.$PORT.lock $D/data/postmaster.pid
su postgres -c "$BIN/pg_ctl -D $D/data -o '-k $D -p $PORT -c listen_addresses=' -l $D/log start >/dev/null" || true
sleep 2
PSQL="su postgres -c"
cp "$ROOT/werkstatt/test/supabase-stub.sql" "$ROOT/supabase/schema.sql" "$ROOT/werkstatt/test/sql-grundtest.sql" $D/ && chmod 644 $D/*.sql
$PSQL "psql -h $D -p $PORT -q -f $D/supabase-stub.sql postgres" >/dev/null 2>&1 || true   # beim zweiten Mal gibt es «already exists», das ist gut so
$PSQL "psql -h $D -p $PORT -q -v ON_ERROR_STOP=1 -f $D/schema.sql postgres" 2>&1 | grep -v NOTICE || true
echo "schema.sql geladen. Grundtest:"
$PSQL "psql -h $D -p $PORT -f $D/sql-grundtest.sql postgres" 2>&1 | tail -25
echo "Eigene Abfragen: su postgres -c \"psql -h $D -p $PORT postgres\""
