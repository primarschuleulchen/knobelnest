# Tagesfolie im Stil der Eulenkiste / Klassenkiste
# Diese Datei gibt es zweimal, gleich: im Knobelnest (werkstatt/einbau/tagesfolie/eulenstil.py)
# und in der Eulenkiste (werkstatt/eulenstil_tagesfolie.py). Bei Änderungen beide anpassen.
#
# Nur die Bedienung bekommt den neuen Stil (obere Leiste, Leiste unten, Menüs, Fenster, Meldungen,
# Rahmen der Bausteine). Was die Lehrperson auf die Folie schreibt (Schrift, Farben), bleibt wie es ist.
#   - Schrift Patrick Hand in einer Stärke, etwas grösser
#   - weisse Knöpfe mit weichem blauem Schatten statt grauer Linien
#   - Gold als Akzent: aktueller Bildschirm, Auswahl, ✦ als Trenner, ✦ ✧ ✦ in den Fenstertiteln
#   - Knöpfe in Fenstern wie in der Klassenkiste (dunkler Rand, hellblau = wichtig)
#   - Bausteine mit blauem Schatten wie die Karten der Eulenkiste
#   - im Ruhemodus (Vollbild, Maus still) verschwindet auch der Mauszeiger

CSS = r'''
/* ===== Stil der Eulenkiste / Klassenkiste (eulenstil.py) ===== */
:root{--gold:#d6ad45;--gold-dark:#b58a24;--sun-soft:#fbf3dc;--sky-soft:#dcf0fd;--sky-deep:#3f78a8;--eline:#dbe7f1;
  --eui:"Patrick Hand","Segoe Print","Comic Sans MS",cursive;
  --eschatten:0 4px 14px rgba(63,120,168,.2);--eschatten-hoch:0 7px 20px rgba(63,120,168,.3)}
.top,.dock,.sheet,.dd,.menu,.chrome,.toast,.kn-tip{font-family:var(--eui)}
.top button,.dock button,.sheet button,.dd button,.menu button,.chrome button,.toast,.status{font-weight:400}
.app.idle,.app.idle *{cursor:none!important}

/* Obere Leiste */
.top{padding-block:12px 4px}
.pill,.tabs .navb{border:0;background:#fff;box-shadow:var(--eschatten);font-size:18px;padding:5px 16px;min-height:38px;transition:box-shadow .15s,transform .15s}
.tabs .navb{width:38px;height:38px;padding:0;font-size:18px}
.pill:hover,.tabs .navb:hover{box-shadow:var(--eschatten-hoch);transform:translateY(-1px)}
.pill:disabled:hover{box-shadow:var(--eschatten);transform:none}
.scrbtn{background:#fff;color:#1f2421;border:0;box-shadow:0 0 0 2px var(--gold),var(--eschatten);font-size:21px;padding:4px 18px;min-height:38px;transition:box-shadow .15s}
.scrbtn::before{content:"✦";color:var(--gold);font-size:.8em}
.scrbtn b{color:var(--gold-dark);font-weight:400;font-size:.8em}
.scrbtn small{background:var(--sky-soft);color:var(--sky-deep);font-size:14px;font-weight:400}
.scrbtn:hover{box-shadow:0 0 0 2px var(--gold),var(--eschatten-hoch)}
.status{background:none;font-size:16px;color:#6c766f}

/* Leiste unten */
.dock{background:rgba(255,255,255,.97);border:0;border-radius:24px;padding:6px 8px;box-shadow:0 10px 28px rgba(63,120,168,.2),0 2px 6px rgba(63,120,168,.1),inset 0 -2px 0 rgba(214,173,69,.45)}
.dock button{font-size:15px;line-height:1.1;border-radius:16px;padding:7px 6px 5px;transition:background .15s,transform .15s}
.dock button:hover{background:var(--sky-soft);transform:translateY(-2px)}
.dock button:active{transform:translateY(0)}
.dock .sep{width:16px;background:none;margin:0;display:flex;align-items:center;justify-content:center}
.dock .sep::before{content:"✦";color:var(--gold);font-size:13px}
@media (max-width:640px){.dock button{font-size:13px}}

/* Bausteine */
.w .card{border-radius:24px;box-shadow:0 8px 24px rgba(63,120,168,.13),0 2px 6px rgba(63,120,168,.08)}
.cal-sheet{box-shadow:0 8px 24px rgba(63,120,168,.13),0 2px 6px rgba(63,120,168,.08)}
.w.sel .card{outline:2px dashed var(--gold);outline-offset:5px}
.w .rse::after,.w .rsb::after{background:var(--gold)}
.w .rs::after{border-color:var(--gold)}
.w .chrome{border:0;box-shadow:var(--eschatten);padding:3px 4px}
.chrome button{font-size:15px;color:#4d5751}
.chrome .grip{font-weight:400}
.chrome button:hover{background:var(--sky-soft);color:#1f2421}
.lfoot,.addrow{font-family:var(--eui)}
.lfoot{border-top:1.5px dashed rgba(214,173,69,.5)}
.lfoot input,.addrow input[type=text]{font-size:16px;border:1.5px solid var(--eline);background:#fff}
.lfoot select{font-size:15px;font-weight:400;border:1.5px solid var(--eline)}

/* Menüs */
.dd,.menu{border:0;border-radius:20px;box-shadow:0 16px 40px rgba(63,120,168,.26),0 2px 8px rgba(63,120,168,.12)}
.ddhead{font-size:15px;font-weight:400;color:var(--sky-deep);letter-spacing:.08em}
.ddhead em{font-weight:400;background:var(--sky-soft)}
.ddrow{font-size:18px;font-weight:400;border-radius:12px}
.ddrow:hover,.menu button:hover,.ddic:hover,.ddfold:hover{background:var(--sky-soft)}
.ddrow.on{background:var(--sun-soft);color:#1f2421;font-weight:400;box-shadow:inset 0 0 0 1.5px var(--gold)}
.ddrow.on::before{content:"✦ ";color:var(--gold)}
.ddempty{font-size:15px}
.ddfoot{border-top:1.5px dashed rgba(214,173,69,.55)}
.menu button{font-size:17px}

/* Fenster */
.sheet-bg{background:rgba(31,52,70,.28)}
.sheet{border-radius:28px;box-shadow:0 24px 60px rgba(63,120,168,.32),0 0 0 1.5px #e1edf7}
.sheet header{padding:20px 22px 8px}
.sheet h2{font-size:34px}
.sheet h2::after{content:"✦ ✧ ✦";font-size:15px;color:var(--gold);letter-spacing:.2em;margin-left:14px;vertical-align:middle}
.sheet .body{padding:4px 22px 22px;font-size:17px}
.sheet p.hint{font-size:16px}
.sheet .body h3{font-weight:400;font-size:21px!important}
.sbtn{border:2px solid #1f2421;border-radius:12px;padding:4px 13px;font-size:16px;font-weight:400;box-shadow:0 3px 10px rgba(63,120,168,.14);transition:transform .15s,box-shadow .15s,background .15s}
.sbtn:hover{border-color:#1f2421;background:var(--sky-soft);transform:translateY(-1px);box-shadow:0 6px 14px rgba(63,120,168,.22)}
.sbtn.rose{background:var(--sky-soft);border-color:#1f2421;color:#1f2421}
.sbtn.rose:hover{background:#c9e7fb}
.chip{border:1.5px solid var(--eline);background:#fff;font-size:16px}
.chip:hover{border-color:var(--sky-deep);background:var(--sky-soft)}
.chip.added{background:var(--sun-soft);color:#1f2421;border-color:var(--gold)}
.sheet textarea,.sheet input[type=text],.sheet input[type=time],.sheet input[type=number],.sheet select{border:1.5px solid var(--eline);border-radius:12px}
.fonts button{border-width:1.5px;border-color:var(--eline);background:#fff}
.fonts button.on{border-color:var(--gold);background:var(--sun-soft);box-shadow:0 0 0 1.5px var(--gold)}
.fonts .fn{font-family:var(--eui);font-size:15px;font-weight:400}
.bgtiles button.on{border-color:var(--gold)}
.bgtiles button,.bgtiles .lab{font-family:var(--eui);font-weight:400}
.bgtiles .lab{font-size:16px}
.tiles button.on{border-color:var(--gold);background:var(--sun-soft)}
.tiles button.on::after{color:var(--gold-dark);font-family:var(--eui);font-weight:400}
.tiles .del{font-family:var(--eui)}
.sheet textarea:focus,.sheet input:focus,.sheet select:focus{outline:2px solid var(--sky-deep);outline-offset:1px}

/* Musik-Knopf */
.music-chip{font-family:var(--eui);border:0;box-shadow:var(--eschatten)}
.music-chip button{background:var(--sky-deep)}
:focus-visible{outline-color:var(--sky-deep)}

/* Meldung */
.toast{background:#fff;color:#1f2421;font-size:18px;padding:8px 20px;box-shadow:0 0 0 2px var(--gold),0 10px 26px rgba(63,120,168,.28)}
.toast::before{content:"✦ ";color:var(--gold)}
'''

