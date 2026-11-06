# 23) Knopf «Wunsch» ganz rechts in der Leiste: «Dir fehlt ein Werkzeug?» → Instagram der Lehrerin
#     (gilt auch für die Eulenkiste, die ihre Tagesfolie aus dieser Datei baut)
WUNSCH_ICON = ('<path d="M16 4a8 8 0 0 0-4.6 14.5c.8.6 1.3 1.5 1.3 2.5v1h6.6v-1c0-1 .5-1.9 1.3-2.5A8 8 0 0 0 16 4z" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linejoin="round"/>'
               '<path d="M12.8 26h6.4M13.8 29h4.4" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/>')
rep('function rerender(w){', r'''// Wunsch-Knopf: ganz rechts in der Leiste (nach allen anderen, auch den grauen der Eulenkiste)
const INSTA = "https://www.instagram.com/primarschuleulchen";
setTimeout(() => {
  const dock = document.getElementById("dock"); if (!dock || dock.querySelector("[data-wunsch]")) return;
  dock.insertAdjacentHTML("beforeend", `<span class="sep"></span><button data-wunsch class="wunsch" aria-label="Dir fehlt ein Werkzeug?"><svg viewBox="0 0 32 32" aria-hidden="true">''' + WUNSCH_ICON + r'''</svg>Wunsch</button>`);
  dock.querySelector("[data-wunsch]").addEventListener("click", () => sheet("Dir fehlt ein Werkzeug?", `<div class="wunsch-box">
      <p>Dir fehlt etwas in der Tagesfolie? Schreib es mir – vielleicht erscheint es schon bald hier.</p>
      <a class="sbtn rose wunsch-link" href="${INSTA}" target="_blank" rel="noopener">Auf Instagram schreiben ✦</a>
      <p class="hint">@primarschuleulchen</p></div>`));
}, 0);
function rerender(w){''')
rep('.t-plan.h{flex-direction:row;flex-wrap:wrap;justify-content:center}', '''.t-plan.h{flex-direction:row;flex-wrap:wrap;justify-content:center}
.dock button.wunsch svg{color:#c4952f}
.wunsch-box{text-align:center;display:flex;flex-direction:column;align-items:center;gap:12px;padding:6px 0 10px;font-size:19px}
.wunsch-box p{margin:0;max-width:30em}
.wunsch-link{display:inline-block;text-decoration:none;font-size:19px!important;padding:8px 20px!important;color:#1f2421}''')
