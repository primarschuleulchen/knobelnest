# Knobelnest – Arbeitsanleitung für Claude

Knobelnest (sichtbarer Name: **«Klassenkiste»**, `C.PORTAL_NAME` in `config.js`) ist das Schulportal von Frau Kressebuch (Primarschule, Schweiz). Lehrpersonen melden sich an, schalten Lernspiele frei und nutzen Klassenwerkzeuge. Kinder melden sich mit Klassencode, Namen und Bildpasswort an.

- Klassencode: Die Lehrperson wählt ihn selbst (z. B. «Otter 123», `ACT.codeEdit`/`codeSave`, beim Anlegen freiwillig). Kinder müssen Gross/klein und Leerzeichen nicht beachten (`_norm_code`).
- Klasse (Version 20): `classes.bild` = Klassenbild/Maskottchen (data:image, `ACT.bildEdit`, Vorlagen der Admin-Lehrperson in `shared_store` «klassenbilder», Verwaltung `kbCard()`), `classes.kid_tools` = Werkzeuge für die Kinder freigegeben `{heft,pin,atelier,tafel}` (fehlt = frei, neue Klassen alles gesperrt; Knöpfe unter den Werkzeug-Kacheln, `ACT.toolRel`), `classes.tafel_cols` = eigene Namen der drei Tafel-Spalten (`setTafelCols()`). Kinder lesen das mit `kid_klasse`; `kid_class` gibt auch das Bild. `DB.listClasses` fällt ohne diese Spalten auf die alten zurück.
- Tafel-Spalten (Version 21): `classes.tafel_cols = {list:[{id,label,color}]}` (höchstens 6, `colList()`/`setTafelCols()`, Editor `colEditor()`); ohne `list` die drei Standardspalten. `tafel_set` prüft mit `_tafel_col_ok`. «helfen»/«frage» behalten ihre Sonderrolle (Hilfe-Hinweis).
- Lizenz (Version 22): `profiles.valid_until` = letzter gültiger Tag (leer = unbefristet, Admin nie gesperrt). Neue Konten bekommen per Trigger heute + 1 Jahr. Nur der Admin ändert es (`admin_set_valid`, Verwaltung `licRow()`, «+ 1 Jahr», «✉ Erinnerung schreiben»). Abgelaufen → `licPage()` statt Portal/Werkzeugen (`licExpired()` in `T.start`, `T.render`, `toolGate`, `licGate`); 30 Tage vorher Hinweis mit `C.SHOP_URL`. Kinder: `_lic_ok()` in `_kid`, `kid_class` (`pausiert`), `kid_login` → Hinweis «pausiert».
- Lehrperson: Reihenfolge der Werkzeug-Kacheln pro Lehrperson in `teacher_store` «kacheln» (`tileOrder()`; Kacheln direkt ziehen, Pointer-Events `tdStart`/`tdMove`, Finger nach 380 ms Halten). Tier-Vorlagen fürs Klassenbild in `bilder/maskottchen/` (`TIERE`).
- Lehrperson: Reiter «Übersicht» (`T.tab = 'uebersicht'`, Start und Klick aufs Logo) = Klassen-Banner mit Werkzeug-Kacheln; Reiter «Spiele» = Fächer und Spiele (beides `T.tabSpiele`). Kachel-Bilder in `bilder/kacheln/` (`KACHEL_BILD`, `ttIcon()`).
- Anmeldeseite: Werkzeug-Galerie mit Vorschau beim Darüberfahren (`LOGIN_TOOLS`), Knopf «Noch kein Login?» → `C.SHOP_URL` in `config.js` (leer = Hinweis «kommt bald»). Kreisbilder in `bilder/kacheln/` und `bilder/maskottchen/` sind rund zugeschnitten (durchsichtige Ecken), den Goldrand macht das CSS.
- Kinderansicht: `body.kidv` (in `K.render`), heller Stil wie die Lehrpersonen-Seite, Schriften Fredoka/Andika bleiben. Startseite ohne Kopfleiste, «Abmelden» neben der Begrüssung (`K.shell(body, null)`).
- Live-Quiz (Version 23): eigene Seite `quiz.html` (Bridge `window.knQuiz`, Modul `QZ` in `app.js`, `QUIZ_VER`). Lehrperson: Route `#/quiz`, Quiz in `teacher_store` «quiz» (Liste) und «quiz-<id>» (Fragen; Typen `quiz`, `rf`, `text`, `reihe`). Live-Runde: Tabellen `quiz_live`/`quiz_players`, Funktionen `quiz_open`/`quiz_step`/`quiz_host`/`quiz_kick`/`quiz_close` (Lehrperson) und `quiz_join`/`quiz_state`/`quiz_answer` (Mitspielen ohne Konto, Token). Mitspielen: `#/q/<6-stellige Nummer>` per QR-Code. Punkte rechnet die Datenbank (bis 1000 × Faktor, schneller = mehr). Runden verschwinden nach einem Tag. Freigabe pro Lehrperson wie die anderen Werkzeuge (`TOOLS` «quiz»).
- Quiz-Ordner und Kinder-Quiz (Version 25): Ordner der Lehrperson in `teacher_store` «quiz» = `{list:[{…, ordner}], ordner:[{id,name}]}`. Kinder erstellen eigene Quiz, wenn die Lehrperson es pro Klasse einschaltet (`classes.kid_tools.quiz === true`, fehlt = aus; Schalter im Ordner «Von den Kindern»). Tabelle `kid_quizzes` (`members` = Kinder, die es sehen und bearbeiten; `ver` für gemeinsames Bearbeiten). Kinder: `kid_quiz_list/get/save/delete` (Kachel «Quiz erstellen», `K.view_quiz`, `mode: 'kid'`). Lehrperson: `kq_list/get/save/new/members/delete`. Bei altem Stand gibt `…_save` `conflict` zurück, `quiz.html` führt mit `merge()` zusammen (geänderte Fragen gewinnen) und holt alle 4 s neue Stände (`kidPull`).
- Quiz mit KI (ohne eigenen KI-Zugang, kein SQL): «✨ Mit KI erstellen» in `quiz.html` (`kiOpen`, `kiAuftrag()`, `kiLesen()`). Die Lehrperson kopiert einen Auftrag, gibt ihn mit dem PDF in claude.ai ein und fügt die JSON-Antwort ein → neues Quiz bzw. «✨ Fragen mit KI» hängt Fragen im Editor an. Einstellungen in `localStorage` «kn_quiz_ki». Nur für Lehrpersonen.
- Quiz-Vorschau: «👁 Vorschau» auf jeder Quiz-Karte und im Editor (Kinder: «👁 Ausprobieren»). Durchklicken und prüfen ohne Klasse, nichts wird gespeichert (`vorStart()`, `vorRender()`, Zustand `V`). Karten: `.qc-main` (Live spielen + Vorschau), `.qc-fuss` (Bearbeiten, Kopie, Ordner, Papierkorb; Linien-Symbole `IC`). Ordnerfarbe `ordner[].farbe` (Auswahl `OFARBEN`, im Ordner «Farbe des Ordners», `ACT.oFarbe`); Karten im Ordner in heller Ordnerfarbe (`karteStil()`), ohne Ordner weiss. Kein bunter Balken.
- Umfrage (Version 26, wie Mentimeter): Modul `U` in `app.js`, Route `#/umfrage/<Klasse>`, Freigabe-Schlüssel `umfrage` in `TOOLS`. Umfragen der Lehrperson (für alle Klassen) in `teacher_store` «umfragen» = `{list:[{id,title,set:{mode,auto,kids,anon},qs}]}`; Live-Stand und Antworten pro Klasse in «umfrage-<Klasse>» = `{live, ans:{Frage:{Kind:Antwort}}}`. «live» schreibt nur die Lehrperson (`umfrage_put`, Timer über `sec`), Kinder lesen mit `kid_umfrage` (Lösung `ok` erst nach Aufdecken `rev`, Antworten anderer ohne Namen und nur bei `show`) und antworten mit `kid_umfrage_send` (Prüfung pro Fragetyp). Fragetypen `UMF_TYPES` (wahl, quiz, stimmung, wort, text, skala, rang, punkte, zahl, feld, info), Ergebnisse `umfRes()`, Eingabe der Kinder `umfInput()`, Vorlagen `UMF_VORLAGEN`. Kinder: Kachel «Umfrage!» (`K.umfOpen`, geprüft in `K.checkRace`), Ansicht `K.view_umfrage`.
- Umfrage offen per QR-Code (Version 27): Beim Starten «Wer macht mit?» → Klasse (`uStartK`) oder offen (`uGoO`). Offene Runde in Tabelle `umf_runden` (eine pro Lehrperson, 6-stellige Nummer `nr`, `data` = `{live, ans}`, nach 30 Tagen gelöscht) mit Gästen `umf_gaeste` (Token, freiwilliger Name, sonst «Gast N»). Lehrperson: `umf_offen_open/put/host/close`; Gäste: `umf_gast_join`, `umf_gast`, `umf_gast_send` (dieselben Regeln über `_umf_apply`, `_umf_view`, `_umf_val`). Im Portal `U.docs = {klasse, offen}`, umschalten mit `U.use()`. Mitmachen: Route `#/u/<Nummer>` (`G.start`, `K.view_gast`, Token in localStorage «kn_umf_gast», dann `K.umfBegin(token)`).
- Umfrage-Vorlagen: eingebaute `UMF_VORLAGEN` (IDs `b0`…), eigene in `teacher_store` «umfrage-vorlagen» = `{eigene:[{id,title,desc,emo,set,qs}], weg:[gelöschte IDs]}` («⭐ Als Vorlage», `ACT.uAsTpl`), für alle in `shared_store` «umfrage-vorlagen» = `{list:[…]}` (nur Admin, `ACT.uTplShare`). Löschen versteckt nur (`weg`), «Gelöschte Vorlagen» fügt wieder ein; eigene lassen sich dort endgültig löschen. Zusammengestellt in `umfTpls()`.
- Zurück-Knöpfe: überall gleich wie in der Eulenkiste (weisse Pille «←» + Eule, oben links). Im Portal `backBtn(attr, label)` + CSS `.kn-back` in `style.css`; in den eingebauten Werkzeugen setzt `werkstatt/einbau/zurueck.py` (aufgerufen von `alle_neu_bauen.py`) den Knopf `#knBack`; `quiz.html` und `gedaechtnis/` (in `bauen.py`) haben ihn direkt.
- Fächer-Bilder: `bilder/faecher/{deutsch,mathematik,englisch,nmg}.webp` (rund, Goldrand per CSS), Zuordnung über den Fachnamen in `fachBild()`; andere Fächer zeigen den Anfangsbuchstaben.
- Elterngespräche (Version 28, 29): Modul `E` (Lehrperson, `#/gespraeche/<Klasse>` = Liste aller gespeicherten Gespräche der Klasse `E.renderList()`, `#/gespraeche/<Klasse>/<Gespräch>` = planen `E.render()`, Kachel «eltern», Freigabe `eltern` in `TOOLS`) und `EP` (Eltern ohne Anmeldung, `#/eltern/<token>`). Tabelle `talks` (Version 29: Schlüssel `id`, mehrere pro Klasse; `cfg.kids` = Kinder, die sich anmelden sollen, fehlt = alle, `E.inKids()`; `cfg` = Termine/Schwierigkeit `diff`/Fixierungen `fixed`, `answers` pro Kind). Eltern nur über `eltern_get`/`eltern_set` (Schlüssel pro Gerät in `localStorage`; pro Gerät nur ein Kind), Lehrperson trägt mit `talk_answer_put(p_talk, …)` ein. Im Plan zeigt ein Klick auf die Zeit, wer sie angekreuzt hat (`E.open`). Plan: `egPlan()` (grösste Zuteilung + Tauschen gegen anspruchsvolle Gespräche hintereinander); `egReserved()` = Termine, ohne die nicht alle Eingetragenen Platz hätten → für neue Eltern ausgeblendet.
- Noch nicht freigeschaltete Werkzeuge: Lehrpersonen (nicht Admin) sehen sie grau unter «Noch mehr in der Klassenkiste» mit «👁 Vorschau» (Fenster mit Bild aus `bilder/vorschau/<Schlüssel>.webp` und Stichworten) und «✦ Hol es dir» (`C.SHOP_URL`, sonst `shopSoon`). Liste und Texte in `MEHR` (`mehrTiles()`, `ACT.ttVorschau`); das Atelier ist bewusst nicht dabei. Der Admin sieht den Bereich nur über den Knopf «👁 So sehen Lehrpersonen …» (`T.mehrAdmin`). Vorschau-Bilder nur mit erfundenen Namen.
- Seite: https://primarschuleulchen.github.io/knobelnest/ (GitHub Pages, Branch `main`, Hauptordner)
- Kinder: `…/knobelnest/#/klasse`
- Datenbank: Supabase (Projekt «Knobelnest»)

