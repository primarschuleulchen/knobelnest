# ===== 18) Widget «Otterteich»: der Lautstärke-Teich läuft neben dem Auftrag weiter =====
OTTER_ICON = '<ellipse cx="16" cy="22" rx="12" ry="5" fill="none" stroke="currentColor" stroke-width="2.4"/><circle cx="16" cy="12" r="6" fill="none" stroke="currentColor" stroke-width="2.4"/><circle cx="11" cy="7.5" r="1.8" fill="currentColor"/><circle cx="21" cy="7.5" r="1.8" fill="currentColor"/><circle cx="16" cy="13.5" r="1.3" fill="currentColor"/>'
rep('''  stand:   { lab: "Arbeitsstand",''', '''  otter:   { lab: "Otterteich", w: 42, h: 46, d: () => ({}), icon: `''' + OTTER_ICON + '''` },
  stand:   { lab: "Arbeitsstand",''')
rep('''.concat(KN ? ["|","stand"] : []);''', '''.concat(KN ? ["|","stand"].concat(KN.otterUrl ? ["otter"] : []) : []);''')
rep('''    case "stand": return KN ?''', '''    case "otter": return `<div class="t-otter"><div class="ohead">🦦 Otterteich</div><div class="obody" data-otter="${w.id}"><span>${KN && KN.otterUrl ? "Der Otterteich erscheint hier (einmal pro Bildschirm)." : KN ? "Der Otterteich ist für dich noch nicht freigegeben." : "Den Otterteich gibt es nur in der Klassenkiste."}</span></div></div>`;
    case "stand": return KN ?''')
rep('''const DRAG_BODY = new Set(["title", "date", "clock", "symbol", "traffic", "image", "stand"]);''',
    '''const DRAG_BODY = new Set(["title", "date", "clock", "symbol", "traffic", "image", "stand", "otter"]);''')
rep('''.t-stand{position:absolute;inset:0}''', '''.t-stand{position:absolute;inset:0}
.w.otter{pointer-events:none}
.w.otter .chrome,.w.otter .ohead,.w.otter .rs,.w.otter .rse,.w.otter .rsb{pointer-events:auto}
.w.otter .card{background:none;box-shadow:none;pointer-events:none}
.t-otter{position:absolute;inset:0;display:flex;flex-direction:column}
.t-otter .ohead{flex:none;background:#123222;color:#fff;font:700 15px/1 var(--font, inherit);padding:7px 14px;border-radius:22px 22px 0 0;cursor:grab;user-select:none;box-shadow:0 3px 18px rgba(40,60,45,.12)}
.t-otter .obody{flex:1;min-height:0;display:flex;align-items:center;justify-content:center;text-align:center;padding:12px;border-radius:0 0 22px 22px;background:rgba(18,50,34,.12);color:#2c4a38;font-size:14px}
.obody.cov{background:none!important}
.obody.cov span{display:none}
.app.idle .t-otter .ohead{opacity:0}
#otterLayer{position:fixed;left:0;top:0;width:10px;height:10px;visibility:hidden;border-radius:0 0 22px 22px;overflow:hidden;background:#123222;box-shadow:0 6px 18px rgba(40,60,45,.16)}
#otterLayer.on{visibility:visible}
#otterLayer iframe{width:100%;height:100%;border:0;display:block}
.drag-otter #otterLayer iframe{pointer-events:none}''')
rep('''  <div class="board" id="board"></div>''', '''  <div id="otterLayer" aria-label="Otterteich"></div>
  <div class="board" id="board"></div>''')
rep('''function rerender(w){''', '''// Otterteich: ein einziges Fenster bleibt bestehen (Mikrofon und Otter laufen weiter) und liegt immer genau über dem Widget
(() => {
  const layer = document.getElementById("otterLayer"); let frame = null, last = "";
  const tick = () => {
    requestAnimationFrame(tick);
    const ph = KN && KN.otterUrl ? document.querySelector("#board .obody[data-otter]") : null;
    if (!ph) { if (last !== "off") { layer.classList.remove("on"); last = "off"; } return; }
    if (!frame) { frame = document.createElement("iframe"); frame.src = KN.otterUrl; frame.title = "Otterteich"; frame.allow = "microphone; autoplay"; layer.appendChild(frame); }
    if (!ph.classList.contains("cov")) ph.classList.add("cov");
    const r = ph.getBoundingClientRect(), wz = ph.closest(".w")?.style.zIndex || "1";
    const k = [r.left, r.top, r.width, r.height, wz].map(v => typeof v === "number" ? Math.round(v) : v).join(",");
    if (k === last) return; last = k;
    Object.assign(layer.style, { left: r.left + "px", top: r.top + "px", width: r.width + "px", height: r.height + "px", zIndex: wz });
    layer.classList.toggle("on", r.width > 20 && r.height > 20);
  };
  if (KN && KN.otterUrl) requestAnimationFrame(tick);
  document.addEventListener("pointerdown", e => { if (e.target.closest?.(".w.otter [data-grip], .w.otter .ohead, .w.otter [data-rs]")) APP_DRAGGING(true); }, true);
  window.addEventListener("pointerup", () => APP_DRAGGING(false));
  function APP_DRAGGING(on){ document.body.classList.toggle("drag-otter", on); }
})();
function rerender(w){''')
