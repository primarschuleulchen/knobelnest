# 11) Stationen nach den Linien auf dem Weg (Höhe in % des Plans), neu «Neues Thema» nach der Präsentation
rep('''  // Höhe der Schildmitte in % des Plans: Thema 66.8, Recherche 45.6, Produkt 29.3
  if(k.y>66.8) return 'Thema';
  if(k.y>45.6) return 'Recherche';
  if(k.y>29.3) return 'Produkt';
  return 'Präsentation';''', '''  // Grenzen auf dem Weg (Höhe in % des Plans, von unten nach oben)
  if(k.y>81.8) return 'Thema';
  if(k.y>61.8) return 'Recherche';
  if(k.y>44.3) return 'Produkt';
  if(k.y>25.9) return 'Präsentation';
  return 'Neues Thema';''')
rep('''  const RANK={'Präsentation':0,'Produkt':1,'Recherche':2,'Thema':3};''', '''  const RANK={'Neues Thema':-1,'Präsentation':0,'Produkt':1,'Recherche':2,'Thema':3};''')
rep('''pill.className='st '+(st||'');''', '''pill.className='st '+(st||'').replace(' ','-');''')
rep('''.st:not(.Thema):not(.Recherche):not(.Produkt):not(.Präsentation){''', '''.st.Neues-Thema{background:#dcf1fa;color:#1f7099}
.st:not(.Thema):not(.Recherche):not(.Produkt):not(.Präsentation):not(.Neues-Thema){''')
# Eingabefelder in den Dialogen in der normalen Schrift statt Schreibmaschinenschrift
rep('''.dlg textarea{border-radius:16px;min-height:170px;font-size:14px;font-weight:400;font-family:ui-monospace,Menlo,Consolas,monospace}''',
    '''.dlg textarea{border-radius:16px;min-height:170px;font-size:16px;font-weight:600;line-height:1.5;font-family:var(--ui)}''')
