# Knobelnest – Arbeitsanleitung für Claude

Knobelnest ist das Schulportal von Frau Kressebuch (Primarschule, Schweiz). Lehrpersonen melden sich an, schalten Lernspiele frei und nutzen Klassenwerkzeuge. Kinder melden sich mit Klassencode, Namen und Bildpasswort an.

- Seite: https://primarschuleulchen.github.io/knobelnest/ (GitHub Pages, Branch `main`, Hauptordner)
- Kinder: `…/knobelnest/#/klasse`
- Datenbank: Supabase (Projekt «Knobelnest»)

## Mit wem du arbeitest

- **Wer:** Die Benutzerin ist Lehrerin und Admin des Portals, keine Programmiererin. Sie arbeitet oft am Handy, manchmal am Laptop, und schickt Screenshots.
- **Antworten:** immer Deutsch in Schweizer Schreibweise («ss» statt «ß», Anführungszeichen «…»). Kurz und ohne Fachjargon. Sag ihr, was sie tun muss, z. B. «in Supabase das SQL ausführen».
- **Oberflächentexte:** ebenfalls Deutsch in Schweizer Schreibweise und kindgerecht, wo Kinder sie sehen.
- **Ablauf:** Mach Änderungen direkt, teste sie und speichere sie mit einem Commit. Frag nur bei echten Unklarheiten.
- **Grenzen:** Ändere nur das, worum sie bittet. Die eigenständige Klassen-Pinnwand (ausserhalb des Knobelnests) baust du nur auf ausdrücklichen Wunsch (`werkstatt/einbau/pinnwand/standalone.py`).

## Sicherheitsregeln (immer)

- **Schlüssel:** Frag nie nach dem geheimen Supabase-Schlüssel (`sb_secret_…` / service_role) oder dem Datenbank-Passwort. Nimm sie nie an und verwende sie nie. Im Code steht nur der öffentliche «Publishable key» in `config.js`.
- **Öffentliches Repository:** Keine Kindernamen, Notizen zu Kindern oder Klassenlisten in Dateien. Das gilt auch für Testdaten und Importdateien. Nimm für Tests erfundene Namen wie Lena, David, Mia oder Noah.
- **Datenzugriff:** Kinder kommen nur über `security definer`-Funktionen mit Token an Daten (`public._kid(p_token)`), nie direkt an Tabellen. Neue Kinderfunktionen bekommen dieselben Prüfungen: nur die eigene Klasse, Grössen- und Typgrenzen, nur erlaubte Felder.

## Aufbau

| Datei | Inhalt |
|---|---|
| `index.html` | Lädt `style.css`, `config.js`, `db.js`, `app.js` mit `?v=N` (Cache-Bremse) |
| `config.js` | Portalname und Supabase-Adresse mit dem öffentlichen Schlüssel |
| `db.js` | Alle Aufrufe an Supabase (Tabellen und RPC-Funktionen) als `DB.xyz()` |
| `app.js` | Die ganze Portal-App (Hash-Routen in `route()`) |
| `style.css` | Gestaltung des Portals |
| `tagesfolie.html`, `hausaufgaben.html`, `pinnwand.html`, `otterteich.html`, `atelier.html` | Eingebettete Werkzeuge (eigene Seiten im iframe) |
| `atelier-*.png/webp` | Bilder für das Atelier |
| `zeitreise/` | Zeitreise (Geschichte), gebaut mit `werkstatt/einbau/zeitreise/build_zeitreise.py` |
| `vokabelkiste/` | Vokabelkiste, gebaut mit `werkstatt/einbau/vokabelkiste/vk_patch.py` (läuft als Spiel, siehe «Spiele») |
| `supabase/schema.sql` | Die ganze Datenbank-Einrichtung (Version 19) |
| `werkstatt/` | Originale, Einbau-Skripte und Tests (siehe unten). Wird nicht vom Portal geladen. |

