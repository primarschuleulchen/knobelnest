# 27) (Stand: Folie unter der oberen Leiste bis an alle anderen Ränder; im Vollbild verschwindet der Streifen der Leiste
#     und die Folie rückt nach oben; Bausteine ganz oben haben ihre Werkzeugleiste innen, .w.oben)
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
  const sw = Math.max(window.screen.width || 0, aw), sh = Math.max(window.screen.height || 0, ah); // window.screen: «screen» ist hier der aktuelle Bildschirm der Folie
  const W = sw, H = sh - th; // Bildschirm ohne den Streifen der oberen Leiste; im Vollbild rückt die Folie nach oben
  const k = Math.min(aw / W, ah / H);
  b.style.width = W + "px"; b.style.height = H + "px"; b.style.setProperty("--vh", (sh / 100) + "px");
  b.style.transform = `translate(${((aw - W * k) / 2).toFixed(1)}px, ${APP.classList.contains("voll") ? 0 : ((ah - H * k) / 2).toFixed(1)}px) scale(${k.toFixed(5)})`;
}
try { new ResizeObserver(() => fitBoard()).observe(document.getElementById("bwrap")); } catch {}
window.addEventListener("resize", fitBoard);
document.addEventListener("fullscreenchange", () => { APP.classList.toggle("voll", !!document.fullscreenElement); setTimeout(fitBoard, 60); });
function renderBoard(){''')
rep('.t-plan.h{flex-direction:row;flex-wrap:wrap;justify-content:center}', '''.t-plan.h{flex-direction:row;flex-wrap:wrap;justify-content:center}
.bwrap{position:absolute;left:0;right:0;bottom:0;top:var(--topH,64px);margin:0}
.app.voll .bwrap{top:0;bottom:var(--topH,64px)}
.w.oben .chrome{top:4px}
#board{position:absolute;left:0;top:0;flex:none;margin:0;transform-origin:0 0;--vh:1vh}
.app .top{position:absolute;top:0;left:0;right:0}
.app .dock{position:absolute;bottom:0;left:50%;transform:translateX(-50%);max-width:calc(100% - 32px)}
.app.dragging .top,.app.dragging .dock,.app.dragging .music-chip,.app.dragging .w .chrome,.app.dragging .w .rs,.app.dragging .w .rse,.app.dragging .w .rsb{opacity:0!important;pointer-events:none}
.app.dragging .lfoot,.app.dragging .mnote.empty,.app.dragging .itools,.app.dragging .pl-ops{display:none!important}
.app.dragging .w.sel .card{outline:0}''')
rep('return `<div class="w ${w.type}${w.type === "title" ? " bare" : ""}', 'return `<div class="w ${w.type}${w.type === "title" ? " bare" : ""}${w.y < 7 ? " oben" : ""}')
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