## Mit wem du arbeitest

- **Wer:** Die Benutzerin ist Lehrerin und Admin des Portals, keine Programmiererin. Sie arbeitet oft am Handy, manchmal am Laptop, und schickt Screenshots.
- **Antworten:** immer Deutsch in Schweizer Schreibweise («ss» statt «ß», Anführungszeichen «…»). Kurz und ohne Fachjargon. Sag ihr, was sie tun muss, z. B. «in Supabase das SQL ausführen».
- **Name:** In allen sichtbaren Texten heisst das Portal «Klassenkiste» (z. B. «← Klassenkiste», «in der Klassenkiste gespeichert»). Repository, Adresse und Code-Namen bleiben «knobelnest».
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
| `style.css` | Gestaltung des Portals. Lehrpersonen-Seiten (`body.lp`, gesetzt in `T.render`/`T.renderLogin`, entfernt in `route()`) im Stil der Eulenkiste (Repo `lernkompass`): Schrift Patrick Hand (`schriften/`), Eulen-Marke (`bilder/eule.webp`), Gold-Akzente, ✦ ✧ ✦. Die Kinderansicht ist noch im alten Stil. |
| `bilder/`, `schriften/` | Bilder und Schriften aus der Eulenkiste (lokal, nichts von Google) |
| `tagesfolie.html`, `hausaufgaben.html`, `pinnwand.html`, `otterteich.html`, `atelier.html`, `quiz.html` | Eingebettete Werkzeuge (eigene Seiten im iframe) |
| `atelier-*.png/webp` | Bilder für das Atelier |
| `gedaechtnis/` | Gedächtniskiste (Werkzeug und 12 Spiele), gebaut mit `werkstatt/spiele/gedaechtnis/bauen.py` |
| `englisch/` | Englisch-Spiel «Owl Town» (3D-Stadt), gebaut mit `werkstatt/spiele/englisch/bauen.py` |
| `zeitreise/` | Zeitreise (Geschichte), gebaut mit `werkstatt/einbau/zeitreise/build_zeitreise.py` |
| `vokabelkiste/` | Vokabelkiste, gebaut mit `werkstatt/einbau/vokabelkiste/vk_patch.py` (läuft als Spiel, siehe «Spiele») |
| `supabase/schema.sql` | Die ganze Datenbank-Einrichtung (Version 29) |
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
- `QZ`: Live-Quiz
- `U`: Umfrage
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
| Pinnwand | `window.knPin` (`pinBridge` baut die `claude.use('db')`-Sammlungen nach) | `pin-<Klasse>` | `kid_pin`, `kid_pin_post` (Version 24: Kategorie, Bild, direkt), `kid_pin_vote`; Lehrperson schreibt mit `pin_put` |
| Otterteich | `window.knOtter` (`otterBridge`) | `otter-<Klasse>` (Einstellungen und `run` = Stand des Teichs) | – |
| Umfrage | – (direkt im Portal, Modul `U`) | «umfragen», `umfrage-<Klasse>` | `kid_umfrage`, `kid_umfrage_send`; Lehrperson schreibt mit `umfrage_put` |
| Atelier | `window.knAtelier` | `atelier-<Klasse>` = `{open, arten, kids:{id:{thema,umsetzung,stufe,farbe,x,y}}}` | `kid_atelier`, `kid_atelier_set`; Lehrperson schreibt mit `atelier_put` |
| Live-Quiz | `window.knQuiz` (`mode` teacher/player) | `quiz`, `quiz-<id>` (nicht pro Klasse) | `quiz_join`, `quiz_state`, `quiz_answer` (ohne Kinder-Anmeldung); eigene Quiz: `kid_quiz_list/get/save/delete` |

