# 22) Start-Vorlage: so starten neue Lehrpersonen (Eulenkiste und Klassenkiste), von der Lehrerin eingerichtet.
#     Die Bildschirme stehen in vorlage.json (ohne Klassenliste/Abwesende). Eine in der Klassenkiste gespeicherte
#     Vorlage («Vorlagen» → «Als Vorlage für alle speichern», shared_store «tagesfolie-vorlage») hat weiterhin Vorrang.
import json as _json, os as _os
_V = _json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'vorlage.json'), encoding='utf-8'))
rep('function defaults(){\n', 'function defaults(){\n  const START = ' + _json.dumps(_V, ensure_ascii=False).replace('</', '<\\/') + ';\n')
rep('  return {\n    v: 3, active: "s-morgen", subjects: makeSubjects(), bgs: [],', '''  if (START && START.screens && START.screens.length) { const t = JSON.parse(JSON.stringify(START)); t.roster = []; t.groupSets = []; t.absent = { date: "", names: [] }; t.tplGot = []; return t; }
  return {
    v: 3, active: "s-morgen", subjects: makeSubjects(), bgs: [],''')