Module in `app.js` (jeweils `var X = {…}`):

- `T`: Lehrpersonen-Portal und Verwaltung, inkl. Spiele hochladen und «Spielpaket importieren»
- `K`: Kinderansicht
- `W`: Arbeitsstand-Tafel (Wandtafel)
- `S`: Klassen-Sprint
- `F`: Tagesfolie
- `H`: Hausaufgabenheft
- `P`: Pinnwand
- `AT`: Atelier
- `O`: Otterteich
- `ACT`: Klick-Aktionen (`data-a="…"`)

### Eingebettete Werkzeuge

Jedes Werkzeug ist ursprünglich eine eigenständige HTML-Datei der Lehrerin. Sie hat diese Dateien meist mit Claude als Artifact gebaut, oft mit `window.claude.use('db')`.

So läuft ein Werkzeug im Portal:

- Das Portal öffnet es als `<div class="folie"><iframe src="werkzeug.html?v=…">`.
- Vorher stellt das Portal ein Brückenobjekt bereit, das die Seite über `window.parent` findet:

| Werkzeug | Brücke | Speicher (`teacher_store`, Dokument) | Kinder-Funktionen |
|---|---|---|---|
| Tagesfolie | `window.knTagesfolie` (inkl. `claude.use`-Nachbau) | eigene Dokumente der Tagesfolie; Vorlage in `shared_store` «tagesfolie-vorlage» | – |
| Hausaufgabenheft | `window.knHeft` | `hat-<Klasse>` | `kid_heft`, `kid_heft_tick`, `kid_heft_own` |
| Pinnwand | `window.knPin` (`pinBridge` baut die `claude.use('db')`-Sammlungen nach) | `pin-<Klasse>` | `kid_pin`, `kid_pin_idea`, `kid_pin_vote`; Lehrperson schreibt mit `pin_put` |
| Otterteich | `window.knOtter` (`otterBridge`) | `otter-<Klasse>` (Einstellungen und `run` = Stand des Teichs) | – |
| Atelier | `window.knAtelier` | `atelier-<Klasse>` = `{open, arten, kids:{id:{thema,umsetzung,stufe,farbe,x,y}}}` | `kid_atelier`, `kid_atelier_set`; Lehrperson schreibt mit `atelier_put` |

- **Otterteich in der Tagesfolie:** Die Tagesfolie zeigt den Otterteich als Baustein. Dafür liegt das Fenster `otterteich.html?embed` dauerhaft über dem Baustein, damit Mikrofon und Otter weiterlaufen. Es findet `knOtter` über `window.parent.parent`.
- **Werkzeuge freigeben:** Der Admin gibt Werkzeuge pro Lehrperson frei. Die Freigaben stehen in `shared_store` «werkzeuge» = `{Lehrperson-ID: {folie, heft, pin, otter, atelier: true}}`. Die Liste dazu ist `TOOLS` in `app.js`, die Prüfung `toolGate()`. Für Admins ist immer alles frei.
- **Neues Werkzeug:**
  - eine Zeile in `TOOLS`
  - eine Route in `route()`
  - ein Start-Modul mit `toolGate`
  - ein Knopf im Klassen-Banner (`T.tools.x`)
  - eventuell eine Kachel in der Kinderansicht (`.tile-pair`, zwei Spalten)

### Spiele

- **Speicherort:** Die Spiele liegen in Supabase (Tabelle `games`). Sie werden in der Verwaltung als HTML oder als «Spielpaket» (JSON) hochgeladen, nicht über GitHub.
- **Spielstand und Fortschritt:** Ein Spiel meldet beides per `postMessage` (`{spielheft|knobelnest: 1, type: …}`). Das Portal speichert sie mit `kid_report` / `kid_save` / `kid_state` (siehe `ACT.kPlay`).
- **Wenn die Lehrerin ein Spiel verbessert haben will:**
  - Du bearbeitest ihre HTML-Datei.
  - Sie lädt die neue Datei in der Verwaltung wieder hoch: beim Spiel unter «Spiel-Datei» oder als Paket mit «Vorhandene Spiele mit gleichem Titel durch die neue Version ersetzen».
  - Achte darauf, dass gespeicherte Spielstände der Kinder kompatibel bleiben.
