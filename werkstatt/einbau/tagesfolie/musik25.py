# 25) Baustein «Lautstärke» (früher «Otterteich»): ohne dunklen Titel, rundum runde Ecken; Verschieben über die Leiste
#     oben (erscheint beim Darüberfahren/Antippen). Musik: YouTube-Fenster bleibt bestehen und ist gross genug
#     (YouTube spielt erst ab 200 × 200 px), der Knopf zeigt, ob wirklich Musik läuft.

# ---------- Lautstärke ----------
rep('  otter:   { lab: "Otterteich",', '  otter:   { lab: "Lautstärke",')
rep('<div class="t-otter"><div class="ohead">🦦 Otterteich</div><div class="obody"', '<div class="t-otter"><div class="obody"')
rep('"Der Otterteich erscheint hier (einmal pro Bildschirm)."', '"Der Lautstärkeregler erscheint hier (einmal pro Bildschirm)."')
rep('"Der Otterteich ist für dich noch nicht freigegeben."', '"Der Lautstärkeregler ist für dich noch nicht freigegeben."')
rep('"Den Otterteich gibt es nur in der Klassenkiste."', '"Den Lautstärkeregler gibt es nur in der Klassenkiste."')
rep('function rerender(w){', r'''// Lautstärke: Maus über dem Teich zeigt die Leiste zum Verschieben (der Teich selbst fängt alle Klicks)
(() => {
  const layer = document.getElementById("otterLayer"); if (!layer) return; let t = 0;
  const w = () => document.querySelector("#board .w.otter");
  layer.addEventListener("pointerenter", () => { clearTimeout(t); w()?.classList.add("hov"); });
  layer.addEventListener("pointerleave", () => { clearTimeout(t); t = setTimeout(() => { const x = w(); if (x && !x.matches(":hover")) x.classList.remove("hov"); }, 900); });
  document.addEventListener("pointerover", e => { const x = w(); if (x && e.target.closest && e.target.closest(".w.otter .chrome")) { clearTimeout(t); x.classList.add("hov"); } });
})();
function rerender(w){''')

# ---------- Musik ----------
rep('  if (MUS.kind === "yt" && MUS.el && !c.contains(MUS.el)) c.appendChild(MUS.el);', '  if (MUS.kind === "yt" && MUS.el && !MUS.el.isConnected) APP.appendChild(MUS.el);')
rep('      MUS.el = f; MUS.playing = true;', '''      f.addEventListener("load", () => { try { f.contentWindow.postMessage(JSON.stringify({ event: "listening", id: 1, channel: "widget" }), "*"); } catch {} });
      MUS.el = f; MUS.playing = false;''')
rep('function musicToggle(){', r'''// YouTube meldet, ob es wirklich spielt (1 = spielt, 3 = lädt)
window.addEventListener("message", e => {
  if (!MUS.el || MUS.kind !== "yt" || e.source !== MUS.el.contentWindow) return;
  let d; try { d = typeof e.data === "string" ? JSON.parse(e.data) : e.data; } catch { return; }
  const st = d && d.info && d.info.playerState; if (st == null) return;
  const p = st === 1 || st === 3; if (p !== MUS.playing) { MUS.playing = p; musicRender(); }
});
function musicToggle(){''')
rep('.t-plan.h{flex-direction:row;flex-wrap:wrap;justify-content:center}', '''.t-plan.h{flex-direction:row;flex-wrap:wrap;justify-content:center}
iframe.yt{position:fixed;left:0;bottom:0;width:220px;height:220px;opacity:0;pointer-events:none;border:0;z-index:-1}
#otterLayer,.t-otter .obody{border-radius:22px!important}
.w.otter.hov .chrome{opacity:1}''')
