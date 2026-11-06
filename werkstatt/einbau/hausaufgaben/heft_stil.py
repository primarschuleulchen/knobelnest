# 12) Klassenkiste-/Eulenkiste-Stil: Schrift Patrick Hand auch in der Bedienung, Aquarell-Hintergrund, Gold-Akzente,
#     ruhige Titel statt Umriss-Schrift, goldenes Lesezeichen, helle Einbände mit Goldrand. Standard «monat»: Farbe passend
#     zum Monat der angezeigten Woche (MONATE_C), dazu die zwölf Monats-Einbände m1–m12 und «Eule» einzeln wählbar.
#     Die Handschrift der Einträge bleibt wählbar (--hand). Nur Aussehen, Daten und Abläufe bleiben gleich.
MK = ' '.join('m%d:MONATE_C[%d],' % (i + 1, i) for i in range(12))
rep('const COVERS = { gruen:', 'const MONATE_C = [["#dfeaf6","#c6d9ee"],["#e7e4f5","#d1cbea"],["#e4f2dc","#cbe5bf"],["#f8e4eb","#efcbd7"],["#ede2f5","#d9c7ec"],["#fbf1d2","#f2df9f"],["#d7eef6","#b7dfee"],["#fbe5d4","#f3cdb0"],["#f2ead2","#e3d2a3"],["#f8e1ca","#eec7a0"],["#e5eae2","#cdd7cb"],["#f5e0e0","#e7c6c6"]];\n'
    'const MONATE_N = ["Januar","Februar","März","April","Mai","Juni","Juli","August","September","Oktober","November","Dezember"];\n'
    'const COVER_N = k => k === "monat" ? "Passend zum Monat" : k === "eule" ? "Eule" : /^m\\d+$/.test(k) ? MONATE_N[+k.slice(1) - 1] : k.charAt(0).toUpperCase() + k.slice(1);\n'
    'const COVERS = { monat:MONATE_C[new Date().getMonth()], eule:["#d9ebfa","#bcd8f1"], ' + MK + ' gruen:')
