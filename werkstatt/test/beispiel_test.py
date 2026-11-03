# Beispiel-Test mit Playwright gegen die Testseite (zuerst: bash werkstatt/test/testseite.sh)
# Aufruf: python3 werkstatt/test/beispiel_test.py /tmp/kn-shots
# Zeigt den typischen Ablauf: Admin-Anmeldung, Klasse anlegen, Werkzeug öffnen, Kind anmelden.
import sys, os
from playwright.sync_api import sync_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/kn-shots'; os.makedirs(OUT, exist_ok=True)
errs = []
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--use-fake-ui-for-media-stream", "--use-fake-device-for-media-stream"])
    ctx = b.new_context(viewport={"width": 1440, "height": 900}, permissions=["microphone"])
    for u in ("https://fonts.googleapis.com/**", "https://fonts.gstatic.com/**"): ctx.route(u, lambda r: r.abort())
    p = ctx.new_page(); p.on("pageerror", lambda e: errs.append(str(e)))
    p.goto("http://localhost:8765/"); p.wait_for_selector("#lgMail")
    # Schein-Konten: admin@x.ch (Admin) und lp@x.ch (Lehrperson «Herr Muster»), Passwort test1234
    p.fill("#lgMail", "admin@x.ch"); p.fill("#lgPw", "test1234"); p.click("form[data-a=login] button.primary")
    p.wait_for_selector("#obName"); p.fill("#obName", "Frau Test"); p.click("text=Weiter")
    p.wait_for_selector("#cName"); p.fill("#cName", "5b"); p.click("form[data-a=createClass] button"); p.wait_for_selector("#kidBulk")
    p.fill("#kidBulk", "Lena\nDavid\nMia\nNoah"); p.click("form[data-a=addBulk] button"); p.wait_for_timeout(500)
    cid = p.evaluate("__D.classes.find(c=>c.name==='5b').id")      # __D = Inhalt der Schein-Datenbank
    # Ein Werkzeug öffnen (läuft als iframe in .folie)
    p.evaluate(f"location.hash='#/atelier/{cid}'"); p.wait_for_selector(".folie iframe"); p.wait_for_timeout(1500)
    f = p.frame_locator(".folie iframe")
    print("Kinder im Atelier:", f.locator(".kid .n").all_inner_texts())
    p.screenshot(path=f"{OUT}/atelier-lp.png")
    # Als Kind anmelden: Klassencode, Name, Bildpasswort
    code = p.evaluate(f"__D.classes.find(c=>c.id==='{cid}').code"); pwd = p.evaluate("__D.kids.find(k=>k.name==='Lena').pw")
    p.evaluate("location.hash='#/klasse'"); p.wait_for_selector("#kCode"); p.fill("#kCode", code); p.click("form[data-a=kCode] button")
    p.wait_for_selector(".kid-name"); p.click(".kid-name:has-text('Lena')")
    for s in pwd.split(","): p.click(f"[data-a=kSym][data-s={s}]")
    p.click("[data-a=kLogin]"); p.wait_for_timeout(1500)
    p.screenshot(path=f"{OUT}/kind-start.png")
    print("Fehler auf der Seite:", errs or "keine")
