# Korrekturen an der Klassen-Pinnwand. Werden von pin6_patch.py (Klassenkiste) ausgeführt;
# dieselben Abschnitte stehen in der Eulenkiste (Repo lernkompass, werkstatt/bauen.py). Bei Änderungen beide anpassen.

# a) Beim Tippen auf eine Einstellung springt die Seite nicht mehr nach oben:
#    vor dem Neuzeichnen die Scroll-Positionen (Seite und Seitenleiste) merken und danach wiederherstellen.
rep('''  $("#app").innerHTML = !S.board ?''', '''  const scrSame = window.__pwScr === S.board + "|" + S.view; window.__pwScr = S.board + "|" + S.view;
  const scrPath = el => { const p = []; while (el && el.id !== "app") { p.unshift([...el.parentNode.children].indexOf(el)); el = el.parentNode; } return p; };
  const scrKeep = [], scrY = scrollY; if (scrSame) document.querySelectorAll("#app *").forEach(el => { if (el.scrollTop > 0) scrKeep.push([scrPath(el), el.scrollTop]); });
  $("#app").innerHTML = !S.board ?''')
rep('''  for (const k in keep) { const el = document.getElementById(k); if (el) el.value = keep[k]; }''', '''  for (const k in keep) { const el = document.getElementById(k); if (el) el.value = keep[k]; }
  if (scrSame) {
    for (const [p, t] of scrKeep) { let el = $("#app"); for (const i of p) el = el && el.children[i]; if (el) el.scrollTop = t; }
    if (Math.abs(scrollY - scrY) > 1) scrollTo(0, scrY);
  }''')

# b) Grössere Schrift auf den Zetteln
rep('.note .txt{font-family:var(--hand);font-size:1.5rem;', '.note .txt{font-family:var(--hand);font-size:1.9rem;')
rep('#app[data-font="klar"] .note .txt{font-size:1.2rem}', '#app[data-font="klar"] .note .txt{font-size:1.55rem}')
rep('.present-on .note .txt{font-size:2rem}', '.present-on .note .txt{font-size:2.5rem}')