- **Vokabelkiste:** ist ein Spiel in der Tabelle `games`, dessen Spiel-Datei die Vokabelkiste aus claude.ai ist (erkannt an `id="vk-content"`). Das Portal öffnet dann `vokabelkiste/index.html` (`gameUrl()`).
  - Wortlisten und Freigaben pro Klasse: `game_settings.settings.content` (Lehrperson: Knopf «📚 Wörter & Freigaben», `ACT.vkOpen`). Ohne Eintrag gelten die Listen aus `werkstatt/originale/vokabelkiste.html`.
  - Fortschritt des Kindes: `progress.save.p` (Karteikasten, Knacknüsse, `days` = Übungen pro Tag). Antworten zählen pro Sprache als Level.

## Datenbank (Supabase)

- **Eine Datei:** `supabase/schema.sql` ist die ganze Einrichtung. Sie darf mehrmals ausgeführt werden, deshalb überall `create … if not exists` und `create or replace`.
- **Ausführen kann nur die Lehrerin.** Sie fügt die ganze Datei in Supabase ein: «SQL Editor» → «New query» → «Run». Du hast keinen Zugang zur Datenbank.
- **Bei jeder SQL-Änderung:**
  1. Versionsnummer oben in der Datei erhöhen (zurzeit 19).
  2. Einen kommentierten Abschnitt «Version N» ergänzen.
  3. Rechte vergeben: Kinderfunktionen `anon, authenticated`, Lehrpersonen-Funktionen nur `authenticated`.
  4. Der Lehrerin klar sagen, dass sie das SQL ausführen muss, bevor sie die neuen Dateien braucht.
- **Speicher der Lehrpersonen:** `teacher_store(teacher_id, doc, data jsonb)` ist der Speicher pro Lehrperson und Dokument (RLS: nur die eigene Lehrperson).
- **Gemeinsamer Speicher:** `shared_store(doc, data)` schreibt nur der Admin, lesen dürfen alle Lehrpersonen.
- **Abfragen für die Lehrerin:** Nur lesende Abfragen, die sie selbst ausführen kann, gehören nach `werkstatt/sql/`.

## Cache-Bremse (wichtig, sonst sehen Geräte alte Dateien)

- **`index.html`:** `?v=N` bei allen vier Dateien um 1 erhöhen, sobald sich `app.js`, `db.js`, `style.css` oder `config.js` ändert (zurzeit `v=67`).
- **Werkzeug-Versionen in `app.js`:** `HEFT_VER`, `PIN_VER`, `OTTER_VER`, `ATELIER_VER`, `ZR_VER`, `VK_VER` und die Tagesfolie (`tagesfolie.html?v=' + ('37')`). Erhöhe die passende Version, wenn sich die Werkzeug-Seite ändert.

## Neue Version eines Werkzeugs einbauen

Die Lehrerin entwickelt ihre Werkzeuge oft in anderen Chats weiter und schickt dann die neue HTML-Datei. So baust du sie ein:

1. Die Datei als `werkstatt/originale/<werkzeug>.html` speichern (Namen siehe `werkstatt/einbau/alle_neu_bauen.py`).
2. `python3 werkstatt/einbau/alle_neu_bauen.py` ausführen.
   - Jedes Einbau-Skript ersetzt genau festgelegte Textstellen (`rep(alt, neu, anzahl)` mit Prüfung der Anzahl).
   - Wenn sich eine Stelle im Original geändert hat, bricht das Skript mit «Anzahl 0 statt 1: …» ab.
   - Dann diese Stelle im Skript an das neue Original anpassen.
   - Die Absicht jedes Abschnitts steht im Kommentar darüber.
