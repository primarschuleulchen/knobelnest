# 8) Pinnwand zeilenweise: 1 links, 2 rechts daneben (statt Spalten von oben nach unten)
rep('#knBack{margin-right:4px}', '''#knBack{margin-right:4px}
.board{columns:auto!important;display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:22px 20px;align-items:start}
.board>.note{margin:0}
.present-on .board{grid-template-columns:repeat(auto-fill,minmax(330px,1fr))}''')
