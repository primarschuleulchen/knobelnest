# 28) Vorschau = Vollbild, nur kleiner: Im Fenster wird die ganze Folie gezeigt (nichts abgeschnitten), verkleinert
#     in den Platz zwischen oberer Leiste und Werkzeugleiste, mittig. Im Vollbild füllt sie den Bildschirm.
#     Die Folie ist immer gleich gross (Bildschirmgrösse), darum liegen Bausteine und Schriften genau gleich.
rep('''  const k = aw / sw;
  b.style.width = sw + "px"; b.style.height = sh + "px"; b.style.setProperty("--vh", (sh / 100) + "px");
  b.style.transform = Math.abs(k - 1) < 0.001 ? "none" : `scale(${k.toFixed(5)})`;''',
'''  const voll = !!document.fullscreenElement, dk = document.getElementById("dock");
  const oben = voll ? 0 : th, unten = voll ? 0 : (dk ? Math.ceil(dk.offsetHeight) + 18 : 90), rand = voll ? 0 : 12;
  const bw = Math.max(50, aw - 2 * rand), bh = Math.max(50, ah - oben - unten);
  const k = Math.min(bw / sw, bh / sh);
  b.style.width = sw + "px"; b.style.height = sh + "px"; b.style.setProperty("--vh", (sh / 100) + "px");
  b.style.left = Math.round((aw - sw * k) / 2) + "px"; b.style.top = Math.round(oben + (bh - sh * k) / 2) + "px";
  b.style.transform = Math.abs(k - 1) < 0.001 ? "none" : `scale(${k.toFixed(5)})`;''')
rep('.t-plan.h{flex-direction:row;flex-wrap:wrap;justify-content:center}', '''.t-plan.h{flex-direction:row;flex-wrap:wrap;justify-content:center}
.bwrap{background:#e9edf1}
.app:not(.voll) #board{box-shadow:0 6px 30px rgba(63,120,168,.22)}
.app.voll .bwrap{background:#000}''')
# Hintergrund gehört zur Folie: liegt genau unter der Fläche, gleich gross und gleich verkleinert, gezeichnet in Bildschirmgrösse
rep('  <div class="bg" id="bg"></div>\n', '')
rep('<div class="bwrap" id="bwrap"><div class="board" id="board"></div></div>', '<div class="bwrap" id="bwrap"><div class="bg" id="bg"></div><div class="board" id="board"></div></div>')
rep('const t = BG_TPL[src.slice(4)], W = window.innerWidth, H = window.innerHeight;', 'const t = BG_TPL[src.slice(4)], W = Math.max(window.screen.width || 0, 1), H = Math.max(window.screen.height || 0, 1);')
rep('  const W = window.innerWidth, H = window.innerHeight;\n  bg.innerHTML', '  const W = Math.max(window.screen.width || 0, 1), H = Math.max(window.screen.height || 0, 1);\n  bg.innerHTML')
rep('''  b.style.transform = Math.abs(k - 1) < 0.001 ? "none" : `scale(${k.toFixed(5)})`;''', '''  b.style.transform = Math.abs(k - 1) < 0.001 ? "none" : `scale(${k.toFixed(5)})`;
  const g = document.getElementById("bg"); if (g) { g.style.width = b.style.width; g.style.height = b.style.height; g.style.left = b.style.left; g.style.top = b.style.top; g.style.transform = b.style.transform; }''')
rep('.app.voll .bwrap{background:#000}', '''.app.voll .bwrap{background:#000}
#bg{inset:auto;left:0;top:0;transform-origin:0 0}''')
