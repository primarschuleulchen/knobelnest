# 27) (Stand: Folie = ganzes Fenster ohne Verkleinern (Wunsch der Lehrerin); Leisten liegen darüber. Bausteine
#     ganz oben (.w.oben) haben ihre Werkzeugleiste unten; jeder Baustein lässt sich an freien Stellen greifen)
#     Die Folie sieht beim Bearbeiten genau gleich aus wie im Vollbild:
#     Die Fläche (#board) hat immer die Grösse, die sie im Vollbild auf diesem Bildschirm hätte (screen.width/height),
#     und wird im Fenster nur verkleinert gezeigt (transform: scale). Schriftgrössen hängen an --vh = 1 % der
#     Bildschirmhöhe statt an der Fensterhöhe. Die Fläche reicht bis an den Rand (#bwrap = ganzes Fenster);
#     obere Leiste und Werkzeugleiste liegen darüber (im Vollbild verschwinden sie, wenn die Maus ruht).
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
  const tb = document.querySelector(".top"), th = tb ? Math.ceil(tb.offsetHeight) + 6 : 64; // Platz für die obere Leiste
  if (APP.style.getPropertyValue("--topH") !== th + "px") APP.style.setProperty("--topH", th + "px");
  const aw = wrap.clientWidth, ah = wrap.clientHeight; if (!aw || !ah) return;
  // Fläche = ganzes Fenster (ohne Verkleinern, ohne Rand); Schrift wächst mit der Fensterhöhe
  b.style.width = aw + "px"; b.style.height = ah + "px"; b.style.setProperty("--vh", (ah / 100) + "px"); b.style.transform = "none";
}
try { new ResizeObserver(() => fitBoard()).observe(document.getElementById("bwrap")); } catch {}
window.addEventListener("resize", fitBoard);
document.addEventListener("fullscreenchange", () => { APP.classList.toggle("voll", !!document.fullscreenElement); setTimeout(fitBoard, 60); });
function renderBoard(){''')
rep('.t-plan.h{flex-direction:row;flex-wrap:wrap;justify-content:center}', '''.t-plan.h{flex-direction:row;flex-wrap:wrap;justify-content:center}
.bwrap{position:absolute;inset:0;margin:0}
.w.oben .chrome{top:auto;bottom:-34px}
.top{pointer-events:none}
.top>*{pointer-events:auto}
#board{position:absolute;left:0;top:0;flex:none;margin:0;transform-origin:0 0;--vh:1vh}
.app .top{position:absolute;top:0;left:0;right:0}
.app .dock{position:absolute;bottom:0;left:50%;transform:translateX(-50%);max-width:calc(100% - 32px)}
.app.dragging .top,.app.dragging .dock,.app.dragging .music-chip,.app.dragging .w .chrome,.app.dragging .w .rs,.app.dragging .w .rse,.app.dragging .w .rsb{opacity:0!important;pointer-events:none}
.app.dragging .lfoot,.app.dragging .mnote.empty,.app.dragging .itools,.app.dragging .pl-ops{display:none!important}
.app.dragging .w.sel .card{outline:0}''')
rep('return `<div class="w ${w.type}${w.type === "title" ? " bare" : ""}', 'return `<div class="w ${w.type}${w.type === "title" ? " bare" : ""}${w.y < 10 ? " oben" : ""}')
# Titel: am Text ziehen verschiebt den Titel; kurz antippen (ohne Ziehen) setzt den Schreibcursor zum Bearbeiten
rep('  const onBody = DRAG_BODY.has(w.type) && !e.target.closest("button,input,textarea,[contenteditable]");',
    '''  const tCe = w.type === "title" ? e.target.closest("[contenteditable]") : null, tEdit = tCe && document.activeElement !== tCe ? tCe : null;
  const onBody = DRAG_BODY.has(w.type) && (tEdit || !e.target.closest("button,input,textarea,[contenteditable]"));''')
rep('  drag = { w, el, mode: rs ? "rs" : "mv",', '  drag = { ted: tEdit ? w.id : "", w, el, mode: rs ? "rs" : "mv",')
rep('if (drag.moved) { save(); justDragged = true; setTimeout(() => justDragged = false, 0); } drag = null; });',
    '''if (drag.moved) { save(); justDragged = true; setTimeout(() => justDragged = false, 0); }
  else if (drag.ted) { const id = drag.ted, x = drag.sx, y = drag.sy; setTimeout(() => { const ce = document.querySelector(`[data-w="${id}"] [contenteditable]`); if (!ce) return; ce.focus();
    try { const r = document.caretRangeFromPoint ? document.caretRangeFromPoint(x, y) : null; if (r && ce.contains(r.startContainer)) { const s = getSelection(); s.removeAllRanges(); s.addRange(r); } } catch {} }, 30); }
  drag = null; });''')
# Jeder Baustein lässt sich an freien Stellen greifen (nicht nur an der Leiste); Knöpfe, Felder und Texte bleiben bedienbar
rep('  const onBody = DRAG_BODY.has(w.type) && (tEdit ||', '  const frei = !e.target.closest("button,input,textarea,select,a,label,[contenteditable],[data-it],[data-mk],[data-gname],[data-pick],iframe,.lfoot,.t-heft,.obody");\n  const onBody = (DRAG_BODY.has(w.type) || frei) && (tEdit ||')