- **Otterteich in der Tagesfolie:** Die Tagesfolie zeigt den Otterteich als Baustein. Dafür liegt das Fenster `otterteich.html?embed` dauerhaft über dem Baustein, damit Mikrofon und Otter weiterlaufen. Es findet `knOtter` über `window.parent.parent`.
- **Werkzeuge freigeben:** Tagesfolie, Pinnwand und Lautstärkeregler (Otterteich) hat jede Lehrperson (`BASE_TOOLS`). Die übrigen gibt der Admin pro Lehrperson frei: `shared_store` «werkzeuge» = `{Lehrperson-ID: {heft, tafel, vk, atelier, quiz, gd, umfrage: true}}`, Liste `TOOLS` in `app.js`, Prüfung `toolGate()`/`toolAccess()`. Ohne `tafel` keine Arbeitsstand-Kachel, kein Reiter, keine Wandtafel; ohne `vk` keine Vokabelkiste-Kachel (beim Freigeben wird das Spiel Vokabelkiste mit zugeteilt). Für Admins ist immer alles frei.
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
- **Gedächtniskiste:** Fach «Gedächtnis», 12 Spiele mit je 5 Stufen (Bereiche Bilder, Orte, Reihenfolgen, Namen merken), Stil der Eulenkiste. Alles gebaut mit `python3 werkstatt/spiele/gedaechtnis/bauen.py` → `gedaechtnis/<spiel>.html` (Spiele), `gedaechtnis/index.html` (Werkzeug für Lehrpersonen: Vorschau, Ausprobieren mit `?vorschau&stufe=N`, Freigeben, Admin «Spiele in die Klassenkiste aufnehmen» = `knGd.install`). In `games` steht pro Spiel nur ein Verweis (`knobelnest-url`), Änderungen kommen also über GitHub (dann `GD_VER` erhöhen). Sterne-Level «Stufe 1» … «Stufe 5», Spielstand-Eintrag `gd`. Werkzeug-Freigabe `gd` in `TOOLS`, Route `#/gedaechtnis/<Klasse>`, Modul `GD`.
- **Knobelspiele:** 12 Spiele mit je 5 Stufen (Kleiderschrank 6): Mathematik (Rechen-Rakete, Wie spät ist es?, Kiosk mit Franken/Rappen), Deutsch (Wort-Raten, Der die das, Silben-Puzzle), Fach «Knobeln» (Bilderrätsel = Nonogramm, Eulen-Weg = Programmieren, Bilder-Sudoku, Wasser-Weg). Die zweite Lieferung steht in `werkstatt/spiele/knobelspiele/weitere.py`. Englisch: «Im Museum» (Bildbeschreibung nach den Arbeitsblättern «describing pictures»: Bild finden, Sätze bauen, nach Beschreibung malen, Profi nur anhören mit englischer Gerätestimme) in `werkstatt/spiele/knobelspiele/museum.py`. Gebaut mit `python3 werkstatt/spiele/knobelspiele/bauen.py` → `knobelspiele/<spiel>.html` und `knobelspiele/knobelspiele-spielpaket.json` (Import in der Verwaltung). Rahmen und Stil kommen aus `werkstatt/spiele/gedaechtnis/bauen.py`, Spielstand-Eintrag `ks`. In `games` steht nur ein Verweis (`knobelnest-url`), Änderungen über GitHub, dann `KS_VER` erhöhen. Bilder fürs Bilderrätsel in `werkstatt/spiele/knobelspiele/bilder.py` (das Skript prüft, dass jedes ohne Raten lösbar ist). Keine fremden Spielnamen (z. B. «Wordle», «Picross») verwenden.
- **Kleiderschrank (Englisch):** Knobelspiel mit 6 Stufen (Entdecken im Schrank, Auswählen, Schreiben, Sprechen, my/your/his/her/our/their mit Mia und Noah, Sätze «This is my … / These are my …»). Alles in `werkstatt/spiele/knobelspiele/kleider.py` (SVG-Zeichnungen `ART`, Plätze im Schrank `PLATZ`, Wörter `WORT`), gebaut von `bauen.py`. Vorlesen mit der Sprachausgabe des Geräts (en-GB). Sprechen: Spracherkennung des Browsers (`SpeechRecognition`, der Ton geht an Google bzw. Apple), sonst aufnehmen, anhören und selber vergleichen. Im Portal bekommt nur dieses Spiel Mikrofon und `allow-same-origin` (`openPlayer`).
- **Owl Town (Englisch):** 3D-Stadt mit three.js (von jsdelivr, wie die Zeitreise), Fach «Englisch», 6 Stufen: Places (Orte finden), Jobs (Wo arbeitet …?), Short routes, Long routes (Brücke, «walk past»), Roundabout (Kreisel, «take the second exit»), Listening (nur vorgelesen, `speechSynthesis` en-GB) und «Free walk» ohne Sterne (`G.extra`). Die Eule läuft mit Pfeiltasten/Knöpfen von Haltepunkt zu Haltepunkt (`owlCmd`, hält an jeder Kreuzung), Ziel markieren mit 📍/Leertaste (`askMark`). Stadtplan, Orte (`PLACES`, `NAMED`), Berufe (`JOBS`), Wege erfinden (`genRoute`) und Fehlererklärung (`explain`: erste Abweichung vom richtigen Weg, roter/blauer Weg) in `werkstatt/spiele/englisch/owl-town.js` und `.css`. Gebaut mit `python3 werkstatt/spiele/englisch/bauen.py` → `englisch/owl-town.html` und `englisch/englisch-spielpaket.json` (Import in der Verwaltung). Rahmen aus der Gedächtniskiste, Spielstand-Eintrag `en`. In `games` nur ein Verweis (`knobelnest-url`), Änderungen über GitHub, dann `EN_VER` erhöhen.
- **Vokabelkiste:** ist ein Spiel in der Tabelle `games`, dessen Spiel-Datei die Vokabelkiste aus claude.ai ist (erkannt an `id="vk-content"`). Das Portal öffnet dann `vokabelkiste/index.html` (`gameUrl()`).
  - Wortlisten und Freigaben pro Klasse: `game_settings.settings.content` (Lehrperson: Knopf «📚 Wörter & Freigaben», `ACT.vkOpen`). Ohne Eintrag gelten die Listen aus `werkstatt/originale/vokabelkiste.html`.
  - Fortschritt des Kindes: `progress.save.p` (Karteikasten, Knacknüsse, `days` = Übungen pro Tag). Antworten zählen pro Sprache als Level.
  - Kinderansicht: Ein Fach, das nur aus der Vokabelkiste besteht, wird eine Kachel mit Kisten-Symbol, die das Spiel direkt öffnet und unter «Mathematik» steht (`vkPlace()`).
  - Lehrperson: Die Vokabelkiste ist im Spiele-Tab eine Kachel bei den Werkzeugen (nicht in der Spieleliste). «Wörter & Freigaben» bekommt `settings.kids` (Stand aller Kinder via `DB.listProgressSaves`) und `settings.frei`. In der Vokabelkiste: «📊 Klasse» (Übersicht pro Kind, pro Portion, pro Kind im Detail). Aufgezeichnet wird in `P.log[Portion][Übung] = {n,a,c,s,t}` und `P.wc[Wort] = [richtig, falsch]`.
  - Vorlagen: Die Admin-Lehrperson markiert Portionen/Ordner mit «📤 Als Vorlage freigeben» (`n.tpl`). Beim Speichern schreibt das Portal `shared_store` «vokabelkiste-vorlage» (`vkTemplate()`, nur aus der Klasse `from`). Die Admin-Lehrperson teilt die Vorlage-Portionen in der Verwaltung einzelnen Lehrpersonen zu (`shared_store` «vokabelkiste-zuweisung» = `{Lehrperson-ID: [Portion-IDs]}`, `vzRow()`, im Portal gefiltert mit `vkOnly()`). Lehrpersonen bekommen neu zugeteilte Portionen beim Öffnen als Kopie (für Kinder gesperrt, `mergeTpl()`, gemerkt in `content.tplSeen`). Sobald es eine Vorlage gibt, starten Klassen anderer Lehrpersonen ohne eigene Listen leer (nur Zugeteiltes, `settings.tplOn`).
  - Sterne: `starCfg()` gibt für die Vokabelkiste `eigene` zurück. Tagesstern = 7 Minuten echte Übungszeit (`P.sec`, zählt nur bei laufender Übung und Eingabe in den letzten 30 s). Serie 🔥 = Schultage hintereinander; Wochenende und Tage mit «Ferien»/«schulfrei» im Hausaufgabenheft (`vkFree()`) zählen nicht. Wochenheld 🏅, Kistenprofi 📦 (100 Wörter im letzten Fach). Die Übersicht zeigt Minuten pro Schultag (`vkHTML()`).