ANKER = '@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}\n</style>'


def eulenstil(rep):
    """rep(alt, neu) = Ersetzen mit Prüfung, wie im jeweiligen Bau-Skript."""
    rep(ANKER, CSS.lstrip('\n') + ANKER)


# ===== Farbkreis: überall, wo man eine Farbe wählt, gibt es zusätzlich «+» = eigene Farbe aus dem Farbkreis =====
# Ein Ring mit allen Farben (aussen kräftig, innen blass), darunter hell/dunkel. «Zuletzt gewählt» merkt sich das Gerät.
# Die gewählte Farbe wird wie ein normaler Farbknopf ausgelöst, darum braucht jedes Farbfenster keine eigene Änderung.
FARBKREIS_JS = r'''
// ---------- Farbkreis (eulenstil.py) ----------
const FK_ATTR = ["data-tc", "data-cc", "data-icc", "data-col", "data-ncol"];
const fkHex = (h, s, l) => { s /= 100; l /= 100; const k = n => (n + h / 30) % 12, a = s * Math.min(l, 1 - l), f = n => l - a * Math.max(-1, Math.min(k(n) - 3, 9 - k(n), 1));
  return "#" + [f(0), f(8), f(4)].map(x => Math.round(x * 255).toString(16).padStart(2, "0")).join(""); };
const fkLast = { get(){ try { return JSON.parse(localStorage.getItem("kn_farbkreis") || "[]"); } catch { return []; } },
  add(c){ try { const l = [c].concat(this.get().filter(x => x !== c)).slice(0, 8); localStorage.setItem("kn_farbkreis", JSON.stringify(l)); } catch {} } };
function fkAdd(row){
  if (row.querySelector(".fk-btn")) return;
  const attr = FK_ATTR.find(a => row.querySelector(`[${a}]`)); if (!attr) return;
  const b = document.createElement("button"); b.type = "button"; b.className = "fk-btn" + (row.classList.contains("colors") ? " big" : "");
  b.title = "Eigene Farbe aus dem Farbkreis"; b.setAttribute("aria-label", "Eigene Farbe aus dem Farbkreis"); b.textContent = "+";
  row.appendChild(b);
  b.addEventListener("click", e => { e.stopPropagation(); fkOpen(row, attr); });
}
function fkOpen(row, attr){
  const holder = row.parentElement.classList.contains("switem") ? row.parentElement : row;
  const old = document.querySelector(".fk-panel"); if (old) { const same = old.previousElementSibling === holder; old.remove(); if (same) return; }
  const P = { h: 200, s: 60, l: 62 };
  const p = document.createElement("div"); p.className = "fk-panel";
  p.innerHTML = `<div class="fk-wheel" role="slider" aria-label="Farbton und Stärke" tabindex="0"><span class="fk-dot"></span></div>
    <div class="fk-side"><div class="fk-prev"></div>
      <label class="fk-lab">hell – dunkel<input type="range" min="18" max="92" value="62" class="fk-l" aria-label="Helligkeit"></label>
      <div class="fk-last"></div>
      <button type="button" class="sbtn rose fk-ok">Diese Farbe nehmen</button></div>`;
  holder.after(p);
  const wh = p.querySelector(".fk-wheel"), dot = p.querySelector(".fk-dot"), prev = p.querySelector(".fk-prev");
  const cur = () => fkHex(P.h, P.s, P.l);
  const paint = () => {
    wh.style.background = `radial-gradient(closest-side, hsl(0 0% ${P.l}%), hsl(0 0% ${P.l}% / 0)), conic-gradient(from 90deg, ${[0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360].map(h => `hsl(${h} 100% ${P.l}%)`).join(",")})`;
    const r = P.s / 100 * 50, a = P.h * Math.PI / 180;
    dot.style.left = (50 + r * Math.cos(a)) + "%"; dot.style.top = (50 + r * Math.sin(a)) + "%"; dot.style.background = cur();
    prev.style.background = cur(); prev.textContent = cur().toUpperCase();
    prev.style.color = P.l > 60 ? "#1f2421" : "#fff";
  };
  const last = fkLast.get();
  p.querySelector(".fk-last").innerHTML = last.length ? `<span>Zuletzt gewählt</span><div>${last.map(c => `<button type="button" class="fk-old" data-fk="${c}" style="background:${c}" aria-label="Farbe ${c}"></button>`).join("")}</div>` : "";
  const pick = e => { const r = wh.getBoundingClientRect(), dx = e.clientX - (r.left + r.width / 2), dy = e.clientY - (r.top + r.height / 2);
    P.h = (Math.atan2(dy, dx) * 180 / Math.PI + 360) % 360; P.s = Math.min(100, Math.hypot(dx, dy) / (r.width / 2) * 100); paint(); };
  wh.addEventListener("pointerdown", e => { e.preventDefault(); wh.setPointerCapture(e.pointerId); pick(e); });
  wh.addEventListener("pointermove", e => { if (wh.hasPointerCapture(e.pointerId)) pick(e); });
  wh.addEventListener("keydown", e => { const k = { ArrowLeft: [-10, 0], ArrowRight: [10, 0], ArrowUp: [0, 8], ArrowDown: [0, -8] }[e.key]; if (!k) return; e.preventDefault(); P.h = (P.h + k[0] + 360) % 360; P.s = Math.max(0, Math.min(100, P.s + k[1])); paint(); });
  p.querySelector(".fk-l").addEventListener("input", e => { P.l = +e.target.value; paint(); });
  const use = c => {
    fkLast.add(c);
    const t = document.createElement("button"); t.hidden = true; t.setAttribute(attr, c);
    const iid = row.querySelector("[data-iid]")?.dataset.iid; if (iid) t.dataset.iid = iid;
    p.remove(); row.appendChild(t); t.click(); t.remove();
  };
  p.addEventListener("click", e => { e.stopPropagation();
    const o = e.target.closest("[data-fk]"); if (o) { use(o.dataset.fk); return; }
    if (e.target.closest(".fk-ok")) use(cur()); });
  paint(); p.scrollIntoView({ block: "nearest", behavior: "smooth" });
}
new MutationObserver(() => document.querySelectorAll(".sheet .swrow, .sheet .colors").forEach(fkAdd)).observe(document.body, { childList: true, subtree: true });
// Kalenderblatt in eigener Farbe: kräftige Farbe oben, ganz helle unten
const calHex = c => /^#[0-9a-f]{6}$/i.test(c || "") ? [c, "#" + [1, 3, 5].map(i => Math.round(parseInt(c.substr(i, 2), 16) * .12 + 255 * .88).toString(16).padStart(2, "0")).join("")] : null;
'''

