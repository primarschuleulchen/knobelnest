# Knobelnest – Einrichtung (Testphase)

Adresse nach der Einrichtung: https://primarschuleulchen.github.io/knobelnest/
Kinder: https://primarschuleulchen.github.io/knobelnest/#/klasse

## 1. Datenbank einrichten (Supabase, einmalig)

1. Supabase öffnen → Projekt «Knobelnest» → links **SQL Editor** → **New query**.
2. Den ganzen Inhalt von `supabase/schema.sql` einfügen → unten rechts **Run**.
   Erwartet: «Success. No rows returned».

## 2. Dein eigenes Konto anlegen (du wirst automatisch Admin)

1. Links **Authentication** → **Users** → **Add user** → **Create new user**.
2. Deine E-Mail und ein Passwort eingeben, **Auto Confirm User** anhaken → **Create user**.
   Das erste Konto wird automatisch Administratorin bzw. Administrator.

Lehrpersonen fügst du genau gleich hinzu und gibst ihnen ihr Startpasswort.
Sie können es danach im Portal oben rechts unter ihrem Namen ändern.

## 3. Webseite veröffentlichen (GitHub Pages)

1. Auf github.com oben rechts **+** → **New repository**.
   Name: `knobelnest`, **Public**, dann **Create repository**.
2. Auf der leeren Seite auf **uploading an existing file** klicken.
3. Alle Dateien aus diesem Ordner hineinziehen (auch den Ordner `supabase`) → **Commit changes**.
4. Im Repository **Settings** → links **Pages** → bei «Branch» **main** und **/ (root)** wählen → **Save**.
5. Nach 1–2 Minuten ist die Seite unter der Adresse oben erreichbar.

## 4. Optional, für später

Supabase → **Authentication** → **URL Configuration** → **Site URL** auf
`https://primarschuleulchen.github.io/knobelnest/` setzen.

## Dateien

- `index.html`, `style.css`, `app.js` – die Webseite
- `config.js` – Name des Portals und Verbindung zur Datenbank
- `db.js` – alles, was mit der Datenbank spricht (beim Umzug zu Infomaniak wird nur diese Datei ersetzt)
- `supabase/schema.sql` – Datenbank-Einrichtung

## Fortschritt aus eigenen Spielen melden

Ein Spiel kann im eigenen Code aufrufen:

```js
knobelnest.answer(true);      // eine Aufgabe richtig (false = falsch)
knobelnest.progress(7, 20);   // 7 von 20 geschafft
```

Spiele aus dem Spielheft melden richtige und falsche Antworten automatisch.
