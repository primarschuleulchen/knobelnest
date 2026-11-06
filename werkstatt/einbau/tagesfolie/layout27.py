# 27) Die Folie sieht beim Bearbeiten genau gleich aus wie im Vollbild:
#     Die Fläche (#board) hat immer die Grösse, die sie im Vollbild auf diesem Bildschirm hätte (screen.width/height),
#     und wird im Fenster nur verkleinert gezeigt (transform: scale). Schriftgrössen hängen an --vh = 1 % der
#     Bildschirmhöhe statt an der Fensterhöhe. Rahmen #bwrap übernimmt den Platz im Layout.
#     Beim Verschieben/Grössenändern sind alle Knöpfe und Leisten ausgeblendet (.app.dragging).
import re as _re

rep('<div class="board" id="board"></div>', '<div class="bwrap" id="bwrap"><div class="board" id="board"></div></div>')
# Schriftgrössen: «var(--fs) * 1.2vh» → «var(--fs) * 1.2 * var(--vh)»
_n = len(_re.findall(r'(var\(--fs\) \* )([\d.]+)vh\b', s))
assert _n >= 10, 'vh-Stellen: ' + str(_n)
s = _re.sub(r'(var\(--fs\) \* )([\d.]+)vh\b', r'\g<1>\2 * var(--vh)', s)
# Beim Messen: Höhe des Bausteins im Verhältnis zur (unskalierten) Fläche
rep('  const hh = AUTO.has(w.type) ? el.offsetHeight / r.height * 100 : w.h;', '  const bH = $("#board").offsetHeight || r.height;\n  const hh = AUTO.has(w.type) ? el.offsetHeight / bH * 100 : w.h;')
rep('  const vh = AUTO.has(w.type) ? Math.max(4, (el.offsetHeight - edPx) / r.height * 100) : w.h;', '  const vh = AUTO.has(w.type) ? Math.max(4, (el.offsetHeight - edPx) / bH * 100) : w.h;')
# Beim Verschieben alles ausblenden, was später nicht zu sehen ist
rep('  if (Math.abs(e.clientX - drag.sx) + Math.abs(e.clientY - drag.sy) > 4) drag.moved = true;',
    '  if (Math.abs(e.clientX - drag.sx) + Math.abs(e.clientY - drag.sy) > 4) { drag.moved = true; APP.classList.add("dragging"); }')
rep('window.addEventListener("pointerup", () => { if (!drag) return;', 'window.addEventListener("pointerup", () => { APP.classList.remove("dragging"); if (!drag) return;')
rep('function renderBoard(){', r'''// Fläche in Vollbild-Grösse, im Fenster verkleinert
function fitBoard(){
  const wrap = document.getElementById("bwrap"), b = document.getElementById("board"); if (!wrap || !b) return;
  const aw = wrap.clientWidth, ah = wrap.clientHeight; if (!aw || !ah) return;
  const sw = Math.max(window.screen.width || 0, aw), sh = Math.max(window.screen.height || 0, ah); // window.screen: «screen» ist hier der aktuelle Bildschirm der Folie
  const W = Math.max(aw, sw - (APP.clientWidth - aw)), H = Math.max(ah, sh - (APP.clientHeight - ah));
  const k = Math.min(aw / W, ah / H);
  b.style.width = W + "px"; b.style.height = H + "px"; b.style.setProperty("--vh", (sh / 100) + "px");
  b.style.transform = `translate(${((aw - W * k) / 2).toFixed(1)}px, ${((ah - H * k) / 2).toFixed(1)}px) scale(${k.toFixed(5)})`;
}
try { new ResizeObserver(() => fitBoard()).observe(document.getElementById("bwrap")); } catch {}
window.addEventListener("resize", fitBoard);
document.addEventListener("fullscreenchange", () => setTimeout(fitBoard, 60));
function renderBoard(){''')
rep('.t-plan.h{flex-direction:row;flex-wrap:wrap;justify-content:center}', '''.t-plan.h{flex-direction:row;flex-wrap:wrap;justify-content:center}
.bwrap{position:relative;flex:1;min-height:0;margin-top:30px;margin-left:max(16px,env(safe-area-inset-left,0px));margin-right:max(16px,env(safe-area-inset-right,0px))}
#board{position:absolute;left:0;top:0;flex:none;margin:0;transform-origin:0 0;--vh:1vh}
.app.dragging .top,.app.dragging .dock,.app.dragging .music-chip,.app.dragging .w .chrome,.app.dragging .w .rs,.app.dragging .w .rse,.app.dragging .w .rsb{opacity:0!important;pointer-events:none}
.app.dragging .lfoot,.app.dragging .mnote.empty,.app.dragging .itools,.app.dragging .pl-ops{display:none!important}
.app.dragging .w.sel .card{outline:0}''')