FARBKREIS_CSS = r'''
/* Farbkreis */
.fk-btn{width:34px;height:34px;border-radius:50%;border:2px solid #fff;padding:0;cursor:pointer;flex:none;font:400 22px/1 var(--eui);color:#fff;text-shadow:0 1px 3px rgba(0,0,0,.45);
  background:conic-gradient(from 90deg,#f28b82,#f6c26b,#f3e27a,#9fd18b,#7ccfc3,#8fc1e8,#9a9ee8,#c7a2e0,#f4a7b9,#f28b82);box-shadow:0 0 0 1.5px var(--gold)}
.fk-btn.big{width:42px;height:42px;border-width:3px}
.swrow.sm .fk-btn{width:26px;height:26px;font-size:18px}
.fk-btn:hover{transform:scale(1.08)}
.fk-panel{display:flex;gap:18px;flex-wrap:wrap;align-items:center;margin:8px 0 14px;padding:14px;border-radius:20px;background:#fbfdff;box-shadow:inset 0 0 0 1.5px var(--eline);font-family:var(--eui)}
.fk-wheel{position:relative;width:190px;height:190px;border-radius:50%;flex:none;cursor:crosshair;touch-action:none;box-shadow:0 0 0 3px #fff,0 0 0 4.5px var(--gold),0 6px 16px rgba(63,120,168,.2)}
.fk-dot{position:absolute;width:24px;height:24px;margin:-12px 0 0 -12px;border-radius:50%;border:3px solid #fff;box-shadow:0 0 0 1.5px #1f2421,0 2px 6px rgba(0,0,0,.3);pointer-events:none}
.fk-side{flex:1;min-width:170px;display:flex;flex-direction:column;gap:10px}
.fk-prev{height:48px;border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:17px;letter-spacing:.05em;box-shadow:inset 0 0 0 1.5px rgba(0,0,0,.08)}
.fk-lab{display:flex;flex-direction:column;gap:2px;font-size:16px;color:#6c766f}
.fk-lab input{width:100%;accent-color:var(--gold)}
.fk-last span{font-size:15px;color:#6c766f}
.fk-last div{display:flex;gap:6px;flex-wrap:wrap;margin-top:3px}
.fk-old{width:28px;height:28px;border-radius:50%;border:2px solid #fff;box-shadow:0 0 0 1px var(--eline);padding:0;cursor:pointer}
.fk-ok{align-self:flex-start}
'''