## Datenbank (Supabase)

- **Eine Datei:** `supabase/schema.sql` ist die ganze Einrichtung. Sie darf mehrmals ausgeführt werden, deshalb überall `create … if not exists` und `create or replace`.
- **Ausführen kann nur die Lehrerin.** Sie fügt die ganze Datei in Supabase ein: «SQL Editor» → «New query» → «Run». Du hast keinen Zugang zur Datenbank.
- **Bei jeder SQL-Änderung:**
  1. Versionsnummer oben in der Datei erhöhen (zurzeit 29).
  2. Einen kommentierten Abschnitt «Version N» ergänzen.
  3. Rechte vergeben: Kinderfunktionen `anon, authenticated`, Lehrpersonen-Funktionen nur `authenticated`.
  4. Der Lehrerin klar sagen, dass sie das SQL ausführen muss, bevor sie die neuen Dateien braucht.
- **Speicher der Lehrpersonen:** `teacher_store(teacher_id, doc, data jsonb)` ist der Speicher pro Lehrperson und Dokument (RLS: nur die eigene Lehrperson).
- **Gemeinsamer Speicher:** `shared_store(doc, data)` schreibt nur der Admin, lesen dürfen alle Lehrpersonen.
- **Abfragen für die Lehrerin:** Nur lesende Abfragen, die sie selbst ausführen kann, gehören nach `werkstatt/sql/`.

