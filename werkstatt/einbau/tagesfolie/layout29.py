# 29) Aufteilung wie bei Klassen-Bildschirmen üblich: Die Folie füllt das ganze Fenster (so gross wie möglich, ganze Folie sichtbar),
#     der Hintergrund reicht bis an alle Ränder (gezeichnet in Folien-Koordinaten, darum liegt er genau wie im Vollbild).
#     Die Bedienung schwebt darüber: links oben Zurück, rechts oben Speicherstand, Rückgängig, Einstellungen (⚙: Schrift,
#     Hintergrund, Meine Bausteine, Vorlagen) und Vollbild, links unten die Bildschirm-Auswahl, unten die Bausteine-Leiste
#     mit Knopf zum Einklappen (gemerkt in localStorage «tf_dock_zu»). Im Vollbild verschwindet alles, wenn die Maus ruht.

# Knöpfe oben rechts zusammenfassen, Einstellungen in ein Menü
rep('''    <button class="pill undo" id="undoBtn" title="Rückgängig (⌘Z)" aria-label="Rückgängig" disabled>↶ Rückgängig</button>
    <button class="pill undo" id="redoBtn" title="Wiederholen (⇧⌘Z)" aria-label="Wiederholen" disabled>↷</button>
    <span class="status" id="status">Wird geladen …</span>
    <button class="pill" id="fontBtn">Schrift</button>
    <button class="pill" id="bgBtn">Hintergrund</button>
    <button class="pill" id="libBtn">Meine Bausteine</button>
    <button class="pill" id="tplBtn" style="display:none">Vorlagen</button>
    <button class="pill" id="fsBtn">⛶ Vollbild</button>''',
'''    <div class="tr">
    <span class="status" id="status">Wird geladen …</span>
    <button class="pill undo ic" id="undoBtn" title="Rückgängig (⌘Z)" aria-label="Rückgängig" disabled>↶</button>
    <button class="pill undo ic" id="redoBtn" title="Wiederholen (⇧⌘Z)" aria-label="Wiederholen" disabled>↷</button>
    <div class="setwrap"><button class="pill ic" id="setBtn" title="Einstellungen" aria-label="Einstellungen" aria-haspopup="true" aria-expanded="false"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="3.2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3M5.3 5.3l2.1 2.1M16.6 16.6l2.1 2.1M5.3 18.7l2.1-2.1M16.6 7.4l2.1-2.1" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></button>
      <div class="setmenu" id="setMenu" hidden>
        <button id="fontBtn">Schrift</button>
        <button id="bgBtn">Hintergrund</button>
        <button id="libBtn">Meine Bausteine</button>
        <button id="tplBtn" style="display:none">Vorlagen</button>
      </div></div>
    <button class="pill" id="fsBtn">⛶ Vollbild</button>
    </div>''')

# Fläche: so gross wie möglich im ganzen Fenster, mittig; Hintergrund deckt das ganze Fenster
rep('''  const voll = !!document.fullscreenElement, dk = document.getElementById("dock");
  const oben = voll ? 0 : th, unten = voll ? 0 : (dk ? Math.ceil(dk.offsetHeight) + 18 : 90), rand = voll ? 0 : 12;
  const bw = Math.max(50, aw - 2 * rand), bh = Math.max(50, ah - oben - unten);
  const k = Math.min(bw / sw, bh / sh);
  b.style.width = sw + "px"; b.style.height = sh + "px"; b.style.setProperty("--vh", (sh / 100) + "px");
  b.style.left = Math.round((aw - sw * k) / 2) + "px"; b.style.top = Math.round(oben + (bh - sh * k) / 2) + "px";''',
'''  const k = Math.min(aw / sw, ah / sh), bl = Math.round((aw - sw * k) / 2), bt = Math.round((ah - sh * k) / 2);
  b.style.width = sw + "px"; b.style.height = sh + "px"; b.style.setProperty("--vh", (sh / 100) + "px");
  b.style.left = bl + "px"; b.style.top = bt + "px";
  const box = [-bl / k, -bt / k, aw / k, ah / k].map(v => v.toFixed(1)).join(" ");
  if (box !== BGBOX) { BGBOX = box; try { drawBg(); } catch {} }
  const tbs = document.getElementById("tabs"); if (tbs) APP.style.setProperty("--tabsW", Math.ceil(tbs.offsetWidth) + "px");''')
rep('''  const g = document.getElementById("bg"); if (g) { g.style.width = b.style.width; g.style.height = b.style.height; g.style.left = b.style.left; g.style.top = b.style.top; g.style.transform = b.style.transform; }''', '')
rep('function fitBoard(){', '''let BGBOX = ""; // sichtbarer Ausschnitt in Folien-Koordinaten (für den Hintergrund bis an den Rand)
function fitBoard(){''')
# Hintergrund in Folien-Koordinaten zeichnen, sichtbar bis an alle Fensterränder
_n = s.count('<svg viewBox="0 0 ${W} ${H}" aria-hidden="true">')
assert _n == 2, 'Hintergrund-SVG: ' + str(_n)
s = s.replace('<svg viewBox="0 0 ${W} ${H}" aria-hidden="true">', '<svg viewBox="${BGBOX || `0 0 ${W} ${H}`}" aria-hidden="true">')

