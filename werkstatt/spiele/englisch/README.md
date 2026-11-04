# Englisch-Spiele im Klassenkiste-Look

Die Englisch-Spiele liegen in Supabase (Tabelle `games`). Die Lehrerin lädt sie in der Verwaltung mit «Spielpaket herunterladen → Englisch» herunter.

- `kk-look.html`: Stil- und Bewegungs-Schicht (weiche Farben, Goldakzente, Funken bei richtigen Antworten). Wird vor dem letzten `</body>` des Spiels eingefügt; der Spielablauf und die Spielstände bleiben unverändert.
- `kk-uhr.html`: macht alle kleinen Uhren im Spiel «Zeit & Uhr» so schön wie die Uhr zum Einstellen (Goldrand, Zahlen, farbige Zeiger); wird nach `kk-look.html` eingefügt.
- `logo-zeit-und-uhr.png`: Logo (Wecker) für «Zeit & Uhr», im Spiel als data:-Bild neben dem Titel.
- `spielpaket-zeit-und-uhr.json`: fertiges Paket zum Importieren (Verwaltung → «Spielpaket importieren» mit «ersetzen»).