def farbkreis(rep):
    rep('function openColors(title, list, current, apply){', FARBKREIS_JS.lstrip('\n') + 'function openColors(title, list, current, apply){')
    rep('(CAL_COLORS[d.color] || CAL_COLORS.rose)', '(CAL_COLORS[d.color] || calHex(d.color) || CAL_COLORS.rose)')
    # Mehr fertige Farben: Gold, Eulenblau, Beere, Petrol
    rep('const TITLE_COLORS = ["#e07a70","#6f9a6c","#6f8fb3","#c99a52","#9b84c4","#1f2421"];',
        'const TITLE_COLORS = ["#e07a70","#6f9a6c","#6f8fb3","#c99a52","#9b84c4","#1f2421","#c4952f","#3f78a8","#b5527a","#4f9a98","#e0954f","#8a8f5a"];')
    rep('lila:["#a690cf","#f3effa"], petrol:["#5f9a98","#e8f3f2"] };',
        'lila:["#a690cf","#f3effa"], petrol:["#5f9a98","#e8f3f2"], gold:["#d6ad45","#fbf3dc"], himmel:["#6fa6d6","#e6f2fc"], beere:["#c9708f","#f9e9ef"], salbei:["#8fa88c","#eef3ec"] };')
    rep(ANKER, FARBKREIS_CSS.lstrip('\n') + ANKER)
