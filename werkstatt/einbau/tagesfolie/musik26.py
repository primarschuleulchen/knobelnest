# 26) Musik: YouTube braucht die Herkunftsangabe (Referrer), sonst «Fehler 153» – die Seite selbst schickt keine
#     (meta no-referrer), darum nur das YouTube-Fenster mit Referrer und origin. Titel nicht mehr anzeigen (nur ▶/⏸ und ♪).
#     «Endlos wiederholen» pro Musik einstellbar (music.loop, fehlt = an).
rep('''<span class="mt" data-medit title="Musik ändern">♪ ${esc(m.name || "Musik")}</span>''', '''<span class="mt" data-medit title="Musik ändern" aria-label="Musik ändern">♪</span>''')
rep('const a = new Audio(m.src); a.loop = true; MUS.el = a;', 'const a = new Audio(m.src); a.loop = m.loop !== false; MUS.el = a; a.addEventListener("ended", () => { MUS.playing = false; musicRender(); });')
rep('f.src = `https://www.youtube-nocookie.com/embed/${m.id}?autoplay=1&loop=1&playlist=${m.id}&controls=0&enablejsapi=1&playsinline=1`;',
    'f.referrerPolicy = "strict-origin-when-cross-origin";\n      f.src = `https://www.youtube-nocookie.com/embed/${m.id}?autoplay=1${m.loop === false ? "" : `&loop=1&playlist=${m.id}`}&controls=0&enablejsapi=1&playsinline=1&origin=${encodeURIComponent(location.origin)}`;')
rep('''<button class="sbtn" data-mrm>Musik entfernen</button></p>` : ""}''', '''<button class="sbtn" data-mrm>Musik entfernen</button></p>
      <label style="display:flex;align-items:center;gap:10px;margin:0 0 14px;font-size:17px"><input type="checkbox" data-mloop ${s.music.loop === false ? "" : "checked"} style="width:22px;height:22px"> Endlos wiederholen (sonst hört die Musik am Ende auf)</label>` : ""}''')
rep('    if (e.target.closest("[data-mrm]")) {', '''    if (e.target.matches && e.target.matches("[data-mloop]")) { s.music.loop = e.target.checked; save();
      if (s.id === S.active && MUS.el) { if (MUS.kind === "file") MUS.el.loop = s.music.loop; else syncMusic(true); } return; }
    if (e.target.closest("[data-mrm]")) {''')
rep('.t-plan.h{flex-direction:row;flex-wrap:wrap;justify-content:center}', '''.t-plan.h{flex-direction:row;flex-wrap:wrap;justify-content:center}
.music-chip{padding:4px!important;gap:2px!important}
.music-chip .mt{padding:0 8px 0 4px;font-size:18px}''')
