# 24) Hausaufgaben-Baustein: umschalten zwischen Kurzansicht (heute / morgen / bald) und dem ganzen Hausaufgabenheft
#     (gleiche Ansicht wie im Werkzeug; das Portal öffnet dafür #/hausaufgaben/<Klasse>/embed, KN.heftUrl). Nur Klassenkiste.
rep('heft: ["↻", "Hausaufgaben neu laden"]', 'heft: ["⇄ Ansicht", "Kurzansicht oder ganzes Heft"]')
rep('    if (w.type === "heft") { heftLoad(true); toast("Hausaufgaben werden neu geladen"); }', '    if (w.type === "heft") heftToggle(w);')
rep('''  if (!HEFT.data) { heftLoad(); return head + `<div class="emptyhint">Hausaufgaben werden geladen …</div>`; }''',
    '''  if (d.voll && KN.heftUrl) return `<div class="t-heftvoll"><iframe src="${esc(KN.heftUrl)}" title="Hausaufgabenheft"></iframe></div>`;
  if (!HEFT.data) { heftLoad(); return head + `<div class="emptyhint">Hausaufgaben werden geladen …</div>`; }''')
rep('''    ${HEFT.err ? `<div class="hf-leer">Das Heft konnte gerade nicht geladen werden.</div>` : ""}</div>`;''',
    '''    ${HEFT.err ? `<div class="hf-leer">Das Heft konnte gerade nicht geladen werden.</div>` : ""}
    ${KN.heftUrl ? `<button class="hf-voll" data-hfvoll>Ganzes Heft zeigen</button>` : ""}</div>`;''')
rep('function heftHTML(w){', r'''function heftToggle(w){
  const d = w.data; d.voll = !d.voll;
  if (d.voll) { w.w = Math.max(w.w, 62); w.h = Math.max(w.h, 74); w.x = Math.max(0, Math.min(w.x, 100 - w.w)); w.y = Math.max(0, Math.min(w.y, 100 - w.h)); }
  else heftLoad(true);
  save(); rerender(w);
}
function heftHTML(w){''')
rep('  if (e.target.closest("[data-rreset]")) {', '''  if (e.target.closest("[data-hfvoll]")) { heftToggle(w); return; }
  if (e.target.closest("[data-rreset]")) {''')
rep('.hf-tag.bald{font-size:.82em}', '''.hf-tag.bald{font-size:.82em}
.hf-voll{align-self:flex-start;margin-top:.2em;border:0;background:none;padding:0;color:#3f78a8;text-decoration:underline;font:inherit;font-size:.7em;cursor:pointer}
.t-heftvoll{position:absolute;inset:0}
.t-heftvoll iframe{width:100%;height:100%;border:0;display:block}''')