# Einstellungs-Menü, Leiste einklappen
rep('function renderBoard(){', r'''(() => {
  const btn = document.getElementById("setBtn"), menu = document.getElementById("setMenu"); if (!btn || !menu) return;
  const zu = () => { menu.hidden = true; btn.setAttribute("aria-expanded", "false"); };
  btn.addEventListener("click", e => { e.stopPropagation(); menu.hidden = !menu.hidden; btn.setAttribute("aria-expanded", String(!menu.hidden)); });
  menu.addEventListener("click", e => { if (e.target.closest("button")) zu(); });
  document.addEventListener("pointerdown", e => { if (!e.target.closest(".setwrap")) zu(); });
  document.addEventListener("keydown", e => { if (e.key === "Escape") zu(); });
})();
(() => {
  const dk = document.getElementById("dock"); if (!dk) return;
  let z = false; try { z = localStorage.getItem("tf_dock_zu") === "1"; } catch {}
  dk.insertAdjacentHTML("afterbegin", `<button class="dk-min" id="dkMin" title="Leiste einklappen" aria-label="Leiste einklappen"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg></button>`);
  dk.insertAdjacentHTML("afterend", `<button class="dk-open pill" id="dkOpen" title="Bausteine zeigen" aria-label="Bausteine zeigen"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 15l6-6 6 6" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>Bausteine</button>`);
  const set = v => { z = v; APP.classList.toggle("dkzu", v); try { localStorage.setItem("tf_dock_zu", v ? "1" : "0"); } catch {} };
  set(z);
  document.getElementById("dkMin").addEventListener("click", () => set(true));
  document.getElementById("dkOpen").addEventListener("click", () => set(false));
})();
function renderBoard(){''')

# Menüs der Bildschirm-Auswahl (jetzt unten links) nach oben aufklappen
rep('dd.className = "dd"; dd.style.left = Math.max(8, r.left) + "px"; dd.style.top = r.bottom + 8 + "px";',
    'dd.className = "dd"; dd.style.left = Math.max(8, r.left) + "px"; if (r.top > window.innerHeight / 2) { dd.style.bottom = (window.innerHeight - r.top + 8) + "px"; dd.style.top = "auto"; } else dd.style.top = r.bottom + 8 + "px";')
rep('m.style.top = r.bottom + 10 + "px";', 'if (r.top > window.innerHeight / 2) { m.style.bottom = (window.innerHeight - r.top + 10) + "px"; m.style.top = "auto"; } else m.style.top = r.bottom + 10 + "px";')

rep('#bg{inset:auto;left:0;top:0;transform-origin:0 0}', '''#bg{inset:0}
#app .top{inset:0;padding:0;display:block;background:none}
#app .top .spacer{display:none}
#app .top>#knBack{position:absolute;left:max(14px,env(safe-area-inset-left,0px));top:12px}
#app .top .tabs{position:absolute;left:max(14px,env(safe-area-inset-left,0px));bottom:calc(12px + env(safe-area-inset-bottom,0px));flex-wrap:nowrap}
#app .top .tr{position:absolute;right:max(14px,env(safe-area-inset-right,0px));top:12px;display:flex;align-items:center;gap:8px}
#app .top .tr .status{font-size:14px;background:rgba(255,255,255,.75);border-radius:999px;padding:3px 10px}
#app .top .pill.ic{width:38px;padding:0;justify-content:center;font-size:20px}
#app .top .pill.ic svg{width:20px;height:20px}
.setwrap{position:relative}
.setmenu{position:absolute;right:0;top:calc(100% + 8px);background:#fff;border-radius:16px;box-shadow:var(--eschatten-hoch);padding:6px;display:flex;flex-direction:column;min-width:190px;z-index:130}
.setmenu[hidden]{display:none}
.setmenu button{border:0;background:none;text-align:left;font:inherit;font-size:18px;padding:8px 14px;border-radius:10px;cursor:pointer;color:var(--ink)}
.setmenu button:hover{background:var(--sky-soft)}
#app .dock{left:calc(var(--tabsW,260px) + 26px);right:max(14px,env(safe-area-inset-right,0px));width:fit-content;max-width:none;margin:0 auto;transform:none;bottom:calc(10px + env(safe-area-inset-bottom,0px));flex-wrap:wrap;justify-content:center;overflow:visible;row-gap:0}
#app .dock button{min-width:52px;padding:5px 3px 4px;font-size:13px}
#app .dock svg{width:24px;height:24px}
.dk-min{order:99;align-self:center;border:0!important;background:none;width:30px!important;min-width:30px!important;height:30px;padding:0!important;border-radius:50%!important;color:var(--muted);margin-left:2px}
.dk-min svg{width:20px!important;height:20px!important}
#app.dkzu .dock{display:none}
.dk-open{display:none}
#app.dkzu .dk-open{display:inline-flex;position:absolute;left:50%;transform:translateX(-50%);bottom:calc(12px + env(safe-area-inset-bottom,0px));z-index:50;align-items:center;gap:4px;padding:4px 14px 4px 10px}
.dk-open svg{width:18px;height:18px}
#app.idle .dk-open,#app.dragging .dk-open{opacity:0;pointer-events:none}
.music-chip{bottom:calc(64px + env(safe-area-inset-bottom,0px))!important}''')
rep('.app:not(.voll) #board{box-shadow:0 6px 30px rgba(63,120,168,.22)}\n', '')
