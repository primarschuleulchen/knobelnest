# 29) Folie so gross wie möglich: Ist im Fenster seitlich mehr Platz als oben/unten (Querformat, Browserleisten),
#     wandern die Knöpfe in eine Spalte links (.app.seiten .top) und die Bausteine in eine Spalte rechts (.dock, zwei Reihen).
#     fitBoard() rechnet beide Anordnungen und nimmt die, bei der die Folie grösser wird (APP.dataset.layout = "oben"/"seiten" erzwingt eine).
rep('''  const voll = !!document.fullscreenElement, dk = document.getElementById("dock");
  const oben = voll ? 0 : th, unten = voll ? 0 : (dk ? Math.ceil(dk.offsetHeight) + 18 : 90), rand = voll ? 0 : 12;
  const bw = Math.max(50, aw - 2 * rand), bh = Math.max(50, ah - oben - unten);
  const k = Math.min(bw / sw, bh / sh);
  b.style.width = sw + "px"; b.style.height = sh + "px"; b.style.setProperty("--vh", (sh / 100) + "px");
  b.style.left = Math.round((aw - sw * k) / 2) + "px"; b.style.top = Math.round(oben + (bh - sh * k) / 2) + "px";''',
'''  const voll = !!document.fullscreenElement, dk = document.getElementById("dock");
  const kO = Math.min((aw - 24) / sw, (ah - 66 - 104) / sh), kS = Math.min((aw - 140 - 136) / sw, (ah - 16) / sh);
  const wahl = APP.dataset.layout, seiten = !voll && (wahl ? wahl === "seiten" : kS > kO + 0.01);
  APP.classList.toggle("seiten", seiten);
  let x0 = 0, x1 = aw, oben = 0, unten = 0;
  if (!voll && seiten) { x0 = (tb ? tb.offsetWidth : 140) + 4; x1 = aw - (dk ? dk.offsetWidth + 10 : 136); oben = 8; unten = 8; }
  else if (!voll) { x0 = 12; x1 = aw - 12; oben = tb ? Math.ceil(tb.offsetHeight) + 6 : 64; unten = dk ? Math.ceil(dk.offsetHeight) + 18 : 90; }
  const bw = Math.max(50, x1 - x0), bh = Math.max(50, ah - oben - unten);
  const k = Math.min(bw / sw, bh / sh);
  b.style.width = sw + "px"; b.style.height = sh + "px"; b.style.setProperty("--vh", (sh / 100) + "px");
  b.style.left = Math.round(x0 + (bw - sw * k) / 2) + "px"; b.style.top = Math.round(oben + (bh - sh * k) / 2) + "px";''')
rep('#bg{inset:auto;left:0;top:0;transform-origin:0 0}', '''#bg{inset:auto;left:0;top:0;transform-origin:0 0}
.app.seiten .top{top:0;bottom:0;right:auto;width:136px;flex-direction:column;flex-wrap:nowrap;align-items:stretch;gap:7px;padding:10px 8px 70px;overflow-y:auto}
.app.seiten .top .pill{font-size:15px;padding:4px 8px;min-height:34px}
.app.seiten .top .tabs{gap:4px}
.app.seiten .top .scrbtn{order:-1;flex:1 1 100%;max-width:100%;min-width:0;justify-content:center;font-size:16px;padding:4px 8px}
.app.seiten .top .scrbtn>span{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.app.seiten .top .scrbtn small{display:none}
.app.seiten .top .kn-back{align-self:center}
.app.seiten .top .tabs .navb{width:32px;height:32px}
.app.seiten .top .spacer{display:none}
.app.seiten .top .tabs{justify-content:center}
.app.seiten .top .pill{justify-content:center}
.app.seiten .top .undo{width:100%}
.app.seiten .top .status{text-align:center;font-size:14px}
.app.seiten .dock{left:auto;right:6px;bottom:auto;top:50%;transform:translateY(-50%);margin:0;display:grid;grid-template-columns:repeat(2,60px);gap:2px;max-height:calc(100% - 16px);overflow-y:auto;max-width:none}
.app.seiten .dock{padding:5px}
.app.seiten .dock button{min-width:0;padding:5px 1px 4px;font-size:11.5px;gap:2px;overflow-wrap:anywhere}
.app.seiten .dock svg{width:23px;height:23px}
.app.seiten .dock button:hover{transform:none}
.app.seiten .dock .sep{grid-column:1/-1;width:auto;height:8px}
.app.seiten .music-chip{bottom:14px}''')
