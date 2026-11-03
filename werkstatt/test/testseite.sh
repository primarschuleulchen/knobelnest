#!/bin/bash
# Baut eine Testkopie des Knobelnests mit Schein-Datenbank (mock-db.js, alles im Speicher, keine echten Daten)
# und startet sie auf http://localhost:8765/   Aufruf im Repo-Hauptordner:  bash werkstatt/test/testseite.sh
set -e
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DST="${1:-/tmp/kn-test}"
rm -rf "$DST"; mkdir -p "$DST"
( cd "$ROOT" && tar --exclude=.git --exclude=werkstatt -cf - . ) | ( cd "$DST" && tar -xf - )
cp "$ROOT/werkstatt/test/mock-db.js" "$DST/"
# Supabase-Skript entfernen, db.js durch mock-db.js ersetzen
sed -i '/supabase-js/d; s#src="db.js#src="mock-db.js#' "$DST/index.html"
grep -q mock-db.js "$DST/index.html" || { echo "index.html konnte nicht umgestellt werden"; exit 1; }
pkill -f "http.server 8765" 2>/dev/null || true
cd "$DST" && (setsid nohup python3 -m http.server 8765 >/dev/null 2>&1 &)
sleep 1; echo "Testseite läuft: http://localhost:8765/  (Ordner $DST)"
