# 30) Lautstärke-Baustein: Leiste «Lautstärke» verschwindet wieder von selbst (auch am Smartboard/Beamer, wo kein
#     «Maus weg» gemeldet wird), und wird der Baustein entfernt (auf keinem Bildschirm mehr ein Lautstärke-Baustein),
#     schliesst sich das Otter-Fenster ganz, damit Musik und Mikrofon aufhören.
rep('''    if (!ph) { if (last !== "off") { layer.classList.remove("on"); last = "off"; } return; }''',
    '''    if (!ph) {
      if (last !== "off") { layer.classList.remove("on"); last = "off"; }
      // Kein Lautstärke-Baustein mehr in der ganzen Tagesfolie: Fenster schliessen (stoppt Musik und Mikrofon)
      if (frame && !S.screens.some(s => (s.widgets || []).some(w => w.type === "otter"))) { frame.remove(); frame = null; }
      return;
    }''')
rep('''  const vor = () => { clearTimeout(t); const el = w(); if (!el) return; el.classList.add("hov");''',
    '''  // Leiste nach 2.5 s wieder ausblenden, ausser die Maus ist gerade auf der Leiste selbst
  const weg = () => { clearTimeout(t); t = setTimeout(() => { const x = w(); if (!x) return; if (x.querySelector(".chrome:hover")) return weg(); x.classList.remove("hov"); }, 2500); };
  const vor = () => { clearTimeout(t); const el = w(); if (!el) return; el.classList.add("hov"); weg();''')
