// Knobelnest – Webseite für Lehrpersonen und Kinder
(function () {
  'use strict';
  var C = window.KN_CONFIG, DB = window.DB;
  var app = document.getElementById('app');

  // ===================================================================
  // Hilfsmittel
  // ===================================================================
  var LS = {
    get: function (k) { try { return JSON.parse(localStorage.getItem(k)); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} },
    del: function (k) { try { localStorage.removeItem(k); } catch (e) {} }
  };
  function h(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function rnd(n) { var a = new Uint32Array(1); crypto.getRandomValues(a); return a[0] % n; }
  function uniq(a) { return a.filter(function (x, i) { return a.indexOf(x) === i; }); }
  function plural(n, one, many) { return n === 1 ? '1 ' + one : n + ' ' + many; }
  function initials(n) { n = (n || '?').trim(); var p = n.split(/\s+/); return (p[0][0] + (p.length > 1 ? p[p.length - 1][0] : '')).toUpperCase(); }
  function hash(s) { var x = 0; s = String(s); for (var i = 0; i < s.length; i++) x = (x * 31 + s.charCodeAt(i)) >>> 0; return x; }
  function kidUrl(code) { return location.origin + location.pathname + '#/klasse' + (code ? '/' + encodeURIComponent(String(code).replace(/\s+/g, '')) : ''); }
  var qrLib = null;
  function loadQR() {
    if (window.qrcode) return Promise.resolve(window.qrcode);
    if (!qrLib) qrLib = new Promise(function (res, rej) {
      var s = document.createElement('script'); s.src = 'https://cdn.jsdelivr.net/npm/qrcode-generator@1.4.4/qrcode.js';
      s.onload = function () { res(window.qrcode); }; s.onerror = function () { qrLib = null; rej(new Error('QR')); };
      document.head.appendChild(s);
    });
    return qrLib;
  }
  function qrSvg(text) { return loadQR().then(function (q) { var c = q(0, 'M'); c.addData(text); c.make(); return c.createSvgTag(8, 2); }); }
  function shortUrl(u) { return u.replace(/^https?:\/\//, ''); }
  function since(ts) {
    if (!ts) return '–';
    var d = new Date(ts), now = new Date();
    var days = Math.floor((new Date(now.toDateString()) - new Date(d.toDateString())) / 86400000);
    if (days <= 0) return 'heute';
    if (days === 1) return 'gestern';
    if (days < 7) return 'vor ' + days + ' Tagen';
    return d.toLocaleDateString('de-CH');
  }
  var toastTimer;
  function toast(msg) {
    var t = document.getElementById('toast');
    t.textContent = msg; t.classList.add('show');
    clearTimeout(toastTimer); toastTimer = setTimeout(function () { t.classList.remove('show'); }, 3200);
  }
  function errMsg(e) {
    var m = (e && e.message) || String(e);
    if (/Invalid login/i.test(m)) return 'E-Mail oder Passwort stimmt nicht.';
    if (/Failed to fetch|NetworkError|Load failed/i.test(m)) return 'Keine Verbindung. Bitte das Internet prüfen.';
    if (/kids_class_name/i.test(m)) return 'Diesen Namen gibt es in der Klasse schon.';
    if (/classes_code/i.test(m)) return 'Dieser Klassencode ist schon vergeben.';
    if (/Password should be|password.*characters/i.test(m)) return 'Das Passwort ist zu kurz (mindestens 8 Zeichen).';
    if (/JWT|session/i.test(m)) return 'Bitte neu anmelden.';
    return m;
  }

  // Bildpasswort-Symbole
  var SYM = {
    sonne: { label: 'Sonne', bg: '#FFE7A3', p: '<circle cx="12" cy="12" r="4.5"/><path d="M12 2v2.5M12 19.5V22M2 12h2.5M19.5 12H22M4.9 4.9l1.8 1.8M17.3 17.3l1.8 1.8M4.9 19.1l1.8-1.8M17.3 6.7l1.8-1.8"/>' },
    mond:  { label: 'Mond',  bg: '#DCE3F5', p: '<path d="M20 15A8.5 8.5 0 1 1 9 4a7 7 0 0 0 11 11z"/>' },
    baum:  { label: 'Baum',  bg: '#D5EBC9', p: '<path d="M12 22v-6"/><path d="M12 2l6 8h-3l4 6H5l4-6H6z"/>' },
    fisch: { label: 'Fisch', bg: '#CBE6EE', p: '<path d="M3 12c3-5 9-6 13-3l5-3v12l-5-3c-4 3-10 2-13-3z"/><circle cx="8" cy="11" r=".9" fill="#1B2A3D"/>' },
    haus:  { label: 'Haus',  bg: '#E1E8F8', p: '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-5h4v5"/>' },
    stern: { label: 'Stern', bg: '#E4F5EC', p: '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/>' }
  };
  var SYM_IDS = Object.keys(SYM);
  function symSvg(id, size) {
    return '<svg width="' + size + '" height="' + size + '" viewBox="0 0 24 24" fill="none" stroke="#1B2A3D" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + SYM[id].p + '</svg>';
  }
  function randPw(not) {
    var p;
    do { var a = SYM_IDS.slice(), o = []; for (var i = 0; i < 3; i++) o.push(a.splice(rnd(a.length), 1)[0]); p = o.join(','); } while (p === not);
    return p;
  }
  function pwLabel(pw) { return pw.split(',').map(function (s) { return SYM[s] ? SYM[s].label : s; }).join(', '); }

  // Farben
  var FACH_COL = { 'Mathematik': '#CFDDF0', 'Englisch': '#F28B82', 'Deutsch': '#E9D7E4', 'NMG': '#F3DDB8', 'Französisch': '#D6E8F5' };
  var TINTS = ['#D5EBC9', '#E1E8F8', '#E3D5F0', '#F3E2A6', '#CBE6EE', '#E4F5EC'];
  var FACH_SHORT = { 'Mathematik': 'Mathe' };
  function fachShort(f) { return FACH_SHORT[f] || f; }
  // Knopf-Farbe pro Fach (dunklerer Ton der Fachfarbe); sonst das normale Blau
  var FACH_BTN = { 'Englisch': '#CC5046' };
  function fachBtn(f) { return FACH_BTN[f] ? 'background:' + FACH_BTN[f] + ';' : ''; }
  function isWall(g) { return /wandtafel/i.test((g.stufe || '') + ' ' + (g.fach || '') + ' ' + (g.thema || '')); }
  function fachColor(f) { if (/wandtafel/i.test(f || '')) return '#E2E5EA'; return FACH_COL[f] || TINTS[hash(f) % TINTS.length]; }
  var KID_TINTS = ['#F6C9A8', '#CFDDF0', '#CFE5C6', '#D3F1E4', '#E3D5F0', '#F3E2A6'];
  function kidColor(name) { return KID_TINTS[hash(name) % KID_TINTS.length]; }
  var PALETTE = [['#2F5E9E', 'Blau'], ['#1E6F7A', 'Petrol'], ['#2E7D4F', 'Grün'], ['#C46A1C', 'Orange'], ['#C0473C', 'Rot'],
    ['#B83A78', 'Pink'], ['#8A4F7D', 'Violett'], ['#7A5634', 'Braun'], ['#E8B710', 'Gelb'], ['#6BB3E8', 'Hellblau'], ['#86C66E', 'Hellgrün']];
  var COLS = [
    { id: 'helfen', label: 'Ich kann helfen', ic: '<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/>' },
    { id: 'klar', label: 'Ich komme gut klar', ic: '<path d="M5 12.5l4.5 4.5L19 7.5"/>' },
    { id: 'frage', label: 'Ich habe eine Frage', ic: '<path d="M9 9a3 3 0 1 1 4.5 2.6c-1 .6-1.5 1.3-1.5 2.4"/><path d="M12 18h.01"/>' }
  ];
  var COL_LABEL = { helfen: 'Ich kann helfen', klar: 'Ich komme gut klar', frage: 'Ich habe eine Frage' };

  function ic(paths, size, color, sw) {
    return '<svg width="' + (size || 18) + '" height="' + (size || 18) + '" viewBox="0 0 24 24" fill="none" stroke="' + (color || 'currentColor') +
      '" stroke-width="' + (sw || 2.2) + '" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + paths + '</svg>';
  }
  var I = {
    logo: '<svg width="38" height="38" viewBox="0 0 40 40" aria-hidden="true"><rect x="5" y="2" width="30" height="36" rx="6" fill="#2B6CB0"/><rect x="8.5" y="6" width="23" height="26" rx="2.5" fill="#DCEEFC"/><circle cx="20" cy="35" r="1.5" fill="#DCEEFC"/><path d="M20 10.5l2.4 4.9 5.4.8-3.9 3.8.9 5.4-4.8-2.6-4.8 2.6.9-5.4-3.9-3.8 5.4-.8z" fill="#A8E6CF" stroke="#2E8B6A" stroke-width="1" stroke-linejoin="round"/></svg>',
    back: '<path d="M15 18l-6-6 6-6"/>',
    play: '<path d="M7 4v16l13-8z" fill="currentColor" stroke="none"/>',
    trash: '<path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13M10 11v6M14 11v6"/>',
    star: '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/>',
    print: '<path d="M6 9V3h12v6M6 18H4a1 1 0 0 1-1-1v-6a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v6a1 1 0 0 1-1 1h-2"/><rect x="6" y="14" width="12" height="7" rx="1"/>',
    board: '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M9 4v12M15 4v12M8 20h8"/>',
    check: '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    reset: '<path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/>',
    sort: '<path d="M7 4v16M3 8l4-4 4 4"/><path d="M17 20V4M13 16l4 4 4-4"/>',
    helpers: '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c.8-3.6 3.4-5.5 6.5-5.5s5.7 1.9 6.5 5.5"/><path d="M17 11l2 2 4-4"/>'
  };

  // Zeichnen mit Fokus-Erhalt
  function paint(html) {
    var a = document.activeElement, id = a && a.id, s = null, e = null;
    try { s = a.selectionStart; e = a.selectionEnd; } catch (x) {}
    app.innerHTML = html;
    if (id) {
      var n = document.getElementById(id);
      if (n) { n.focus(); try { if (s != null) n.setSelectionRange(s, e); } catch (x) {} }
    }
    if (app.querySelector('.matrix')) fitBoard();
  }
  // Tafel: Namen so gross wie möglich, aber alles ohne Scrollen sichtbar
  function fitBoard() {
    var m = app.querySelector('.matrix'); if (!m) return;
    var cells = m.querySelectorAll('.cell'), fs = Math.min(26, Math.max(14, Math.round(window.innerHeight / 40)));
    // jedes Feld einzeln: nur volle Felder bekommen kleinere Namen
    Array.prototype.forEach.call(cells, function (c) {
      var f = fs; c.style.setProperty('--fs', f + 'px');
      while (f > 9 && (c.scrollHeight > c.clientHeight + 1 || c.scrollWidth > c.clientWidth + 1)) { f--; c.style.setProperty('--fs', f + 'px'); }
    });
  }
  window.addEventListener('resize', function () { if (app.querySelector('.matrix')) fitBoard(); });

  // Aktionen (Klicks, Formulare, Eingaben)
  var ACT = {};
  function run(fn, el, ev) {
    if (!fn) return;
    Promise.resolve().then(function () { return fn(el, ev); }).catch(function (err) { console.error(err); toast(errMsg(err)); });
  }
  document.addEventListener('click', function (e) {
    var el = e.target.closest('[data-a]');
    if (!el || el.tagName === 'FORM') return;
    if (el.tagName === 'A' && !el.getAttribute('href')) e.preventDefault();
    run(ACT[el.dataset.a], el, e);
  });
  document.addEventListener('submit', function (e) {
    var f = e.target.closest('form[data-a]'); if (!f) return;
    e.preventDefault(); run(ACT[f.dataset.a], f, e);
  });
  document.addEventListener('change', function (e) { var el = e.target.closest('[data-change]'); if (el) run(ACT[el.dataset.change], el, e); });
  document.addEventListener('input', function (e) { var el = e.target.closest('[data-input]'); if (el) run(ACT[el.dataset.input], el, e); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { if (PL) closePlayer(); else closeOverlays(); } });

  var confirmTimer;
  function armed(key) {
    if (UI.confirm === key) { UI.confirm = null; return true; }
    UI.confirm = key; clearTimeout(confirmTimer);
    confirmTimer = setTimeout(function () { if (UI.confirm === key) { UI.confirm = null; rerender(); } }, 4000);
    return false;
  }
  var UI = { confirm: null, view: null };
  function rerender() { if (UI.view === 'teacher') T.render(); else if (UI.view === 'kid') K.render(); }

  // Overlays
  function overlay(html) {
    closeOverlays();
    var o = document.createElement('div'); o.className = 'overlay'; o.innerHTML = html;
    o.addEventListener('click', function (e) { if (e.target === o) closeOverlays(); });
    document.body.appendChild(o);
    var f = o.querySelector('input,button'); if (f) f.focus();
    return o;
  }
  function closeOverlays() { Array.prototype.forEach.call(document.querySelectorAll('.overlay'), function (o) { o.remove(); }); }
  ACT.closeOverlay = function () { closeOverlays(); };

  // Spiel-Player (Spiel läuft abgeschirmt in einem iframe)
  // Läuft im Spiel (iframe): Speicher nachbilden, gespeicherten Stand laden, Meldungen an das Portal
  function shimMain(seed, aw) {
    function send(m) { try { m.knobelnest = 1; parent.postMessage(m, '*'); } catch (e) {} }
    function mem(init, onchange) {
      var m = {}, k;
      if (init && typeof init === 'object') for (k in init) if (typeof init[k] === 'string') m[k] = init[k];
      function ch() { if (onchange) onchange(m); }
      return {
        getItem: function (k) { k = String(k); return Object.prototype.hasOwnProperty.call(m, k) ? m[k] : null; },
        setItem: function (k, v) { k = String(k); v = String(v); if (m[k] === v) return; m[k] = v; ch(); },
        removeItem: function (k) { k = String(k); if (Object.prototype.hasOwnProperty.call(m, k)) { delete m[k]; ch(); } },
        clear: function () { m = {}; ch(); },
        key: function (i) { return Object.keys(m)[i] || null; },
        get length() { return Object.keys(m).length; }
      };
    }
    try { Object.defineProperty(window, 'localStorage', { value: mem(seed, function (m) { send({ type: 'store', data: m }); }), configurable: true }); } catch (e) {}
    try { window.sessionStorage.getItem('x'); } catch (e) { try { Object.defineProperty(window, 'sessionStorage', { value: mem(), configurable: true }); } catch (_) {} }
    window.knobelnest = {
      answer: function (ok) { send({ type: 'answer', ok: !!ok }); },
      progress: function (done, total) { send({ type: 'progress', done: +done, total: +total }); },
      level: function (n) { send({ type: 'level', level: n == null ? null : String(n) }); },
      round: function () { send({ type: 'round' }); },
      award: function (a) { try { send({ type: 'award', award: JSON.parse(JSON.stringify(a || {})) }); } catch (e) {} }
    };
    // Sterne pro Level lesen: knobelnest.sterne('Mittel · Ablesen') -> { have, max }; bei Änderung kommt das Ereignis 'knobelnest-sterne'
    var AW = aw && typeof aw === 'object' ? aw : { lv: {}, max: 0 };
    window.knobelnest.sterne = function (k) { return { have: +((AW.lv || {})[k]) || 0, max: +AW.max || 0 }; };
    window.knobelnest.alle = function () { return { lv: AW.lv || {}, max: +AW.max || 0 }; };
    window.addEventListener('message', function (e) {
      if (e.source !== parent || !e.data || !e.data.knobelnestAward) return;
      AW = e.data.knobelnestAward;
      try { window.dispatchEvent(new Event('knobelnest-sterne')); } catch (x) {}
    });
    if (!window.__report) window.__report = function (ok) { send({ type: 'answer', ok: !!ok }); };
  }
  function prepare(html, seed) {
    seed = seed || {};
    var aw = seed.award || { lv: {}, max: starMax(starCfg(html)) };
    var J = function (v) { return JSON.stringify(v == null ? null : v).replace(/</g, '\\u003c'); };
    var tag = '<script>(' + shimMain.toString() + ')(' + J(seed.store) + ',' + J(aw) + ');<\/script>';
    var m = /<head[^>]*>/i.exec(html);
    return m ? html.slice(0, m.index + m[0].length) + tag + html.slice(m.index + m[0].length) : tag + html;
  }
  var PL = null;
  function openPlayer(title, html, onMsg, onClose, seed) {
    closePlayer();
    var p = document.createElement('div');
    p.className = 'player'; p.setAttribute('role', 'dialog'); p.setAttribute('aria-label', title);
    p.innerHTML = '<div class="player-bar"><button class="btn sm" data-a="closePlayer">' + ic(I.back) + ' Zurück</button><b>' + h(title) +
      '</b><button class="btn sm" data-a="playerFull">Vollbild</button></div>';
    var f = document.createElement('iframe');
    f.setAttribute('sandbox', 'allow-scripts allow-forms allow-modals allow-popups allow-downloads allow-pointer-lock');
    f.setAttribute('allow', 'fullscreen; autoplay');
    f.title = title;
    f.srcdoc = prepare(html, seed);
    var bar = document.createElement('div'); bar.className = 'starbar'; bar.hidden = true; bar.setAttribute('aria-live', 'polite');
    p.querySelector('.player-bar').insertBefore(bar, p.querySelector('[data-a="playerFull"]'));
    p.appendChild(f); document.body.appendChild(p); document.body.style.overflow = 'hidden';
    PL = { el: p, frame: f, bar: bar, onMsg: onMsg, onClose: onClose };
  }
  function closePlayer() {
    if (!PL) return; var x = PL; PL = null;
    try { if (document.fullscreenElement) document.exitFullscreen(); else if (document.webkitFullscreenElement) document.webkitExitFullscreen(); } catch (e) {}
    x.el.remove(); document.body.style.overflow = '';
    if (x.onClose) x.onClose();
  }
  ACT.closePlayer = function () { closePlayer(); };
  ACT.playerFull = function () { if (!PL) return; var e = PL.el; try { (e.requestFullscreen || e.webkitRequestFullscreen).call(e); } catch (x) {} };
  window.addEventListener('message', function (e) {
    if (!PL || e.source !== PL.frame.contentWindow) return;
    var d = e.data; if (!d || typeof d !== 'object') return;
    if (PL.onMsg) PL.onMsg(d);
  });

  // Router
  var timers = [];
  function every(ms, fn) { timers.push(setInterval(fn, ms)); }
  function stopTimers() { timers.forEach(clearInterval); timers = []; }
  function route() {
    stopTimers(); closeOverlays(); closePlayer(); UI.confirm = null;
    var hs = location.hash || '';
    if (/error_description=/.test(hs)) return linkError(hs);
    if (/access_token=|type=recovery/.test(hs)) { setTimeout(function () { if (/access_token=/.test(location.hash) && UI.view !== 'recovery') { location.hash = '#/'; } }, 4000); return; }
    if (hs.indexOf('#/klasse') === 0) return K.start();
    var m = hs.match(/^#\/wandtafel\/([0-9a-f-]{36})(\/embed)?/);
    if (m) return W.start(m[1], !!m[2]);
    var mf = hs.match(/^#\/tagesfolie\/([0-9a-f-]{36})/);
    if (mf) return F.start(mf[1]);
    var ms = hs.match(/^#\/sprint\/([0-9a-f-]{36})/);
    if (ms) return S.start(ms[1]);
    return T.start();
  }

  // ===================================================================
  // Tafel (gemeinsam für Kinder und Wandtafel)
  // ===================================================================
  function board(t, mode) {
    var s = t.state || { subjects: [], kids: [], entries: [] }, me = t.me;
    var kidName = {}; s.kids.forEach(function (k) { kidName[k.id] = k.name; });
    var entry = {}; s.entries.forEach(function (e) { entry[e.kid_id] = e; });
    var mine = me ? entry[me] : null;
    var subjName = {}; s.subjects.forEach(function (x) { subjName[x.id] = x.name; });
    var kid = mode === 'kid', emb = mode === 'embed';
    var out = emb ? '<div class="board-head"><div class="stack" style="gap:0"><span class="kick">Arbeitsstand · Klasse ' + h(s.class_name || '') + '</span><h1>Wer kann wem helfen?</h1></div></div>' : '<div class="board-head"><div class="stack" style="gap:6px"><span class="kick">Arbeitsstand · Klasse ' + h(s.class_name || '') + '</span>' +
      '<h1>' + (kid ? 'Wo stehst du gerade?' : 'Wer kann wem helfen?') + '</h1>' +
      '<p>' + (kid ? 'Tippe beim Fach auf das Feld, das zu dir passt. Dein Name steht immer nur an einem Ort.' : 'Hast du eine Frage? Schau, wer im gleichen Fach helfen kann.') + '</p></div>' +
      '<div class="row">' + (kid ? '<button class="board-btn" data-a="kBack">' + ic(I.back) + ' Zurück</button>' :
        '<button class="board-btn" data-a="wallFull">Vollbild</button><a class="board-btn" href="#/">Zum Portal</a>') + '</div></div>';
    if (kid) {
      out += '<div class="mine"><b>Du (' + h(kidName[me] || '') + '):</b><span>' +
        (mine && subjName[mine.subject_id] ? h(subjName[mine.subject_id]) + ' · ' + COL_LABEL[mine.col] : 'Du stehst noch nicht auf der Tafel. Wähle unten dein Fach und die passende Spalte.') + '</span>' +
        (mine ? '<button class="board-btn" style="margin-left:auto;min-height:36px" data-a="tOff">Namen wegnehmen</button>' : '') +
        (function () {
          if (!mine || mine.col !== 'frage') return '';
          var hs = s.entries.filter(function (e) { return e.subject_id === mine.subject_id && e.col === 'helfen'; }).map(function (e) { return kidName[e.kid_id]; });
          return hs.length ? '<span class="help">' + ic(I.helpers, 22, '#1F3F6B') + '<span><b>Diese Kinder können dir helfen:</b> ' + h(hs.join(', ')) + '</span></span>' : '';
        })() + '</div>';
    }
    if (!s.subjects.length) out += '<div class="subject"><p class="muted">Die Lehrperson hat noch keine Fächer für die Tafel ausgewählt.</p></div>';
    else {
      // Alles auf einen Blick: Zeilen = Fächer, Spalten = die drei Stände
      var N = s.subjects.length, maxIn = 1;
      s.subjects.forEach(function (sub) { COLS.forEach(function (c) {
        var n = s.entries.filter(function (e) { return e.subject_id === sub.id && e.col === c.id; }).length; if (n > maxIn) maxIn = n; }); });
      // Schriftgrösse je nach Anzahl Fächer und Namen pro Feld
      var fs = 'clamp(11px, calc((100dvh - ' + (kid ? 250 : 200) + 'px) / ' + N + ' / ' + (maxIn > 8 ? 4.6 : maxIn > 4 ? 3.4 : 2.4) + '), 22px)';
      out += '<div class="matrix" style="--rows:' + N + ';--fs-s:clamp(14px, calc((100dvh - 200px) / ' + N + ' / 3), 26px)">' +
        '<div class="mx-h blank"></div>' + COLS.map(function (c) {
          return '<div class="mx-h c-' + c.id + '"><span class="dot">' + ic(c.ic, 18, '#fff', 2.4) + '</span><span class="lbl">' + c.label + '</span></div>'; }).join('');
      s.subjects.forEach(function (sub) {
        var inSub = s.entries.filter(function (e) { return e.subject_id === sub.id; });
        out += '<div class="mx-subj"><i style="background:' + h(sub.color) + '"></i><span>' + h(sub.name) + '<small>' + (inSub.length === 1 ? '1 Kind' : inSub.length + ' Kinder') + '</small></span></div>';
        COLS.forEach(function (c) {
          var names = inSub.filter(function (e) { return e.col === c.id; });
          var here = mine && mine.subject_id === sub.id && mine.col === c.id;
          var tags = names.map(function (e) {
            var n = kidName[e.kid_id] || '';
            return '<span class="tag' + (kid && e.kid_id === me ? ' me' : '') + '"><span class="ini" style="background:' + kidColor(n) + '">' + h(n.charAt(0)) + '</span>' + h(n) + '</span>';
          }).join('');
          if (kid && !here) out += '<button class="cell c-' + c.id + '" data-a="tSet" data-s="' + sub.id + '" data-c="' + c.id + '" aria-label="' + h(sub.name) + ': ' + c.label + '">' + tags +
            '<span class="put">' + (mine ? 'hierhin' : 'Hier eintragen') + '</span></button>';
          else out += '<div class="cell c-' + c.id + (here ? ' here' : '') + '">' + tags + '</div>';
        });
      });
      out += '</div>';
    }
    var missing = s.kids.filter(function (k) { return !entry[k.id] || !subjName[entry[k.id].subject_id]; }).map(function (k) { return k.name; });
    if (!kid && !emb) out += '<p style="flex:none;margin:0;color:#3D5A7A;font-size:16px">' + (missing.length ? 'Noch nicht auf der Tafel: ' + h(missing.join(', ')) : 'Alle Kinder stehen auf der Tafel.') + '</p>';
    return '<div class="board' + (kid ? '' : ' wall') + (emb ? ' embed' : '') + '"><div class="board-in">' + out + '</div></div>';
  }


  // ===================================================================
  // Klassen-Sprint: Lehrperson zeigt das Rennen, alle Kinder rechnen am iPad
  // ===================================================================
  var SPR_GOALS = [10, 15, 20, 30];
  var SPR_MODES = [['mal', 'Malrechnungen', '3 · 7 = ?'], ['luecke', 'Fehlende Zahl', '3 · ? = 21'], ['div', 'Division', '21 : 3 = ?'], ['mix', 'Gemischt', 'alles durcheinander']];
  function sprTask(rows, last, mode) {
    var a, b, p, m, key, q, ans, g = 0, gap = '<span class="gap">?</span>';
    rows = rows && rows.length ? rows : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    do {
      m = mode === 'mix' ? ['mal', 'luecke', 'div'][Math.floor(Math.random() * 3)] : (mode || 'mal');
      a = rows[Math.floor(Math.random() * rows.length)]; b = 1 + Math.floor(Math.random() * 10); p = a * b;
      if (m === 'div') { q = p + ' : ' + a + ' = ' + gap; ans = b; key = 'd' + p + ':' + a; }
      else if (m === 'luecke') {
        if (Math.random() < .5) { q = a + ' · ' + gap + ' = ' + p; } else { q = gap + ' · ' + a + ' = ' + p; }
        ans = b; key = 'l' + a + 'x' + b;
      } else { if (Math.random() < .5) { q = a + ' · ' + b + ' = ' + gap; } else { q = b + ' · ' + a + ' = ' + gap; } ans = p; key = 'm' + a + 'x' + b; }
    } while (key === last && g++ < 20);
    return { q: q, ans: ans, full: q.replace(gap, '<b>' + ans + '</b>'), key: key };
  }
  function sprModeName(m) { var x = SPR_MODES.filter(function (y) { return y[0] === (m || 'mal'); })[0]; return x ? x[1] : 'Malrechnungen'; }
  function medal(n) { return n === 1 ? '🥇' : n === 2 ? '🥈' : n === 3 ? '🥉' : n + '.'; }
  var S = {
    start: async function (cid) {
      UI.view = 'sprint';
      var sess = await DB.session(); if (!sess) { location.hash = '#/'; return; }
      S.cid = cid; S.race = null; S.runs = []; S.setup = S.setup || LS.get('kn_sprint') || { rows: [2, 3, 4, 5, 6, 7, 8, 9, 10], goal: 10 };
      app.innerHTML = '<p class="boot">Sprint wird geladen …</p>';
      try {
        var cls = (await DB.listClasses()).filter(function (c) { return c.id === cid; })[0];
        S.cls = cls; S.kids = await DB.listKids(cid);
        var r = await DB.raceLatest(cid); S.race = r && r.status !== 'done' ? r : null;
      } catch (e) { paint('<div class="main"><div class="card stack"><h2>Sprint nicht verfügbar</h2><p>' + h(errMsg(e)) + '</p><a class="btn" href="#/">Zum Portal</a></div></div>'); return; }
      S.offset = 0; S.render(); S.poll();
      every(1000, function () { if (!document.hidden) S.poll(); });
      every(250, function () { if (S.race && S.race.status === 'run' && S.countLeft() > -1) S.render(); });
    },
    poll: async function () {
      if (!S.race || S.busy) return; S.busy = true;
      try {
        var r = await DB.raceGet(S.race.id); S.race = r;
        S.runs = await DB.raceRuns(r.id);
        // alle fertig -> Rangliste
        if (r.status === 'run' && S.runs.length && S.runs.every(function (x) { return x.finished_at; })) { await DB.raceEnd(r.id); S.race.status = 'done'; }
      } catch (e) { console.warn(e); }
      S.busy = false; S.render();
    },
    countLeft: function () { if (!S.race || !S.race.starts_at) return -1; return Math.ceil((Date.parse(S.race.starts_at) - S.offset - Date.now()) / 1000); },
    render: function () {
      var cls = S.cls || { name: '' }, r = S.race, kidName = {}; (S.kids || []).forEach(function (k) { kidName[k.id] = k.name; });
      var head = '<div class="spr-head"><div><span class="kick">Klassen-Sprint · Klasse ' + h(cls.name) + '</span><h1>' +
        (!r ? 'Neuer Sprint' : r.status === 'wait' ? 'Auf die Plätze …' : r.status === 'run' ? 'Los geht\'s!' : 'Zieleinlauf') + '</h1></div><div class="row">' +
        (r && r.status === 'wait' ? '<button class="btn primary big" data-a="sGo"' + (S.runs.length ? '' : ' disabled') + '>▶ Start</button><button class="btn" data-a="sCancel">Abbrechen</button>' : '') +
        (r && r.status === 'run' ? '<button class="btn" data-a="sEnd">Beenden</button>' : '') +
        (r && r.status === 'done' ? '<button class="btn primary" data-a="sNew">Neuer Sprint</button>' : '') +
        '<button class="btn" data-a="wallFull">Vollbild</button><a class="btn" href="#/">Zum Portal</a></div></div>';
      var body = '';
      if (!r) {
        body = '<div class="spr-setup card stack"><p class="lead">Alle Kinder rechnen gleichzeitig an ihrem iPad. Jede richtige Antwort bringt ihren Läufer einen Schritt weiter. Hier vorne sieht die ganze Klasse das Rennen.</p>' +
          '<div><p class="h3">Was wird gerechnet?</p><div class="chips">' + SPR_MODES.map(function (m) {
            return '<button class="chip mode" aria-pressed="' + ((S.setup.mode || 'mal') === m[0]) + '" data-a="sMode" data-m="' + m[0] + '"><b>' + m[1] + '</b><small>' + m[2] + '</small></button>'; }).join('') + '</div></div>' +
          '<div><p class="h3">Welche Reihen?</p><div class="chips"><button class="chip" aria-pressed="' + (S.setup.rows.length === 10) + '" data-a="sRow" data-n="all">Alle Reihen</button>' + [1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(function (n) {
            return '<button class="chip" aria-pressed="' + (S.setup.rows.length < 10 && S.setup.rows.indexOf(n) >= 0) + '" data-a="sRow" data-n="' + n + '">' + n + '</button>'; }).join('') + '</div></div>' +
          '<div><p class="h3">Länge der Strecke</p><div class="chips">' + SPR_GOALS.map(function (n) {
            return '<button class="chip" aria-pressed="' + (S.setup.goal === n) + '" data-a="sGoal" data-n="' + n + '">' + n + ' Aufgaben</button>'; }).join('') + '</div></div>' +
          '<button class="btn primary big" data-a="sOpen"' + (S.setup.rows.length ? '' : ' disabled') + '>Sprint öffnen</button></div>';
        return paint('<div class="spr">' + head + body + '</div>');
      }
      var goal = (r.settings && r.settings.goal) || 10, runs = S.runs.slice(), byKid = {};
      runs.forEach(function (x) { byKid[x.kid_id] = x; });
      var fin = runs.filter(function (x) { return x.finished_at; }).sort(function (a, b) { return a.finished_at < b.finished_at ? -1 : 1; });
      var place = {}; fin.forEach(function (x, i) { place[x.kid_id] = i + 1; });
      if (r.status === 'wait') {
        body = '<div class="spr-info">Kinder: einloggen und auf <b>«🏃 Sprint»</b> tippen · Code <b>' + h(cls.code || '') + '</b> · ' +
          runs.length + ' von ' + S.kids.length + ' Kindern sind bereit · ' + sprModeName(r.settings && r.settings.mode) + ', ' +
          (r.settings && r.settings.rows && r.settings.rows.length < 10 ? 'Reihen ' + r.settings.rows.join(', ') : 'alle Reihen') + ', ' + goal + ' Aufgaben</div>';
      }
      var list = r.status === 'wait' ? S.kids.map(function (k) { return { kid_id: k.id, pos: 0, wait: !byKid[k.id] }; }) : runs;
      list.sort(function (a, b) { return (kidName[a.kid_id] || '').localeCompare(kidName[b.kid_id] || ''); });
      if (r.status === 'done') {
        var rest = runs.filter(function (x) { return !x.finished_at; }).sort(function (a, b) { return b.pos - a.pos; });
        var order = fin.concat(rest);
        body = '<div class="spr-result"><div class="podium">' + [1, 0, 2].map(function (i) {
          var x = order[i]; if (!x) return '<div class="pod p' + (i + 1) + ' empty"></div>';
          return '<div class="pod p' + (i + 1) + '"><span class="m">' + medal(i + 1) + '</span><b>' + h(kidName[x.kid_id] || '') + '</b><span>' + (x.finished_at ? 'im Ziel' : x.pos + ' von ' + goal) + '</span></div>';
        }).join('') + '</div><ol class="ranking" start="4">' + order.slice(3).map(function (x) {
          return '<li><b>' + h(kidName[x.kid_id] || '') + '</b> · ' + (x.finished_at ? 'im Ziel' : x.pos + ' von ' + goal) + '</li>'; }).join('') + '</ol></div>';
        return paint('<div class="spr">' + head + body + '</div>');
      }
      var n = Math.max(1, list.length);
      body += '<div class="lanes" style="--n:' + n + '">' + list.map(function (x, i) {
        var nm = kidName[x.kid_id] || '', p = Math.min(1, (x.pos || 0) / goal), pl = place[x.kid_id];
        return '<div class="lane' + (x.wait ? ' waiting' : '') + '"><span class="lname">' + h(nm) + '</span><div class="ltrack"><span class="lfinish"></span>' +
          '<span class="runner" style="left:calc(' + (p * 100) + '% - ' + (p * 2.4) + 'em);background:' + kidColor(nm) + '">' + h(nm.charAt(0)) + '</span></div>' +
          (pl ? '<span class="lplace">' + medal(pl) + '</span>' : '<span class="lscore">' + (x.wait ? '…' : (x.pos || 0) + '/' + goal) + '</span>') + '</div>';
      }).join('') + '</div>';
      var left = S.countLeft();
      if (r.status === 'run' && left > 0) body += '<div class="spr-count">' + left + '</div>';
      paint('<div class="spr">' + head + body + '</div>');
    }
  };
  ACT.sMode = function (el) { S.setup.mode = el.dataset.m; LS.set('kn_sprint', S.setup); S.render(); };
  ACT.sRow = function (el) {
    if (el.dataset.n === 'all') { S.setup.rows = S.setup.rows.length === 10 ? [] : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]; LS.set('kn_sprint', S.setup); return S.render(); }
    var n = +el.dataset.n; if (S.setup.rows.length === 10) S.setup.rows = [];
    var i = S.setup.rows.indexOf(n); if (i >= 0) S.setup.rows.splice(i, 1); else S.setup.rows.push(n); S.setup.rows.sort(function (a, b) { return a - b; }); LS.set('kn_sprint', S.setup); S.render(); };
  ACT.sGoal = function (el) { S.setup.goal = +el.dataset.n; LS.set('kn_sprint', S.setup); S.render(); };
  ACT.sOpen = async function () { S.race = await DB.raceCreate(S.cid, { rows: S.setup.rows, goal: S.setup.goal, mode: S.setup.mode || 'mal' }); S.runs = []; S.render(); };
  ACT.sGo = async function () { var r = await DB.raceStart(S.race.id); S.offset = Date.parse(r.now) - Date.now(); S.race.status = 'run'; S.race.starts_at = r.starts_at; S.render(); };
  ACT.sEnd = async function () { await DB.raceEnd(S.race.id); S.race.status = 'done'; await S.poll(); };
  ACT.sCancel = async function () { await DB.raceEnd(S.race.id); S.race = null; S.runs = []; S.render(); };
  ACT.sNew = function () { S.race = null; S.runs = []; S.render(); };

  // ===================================================================
  // Wandtafel (Lehrperson, für den Beamer)
  // ===================================================================
  var W = {
    start: async function (cid, embed) {
      UI.view = 'wall';
      var s = await DB.session();
      if (!s) { location.hash = '#/'; return; }
      app.innerHTML = '<p class="boot">Tafel wird geladen …</p>';
      async function load() {
        try { paint(board(await DB.tafelTeacher(cid), embed ? 'embed' : 'wall')); }
        catch (e) { paint('<div class="main"><div class="card stack"><h2>Tafel nicht verfügbar</h2><p>' + h(errMsg(e)) + '</p><a class="btn" href="#/">Zum Portal</a></div></div>'); stopTimers(); }
      }
      await load();
      every(embed ? 3000 : 5000, function () { if (!document.hidden) load(); });
    }
  };

  // ===================================================================
  // Tagesfolie (Lehrperson, an der Wandtafel). Läuft als eigene Seite tagesfolie.html im Rahmen;
  // Klassenliste, Speicher und Arbeitsstand-Tafel kommen von hier.
  // ===================================================================
  var F = {
    start: async function (cid) {
      UI.view = 'folie';
      var s = await DB.session();
      if (!s) { location.hash = '#/'; return; }
      app.innerHTML = '<p class="boot">Tagesfolie wird geladen …</p>';
      var cls, kids;
      var me = null, tpl = null;
      try {
        cls = (await DB.listClasses()).filter(function (c) { return c.id === cid; })[0]; kids = await DB.listKids(cid);
        me = await DB.me(); try { tpl = await DB.sharedGet('tagesfolie-vorlage'); } catch (e2) { tpl = null; }
      }
      catch (e) { paint('<div class="main"><div class="card stack"><h2>Tagesfolie nicht verfügbar</h2><p>' + h(errMsg(e)) + '</p><a class="btn" href="#/">Zum Portal</a></div></div>'); return; }
      var uid = s.user.id, base = location.href.split('#')[0];
      var doc = function (id) {
        return {
          get: async function () { var d = await DB.storeGet(id); return { exists: d != null, data: function () { return d; } }; },
          set: async function (v) { await DB.storeSet(id, JSON.parse(JSON.stringify(v))); },
          delete: async function () { await DB.storeDel(id); }
        };
      };
      window.knTagesfolie = {
        uid: uid, className: cls ? cls.name : '', isAdmin: !!(me && me.is_admin), template: tpl,
        saveTemplate: function (t) { return DB.sharedSet('tagesfolie-vorlage', JSON.parse(JSON.stringify(t))); },
        roster: (kids || []).map(function (k) { return k.name; }),
        boardUrl: base + '#/wandtafel/' + cid + '/embed',
        back: function () { if (document.fullscreenElement && document.exitFullscreen) document.exitFullscreen().catch(function () {}); location.hash = '#/'; },
        claude: {
          use: async function (name) {
            if (name === 'db') return { collection: function () { return { doc: doc }; } };
            if (name === 'user') return { id: async function () { return uid; } };
            if (name === 'assets') return { upload: async function (blob) { return { url: await DB.storeUpload(blob) }; } };
            return null;
          }
        }
      };
      paint('<div class="folie"><iframe src="tagesfolie.html?v=' + ('26') + '" title="Tagesfolie" allow="fullscreen"></iframe></div>');
    }
  };
  ACT.wallFull = function () { if (document.documentElement.requestFullscreen) document.documentElement.requestFullscreen(); };

  // ===================================================================
  // Lehrpersonen
  // ===================================================================
  var T = {
    me: null, classes: [], cls: null, games: [], rel: new Set(), kids: [], subjects: [],
    progress: null, progressBusy: false, tafel: null, tafelBusy: false,
    tab: LS.get('kn_tab') || 'spiele', fach: 'alle', closed: LS.get('kn_closed') || {}, q: '', pfilter: 'alle',
    fresh: new Set(), editColor: null, newColor: '#2E7D4F', loginErr: '', loginInfo: '',
    admin: { teachers: null, tg: [], open: null, form: null }
  };

  T.start = async function () {
    UI.view = 'teacher';
    var s = await DB.session();
    if (!s) return T.renderLogin();
    app.innerHTML = '<p class="boot">Wird geladen …</p>';
    T.me = await DB.me();
    T.classes = await DB.listClasses();
    var saved = LS.get('kn_cls');
    T.cls = (T.classes.filter(function (c) { return c.id === saved; })[0] || T.classes[0] || {}).id || null;
    T.games = await DB.listGames();
    await T.loadClass();
    T.render();
  };
  T.loadClass = async function () {
    T.progress = null; T.tafel = null; T.fresh = new Set();
    if (!T.cls) { T.rel = new Set(); T.kids = []; T.subjects = []; return; }
    var r = await Promise.all([DB.listReleases(T.cls), DB.listKids(T.cls), DB.listSubjects(T.cls)]);
    T.rel = new Set(r[0]); T.kids = r[1]; T.subjects = r[2];
  };
  T.cur = function () { return T.classes.filter(function (c) { return c.id === T.cls; })[0] || null; };

  T.renderLogin = function () {
    UI.view = 'login';
    paint('<div class="login"><section class="login-hero"><a class="logo" href="#/">' + I.logo + h(C.PORTAL_NAME) + '</a>' +
      '<div class="stack" style="gap:18px"><h1>Ihre Lernspiele an einem Ort.</h1><p>Spiele für die Klasse freigeben, den Fortschritt sehen und die Arbeitsstand-Tafel für den Wochenplan nutzen.</p></div>' +
      '<a class="kidlink" href="#/klasse">' + ic(I.play, 22) + '<span>Für Kinder: Hier geht\'s zum Klassen-Login</span></a></section>' +
      '<section class="login-form"><form data-a="login" class="stack"><div class="stack" style="gap:8px"><h2 style="font-size:34px">Anmelden</h2>' +
      '<p class="muted">Für Lehrpersonen mit Zugang zu ' + h(C.PORTAL_NAME) + '.</p></div>' +
      '<div class="field"><label for="lgMail">E-Mail</label><input class="input" id="lgMail" name="email" type="email" autocomplete="username" value="' + h(T.loginEmail || '') + '" required></div>' +
      '<div class="field"><label for="lgPw">Passwort</label><input class="input" id="lgPw" name="pw" type="password" autocomplete="current-password" required></div>' +
      '<p class="err">' + h(T.loginErr) + '</p>' +
      '<button class="btn primary" style="min-height:54px;font-size:18px">Anmelden</button>' +
      '<button type="button" class="btn" data-a="forgot">Passwort vergessen?</button>' +
      (T.loginInfo ? '<p class="note">' + h(T.loginInfo) + '</p>' : '') +
      '</form></section></div>');
  };
  ACT.login = async function (f) {
    T.loginErr = ''; T.loginEmail = f.elements.email.value.trim();
    try { await DB.signIn(T.loginEmail, f.elements.pw.value); }
    catch (e) { T.loginErr = errMsg(e); return T.renderLogin(); }
    await T.start();
  };
  ACT.forgot = function () {
    T.loginInfo = 'Bitte melden Sie sich bei ' + C.CONTACT + '. Sie erhalten ein neues Startpasswort.';
    T.renderLogin();
  };
  ACT.logout = async function () { await DB.signOut(); T.me = null; location.hash = '#/'; T.renderLogin(); };

  T.render = function () {
    if (!T.me) return;
    if (!T.me.name) return paint(T.onboardName());
    if (T.tab === 'verwaltung' && !T.me.is_admin) T.tab = 'spiele';
    var body;
    if (!T.classes.length && T.tab !== 'verwaltung') body = T.onboardClass();
    else body = ({ spiele: T.tabSpiele, kinder: T.tabKinder, fortschritt: T.tabFortschritt, tafel: T.tabTafel, verwaltung: T.tabAdmin }[T.tab] || T.tabSpiele)();
    paint(T.shell(body));
  };
  T.shell = function (body) {
    var tabs = [['spiele', 'Spiele'], ['kinder', 'Kinder'], ['fortschritt', 'Fortschritt'], ['tafel', 'Arbeitsstand-Tafel']];
    if (T.me.is_admin) tabs.push(['verwaltung', 'Verwaltung']);
    return '<header class="top"><div class="top-in"><a class="logo" href="#/">' + I.logo + h(C.PORTAL_NAME) + '</a><div class="row">' +
      (T.classes.length ? '<label class="sr" for="clsSel">Klasse wählen</label><select id="clsSel" class="input" style="min-height:44px;width:auto" data-change="pickClass">' +
        T.classes.map(function (c) { return '<option value="' + c.id + '"' + (c.id === T.cls ? ' selected' : '') + '>Klasse ' + h(c.name) + '</option>'; }).join('') + '</select>' : '') +
      '<button class="btn sm" data-a="account"><span class="avatar">' + h(initials(T.me.name)) + '</span>' + h(T.me.name) + '</button>' +
      '<button class="btn sm" data-a="logout">Abmelden</button></div></div>' +
      '<nav class="tabs" role="tablist">' + tabs.map(function (t) {
        return '<button class="tab" role="tab" aria-selected="' + (T.tab === t[0]) + '" data-a="tab" data-t="' + t[0] + '">' + t[1] + '</button>';
      }).join('') + '</nav></header><main class="main">' + body + '</main>';
  };
  ACT.tab = function (el) { T.tab = el.dataset.t; LS.set('kn_tab', T.tab); UI.confirm = null; T.render(); };
  ACT.pickClass = async function (el) { T.cls = el.value; LS.set('kn_cls', T.cls); await T.loadClass(); T.render(); };

  T.onboardName = function () {
    return '<main class="main" style="max-width:560px"><form class="card stack" data-a="saveName"><a class="logo" href="#/">' + I.logo + h(C.PORTAL_NAME) + '</a>' +
      '<h1 class="h1">Willkommen!</h1><p class="muted">Wie sollen Ihre Kinder und Kolleginnen Sie im Portal sehen?</p>' +
      '<div class="field"><label for="obName">Ihr Name</label><input class="input" id="obName" name="name" placeholder="z. B. Frau Meier" required></div>' +
      '<button class="btn primary">Weiter</button></form></main>';
  };
  ACT.saveName = async function (f) {
    var n = f.elements.name.value.trim(); if (!n) return;
    await DB.setMyName(T.me.id, n); T.me.name = n; toast('Name gespeichert.');
    if (document.querySelector('.overlay')) T.account();
    T.render();
  };
  T.onboardClass = function () {
    return '<form class="card stack" data-a="createClass" style="max-width:620px"><h1 class="h1">Ihre erste Klasse</h1>' +
      '<p class="muted">Jede Klasse bekommt einen eigenen Klassencode. Damit melden sich die Kinder an.</p>' +
      '<div class="field"><label for="cName">Name der Klasse</label><input class="input" id="cName" name="cname" placeholder="z. B. 5a" required maxlength="30"></div>' +
      '<button class="btn primary">Klasse anlegen</button></form>';
  };
  var CODE_WORDS = ['FUCHS', 'DACHS', 'LUCHS', 'BIBER', 'IGEL', 'ADLER', 'EULE', 'OTTER', 'GEMSE', 'WOLF', 'HASE', 'FALKE', 'KAUZ', 'MARDER', 'SPATZ',
    'PANDA', 'KOALA', 'DELFIN', 'PINGUIN', 'ZEBRA', 'TIGER', 'KATZE', 'MAUS', 'ELCH', 'STORCH', 'RABE', 'SCHWAN', 'LAMA', 'WAL', 'MURMEL'];
  function genCode() { return CODE_WORDS[rnd(CODE_WORDS.length)] + ' ' + (100 + rnd(900)); }
  async function withFreeCode(fn) {
    for (var i = 0; i < 8; i++) {
      try { return await fn(genCode()); }
      catch (e) { if (!/classes_code/.test(e.message)) throw e; }
    }
    throw new Error('Kein freier Klassencode gefunden. Bitte nochmals versuchen.');
  }
  ACT.createClass = async function (f) {
    var name = f.elements.cname.value.trim(); if (!name) return;
    var c = await withFreeCode(function (code) { return DB.createClass(name, code); });
    var d = [['Mathematik', '#2F5E9E'], ['Deutsch', '#8A4F7D'], ['Englisch', '#C0473C'], ['NMG', '#C46A1C']];
    for (var i = 0; i < d.length; i++) await DB.addSubject(c.id, { name: d[i][0], color: d[i][1], fav: true, active: true, sort: i });
    T.classes.push(c); T.cls = c.id; LS.set('kn_cls', c.id);
    await T.loadClass(); T.tab = 'kinder'; LS.set('kn_tab', 'kinder');
    closeOverlays(); toast('Klasse ' + name + ' angelegt. Code: ' + c.code); T.render();
  };

  // ---------- Spiele ----------
  function isNew(g) { return Date.now() - new Date(g.created_at).getTime() < 14 * 86400000; }
  T.tabSpiele = function () {
    var c = T.cur(), games = T.games.concat(liveGames());
    var released = T.games.filter(function (g) { return T.rel.has(g.id); }).length;
    var fachs = uniq(games.map(function (g) { return g.fach; }));
    if (T.fach !== 'alle' && fachs.indexOf(T.fach) < 0) T.fach = 'alle';
    var q = T.q.trim().toLowerCase();
    var shown = games.filter(function (g) {
      return (T.fach === 'alle' || g.fach === T.fach) && (!q || (g.title + ' ' + g.description + ' ' + g.thema + ' ' + g.fach).toLowerCase().indexOf(q) >= 0);
    });
    var out = '<section class="banner"><div class="stack" style="gap:8px;flex:1 1 360px"><h2>Klasse ' + h(c.name) + '</h2>' +
      '<p>Die Kinder öffnen <b>' + h(shortUrl(kidUrl())) + '</b>, geben den Code ein, tippen auf ihren Namen und ihr Bildpasswort. Sie sehen nur die Spiele, die Sie freigeben.</p>' +
      '<p style="font-weight:700;color:var(--ink)">' + released + ' von ' + plural(T.games.length, 'Spiel', 'Spielen') + ' für die Klasse freigegeben</p></div>' +
      '<div class="row" style="gap:16px"><div class="codebox"><small>Klassencode</small><b>' + h(c.code) + '</b></div><div class="stack" style="gap:8px">' +
      '<button class="btn amber" data-a="showCode">Code gross zeigen</button><a class="btn" href="#/klasse" target="_blank" rel="noopener">Ansicht der Kinder</a>' +
      '<a class="btn primary" href="#/tagesfolie/' + T.cls + '">☀️ Tagesfolie starten</a></div></div></section>';
    if (!T.games.length) {
      return out + '<div class="empty">' + (T.me.is_admin ? 'Noch keine Spiele. Laden Sie Ihr erstes Spiel unter «Verwaltung» hoch.' :
        'Für Sie sind noch keine Spiele freigeschaltet. Melden Sie sich bei ' + h(C.CONTACT) + '.') + '</div>';
    }
    out += '<section class="stack"><h2 style="font-size:26px">Fächer</h2><div class="tiles">' +
      [{ id: 'alle', label: 'Alle Fächer', n: games.length, col: '#E3ECF5' }].concat(fachs.map(function (f) {
        return { id: f, label: f, n: games.filter(function (g) { return g.fach === f; }).length, col: fachColor(f) };
      })).map(function (t) {
        return '<button class="tile" aria-pressed="' + (T.fach === t.id) + '" data-a="fach" data-f="' + h(t.id) + '"><span class="sw" style="background:' + t.col + '">' +
          h(t.id === 'alle' ? '★' : t.label.charAt(0)) + '</span><span><b' + (t.label.length > 13 ? ' style="font-size:' + (t.label.length > 17 ? 13 : 15) + 'px"' : '') + '>' + h(t.label) + '</b><span>' + plural(t.n, 'Spiel', 'Spiele') + '</span></span></button>';
      }).join('') + '</div></section>';
    out += '<section class="stack"><div class="row" style="justify-content:space-between;align-items:flex-end"><h2 style="font-size:26px">' +
      (T.fach === 'alle' ? 'Alle Spiele' : 'Spiele in ' + h(T.fach)) + '</h2><div class="row" style="align-items:flex-end"><button class="btn sm" data-a="gGroupAll" data-v="1">Alle einklappen</button><button class="btn sm" data-a="gGroupAll" data-v="0">Alle ausklappen</button></div><div class="field" style="flex:0 1 320px"><label for="gSearch">Spiel suchen</label>' +
      '<input class="input" id="gSearch" type="search" placeholder="z. B. Einmaleins" value="' + h(T.q) + '" data-input="search"></div></div>';
    var groups = [], by = {};
    shown.forEach(function (g) { var k = g.fach + '|' + g.thema; if (!by[k]) { by[k] = { fach: g.fach, thema: g.thema, list: [] }; groups.push(by[k]); } by[k].list.push(g); });
    if (!groups.length) out += '<div class="empty">Kein Spiel gefunden.</div>';
    groups.forEach(function (gr) {
      var gk = gr.fach + '|' + gr.thema, shut = !!T.closed[gk] && !q;
      var sorting = T.sorting === gk && !shut, real = gr.list.filter(function (g) { return !g.live; });
      out += '<div class="ghead"><h3 class="gtitle"><button class="gtoggle" aria-expanded="' + !shut + '" data-a="gGroup" data-k="' + h(gk) + '"><span class="chev" aria-hidden="true">›</span>' +
        '<small>' + h(gr.fach) + ' ›</small> ' + h(gr.thema) + ' <small>' + plural(gr.list.length, 'Spiel', 'Spiele') + ' · ' +
        gr.list.filter(function (g) { return T.rel.has(g.id); }).length + ' freigegeben</small></button></h3>' +
        (T.me.is_admin && !shut && real.length > 1 && !q ? '<button class="btn sm" data-a="gSort" data-k="' + h(gk) + '"' + (sorting ? ' aria-pressed="true"' : '') + '>' + ic(I.sort, 14) + (sorting ? ' Fertig' : ' Reihenfolge ändern') + '</button>' : '') + '</div>';
      if (sorting) {
        out += '<div class="sortbox"><p class="muted">Ziehen Sie ein Spiel am Griff <span aria-hidden="true">⠿</span> an die richtige Stelle oder benutzen Sie die Pfeile. Die Reihenfolge wird sofort gespeichert und gilt für alle Lehrpersonen und Kinder.</p>' +
          '<ol class="sorter" data-k="' + h(gk) + '">' + real.map(function (g, i) {
            return '<li class="srow" data-id="' + g.id + '"><span class="grip" title="Ziehen" aria-hidden="true">⠿</span><span class="snum">' + (i + 1) + '</span><b>' + h(g.title) + '</b>' +
              '<span class="sbtns"><button class="btn sm" data-a="sMove" data-d="-1" data-id="' + g.id + '" aria-label="' + h(g.title) + ' nach oben"' + (i ? '' : ' disabled') + '>↑</button>' +
              '<button class="btn sm" data-a="sMove" data-d="1" data-id="' + g.id + '" aria-label="' + h(g.title) + ' nach unten"' + (i < real.length - 1 ? '' : ' disabled') + '>↓</button></span></li>';
          }).join('') + '</ol><div class="row"><button class="btn primary" data-a="gSort" data-k="' + h(gk) + '">Fertig</button></div></div>';
        return;
      }
      out += (shut ? '' : '<div class="games">' +
        gr.list.map(function (g) {
          if (g.live) return '<article class="game live"><div class="game-top" style="background:' + fachColor(g.fach) + '">' + h(fachShort(g.fach)) + '</div><div class="game-body"><div class="row" style="gap:8px">' +
            '<span class="pill" style="background:#E3F0FC;color:#2B6CB0">' + h(g.fach) + '</span><span class="pill" style="background:#FFE8A3;color:#6A5420">Live mit iPads</span></div>' +
            '<h3>' + g.icon + ' ' + h(g.title) + '</h3><p>' + h(g.description) + '</p>' +
            '<div class="game-foot"><p class="muted small" style="margin:0">Immer verfügbar. Die Kinder sehen den Sprint erst, wenn Sie ihn öffnen.</p>' +
            '<a class="btn primary" href="' + g.href + '">' + ic(I.play, 14, '#fff') + ' Spielen</a></div></div></article>';
          var on = T.rel.has(g.id);
          return '<article class="game"><div class="game-top" style="background:' + fachColor(g.fach) + '">' + h(fachShort(g.fach)) +
            (isNew(g) ? '<span class="pill">Neu</span>' : '') + '</div><div class="game-body"><div class="row" style="gap:8px">' +
            '<span class="pill" style="background:#E3F0FC;color:#2B6CB0">' + h(g.fach) + '</span>' +
            (g.stufe ? (/zusatz/i.test(g.stufe) ? '<span class="pill zusatz-t">★ ' + h(g.stufe) + '</span>' : '<span class="pill" style="background:#DDF5EA;color:#1F6B50">' + h(g.stufe) + '</span>') : '') + '</div>' +
            '<h3>' + h(g.title) + '</h3>' + (g.description ? '<p>' + h(g.description) + '</p>' : '') +
            '<div class="game-foot"><button class="switch" role="switch" aria-checked="' + on + '" data-a="rel" data-id="' + g.id + '"><span>' +
            (on ? 'Für die Klasse freigegeben' : 'Für die Klasse gesperrt') + '</span><span class="track"></span></button>' +
            (isWall(g) ? '<button class="btn primary" data-a="playBoard" data-id="' + g.id + '">' + ic(I.play, 14, '#fff') + ' Spielen</button>' :
            '<button class="btn" data-a="preview" data-id="' + g.id + '">' + ic(I.play, 14) + ' Selbst ansehen</button>') + '</div></div></article>';
        }).join('') + '</div>');
    });
    return out + '</section>';
  };
  ACT.fach = function (el) { T.fach = el.dataset.f; T.render(); };
  // Eingebaute Live-Spiele (Kinder spielen gleichzeitig am iPad, die Wandtafel zeigt alles live).
  // Sie erscheinen im gleichen Fach und Thema wie Ihre anderen Wandtafelspiele.
  function liveGames() {
    var wall = T.games.filter(function (g) { return /wandtafel/i.test(g.fach); })[0];
    var fach = wall ? wall.fach : 'Wandtafelspiele', thema = wall ? wall.thema : 'Wandtafel';
    return [{ id: 'live-sprint', live: true, icon: '🏃', title: 'Klassen-Sprint', fach: fach, thema: thema, description: 'Alle Kinder rechnen gleichzeitig 1×1 am iPad. Vorne an der Wandtafel sieht man live, wer wo auf der Rennbahn ist.', href: '#/sprint/' + T.cls }];
  }
  // Reihenfolge der Spiele innerhalb eines Themas (nur Admin)
  function gameCmp(a, b) {
    return a.fach.localeCompare(b.fach, 'de') || a.thema.localeCompare(b.thema, 'de') || ((a.sort || 0) - (b.sort || 0)) || a.title.localeCompare(b.title, 'de');
  }
  ACT.gSort = function (el) { T.sorting = T.sorting === el.dataset.k ? null : el.dataset.k; T.render(); };
  async function saveOrder(ids) {
    var by = {}; T.games.forEach(function (g) { by[g.id] = g; });
    var old = ids.map(function (id) { return by[id].sort || 0; });
    ids.forEach(function (id, i) { by[id].sort = i + 1; });
    T.games.sort(gameCmp); T.render();
    try { await DB.setGameOrder(ids); toast('Reihenfolge gespeichert'); }
    catch (e) { ids.forEach(function (id, i) { by[id].sort = old[i]; }); T.games.sort(gameCmp); T.render(); throw e; }
  }
  function sorterIds(list) { return Array.prototype.map.call(list.querySelectorAll('.srow'), function (r) { return r.dataset.id; }); }
  ACT.sMove = function (el) {
    var row = el.closest('.srow'), list = row.parentNode, ids = sorterIds(list), i = ids.indexOf(row.dataset.id), j = i + (+el.dataset.d);
    if (j < 0 || j >= ids.length) return;
    ids.splice(j, 0, ids.splice(i, 1)[0]);
    return saveOrder(ids).then(function () {
      var r = document.querySelector('.srow[data-id="' + row.dataset.id + '"]'); if (!r) return;
      var b = r.querySelector('[data-a="sMove"][data-d="' + el.dataset.d + '"]');
      if (!b || b.disabled) b = r.querySelector('[data-a="sMove"][data-d="' + (-el.dataset.d) + '"]');
      if (b) b.focus();
    });
  };
  // Ziehen mit Maus, Finger oder Stift
  document.addEventListener('pointerdown', function (e) {
    var grip = e.target.closest && e.target.closest('.srow .grip'); if (!grip) return;
    e.preventDefault();
    var row = grip.closest('.srow'), list = row.parentNode, before = sorterIds(list).join(), y0 = e.clientY;
    row.classList.add('dragging');
    function move(ev) {
      var y = ev.clientY, rows = Array.prototype.filter.call(list.children, function (r) { return r !== row; }), next = null;
      for (var i = 0; i < rows.length; i++) { var b = rows[i].getBoundingClientRect(); if (y < b.top + b.height / 2) { next = rows[i]; break; } }
      if (next) { if (row.nextElementSibling !== next) list.insertBefore(row, next); }
      else if (list.lastElementChild !== row) list.appendChild(row);
      if (y < 70) window.scrollBy(0, -12); else if (y > window.innerHeight - 70) window.scrollBy(0, 12);
    }
    function up() {
      window.removeEventListener('pointermove', move); window.removeEventListener('pointerup', up); window.removeEventListener('pointercancel', up);
      row.classList.remove('dragging');
      var ids = sorterIds(list);
      if (ids.join() !== before) saveOrder(ids).catch(function (x) { toast(errMsg(x)); });
    }
    window.addEventListener('pointermove', move); window.addEventListener('pointerup', up); window.addEventListener('pointercancel', up);
  });
  ACT.gGroup = function (el) { var k = el.dataset.k; if (T.closed[k]) delete T.closed[k]; else T.closed[k] = 1; LS.set('kn_closed', T.closed); T.render(); };
  ACT.gGroupAll = function (el) {
    T.closed = {};
    if (el.dataset.v === '1') T.games.concat(liveGames()).forEach(function (g) { T.closed[g.fach + '|' + g.thema] = 1; });
    LS.set('kn_closed', T.closed); T.render();
  };
  ACT.search = function (el) { T.q = el.value; T.render(); };
  ACT.rel = async function (el) {
    var id = el.dataset.id, on = !T.rel.has(id);
    if (on) T.rel.add(id); else T.rel.delete(id);
    T.render();
    try { await DB.setRelease(T.cls, id, on); }
    catch (e) { if (on) T.rel.delete(id); else T.rel.add(id); T.render(); throw e; }
  };
  // Spiele für die Wandtafel: direkt im Vollbild starten (Lehrperson spielt mit der Klasse)
  ACT.playBoard = async function (el) {
    var g = T.games.filter(function (x) { return x.id === el.dataset.id; })[0], d = document.documentElement;
    try { (d.requestFullscreen || d.webkitRequestFullscreen || function () {}).call(d); } catch (e) {}
    toast('Spiel wird geladen …');
    openPlayer(g.title, await DB.gameHtml(g.id));
  };
  ACT.preview = async function (el) {
    var g = T.games.filter(function (x) { return x.id === el.dataset.id; })[0];
    toast('Spiel wird geladen …');
    openPlayer(g.title + ' (Vorschau)', await DB.gameHtml(g.id));
  };
  ACT.showCode = function () {
    var c = T.cur();
    var o = overlay('<div class="bigcode"><p>Klasse ' + h(c.name) + ' · QR-Code scannen oder ' + h(shortUrl(kidUrl())) + ' öffnen</p>' +
      '<div class="bigcode-row"><div class="qrbox" id="qrBox" role="img" aria-label="QR-Code zum Klassen-Login">QR-Code wird geladen …</div><b>' + h(c.code) + '</b></div>' +
      '<button class="btn" style="align-self:center" data-a="closeOverlay">Schliessen</button></div>');
    qrSvg(kidUrl(c.code)).then(function (svg) { var b = o.querySelector('#qrBox'); if (b) b.innerHTML = svg; })
      .catch(function () { var b = o.querySelector('#qrBox'); if (b) b.textContent = 'QR-Code nicht verfügbar. Bitte die Adresse eintippen.'; });
  };

  // ---------- Kinder ----------
  T.tabKinder = function () {
    var c = T.cur();
    var list = T.kids.length ? '<ul class="list">' + T.kids.map(function (k) {
      var key = 'kid:' + k.id;
      return '<li class="' + (T.fresh.has(k.id) ? 'fresh' : '') + '"><span class="avatar" style="background:' + kidColor(k.name) + ';color:#1B2A3D">' + h(k.name.charAt(0)) + '</span>' +
        '<b class="grow" style="font-size:18px">' + h(k.name) + '</b><span class="pwrow" role="img" aria-label="Bildpasswort: ' + h(pwLabel(k.pw)) + '">' +
        k.pw.split(',').map(function (p) { return SYM[p] ? '<span style="background:' + SYM[p].bg + '">' + symSvg(p, 24) + '</span>' : ''; }).join('') + '</span>' +
        (T.fresh.has(k.id) ? '<span class="pill" style="background:#E3F0FC;color:#2B6CB0">Neues Passwort</span>' : '') +
        '<span class="row" style="margin-left:auto;gap:8px"><button class="btn sm" data-a="kidPw" data-id="' + k.id + '">Passwort zurücksetzen</button>' +
        '<button class="btn sm danger' + (UI.confirm === key ? ' armed' : '') + '" data-a="kidDel" data-id="' + k.id + '">' + (UI.confirm === key ? 'Wirklich löschen?' : 'Löschen') + '</button></span></li>';
    }).join('') + '</ul>' : '<div class="empty">Noch keine Kinder. Tragen Sie rechts die Namen ein.</div>';
    return '<div class="cols2"><div class="wide"><div class="row" style="justify-content:space-between;align-items:flex-end">' +
      '<div class="stack" style="gap:6px"><h1 class="h1">Kinder der Klasse ' + h(c.name) + '</h1><p class="muted">' + plural(T.kids.length, 'Kind', 'Kinder') +
      ' · Klassencode <b style="color:var(--ink)">' + h(c.code) + '</b></p></div>' +
      (T.kids.length ? '<button class="btn primary" data-a="printCards">' + ic(I.print) + ' Passwort-Kärtchen drucken</button>' : '') + '</div>' + list +
      '<p class="muted small">Beim Zurücksetzen bekommt das Kind drei neue Bilder. Der Fortschritt bleibt erhalten.</p></div>' +
      '<aside class="side"><form class="card stack" data-a="addKid"><h2 style="font-size:22px">Ein Kind hinzufügen</h2>' +
      '<div class="field"><label for="kidName">Vorname oder Spitzname</label><input class="input" id="kidName" name="name" maxlength="30" placeholder="z. B. Mila" required></div>' +
      '<button class="btn primary">Hinzufügen</button></form>' +
      '<form class="card stack" data-a="addBulk"><h2 style="font-size:22px">Ganze Klasse auf einmal</h2>' +
      '<div class="field"><label for="kidBulk">Ein Name pro Zeile</label><textarea class="input" id="kidBulk" name="list" rows="6" placeholder="Mila&#10;Tim&#10;Aylin"></textarea></div>' +
      '<button class="btn">Alle hinzufügen</button><p class="muted small">Tipp: Namensliste aus Excel kopieren und hier einfügen.</p></form>' +
      '<div class="note"><b>Datenschutz:</b> Nur Vornamen oder Spitznamen eintragen. Keine Nachnamen, Geburtsdaten oder E-Mail-Adressen der Kinder.</div></aside></div>';
  };
  function kidExists(n) { return T.kids.some(function (k) { return k.name.toLowerCase() === n.toLowerCase(); }); }
  ACT.addKid = async function (f) {
    var n = f.elements.name.value.trim(); if (!n) return;
    if (kidExists(n)) return toast('Diesen Namen gibt es in der Klasse schon.');
    var r = await DB.addKids(T.cls, [{ name: n, pw: randPw() }]);
    r.forEach(function (k) { T.kids.push(k); T.fresh.add(k.id); });
    T.kids.sort(function (a, b) { return a.name.localeCompare(b.name, 'de'); }); T.progress = null; T.tafel = null;
    T.render(); var i = document.getElementById('kidName'); if (i) { i.value = ''; i.focus(); }
  };
  ACT.addBulk = async function (f) {
    var seen = {}, add = [];
    f.elements.list.value.split(/[\n,;]/).forEach(function (s) {
      var n = s.trim().slice(0, 30); var k = n.toLowerCase();
      if (n && !seen[k] && !kidExists(n)) { seen[k] = 1; add.push({ name: n, pw: randPw() }); }
    });
    if (!add.length) return toast('Keine neuen Namen gefunden.');
    var r = await DB.addKids(T.cls, add);
    r.forEach(function (k) { T.kids.push(k); T.fresh.add(k.id); });
    T.kids.sort(function (a, b) { return a.name.localeCompare(b.name, 'de'); }); T.progress = null; T.tafel = null;
    toast(plural(r.length, 'Kind', 'Kinder') + ' hinzugefügt.'); T.render();
  };
  ACT.kidPw = async function (el) {
    var k = T.kids.filter(function (x) { return x.id === el.dataset.id; })[0];
    var pw = randPw(k.pw); await DB.setKidPw(k.id, pw); k.pw = pw; T.fresh.add(k.id);
    toast('Neues Bildpasswort für ' + k.name + ': ' + pwLabel(pw)); T.render();
  };
  ACT.kidDel = async function (el) {
    if (!armed('kid:' + el.dataset.id)) return T.render();
    await DB.deleteKid(el.dataset.id);
    T.kids = T.kids.filter(function (k) { return k.id !== el.dataset.id; }); T.progress = null; T.tafel = null; T.render();
  };
  ACT.printCards = function () {
    var c = T.cur();
    document.getElementById('print').innerHTML = '<div class="pcards">' + T.kids.map(function (k) {
      return '<div class="pcard"><h3>' + h(k.name) + '</h3><div class="pw">' + k.pw.split(',').map(function (p) {
        return SYM[p] ? '<span style="background:' + SYM[p].bg + '">' + symSvg(p, 48) + '</span>' : ''; }).join('') +
        '</div><p>Klasse ' + h(c.name) + ' · Code <b>' + h(c.code) + '</b><br>' + h(shortUrl(kidUrl())) + '</p></div>';
    }).join('') + '</div>';
    setTimeout(function () { window.print(); }, 50);
  };

  // ---------- Fortschritt ----------
  T.tabFortschritt = function () {
    if (T.progress === null) {
      if (!T.progressBusy) {
        T.progressBusy = true;
        DB.listProgress(T.kids.map(function (k) { return k.id; })).then(function (p) { T.progress = p; T.progressBusy = false; T.render(); })
          .catch(function (e) { T.progressBusy = false; toast(errMsg(e)); });
      }
      return '<p class="muted">Fortschritt wird geladen …</p>';
    }
    var c = T.cur();
    var allGames = T.games.filter(function (g) { return T.rel.has(g.id); });
    var fachs = uniq(allGames.map(function (g) { return g.fach; }));
    if (T.pfach && T.pfach !== 'alle' && fachs.indexOf(T.pfach) < 0) T.pfach = 'alle';
    var games = allGames.filter(function (g) { return !T.pfach || T.pfach === 'alle' || g.fach === T.pfach; });
    var P = {}; T.progress.forEach(function (p) { P[p.kid_id + '|' + p.game_id] = p; });
    T.pOpen = T.pOpen || LS.get('kn_popen') || {};
    // Spalten-Gruppen: ein Thema = eine Gruppe; zugeklappt = eine Übersichts-Spalte
    var groups = [], byG = {}, fgroups = [], byF = {};
    games.forEach(function (g) {
      var k = g.fach + '|' + g.thema; if (!byG[k]) { byG[k] = { key: k, fach: g.fach, thema: g.thema, list: [] }; groups.push(byG[k]); } byG[k].list.push(g);
      if (!byF[g.fach]) { byF[g.fach] = { key: 'F:' + g.fach, fach: g.fach, list: [], groups: [] }; fgroups.push(byF[g.fach]); } byF[g.fach].list.push(g);
    });
    groups.forEach(function (gr) { byF[gr.fach].groups.push(gr); });
    // Anzahl Spalten eines Fachs / Themas, je nach auf- oder zugeklappt
    function tCols(gr) { return T.pOpen[gr.key] ? gr.list.length : 1; }
    function fCols(f) { return T.pOpen[f.key] ? f.groups.reduce(function (n, gr) { return n + tCols(gr); }, 0) : 1; }
    function tog(key, open, top, label) {
      return '<button class="gtoggle" aria-expanded="' + open + '" data-a="pGroup" data-k="' + h(key) + '"><span class="chev" aria-hidden="true">›</span><span>' +
        (top ? '<small>' + h(top) + '</small><br>' : '') + h(label) + '</span></button>';
    }
    function started(p) { return p && (p.plays || p.attempts || p.done != null); }
    function sumCell(k, gr) {
      var st = 0, n = 0, ok = 0;
      gr.list.forEach(function (g) { var p = P[k.id + '|' + g.id]; if (started(p)) { n++; ok += p.correct || 0; var a = p.award || {}; st += typeof a.stars === 'number' ? a.stars : awardSum(a); } });
      if (!n) return '<span class="small" style="color:#66788D">Noch nichts</span>';
      return (st ? '<span class="small" style="font-weight:700;white-space:nowrap">⭐ ' + st + (st === 1 ? ' Stern' : ' Sterne') + '</span>' : '') +
        '<span class="small" style="white-space:nowrap"><b>' + n + ' von ' + gr.list.length + '</b> Spielen</span>' +
        (ok ? '<span class="small muted">' + ok + ' richtig</span>' : '') +
        '<div class="bar"><i style="width:' + Math.round(n / gr.list.length * 100) + '%"></i></div>';
    }
    function cell(p) {
      if (!p || (!p.plays && !p.attempts && p.done == null)) return { none: true, html: '<span class="small" style="color:#66788D">Noch nicht begonnen</span>' };
      var ls = lvlInfo(p), lines;
      if (ls.length) {
        lines = ls.slice(0, 4).map(function (x, i) {
          return '<span class="small"' + (i ? ' style="color:var(--soft)"' : '') + '><b>' + h(x.name) + ':</b> ' + lvlText(x) + '</span>' +
            (i === 0 && x.t ? '<div class="bar"><i style="width:' + Math.min(100, Math.round((x.d || 0) / x.t * 100)) + '%"></i></div>' : '');
        });
        if (ls.length > 4) lines.push('<span class="small muted">+ ' + (ls.length - 4) + ' weitere Level</span>');
      } else {
        lines = ['<span class="small">' + (p.total ? p.done + ' von ' + p.total + ' geschafft' : p.attempts ? p.correct + ' richtig, ' + (p.attempts - p.correct) + ' falsch' : 'geöffnet (' + p.plays + '×)') + '</span>'];
      }
      var aw = awardText(p.award);
      if (aw) lines.unshift('<span class="small" style="font-weight:700">' + h(aw) + '</span>');
      return { html: lines.join('') };
    }
    var kids = T.kids.filter(function (k) {
      if (T.pfilter !== 'offen') return true;
      return games.some(function (g) { return cell(P[k.id + '|' + g.id]).none; });
    });
    var head = '<div class="row" style="justify-content:space-between;align-items:flex-end"><div class="stack" style="gap:6px"><h1 class="h1">Fortschritt Klasse ' + h(c.name) + '</h1>' +
      '<p class="muted">' + plural(T.kids.length, 'Kind', 'Kinder') + ' · ' + plural(games.length, 'Spiel', 'Spiele') + ' freigegeben</p></div>' +
      '<div class="row"><button class="btn" data-a="refreshProgress">' + ic(I.reset) + ' Aktualisieren</button><button class="btn" data-a="tab" data-t="kinder">Kinder verwalten</button></div></div>' +
      '<div class="row" style="justify-content:space-between;align-items:center">' +
      '<div class="chips" role="group" aria-label="Fach">' + ['alle'].concat(fachs).map(function (f) {
        return '<button class="chip" aria-pressed="' + ((T.pfach || 'alle') === f) + '" data-a="pfach" data-f="' + h(f) + '">' + (f === 'alle' ? 'Alle Fächer' : h(f)) + '</button>'; }).join('') + '</div>' +
      '<div class="chips" role="group" aria-label="Filter">' + [['alle', 'Alle Kinder'], ['offen', 'Spiel noch nicht begonnen']].map(function (f) {
        return '<button class="chip" aria-pressed="' + (T.pfilter === f[0]) + '" data-a="pfilter" data-f="' + f[0] + '">' + f[1] + '</button>'; }).join('') + '</div>' +
      '<div class="row"><button class="btn sm" data-a="pOpenAll" data-v="0">Alles zuklappen</button><button class="btn sm" data-a="pOpenAll" data-v="f">Themen zeigen</button><button class="btn sm" data-a="pOpenAll" data-v="1">Alle Spiele zeigen</button></div></div>';
    if (!T.kids.length || !games.length) return head + '<div class="empty">' + (!T.kids.length ? 'Noch keine Kinder in dieser Klasse.' : 'Noch keine Spiele freigegeben.') + '</div>';
    // Kopf mit drei Ebenen: Fach › Thema › Spiel
    var r1 = '', r2 = '', r3 = '';
    fgroups.forEach(function (f) {
      var fo = !!T.pOpen[f.key];
      r1 += '<th scope="colgroup" class="pfach" colspan="' + fCols(f) + '" style="background:' + fachColor(f.fach) + '">' + tog(f.key, fo, '', f.fach) + '</th>';
      if (!fo) { r2 += '<th scope="col" class="pgame muted" rowspan="2">' + plural(f.list.length, 'Spiel', 'Spiele') + '</th>'; return; }
      f.groups.forEach(function (gr) {
        var to = !!T.pOpen[gr.key];
        r2 += '<th scope="colgroup" class="pgrp" colspan="' + tCols(gr) + '">' + tog(gr.key, to, '', gr.thema) + '</th>';
        r3 += to ? gr.list.map(function (g) { return '<th scope="col" class="pgame">' + h(g.title) + '</th>'; }).join('') :
          '<th scope="col" class="pgame muted">' + plural(gr.list.length, 'Spiel', 'Spiele') + '</th>';
      });
    });
    var table = '<div class="tablewrap"><table class="ptable"><thead><tr><th scope="col" rowspan="3">Kind</th>' + r1 + '<th scope="col" rowspan="3">Zuletzt aktiv</th></tr>' +
      '<tr>' + r2 + '</tr><tr>' + r3 + '</tr></thead><tbody>' + kids.map(function (k) {
        var last = null;
        games.forEach(function (g) { var p = P[k.id + '|' + g.id]; if (p && p.last_played && (!last || p.last_played > last)) last = p.last_played; });
        var cells = fgroups.map(function (f) {
          if (!T.pOpen[f.key]) return '<td class="psum"><div class="stack" style="gap:3px">' + sumCell(k, f) + '</div></td>';
          return f.groups.map(function (gr) {
            if (!T.pOpen[gr.key]) return '<td class="psum"><div class="stack" style="gap:3px">' + sumCell(k, gr) + '</div></td>';
            return gr.list.map(function (g) { return '<td style="min-width:180px"><div class="stack" style="gap:4px">' + cell(P[k.id + '|' + g.id]).html + '</div></td>'; }).join('');
          }).join('');
        }).join('');
        return '<tr><th scope="row" style="white-space:nowrap"><span class="row" style="gap:10px;flex-wrap:nowrap"><span class="avatar" style="width:32px;height:32px;background:' +
          kidColor(k.name) + ';color:#1B2A3D">' + h(k.name.charAt(0)) + '</span>' + h(k.name) + '</span></th>' + cells +
          '<td class="muted" style="white-space:nowrap">' + since(last) + '</td></tr>';
      }).join('') + '</tbody></table></div>';
    return head + table + '<p class="muted small">Spiele, die dafür vorbereitet sind, melden richtige Antworten oder den Spielstand. Bei anderen Spielen sieht man, wie oft sie geöffnet wurden. Gespeichert werden nur Vorname, Fortschritt und Datum.</p>';
  };
  ACT.pfilter = function (el) { T.pfilter = el.dataset.f; T.render(); };
  ACT.pfach = function (el) { T.pfach = el.dataset.f; T.render(); };
  ACT.pGroup = function (el) { var k = el.dataset.k; T.pOpen = T.pOpen || {}; if (T.pOpen[k]) delete T.pOpen[k]; else T.pOpen[k] = 1; LS.set('kn_popen', T.pOpen); T.render(); };
  ACT.pOpenAll = function (el) {
    T.pOpen = {};
    if (el.dataset.v === '1') T.games.forEach(function (g) { if (!T.pfach || T.pfach === 'alle' || g.fach === T.pfach) { T.pOpen['F:' + g.fach] = 1; T.pOpen[g.fach + '|' + g.thema] = 1; } });
    if (el.dataset.v === 'f') T.games.forEach(function (g) { T.pOpen['F:' + g.fach] = 1; });
    LS.set('kn_popen', T.pOpen); T.render();
  };
  ACT.refreshProgress = function () { T.progress = null; T.render(); };

  // ---------- Arbeitsstand-Tafel ----------
  T.tabTafel = function () {
    var c = T.cur();
    if (T.tafel === null && !T.tafelBusy) {
      T.tafelBusy = true;
      DB.tafelTeacher(T.cls).then(function (t) { T.tafel = t; T.tafelBusy = false; if (T.tab === 'tafel') T.render(); })
        .catch(function (e) { T.tafelBusy = false; toast(errMsg(e)); });
    }
    function swatches(sel, action, id) {
      return '<div class="swatches" role="group" aria-label="Farbe wählen">' + PALETTE.map(function (p) {
        return '<button type="button" class="swatch" style="background:' + p[0] + '" aria-label="' + p[1] + '" aria-pressed="' + (p[0] === sel) + '" data-a="' + action + '" data-c="' + p[0] + '"' + (id ? ' data-id="' + id + '"' : '') + '></button>';
      }).join('') + '</div>';
    }
    var list = T.subjects.length ? '<div class="stack" style="gap:8px">' + T.subjects.map(function (s) {
      var key = 'subj:' + s.id;
      return '<div class="subj' + (s.active ? '' : ' off') + '"><div class="subj-row">' +
        '<button type="button" class="check" role="checkbox" aria-checked="' + s.active + '" aria-label="' + h(s.name) + ' diese Woche auf der Tafel" data-a="subjActive" data-id="' + s.id + '">' +
        (s.active ? ic(I.check, 16, '#fff', 3.4) : '') + '</button>' +
        '<button type="button" class="colorbtn" style="background:' + h(s.color) + '" aria-label="Farbe von ' + h(s.name) + ' ändern" data-a="subjColor" data-id="' + s.id + '"></button>' +
        '<b class="grow" style="font-size:18px">' + h(s.name) + '</b><span class="muted small">' + (s.active ? 'diese Woche auf der Tafel' : 'nicht auf der Tafel') + '</span>' +
        '<button type="button" class="btn icon" aria-pressed="' + s.fav + '" aria-label="' + h(s.name) + (s.fav ? ' ist Favorit' : ' als Favorit markieren') + '" data-a="subjFav" data-id="' + s.id + '">' +
        '<svg width="22" height="22" viewBox="0 0 24 24" fill="' + (s.fav ? '#A8E6CF' : 'none') + '" stroke="' + (s.fav ? '#2E8B6A' : '#66788D') + '" stroke-width="1.9" stroke-linejoin="round" aria-hidden="true">' + I.star + '</svg></button>' +
        '<button type="button" class="btn icon' + (UI.confirm === key ? ' danger armed' : '') + '" aria-label="' + h(s.name) + ' löschen" data-a="subjDel" data-id="' + s.id + '">' +
        (UI.confirm === key ? '?' : ic(I.trash, 20, '#9A3B1A', 2)) + '</button></div>' +
        (T.editColor === s.id ? '<div style="padding-left:44px">' + swatches(s.color, 'subjPick', s.id) + '</div>' : '') + '</div>';
    }).join('') + '</div>' : '<div class="empty">Noch keine Fächer. Fügen Sie unten eines hinzu.</div>';
    var counts = '';
    if (T.tafel) {
      var st = T.tafel.state;
      counts = st.subjects.map(function (s) {
        var n = st.entries.filter(function (e) { return e.subject_id === s.id && e.col === 'frage'; }).length;
        return '<div class="row" style="justify-content:space-between;padding:10px 12px;border-radius:10px;background:#3D7CC0"><span class="row" style="gap:10px;font-weight:700">' +
          '<span style="width:12px;height:12px;border-radius:4px;background:' + h(s.color) + ';box-shadow:0 0 0 1.5px #fff"></span>' + h(s.name) + '</span><span>' +
          (n === 0 ? 'keine' : plural(n, 'Kind', 'Kinder')) + '</span></div>';
      }).join('') || '<p class="muted">Keine Fächer aktiv.</p>';
    } else counts = '<p class="muted">Wird geladen …</p>';
    var resetKey = 'resetFav', clearKey = 'clearTafel';
    return '<div class="cols2"><div class="wide"><div class="stack" style="gap:8px"><h1 class="h1">Arbeitsstand-Tafel</h1>' +
      '<p class="muted">Haken Sie an, was diese Woche auf der Tafel steht. Mit dem Stern markieren Sie Favoriten, die beim Zurücksetzen bleiben.</p></div>' +
      '<section class="card stack"><div class="row" style="justify-content:space-between"><h2>Fächer und Aufgaben</h2>' +
      '<button class="btn sm' + (UI.confirm === resetKey ? ' danger armed' : '') + '" data-a="resetFav">' + ic(I.reset) + (UI.confirm === resetKey ? ' Nicht-Favoriten wirklich löschen?' : ' Zurücksetzen auf Favoriten') + '</button></div>' +
      list + '<form class="stack" data-a="addSubj" style="padding-top:14px;border-top:1.5px solid #E2EBF5"><div class="field"><label for="subjName">Eigenes Fach oder Aufgabe hinzufügen</label>' +
      '<div class="row"><input class="input grow" style="flex:1 1 220px" id="subjName" name="name" maxlength="40" placeholder="z. B. Lesetraining" value="' + h(T.subjDraft || '') + '" data-input="subjDraft" required><button class="btn primary">Hinzufügen</button></div></div>' +
      '<div class="row"><span class="lbl">Farbe:</span>' + swatches(T.newColor, 'newColor') + '</div></form></section>' +
      '<section class="card stack"><h2>Die drei Spalten</h2><div class="columns">' + COLS.map(function (col) {
        return '<div class="column c-' + col.id + '" style="min-height:0"><div class="column-h" style="font-size:17px">' + col.label + '</div></div>'; }).join('') +
      '</div><p class="muted small">Wer «Ich habe eine Frage» wählt, sieht sofort, wer im gleichen Fach helfen kann. Jedes Kind steht nur an einem Ort.</p></section>' +
      '<section class="card stack"><h2>Neue Woche</h2><button class="switch" role="switch" aria-checked="' + !!c.tafel_auto + '" data-a="tafelAuto"><span>Namen jeden Montag automatisch von der Tafel nehmen</span><span class="track"></span></button>' +
      '<div class="row"><button class="btn danger' + (UI.confirm === clearKey ? ' armed' : '') + '" data-a="tafelClear">' + (UI.confirm === clearKey ? 'Wirklich alle Namen entfernen?' : 'Alle Namen jetzt entfernen') + '</button>' +
      '<span class="muted small">Die Fächer bleiben, nur die Namen gehen weg.</span></div></section></div>' +
      '<aside class="side"><section class="card stack" style="background:var(--pastel);border-color:#A9C9EC"><h2 style="font-size:22px">Offene Fragen gerade</h2>' + counts +
      '<a class="btn amber" href="#/wandtafel/' + T.cls + '" target="_blank" rel="noopener">' + ic(I.board) + ' An der Wandtafel zeigen</a>' +
      '<button class="btn" data-a="tafelRefresh">' + ic(I.reset) + ' Aktualisieren</button>' +
      '<p class="muted" style="font-size:14px">Die Kinder öffnen die Tafel nach dem Einloggen über «Unsere Tafel».</p></section></aside></div>';
  };
  function subj(id) { return T.subjects.filter(function (s) { return s.id === id; })[0]; }
  ACT.subjActive = async function (el) { var s = subj(el.dataset.id); s.active = !s.active; T.render(); await DB.updateSubject(s.id, { active: s.active }); T.tafel = null; T.render(); };
  ACT.subjFav = async function (el) { var s = subj(el.dataset.id); s.fav = !s.fav; T.render(); await DB.updateSubject(s.id, { fav: s.fav }); };
  ACT.subjColor = function (el) { T.editColor = T.editColor === el.dataset.id ? null : el.dataset.id; T.render(); };
  ACT.subjPick = async function (el) { var s = subj(el.dataset.id); s.color = el.dataset.c; T.editColor = null; T.render(); await DB.updateSubject(s.id, { color: s.color }); T.tafel = null; T.render(); };
  ACT.subjDel = async function (el) {
    if (!armed('subj:' + el.dataset.id)) return T.render();
    await DB.deleteSubjects([el.dataset.id]);
    T.subjects = T.subjects.filter(function (s) { return s.id !== el.dataset.id; }); T.tafel = null; T.render();
  };
  ACT.newColor = function (el) { T.newColor = el.dataset.c; T.render(); };
  ACT.addSubj = async function (f) {
    var n = f.elements.name.value.trim(); if (!n) return;
    if (T.subjects.some(function (s) { return s.name.toLowerCase() === n.toLowerCase(); })) return toast('Dieses Fach gibt es schon.');
    var s = await DB.addSubject(T.cls, { name: n, color: T.newColor, fav: false, active: true, sort: T.subjects.length });
    T.subjects.push(s); T.subjDraft = ''; T.tafel = null; T.render();
  };
  ACT.subjDraft = function (el) { T.subjDraft = el.value; };
  ACT.resetFav = async function () {
    if (!armed('resetFav')) return T.render();
    var del = T.subjects.filter(function (s) { return !s.fav; }).map(function (s) { return s.id; });
    await DB.deleteSubjects(del);
    T.subjects = T.subjects.filter(function (s) { return s.fav; });
    for (var i = 0; i < T.subjects.length; i++) if (!T.subjects[i].active) { T.subjects[i].active = true; await DB.updateSubject(T.subjects[i].id, { active: true }); }
    T.tafel = null; toast('Nur noch die Favoriten sind auf der Tafel.'); T.render();
  };
  ACT.tafelAuto = async function () { var c = T.cur(); c.tafel_auto = !c.tafel_auto; T.render(); await DB.updateClass(c.id, { tafel_auto: c.tafel_auto }); };
  ACT.tafelClear = async function () {
    if (!armed('clearTafel')) return T.render();
    await DB.clearTafel(T.cls); T.tafel = null; toast('Alle Namen wurden von der Tafel genommen.'); T.render();
  };
  ACT.tafelRefresh = function () { T.tafel = null; T.render(); };

  // ---------- Konto ----------
  T.account = function () {
    var c = T.cur(), delKey = 'delClass';
    overlay('<div class="dialog" role="dialog" aria-label="Konto und Klassen"><div class="row" style="justify-content:space-between"><h2 style="font-size:26px">Konto und Klassen</h2>' +
      '<button class="btn sm" data-a="closeOverlay">Schliessen</button></div>' +
      '<form class="stack" data-a="saveName"><div class="field"><label for="accName">Ihr Name</label><div class="row"><input class="input grow" style="flex:1 1 200px" id="accName" name="name" value="' + h(T.me.name) + '" required><button class="btn">Speichern</button></div></div></form>' +
      '<form class="stack" data-a="savePw"><div class="field"><label for="accPw">Neues Passwort (mindestens 8 Zeichen)</label><input class="input" id="accPw" name="pw" type="password" minlength="8" autocomplete="new-password" required></div>' +
      '<div class="field"><label for="accPw2">Passwort wiederholen</label><input class="input" id="accPw2" name="pw2" type="password" minlength="8" autocomplete="new-password" required></div>' +
      '<button class="btn">Passwort ändern</button></form>' +
      (c ? '<div class="stack" style="padding-top:14px;border-top:1.5px solid var(--line)"><h3 style="font-size:20px">Klasse ' + h(c.name) + ' · Code ' + h(c.code) + '</h3>' +
        '<form class="row" data-a="renameClass"><label class="sr" for="accCls">Neuer Klassenname</label><input class="input grow" style="flex:1 1 180px" id="accCls" name="cname" value="' + h(c.name) + '" required maxlength="30"><button class="btn">Umbenennen</button></form>' +
        '<div class="row"><button class="btn" data-a="newCode">Neuen Klassencode erstellen</button><button class="btn danger' + (UI.confirm === delKey ? ' armed' : '') + '" data-a="delClass">' +
        (UI.confirm === delKey ? 'Klasse mit allen Kindern löschen?' : 'Klasse löschen') + '</button></div>' +
        '<p class="muted small">Mit einem neuen Code funktioniert der alte nicht mehr.</p></div>' : '') +
      '<form class="stack" data-a="createClass" style="padding-top:14px;border-top:1.5px solid var(--line)"><div class="field"><label for="accNew">Weitere Klasse anlegen</label>' +
      '<div class="row"><input class="input grow" style="flex:1 1 180px" id="accNew" name="cname" placeholder="z. B. 6b" required maxlength="30"><button class="btn primary">Anlegen</button></div></div></form></div>');
  };
  ACT.account = function () { T.account(); };
  ACT.savePw = async function (f) {
    if (f.elements.pw.value !== f.elements.pw2.value) return toast('Die beiden Passwörter sind nicht gleich.');
    await DB.setPassword(f.elements.pw.value); toast('Passwort geändert.'); closeOverlays();
  };
  ACT.renameClass = async function (f) {
    var c = T.cur(), n = f.elements.cname.value.trim(); if (!n) return;
    await DB.updateClass(c.id, { name: n }); c.name = n; toast('Klasse umbenannt.'); T.account(); T.render();
  };
  ACT.newCode = async function () {
    var c = T.cur();
    await withFreeCode(function (code) { return DB.updateClass(c.id, { code: code }).then(function () { c.code = code; }); });
    toast('Neuer Klassencode: ' + c.code); T.account(); T.render();
  };
  ACT.delClass = async function () {
    if (!armed('delClass')) return T.account();
    var c = T.cur(); await DB.deleteClass(c.id);
    T.classes = T.classes.filter(function (x) { return x.id !== c.id; });
    T.cls = T.classes[0] ? T.classes[0].id : null; LS.set('kn_cls', T.cls);
    await T.loadClass(); closeOverlays(); toast('Klasse gelöscht.'); T.render();
  };

  // ---------- Verwaltung (nur Admin) ----------
  function blankForm() { return { id: null, title: '', description: '', fach: '', thema: '', stufe: '', for_all: false, html: null, filename: '' }; }
  T.tabAdmin = function () {
    var A = T.admin; if (!A.form) A.form = blankForm();
    if (A.teachers === null && !A.busy) {
      A.busy = true;
      Promise.all([DB.listTeachers(), DB.listTeacherGames()]).then(function (r) { A.teachers = r[0]; A.tg = r[1]; A.busy = false; if (T.tab === 'verwaltung') T.render(); })
        .catch(function (e) { A.busy = false; toast(errMsg(e)); });
    }
    var F = A.form;
    var fachs = uniq(T.games.map(function (g) { return g.fach; }).concat(['Mathematik', 'Deutsch', 'Englisch', 'NMG', 'Französisch', 'Gestalten', 'Musik']));
    var themen = uniq(T.games.filter(function (g) { return !F.fach || g.fach === F.fach; }).map(function (g) { return g.thema; }));
    var form = '<form class="card stack" data-a="gSave"><h2>' + (F.id ? 'Spiel bearbeiten' : 'Neues Spiel hochladen') + '</h2>' +
      '<div class="field"><label for="gFile">Spiel-Datei (.html)' + (F.id ? ' – nur wählen, wenn Sie die Datei ersetzen möchten' : '') + '</label>' +
      '<input class="input" id="gFile" type="file" accept=".html,.htm,text/html" data-change="gFile">' +
      (F.filename ? '<span class="muted small">Gewählt: ' + h(F.filename) + '</span>' : '') + '</div>' +
      '<div class="field"><label for="gTitle">Titel</label><input class="input" id="gTitle" value="' + h(F.title) + '" data-input="gField" data-k="title" required maxlength="80"></div>' +
      '<div class="field"><label for="gDesc">Kurzbeschreibung</label><input class="input" id="gDesc" value="' + h(F.description) + '" data-input="gField" data-k="description" maxlength="160"></div>' +
      '<div class="row" style="align-items:flex-start"><div class="field grow" style="flex:1 1 200px"><label for="gFach">Fach</label><input class="input" id="gFach" list="fachList" value="' + h(F.fach) + '" data-input="gField" data-k="fach" required maxlength="40"></div>' +
      '<div class="field grow" style="flex:1 1 200px"><label for="gThema">Thema</label><input class="input" id="gThema" list="themaList" value="' + h(F.thema) + '" data-input="gField" data-k="thema" placeholder="z. B. Raster & Koordinaten" maxlength="60"></div>' +
      '<div class="field grow" style="flex:1 1 140px"><label for="gStufe">Stufe</label><input class="input" id="gStufe" value="' + h(F.stufe) + '" data-input="gField" data-k="stufe" placeholder="z. B. 5./6. Klasse oder Zusatz" maxlength="30"></div></div>' +
      '<datalist id="fachList">' + fachs.map(function (f) { return '<option value="' + h(f) + '">'; }).join('') + '</datalist>' +
      '<datalist id="themaList">' + themen.map(function (t) { return '<option value="' + h(t) + '">'; }).join('') + '</datalist>' +
      '<button type="button" class="switch" role="switch" aria-checked="' + F.for_all + '" data-a="gAll"><span>Für alle Lehrpersonen freischalten</span><span class="track"></span></button>' +
      '<div class="row"><button class="btn primary">' + (F.id ? 'Änderungen speichern' : 'Spiel speichern') + '</button>' + (F.id ? '<button type="button" class="btn" data-a="gCancel">Abbrechen</button>' : '') + '</div>' +
      '<p class="muted small">Tipp für Fortschritt: Ein Spiel kann <code>knobelnest.answer(true/false)</code> oder <code>knobelnest.progress(erledigt, total)</code> aufrufen. Spiele aus dem Spielheft melden sich automatisch.</p></form>';
    var sel = A.sel || (A.sel = {}), nSel = Object.keys(sel).length;
    var afs = uniq(T.games.map(function (g) { return g.fach; })); if (afs.indexOf(A.fach) < 0) A.fach = 'alle';
    var ats = A.fach === 'alle' ? [] : uniq(T.games.filter(function (g) { return g.fach === A.fach; }).map(function (g) { return g.thema; }));
    if (ats.indexOf(A.thema) < 0) A.thema = 'alle';
    var FG = adminGames();
    var fchips = afs.length > 1 ? '<div class="chips" role="group" aria-label="Nach Fach filtern">' + ['alle'].concat(afs).map(function (f) {
      var n = f === 'alle' ? T.games.length : T.games.filter(function (g) { return g.fach === f; }).length;
      return '<button class="chip" aria-pressed="' + (A.fach === f) + '" data-a="aFach" data-f="' + h(f) + '">' + (f === 'alle' ? 'Alle Fächer' : h(f)) + ' · ' + n + '</button>'; }).join('') + '</div>' +
      (ats.length > 1 ? '<div class="chips" role="group" aria-label="Nach Thema filtern" style="margin-top:-4px;padding-left:14px;border-left:3px solid var(--line2)">' + ['alle'].concat(ats).map(function (t) {
        var n = T.games.filter(function (g) { return g.fach === A.fach && (t === 'alle' || g.thema === t); }).length;
        return '<button class="chip" style="min-height:38px" aria-pressed="' + (A.thema === t) + '" data-a="aThema" data-t="' + h(t) + '">' + (t === 'alle' ? 'Alle Themen' : h(t)) + ' · ' + n + '</button>'; }).join('') + '</div>' : '') : '';
    var others = (A.teachers || []).filter(function (t) { return !t.is_admin; });
    var bulk = T.games.length ? '<div class="card row" style="padding:14px 16px;position:sticky;top:110px;z-index:3' + (nSel ? ';border-color:var(--green);box-shadow:0 4px 0 var(--green)' : '') + '">' +
      '<b class="grow">' + (nSel ? plural(nSel, 'Spiel', 'Spiele') + ' ausgewählt' : 'Spiele anhaken, um sie einer Lehrperson auf einmal zu geben') + '</b>' +
      (nSel ? '<label class="sr" for="bulkT">Lehrperson</label><select class="input" id="bulkT" style="width:auto;min-height:44px" data-change="bulkT">' +
        '<option value="">Lehrperson wählen …</option>' + others.map(function (t) { return '<option value="' + t.id + '"' + (A.bulkT === t.id ? ' selected' : '') + '>' + h(t.name || t.email) + '</option>'; }).join('') + '</select>' +
        '<button class="btn sm primary" data-a="bulkGo" data-on="1">Zuteilen</button><button class="btn sm" data-a="bulkGo" data-on="0">Wegnehmen</button>' +
        '<button class="btn sm" data-a="bulkClear">Auswahl aufheben</button>' : '') + '</div>' : '';
    var allSel = FG.length && FG.every(function (g) { return sel[g.id]; });
    var glist = T.games.length ? bulk + '<div class="tablewrap"><table><thead><tr><th style="width:44px"><input type="checkbox" aria-label="Alle Spiele auswählen" style="width:22px;height:22px" data-change="gSelAll"' + (allSel ? ' checked' : '') + '></th><th>Spiel</th><th>Fach › Thema</th><th>Zugang</th><th></th></tr></thead><tbody>' + FG.map(function (g) {
      var key = 'game:' + g.id;
      return '<tr><td><input type="checkbox" aria-label="' + h(g.title) + ' auswählen" style="width:22px;height:22px" data-change="gSel" data-id="' + g.id + '"' + (sel[g.id] ? ' checked' : '') + '></td><td><b>' + h(g.title) + '</b>' + (g.stufe ? '<br><span class="muted small">' + h(g.stufe) + '</span>' : '') + '</td><td>' + h(g.fach) + ' › ' + h(g.thema) + '</td>' +
        '<td><button class="switch" style="min-height:44px;min-width:190px" role="switch" aria-checked="' + g.for_all + '" data-a="gAllToggle" data-id="' + g.id + '"><span>' + (g.for_all ? 'Für alle' : 'Nur zugeteilt') + '</span><span class="track"></span></button></td><td><div class="row" style="justify-content:flex-end;flex-wrap:nowrap">' +
        '<button class="btn sm" data-a="preview" data-id="' + g.id + '">Ansehen</button><button class="btn sm" data-a="gEdit" data-id="' + g.id + '">Bearbeiten</button>' +
        '<button class="btn sm danger' + (UI.confirm === key ? ' armed' : '') + '" data-a="gDel" data-id="' + g.id + '">' + (UI.confirm === key ? 'Wirklich?' : 'Löschen') + '</button></div></td></tr>';
    }).join('') + '</tbody></table></div>' : '<div class="empty">Noch keine Spiele hochgeladen.</div>';
    var teachers = A.teachers === null ? '<p class="muted">Wird geladen …</p>' : '<ul class="list">' + A.teachers.map(function (t) {
      var mine = A.tg.filter(function (x) { return x.teacher_id === t.id; }).map(function (x) { return x.game_id; });
      var open = A.open === t.id;
      return '<li style="flex-direction:column;align-items:stretch"><div class="row"><span class="avatar">' + h(initials(t.name || t.email)) + '</span><span class="grow"><b>' + h(t.name || '(noch kein Name)') + '</b>' +
        (t.is_admin ? ' <span class="pill" style="background:#A8E6CF">Admin</span>' : '') + '<br><span class="muted small">' + h(t.email) + '</span></span>' +
        '<span class="muted small">' + (t.is_admin ? 'sieht alle Spiele' : plural(mine.length, 'Spiel', 'Spiele') + ' zugeteilt') + '</span>' +
        (t.is_admin ? '' : '<button class="btn sm" data-a="tOpen" data-id="' + t.id + '" aria-expanded="' + open + '">' + (open ? 'Schliessen' : 'Spiele zuteilen') + '</button>') + '</div>' +
        (open ? (function () {
          var ids = function (list) { return list.filter(function (g) { return !g.for_all; }).map(function (g) { return g.id; }).join(','); };
          var groups = [], by = {};
          FG.forEach(function (g) { var k = g.fach + ' › ' + g.thema; if (!by[k]) { by[k] = []; groups.push(k); } by[k].push(g); });
          return '<div class="stack" style="gap:14px;padding:12px 0 6px">' +
            '<div class="row"><button class="btn sm" data-a="tgBulk" data-t="' + t.id + '" data-on="1" data-ids="' + ids(FG) + '">' + (A.fach === 'alle' ? 'Alle Spiele geben' : 'Alle ' + h(A.thema !== 'alle' ? A.thema : A.fach) + '-Spiele geben') + '</button>' +
            '<button class="btn sm" data-a="tgBulk" data-t="' + t.id + '" data-on="0" data-ids="' + ids(FG) + '">' + (A.fach === 'alle' ? 'Alle wegnehmen' : 'Alle ' + h(A.thema !== 'alle' ? A.thema : A.fach) + '-Spiele wegnehmen') + '</button></div>' +
            '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px">' + groups.map(function (k) {
              var list = by[k], free = list.filter(function (g) { return !g.for_all; });
              var allOn = free.length && free.every(function (g) { return mine.indexOf(g.id) >= 0; });
              return '<div class="card stack" style="padding:14px;gap:8px"><div class="row" style="justify-content:space-between"><b>' + h(k) + '</b>' +
                (free.length ? '<button class="btn sm" data-a="tgBulk" data-t="' + t.id + '" data-on="' + (allOn ? 0 : 1) + '" data-ids="' + ids(list) + '">' + (allOn ? 'Thema wegnehmen' : 'Ganzes Thema') + '</button>' : '') + '</div>' +
                list.map(function (g) {
                  var on = g.for_all || mine.indexOf(g.id) >= 0;
                  return '<label class="row" style="gap:10px;font-size:16px;flex-wrap:nowrap"><input type="checkbox" style="width:22px;height:22px;flex:none" ' + (on ? 'checked ' : '') + (g.for_all ? 'disabled ' : '') +
                    'data-change="tgSet" data-t="' + t.id + '" data-g="' + g.id + '"><span>' + h(g.title) + (g.for_all ? ' <span class="muted small">· für alle</span>' : '') + '</span></label>';
                }).join('') + '</div>';
            }).join('') + '</div></div>';
        })() : '') + '</li>';
    }).join('') + '</ul>';
    var pack = '<section class="card stack"><h2>Spielpaket importieren</h2><p class="muted">Mehrere Spiele auf einmal hochladen, zum Beispiel die Datei <b>knobelnest-spielpaket.json</b>. Spiele mit gleichem Titel werden übersprungen.</p>' +
      '<label class="row" style="gap:10px"><input type="checkbox" style="width:22px;height:22px" data-change="packUpd"' + (A.packUpd ? ' checked' : '') + '> Vorhandene Spiele mit gleichem Titel durch die neue Version ersetzen (Fach, Thema, Zuteilungen und Fortschritt bleiben)</label>' +
      '<div class="field"><label for="gPack">Spielpaket (.json)</label><input class="input" id="gPack" type="file" accept=".json,application/json" data-change="gPack"' + (A.importing ? ' disabled' : '') + '></div>' +
      (A.importing ? '<p class="note">' + h(A.importing) + '</p>' : '') + '</section>';
    return '<div class="stack" style="gap:8px"><h1 class="h1">Verwaltung</h1><p class="muted">Nur für Sie sichtbar: Spiele hochladen und Lehrpersonen Spiele zuteilen.</p></div>' +
      '<div class="cols2"><div class="wide">' + pack + form + '</div>' +
      '<aside class="side"><div class="note"><b>So teilen Sie Spiele zu:</b> Spiele mit «Nur zugeteilt» sehen nur die Lehrpersonen, denen Sie sie unten zuteilen. Spiele mit «Für alle» sehen alle Lehrpersonen.</div>' +
      '<div class="note"><b>Neue Lehrperson hinzufügen:</b> In Supabase links «Authentication» → «Users» → «Add user» → «Create new user». E-Mail und ein Startpasswort eingeben, «Auto Confirm User» anhaken. Danach erscheint die Person hier, und Sie können ihr Spiele zuteilen. Sie kann ihr Passwort oben rechts unter ihrem Namen ändern.</div></aside></div>' +
      '<section class="stack"><h2 style="font-size:26px">Alle Spiele</h2>' + fchips + glist + '</section>' +
      '<section class="stack"><h2 style="font-size:26px">Lehrpersonen und ihre Spiele</h2>' + (fchips ? '<p class="muted small" style="margin:0">Beim Zuteilen werden nur die hier gewählten Spiele gezeigt:</p>' + fchips : '') + teachers + '</section>';
  };
  ACT.gField = function (el) { T.admin.form[el.dataset.k] = el.value; };
  ACT.gAll = function () { T.admin.form.for_all = !T.admin.form.for_all; T.render(); };
  ACT.gFile = function (el) {
    var file = el.files && el.files[0]; if (!file) return;
    if (file.size > 8 * 1024 * 1024) return toast('Die Datei ist zu gross (höchstens 8 MB).');
    var r = new FileReader();
    r.onload = function () {
      var F = T.admin.form; F.html = String(r.result); F.filename = file.name;
      if (!F.title) { var m = /<title[^>]*>([^<]*)<\/title>/i.exec(F.html); F.title = (m ? m[1] : file.name.replace(/\.html?$/i, '')).trim().slice(0, 80); }
      T.render();
    };
    r.readAsText(file, 'utf-8');
  };
  ACT.gPack = function (el) {
    var file = el.files && el.files[0]; if (!file) return;
    var r = new FileReader();
    r.onload = async function () {
      var A = T.admin, data;
      try { data = JSON.parse(String(r.result)); } catch (e) { return toast('Diese Datei ist kein gültiges Spielpaket.'); }
      if (!data || data.format !== 'knobelnest-spielpaket' || !Array.isArray(data.games)) return toast('Diese Datei ist kein Knobelnest-Spielpaket.');
      var have = {}; T.games.forEach(function (g) { have[g.title.toLowerCase()] = g; });
      var valid = data.games.filter(function (g) { return g && g.title && g.fach && g.html; });
      var todo = valid.filter(function (g) { return A.packUpd || !have[String(g.title).toLowerCase()]; });
      var skipped = valid.length - todo.length, added = 0, updated = 0, failed = 0;
      for (var i = 0; i < todo.length; i++) {
        var g = todo[i], old = have[String(g.title).toLowerCase()];
        A.importing = 'Spiel ' + (i + 1) + ' von ' + todo.length + (old ? ' wird aktualisiert: ' : ' wird hochgeladen: ') + g.title; T.render();
        try {
          if (old) { await DB.saveGame({ id: old.id, title: old.title, description: old.description, fach: old.fach, thema: old.thema, stufe: old.stufe || String(g.stufe || '').slice(0, 30), for_all: old.for_all, sort: old.sort || (isFinite(g.sort) ? +g.sort : 0), html: String(g.html) }); updated++; }
          else {
            await DB.saveGame({ title: String(g.title).slice(0, 80), description: String(g.description || '').slice(0, 160), fach: String(g.fach).slice(0, 40),
              thema: String(g.thema || 'Allgemein').slice(0, 60), stufe: String(g.stufe || '').slice(0, 30), for_all: g.for_all === true, sort: isFinite(g.sort) ? +g.sort : 0, html: String(g.html) });
            added++;
          }
        } catch (e) { failed++; console.error(e); }
      }
      A.importing = null; T.games = await DB.listGames(); T.render();
      toast(plural(added, 'Spiel', 'Spiele') + ' neu' + (updated ? ', ' + updated + ' aktualisiert' : '') + (skipped ? ', ' + skipped + ' schon vorhanden' : '') + (failed ? ', ' + failed + ' fehlgeschlagen' : '') + '.');
    };
    r.readAsText(file, 'utf-8');
  };
  ACT.packUpd = function (el) { T.admin.packUpd = el.checked; };
  ACT.gSave = async function () {
    var F = T.admin.form;
    if (!F.title.trim() || !F.fach.trim()) return toast('Bitte Titel und Fach ausfüllen.');
    if (!F.id && !F.html) return toast('Bitte eine Spiel-Datei wählen.');
    await DB.saveGame({ id: F.id, title: F.title.trim(), description: F.description.trim(), fach: F.fach.trim(), thema: F.thema.trim() || 'Allgemein',
      stufe: F.stufe.trim(), for_all: F.for_all, html: F.html });
    toast(F.id ? 'Spiel gespeichert.' : 'Spiel hochgeladen.');
    T.admin.form = blankForm(); T.games = await DB.listGames(); T.render();
  };
  ACT.gEdit = function (el) {
    var g = T.games.filter(function (x) { return x.id === el.dataset.id; })[0];
    T.admin.form = { id: g.id, title: g.title, description: g.description, fach: g.fach, thema: g.thema, stufe: g.stufe, for_all: g.for_all, html: null, filename: '' };
    T.render(); window.scrollTo(0, 0);
  };
  ACT.gCancel = function () { T.admin.form = blankForm(); T.render(); };
  ACT.gDel = async function (el) {
    if (!armed('game:' + el.dataset.id)) return T.render();
    await DB.deleteGame(el.dataset.id); T.games = await DB.listGames(); T.rel.delete(el.dataset.id); toast('Spiel gelöscht.'); T.render();
  };
  ACT.gSel = function (el) { var s = T.admin.sel; if (el.checked) s[el.dataset.id] = 1; else delete s[el.dataset.id]; T.render(); };
  function adminGames() {
    var f = T.admin.fach || 'alle', t = f === 'alle' ? 'alle' : (T.admin.thema || 'alle');
    return T.games.filter(function (g) { return (f === 'alle' || g.fach === f) && (t === 'alle' || g.thema === t); });
  }
  ACT.aFach = function (el) { T.admin.fach = el.dataset.f; T.admin.thema = 'alle'; T.render(); };
  ACT.aThema = function (el) { T.admin.thema = el.dataset.t; T.render(); };
  ACT.gSelAll = function (el) { T.admin.sel = {}; if (el.checked) adminGames().forEach(function (g) { T.admin.sel[g.id] = 1; }); T.render(); };
  ACT.bulkClear = function () { T.admin.sel = {}; T.render(); };
  ACT.bulkT = function (el) { T.admin.bulkT = el.value; };
  ACT.bulkGo = async function (el) {
    var A = T.admin, t = A.bulkT, ids = Object.keys(A.sel), on = el.dataset.on === '1';
    if (!t) return toast('Bitte zuerst eine Lehrperson wählen.');
    await DB.setTeacherGames(t, ids, on);
    A.tg = A.tg.filter(function (x) { return !(x.teacher_id === t && ids.indexOf(x.game_id) >= 0); });
    if (on) ids.forEach(function (g) { A.tg.push({ teacher_id: t, game_id: g }); });
    var who = (A.teachers.filter(function (x) { return x.id === t; })[0] || {});
    toast(plural(ids.length, 'Spiel', 'Spiele') + (on ? ' an ' : ' weggenommen von ') + (who.name || who.email) + (on ? ' zugeteilt.' : '.'));
    T.render();
  };
  ACT.gAllToggle = async function (el) {
    var g = T.games.filter(function (x) { return x.id === el.dataset.id; })[0];
    await DB.setGameForAll(g.id, !g.for_all); g.for_all = !g.for_all;
    toast(g.title + (g.for_all ? ': für alle Lehrpersonen.' : ': nur noch für zugeteilte Lehrpersonen.')); T.render();
  };
  ACT.tgBulk = async function (el) {
    var t = el.dataset.t, on = el.dataset.on === '1', ids = (el.dataset.ids || '').split(',').filter(Boolean);
    if (!ids.length) return;
    await DB.setTeacherGames(t, ids, on);
    T.admin.tg = T.admin.tg.filter(function (x) { return !(x.teacher_id === t && ids.indexOf(x.game_id) >= 0); });
    if (on) ids.forEach(function (g) { T.admin.tg.push({ teacher_id: t, game_id: g }); });
    T.render();
  };
  ACT.tOpen = function (el) { T.admin.open = T.admin.open === el.dataset.id ? null : el.dataset.id; T.render(); };
  ACT.tgSet = async function (el) {
    var t = el.dataset.t, g = el.dataset.g, on = el.checked;
    await DB.setTeacherGame(t, g, on);
    if (on) T.admin.tg.push({ teacher_id: t, game_id: g });
    else T.admin.tg = T.admin.tg.filter(function (x) { return !(x.teacher_id === t && x.game_id === g); });
    T.render();
  };

  // ===================================================================
  // Kinder
  // ===================================================================
  var K = { step: 'code', code: null, cls: null, kid: null, pw: [], sess: null, home: null, fach: null, thema: null, tafel: null, err: '', busy: false };

  K.start = async function () {
    UI.view = 'kid';
    K.err = ''; K.pw = [];
    var m = (location.hash || '').match(/^#\/klasse\/([^/?#]+)/);
    if (m) {
      var given = decodeURIComponent(m[1]);
      try { history.replaceState(null, '', location.pathname + location.search + '#/klasse'); } catch (e) {}
      var old = LS.get('kn_kid');
      if (old && String(old.code || '').replace(/\s+/g, '').toUpperCase() !== given.toUpperCase()) { DB.kidLogout(old.token); LS.del('kn_kid'); }
      LS.set('kn_code', given);
    }
    var s = LS.get('kn_kid');
    if (s && s.exp > Date.now()) { K.sess = s; K.step = 'home'; return K.loadHome(); }
    LS.del('kn_kid'); K.sess = null;
    var code = LS.get('kn_code');
    if (code) {
      try { var c = await DB.kidClass(code); if (c) { K.code = code; K.cls = c; K.step = 'names'; return K.render(); } } catch (e) {}
    }
    K.step = 'code'; K.render();
  };
  K.loadHome = async function () {
    try { K.home = await DB.kidHome(K.sess.token); }
    catch (e) { return K.sessionLost(e); }
    K.render(); K.checkRace();
    if (!K.raceWatch) K.raceWatch = setInterval(function () { if (K.sess && UI.view === 'kid' && K.step === 'home' && !document.hidden) K.checkRace(); }, 4000);
  };
  K.sessionLost = function (e) {
    if (/Anmeldung|session/i.test((e && e.message) || '')) {
      LS.del('kn_kid'); K.sess = null; K.home = null; toast('Bitte melde dich nochmals an.'); return K.start();
    }
    toast(errMsg(e));
  };
  K.shell = function (body, back) {
    return '<div class="kid"><div class="kid-in"><div class="kid-top"><span class="logo">' + I.logo + h(C.PORTAL_NAME) + '</span>' +
      (back ? '<button class="kid-btn" data-a="kBack">' + back + '</button>' : '<a class="kid-btn" href="#/" style="display:inline-flex;align-items:center;text-decoration:none;color:var(--ink);border-width:1.5px;font-size:15px">Für Lehrpersonen</a>') +
      '</div>' + body + '</div></div>';
  };
  K.render = function () {
    var b = K['view_' + K.step](); if (b == null) return;
    paint(b);
  };
  // Fortschritt eines Spiels: zuletzt gespieltes Level zuerst
  function lvlInfo(p) {
    var lv = (p && p.levels) || {}, keys = Object.keys(lv);
    if (p && p.last_level && keys.indexOf(p.last_level) > 0) { keys.splice(keys.indexOf(p.last_level), 1); keys.unshift(p.last_level); }
    return keys.map(function (k) { var x = lv[k] || {}; return { name: k, c: x.c || 0, a: x.a || 0, d: x.d, t: x.t }; });
  }
  function lvlText(x) { return x.t ? (x.d || 0) + ' von ' + x.t + ' geschafft' : x.c + ' richtig, ' + (x.a - x.c) + ' falsch'; }
  function pct(g) {
    var l = lvlInfo(g)[0];
    if (l) return l.t ? Math.min(100, Math.round((l.d || 0) / l.t * 100)) : null;
    return g.total ? Math.min(100, Math.round((g.done || 0) / g.total * 100)) : null;
  }

  K.view_code = function () {
    return K.shell('<form class="kid-card" data-a="kCode"><h1>Hallo!</h1><p class="lead">Gib den Code ein, den deine Lehrerin oder dein Lehrer an die Wandtafel geschrieben hat.</p>' +
      '<label class="sr" for="kCode">Klassencode</label><input class="kid-input" id="kCode" name="code" placeholder="FUCHS 123" autocomplete="off" autocapitalize="characters" spellcheck="false" required>' +
      '<p class="err" style="font-size:18px">' + h(K.err) + '</p><button class="kid-go">Weiter</button></form>');
  };
  K.view_names = function () {
    return K.shell('<div class="stack" style="gap:6px"><h1>Wer bist du?</h1><p class="lead">Klasse ' + h(K.cls.class_name) + ' · Tippe auf deinen Namen.</p></div>' +
      (K.cls.kids.length ? '<div class="kid-grid">' + K.cls.kids.map(function (k) {
        return '<button class="kid-name" data-a="kName" data-id="' + k.id + '"><span class="ini" style="background:' + kidColor(k.name) + '">' + h(k.name.charAt(0)) + '</span><b>' + h(k.name) + '</b></button>';
      }).join('') + '</div>' : '<div class="kid-card"><p class="lead">In dieser Klasse sind noch keine Kinder eingetragen.</p></div>'), 'Anderer Code');
  };
  K.view_pw = function () {
    var full = K.pw.length >= 3;
    return K.shell('<div class="kid-card"><h1>Hallo ' + h(K.kid.name) + '!</h1><p class="lead">Tippe deine drei Bilder in der richtigen Reihenfolge an.</p>' +
      '<div class="slots" aria-label="' + K.pw.length + ' von 3 Bildern gewählt">' + [0, 1, 2].map(function (i) {
        return '<span class="slot' + (i < K.pw.length ? ' on' : '') + '">' + (i < K.pw.length ? ic(I.check, 30, '#fff', 3) : '') + '</span>'; }).join('') + '</div>' +
      '<div class="syms">' + SYM_IDS.map(function (id) {
        return '<button class="sym" style="background:' + SYM[id].bg + '" aria-label="' + SYM[id].label + '" data-a="kSym" data-s="' + id + '"' + (full ? ' disabled' : '') + '>' + symSvg(id, 54) + '</button>';
      }).join('') + '</div><p class="err" style="font-size:18px">' + h(K.err) + '</p>' +
      '<div class="row" style="flex-wrap:nowrap"><button class="kid-btn" style="flex:1;height:62px;background:#fff" data-a="kClear">Nochmals</button>' +
      '<button class="kid-go" style="flex:2;height:62px" data-a="kLogin"' + (full && !K.busy ? '' : ' disabled') + '>Einloggen</button></div>' +
      '<p class="muted">Bilder vergessen? Frag deine Lehrperson.</p></div>', 'Zurück');
  };
  K.view_home = function () {
    if (!K.home) return K.shell('<p class="lead">Wird geladen …</p>', 'Abmelden');
    var games = K.home.games, fachs = uniq(games.map(function (g) { return g.fach; }));
    var tiles = fachs.map(function (f) {
      var n = games.filter(function (g) { return g.fach === f; }).length;
      return '<button class="big-tile" style="background:' + fachColor(f) + '" data-a="kFach" data-f="' + h(f) + '"><span class="ic">' + h(f.charAt(0)) + '</span><b>' + h(f) + '</b><span>' + plural(n, 'Spiel', 'Spiele') + '</span></button>';
    }).join('');
    return K.shell('<div class="stack" style="gap:6px"><h1>Hallo ' + h(K.home.kid.name) + '!</h1><p class="lead">' + (fachs.length ? 'Welches Fach möchtest du üben?' : 'Deine Lehrperson hat noch keine Spiele freigegeben.') + '</p></div>' +
      (K.raceOpen ? '<button class="sprint-tile" data-a="kRace"><span class="ic">🏃</span><span><b>Sprint!</b><span>Deine Lehrperson hat einen Klassen-Sprint geöffnet. Tippe hier, um mitzumachen.</span></span></button>' : '') +
      (tiles ? '<div class="big-tiles">' + tiles + '</div>' : '') +
      '<button class="tafel-tile" data-a="kTafel"><span class="ic" style="flex:none;width:60px;height:60px;border-radius:16px;background:#fff;border:2px solid var(--ink);display:grid;place-items:center">' + ic(I.board, 34, '#1B2A3D', 2) + '</span>' +
      '<span><b>Unsere Tafel</b><span>Zeig, wo du im Wochenplan stehst, und finde Hilfe.</span></span></button>', 'Abmelden');
  };
  K.view_thema = function () {
    var games = K.home.games.filter(function (g) { return g.fach === K.fach; });
    var themen = uniq(games.map(function (g) { return g.thema; }));
    return K.shell('<div class="stack" style="gap:6px"><p class="lead" style="font-weight:700">' + h(K.fach) + '</p><h1>Wähle ein Thema</h1></div><div class="big-tiles">' + themen.map(function (t) {
      var gs = games.filter(function (g) { return g.thema === t; });
      var played = gs.filter(function (g) { return g.plays; }).length;
      var stars = gs.reduce(function (n, g) { var a = g.award || {}; return n + (typeof a.stars === 'number' ? a.stars : awardSum(a)); }, 0);
      return '<button class="big-tile" style="min-height:150px" data-a="kThema" data-t="' + h(t) + '"><b style="font-size:30px">' + h(t) + '</b><span>' + plural(gs.length, 'Spiel', 'Spiele') + '</span>' +
        '<span style="margin-top:auto;font-size:17px;font-weight:400">' + (played ? 'Schon gespielt: ' + played + ' von ' + gs.length : 'Noch nichts gespielt') + '</span>' + (stars ? '<span class="kaward">⭐ ' + stars + '</span>' : '') + '</button>';
    }).join('') + '</div>', 'Zurück');
  };
  K.view_games = function () {
    var games = K.home.games.filter(function (g) { return g.fach === K.fach && g.thema === K.thema; });
    return K.shell('<div class="stack" style="gap:6px"><p class="lead" style="font-weight:700">' + h(K.fach) + ' › ' + h(K.thema) + '</p><h1>Wähle ein Spiel</h1></div><div class="big-tiles">' + games.map(function (g) {
      var p = pct(g), l = lvlInfo(g)[0];
      var label = l ? 'Zuletzt: ' + l.name + ' · ' + (l.t ? (l.d || 0) + ' von ' + l.t + ' geschafft' : plural(l.c, 'Aufgabe', 'Aufgaben') + ' richtig') :
        g.total ? (g.done || 0) + ' von ' + g.total + ' geschafft' : g.attempts ? g.correct + ' Aufgaben richtig gelöst' : g.plays ? 'Schon ' + g.plays + '× gespielt' : 'Noch nicht gespielt';
      var extra = /zusatz/i.test(g.stufe || '');
      return '<article class="big-tile' + (extra ? ' extra' : '') + '" style="cursor:default;padding:0;overflow:hidden;gap:0"><div style="width:100%;padding:14px 22px;background:' + fachColor(g.fach) + ';border-bottom:3px solid var(--ink);font-family:var(--h);font-weight:500;display:flex;justify-content:space-between;align-items:center;gap:8px">' + h(g.thema) +
        (extra ? '<span class="zusatz">★ Zusatz</span>' : '') + '</div>' +
        '<div class="stack" style="padding:20px 22px 24px;width:100%;flex:1"><b style="font-size:28px">' + h(g.title) + '</b>' +
        (awardText(g.award) ? '<span class="kaward">' + h(awardText(g.award)) + '</span>' : '') +
        (p == null ? '' : '<span class="kbar"><i style="width:' + p + '%"></i></span>') + '<span style="font-size:17px">' + h(label) + '</span>' +
        '<button class="kid-go" style="margin-top:auto;height:60px;font-size:22px;' + fachBtn(g.fach) + '" data-a="kPlay" data-id="' + g.id + '">' + (g.plays ? 'Weiterspielen' : 'Starten') + '</button></div></article>';
    }).join('') + '</div>', 'Zurück');
  };
  K.view_tafel = function () {
    if (!K.tafel) return K.shell('<p class="lead">Tafel wird geladen …</p>', 'Zurück');
    return board(K.tafel, 'kid');
  };

  ACT.kCode = async function (f) {
    var code = f.elements.code.value.trim(); if (!code) return;
    var c = await DB.kidClass(code);
    if (!c) { K.err = 'Diesen Code kennen wir nicht. Schau nochmals an der Wandtafel.'; return K.render(); }
    K.err = ''; K.code = code; K.cls = c; LS.set('kn_code', code); K.step = 'names'; K.render();
  };
  ACT.kName = function (el) {
    K.kid = K.cls.kids.filter(function (k) { return k.id === el.dataset.id; })[0];
    K.pw = []; K.err = ''; K.step = 'pw'; K.render();
  };
  ACT.kSym = function (el) { if (K.pw.length < 3) { K.pw.push(el.dataset.s); K.err = ''; K.render(); } };
  ACT.kClear = function () { K.pw = []; K.err = ''; K.render(); };
  ACT.kLogin = async function () {
    if (K.pw.length < 3 || K.busy) return;
    K.busy = true;
    try {
      var r = await DB.kidLogin(K.code, K.kid.id, K.pw.join(','));
      if (!r.ok) {
        K.pw = [];
        K.err = r.error === 'gesperrt' ? 'Kurze Pause! Versuch es in ' + Math.max(1, Math.ceil((r.seconds || 60) / 60)) + ' Minuten wieder.' :
          r.error === 'unbekannt' ? 'Das hat nicht geklappt. Gib den Code nochmals ein.' : 'Das waren nicht deine Bilder. Versuch es nochmals.';
        if (r.error === 'unbekannt') { LS.del('kn_code'); K.step = 'code'; }
        return K.render();
      }
      K.sess = { token: r.token, name: r.name, code: K.code, exp: Date.now() + 11.5 * 3600 * 1000 };
      LS.set('kn_kid', K.sess); K.home = null; K.step = 'home'; K.render(); await K.loadHome();
    } finally { K.busy = false; }
  };
  ACT.kFach = function (el) { K.fach = el.dataset.f; var th = uniq(K.home.games.filter(function (g) { return g.fach === K.fach; }).map(function (g) { return g.thema; }));
    if (th.length === 1) { K.thema = th[0]; K.step = 'games'; } else K.step = 'thema'; K.render(); };
  ACT.kThema = function (el) { K.thema = el.dataset.t; K.step = 'games'; K.render(); };
  ACT.kBack = async function () {
    stopTimers(); K.err = '';
    switch (K.step) {
      case 'names': LS.del('kn_code'); K.step = 'code'; break;
      case 'pw': K.step = 'names'; break;
      case 'home':
        if (K.sess) await DB.kidLogout(K.sess.token);
        LS.del('kn_kid'); K.sess = null; K.home = null; return K.start();
      case 'thema': K.step = 'home'; break;
      case 'games': var th = uniq(K.home.games.filter(function (g) { return g.fach === K.fach; }).map(function (g) { return g.thema; }));
        K.step = th.length === 1 ? 'home' : 'thema'; break;
      case 'tafel': K.step = 'home'; K.tafel = null; K.loadHome(); break;
      case 'race': clearInterval(K.raceIv); if (K.R && K.R.cd) clearInterval(K.R.cd); K.R = null; K.step = 'home'; K.loadHome(); break;
      default: K.step = 'home';
    }
    K.render();
  };
  // ---------- Sterne (wie im Lernheft) ----------
  // Ein Spiel kann im <head> festlegen, wie es Sterne gibt:
  //   <meta name="knobelnest-sterne" content='{"modus":"runde","n":10}'>                       10 Antworten = 1 Runde, bis 3 Sterne pro Level
  //   <meta name="knobelnest-sterne" content='{"modus":"sammeln","pro":10,"max":5,"proLevel":true}'>  je 10 richtige 1 Stern (1 pro Tag), höchstens 5
  //   <meta name="knobelnest-sterne" content='{"modus":"eigene"}'>                              das Spiel zählt selbst (knobelnest.award)
  function starCfg(html) {
    var m = /<meta\s+name=["']knobelnest-sterne["']\s+content=(["'])([\s\S]*?)\1/i.exec(html || ''), c = null;
    if (m) try { c = JSON.parse(m[2].replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&amp;/g, '&')); } catch (e) {}
    c = c || { modus: 'runde' };
    if (c.modus === 'sammeln') {
      var pf = {}; if (c.proFuer && typeof c.proFuer === 'object') Object.keys(c.proFuer).forEach(function (k) { pf[k] = Math.max(1, Math.min(100, +c.proFuer[k] || 10)); });
      return { modus: 'sammeln', pro: c.pro === 'runde' ? 'runde' : Math.max(1, Math.min(100, +c.pro || 10)), max: Math.max(1, Math.min(20, +c.max || 5)), proLevel: !!c.proLevel, proFuer: pf, proTag: c.proTag !== false };
    }
    if (c.modus === 'eigene' || c.modus === 'aus') return { modus: c.modus };
    return { modus: 'runde', n: Math.max(3, Math.min(100, +c.n || 10)) };
  }
  function starMax(c) { return c.modus === 'sammeln' ? c.max : c.modus === 'runde' ? 3 : 0; }
  // Wie viele richtige braucht es für einen Stern? (pro Level verschieden möglich, z. B. "Zeichnen": 1)
  function starPer(c, k) { var n = c.pro; Object.keys(c.proFuer || {}).forEach(function (p) { if (String(k).indexOf(p) === 0) n = c.proFuer[p]; }); return n; }
  function today() { return new Date().toLocaleDateString('sv-SE'); }
  function starRow(n, max, cls) { var o = ''; for (var i = 0; i < max; i++) o += '<span class="st' + (i < n ? '' : ' off') + (cls && i === n - 1 ? ' ' + cls : '') + '">★</span>'; return o; }
  function fmtTime(ms) { var t = Math.round(ms / 1000), m = Math.floor(t / 60); t %= 60; return m + ':' + (t < 10 ? '0' : '') + t; }
  function awardSum(a) { var n = 0, lv = (a && a.lv) || {}; Object.keys(lv).forEach(function (k) { n += +lv[k] || 0; }); return n; }
  // Kurztext für Übersichten: "⭐ 7 · ⏱️ 3:12"
  function awardText(a) {
    if (!a) return '';
    var parts = [], st = typeof a.stars === 'number' ? a.stars : awardSum(a);
    if (st) parts.push('⭐ ' + st + ' ' + (st === 1 ? 'Stern' : 'Sterne'));
    if (a.best) parts.push('⏱️ Bestzeit ' + fmtTime(a.best));
    return parts.join(' · ');
  }
  function Stars(cfg, award, base) {
    var S = { cfg: cfg, a: award && typeof award === 'object' ? award : {}, level: null, round: null, dirty: false, total: base || 0 };
    ['lv', 'box', 'boxDay', 'starDay'].forEach(function (k) { if (!S.a[k] || typeof S.a[k] !== 'object') S.a[k] = {}; });
    var a = S.a;
    function key() { return cfg.modus === 'sammeln' && !cfg.proLevel ? 'Spiel' : (S.level || 'Spiel'); }
    function maxFor() { return cfg.modus === 'sammeln' ? cfg.max : 3; }
    S.view = function () { return { lv: a.lv, max: maxFor() }; };
    function sync() {
      a.stars = awardSum(a); a.max = maxFor(); S.dirty = true;
      if (PL) try { PL.frame.contentWindow.postMessage({ knobelnestAward: S.view() }, '*'); } catch (e) {}
    }
    function boxOf(k) { return !cfg.proTag || a.boxDay[k] === today() ? (+a.box[k] || 0) : 0; }
    function doneToday(k) { return cfg.proTag && a.starDay[k] === today(); }
    function modal(have, max, title, line, isNew) {
      if (!PL) return;
      var old = PL.el.querySelector('.pmodal'); if (old) old.remove();
      var m = document.createElement('div'); m.className = 'pmodal'; m.setAttribute('role', 'dialog'); m.setAttribute('aria-modal', 'true');
      m.innerHTML = '<div class="pmodal-box">' + (S.level ? '<p class="pm-lv">' + h(S.level) + '</p>' : '') +
        '<div class="pm-stars" aria-label="' + have + ' von ' + max + ' Sternen">' + starRow(have, max, isNew ? 'new' : '') + '</div>' +
        '<h2>' + h(title) + '</h2><p>' + h(line) + '</p><button class="kid-go" data-a="pmClose">Weiter spielen</button></div>';
      PL.el.appendChild(m); m.querySelector('button').focus();
    }
    S.render = function () {
      if (!PL || cfg.modus === 'eigene' || cfg.modus === 'aus') return;
      var b = PL.bar, k = key(), max = maxFor(), have = Math.min(max, +a.lv[k] || 0), name = S.level || '', body;
      if (!S.shown) return;
      if (cfg.modus === 'runde') {
        var r = S.round || { n: 0, res: [] }, dots = '';
        for (var i = 0; i < cfg.n; i++) dots += '<span class="dot' + (i < r.res.length ? (r.res[i] ? ' ok' : ' no') : '') + '"></span>';
        body = '<span class="sb-name">' + (name ? h(name) + ' · ' : '') + 'Antwort ' + Math.min(r.n + 1, cfg.n) + ' von ' + cfg.n + '</span><span class="sb-dots" aria-hidden="true">' + dots + '</span>' +
          '<span class="sb-best" aria-label="Bestwert ' + have + ' von 3 Sternen">Bestwert ' + starRow(have, 3) + '</span>';
      } else {
        var info;
        if (have >= max) info = 'Alle ' + max + ' Sterne!';
        else if (doneToday(k)) info = 'Heute verdient ✓ Morgen gibt es den nächsten.';
        else if (cfg.pro === 'runde') info = 'Für einen fertigen Durchgang gibt es einen Stern.';
        else { var bx = boxOf(k), per = starPer(cfg, k), d2 = ''; for (var j = 0; j < per; j++) d2 += '<span class="dot' + (j < bx ? ' ok' : '') + '"></span>';
          info = per === 1 ? 'Nächste Aufgabe = 1 Stern' : 'Nächster Stern: <b>' + bx + ' von ' + per + '</b> richtig</span><span class="sb-dots" aria-hidden="true">' + d2; }
        body = '<span class="sb-name">' + (cfg.proLevel && name ? h(name) : 'Deine Sterne') + '</span><span class="sb-stars" aria-label="' + have + ' von ' + max + ' Sternen">' + starRow(have, max) + '</span><span class="sb-info">' + info + '</span>';
      }
      b.innerHTML = body + '<span class="sb-total">Insgesamt ' + S.total + ' richtig</span>'; b.hidden = false;
    };
    S.setLevel = function (lv) { if (lv === S.level) return; S.level = lv; S.round = null; S.render(); };
    S.answer = function (ok) {
      if (ok) S.total++;
      if (cfg.modus === 'eigene' || cfg.modus === 'aus') return;
      S.shown = true;
      var k = key();
      if (cfg.modus === 'runde') {
        var r = S.round = S.round || { n: 0, c: 0, res: [] };
        r.n++; if (ok) r.c++; r.res.push(!!ok);
        if (r.n >= cfg.n) {
          var n = cfg.n, st = r.c >= Math.ceil(n * .9) ? 3 : r.c >= Math.ceil(n * .7) ? 2 : r.c >= Math.ceil(n * .5) ? 1 : 0;
          var prev = +a.lv[k] || 0; if (st > prev) { a.lv[k] = st; sync(); }
          S.round = null; S.render();
          setTimeout(function () {
            modal(st, 3, st === 3 ? 'Super gemacht!' : st === 2 ? 'Gut gemacht!' : st === 1 ? 'Geschafft!' : 'Weiter üben!',
              r.c + ' von ' + n + ' richtig.' + (st > prev && prev ? ' Neuer Bestwert!' : st < prev ? ' Dein Bestwert: ' + prev + (prev === 1 ? ' Stern.' : ' Sterne.') : ''), st > 0);
          }, 700);
          return;
        }
      } else if (ok && cfg.pro !== 'runde') {
        var have = +a.lv[k] || 0;
        if (have < cfg.max && !doneToday(k)) {
          a.box[k] = boxOf(k) + 1; a.boxDay[k] = today(); S.dirty = true;
          if (a.box[k] >= starPer(cfg, k)) { win(k); return; }
        }
      }
      S.render();
    };
    function win(k) {
      a.lv[k] = (+a.lv[k] || 0) + 1; a.box[k] = 0; a.starDay[k] = today(); sync(); S.render();
      var done = a.lv[k] >= cfg.max;
      setTimeout(function () {
        modal(a.lv[k], cfg.max, done ? 'Alle Sterne!' : 'Neuer Stern!', done ? 'Du hast alle ' + cfg.max + ' Sterne gesammelt. Super geübt!' :
          cfg.proTag ? 'Morgen kannst du den nächsten Stern holen. Weiterüben darfst du trotzdem.' : 'Mit ' + starPer(cfg, k) + ' weiteren richtigen gibt es den nächsten Stern.', true);
      }, 600);
    }
    S.roundDone = function () {
      if (cfg.modus !== 'sammeln' || cfg.pro !== 'runde') return;
      S.shown = true; var k = key();
      if ((+a.lv[k] || 0) >= cfg.max) return S.render();
      if (doneToday(k)) { S.render(); return setTimeout(function () { modal(+a.lv[k] || 0, cfg.max, 'Durchgang geschafft!', 'Deinen Stern für heute hast du schon. Morgen kannst du den nächsten holen.'); }, 400); }
      win(k);
    };
    S.own = function (x) {
      if (!x || typeof x !== 'object') return;
      if (isFinite(x.stars)) a.stars = Math.max(0, Math.min(10000, Math.round(x.stars)));
      if (isFinite(x.max)) a.max = Math.round(x.max);
      if (x.best == null || isFinite(x.best)) a.best = x.best == null ? null : Math.max(0, Math.round(x.best));
      if (x.lv && typeof x.lv === 'object') { a.lv = {}; Object.keys(x.lv).slice(0, 40).forEach(function (k) { if (isFinite(x.lv[k])) a.lv[String(k).slice(0, 40)] = Math.round(x.lv[k]); }); }
      S.dirty = true;
    };
    if (a.stars) S.shown = true;
    return S;
  }
  ACT.pmClose = function (el) { var m = el.closest('.pmodal'); if (m) m.remove(); if (PL) try { PL.frame.focus(); } catch (e) {} };

  ACT.kPlay = async function (el) {
    var g = K.home.games.filter(function (x) { return x.id === el.dataset.id; })[0];
    var html, st;
    try {
      var both = await Promise.all([DB.kidGame(K.sess.token, g.id), DB.kidState(K.sess.token, g.id).catch(function () { return null; })]);
      html = both[0]; st = both[1] || {};
    } catch (e) { return K.sessionLost(e); }
    var pend = { correct: 0, attempts: 0, done: null, total: null, level: null, dirty: false };
    var save = { data: null, dirty: false };
    var S = Stars(starCfg(html), st.award, g.correct || 0);
    async function flush() {
      if (!K.sess) return;
      var jobs = [];
      if (pend.dirty) {
        var r = { correct: pend.correct, attempts: pend.attempts, done: pend.done, total: pend.total, level: pend.level };
        pend.correct = 0; pend.attempts = 0; pend.dirty = false;
        jobs.push(DB.kidReport(K.sess.token, g.id, r));
      }
      if (save.dirty || S.dirty) {
        var sv = save.dirty ? save.data : null, aw = S.dirty ? S.a : null;
        save.dirty = false; S.dirty = false;
        jobs.push(DB.kidSave(K.sess.token, g.id, sv, aw));
      }
      try { await Promise.all(jobs); } catch (e) { console.warn(e); }
    }
    var t = setInterval(flush, 4000);
    openPlayer(g.title, html, function (d) {
      if (!d.spielheft && !d.knobelnest) return;
      if (d.type === 'level') {
        var nl = d.level == null || d.level === 'main' ? null : String(d.level).slice(0, 40);
        if (nl !== pend.level) { flush(); pend.level = nl; pend.done = null; pend.total = null; }
        S.setLevel(nl);
      }
      if (d.type === 'answer') { pend.attempts++; if (d.ok) pend.correct++; pend.dirty = true; S.answer(!!d.ok); }
      if (d.type === 'round') S.roundDone();
      if (d.type === 'progress' && d.knobelnest && isFinite(d.done) && isFinite(d.total)) { pend.done = Math.round(d.done); pend.total = Math.round(d.total); pend.dirty = true; }
      if (d.type === 'award' && d.knobelnest) S.own(d.award);
      if (d.type === 'store' && d.knobelnest && d.data && typeof d.data === 'object') {
        var js = JSON.stringify(d.data);
        if (js.length < 190000) { save.data = d.data; save.dirty = true; } else console.warn('Spielstand zu gross, wird nicht gespeichert');
      }
    }, async function () { clearInterval(t); await flush(); K.loadHome(); }, { store: st.save, award: S.view() });
    S.render();
  };
  ACT.kTafel = async function () {
    K.step = 'tafel'; K.tafel = null; K.render();
    async function load() {
      if (K.step !== 'tafel' || document.hidden) return;
      try { K.tafel = await DB.tafelGet(K.sess.token); if (K.step === 'tafel') K.render(); }
      catch (e) { stopTimers(); K.sessionLost(e); }
    }
    await load(); every(5000, load);
  };
  ACT.tSet = async function (el) {
    try { K.tafel = await DB.tafelSet(K.sess.token, el.dataset.s, el.dataset.c); } catch (e) { return K.sessionLost(e); }
    K.render();
  };
  ACT.tOff = async function () {
    try { K.tafel = await DB.tafelSet(K.sess.token, null, null); } catch (e) { return K.sessionLost(e); }
    K.render();
  };

  // ---------- Kinder: Sprint mitmachen ----------
  K.checkRace = async function () {
    if (!K.sess) return;
    try {
      var r = await DB.kidRace(K.sess.token), open = r.race && r.race.status !== 'done' ? r.race.id : null;
      if (open !== (K.raceOpen || null)) { K.raceOpen = open; if (K.step === 'home') K.render(); }
    } catch (e) {}
  };
  ACT.kRace = async function () {
    var r = await DB.kidRaceJoin(K.sess.token, K.raceOpen);
    K.R = { r: r, offset: Date.parse(r.now) - Date.now(), task: null, input: '', lock: false, msg: '' };
    K.step = 'race'; K.render();
    clearInterval(K.raceIv);
    K.raceIv = setInterval(K.racePoll, 1000);
  };
  K.racePoll = async function () {
    if (K.step !== 'race' || !K.R || UI.view !== 'kid') { clearInterval(K.raceIv); return; }
    var R = K.R, ph = K.racePhase();
    if (ph === 'run' && (R.tick = (R.tick || 0) + 1) % 3) return; // während dem Rennen nur alle 3 Sekunden nachfragen
    try { var r = await DB.kidRace(K.sess.token); if (r.race) { R.r = r; R.offset = Date.parse(r.now) - Date.now(); } else R.r.race.status = 'done'; }
    catch (e) { return; }
    K.render();
  };
  K.racePhase = function () {
    var R = K.R, race = R.r.race, run = R.r.run || {};
    if (run.finished || R.finished) return 'fin';
    if (!race || race.status === 'done') return 'done';
    if (race.status === 'wait') return 'wait';
    var left = Date.parse(race.starts_at) - R.offset - Date.now();
    return left > 0 ? 'count' : 'run';
  };
  K.view_race = function () {
    var R = K.R, race = R.r.race || {}, goal = (race.settings && race.settings.goal) || 10, rows = (race.settings && race.settings.rows) || [2, 3, 4, 5, 6, 7, 8, 9, 10];
    var run = R.r.run || {}, pos = R.pos != null ? R.pos : (run.pos || 0), ph = K.racePhase();
    var track = '<div class="kspr-track"><span class="lfinish"></span><span class="runner" style="left:calc(' + (pos / goal * 100) + '% - ' + (pos / goal * 2.4) + 'em);background:' + kidColor(K.sess.name) + '">' + h(K.sess.name.charAt(0)) + '</span></div>' +
      '<p class="kspr-pos">' + pos + ' von ' + goal + '</p>';
    var body;
    if (ph === 'wait') body = '<div class="kid-card"><h1>Du bist dabei!</h1><p class="lead">Warte, bis deine Lehrperson den Sprint startet. Schau nach vorne an die Wandtafel.</p>' + track + '</div>';
    else if (ph === 'count') {
      var left = Math.ceil((Date.parse(race.starts_at) - R.offset - Date.now()) / 1000);
      if (!R.cd) R.cd = setInterval(function () { if (K.step !== 'race' || UI.view !== 'kid' || K.racePhase() !== 'count') { clearInterval(R.cd); R.cd = null; if (UI.view !== 'kid') return; } K.render(); }, 250);
      body = '<div class="kid-card"><div class="kspr-count">' + Math.max(1, left) + '</div><p class="lead">Gleich geht\'s los!</p></div>';
    } else if (ph === 'run') {
      if (!R.task) R.task = sprTask(rows, null, race.settings && race.settings.mode);
      var t = R.task;
      body = '<div class="kspr">' + track + '<div class="kspr-task">' + t.q + '</div><div class="kspr-ans' + (R.state ? ' ' + R.state : '') + '">' + (R.state === 'no' ? R.input : R.input ? h(R.input) : (R.msg || '?')) + '</div>' +
        '<div class="kspr-pad">' + ['7', '8', '9', '4', '5', '6', '1', '2', '3', 'del', '0', 'ok'].map(function (k) {
          return '<button class="key' + (k === 'ok' ? ' ok' : '') + '" data-a="kRk" data-k="' + k + '"' + (R.lock ? ' disabled' : '') + '>' + (k === 'del' ? '⌫' : k === 'ok' ? '✓' : k) + '</button>'; }).join('') + '</div></div>';
    } else if (ph === 'fin') {
      var pl = R.place || R.r.place;
      body = '<div class="kid-card"><div class="kspr-count">' + (pl && pl <= 3 ? medal(pl) : '🎉') + '</div><h1>Im Ziel!</h1><p class="lead">' + (pl ? 'Du bist als ' + pl + '. im Ziel. ' : '') + 'Super gerannt! Schau nach vorne, wie die anderen laufen.</p>' + track + '</div>';
    } else body = '<div class="kid-card"><h1>Der Sprint ist vorbei</h1><p class="lead">Du hast ' + pos + ' von ' + goal + ' Aufgaben geschafft. Gut gemacht!</p>' + track + '</div>';
    return K.shell(body, 'Zurück');
  };
  ACT.kRk = function (el) {
    var R = K.R, k = el.dataset.k; if (!R || R.lock || K.racePhase() !== 'run') return;
    if (k === 'del') R.input = R.input.slice(0, -1);
    else if (k === 'ok') return K.raceCheck();
    else if (R.input.length < 3) R.input = (R.input === '0' ? '' : R.input) + k;
    R.msg = ''; K.render();
  };
  document.addEventListener('keydown', function (e) {
    if (typeof K === 'undefined' || UI.view !== 'kid' || K.step !== 'race' || !K.R || K.racePhase() !== 'run') return;
    var k = /^[0-9]$/.test(e.key) ? e.key : e.key === 'Backspace' ? 'del' : e.key === 'Enter' ? 'ok' : null;
    if (!k) return; e.preventDefault(); ACT.kRk({ dataset: { k: k } });
  });
  K.raceCheck = function () {
    var R = K.R; if (!R.input) return;
    var race = R.r.race, rows = race.settings.rows || [2, 3, 4, 5, 6, 7, 8, 9, 10], goal = race.settings.goal || 10, t = R.task, ok = +R.input === t.ans;
    var run = R.r.run || {}; if (R.pos == null) R.pos = run.pos || 0;
    if (ok) { R.pos = Math.min(goal, R.pos + 1); R.state = 'ok'; } else { R.state = 'no'; R.msg = ''; R.input = '<span>' + t.full + '</span>'; }
    R.lock = true; K.render();
    DB.kidRaceStep(K.sess.token, race.id, ok).then(function (res) {
      if (res && res.ok) { R.pos = res.pos; if (res.finished) { R.finished = true; R.place = res.place; } K.render(); }
    }).catch(function () {});
    setTimeout(function () { R.lock = false; R.state = ''; R.input = ''; R.task = sprTask(rows, t.key, race.settings.mode); if (R.pos >= goal) R.finished = true; K.render(); }, ok ? 350 : 1300);
  };

  // ===================================================================
  // Start
  // ===================================================================
  // Einladungs-/Passwort-Links aus der E-Mail
  var LINK_INVITE = /type=(invite|signup|magiclink)/.test(location.hash), LINK_RECOVERY = /type=recovery/.test(location.hash);
  function linkError(hs) {
    var p = new URLSearchParams(hs.replace(/^#\/?/, ''));
    var code = p.get('error_code') || '', msg = /expired/.test(code + p.get('error_description')) ?
      'Dieser Link ist abgelaufen oder wurde schon benutzt. Bitten Sie die Administratorin um einen neuen Link oder setzen Sie Ihr Passwort mit «Passwort vergessen?» neu.' :
      'Der Link aus der E-Mail hat nicht funktioniert (' + (p.get('error_description') || code || 'unbekannter Fehler').replace(/\+/g, ' ') + ').';
    history.replaceState(null, '', location.pathname + '#/');
    T.start(); setTimeout(function () { toast(msg); }, 400);
    UI.linkMsg = msg;
  }
  DB.onAuth(function (ev, sess) {
    var viaLink = sess && (ev === 'SIGNED_IN' || ev === 'INITIAL_SESSION') && (LINK_INVITE || LINK_RECOVERY);
    if (ev === 'PASSWORD_RECOVERY' || viaLink) {
      if (UI.view === 'recovery') return;
      var invite = LINK_INVITE && ev !== 'PASSWORD_RECOVERY'; LINK_INVITE = false; LINK_RECOVERY = false;
      UI.view = 'recovery';
      paint('<main class="main" style="max-width:560px"><form class="card stack" data-a="recoverPw"><h1 class="h1">' + (invite ? 'Willkommen bei ' + h(C.PORTAL_NAME) + '!' : 'Neues Passwort') + '</h1>' +
        (invite ? '<p class="muted">Legen Sie jetzt Ihr eigenes Passwort fest. Damit melden Sie sich künftig mit Ihrer E-Mail-Adresse an.</p>' : '') +
        '<div class="field"><label for="rcPw">Neues Passwort (mindestens 8 Zeichen)</label><input class="input" id="rcPw" name="pw" type="password" minlength="8" autocomplete="new-password" required></div>' +
        '<button class="btn primary">Speichern</button></form></main>');
    }
  });
  ACT.recoverPw = async function (f) { await DB.setPassword(f.elements.pw.value); toast('Passwort gespeichert.'); history.replaceState(null, '', location.pathname + '#/'); UI.view = null; T.start(); };

  window.addEventListener('hashchange', route);
  route();
})();
