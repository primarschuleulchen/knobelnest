# Einheitlicher Zurück-Knopf wie auf der Eulenkiste: weisse Pille mit Pfeil und Eulen-Logo.
# Wird von alle_neu_bauen.py auf jedes eingebaute Werkzeug angewendet (nach dem Einbau-Skript).
LABEL = 'Zurück zur Klassenkiste'
def inhalt(eule):
    return '<span aria-hidden="true">←</span><img src="' + eule + '" alt="" width="34" height="34">'
CSS = ('#knBack,.kn-back{align-items:center;gap:6px;padding:3px 4px 3px 13px!important;min-height:0!important;height:auto!important;'
       'border-radius:999px!important;background:#fff!important;color:#1f2421!important;border:0!important;text-decoration:none;'
       'font:700 19px/1 system-ui,-apple-system,sans-serif!important;box-shadow:0 4px 14px rgba(63,120,168,.2)!important;flex:none;cursor:pointer}'
       '#knBack:not([hidden]),.kn-back{display:inline-flex}'
       '#knBack:hover,.kn-back:hover{box-shadow:0 6px 18px rgba(63,120,168,.3)!important;transform:none}'
       '#knBack img,.kn-back img{width:34px;height:34px;display:block;border-radius:50%}')
def zurueck(s, eule):
    s = s.replace('>← Klassenkiste<', '>' + inhalt(eule) + '<')
    s = s.replace('id="knBack"', 'id="knBack" aria-label="' + LABEL + '" title="' + LABEL + '"')
    s = s.replace("b.textContent='← Klassenkiste';", "b.innerHTML='" + inhalt(eule) + "';b.setAttribute('aria-label','" + LABEL + "');")
    s = s.replace("img-src data:;", "img-src data: 'self';")  # Otterteich: Eulen-Bild darf geladen werden
    if '/* kn-back */' not in s:
        i = s.find('</style>')
        if i >= 0: s = s[:i] + '/* kn-back */' + CSS + '\n' + s[i:]
    return s