3. Mit `--schreiben` die Dateien im Hauptordner ersetzen, testen, Version erhöhen.
4. Wenn die neue Version etwas ganz anders macht (z. B. Otterteich 16 war ein kompletter Umbau), lieber ein neues Einbau-Skript schreiben, statt das alte zu verbiegen.

Wenn die Lehrerin Änderungen direkt im Knobelnest will, ändere auch das Einbau-Skript (neuer Abschnitt), nicht nur die fertige Datei. Sonst geht die Änderung beim nächsten Einbau verloren. Prüfe danach mit `alle_neu_bauen.py`, dass Skript und Datei übereinstimmen («gleich»).

## Testen

- **Portal im Browser:**
  - `bash werkstatt/test/testseite.sh` baut nach `/tmp/kn-test` eine Kopie mit Schein-Datenbank (`werkstatt/test/mock-db.js`, alles im Speicher) und startet sie auf http://localhost:8765/.
  - Schein-Konten: `admin@x.ch` und `lp@x.ch`, Passwort `test1234`.
  - `__D` im Browser zeigt den Inhalt der Schein-Datenbank.
  - Mit Playwright testen, siehe `werkstatt/test/beispiel_test.py`, und Screenshots anschauen.
  - Für Mikrofon-Tests Chromium mit `--use-fake-ui-for-media-stream --use-fake-device-for-media-stream` starten. Der Schein-Ton ist laut und verscheucht die Otter, darum im Otterteich lieber den Testmodus «Ohne Mikrofon» mit Test-Lautstärke 0 nehmen.
- **Neue SQL-Funktion:** dieselbe Funktion in `mock-db.js` nachbauen, sonst läuft die Testseite nicht.
- **SQL:** `bash werkstatt/test/pg-test.sh` lädt `schema.sql` in ein lokales PostgreSQL mit nachgebauten Supabase-Teilen (`supabase-stub.sql`). Dort Funktionen mit `set role anon/authenticated` und `select set_config('request.jwt.claim.sub', '<id>', false)` prüfen.

## Veröffentlichen

Claude arbeitet in einer Cloud-Sitzung und darf nicht direkt auf `main` schreiben. Die Seite zeigt aber nur, was auf `main` liegt. Darum:

1. **Commit und Push:** Jede Sitzung hat einen eigenen Arbeitszweig (z. B. `claude/…`, steht in den Sitzungsangaben). Dort committen (kurze deutsche Commit-Nachricht) und pushen. Online ist damit noch nichts.
2. **Pull Request:** Wenn die Lehrerin sagt «online stellen» (oder Ähnliches), erstellt Claude einen Pull Request vom Arbeitszweig nach `main` und schickt ihr den Link.
3. **Zusammenführen:** Die Lehrerin öffnet den Link und tippt «Merge pull request» → «Confirm merge». Sagt sie ausdrücklich «führ es gleich zusammen», darf Claude den Pull Request selbst zusammenführen.
4. **Online:** GitHub Pages ist 1–2 Minuten nach dem Zusammenführen aktuell. Falls ein Gerät noch Altes zeigt: Seite neu laden (Cache-Bremse prüfen).

- **SQL zuerst:** Braucht die Änderung neues SQL, muss die Lehrerin es in Supabase ausführen, bevor sie zusammenführt.
- **Nach dem Zusammenführen:** Für weitere Änderungen den Arbeitszweig neu auf dem aktuellen `main` aufsetzen und einen neuen Pull Request machen (einen zusammengeführten nie weiterverwenden).
- **Nachricht an die Lehrerin:** kurz auf Deutsch, was sich geändert hat, ob ein SQL-Schritt nötig ist und worauf sie achten soll. Keine Dateilisten zum Hochladen, das ist ja erledigt.
