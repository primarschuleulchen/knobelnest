# Mein Wochenziel -> Klassenkiste (wochenziel.html). Aufruf: python3 wz_patch.py <Original> <Ziel>
# Version 1: läuft unter dem Konto der Lehrperson (Klassengerät/Beamer). Gespeichert wird im Speicher der Lehrperson
# (teacher_store «wz-<Klasse>») über die Brücke window.knWochenziel (claude.use('db')-Nachbau in app.js, wzBridge).
# Kinder melden sich im Werkzeug selbst mit Namen und Bildpasswort an (wie im Original).
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, ('Anzahl %d statt %d: ' % (c, n)) + a[:90]
    s = s.replace(a, b)

# 1) Speicher: im Portal die Brücke der Klassenkiste nehmen, sonst wie bisher claude.ai bzw. nur dieses Gerät
rep('''    if (window.claude && typeof window.claude.use === 'function')
      db = await Promise.race([window.claude.use('db'), new Promise(r => setTimeout(() => r(null), 10000))]);''',
    '''    const KNW = (() => { try { return window.parent !== window && window.parent.knWochenziel; } catch (e) { return null; } })();
    if (KNW && KNW.claude) db = await KNW.claude.use('db');
    else if (window.claude && typeof window.claude.use === 'function')
      db = await Promise.race([window.claude.use('db'), new Promise(r => setTimeout(() => r(null), 10000))]);''')

# 2) Zurück-Knopf zur Klassenkiste (oben links, nur im Portal sichtbar)
rep('<header class="top">', '<header class="top">', 1)
i = s.find('</body>')
assert i > 0
s = s[:i] + '''<button class="pill" id="knBack" type="button" hidden>← Klassenkiste</button>
<style>#knBack{position:fixed;left:12px;top:10px;z-index:60}body.inkn{padding-top:58px}</style>
<script>(() => { let K = null; try { K = window.parent !== window && window.parent.knWochenziel; } catch (e) {}
  if (!K) return; const b = document.getElementById('knBack'); b.hidden = false; document.body.classList.add('inkn');
  b.addEventListener('click', () => { try { K.back(); } catch (e) {} }); })();</script>
''' + s[i:]
open(dst, 'w', encoding='utf-8').write(s)
# 3) Startseite: die Regel für die Kinderansicht (.kid = ganze Bildschirmhöhe) traf auch den Knopf «Ich bin ein Kind»
s = s.replace('</style>', '.door.kid{min-height:0;padding:16px 18px}\n</style>', 1)
open(dst, 'w', encoding='utf-8').write(s)