## Cache-Bremse (wichtig, sonst sehen Geräte alte Dateien)

- **`index.html`:** `?v=N` bei allen vier Dateien um 1 erhöhen, sobald sich `app.js`, `db.js`, `style.css` oder `config.js` ändert (zurzeit `v=112`).
- **Werkzeug-Versionen in `app.js`:** `HEFT_VER`, `PIN_VER`, `OTTER_VER`, `ATELIER_VER`, `QUIZ_VER`, `ZR_VER`, `VK_VER`, `GD_VER`, `KS_VER`, `EN_VER` und die Tagesfolie (`tagesfolie.html?v=' + ('39')`). Erhöhe die passende Version, wenn sich die Werkzeug-Seite ändert.

## Neue Version eines Werkzeugs einbauen

- **Klassenkiste und Eulenkiste zusammen:** Die Lehrerin will, dass Änderungen an einem Werkzeug, das es in beiden gibt (Tagesfolie, Glücksrad, Lautstärkeregler, Pinnwand), immer in beiden gemacht werden. Die Eulenkiste ist das Repo `primarschuleulchen/lernkompass` (ohne Daten, eigenes `werkstatt/bauen.py`); dort direkt online stellen. Pinnwand: Original `werkstatt/originale/klassen-pinnwand.html` (Version 6), Einbau `werkstatt/einbau/pinnwand/pin6_patch.py`, gemeinsame Korrekturen in `pin_fixes.py` (dieselben Abschnitte stehen in der Eulenkiste).

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
2. **Pull Request:** Nach dem Testen erstellt Claude einen Pull Request vom Arbeitszweig nach `main` – immer, auch ohne dass die Lehrerin «online stellen» sagt.
3. **Zusammenführen:** Die Lehrerin will, dass Claude Änderungen **immer direkt selbst online stellt**: Pull Request gleich selbst zusammenführen, ohne nachzufragen (vorher mit dem neusten `main` zusammenführen und testen). Ausnahme: Braucht die Änderung neues SQL, zuerst die Lehrerin das SQL ausführen lassen und erst zusammenführen, wenn es gelaufen ist (prüfen, ob die neue Funktion antwortet).
4. **Online:** GitHub Pages ist 1–2 Minuten nach dem Zusammenführen aktuell. Falls ein Gerät noch Altes zeigt: Seite neu laden (Cache-Bremse prüfen).

- **SQL zuerst:** Braucht die Änderung neues SQL, muss die Lehrerin es in Supabase ausführen, bevor sie zusammenführt.
- **Nach dem Zusammenführen:** Für weitere Änderungen den Arbeitszweig neu auf dem aktuellen `main` aufsetzen und einen neuen Pull Request machen (einen zusammengeführten nie weiterverwenden).
- **Nachricht an die Lehrerin:** kurz auf Deutsch, was sich geändert hat, ob ein SQL-Schritt nötig ist und worauf sie achten soll. Keine Dateilisten zum Hochladen, das ist ja erledigt.