rep('settings:{ lines:8, font:"Patrick Hand", cover:"gruen" }', 'settings:{ lines:8, font:"Patrick Hand", cover:"monat" }')
rep('const c = COVERS[S.settings.cover] || COVERS.gruen;', 'const c = S.settings.cover === "monat" || !COVERS[S.settings.cover] ? MONATE_C[addDays(week, 3).getMonth()] : COVERS[S.settings.cover];')
rep('book.style.setProperty("--cover", c[0]);', 'book.classList.toggle("eule", !COVERS[S.settings.cover] || /^(eule|monat|m\\d+)$/.test(S.settings.cover)); book.style.setProperty("--cover", c[0]);')
# Auswahl im Fenster: Namen beim Darüberfahren, «Passend zum Monat» mit Stern
rep('aria-label="Umschlag ${k}"></button>`).join("")}</div></div>`;', 'aria-label="Umschlag ${COVER_N(k)}" title="${COVER_N(k)}">${k === "monat" ? "✦" : ""}</button>`).join("")}</div><p class="covtip">✦ = passend zum Monat, wechselt von selbst mit der Woche</p></div>`;')
rep('#knBack{font-weight:700}', '''#knBack{font-weight:700}
/* ===== Klassenkiste-Stil ===== */
:root{--ui:"Patrick Hand","Segoe Print","Comic Sans MS",cursive;--gold:#d6ad45;--gold-d:#a87c1f;--sun:#fbf3dc;--himmel:#dcf0fd;--blau:#3f78a8;--line2:#c5d8e8;
  --sch:0 10px 26px rgba(63,120,168,.18),0 2px 6px rgba(63,120,168,.10);--sch-k:0 4px 12px rgba(63,120,168,.14);--leaf-soft:#eaf5fe}
body{font-size:17px}
:focus-visible{outline:3px solid var(--gold)!important;outline-offset:2px}
.bg{background:radial-gradient(1200px 600px at 10% -10%,#e3f1fc 0%,transparent 60%),radial-gradient(900px 500px at 110% 110%,#fbf3dc 0%,transparent 60%),#f4f9fd!important}
/* Leiste oben: weisse Pillen mit feinem Rand, Hauptknopf hellblau */
.pill{border:1.5px solid var(--line2);font-weight:400;font-size:18px;height:40px;box-shadow:var(--sch-k)}
.pill:hover{background:var(--himmel)}
.pill.ic{width:40px;font-weight:400}
.pill.rose{background:var(--himmel);border:2px solid var(--ink);color:var(--ink)}
.pill.rose:hover{background:#c9e5fa}
.wk{font-size:28px}
.wk small,.status{font-family:var(--ui);font-weight:400;font-size:15px}
/* Buch: Umschlag «Eule» hell mit goldenen Stichen */
.book{box-shadow:var(--sch),inset 0 0 0 2px rgba(255,255,255,.4)}
.book.eule{background:radial-gradient(circle,rgba(214,173,69,.55) 1.4px,transparent 2px) 0 0/16px 16px,linear-gradient(160deg,var(--cover),var(--cover2));box-shadow:var(--sch),inset 0 0 0 3px #fff,inset 0 0 0 5px rgba(214,173,69,.6)}
.ribbon{background:repeating-linear-gradient(170deg,#e2bd5c 0 3px,#d6ad45 3px 6px)}
/* Titel «November» / «Woche 45»: ruhige Handschrift mit Gold-Stern statt Umriss-Schrift */
.big,.rtop h1{font-family:var(--ui)!important;font-weight:400!important;color:var(--ink)!important;text-shadow:none!important;letter-spacing:.01em}
.big::after,.rtop h1::after{content:" ✦";color:var(--gold);font-size:.5em;vertical-align:super}
.klasse{font-family:var(--ui)}
/* Tage: Name in Schwarz (passt zu allen Einbänden), heute als goldene Pille */
.dname{font-family:var(--ui);font-weight:400;letter-spacing:.08em;color:var(--ink);font-size:clamp(13px,calc(var(--lh)*.48),20px)}
.today .dname{background:var(--sun);color:var(--ink);box-shadow:0 0 0 1.5px var(--gold);padding:1px 12px 0}
.dadd:hover{background:var(--himmel)}
/* Seitenleiste zum Bearbeiten und Fenster */
.panel{font-family:var(--ui)}
.ph h2::after{content:" ✦";color:var(--gold);font-size:.5em;vertical-align:super}
.lbl{font-weight:400;font-size:14px;letter-spacing:.1em;color:var(--blau)}
.opt,.btn{font-weight:400;font-size:17px;border:1.5px solid var(--line2)}
.opt:hover,.btn:hover{background:var(--himmel)}
.opt.on{background:var(--sun);border-color:var(--gold);color:var(--ink);box-shadow:0 0 0 1px var(--gold) inset}
.btn.go{background:var(--himmel);border:2px solid var(--ink);color:var(--ink)}
.btn.go:hover{background:#c9e5fa}
.toast{font-weight:400;font-size:17px}
.tile .tn{font-family:var(--ui)!important;font-weight:400!important}
.sw[data-cov="monat"]{display:inline-grid;place-items:center;color:var(--gold-d);font-size:18px;background:conic-gradient(#cbe5bf 0 25%,#f2df9f 0 50%,#eec7a0 0 75%,#c6d9ee 0)!important}
.covtip{margin:6px 0 0;font-size:14px;color:var(--muted)}
.ptab,.seg button{font-weight:400;font-size:17px}
.ptab{border:1.5px solid var(--line2)}
.ptab.on,.seg button.on{background:var(--himmel);border-color:var(--ink);color:var(--ink);box-shadow:0 0 0 1px var(--ink) inset}''')
