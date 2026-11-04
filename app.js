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
  var FACH_COL = { 'Mathematik': '#CFDDF0', 'Englisch': '#F28B82', 'Deutsch': '#F7E3A1', 'NMG': '#D3F1E4', 'Französisch': '#D6E8F5' };
  var TINTS = ['#D5EBC9', '#E1E8F8', '#E3D5F0', '#F3E2A6', '#CBE6EE', '#E4F5EC'];
  var FACH_SHORT = { 'Mathematik': 'Mathe' };
  function fachShort(f) { return FACH_SHORT[f] || f; }
  // Knopf-Farbe pro Fach (dunklerer Ton der Fachfarbe); sonst das normale Blau
  var FACH_BTN = { 'Englisch': '#CC5046', 'Deutsch': '#E9B824' };
  var FACH_INK = { 'Deutsch': '#2B2300' };
  function fachBtn(f) { return (FACH_BTN[f] ? 'background:' + FACH_BTN[f] + ';' : '') + (FACH_INK[f] ? 'color:' + FACH_INK[f] + ';' : ''); }
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
  var COL_DEF = { helfen: 'Ich kann helfen', klar: 'Ich komme gut klar', frage: 'Ich habe eine Frage' };
  // Eigene Namen der drei Spalten pro Klasse (classes.tafel_cols); leer = Standard. Gespeichert schon «escaped» für das HTML.
  // Version 21: { list: [ { id, label, color } ] } = eigene Spalten (höchstens 6); sonst die drei Standardspalten
  var COL_IC = { helfen: COLS[0].ic, klar: COLS[1].ic, frage: COLS[2].ic, stern: '<path d="M12 4l2.3 4.8 5.2.7-3.8 3.6.9 5.2L12 15.8 7.4 18.3l.9-5.2-3.8-3.6 5.2-.7z"/>' };
  var COL_STDCOL = { helfen: '#2F5E9E', klar: '#2E7D4F', frage: '#E8B710' };
  function colList(o) {
    o = o && typeof o === 'object' ? o : {};
    if (Array.isArray(o.list) && o.list.length) return o.list.slice(0, 6).map(function (x, i) {
      var id = String((x && x.id) || '').toLowerCase().replace(/[^a-z0-9]/g, '').slice(0, 12) || ('s' + i);
      return { id: id, label: String((x && x.label) || COL_DEF[id] || 'Spalte').trim().slice(0, 40), color: /^#[0-9a-fA-F]{6}$/.test((x && x.color) || '') ? x.color : (COL_STDCOL[id] || PALETTE[i % PALETTE.length][0]) };
    });
    return ['helfen', 'klar', 'frage'].map(function (id) { return { id: id, label: String(o[id] || '').trim().slice(0, 40) || COL_DEF[id], color: COL_STDCOL[id] }; });
  }
  function setTafelCols(o) {
    var own = o && Array.isArray(o.list) && o.list.length;
    COLS.length = 0; Object.keys(COL_LABEL).forEach(function (k) { delete COL_LABEL[k]; });
    colList(o).forEach(function (x) {
      var std = !own || (COL_STDCOL[x.id] && x.color.toLowerCase() === COL_STDCOL[x.id].toLowerCase());
      COLS.push({ id: x.id, label: h(x.label), color: std && COL_STDCOL[x.id] ? null : x.color, ic: COL_IC[x.id] || COL_IC.stern });
      COL_LABEL[x.id] = h(x.label);
    });
  }
  // Farben einer eigenen Spalte: helle Fläche, mittlerer Rand, dunkle Schrift
  function mixHex(c, w, t) { var n = parseInt(c.slice(1), 16), r = n >> 16, g = (n >> 8) & 255, b = n & 255; var f = function (v) { return Math.round(v + (t - v) * w); };
    return 'rgb(' + f(r) + ',' + f(g) + ',' + f(b) + ')'; }
  function colStyle(c) { return c.color ? ' style="background:' + mixHex(c.color, .84, 255) + ';border-color:' + mixHex(c.color, .45, 255) + ';color:' + mixHex(c.color, .55, 0) + '"' : ''; }
  function dotStyle(c) { return c.color ? ' style="background:' + c.color + '"' : ''; }
  // Klassenbild (Maskottchen): eigenes Bild oder das Standardbild
  function klassBild(b) { return /^data:image\//.test(b || '') ? b : 'bilder/klassenkiste.webp'; }
  // Werkzeuge für die Kinder: fehlt ein Eintrag, gilt «freigegeben» (so bleiben bestehende Klassen wie bisher)
  function toolOn(c, k) { var t = c && c.kid_tools; return !(t && t[k] === false); }

  // Einheitlicher Zurück-Knopf wie in der Eulenkiste: weisse Pille mit Pfeil und Eule (oben links)
  function backBtn(attr, label) {
    label = label || 'Zurück zur Klassenkiste';
    var inner = '<span aria-hidden="true">←</span><img src="bilder/eule.webp" alt="" width="34" height="34" draggable="false">';
    return /href=/.test(attr) ? '<a class="kn-back" ' + attr + ' aria-label="' + h(label) + '" title="' + h(label) + '">' + inner + '</a>'
      : '<button class="kn-back" ' + attr + ' aria-label="' + h(label) + '" title="' + h(label) + '">' + inner + '</button>';
  }
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
    app.innerHTML = html; document.body.classList.remove('wechsel');
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
  function rerender() { if (UI.view === 'teacher') T.render(); else if (UI.view === 'kid') K.render(); else if (UI.view === 'umfrage') U.render(); else if (UI.view === 'eg') E.render(); }

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
  function shimMain(seed, aw, lvls) {
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
    // Bisheriger Stand pro Level aus dem Portal: { 'Level': { c: richtig, a: Versuche } }
    window.knobelnest.levels = function () { return lvls && typeof lvls === 'object' ? lvls : {}; };
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
    var tag = '<script>(' + shimMain.toString() + ')(' + J(seed.store) + ',' + J(aw) + ',' + J(seed.levels || {}) + ');<\/script>';
    var m = /<head[^>]*>/i.exec(html);
    return m ? html.slice(0, m.index + m[0].length) + tag + html.slice(m.index + m[0].length) : tag + html;
  }
  // Spiele, die als eigener Ordner auf dem Server liegen (z. B. die Zeitreise): <meta name="knobelnest-url" content="zeitreise/index.html">
  // Die Vokabelkiste liegt im Ordner vokabelkiste/. Als Spiel-Datei geht auch die Vokabelkiste aus claude.ai (erkannt an «vk-content»).
  function gameUrl(html) {
    if (/<script[^>]*id=["']vk-content["']/i.test(html || '')) return 'vokabelkiste/index.html';
    var m = /<meta\s+name=["']knobelnest-url["']\s+content=["']([^"']+)["']/i.exec(html || '');
    return m && /^[a-z0-9][a-z0-9_\-\/\.]*$/i.test(m[1]) && m[1].indexOf('..') < 0 ? m[1] : null;
  }
  var ZR_VER = '1';
  var VK_VER = '10'; // Vokabelkiste (vokabelkiste/index.html)
  var GD_VER = '2'; // Gedächtniskiste (gedaechtnis/, gebaut mit werkstatt/spiele/gedaechtnis/bauen.py)
  var KS_VER = '1'; // Knobelspiele (knobelspiele/, gebaut mit werkstatt/spiele/knobelspiele/bauen.py)
  var EN_VER = '1'; // Englisch-Spiele (englisch/, gebaut mit werkstatt/spiele/englisch/bauen.py)
  var PL = null;
  function openPlayer(title, html, onMsg, onClose, seed) {
    closePlayer();
    var p = document.createElement('div');
    p.className = 'player'; p.setAttribute('role', 'dialog'); p.setAttribute('aria-label', title);
    p.innerHTML = '<div class="player-bar">' + backBtn('data-a="closePlayer"', 'Zurück') + '<b>' + h(title) +
      '</b><button class="btn sm" data-a="playerFull">Vollbild</button></div>';
    var f = document.createElement('iframe');
    f.setAttribute('sandbox', 'allow-scripts allow-forms allow-modals allow-popups allow-downloads allow-pointer-lock');
    f.setAttribute('allow', 'fullscreen; autoplay; picture-in-picture; encrypted-media');
    f.title = title;
    var url = gameUrl(html);
    if (url) f.src = url + (url.indexOf('?') < 0 ? '?' : '&') + 'v=' + (/^vokabelkiste\//.test(url) ? VK_VER : /^gedaechtnis\//.test(url) ? GD_VER : /^knobelspiele\//.test(url) ? KS_VER : /^englisch\//.test(url) ? EN_VER : ZR_VER);
    else f.srcdoc = prepare(html, seed);
    if (url && /^vokabelkiste\//.test(url)) p.classList.add('player-vk'); // eigener Knopf «← Klassenkiste» statt dunklem Balken
    var bar = document.createElement('div'); bar.className = 'starbar'; bar.hidden = true; bar.setAttribute('aria-live', 'polite');
    p.querySelector('.player-bar').insertBefore(bar, p.querySelector('[data-a="playerFull"]'));
    p.appendChild(f); document.body.appendChild(p); document.body.style.overflow = 'hidden';
    PL = { el: p, frame: f, bar: bar, onMsg: onMsg, onClose: onClose, url: url, seed: seed || null };
  }
  function closePlayer() {
    if (!PL) return; var x = PL; PL = null;
    try { if (document.fullscreenElement) document.exitFullscreen(); else if (document.webkitFullscreenElement) document.webkitExitFullscreen(); } catch (e) {}
    x.el.remove(); document.body.style.overflow = '';
    if (x.onClose) x.onClose();
  }
  ACT.closePlayer = function () { closePlayer(); };
  // Fortschritt eines Kindes zurücksetzen (alles oder einzelne Spiele)
  ACT.pReset = function (el) {
    var k = T.kids.filter(function (x) { return x.id === el.dataset.k; })[0]; if (!k) return;
    var P = {}; (T.progress || []).forEach(function (r) { if (r.kid_id === k.id) P[r.game_id] = r; });
    var gs = T.games.filter(function (g) { return P[g.id]; });
    overlay('<form class="card stack" style="width:min(560px,100%);max-height:calc(100dvh - 32px);overflow:auto" data-a="pResetGo" data-k="' + k.id + '">' +
      '<h2 style="margin:0">Fortschritt von ' + h(k.name) + ' zurücksetzen</h2>' +
      '<p class="muted" style="margin:0">Gelöscht werden Punkte, Sterne, Bestzeiten und der gespeicherte Spielstand. Das lässt sich nicht rückgängig machen.</p>' +
      '<label class="row" style="gap:10px;font-weight:700"><input type="checkbox" data-change="pResetAll" checked style="width:22px;height:22px"> Alle Spiele (' + gs.length + ')</label>' +
      '<div class="stack" id="pResetList" style="gap:6px;padding-left:14px;border-left:3px solid var(--line)">' + gs.map(function (g) {
        return '<label class="row" style="gap:10px;flex-wrap:nowrap"><input type="checkbox" name="g" value="' + g.id + '" checked style="width:20px;height:20px;flex:none"> <span>' + h(g.title) + ' <span class="muted small">' + h(g.fach) + ' › ' + h(g.thema) + '</span></span></label>'; }).join('') + '</div>' +
      '<div class="row" style="justify-content:flex-end"><button type="button" class="btn" data-a="closeOverlay">Abbrechen</button><button class="btn danger">Zurücksetzen</button></div></form>');
  };
  ACT.pResetAll = function (el) { Array.prototype.forEach.call(document.querySelectorAll('#pResetList input'), function (i) { i.checked = el.checked; }); };
  ACT.pResetGo = async function (f) {
    var boxes = Array.prototype.slice.call(f.querySelectorAll('input[name=g]')), ids = boxes.filter(function (i) { return i.checked; }).map(function (i) { return i.value; });
    if (!ids.length) return toast('Bitte mindestens ein Spiel wählen.');
    var all = ids.length === boxes.length, k = T.kids.filter(function (x) { return x.id === f.dataset.k; })[0];
    await DB.resetProgress(f.dataset.k, all ? null : ids);
    closeOverlays(); T.progress = null; toast('Fortschritt von ' + (k ? k.name : '') + ' zurückgesetzt'); T.render();
  };
  ACT.playerFull = function () { if (!PL) return; var e = PL.el; try { (e.requestFullscreen || e.webkitRequestFullscreen).call(e); } catch (x) {} };
  window.addEventListener('message', function (e) {
    if (!PL || e.source !== PL.frame.contentWindow) return;
    var d = e.data; if (!d || typeof d !== 'object') return;
    if (PL.url && d.knobelnest && d.type === 'hello') {
      var sd = PL.seed || {};
      try { PL.frame.contentWindow.postMessage({ knobelnestInit: { store: sd.store || null, settings: sd.settings || null, teacher: sd.teacher != null ? !!sd.teacher : !PL.seed, edit: !!sd.edit, admin: !!sd.admin, award: sd.award || null } }, '*'); } catch (x) {}
      return;
    }
    if (PL.url && d.knobelnest && d.type === 'close') { closePlayer(); return; }
    if (PL.onMsg) PL.onMsg(d);
  });

  // Router
  var timers = [];
  function every(ms, fn) { timers.push(setInterval(fn, ms)); }
  function stopTimers() { timers.forEach(clearInterval); timers = []; }
  function route() {
    stopTimers(); closeOverlays(); closePlayer(); UI.confirm = null; document.body.classList.remove('lp'); document.body.classList.remove('kidv');
    // Beim Wechsel die alte Seite ausblenden, bis die neue gezeichnet ist (sonst blitzt sie kurz ohne Gestaltung auf)
    document.body.classList.add('wechsel'); clearTimeout(UI.wechselT);
    UI.wechselT = setTimeout(function () { document.body.classList.remove('wechsel'); }, 1500);
    var hs = location.hash || '';
    if (/error_description=/.test(hs)) return linkError(hs);
    if (/access_token=|type=recovery/.test(hs)) { setTimeout(function () { if (/access_token=/.test(location.hash) && UI.view !== 'recovery') { location.hash = '#/'; } }, 4000); return; }
    if (hs.indexOf('#/klasse') === 0) return K.start();
    var m = hs.match(/^#\/wandtafel\/([0-9a-f-]{36})(\/embed)?/);
    if (m) return W.start(m[1], !!m[2]);
    var mf = hs.match(/^#\/tagesfolie\/([0-9a-f-]{36})/);
    if (mf) return F.start(mf[1]);
    var mo = hs.match(/^#\/otterteich\/([0-9a-f-]{36})/);
    if (mo) return O.start(mo[1]);
    var mg = hs.match(/^#\/gedaechtnis\/([0-9a-f-]{36})/);
    if (mg) return GD.start(mg[1]);
    var ma = hs.match(/^#\/atelier\/([0-9a-f-]{36})/);
    if (ma) return AT.start(ma[1]);
    var mp = hs.match(/^#\/pinnwand\/([0-9a-f-]{36})/);
    if (mp) return P.start(mp[1]);
    var mh = hs.match(/^#\/hausaufgaben\/([0-9a-f-]{36})/);
    if (mh) return H.start(mh[1]);
    var mgs = hs.match(/^#\/gespraeche\/([0-9a-f-]{36})(?:\/([0-9a-f-]{36}))?/);
    if (mgs) return E.start(mgs[1], mgs[2]);
    var mel = hs.match(/^#\/eltern\/([0-9a-f-]{36})/);
    if (mel) return EP.start(mel[1]);
    var mg = hs.match(/^#\/u(?:\/(\d*))?\/?$/);
    if (mg) return G.start(mg[1] || '');
    var mu = hs.match(/^#\/umfrage\/([0-9a-f-]{36})/);
    if (mu) return U.start(mu[1]);
    if (/^#\/quiz(\/|$)/.test(hs)) return QZ.start();
    var mq = hs.match(/^#\/q(?:\/(\d*))?\/?$/);
    if (mq) return QZ.play(mq[1] || '');
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
    var out = emb ? '<div class="board-head"><div class="stack" style="gap:0"><span class="kick">Arbeitsstand · Klasse ' + h(s.class_name || '') + '</span><h1>Wer kann wem helfen?</h1></div></div>' : '<div class="board-head">' + (kid ? backBtn('data-a="kBack"', 'Zurück') : backBtn('href="#/"')) + '<img class="board-bild" src="' + h(klassBild(kid ? (K.kl && K.kl.bild) : W.bild)) + '" alt=""><div class="stack" style="gap:6px;flex:1 1 300px"><span class="kick">Arbeitsstand · Klasse ' + h(s.class_name || '') + ' <span class="sterne" aria-hidden="true">✦ ✧ ✦</span></span>' +
      '<h1>' + (kid ? 'Wo stehst du gerade?' : 'Wer kann wem helfen?') + '</h1>' +
      '<p>' + (kid ? 'Tippe beim Fach auf das Feld, das zu dir passt. Dein Name steht immer nur an einem Ort.' : 'Hast du eine Frage? Schau, wer im gleichen Fach helfen kann.') + '</p></div>' +
      (kid ? '' : '<div class="row"><button class="board-btn" data-a="wallFull">Vollbild</button></div>') + '</div>';
    if (kid) {
      out += '<div class="mine"><b>Du (' + h(kidName[me] || '') + '):</b><span>' +
        (mine && subjName[mine.subject_id] ? h(subjName[mine.subject_id]) + ' · ' + (COL_LABEL[mine.col] || '') : 'Du stehst noch nicht auf der Tafel. Wähle unten dein Fach und die passende Spalte.') + '</span>' +
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
      out += '<div class="matrix" style="--ncol:' + COLS.length + ';--rows:' + N + ';--fs-s:clamp(14px, calc((100dvh - 200px) / ' + N + ' / 3), 26px)">' +
        '<div class="mx-h blank"></div>' + COLS.map(function (c) {
          return '<div class="mx-h c-' + c.id + '"' + colStyle(c) + '><span class="dot"' + dotStyle(c) + '>' + ic(c.ic, 18, '#fff', 2.4) + '</span><span class="lbl">' + c.label + '</span></div>'; }).join('');
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
          if (kid && !here) out += '<button class="cell c-' + c.id + '"' + colStyle(c) + ' data-a="tSet" data-s="' + sub.id + '" data-c="' + c.id + '" aria-label="' + h(sub.name) + ': ' + c.label + '">' + tags +
            '<span class="put">' + (mine ? 'hierhin' : 'Hier eintragen') + '</span></button>';
          else out += '<div class="cell c-' + c.id + (here ? ' here' : '') + '"' + colStyle(c) + '>' + tags + '</div>';
        });
      });
      out += '</div>';
    }
    var missing = s.kids.filter(function (k) { return !entry[k.id] || !subjName[entry[k.id].subject_id]; }).map(function (k) { return k.name; });
    if (!kid && !emb) out += '<div class="board-fehlt">' + (missing.length ? '<b>Noch nicht auf der Tafel:</b>' + missing.map(function (n) { return '<span class="tag"><span class="ini" style="background:' + kidColor(n) + '">' + h(n.charAt(0)) + '</span>' + h(n) + '</span>'; }).join('') : '<b>✓ Alle Kinder stehen auf der Tafel.</b>') + '</div>';
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
      if (!(await licGate())) return;
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
      var head = '<div class="spr-head">' + backBtn('href="#/"') + '<div style="flex:1 1 auto"><span class="kick">Klassen-Sprint · Klasse ' + h(cls.name) + '</span><h1>' +
        (!r ? 'Neuer Sprint' : r.status === 'wait' ? 'Auf die Plätze …' : r.status === 'run' ? 'Los geht\'s!' : 'Zieleinlauf') + '</h1></div><div class="row">' +
        (r && r.status === 'wait' ? '<button class="btn primary big" data-a="sGo"' + (S.runs.length ? '' : ' disabled') + '>▶ Start</button><button class="btn" data-a="sCancel">Abbrechen</button>' : '') +
        (r && r.status === 'run' ? '<button class="btn" data-a="sEnd">Beenden</button>' : '') +
        (r && r.status === 'done' ? '<button class="btn primary" data-a="sNew">Neuer Sprint</button>' : '') +
        '<button class="btn" data-a="wallFull">Vollbild</button></div></div>';
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
      if (!embed && !(await toolGate('tafel', 'Die Arbeitsstand-Tafel'))) return;
      app.innerHTML = '<p class="boot">Tafel wird geladen …</p>';
      try { var wc = (await DB.listClasses()).filter(function (c) { return c.id === cid; })[0]; setTafelCols(wc && wc.tafel_cols); W.bild = wc && wc.bild; } catch (e) {}
      async function load() {
        try { paint(board(await DB.tafelTeacher(cid), embed ? 'embed' : 'wall')); }
        catch (e) { paint('<div class="main"><div class="card stack"><h2>Tafel nicht verfügbar</h2><p>' + h(errMsg(e)) + '</p><a class="btn" href="#/">Zum Portal</a></div></div>'); stopTimers(); }
      }
      await load();
      every(embed ? 3000 : 5000, function () { if (!document.hidden) load(); });
    }
  };

  // ===================================================================
  // Tagesfolie, Pinnwand und Lautstärkeregler (Otterteich) hat jede Lehrperson (BASE_TOOLS).
  // Die übrigen Werkzeuge (TOOLS) gibt die Admin-Person pro Lehrperson frei.
  // Gespeichert in shared_store «werkzeuge» = { Lehrperson-ID: { heft: true, atelier: true, tafel: true, vk: true } }
  // ===================================================================
  var BASE_TOOLS = [['folie', '☀️ Tagesfolie'], ['pin', '📌 Pinnwand'], ['otter', '🦦 Lautstärkeregler']];
  var TOOLS = [['heft', '📒 Hausaufgabenheft'], ['tafel', '🙋 Arbeitsstand'], ['vk', '📦 Vokabelkiste'], ['atelier', '🚲 Atelier'], ['quiz', '❓ Live-Quiz'], ['gd', '🧠 Gedächtniskiste'], ['umfrage', '📊 Umfrage'], ['eltern', '🗓️ Elterngespräche']];
  async function toolAccess(me) {
    var all = {}; BASE_TOOLS.concat(TOOLS).forEach(function (t) { all[t[0]] = true; });
    if (me && me.is_admin) return all;
    var acc = {}; BASE_TOOLS.forEach(function (t) { acc[t[0]] = true; });
    try { var d = await DB.sharedGet('werkzeuge'); var mine = (d && me && d[me.id]) || {}; TOOLS.forEach(function (t) { if (mine[t[0]]) acc[t[0]] = true; }); } catch (e) {}
    return acc;
  }
  // Lizenz (Version 22): profiles.valid_until = letzter gültiger Tag (leer = unbefristet, Admin immer frei)
  function licLeft(me) {
    if (!me || me.is_admin || !me.valid_until) return null;
    return Math.round((new Date(me.valid_until + 'T12:00:00') - new Date(isoDay(new Date()) + 'T12:00:00')) / 864e5);
  }
  function licExpired(me) { var d = licLeft(me); return d !== null && d < 0; }
  function dateCH(iso) { var p = String(iso || '').split('-'); return p.length === 3 ? (+p[2]) + '.' + (+p[1]) + '.' + p[0] : ''; }
  function renewBtn(cls) {
    return C.SHOP_URL ? '<a class="btn ' + (cls || 'primary') + '" href="' + h(C.SHOP_URL) + '" target="_blank" rel="noopener">✦ Jetzt verlängern</a>'
      : '<a class="btn ' + (cls || 'primary') + '" href="mailto:' + h(C.CONTACT) + '?subject=' + encodeURIComponent(C.PORTAL_NAME + ' verlängern') + '">✦ Jetzt verlängern</a>';
  }
  function licPage(me) {
    document.body.classList.add('lp');
    paint('<div class="main"><div class="card stack" style="max-width:600px;margin:40px auto;text-align:center;align-items:center;gap:16px">' +
      '<img src="bilder/eule.webp" alt="" width="96" height="96"><h2>Ihre ' + h(C.PORTAL_NAME) + ' ist abgelaufen</h2>' +
      '<p>Ihre Lizenz war gültig bis am <b>' + h(dateCH(me.valid_until)) + '</b>. Ihre Klassen und alles, was Sie gespeichert haben, bleiben erhalten. Sobald Sie verlängern, geht es genau dort weiter.</p>' +
      '<div class="row" style="justify-content:center">' + renewBtn() + '<button class="btn" data-a="logout">Abmelden</button></div>' +
      '<p class="muted small">Fragen? ' + h(C.CONTACT) + '</p></div></div>');
  }
  // Für Werkzeug-Seiten ohne toolGate (Wandtafel, Sprint): false = abgelaufen, Hinweis gezeigt
  async function licGate() {
    var me = null; try { me = await DB.me(); } catch (e) {}
    if (licExpired(me)) { licPage(me); return false; }
    return true;
  }
  async function toolGate(key, name) {
    var me = null; try { me = await DB.me(); } catch (e) {}
    if (licExpired(me)) { licPage(me); return false; }
    var acc = await toolAccess(me);
    if (acc[key]) return true;
    paint('<div class="main"><div class="card stack"><h2>' + h(name) + ' ist noch nicht freigegeben</h2><p>Die Administratorin oder der Administrator kann es Ihnen unter «Verwaltung» freigeben.</p><a class="btn" href="#/">Zum Portal</a></div></div>');
    return false;
  }

  // ===================================================================
  // Tagesfolie (Lehrperson, an der Wandtafel). Läuft als eigene Seite tagesfolie.html im Rahmen;
  // Klassenliste, Speicher und Arbeitsstand-Tafel kommen von hier.
  // ===================================================================
  var F = {
    start: async function (cid) {
      UI.view = 'folie';
      var s = await DB.session();
      if (!s) { location.hash = '#/'; return; }
      if (!(await toolGate('folie', 'Die Tagesfolie'))) return;
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
      var otterOk = false; try { otterOk = !!(await toolAccess(me)).otter; } catch (e3) {}
      if (otterOk) window.knOtter = otterBridge(cid, (kids || []).slice().sort(kidSort).map(function (k) { return k.name; }), function () {});
      window.knTagesfolie = {
        uid: uid, className: cls ? cls.name : '', isAdmin: !!(me && me.is_admin), template: tpl,
        saveTemplate: function (t) { return DB.sharedSet('tagesfolie-vorlage', JSON.parse(JSON.stringify(t))); },
        roster: (kids || []).map(function (k) { return k.name; }),
        boardUrl: base + '#/wandtafel/' + cid + '/embed',
        otterUrl: otterOk ? 'otterteich.html?embed&v=' + OTTER_VER : '',
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
      paint('<div class="folie"><iframe src="tagesfolie.html?v=' + ('39') + '" title="Tagesfolie" allow="fullscreen; autoplay; encrypted-media; microphone"></iframe></div>');
    }
  };
  // ===================================================================
  // Hausaufgabenheft: eigene Seite hausaufgaben.html im Rahmen, ein Heft pro Klasse.
  // Die Kinder kommen aus der Klassenkiste; gespeichert wird bei der Lehrperson (teacher_store «hat-<Klasse>»).
  // ===================================================================
  var HEFT_VER = '6';
  function heftDownloads() {
    return { save: async function (o) {
      var b = new Blob([o.data], { type: o.type || 'application/pdf' }), u = URL.createObjectURL(b), a = document.createElement('a');
      a.href = u; a.download = o.filename || 'Hausaufgaben.pdf'; document.body.appendChild(a); a.click(); a.remove(); setTimeout(function () { URL.revokeObjectURL(u); }, 4000);
    } };
  }
  var H = {
    start: async function (cid) {
      UI.view = 'heft';
      var s = await DB.session();
      if (!s) { location.hash = '#/'; return; }
      if (!(await toolGate('heft', 'Das Hausaufgabenheft'))) return;
      app.innerHTML = '<p class="boot">Hausaufgabenheft wird geladen …</p>';
      var cls, kids;
      try { cls = (await DB.listClasses()).filter(function (c) { return c.id === cid; })[0]; kids = await DB.listKids(cid); }
      catch (e) { cls = null; }
      if (!cls) { paint('<div class="main"><div class="card stack"><h2>Hausaufgabenheft nicht verfügbar</h2><p>Diese Klasse wurde nicht gefunden.</p><a class="btn" href="#/">Zum Portal</a></div></div>'); return; }
      var key = 'hat-' + cid;
      // wseq zählt Speichervorgänge: Ein Nachladen, das vor dem Speichern begonnen hat, wird verworfen (sonst überschreibt es frische Haken)
      var wseq = 0, busy = 0;
      var doc = {
        get: async function () { var d = await DB.storeGet(key); return { exists: d != null, data: function () { return d; } }; },
        set: async function (v) {
          wseq++; busy++;
          try {
          v = JSON.parse(JSON.stringify(v));
          // Was den Kindern gehört, kommt immer vom Server: ihre Haken («selbst») und ihre eigenen Aufgaben («by»)
          try { var cur = await DB.storeGet(key), sb = {}, own = [];
            ((cur && cur.entries) || []).forEach(function (e) { if (!e) return; if (e.by) own.push(e); else if (e.selbst) sb[e.id] = e.selbst; });
            v.entries = (v.entries || []).filter(function (e) { return !e.by; });
            v.entries.forEach(function (e) { if (sb[e.id]) e.selbst = sb[e.id]; else delete e.selbst; });
            v.entries = v.entries.concat(own);
          } catch (e) {}
          await DB.storeSet(key, v);
          } finally { busy--; wseq++; }
        },
        onSnapshot: function (cb) {
          var iv = setInterval(async function () { if (document.hidden || UI.view !== 'heft' || busy) return;
            var seq = wseq;
            try { var d = await DB.storeGet(key); if (d && seq === wseq && !busy) cb({ exists: true, data: function () { return d; } }); } catch (e) {} }, 30000);
          return function () { clearInterval(iv); };
        }
      };
      window.knHeft = {
        mode: 'teacher', key: cid, className: 'Klasse ' + cls.name,
        roster: (kids || []).slice().sort(kidSort).map(function (k) { return { id: k.id, name: k.name }; }),
        back: function () { if (document.fullscreenElement && document.exitFullscreen) document.exitFullscreen().catch(function () {}); location.hash = '#/'; },
        claude: { use: async function (name) {
          if (name === 'db') return { doc: function () { return doc; }, collection: function () { return { doc: function () { return doc; } }; } };
          if (name === 'assets') return { upload: async function (blob) { var u = await DB.storeUpload(blob); return { id: u, url: u, contentType: blob.type }; }, delete: async function () {} };
          if (name === 'downloads') return heftDownloads();
          return null;
        } }
      };
      paint('<div class="folie"><iframe src="hausaufgaben.html?v=' + HEFT_VER + '" title="Hausaufgabenheft" allow="fullscreen"></iframe></div>');
    }
  };
  // ===================================================================
  // Klassen-Pinnwand: eigene Seite pinnwand.html im Rahmen. Sie spricht mit einer nachgebauten
  // «claude.use('db')»-Schnittstelle; dahinter liegen teacher_store «pin-<Klasse>» und die kid_pin-Funktionen.
  // ===================================================================
  var PIN_VER = '16';
  function pinBridge(o) {
    // o.load() -> { boards, ideas, settings, votes }, o.put(coll, id, obj|null), o.add(coll, obj) -> id, o.vote(body)
    var data = { boards: {}, ideas: {}, settings: {}, votes: {} }, subs = [], iv = null;
    function snapColl(name) {
      var m = data[name] || {};
      return { docs: Object.keys(m).map(function (id) { var v = m[id]; return { id: id, exists: true, data: function () { return name === 'votes' ? o.voteDoc(id, v) : JSON.parse(JSON.stringify(v)); } }; }) };
    }
    function snapDoc(coll, id) {
      var v = (data[coll] || {})[id];
      return { id: id, exists: v != null, data: function () { return v == null ? null : coll === 'votes' ? o.voteDoc(id, v) : JSON.parse(JSON.stringify(v)); } };
    }
    function emit() { subs.forEach(function (x) { var sn = x.f(), j = JSON.stringify(x.doc ? sn.data() : sn.docs.map(function (d) { return [d.id, d.data()]; })); if (j !== x.last) { x.last = j; try { x.cb(sn); } catch (e) {} } }); }
    async function refresh() { try { var d = await o.load(); if (d) data = d; } catch (e) {} emit(); }
    var st = null; function soon() { clearTimeout(st); st = setTimeout(refresh, 450); }
    function watch(f, cb, isDoc) {
      var x = { f: f, cb: cb, doc: isDoc, last: null }; subs.push(x);
      if (!iv) { refresh(); iv = setInterval(function () { if (!o.active()) { clearInterval(iv); return; } if (!document.hidden) refresh(); }, o.every || 4000); }
      else { var sn = f(); x.last = JSON.stringify(isDoc ? sn.data() : sn.docs.map(function (d) { return [d.id, d.data()]; })); setTimeout(function () { cb(sn); }, 0); }
      return function () { subs = subs.filter(function (y) { return y !== x; }); };
    }
    function merge(a, b) { var r = JSON.parse(JSON.stringify(a || {})); Object.keys(b || {}).forEach(function (k) { var v = b[k]; r[k] = v && typeof v === 'object' && !Array.isArray(v) && r[k] && typeof r[k] === 'object' && !Array.isArray(r[k]) ? Object.assign({}, r[k], v) : v; }); return r; }
    var db = {
      collection: function (name) { return {
        add: async function (obj) {
          var id = await o.add(name, JSON.parse(JSON.stringify(obj)));
          // sofort lokal eintragen: eine neue Pinnwand muss gleich da sein, ein neuer Zettel erst nach dem Leeren des Eingabefelds
          data[name] = data[name] || {}; data[name][id] = JSON.parse(JSON.stringify(obj));
          if (name === 'boards') emit(); else setTimeout(emit, 0);
          soon(); return { id: id };
        },
        onSnapshot: function (cb) { return watch(function () { return snapColl(name); }, cb, false); }
      }; },
      doc: function (path) { var p = String(path).split('/'), coll = p[0], id = p[1]; return {
        get: async function () { await refresh(); return snapDoc(coll, id); },
        set: async function (obj) { if (coll === 'votes') await o.vote(JSON.parse(JSON.stringify(obj))); else await o.put(coll, id, JSON.parse(JSON.stringify(obj))); soon(); },
        update: async function (patch) { var m = merge((data[coll] || {})[id], patch); if (data[coll]) data[coll][id] = m; await o.put(coll, id, m); soon(); },
        delete: async function () { await o.put(coll, id, null); soon(); },
        onSnapshot: function (cb) { return watch(function () { return snapDoc(coll, id); }, cb, true); }
      }; }
    };
    return db;
  }
  var P = {
    start: async function (cid) {
      UI.view = 'pin';
      var s = await DB.session();
      if (!s) { location.hash = '#/'; return; }
      if (!(await toolGate('pin', 'Die Pinnwand'))) return;
      app.innerHTML = '<p class="boot">Pinnwand wird geladen …</p>';
      var cls, kids;
      try { cls = (await DB.listClasses()).filter(function (c) { return c.id === cid; })[0]; kids = await DB.listKids(cid); } catch (e) { cls = null; }
      if (!cls) { paint('<div class="main"><div class="card stack"><h2>Pinnwand nicht verfügbar</h2><p>Diese Klasse wurde nicht gefunden.</p><a class="btn" href="#/">Zum Portal</a></div></div>'); return; }
      var key = 'pin-' + cid, uid = s.user.id;
      var roster = (kids || []).slice().sort(kidSort).map(function (k) { return { id: k.id, name: k.name }; });
      var nameOf = {}; roster.forEach(function (k) { nameOf[k.id] = k.name; });
      var db = pinBridge({
        active: function () { return UI.view === 'pin'; },
        load: async function () { var d = (await DB.storeGet(key)) || {}; return { boards: d.boards || {}, ideas: d.ideas || {}, settings: d.settings || {}, votes: d.votes || {} }; },
        put: function (coll, id, obj) { if (coll === 'votes') return Promise.resolve(); return DB.pinPut(cid, coll, id, obj); },
        add: async function (coll, obj) { var id = 'i' + Date.now().toString(36) + Math.random().toString(36).slice(2, 7); await DB.pinPut(cid, coll, id, obj); return id; },
        vote: async function () {},
        voteDoc: function (id, v) { return { name: nameOf[id] || 'Kind', r: JSON.parse(JSON.stringify((v && v.r) || {})), at: v && v.at }; }
      });
      window.knPin = {
        mode: 'teacher', name: 'Lehrperson', roster: roster,
        back: function () { if (document.fullscreenElement && document.exitFullscreen) document.exitFullscreen().catch(function () {}); location.hash = '#/'; },
        claude: { use: async function (n) {
          if (n === 'db') return db;
          if (n === 'user') return { me: async function () { return { id: uid, isOwner: true, canEdit: true }; } };
          return null;
        } }
      };
      paint('<div class="folie"><iframe src="pinnwand.html?v=' + PIN_VER + '" title="Klassen-Pinnwand" allow="fullscreen"></iframe></div>');
    }
  };
  // ===================================================================
  // Otterteich (Ruhe-Werkzeug für den Beamer): eigene Seite otterteich.html, Namen der Klasse aus der Klassenkiste
  // ===================================================================
  // ===================================================================
  // Atelier (Velo-Weg): eigene Seite atelier.html, Kinder der Klasse aus der Klassenkiste.
  // Speicher «atelier-<Klasse>» = { open, kids: { Kind-ID: { thema, umsetzung, stufe, farbe, x, y } } }
  // ===================================================================
  var ATELIER_VER = '6';
  var ATELIER_SVG = '<svg viewBox="0 0 64 64" width="54" height="54" aria-hidden="true"><g fill="none" stroke="#3f8fd6" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="16" cy="42" r="10"/><circle cx="48" cy="42" r="10"/><path d="M16 42l10-18h16l6 18M26 24l8 18h6M42 24l-2-6h-6M22 18h8"/></g><rect x="38" y="8" width="18" height="9" rx="3" fill="#e0584f"/></svg>';
  var AT = {
    start: async function (cid) {
      UI.view = 'atelier';
      var s = await DB.session();
      if (!s) { location.hash = '#/'; return; }
      if (!(await toolGate('atelier', 'Das Atelier'))) return;
      app.innerHTML = '<p class="boot">Atelier wird geladen …</p>';
      var cls, kids;
      try { cls = (await DB.listClasses()).filter(function (c) { return c.id === cid; })[0]; kids = await DB.listKids(cid); } catch (e) { cls = null; }
      if (!cls) { paint('<div class="main"><div class="card stack"><h2>Atelier nicht verfügbar</h2><p>Diese Klasse wurde nicht gefunden.</p><a class="btn" href="#/">Zum Portal</a></div></div>'); return; }
      var roster = (kids || []).slice().sort(kidSort), made = false;
      window.knAtelier = {
        mode: 'teacher', className: cls.name,
        back: function () { location.hash = '#/'; },
        load: async function () {
          var d = await DB.storeGet('atelier-' + cid);
          if (!d && !made) { made = true; await DB.atelierPut(cid, '_', { open: false }); d = { open: false, kids: {} }; }
          var m = (d && d.kids) || {};
          return { open: !!(d && d.open), arten: (d && d.arten) || [], kids: roster.map(function (k) { var e = m[k.id] || {};
            return { id: k.id, name: k.name, thema: e.thema || '', umsetzung: e.umsetzung || '', stufe: e.stufe || '', farbe: e.farbe || '', x: e.x == null ? null : e.x, y: e.y == null ? null : e.y }; }) };
        },
        put: function (id, patch) { return DB.atelierPut(cid, id, JSON.parse(JSON.stringify(patch))); },
        setOpen: function (on) { return DB.atelierPut(cid, '_', { open: !!on }); },
        setArten: function (a) { return DB.atelierPut(cid, '_', { arten: a }); }
      };
      paint('<div class="folie"><iframe src="atelier.html?v=' + ATELIER_VER + '" title="Atelier" allow="fullscreen"></iframe></div>');
    }
  };
  // ===================================================================
  // Elterngespräche: Die Lehrperson bietet Termine an, die Eltern kreuzen über einen Link alle möglichen Termine an,
  // die Klassenkiste rechnet laufend einen Plan aus. Tabelle «talks» (Version 22):
  //   cfg = { title, info, open, slots:[{id,d,t,e}], diff:{Kind-ID: 0|1|2}, fixed:{Termin-ID: Kind-ID oder "_"}, dur, gap }
  //   answers = { Kind-ID: { name, slots, note, none, key, at } }
  // Lehrperson: #/gespraeche/<Klasse> (E), Eltern: #/eltern/<Link> (EP, ohne Anmeldung)
  // ===================================================================
  var EG_DIFF = [['leicht', '#7ea56a'], ['mittel', '#d6ad45'], ['anspruchsvoll', '#b5524a']];
  function egMin(t) { var m = /^(\d{1,2}):(\d{2})$/.exec(t || ''); return m ? +m[1] * 60 + +m[2] : 0; }
  function egHM(n) { return String(Math.floor(n / 60)).padStart(2, '0') + ':' + String(n % 60).padStart(2, '0'); }
  function egDay(d, long) {
    var x = new Date(d + 'T12:00:00'); if (isNaN(x)) return d;
    return x.toLocaleDateString('de-CH', long ? { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' } : { weekday: 'short', day: 'numeric', month: 'short' });
  }
  function egSort(sl) { return sl.slice().sort(function (a, b) { return a.d < b.d ? -1 : a.d > b.d ? 1 : egMin(a.t) - egMin(b.t); }); }
  function egDays(sl) { var out = [], by = {}; egSort(sl).forEach(function (s) { if (!by[s.d]) { by[s.d] = []; out.push({ d: s.d, list: by[s.d] }); } by[s.d].push(s); }); return out; }
  function egLabel(s) { return s ? egDay(s.d) + ', ' + s.t + '–' + s.e : '?'; }
  function egKey() { var a = new Uint8Array(16); crypto.getRandomValues(a); return Array.prototype.map.call(a, function (b) { return ('0' + b.toString(16)).slice(-2); }).join(''); }
  function egSid() { return 's' + Date.now().toString(36).slice(-4) + egKey().slice(0, 6); }
  function egHint(e) { return /talks|eltern_|talk_answer|schema cache|relation|does not exist/i.test((e && e.message) || '') ? 'Dafür zuerst das neue SQL (Version 22) in Supabase ausführen.' : errMsg(e); }

  // Grösstmögliche Zuteilung: jede Familie höchstens ein Termin, jeder Termin höchstens eine Familie.
  // Familien mit wenig Möglichkeiten kommen zuerst dran, sonst der früheste mögliche Termin.
  function egMatch(fams, avail, free) {
    var kidOf = {}, slotOf = {};
    function go(f, seen) {
      var l = avail[f] || [];
      for (var i = 0; i < l.length; i++) {
        var s = l[i]; if (!free[s] || seen[s]) continue; seen[s] = 1;
        if (!kidOf[s] || go(kidOf[s], seen)) { kidOf[s] = f; slotOf[f] = s; return true; }
      }
      return false;
    }
    fams.slice().sort(function (a, b) { return (avail[a] || []).length - (avail[b] || []).length; }).forEach(function (f) { go(f, {}); });
    return { kidOf: kidOf, slotOf: slotOf, n: Object.keys(slotOf).length };
  }
  // Termine, ohne die nicht mehr alle eingetragenen Familien einen Platz hätten (z. B. Eltern, die nur dann können).
  // Diese Termine sind reserviert und verschwinden für Eltern, die sich neu eintragen.
  function egReserved(fams, avail, free) {
    var m = egMatch(fams, avail, free), res = {};
    Object.keys(m.kidOf).forEach(function (s) {
      var f2 = Object.assign({}, free); delete f2[s];
      if (egMatch(fams, avail, f2).n < m.n) res[s] = true;
    });
    return res;
  }
  // Der ganze Plan für die Lehrperson: Fixiertes bleibt, der Rest wird zugeteilt,
  // danach so getauscht, dass anspruchsvolle Gespräche möglichst nicht direkt hintereinander kommen.
  function egPlan(cfg, answers, kids) {
    var slots = egSort(cfg.slots || []), byId = {}, pos = {}, fixed = {}, fixedKid = {}, isKid = {};
    kids.forEach(function (k) { isKid[k.id] = true; });
    slots.forEach(function (s, i) { byId[s.id] = s; pos[s.id] = i; });
    Object.keys(cfg.fixed || {}).forEach(function (s) {
      var k = cfg.fixed[s]; if (!byId[s] || !(k === '_' || isKid[k]) || (k !== '_' && fixedKid[k])) return;
      fixed[s] = k; if (k !== '_') fixedKid[k] = s;
    });
    var free = {}; slots.forEach(function (s) { if (!fixed[s.id]) free[s.id] = 1; });
    var fams = [], avail = {};
    kids.forEach(function (k) {
      var a = answers[k.id]; if (!a || fixedKid[k.id] || a.none) return;
      avail[k.id] = (a.slots || []).filter(function (s) { return free[s]; }).sort(function (x, y) { return pos[x] - pos[y]; });
      fams.push(k.id);
    });
    var m = egMatch(fams, avail, free), kidOf = m.kidOf, slotOf = m.slotOf, diff = cfg.diff || {};
    function dv(k) { return k && k !== '_' ? Math.max(0, Math.min(2, +diff[k] || 0)) : 0; }
    function who(s) { return fixed[s] || kidOf[s] || null; }
    // Nachbarn: gleicher Tag, höchstens 10 Minuten Pause dazwischen
    var pairs = [];
    for (var i = 1; i < slots.length; i++) { var a = slots[i - 1], b = slots[i]; if (a.d === b.d && egMin(b.t) - egMin(a.e) <= 10) pairs.push([a.id, b.id]); }
    var W = [[0, 0, 0], [0, 1, 3], [0, 3, 10]];
    function pen() { var p = 0; pairs.forEach(function (q) { p += W[dv(who(q[0]))][dv(who(q[1]))]; }); return p; }
    var cur = pen(), rounds = 0, better = cur > 0;
    while (better && rounds++ < 40) {
      better = false;
      fams.forEach(function (f) {
        if (!slotOf[f]) return;
        avail[f].forEach(function (s) {
          var mine = slotOf[f]; if (s === mine || cur === 0) return;
          var g = kidOf[s]; if (g && avail[g].indexOf(mine) < 0) return;
          kidOf[s] = f; slotOf[f] = s; if (g) { kidOf[mine] = g; slotOf[g] = mine; } else delete kidOf[mine];
          var p = pen(); if (p < cur) { cur = p; better = true; return; }
          kidOf[mine] = f; slotOf[f] = mine; if (g) { kidOf[s] = g; slotOf[g] = s; } else delete kidOf[s];
        });
      });
    }
    return { slots: slots, byId: byId, fixed: fixed, fixedKid: fixedKid, kidOf: kidOf, slotOf: slotOf, fams: fams, avail: avail,
      reserved: egReserved(fams, avail, free),
      warn: pairs.filter(function (q) { return W[dv(who(q[0]))][dv(who(q[1]))] >= 3; }).map(function (q) { return [who(q[0]), who(q[1]), q[0]]; }),
      unplaced: fams.filter(function (f) { return !slotOf[f]; }) };
  }

  // ---------- Lehrperson ----------
  var E = {
    // #/gespraeche/<Klasse> = Liste der Gespräche, #/gespraeche/<Klasse>/<Gespräch> = ein Gespräch planen
    start: async function (cid, tid) {
      UI.view = 'eg';
      var s = await DB.session();
      if (!s) { location.hash = '#/'; return; }
      document.body.classList.add('lp');
      if (!(await toolGate('eltern', 'Elterngespräche'))) return;
      app.innerHTML = '<p class="boot">Elterngespräche werden geladen …</p>';
      E.cid = cid; E.open = {}; E.row = null; E.list = null;
      try {
        E.cls = (await DB.listClasses()).filter(function (c) { return c.id === cid; })[0];
        if (!E.cls) throw new Error('Diese Klasse wurde nicht gefunden.');
        E.kids = (await DB.listKids(cid)).slice().sort(kidSort);
        if (!tid) { E.list = await DB.talkList(cid); return E.renderList(); }
        E.row = await DB.talkGet(tid);
        if (!E.row || E.row.class_id !== cid) { location.hash = '#/gespraeche/' + cid; return; }
      } catch (e) {
        paint('<div class="umf-page">' + egTop(backBtn('href="#/"')) + '<div class="card stack"><h2>Elterngespräche nicht verfügbar</h2><p>' + h(egHint(e)) + '</p></div></div>');
        return;
      }
      egFill(E.row);
      E.render();
      // neue Einträge der Eltern laufend holen
      every(15000, async function () {
        if (document.hidden || document.querySelector('.overlay') || E.busy || !E.row) return;
        var a = document.activeElement; if (a && /INPUT|TEXTAREA|SELECT/.test(a.tagName)) return;
        try { var r = await DB.talkGet(E.row.id); if (r && JSON.stringify(r.answers) !== JSON.stringify(E.row.answers)) { E.row.answers = r.answers || {}; E.render(); } } catch (e) {}
      });
    },
    link: function () { return location.origin + location.pathname + '#/eltern/' + E.row.token; },
    save: async function () {
      E.busy = true;
      try { await DB.talkSave(E.row.id, JSON.parse(JSON.stringify(E.row.cfg))); }
      catch (e) { toast(egHint(e)); }
      finally { E.busy = false; }
    },
    // Kinder, die bei diesem Gespräch dabei sind (cfg.kids fehlt = alle)
    inKids: function (c) { var l = c.kids; return Array.isArray(l) ? E.kids.filter(function (k) { return l.indexOf(k.id) >= 0; }) : E.kids; }
  };
  function egFill(row) {
    var c = row.cfg || (row.cfg = {});
    if (!Array.isArray(c.slots)) c.slots = [];
    ['diff', 'fixed'].forEach(function (k) { if (!c[k] || typeof c[k] !== 'object') c[k] = {}; });
    row.answers = row.answers || {};
  }
  function egTop(left) {
    return '<div class="umf-top eg-noprint"><div class="row">' + left + '</div><span class="umf-kick"><img src="' + h(klassBild(E.cls && E.cls.bild)) + '" alt="" width="40" height="40">Elterngespräche' +
      (E.cls ? ' · Klasse ' + h(E.cls.name) : '') + ' <span class="sterne" aria-hidden="true">✦ ✧ ✦</span></span><div class="row"></div></div>';
  }
  function egSpan(c) {
    var d = egSort(c.slots || []); if (!d.length) return 'noch keine Termine';
    var a = egDay(d[0].d, true), b = egDay(d[d.length - 1].d, true);
    return a === b ? a : egDay(d[0].d) + ' bis ' + egDay(d[d.length - 1].d);
  }
  function egState(c) {
    var d = egSort(c.slots || []), today = new Date().toISOString().slice(0, 10);
    if (d.length && d[d.length - 1].d < today) return ['vorbei', 'eg-alt'];
    return c.open ? ['Anmeldung offen', 'eg-auf'] : ['Anmeldung geschlossen', ''];
  }
  // ---------- Liste: alle Elterngespräche der Klasse ----------
  E.renderList = function () {
    var out = '<div class="umf-page eg">' + egTop(backBtn('href="#/"')) +
      '<section class="umf-hero card"><img class="umf-hero-bild" src="' + h(klassBild(E.cls.bild)) + '" alt="" width="110" height="110"><div class="stack" style="gap:8px;flex:1 1 320px"><h1>Elterngespräche</h1>' +
      '<p class="muted">Jedes Gespräch bleibt gespeichert. So können Sie mehrere gleichzeitig planen und später nachschauen, wann welches Gespräch war.</p></div>' +
      '<button class="btn primary big" data-a="egNew">＋ Neues Elterngespräch</button></section>';
    if (!E.list.length) out += '<div class="empty">Noch keine Elterngespräche. Tippen Sie auf «Neues Elterngespräch».</div>';
    else out += '<div class="umf-grid">' + E.list.map(function (t) {
      egFill(t);
      var c = t.cfg, st = egState(c), kids = E.inKids(c), ans = t.answers, n = kids.filter(function (k) { return ans[k.id]; }).length, key = 'egdel:' + t.id;
      return '<div class="card umf-card eg-tcard"><a class="umf-card-open" href="#/gespraeche/' + E.cid + '/' + t.id + '"><span class="pill eg-st-' + st[1] + '">' + st[0] + '</span>' +
        '<b class="eg-ttitle">' + h(c.title || 'Elterngespräche') + '</b><span class="muted">' + h(egSpan(c)) + '</span>' +
        '<span class="muted small">' + n + ' von ' + kids.length + ' eingetragen · ' + plural(c.slots.length, 'Termin', 'Termine') + '</span></a>' +
        '<div class="row"><a class="btn sm primary" href="#/gespraeche/' + E.cid + '/' + t.id + '">Öffnen</a>' +
        '<button class="btn sm danger' + (UI.confirm === key ? ' armed' : '') + '" data-a="egDel" data-id="' + t.id + '">' + (UI.confirm === key ? 'Wirklich löschen?' : 'Löschen') + '</button></div></div>';
    }).join('') + '</div>';
    paint(out + '</div>');
  };
  ACT.egNew = async function () {
    var m = new Date().toLocaleDateString('de-CH', { month: 'long', year: 'numeric' }), row;
    try { row = await DB.talkNew(E.cid, { title: 'Elterngespräche ' + m, info: '', open: false, slots: [], diff: {}, fixed: {}, dur: 20, gap: 5 }); }
    catch (e) { return toast(egHint(e)); }
    location.hash = '#/gespraeche/' + E.cid + '/' + row.id;
  };
  ACT.egDel = async function (el) {
    if (!armed('egdel:' + el.dataset.id)) return E.list ? E.renderList() : null;
    try { await DB.talkDelete(el.dataset.id); } catch (e) { return toast(egHint(e)); }
    E.list = E.list.filter(function (t) { return t.id !== el.dataset.id; }); toast('Gelöscht.'); E.renderList();
  };
  function egHead(sub) {
    return '<header class="top"><div class="top-in"><span class="marke"><span class="marke-bild"><img src="bilder/eule.webp" alt="" width="60" height="60"></span>' +
      '<span class="marke-text"><b>' + markeName() + '<i aria-hidden="true">✦</i></b><small>' + h(sub) + '</small></span></span></div></header>';
  }
  function egDot(v) { var d = EG_DIFF[v || 0]; return '<span class="eg-dot" style="background:' + d[1] + '" title="' + d[0] + '"></span>'; }
  E.render = function () {
    if (!E.row) return E.list ? E.renderList() : null;
    var c = E.row.cfg, ans = E.row.answers || {}, kids = E.inKids(c), P = egPlan(c, ans, kids);
    var name = {}; E.kids.forEach(function (k) { name[k.id] = k.name; });
    var nAns = kids.filter(function (k) { return ans[k.id] || P.fixedKid[k.id]; }).length;
    var nPlan = Object.keys(P.fixedKid).length + Object.keys(P.slotOf).length;
    var out = '<div class="umf-page eg">' + egTop(backBtn('href="#/gespraeche/' + E.cid + '"', 'Zurück zu allen Elterngesprächen'));
    out += '<section class="umf-hero card eg-noprint"><img class="umf-hero-bild" src="' + h(klassBild(E.cls.bild)) + '" alt="" width="110" height="110"><div class="stack" style="gap:8px;flex:1 1 320px">' +
      '<h1>' + h(c.title || 'Elterngespräche') + '</h1>' +
      '<p class="muted">① Termine eintragen · ② Link an die Eltern schicken · ③ Plan anschauen und fixieren</p>' +
      '<div class="row eg-stats"><span class="pill">' + nAns + ' von ' + kids.length + ' eingetragen</span><span class="pill">' + nPlan + ' eingeplant</span>' +
      (P.unplaced.length ? '<span class="pill eg-bad">' + P.unplaced.length + ' ohne Platz</span>' : '') + '<span class="pill">' + plural(c.slots.length, 'Termin', 'Termine') + '</span></div></div></section>';

    // ① Termine
    var dur = c.dur || 20, gap = c.gap == null ? 5 : c.gap;
    out += '<section class="card stack eg-noprint"><h2>① Termine</h2>' +
      '<form class="eg-add" data-a="egAdd"><div class="field"><label for="egD">Datum</label><input class="input" id="egD" name="d" type="date" required></div>' +
      '<div class="field"><label for="egF">Von</label><input class="input" id="egF" name="from" type="time" value="' + h(c.lastFrom || '16:00') + '" required></div>' +
      '<div class="field"><label for="egT">Bis</label><input class="input" id="egT" name="to" type="time" value="' + h(c.lastTo || '18:00') + '" required></div>' +
      '<div class="field"><label for="egDur">Gespräch (Min.)</label><input class="input" id="egDur" name="dur" type="number" min="5" max="120" value="' + dur + '"></div>' +
      '<div class="field"><label for="egGap">Pause (Min.)</label><input class="input" id="egGap" name="gap" type="number" min="0" max="60" value="' + gap + '"></div>' +
      '<button class="btn primary">Termine hinzufügen</button></form>' +
      (c.slots.length ? egDays(c.slots).map(function (day) {
        return '<div class="eg-day"><div class="row" style="justify-content:space-between"><h3>' + h(egDay(day.d, true)) + '</h3><button class="btn sm danger' + (UI.confirm === 'egday:' + day.d ? ' armed' : '') + '" data-a="egDelDay" data-d="' + h(day.d) + '">' + (UI.confirm === 'egday:' + day.d ? 'Wirklich den ganzen Tag löschen?' : 'Tag löschen') + '</button></div>' +
          '<div class="eg-chips">' + day.list.map(function (s) {
            return '<span class="eg-chip' + (P.fixed[s.id] ? ' fix' : '') + '">' + h(s.t) + '–' + h(s.e) + '<button data-a="egDelSlot" data-s="' + h(s.id) + '" aria-label="Termin ' + h(s.t) + ' löschen" title="löschen">×</button></span>';
          }).join('') + '</div></div>';
      }).join('') : '<div class="empty">Noch keine Termine. Wählen Sie oben Datum und Zeit, die Klassenkiste teilt die Zeit in einzelne Gespräche auf.</div>') + '</section>';

    // ② Link
    var on = !!c.open;
    out += '<section class="card stack eg-noprint"><h2>② Link für die Eltern</h2>' +
      '<button class="switch" role="switch" aria-checked="' + on + '" data-a="egOpen"><span>' + (on ? 'Eltern können sich jetzt eintragen' : 'Anmeldung ist geschlossen · zum Öffnen tippen') + '</span><span class="track"></span></button>' +
      '<div class="field"><label for="egTitle">Titel</label><input class="input" id="egTitle" maxlength="80" value="' + h(c.title || '') + '" data-change="egTitle" placeholder="z. B. Elterngespräche Herbst"></div>' +
      '<div class="field"><label for="egInfo">Hinweis für die Eltern (freiwillig)</label><textarea class="input" id="egInfo" rows="3" maxlength="600" data-change="egInfo" placeholder="z. B. Die Gespräche finden im Schulzimmer statt und dauern etwa 20 Minuten.">' + h(c.info || '') + '</textarea></div>' +
      '<div class="eg-link"><input class="input" id="egLink" readonly value="' + h(E.link()) + '" aria-label="Link für die Eltern">' +
      '<button class="btn" data-a="egCopy">Link kopieren</button><button class="btn" data-a="egQR">QR-Code</button><a class="btn" href="' + h(E.link()) + '" target="_blank" rel="noopener">Elternansicht</a></div>' +
      '<p class="muted small">Die Eltern wählen ihr Kind aus der Klassenliste und kreuzen alle Termine an, an denen sie können. Wer den Link hat, sieht die Vornamen der Klasse – schicken Sie ihn nur an die Eltern.</p>' +
      '<div class="row"><button class="btn sm danger' + (UI.confirm === 'eglink' ? ' armed' : '') + '" data-a="egNewLink">' + (UI.confirm === 'eglink' ? 'Wirklich? Der alte Link geht dann nicht mehr' : 'Neuen Link erstellen') + '</button>' +
      '<button class="btn sm danger' + (UI.confirm === 'egreset' ? ' armed' : '') + '" data-a="egReset">' + (UI.confirm === 'egreset' ? 'Wirklich alle Einträge und Fixierungen löschen?' : 'Alle Einträge löschen') + '</button></div></section>';

    // ③ Plan
    var kidOpts = function (s) {
      var chose = kids.filter(function (k) { return !P.fixedKid[k.id] && ans[k.id] && (ans[k.id].slots || []).indexOf(s) >= 0; });
      var rest = kids.filter(function (k) { return !P.fixedKid[k.id] && chose.indexOf(k) < 0; });
      return '<option value="">Fix eintragen …</option>' + chose.map(function (k) { return '<option value="' + k.id + '">✓ ' + h(k.name) + ' (kann dann)</option>'; }).join('') +
        rest.map(function (k) { return '<option value="' + k.id + '">' + h(k.name) + '</option>'; }).join('') + '<option value="_">⛔ Termin sperren (Pause)</option>';
    };
    out += '<section class="card stack eg-plancard"><div class="row" style="justify-content:space-between"><h2>③ Plan · Klasse ' + h(E.cls.name) + '</h2><div class="row eg-noprint">' +
      (Object.keys(P.slotOf).length ? '<button class="btn sm" data-a="egFixAll">📌 Alle Vorschläge fixieren</button>' : '') + '<button class="btn sm" data-a="egPrint">Drucken</button></div></div>' +
      '<p class="muted small eg-noprint">Der Plan wird bei jedem neuen Eintrag neu ausgerechnet. «Vorschlag» kann sich noch ändern, 📌 fixierte Termine bleiben und verschwinden für die Eltern. ' +
      '🔒 = nur so bekommen alle eingetragenen Familien einen Platz; diese Zeit ist für neue Eltern schon ausgeblendet. Tippen Sie auf eine Zeit, um zu sehen, wer sie angekreuzt hat (die Zahl daneben).</p>';
    if (P.unplaced.length) out += '<div class="note eg-noprint"><b>Kein Platz gefunden für:</b> ' + P.unplaced.map(function (k) {
      return h(name[k]) + ' <span class="muted">(' + (P.avail[k].length ? P.avail[k].map(function (s) { return h(egLabel(P.byId[s])); }).join(', ') : 'keine freien Termine angekreuzt') + ')</span>';
    }).join('; ') + '<br>Tipp: einen weiteren Termin anbieten, einen fixierten Termin lösen oder mit den Eltern sprechen.</div>';
    if (P.warn.length) out += '<div class="note eg-noprint"><b>Hintereinander:</b> ' + P.warn.map(function (w) {
      return h(name[w[0]] || '') + ' und ' + h(name[w[1]] || '') + ' (' + h(egDay(P.byId[w[2]].d)) + ')';
    }).join('; ') + ' – anders ging es mit den angekreuzten Terminen nicht. Fixieren Sie einen davon von Hand an einem anderen Termin, wenn Sie möchten.</div>';
    if (!c.slots.length) out += '<div class="empty">Sobald es Termine gibt, steht hier der Plan.</div>';
    out += egDays(c.slots).map(function (day) {
      return '<div class="eg-planday"><h3>' + h(egDay(day.d, true)) + '</h3><ol class="eg-rows">' + day.list.map(function (s) {
        var fk = P.fixed[s.id], sk = P.kidOf[s.id], body;
        if (fk === '_') body = '<span class="eg-who muted">gesperrt (Pause)</span><button class="btn sm eg-noprint" data-a="egUnfix" data-s="' + s.id + '">freigeben</button>';
        else if (fk) body = '<span class="eg-who">' + egDot(c.diff[fk]) + '<b>' + h(name[fk]) + '</b>' + (ans[fk] && ans[fk].name ? ' <span class="muted small">· ' + h(ans[fk].name) + '</span>' : '') + '</span><span class="pill eg-fix">📌 fixiert</span><button class="btn sm eg-noprint" data-a="egUnfix" data-s="' + s.id + '">lösen</button>';
        else if (sk) body = '<span class="eg-who">' + egDot(c.diff[sk]) + '<b>' + h(name[sk]) + '</b>' + (ans[sk] && ans[sk].name ? ' <span class="muted small">· ' + h(ans[sk].name) + '</span>' : '') + '</span><span class="pill eg-vor">Vorschlag' + (P.reserved[s.id] ? ' 🔒' : '') + '</span>' +
          '<button class="btn sm eg-noprint" data-a="egFix" data-s="' + s.id + '" data-k="' + sk + '">📌 fixieren</button>';
        else body = '<span class="eg-who muted">frei</span><select class="input eg-sel eg-noprint" data-change="egFixSel" data-s="' + s.id + '" aria-label="Termin ' + h(s.t) + ' fix vergeben">' + kidOpts(s.id) + '</select>';
        // Aufklappen: wer hat diesen Termin angekreuzt?
        var who = kids.filter(function (k) { return ans[k.id] && (ans[k.id].slots || []).indexOf(s.id) >= 0; }), op = !!E.open[s.id];
        var more = op ? '<div class="eg-wholist">' + (who.length ? '<b>Diesen Termin haben angekreuzt:</b><ul>' + who.map(function (k) {
          var a = ans[k.id], where = P.fixedKid[k.id] || P.slotOf[k.id];
          return '<li>' + egDot(c.diff[k.id]) + '<b>' + h(k.name) + '</b>' + (a.name ? ' <span class="muted small">· ' + h(a.name) + '</span>' : '') +
            ' <span class="muted small">(' + plural((a.slots || []).length, 'Termin', 'Termine') + ' gewählt' + (where && where !== s.id ? ', eingeplant ' + h(egLabel(P.byId[where])) : '') + ')</span></li>';
        }).join('') + '</ul>' : '<span class="muted">Noch niemand hat diesen Termin angekreuzt.</span>') + '</div>' : '';
        return '<li class="' + (fk ? (fk === '_' ? 'blk' : 'fix') : sk ? 'vor' : 'frei') + (op ? ' auf' : '') + '"><button class="eg-time" data-a="egSlotOpen" data-s="' + s.id + '" aria-expanded="' + op + '" title="Wer hat diesen Termin angekreuzt?">' +
          '<span class="eg-pfeil eg-noprint" aria-hidden="true">' + (op ? '▾' : '▸') + '</span>' + h(s.t) + '–' + h(s.e) + '<span class="eg-n eg-noprint">' + who.length + '</span></button>' + body + more + '</li>';
      }).join('') + '</ol></div>';
    }).join('') + '</section>';

    // Kinder und Eltern: wer muss sich anmelden?
    var inSet = {}; kids.forEach(function (k) { inSet[k.id] = 1; });
    var outKids = E.kids.filter(function (k) { return !inSet[k.id]; });
    out += '<section class="card stack eg-noprint"><div class="row" style="justify-content:space-between"><h2>Kinder und Eltern</h2><div class="row">' +
      '<button class="btn sm" data-a="egAll" data-v="1">Alle dabei</button><button class="btn sm" data-a="egAll" data-v="0">Niemand</button></div></div>' +
      '<p class="muted small">Nur die Kinder, die «dabei» sind, erscheinen bei den Eltern zur Auswahl. Wie anspruchsvoll ein Gespräch ist, sehen nur Sie. Die Klassenkiste plant anspruchsvolle Gespräche möglichst nicht direkt hintereinander.</p>' +
      (kids.length ? '<ul class="list eg-kids">' + kids.map(function (k) {
        var a = ans[k.id], fs = P.fixedKid[k.id], st;
        if (fs) st = '<span class="eg-st ok">📌 ' + h(egLabel(P.byId[fs])) + '</span>';
        else if (a && a.none) st = '<span class="eg-st bad">Kein Termin passt</span>';
        else if (a) st = '<span class="eg-st ok">✓ ' + plural((a.slots || []).length, 'Termin', 'Termine') + (P.slotOf[k.id] ? ' · Vorschlag ' + h(egLabel(P.byId[P.slotOf[k.id]])) : ' · noch kein Platz') + '</span>';
        else st = '<span class="eg-st">noch offen</span>';
        return '<li><button class="eg-in on" data-a="egIn" data-k="' + k.id + '" title="Nicht mehr dabei">✓ dabei</button><div class="eg-kid"><b>' + h(k.name) + '</b>' + (a && a.name ? '<span class="muted small">' + h(a.name) + (a.lp ? ' (von Ihnen eingetragen)' : '') + '</span>' : '') + st +
          (a && a.note ? '<span class="eg-note">«' + h(a.note) + '»</span>' : '') + '</div>' +
          '<div class="eg-diff" role="group" aria-label="Wie anspruchsvoll">' + EG_DIFF.map(function (d, i) {
            return '<button class="chip" style="--c:' + d[1] + '" aria-pressed="' + ((+c.diff[k.id] || 0) === i) + '" data-a="egDiff" data-k="' + k.id + '" data-v="' + i + '">' + d[0] + '</button>'; }).join('') + '</div>' +
          '<button class="btn sm" data-a="egEdit" data-k="' + k.id + '">' + (a ? 'Termine ändern' : 'Selbst eintragen') + '</button></li>';
      }).join('') + '</ul>' : '<div class="empty">' + (E.kids.length ? 'Noch kein Kind dabei. Tippen Sie unten auf die Kinder, die sich anmelden sollen.' : 'Diese Klasse hat noch keine Kinder. Tragen Sie sie im Reiter «Kinder» ein.') + '</div>') +
      (outKids.length ? '<div class="stack" style="gap:8px"><span class="lbl">Nicht dabei (müssen sich nicht anmelden):</span><div class="eg-chips">' + outKids.map(function (k) {
        return '<button class="eg-in" data-a="egIn" data-k="' + k.id + '" title="Dazunehmen">＋ ' + h(k.name) + '</button>'; }).join('') + '</div></div>' : '') + '</section>';
    paint(out + '</div>');
  };
  ACT.egSlotOpen = function (el) { var s = el.dataset.s; if (E.open[s]) delete E.open[s]; else E.open[s] = 1; E.render(); };
  ACT.egIn = async function (el) {
    var c = E.row.cfg, k = el.dataset.k, l = Array.isArray(c.kids) ? c.kids.slice() : E.kids.map(function (x) { return x.id; });
    var i = l.indexOf(k); if (i >= 0) l.splice(i, 1); else l.push(k);
    c.kids = l.length === E.kids.length ? null : l; if (!c.kids) delete c.kids;
    await egSaveRender();
  };
  ACT.egAll = async function (el) { if (+el.dataset.v) delete E.row.cfg.kids; else E.row.cfg.kids = []; await egSaveRender(); };
  async function egSaveRender() { E.render(); await E.save(); }
  ACT.egAdd = async function (f) {
    var c = E.row.cfg, d = f.elements.d.value, a = egMin(f.elements.from.value), b = egMin(f.elements.to.value);
    var dur = Math.max(5, Math.min(120, +f.elements.dur.value || 20)), gap = Math.max(0, Math.min(60, +f.elements.gap.value || 0));
    if (!d || b <= a) return toast('Bitte Datum und eine Endzeit nach der Startzeit wählen.');
    var n = 0;
    for (var t = a; t + dur <= b; t += dur + gap) {
      var hm = egHM(t);
      if (c.slots.some(function (s) { return s.d === d && s.t === hm; })) continue;
      if (c.slots.length >= 300) { toast('Höchstens 300 Termine.'); break; }
      c.slots.push({ id: egSid(), d: d, t: hm, e: egHM(t + dur) }); n++;
    }
    if (!n) return toast('In dieser Zeit hat kein Gespräch Platz (oder die Termine gibt es schon).');
    c.dur = dur; c.gap = gap; c.lastFrom = f.elements.from.value; c.lastTo = f.elements.to.value;
    c.slots = egSort(c.slots);
    toast(plural(n, 'Termin', 'Termine') + ' hinzugefügt.');
    await egSaveRender();
  };
  ACT.egDelSlot = async function (el) {
    var c = E.row.cfg, id = el.dataset.s;
    c.slots = c.slots.filter(function (s) { return s.id !== id; }); delete c.fixed[id];
    await egSaveRender();
  };
  ACT.egDelDay = async function (el) {
    var d = el.dataset.d; if (!armed('egday:' + d)) return E.render();
    var c = E.row.cfg; c.slots = c.slots.filter(function (s) { if (s.d === d) { delete c.fixed[s.id]; return false; } return true; });
    await egSaveRender();
  };
  ACT.egOpen = async function () { E.row.cfg.open = !E.row.cfg.open; toast(E.row.cfg.open ? 'Die Eltern können sich jetzt eintragen.' : 'Anmeldung geschlossen.'); await egSaveRender(); };
  ACT.egTitle = async function (el) { E.row.cfg.title = el.value.trim().slice(0, 80); await egSaveRender(); toast('Gespeichert.'); };
  ACT.egInfo = async function (el) { E.row.cfg.info = el.value.trim().slice(0, 600); await E.save(); toast('Gespeichert.'); };
  ACT.egCopy = async function () {
    try { await navigator.clipboard.writeText(E.link()); toast('Link kopiert. Jetzt z. B. in die Eltern-Nachricht einfügen.'); }
    catch (e) { var i = document.getElementById('egLink'); i.select(); toast('Link markiert – jetzt kopieren.'); }
  };
  ACT.egQR = function () {
    var o = overlay('<div class="bigcode"><p>' + h(E.row.cfg.title || 'Elterngespräche') + ' · Klasse ' + h(E.cls.name) + '</p>' +
      '<div class="bigcode-row"><div class="qrbox" id="qrBox" role="img" aria-label="QR-Code für die Eltern">QR-Code wird geladen …</div></div>' +
      '<button class="btn" style="align-self:center" data-a="closeOverlay">Schliessen</button></div>');
    qrSvg(E.link()).then(function (svg) { var b = o.querySelector('#qrBox'); if (b) b.innerHTML = svg; })
      .catch(function () { var b = o.querySelector('#qrBox'); if (b) b.textContent = 'QR-Code nicht verfügbar.'; });
  };
  ACT.egNewLink = async function () {
    if (!armed('eglink')) return E.render();
    var t = crypto.randomUUID ? crypto.randomUUID() : null; if (!t) return toast('Dieser Browser kann keinen neuen Link erstellen.');
    try { await DB.talkReset(E.row.id, { token: t }); E.row.token = t; toast('Neuer Link erstellt.'); } catch (e) { toast(egHint(e)); }
    E.render();
  };
  ACT.egReset = async function () {
    if (!armed('egreset')) return E.render();
    try { await DB.talkReset(E.row.id, { answers: {} }); E.row.answers = {}; E.row.cfg.fixed = {}; await E.save(); toast('Alle Einträge gelöscht. Die Termine sind noch da.'); } catch (e) { toast(egHint(e)); }
    E.render();
  };
  function egSetFix(s, k) {
    var fx = E.row.cfg.fixed;
    if (k !== '_') Object.keys(fx).forEach(function (x) { if (fx[x] === k) delete fx[x]; });
    fx[s] = k;
  }
  ACT.egFix = async function (el) { egSetFix(el.dataset.s, el.dataset.k); toast('Fixiert. Dieser Termin verschwindet für die anderen Eltern.'); await egSaveRender(); };
  ACT.egFixSel = async function (el) { if (!el.value) return; egSetFix(el.dataset.s, el.value); await egSaveRender(); };
  ACT.egUnfix = async function (el) { delete E.row.cfg.fixed[el.dataset.s]; await egSaveRender(); };
  ACT.egFixAll = async function () {
    var P = egPlan(E.row.cfg, E.row.answers, E.inKids(E.row.cfg)), n = 0;
    Object.keys(P.kidOf).forEach(function (s) { egSetFix(s, P.kidOf[s]); n++; });
    toast(plural(n, 'Termin', 'Termine') + ' fixiert.'); await egSaveRender();
  };
  ACT.egPrint = function () { window.print(); };
  ACT.egDiff = async function (el) { E.row.cfg.diff[el.dataset.k] = +el.dataset.v; if (!+el.dataset.v) delete E.row.cfg.diff[el.dataset.k]; await egSaveRender(); };
  // Lehrperson trägt für eine Familie ein (z. B. nach einem Telefon)
  ACT.egEdit = function (el) {
    var k = el.dataset.k, kid = E.kids.filter(function (x) { return x.id === k; })[0], a = E.row.answers[k] || {}, sel = a.slots || [], fx = E.row.cfg.fixed;
    overlay('<form class="dialog stack eg-dlg" role="dialog" aria-label="Termine eintragen" data-a="egEditSave" data-k="' + k + '"><h2 style="font-size:30px">Termine für ' + h(kid.name) + '</h2>' +
      '<div class="field"><label for="egEName">Name der Eltern</label><input class="input" id="egEName" name="name" maxlength="80" value="' + h(a.name || '') + '"></div>' +
      '<span class="lbl">An diesen Terminen können die Eltern:</span>' +
      egDays(E.row.cfg.slots).map(function (day) {
        return '<div class="eg-dday"><b>' + h(egDay(day.d)) + '</b><div class="eg-chips">' + day.list.map(function (s) {
          var other = fx[s.id] && fx[s.id] !== k;
          return '<label class="eg-tick' + (other ? ' off' : '') + '"><input type="checkbox" name="s" value="' + h(s.id) + '"' + (sel.indexOf(s.id) >= 0 ? ' checked' : '') + (other ? ' disabled' : '') + '>' + h(s.t) + '</label>';
        }).join('') + '</div></div>';
      }).join('') +
      '<label class="row" style="gap:10px"><input type="checkbox" name="none" style="width:22px;height:22px"' + (a.none ? ' checked' : '') + '> Kein Termin passt</label>' +
      '<div class="field"><label for="egENote">Bemerkung</label><textarea class="input" id="egENote" name="note" rows="2" maxlength="500">' + h(a.note || '') + '</textarea></div>' +
      '<div class="row"><button class="btn primary">Speichern</button>' + (E.row.answers[k] ? '<button type="button" class="btn danger" data-a="egEditDel" data-k="' + k + '">Eintrag löschen</button>' : '') +
      '<button type="button" class="btn" data-a="closeOverlay">Abbrechen</button></div>' +
      (E.row.answers[k] ? '<p class="muted small">«Eintrag löschen» gibt das Kind wieder frei, damit sich die Eltern neu eintragen können.</p>' : '') + '</form>');
  };
  ACT.egEditSave = async function (f) {
    var k = f.dataset.k, sl = Array.prototype.filter.call(f.querySelectorAll('input[name=s]'), function (x) { return x.checked; }).map(function (x) { return x.value; });
    var a = { name: f.elements.name.value.trim(), slots: sl, note: f.elements.note.value.trim(), none: f.elements.none.checked };
    try { await DB.talkAnswerPut(E.row.id, k, a); } catch (e) { return toast(egHint(e)); }
    E.row.answers[k] = Object.assign({}, E.row.answers[k] || {}, a, { lp: true });
    closeOverlays(); toast('Gespeichert.'); E.render();
  };
  ACT.egEditDel = async function (el) {
    var k = el.dataset.k;
    try { await DB.talkAnswerPut(E.row.id, k, null); } catch (e) { return toast(egHint(e)); }
    delete E.row.answers[k]; closeOverlays(); toast('Eintrag gelöscht.'); E.render();
  };

  // ---------- Eltern (ohne Anmeldung, nur mit dem Link) ----------
  var EP = {
    start: async function (tok) {
      UI.view = 'eltern'; document.body.classList.add('lp');
      EP.tok = tok; EP.kid = null; EP.step = 'kids'; EP.err = '';
      EP.keys = LS.get('kn_eltern_' + tok) || {};
      app.innerHTML = '<p class="boot">Wird geladen …</p>';
      await EP.load(null);
      EP.render();
    },
    load: async function (kid) {
      try { EP.d = await DB.elternGet(EP.tok, kid, kid ? EP.keys[kid] : null); EP.err = ''; }
      catch (e) { EP.d = null; EP.err = errMsg(e); }
    }
  };
  EP.render = function () {
    document.body.classList.add('lp');
    var d = EP.d, out = egHead('für Eltern') + '<main class="main eg eg-eltern">';
    if (!d) {
      paint(out + '<div class="card stack"><h1 class="h1">Link nicht gültig</h1><p>' + h(EP.err || 'Dieser Link gilt nicht (mehr). Bitte fragen Sie die Lehrperson nach dem aktuellen Link.') + '</p></div></main>');
      return;
    }
    out += '<section class="banner eg-banner"><img class="banner-bild" src="' + h(klassBild(d.bild)) + '" alt="" width="132" height="132"><div class="stack" style="gap:6px;flex:1 1 260px">' +
      '<span class="kick">Klasse ' + h(d.class_name || '') + (d.teacher ? ' · ' + h(d.teacher) : '') + ' <span class="sterne" aria-hidden="true">✦ ✧ ✦</span></span>' +
      '<h1 class="h1">' + h(d.title || 'Elterngespräche') + '</h1>' + (d.info ? '<p class="eg-info">' + h(d.info) + '</p>' : '') + '</div></section>';
    if (!d.open) { paint(out + '<div class="card stack"><h2>Die Anmeldung ist geschlossen</h2><p>Zurzeit kann man sich nicht eintragen. Bei Fragen melden Sie sich bitte bei der Lehrperson.</p></div></main>'); return; }
    var kidName = {}; d.kids.forEach(function (k) { kidName[k.id] = k.name; });
    var byId = {}; d.slots.forEach(function (s) { byId[s.id] = s; });

    if (EP.step === 'kids') {
      // Pro Gerät nur ein Kind: Wer schon eingetragen hat, kann nur noch das eigene Kind öffnen.
      var own = d.kids.filter(function (k) { return EP.keys[k.id] && k.done; })[0];
      out += '<section class="card stack"><h2>Für welches Kind?</h2><p class="muted">' + (own ? 'Sie haben auf diesem Gerät schon für <b>' + h(own.name) + '</b> eingetragen. Tippen Sie darauf, um Ihre Angaben anzuschauen oder zu ändern.' : 'Tippen Sie auf den Namen Ihres Kindes. Sie können nur ein Kind eintragen.') + '</p><div class="eg-kidpick">' + d.kids.map(function (k) {
        var mine = !!EP.keys[k.id];
        if (k.done && !mine) return '<button class="eg-kidbtn done" disabled><b>' + h(k.name) + '</b><small>✓ schon eingetragen</small></button>';
        if (own && own.id !== k.id) return '<button class="eg-kidbtn done" disabled><b>' + h(k.name) + '</b><small>gesperrt</small></button>';
        return '<button class="eg-kidbtn' + (mine ? ' mine' : '') + '" data-a="epKid" data-k="' + k.id + '"><b>' + h(k.name) + '</b>' + (mine ? '<small>✓ eingetragen · ändern</small>' : '') + '</button>';
      }).join('') + '</div><p class="muted small">Steht bei Ihrem Kind schon «eingetragen», obwohl Sie noch nichts gewählt haben? Oder haben Sie zwei Kinder in dieser Klasse? Dann melden Sie sich bitte bei der Lehrperson.</p></section>';
      paint(out + '</main>'); return;
    }
    var mine = d.mine;
    if (EP.step === 'done' || (mine && mine.fixed)) {
      var fixedS = mine && mine.fixed && byId[mine.fixed];
      out += '<section class="card stack eg-done"><h2>' + (fixedS ? 'Ihr Termin steht fest' : 'Danke, Sie sind eingetragen!') + '</h2>';
      if (fixedS) out += '<p class="eg-big">' + h(egDay(fixedS.d, true)) + '<br><b>' + h(fixedS.t) + '–' + h(fixedS.e) + ' Uhr</b></p><p>Gespräch für ' + h(kidName[EP.kid] || '') + '. Bitte notieren Sie sich den Termin.</p>';
      else {
        var ch = egSort((mine && mine.slots || []).map(function (s) { return byId[s]; }).filter(Boolean));
        out += '<p>Für <b>' + h(kidName[EP.kid] || '') + '</b> haben Sie ' + (mine && mine.none ? 'angegeben, dass kein Termin passt. Die Lehrperson meldet sich bei Ihnen.' : plural(ch.length, 'möglichen Termin', 'mögliche Termine') + ' gewählt:') + '</p>' +
          (ch.length ? '<ul class="eg-chosen">' + ch.map(function (s) { return '<li>' + h(egLabel(s)) + '</li>'; }).join('') + '</ul>' : '') +
          '<p class="muted">' + h(d.teacher || 'Die Lehrperson') + ' plant die Gespräche und teilt Ihnen den genauen Termin mit. Wenn Sie diesen Link später auf diesem Gerät wieder öffnen, sehen Sie hier den festen Termin.</p>' +
          '<div class="row"><button class="btn" data-a="epChange">Angaben ändern</button></div>';
      }
      out += '<button class="btn" style="align-self:flex-start" data-a="epBack">Zurück zur Übersicht</button></section>';
      paint(out + '</main>'); return;
    }
    // Formular: welche Termine gehen?
    var fixedSet = {}; (d.fixed || []).forEach(function (s) { fixedSet[s] = 1; });
    var free = {}, order = {}; egSort(d.slots).forEach(function (s, i) { order[s.id] = i; if (!fixedSet[s.id]) free[s.id] = 1; });
    var fams = [], avail = {};
    (d.others || []).forEach(function (l, i) { if (!Array.isArray(l)) return; fams.push('o' + i); avail['o' + i] = l.filter(function (s) { return free[s]; }).sort(function (a, b) { return order[a] - order[b]; }); });
    var res = egReserved(fams, avail, free);
    var show = d.slots.filter(function (s) { return free[s.id] && (!res[s.id] || EP.sel.has(s.id)); });
    out += '<section class="card stack"><div class="row" style="justify-content:space-between"><h2>Termine für ' + h(kidName[EP.kid] || '') + '</h2><button class="btn sm" data-a="epBack">anderes Kind</button></div>' +
      '<p>Tippen Sie <b>alle</b> Termine an, an denen Sie können. Je mehr Sie wählen, desto besser lässt sich für alle planen.</p>';
    if (!show.length) out += '<div class="note">Leider sind alle Termine schon vergeben. Kreuzen Sie unten «Keiner dieser Termine passt» an und schreiben Sie eine kurze Bemerkung.</div>';
    out += egDays(show).map(function (day) {
      return '<div class="eg-pday"><h3>' + h(egDay(day.d, true)) + '</h3><div class="eg-slots">' + day.list.map(function (s) {
        var on = EP.sel.has(s.id);
        return '<button class="eg-slot" aria-pressed="' + on + '" data-a="epSlot" data-s="' + h(s.id) + '"><span class="eg-box">' + (on ? '✓' : '') + '</span>' + h(s.t) + '–' + h(s.e) + '</button>';
      }).join('') + '</div></div>';
    }).join('');
    out += '<p class="eg-count">' + (EP.sel.size ? '✓ ' + plural(EP.sel.size, 'Termin', 'Termine') + ' gewählt' : 'Noch kein Termin gewählt') + '</p>' +
      '<label class="eg-none"><input type="checkbox" data-change="epNone"' + (EP.none ? ' checked' : '') + '> Keiner dieser Termine passt</label>' +
      '<form class="stack" data-a="epSend"><div class="field"><label for="epName">Ihr Name</label><input class="input" id="epName" maxlength="80" autocomplete="name" required value="' + h(EP.name || '') + '" data-input="epName" placeholder="z. B. Sandra Muster"></div>' +
      '<div class="field"><label for="epNote">Bemerkung (freiwillig)</label><textarea class="input" id="epNote" rows="2" maxlength="500" data-input="epNote" placeholder="z. B. Wir bringen eine Übersetzerin mit.">' + h(EP.note || '') + '</textarea></div>' +
      (EP.err ? '<p class="err">' + h(EP.err) + '</p>' : '') +
      '<button class="btn primary eg-send"' + (EP.busy ? ' disabled' : '') + '>' + (mine ? 'Änderungen speichern' : 'Eintragen') + '</button></form></section>';
    paint(out + '</main>');
  };
  ACT.epKid = async function (el) {
    var own = Object.keys(EP.keys).filter(function (k) { return EP.d && EP.d.kids.some(function (x) { return x.id === k && x.done; }); })[0];
    if (own && own !== el.dataset.k) return toast('Auf diesem Gerät ist schon ein Kind eingetragen.');
    EP.kid = el.dataset.k; await EP.load(EP.kid);
    var m = EP.d && EP.d.mine;
    EP.sel = new Set(m ? m.slots || [] : []); EP.name = m ? m.name || '' : (EP.name || ''); EP.note = m ? m.note || '' : ''; EP.none = !!(m && m.none);
    EP.step = m ? 'done' : 'form'; EP.render(); window.scrollTo(0, 0);
  };
  ACT.epBack = async function () { EP.step = 'kids'; EP.kid = null; await EP.load(null); EP.render(); window.scrollTo(0, 0); };
  ACT.epChange = function () { EP.step = 'form'; EP.render(); };
  ACT.epSlot = function (el) { var s = el.dataset.s; if (EP.sel.has(s)) EP.sel.delete(s); else { EP.sel.add(s); EP.none = false; } EP.render(); };
  ACT.epNone = function (el) { EP.none = el.checked; if (EP.none) EP.sel.clear(); EP.render(); };
  ACT.epName = function (el) { EP.name = el.value; };
  ACT.epNote = function (el) { EP.note = el.value; };
  ACT.epSend = async function () {
    if (!String(EP.name || '').trim()) { EP.err = 'Bitte geben Sie Ihren Namen ein.'; return EP.render(); }
    if (!EP.sel.size && !EP.none) { EP.err = 'Bitte wählen Sie mindestens einen Termin oder «Keiner dieser Termine passt».'; return EP.render(); }
    var key = EP.keys[EP.kid] || egKey();
    EP.busy = true; EP.err = ''; EP.render();
    try {
      await DB.elternSet(EP.tok, EP.kid, key, { name: EP.name.trim(), slots: Array.from(EP.sel), note: (EP.note || '').trim(), none: !!EP.none });
      EP.keys[EP.kid] = key; LS.set('kn_eltern_' + EP.tok, EP.keys);
      await EP.load(EP.kid); EP.step = 'done';
    } catch (e) { EP.err = errMsg(e); }
    EP.busy = false; EP.render(); window.scrollTo(0, 0);
  };
  // Umfrage (ähnlich wie Mentimeter): Die Lehrperson stellt Fragen an der Wandtafel, die Kinder antworten am iPad.
  // Umfragen der Lehrperson (für alle Klassen): teacher_store «umfragen» = { list: [ { id, title, set, qs: [Frage] } ] }
  // Live-Stand pro Klasse: teacher_store «umfrage-<Klasse>» = { live: {...}, ans: { Frage-ID: { Kind-ID: Antwort } } }
  //   live (schreibt nur die Lehrperson, umfrage_put) = { on, sid, title, mode, cur, open, show, auto, kids, rev, hid, hidw, until, qs }
  //   Antworten schreiben die Kinder mit kid_umfrage_send, lesen mit kid_umfrage (ohne Namen, Lösung erst nach dem Aufdecken).
  // ===================================================================
  var UMF_TYPES = [
    ['wahl', 'Auswahl', '📊', 'Eine oder mehrere Antworten wählen'],
    ['quiz', 'Quizfrage', '🏆', 'Eine Antwort ist richtig, mit Auflösung'],
    ['stimmung', 'Stimmung', '😊', 'Gesichter, Ampel, Daumen oder Wetter'],
    ['wort', 'Wortwolke', '☁️', 'Kurze Wörter werden zur Wolke'],
    ['text', 'Offene Frage', '💬', 'Sätze und Ideen als Kärtchen'],
    ['skala', 'Skala', '🎚️', 'Aussagen von 1 bis 5 bewerten'],
    ['rang', 'Rangliste', '🥇', 'In die wichtigste Reihenfolge bringen'],
    ['punkte', 'Sterne verteilen', '⭐', 'Sterne auf die Ideen verteilen'],
    ['zahl', 'Schätzfrage', '🔢', 'Eine Zahl schätzen, mit Lösung'],
    ['feld', 'Punkt setzen', '🎯', 'Einen Punkt ins Feld setzen'],
    ['info', 'Infofolie', '📝', 'Nur Text, ohne Antwort']
  ];
  function umfType(t) { return UMF_TYPES.filter(function (x) { return x[0] === t; })[0] || UMF_TYPES[0]; }
  var UMF_COL = ['#5f97c8', '#e8a33d', '#7ea56a', '#d9736a', '#9b7fc4', '#4fb0a8', '#d6ad45', '#c77ca6'];
  var UMF_INK = ['#2f5f8f', '#a8650c', '#4a7536', '#a8443b', '#674c98', '#2a7a73', '#93701a', '#93456f'];
  var UMF_TINT = ['#fbf3dc', '#dcf0fd', '#e9f1e3', '#fcefed', '#efe7f8', '#e0f4f1'];
  var UMF_STIL = {
    gesichter: ['😄 Super', '🙂 Gut', '😐 Geht so', '🙁 Nicht so gut', '😢 Schlecht'],
    ampel: ['🟢 Alles klar', '🟡 Fast', '🔴 Noch nicht'],
    daumen: ['👍 Ja', '🤷 Weiss nicht', '👎 Nein'],
    wetter: ['☀️ Sonnig', '⛅ Wolkig', '🌧️ Regnerisch', '⛈️ Gewitter']
  };
  var UMF_STIL_NAME = { gesichter: 'Gesichter', ampel: 'Ampel', daumen: 'Daumen', wetter: 'Wetter' };
  function umfId(p) { return p + Date.now().toString(36).slice(-5) + Math.random().toString(36).slice(2, 6); }
  function umfNewQ(type) {
    var q = { id: umfId('q'), type: type, text: '' };
    if (type === 'wahl') { q.opts = ['', '', '']; q.multi = false; }
    else if (type === 'quiz') { q.opts = ['', '', '', '']; q.ok = [0]; q.multi = false; }
    else if (type === 'stimmung') { q.stil = 'gesichter'; q.opts = UMF_STIL.gesichter.slice(); q.text = 'Wie geht es dir heute?'; }
    else if (type === 'wort') q.max = 3;
    else if (type === 'text') q.max = 1;
    else if (type === 'skala') { q.opts = ['']; q.max = 5; q.lo = 'stimmt gar nicht'; q.hi = 'stimmt genau'; }
    else if (type === 'rang') q.opts = ['', '', ''];
    else if (type === 'punkte') { q.opts = ['', '', '']; q.pts = 10; }
    else if (type === 'zahl') { q.min = ''; q.max = ''; q.ok = ''; q.unit = ''; }
    else if (type === 'feld') q.ax = ['müde', 'wach', 'traurig', 'fröhlich']; // links, rechts, unten, oben
    else if (type === 'info') q.sub = '';
    return q;
  }
  function umfNum(v) { var s = String(v == null ? '' : v).trim().replace(/[’']/g, '').replace(',', '.'); return s !== '' && /^-?\d+(\.\d+)?$/.test(s) ? +s : null; }
  function umfFmtNum(x) { return x == null || !isFinite(x) ? '' : (Math.round(x * 100) / 100).toLocaleString('de-CH'); }
  function umfHasOk(q) { return q.type === 'quiz' ? Array.isArray(q.ok) && q.ok.length > 0 : q.type === 'zahl' ? umfNum(q.ok) !== null : false; }
  function umfSkMax(q) { return Math.min(10, Math.max(3, +q.max || 5)); }
  // Emoji vorne abtrennen («😄 Super» -> ['😄', 'Super'])
  function umfEmo(o) {
    var m = /^(\S+)\s*(.*)$/.exec(String(o || '').trim());
    try { if (m && /\p{Extended_Pictographic}/u.test(m[1])) return [m[1], m[2]]; } catch (e) {}
    return ['', String(o || '')];
  }
  // Für den Start: leere Antworten weglassen, nur bekannte Felder (Lösung bei Quiz entsprechend umrechnen)
  function umfClean(q) {
    var c = { id: q.id, type: q.type, text: String(q.text || '').trim().slice(0, 200) };
    if (q.opts) {
      var map = {}, o = [];
      q.opts.forEach(function (x, i) { x = String(x || '').trim().slice(0, 80); if (x) { map[i] = o.length; o.push(x); } });
      c.opts = o;
      if (q.type === 'quiz') c.ok = (q.ok || []).filter(function (i) { return map[i] != null; }).map(function (i) { return map[i]; });
    }
    if (q.type === 'wahl' || q.type === 'quiz') c.multi = !!q.multi;
    if (q.type === 'wort' || q.type === 'text') c.max = +q.max || 1;
    if (q.type === 'skala') { c.max = umfSkMax(q); c.lo = String(q.lo || '').slice(0, 40); c.hi = String(q.hi || '').slice(0, 40); }
    if (q.type === 'punkte') c.pts = Math.min(100, Math.max(1, +q.pts || 10));
    if (q.type === 'stimmung') c.stil = q.stil;
    if (q.type === 'zahl') { c.min = umfNum(q.min); c.max = umfNum(q.max); c.ok = umfNum(q.ok); c.unit = String(q.unit || '').slice(0, 20); }
    if (q.type === 'feld') c.ax = (q.ax || []).slice(0, 4).map(function (x) { return String(x || '').slice(0, 30); });
    if (q.type === 'info') c.sub = String(q.sub || '').slice(0, 600);
    return c;
  }
  function umfCheck(sv) {
    if (!sv.qs.length) return 'Bitte zuerst eine Frage hinzufügen.';
    for (var i = 0; i < sv.qs.length; i++) {
      var q = umfClean(sv.qs[i]), nr = 'Frage ' + (i + 1) + ': ';
      if (!q.text) return nr + 'Bitte die Frage eintippen.';
      if (q.opts && q.opts.length < (q.type === 'skala' ? 1 : 2)) return nr + (q.type === 'skala' ? 'Bitte mindestens eine Aussage eintippen.' : 'Bitte mindestens zwei Antworten eintippen.');
      if (q.type === 'quiz' && !q.ok.length) return nr + 'Bitte die richtige Antwort mit ✓ markieren.';
      if (q.type === 'zahl' && q.min != null && q.max != null && q.min >= q.max) return nr + 'Die kleinste Zahl muss kleiner als die grösste sein.';
    }
    return '';
  }
  // Antwort als Text (Tabelle und Kinderansicht)
  function umfFmt(q, v) {
    if (v == null) return '';
    var o = q.opts || [];
    switch (q.type) {
      case 'wahl': case 'quiz': case 'stimmung': return (v || []).map(function (i) { return o[i]; }).join(', ');
      case 'wort': case 'text': return (v || []).join(' / ');
      case 'skala': return (v || []).map(function (x, i) { return (o.length > 1 ? o[i] + ': ' : '') + x; }).join(', ');
      case 'rang': return (v || []).map(function (i, p) { return (p + 1) + '. ' + o[i]; }).join(', ');
      case 'punkte': return (v || []).map(function (x, i) { return x ? o[i] + ': ' + x : ''; }).filter(Boolean).join(', ');
      case 'zahl': return umfFmtNum(+v) + (q.unit ? ' ' + q.unit : '');
      case 'feld': return Math.round(v.x) + ' / ' + Math.round(v.y);
    }
    return '';
  }
  function umfQuizOk(q, v) { if (!Array.isArray(v) || !Array.isArray(q.ok)) return false; return v.slice().sort().join(',') === q.ok.slice().sort().join(','); }

  // Ergebnisse einer Frage zeichnen. E = [{ v: Antwort, k: Kind-ID, n: Name }] (Kinder bekommen nur v)
  // o = { rev: Lösung zeigen, names: Namen zeigen, mod: Lehrperson darf ausblenden, small: schmale Ansicht, hidw: ausgeblendete Wörter }
  function umfRes(q, E, o) {
    o = o || {}; var t = q.type, opts = q.opts || [], n = opts.length, N = E.length;
    if (t === 'info') return '';
    if (!N) return '<div class="ur-leer">Noch keine Antworten</div>';
    var col = function (i) { return UMF_COL[i % UMF_COL.length]; };
    var label = function (x) { var e = umfEmo(x); return e[0] ? '<span class="ur-emo">' + e[0] + '</span><span>' + h(e[1]) + '</span>' : '<span>' + h(x) + '</span>'; };
    if (t === 'wahl' || t === 'quiz' || t === 'stimmung') {
      var cnt = opts.map(function () { return 0; }), who = opts.map(function () { return []; });
      E.forEach(function (e) { (e.v || []).forEach(function (i) { if (cnt[i] != null) { cnt[i]++; if (e.n) who[i].push(e.n); } }); });
      var mx = Math.max.apply(null, cnt.concat([1])), okA = o.rev && Array.isArray(q.ok) ? q.ok : null;
      var cls = function (i) { return okA ? (okA.indexOf(i) >= 0 ? ' ok' : ' no') : ''; };
      var pc = function (i) { return Math.round(cnt[i] / N * 100) + '%'; };
      if (o.small || n > 6) return '<div class="ur-hbars">' + opts.map(function (x, i) {
        return '<div class="ur-h' + cls(i) + '"><span class="ur-l">' + (okA && okA.indexOf(i) >= 0 ? '✓ ' : '') + label(x) + '</span><span class="ur-t"><i style="width:' + Math.max(cnt[i] ? 3 : 0, Math.round(cnt[i] / mx * 100)) + '%;background:' + col(i) + '"></i></span><b>' + cnt[i] + '</b>' +
          (o.names && who[i].length ? '<small class="ur-who">' + h(who[i].join(', ')) + '</small>' : '') + '</div>'; }).join('') + '</div>';
      return '<div class="ur-cols" style="--n:' + n + '">' + opts.map(function (x, i) {
        return '<div class="ur-col' + cls(i) + '"><b class="ur-c">' + cnt[i] + '<small>' + pc(i) + '</small></b><span class="ur-box"><span class="ur-bar" style="height:' + Math.max(cnt[i] ? 2 : 0, Math.round(cnt[i] / mx * 100)) + '%;background:' + col(i) + '"></span></span>' +
          '<span class="ur-l' + (t === 'stimmung' ? ' emo' : '') + '">' + (okA && okA.indexOf(i) >= 0 ? '<span class="ur-ok">✓</span>' : '') + label(x) + '</span>' +
          (o.names && who[i].length ? '<small class="ur-who">' + h(who[i].join(', ')) + '</small>' : '') + '</div>'; }).join('') + '</div>';
    }
    if (t === 'wort') {
      var f = {}, show = {}, hw = o.hidw || [];
      E.forEach(function (e) { (e.v || []).forEach(function (w) { w = String(w).trim(); var k = w.toLowerCase(); if (!k || hw.indexOf(k) >= 0) return; f[k] = (f[k] || 0) + 1; if (!show[k]) show[k] = w; }); });
      var keys = Object.keys(f).sort(function (a, b) { return f[b] - f[a] || a.localeCompare(b); }); if (!keys.length) return '<div class="ur-leer">Noch keine Wörter</div>';
      var top = f[keys[0]], arr = []; keys.forEach(function (k, i) { if (i % 2) arr.push(k); else arr.unshift(k); });
      return '<div class="ur-cloud' + (o.small ? ' sm' : '') + '">' + arr.map(function (k) {
        var s = o.small ? 15 + 22 * Math.pow(f[k] / top, .8) : 22 + 64 * Math.pow(f[k] / top, .8), r = (hash(k) % 3 - 1) * 3;
        return '<span class="ur-w" style="font-size:' + Math.round(s) + 'px;color:' + UMF_INK[hash(k) % UMF_INK.length] + ';transform:rotate(' + r + 'deg)"' + (o.mod ? ' data-a="uHideW" data-w="' + h(k) + '" title="Wort ausblenden"' : '') + '>' + h(show[k]) + (f[k] > 1 ? '<sup>' + f[k] + '</sup>' : '') + '</span>';
      }).join('') + '</div>';
    }
    if (t === 'text') {
      var cards = []; E.forEach(function (e) { (e.v || []).forEach(function (s) { cards.push({ s: s, k: e.k, n: e.n }); }); });
      return '<div class="ur-cards' + (o.small ? ' sm' : '') + '">' + cards.map(function (c, i) {
        return '<div class="ur-card" style="background:' + UMF_TINT[(c.k ? hash(c.k) : i) % UMF_TINT.length] + '"><p>' + h(c.s) + '</p>' + (o.names && c.n ? '<small>' + h(c.n) + '</small>' : '') +
          (o.mod && c.k ? '<button class="ur-x" data-a="uHide" data-k="' + h(c.k) + '" title="Ausblenden" aria-label="Antwort ausblenden">✕</button>' : '') + '</div>'; }).join('') + '</div>';
    }
    if (t === 'skala') {
      var m = umfSkMax(q);
      return '<div class="ur-skala' + (o.small ? ' sm' : '') + '"><div class="ur-skends"><span></span><span>1 = ' + h(q.lo || '') + '</span><span>' + m + ' = ' + h(q.hi || '') + '</span></div>' + opts.map(function (st, i) {
        var c = []; for (var j = 0; j < m; j++) c.push(0); var s = 0, z = 0;
        E.forEach(function (e) { var x = (e.v || [])[i]; if (x >= 1 && x <= m) { c[x - 1]++; s += x; z++; } });
        var cm = Math.max.apply(null, c.concat([1])), avg = z ? s / z : 0;
        return '<div class="ur-sk"><span class="ur-l">' + h(st) + '</span><div class="ur-skbar" style="--m:' + m + '">' + c.map(function (v, j) {
          return '<span class="ur-skc"><i style="height:' + Math.round(v / cm * 100) + '%;background:' + col(i) + '"></i><small>' + (j + 1) + '</small></span>'; }).join('') +
          (z ? '<span class="ur-avg" style="left:' + ((avg - .5) / m * 100) + '%"><b>Ø ' + avg.toFixed(1).replace('.', ',') + '</b></span>' : '') + '</div></div>';
      }).join('') + '</div>';
    }
    if (t === 'rang' || t === 'punkte') {
      var sc = opts.map(function () { return 0; }), tot = 0;
      E.forEach(function (e) { (e.v || []).forEach(function (x, p) { if (t === 'rang') { if (sc[x] != null) sc[x] += n - p; } else if (sc[p] != null) { sc[p] += +x || 0; } }); });
      sc.forEach(function (x) { tot = Math.max(tot, x); });
      var ord = opts.map(function (x, i) { return i; }).sort(function (a, b) { return sc[b] - sc[a] || a - b; });
      return '<ol class="ur-rang' + (o.small ? ' sm' : '') + '">' + ord.map(function (i, p) {
        var side = t === 'rang' ? 'Ø Platz ' + (n - sc[i] / N + 1).toFixed(1).replace('.', ',') : sc[i] + ' ⭐';
        return '<li><span class="ur-p">' + (p < 3 ? medal(p + 1) : (p + 1) + '.') + '</span><span class="ur-l">' + h(opts[i]) + '</span><span class="ur-t"><i style="width:' + Math.round(sc[i] / Math.max(1, tot) * 100) + '%;background:' + col(i) + '"></i></span><b>' + side + '</b></li>';
      }).join('') + '</ol>';
    }
    if (t === 'zahl') {
      var xs = E.map(function (e) { return { x: +e.v, n: e.n }; }).filter(function (e) { return isFinite(e.x); }).sort(function (a, b) { return a.x - b.x; });
      if (!xs.length) return '<div class="ur-leer">Noch keine Antworten</div>';
      var okv = o.rev ? umfNum(q.ok) : null, lo = xs[0].x, hi = xs[xs.length - 1].x;
      if (okv !== null) { lo = Math.min(lo, okv); hi = Math.max(hi, okv); }
      if (lo === hi) { lo -= 1; hi += 1; }
      var B = o.small ? 12 : 20, bins = []; for (var b = 0; b < B; b++) bins.push(0);
      xs.forEach(function (e) { bins[Math.min(B - 1, Math.floor((e.x - lo) / (hi - lo) * B))]++; });
      var bm = Math.max.apply(null, bins), sum = 0; xs.forEach(function (e) { sum += e.x; });
      var med = xs.length % 2 ? xs[(xs.length - 1) / 2].x : (xs[xs.length / 2 - 1].x + xs[xs.length / 2].x) / 2, u = q.unit ? ' ' + h(q.unit) : '';
      var near = okv !== null && o.names ? xs.filter(function (e) { return e.n; }).slice().sort(function (a, b) { return Math.abs(a.x - okv) - Math.abs(b.x - okv); }).slice(0, 3) : [];
      return '<div class="ur-zahl' + (o.small ? ' sm' : '') + '"><div class="ur-zl">' + bins.map(function (c, j) {
        return c ? '<span class="ur-zb" style="left:' + (j / B * 100) + '%;width:' + (100 / B) + '%"><i style="height:' + Math.round(c / bm * 100) + '%"></i><b>' + c + '</b></span>' : ''; }).join('') +
        (okv !== null ? '<span class="ur-zok" style="left:' + ((okv - lo) / (hi - lo) * 100) + '%"><b>Lösung: ' + umfFmtNum(okv) + u + '</b></span>' : '') + '</div>' +
        '<div class="ur-zax"><span>' + umfFmtNum(lo) + '</span><span>' + umfFmtNum(hi) + '</span></div>' +
        '<div class="ur-stats"><span>Durchschnitt <b>' + umfFmtNum(sum / xs.length) + u + '</b></span><span>Mitte <b>' + umfFmtNum(med) + u + '</b></span><span>Kleinste <b>' + umfFmtNum(xs[0].x) + '</b></span><span>Grösste <b>' + umfFmtNum(xs[xs.length - 1].x) + '</b></span></div>' +
        (near.length ? '<p class="ur-near">Am nächsten dran: ' + near.map(function (e) { return '<b>' + h(e.n) + '</b> (' + umfFmtNum(e.x) + ')'; }).join(', ') + '</p>' : '') + '</div>';
    }
    if (t === 'feld') {
      var ax = q.ax || [], ux = 0, uy = 0;
      E.forEach(function (e) { ux += +e.v.x || 0; uy += +e.v.y || 0; });
      return umfFeld(ax, E.map(function (e, i) { return '<span class="ur-dot" style="left:' + e.v.x + '%;top:' + (100 - e.v.y) + '%;background:' + (e.n ? kidColor(e.n) : UMF_COL[i % UMF_COL.length]) + '">' + (o.names && e.n ? h(e.n.charAt(0)) : '') + '</span>'; }).join('') +
        '<span class="ur-mitte" style="left:' + (ux / N) + '%;top:' + (100 - uy / N) + '%" title="Mitte der Klasse">✦</span>', o.small);
    }
    return '';
  }
  function umfFeld(ax, inner, small, act) {
    return '<div class="ur-feld' + (small ? ' sm' : '') + '"><span class="ur-ax o">' + h(ax[3] || '') + ' ↑</span><span class="ur-ax l">← ' + h(ax[0] || '') + '</span>' +
      '<div class="ur-fq"' + (act ? ' data-a="' + act + '"' : '') + '><i></i><i></i><i></i><i></i>' + inner + '</div><span class="ur-ax r">' + h(ax[1] || '') + ' →</span><span class="ur-ax u">↓ ' + h(ax[2] || '') + '</span></div>';
  }
  // Quiz-Rangliste: richtige Quizantworten pro Kind
  function umfRank(qs, ans, kids) {
    var quiz = qs.filter(function (q) { return q.type === 'quiz' && (q.ok || []).length; }), pts = {}, seen = {};
    quiz.forEach(function (q) { var a = ans[q.id] || {}; Object.keys(a).forEach(function (id) { seen[id] = 1; pts[id] = (pts[id] || 0) + (umfQuizOk(q, a[id]) ? 1 : 0); }); });
    return { n: quiz.length, list: kids.filter(function (k) { return seen[k.id]; }).map(function (k) { return { name: k.name, p: pts[k.id] || 0 }; }).sort(function (a, b) { return b.p - a.p || a.name.localeCompare(b.name); }) };
  }

  // Vorlagen (eigene Kopie beim Übernehmen)
  function umfQ(type, text, x) { var q = umfNewQ(type); q.text = text; if (x) Object.keys(x).forEach(function (k) { q[k] = x[k]; }); return q; }
  var UMF_VORLAGEN = [
    ['🌈', 'Wie war die Woche?', 'Wochenrückblick am Freitag', function () { return [
      umfQ('stimmung', 'Wie war deine Woche?'),
      umfQ('wort', 'Ein Wort für diese Woche', { max: 1 }),
      umfQ('wahl', 'Was hat dir am besten gefallen?', { opts: ['Mathe', 'Deutsch', 'NMG', 'Sport', 'Gestalten', 'Pause'], multi: true }),
      umfQ('text', 'Das wünsche ich mir für nächste Woche')]; }],
    ['🚦', 'Verstanden?', 'Kurze Lernkontrolle nach einer Lektion', function () { return [
      umfQ('stimmung', 'Wie gut hast du es verstanden?', { stil: 'ampel', opts: UMF_STIL.ampel.slice() }),
      umfQ('skala', 'Wie sicher bist du?', { opts: ['Ich kann es erklären.', 'Ich kann es allein lösen.'] }),
      umfQ('text', 'Das ist mir noch unklar')]; }],
    ['🇨🇭', 'Quiz: Schweiz', 'Vier Fragen mit Auflösung und Rangliste', function () { return [
      umfQ('quiz', 'Wie heisst die Bundesstadt der Schweiz?', { opts: ['Zürich', 'Bern', 'Genf', 'Basel'], ok: [1] }),
      umfQ('zahl', 'Wie viele Kantone hat die Schweiz? Schätze!', { min: '0', max: '100', ok: '26' }),
      umfQ('quiz', 'Welche Sprache ist eine Landessprache?', { opts: ['Englisch', 'Spanisch', 'Rätoromanisch', 'Holländisch'], ok: [2] }),
      umfQ('quiz', 'Wie heisst der höchste Berg der Schweiz?', { opts: ['Matterhorn', 'Eiger', 'Dufourspitze', 'Säntis'], ok: [2] })]; }],
    ['🗣️', 'Klassenrat', 'Anliegen sammeln und gewichten', function () { return [
      umfQ('info', 'Klassenrat', { sub: 'Heute sammeln wir eure Anliegen. Jede Stimme zählt!' }),
      umfQ('text', 'Was möchtest du im Klassenrat besprechen?', { max: 2 }),
      umfQ('punkte', 'Was ist dir am wichtigsten? Verteile deine Sterne.', { opts: ['Pausenplatz', 'Ämtli', 'Lautstärke', 'Klassenausflug'] })]; }],
    ['🎒', 'Ausflug planen', 'Gemeinsam entscheiden', function () { return [
      umfQ('wahl', 'Wohin soll der Ausflug gehen?', { opts: ['Zoo', 'Wald', 'Museum', 'See'] }),
      umfQ('rang', 'Was ist beim Ausflug am wichtigsten?', { opts: ['Spielen', 'Feuer und Bräteln', 'Tiere sehen', 'Wandern'] }),
      umfQ('wort', 'Was darf im Rucksack nicht fehlen?')]; }],
    ['☀️', 'Morgen-Check', 'Wie fühlt ihr euch am Morgen?', function () { return [
      umfQ('feld', 'Wie fühlst du dich gerade?'),
      umfQ('stimmung', 'Wie hast du geschlafen?', { stil: 'wetter', opts: UMF_STIL.wetter.slice() })]; }]
  ];

  var U = { list: [], view: 'list', eid: null, qi: 0, doc: null, add: false, names: null, fehlt: false, rank: false, more: false };
  U.start = async function (cid) {
    UI.view = 'umfrage';
    var s = await DB.session(); if (!s) { location.hash = '#/'; return; }
    if (!(await toolGate('umfrage', 'Die Umfrage'))) return;
    document.body.classList.add('lp');
    app.innerHTML = '<p class="boot">Umfrage wird geladen …</p>';
    try {
      var r = await Promise.all([DB.listClasses(), DB.listKids(cid), DB.storeGet('umfragen'), DB.storeGet('umfrage-' + cid),
        DB.storeGet('umfrage-vorlagen').catch(function () { return null; }), DB.sharedGet('umfrage-vorlagen').catch(function () { return null; }), DB.me().catch(function () { return null; })]);
      U.tv = r[4] && typeof r[4] === 'object' ? r[4] : {}; U.tv.eigene = Array.isArray(U.tv.eigene) ? U.tv.eigene : []; U.tv.weg = Array.isArray(U.tv.weg) ? U.tv.weg : [];
      U.tshared = r[5] && Array.isArray(r[5].list) ? r[5].list : []; U.admin = !!(r[6] && r[6].is_admin); U.tvWeg = false;
      U.cls = r[0].filter(function (c) { return c.id === cid; })[0]; U.ckids = (r[1] || []).slice().sort(kidSort);
      U.list = r[2] && Array.isArray(r[2].list) ? r[2].list : [];
      U.docs = { klasse: r[3] && typeof r[3] === 'object' ? r[3] : { live: null, ans: {} }, offen: null };
      U.docs.klasse.ans = U.docs.klasse.ans || {};
    } catch (e) { U.cls = null; }
    // Version 27: offene Runde (QR-Code) der Lehrperson; ohne neues SQL einfach keine
    try { U.docs && (U.docs.offen = umfOffenDoc(await DB.umfOffenHost(null))); } catch (e) {}
    if (!U.cls) { paint('<div class="main"><div class="card stack"><h2>Umfrage nicht verfügbar</h2><p>Diese Klasse wurde nicht gefunden.</p><a class="btn" href="#/">Zum Portal</a></div></div>'); return; }
    U.cid = cid; U.add = false; U.fehlt = false; U.rank = false; U.more = false; U.off = 0;
    U.use(U.docs.offen && U.docs.offen.live && U.docs.offen.live.on ? 'offen' : 'klasse');
    var l = U.doc.live; U.view = l && l.on ? 'show' : 'list';
    U.names = l && l.on ? U.namesDefault(l.sid) : null;
    U.render();
    every(1500, function () { if (!document.hidden && (U.view === 'show' || U.view === 'res')) U.poll(); });
    every(500, U.tick);
  };
  // Zwei Orte für den Live-Stand: «klasse» (Kinder der Klasse) und «offen» (Gäste per QR-Code, umf_runden)
  function umfOffenDoc(r) { return r ? { id: r.id, nr: r.nr, live: (r.data && r.data.live) || null, ans: (r.data && r.data.ans) || {}, gaeste: r.gaeste || [] } : null; }
  function umfGastUrl(nr) { return location.origin + location.pathname + '#/u' + (nr ? '/' + nr : ''); }
  function umfNr(nr) { return String(nr || '').replace(/^(\d{3})(\d{3})$/, '$1 $2'); }
  U.use = function (src) {
    U.src = src === 'offen' && U.docs.offen ? 'offen' : 'klasse'; U.doc = U.docs[U.src];
    U.kids = U.src === 'offen' ? U.doc.gaeste.map(function (g) { return { id: g.id, name: g.name }; }) : U.ckids;
  };
  U.find = function (id) { return U.list.filter(function (x) { return x.id === id; })[0] || null; };
  U.namesDefault = function (sid) { var sv = U.find(sid); return !!(sv && sv.set && sv.set.anon === false); };
  U.saveSoon = function () { clearTimeout(U.st); U.st = setTimeout(U.save, 700); var m = document.getElementById('ueSaved'); if (m) m.textContent = 'Wird gespeichert …'; };
  U.save = function () {
    clearTimeout(U.st); U.st = null;
    return DB.storeSet('umfragen', { list: U.list }).then(function () { var m = document.getElementById('ueSaved'); if (m) m.textContent = '✓ Gespeichert'; })
      .catch(function (e) { toast('Nicht gespeichert: ' + errMsg(e)); });
  };
  window.addEventListener('pagehide', function () { if (U.st) U.save(); });
  U.poll = async function () {
    if (U.busy) return; U.busy = true;
    try {
      if (U.src === 'offen') {
        var o = umfOffenDoc(await DB.umfOffenHost(U.doc.id));
        if (o && o.id === U.doc.id && (JSON.stringify(o.ans) !== JSON.stringify(U.doc.ans) || o.gaeste.length !== U.doc.gaeste.length)) { U.doc.ans = o.ans; U.doc.gaeste = o.gaeste; U.use('offen'); if (UI.view === 'umfrage') U.render(); }
      } else { var d = await DB.storeGet('umfrage-' + U.cid), a = (d && d.ans) || {}; if (JSON.stringify(a) !== JSON.stringify(U.doc.ans)) { U.doc.ans = a; if (UI.view === 'umfrage') U.render(); } }
    } catch (e) {}
    U.busy = false;
  };
  function umfSec(s) { s = Math.max(0, s); return Math.floor(s / 60) + ':' + ('0' + (s % 60)).slice(-2); }
  U.left = function () { var l = U.doc && U.doc.live; return l && l.until ? Math.ceil((l.until - (Date.now() + U.off)) / 1000) : null; };
  U.tick = function () {
    var l = U.doc && U.doc.live; if (UI.view !== 'umfrage' || U.view !== 'show' || !l || !l.until) return;
    var left = U.left(), el = document.getElementById('umfTimer');
    if (left <= 0 && !U.closing) { U.closing = true; toast('Die Zeit ist um.'); U.setLive({ open: false, until: null, show: true }).catch(function (e) { toast(errMsg(e)); }).then(function () { U.closing = false; }); return; }
    if (el) el.textContent = umfSec(left);
  };
  // Live-Stand ändern (nur die Lehrperson schreibt ihn). sec = Timer starten, clear = Antworten dieser Fragen löschen
  U.setLive = async function (patch, clear, sec, replace) {
    var l = replace ? patch : Object.assign({}, U.doc.live || {}, patch); U.doc.live = l;
    (clear || []).forEach(function (q) { if (q === '*') U.doc.ans = {}; else delete U.doc.ans[q]; });
    var send = JSON.parse(JSON.stringify(l)); if (sec != null) send.sec = sec;
    U.render();
    var r = U.src === 'offen' ? await DB.umfOffenPut(U.doc.id, send, clear || null) : await DB.umfragePut(U.cid, send, clear || null);
    if (r && r.now) { U.off = r.now - Date.now(); if (sec != null) { U.doc.live.until = r.until || null; U.render(); } }
  };
  U.render = function () {
    if (UI.view !== 'umfrage') return;
    document.body.classList.add('lp');
    var l = U.doc.live;
    if (U.view === 'show' && !(l && l.on)) U.view = 'list';
    if (U.view === 'edit' && !U.find(U.eid)) U.view = 'list';
    paint(U.view === 'show' ? U.viewShow() : U.view === 'edit' ? U.viewEdit() : U.view === 'res' ? U.viewRes() : U.viewList());
    if (U.view === 'show') { U.tick(); U.qrMini(); }
  };
  // QR-Code der offenen Runde (einmal erzeugen, dann merken)
  U.qr = function () {
    var o = U.docs.offen; if (!o) return Promise.reject(new Error('keine Runde'));
    if (U.qrFor !== o.nr) { U.qrFor = o.nr; U.qrSvg = qrSvg(umfGastUrl(o.nr)); }
    return U.qrSvg;
  };
  U.qrMini = function () { var b = document.getElementById('usQr'); if (b && U.src === 'offen') U.qr().then(function (svg) { var x = document.getElementById('usQr'); if (x) x.innerHTML = svg; }).catch(function () {}); };
  ACT.uQr = function () {
    var o = U.docs.offen; if (!o) return;
    var ov = overlay('<div class="bigcode umf-qrbig"><p>Mitmachen ohne Login: QR-Code scannen oder <span style="color:#1f2421">' + h(shortUrl(umfGastUrl())) + '</span> öffnen und die Nummer eingeben</p>' +
      '<div class="bigcode-row"><div class="qrbox" id="uQrBig" role="img" aria-label="QR-Code zum Mitmachen">QR-Code wird geladen …</div><b>' + h(umfNr(o.nr)) + '</b></div>' +
      '<button class="btn" style="align-self:center" data-a="closeOverlay">Schliessen</button></div>');
    U.qr().then(function (svg) { var b = ov.querySelector('#uQrBig'); if (b) b.innerHTML = svg; })
      .catch(function () { var b = ov.querySelector('#uQrBig'); if (b) b.textContent = 'QR-Code nicht verfügbar. Bitte die Adresse eintippen.'; });
  };
  U.top = function (left, right) {
    return '<div class="umf-top"><div class="row">' + left + '</div><span class="umf-kick"><img src="' + h(klassBild(U.cls.bild)) + '" alt="" width="40" height="40">Umfrage · Klasse ' + h(U.cls.name) + ' <span class="sterne" aria-hidden="true">✦ ✧ ✦</span></span><div class="row">' + (right || '') + '</div></div>';
  };
  U.answers = function (sv, src) { var d = U.docs[src || 'klasse'], n = 0; if (!d) return 0; sv.qs.forEach(function (q) { n = Math.max(n, Object.keys(d.ans[q.id] || {}).length); }); return n; };

  // ---------- Liste der Umfragen ----------
  U.viewList = function () {
    var out = '<div class="umf-page">' + U.top(backBtn('href="#/"')) +
      '<section class="umf-hero card"><img class="umf-hero-bild" src="bilder/kacheln/umfrage-kiste.webp" alt="" width="110" height="110"><div class="stack" style="gap:8px;flex:1 1 320px"><h1>Umfragen</h1>' +
      '<p>Stellen Sie der Klasse Fragen: Abstimmungen, Wortwolken, Quiz, Schätzfragen und mehr. Die Kinder antworten am iPad, die Ergebnisse erscheinen live an der Wandtafel.</p>' +
      '<p class="muted small">Ihre Umfragen gelten für alle Ihre Klassen. Die Antworten werden pro Klasse gespeichert.</p></div>' +
      '<button class="btn primary big" data-a="uNew">+ Neue Umfrage</button></section>';
    ['klasse', 'offen'].forEach(function (src) { var d = U.docs[src], l = d && d.live;
      if (l && l.on) out += '<div class="note row" style="justify-content:space-between"><span>✦ Gerade läuft' + (src === 'offen' ? ' (offen per QR-Code, Nummer ' + h(umfNr(d.nr)) + ')' : ' in der Klasse') + ': <b>' + h(l.title || 'Umfrage') + '</b></span><button class="btn sm primary" data-a="uToShow" data-s="' + src + '">Zur Anzeige</button></div>'; });
    out += '<section class="stack"><h2>Meine Umfragen</h2>' + (U.list.length ? '<div class="umf-grid">' + U.list.map(function (sv) {
      var a = U.answers(sv), ao = U.docs.offen && U.docs.offen.live && U.docs.offen.live.sid === sv.id ? U.answers(sv, 'offen') : 0, del = UI.confirm === 'uDel' + sv.id;
      return '<div class="umf-card card"><button class="umf-card-open" data-a="uEdit" data-id="' + sv.id + '"><b>' + h(sv.title || 'Ohne Titel') + '</b><span class="umf-icons">' + sv.qs.map(function (q) { return '<span title="' + h(umfType(q.type)[1]) + '">' + umfType(q.type)[2] + '</span>'; }).join('') + '</span>' +
        '<small>' + plural(sv.qs.length, 'Frage', 'Fragen') + ' · ' + (sv.set && sv.set.mode === 'selbst' ? 'Selbsttempo' : 'Live') + (a ? ' · ' + plural(a, 'Kind hat', 'Kinder haben') + ' geantwortet' : '') + (ao ? ' · offen: ' + plural(ao, 'Antwort', 'Antworten') : '') + '</small></button>' +
        '<div class="row umf-card-btns"><button class="btn sm primary" data-a="uStart" data-id="' + sv.id + '">▶ Starten</button><button class="btn sm" data-a="uEdit" data-id="' + sv.id + '">✎ Bearbeiten</button>' +
        (a || ao ? '<button class="btn sm" data-a="uRes" data-id="' + sv.id + '" data-s="' + (a ? 'klasse' : 'offen') + '">📊 Ergebnisse</button>' : '') +
        '<button class="btn sm icon" data-a="uCopy" data-id="' + sv.id + '" title="Kopieren" aria-label="Kopieren">⧉</button>' +
        '<button class="btn sm" data-a="uAsTpl" data-id="' + sv.id + '" title="Als Vorlage speichern">⭐ Als Vorlage</button>' +
        '<button class="btn sm danger' + (del ? ' armed' : '') + '" data-a="uDel" data-id="' + sv.id + '">' + (del ? 'Wirklich löschen?' : '🗑') + '</button></div></div>';
    }).join('') + '</div>' : '<div class="empty">Noch keine Umfrage. Beginnen Sie mit «+ Neue Umfrage» oder übernehmen Sie eine Vorlage.</div>') + '</section>';
    var all = umfTpls(), shown = all.filter(function (t) { return U.tv.weg.indexOf(t.id) < 0; }), weg = all.filter(function (t) { return U.tv.weg.indexOf(t.id) >= 0; });
    var sharedIds = U.tshared.map(function (t) { return t.id; });
    out += '<section class="stack"><h2>Vorlagen</h2><div class="umf-grid tpl">' + shown.map(function (t) {
      var badge = t.src === 'e' ? (sharedIds.indexOf(t.id) >= 0 ? '🌍 Meine · für alle freigegeben' : '⭐ Meine Vorlage') : t.src === 's' ? '🌍 Für alle' : '';
      var delKey = 'uTplDel' + t.id;
      return '<div class="umf-tpl"><button class="umf-tpl-open" data-a="uTpl" data-id="' + h(t.id) + '"><span class="umf-tpl-emo">' + h(t.emo) + '</span><span><b>' + h(t.title) + '</b>' + (t.desc ? '<small>' + h(t.desc) + '</small>' : '') +
        '<span class="umf-icons">' + t.qs().map(function (q) { return umfType(q.type)[2]; }).join('') + '</span>' + (badge ? '<span class="umf-tpl-badge">' + badge + '</span>' : '') + '</span></button>' +
        '<span class="umf-tpl-acts">' + (U.admin && t.src === 'e' ? '<button class="btn sm" data-a="uTplShare" data-id="' + h(t.id) + '">' + (sharedIds.indexOf(t.id) >= 0 ? 'Freigabe zurücknehmen' : '🌍 Für alle freigeben') + '</button>' : '') +
        '<button class="btn sm icon danger' + (UI.confirm === delKey ? ' armed' : '') + '" data-a="uTplDel" data-id="' + h(t.id) + '" title="Vorlage löschen" aria-label="Vorlage löschen">' + (UI.confirm === delKey ? '?' : '🗑') + '</button></span></div>';
    }).join('') + (shown.length ? '' : '<div class="empty">Alle Vorlagen sind gelöscht. Unten können Sie sie wieder einfügen.</div>') + '</div>' +
    (weg.length ? '<div class="umf-weg card"><button class="umf-weg-head" data-a="uTplWeg" aria-expanded="' + !!U.tvWeg + '">🗑 Gelöschte Vorlagen (' + weg.length + ') <span>' + (U.tvWeg ? '▲' : '▼') + '</span></button>' +
      (U.tvWeg ? '<div class="stack" style="gap:8px">' + weg.map(function (t) {
        return '<div class="row umf-weg-row"><span class="umf-tpl-emo sm">' + h(t.emo) + '</span><span class="grow">' + h(t.title) + (t.src === 'e' ? ' <small class="muted">(meine)</small>' : '') + '</span>' +
          '<button class="btn sm" data-a="uTplBack" data-id="' + h(t.id) + '">↺ Wieder einfügen</button>' +
          (t.src === 'e' ? '<button class="btn sm danger' + (UI.confirm === 'uTplGone' + t.id ? ' armed' : '') + '" data-a="uTplGone" data-id="' + h(t.id) + '">' + (UI.confirm === 'uTplGone' + t.id ? 'Wirklich für immer löschen?' : 'Endgültig löschen') + '</button>' : '') + '</div>';
      }).join('') + '</div>' : '') + '</div>' : '') + '</section></div>';
    return out;
  };
  U.blank = function (title, qs) { return { id: umfId('u'), title: title || '', at: Date.now(), set: { mode: 'live', auto: 'live', kids: true, anon: true }, qs: qs || [] }; };
  ACT.uNew = function () { var sv = U.blank('', []); U.list.unshift(sv); U.eid = sv.id; U.qi = 0; U.add = true; U.view = 'edit'; U.save(); U.render(); var t = document.getElementById('ueTitle'); if (t) t.focus(); };
  // Vorlagen: eingebaute (UMF_VORLAGEN), für alle freigegebene (shared_store «umfrage-vorlagen», nur Admin schreibt)
  // und eigene (teacher_store «umfrage-vorlagen» = { eigene: [Vorlage], weg: [gelöschte Vorlagen-IDs] })
  function umfTpls() {
    var copy = function (qs) { return function () { return JSON.parse(JSON.stringify(qs || [])).map(function (q) { q.id = umfId('q'); return q; }); }; };
    var out = UMF_VORLAGEN.map(function (v, i) { return { id: 'b' + i, src: 'b', emo: v[0], title: v[1], desc: v[2], qs: v[3] }; });
    var mine = U.tv.eigene.map(function (t) { return t.id; });
    U.tshared.forEach(function (t) { if (mine.indexOf(t.id) < 0) out.push({ id: t.id, src: 's', emo: t.emo || '📊', title: t.title, desc: t.desc, set: t.set, qs: copy(t.qs) }); });
    U.tv.eigene.forEach(function (t) { out.push({ id: t.id, src: 'e', emo: t.emo || '⭐', title: t.title, desc: t.desc, set: t.set, qs: copy(t.qs) }); });
    return out;
  }
  U.tvSave = function () { return DB.storeSet('umfrage-vorlagen', { eigene: U.tv.eigene, weg: U.tv.weg }).catch(function (e) { toast('Nicht gespeichert: ' + errMsg(e)); }); };
  ACT.uTpl = function (el) {
    var t = umfTpls().filter(function (x) { return x.id === el.dataset.id; })[0]; if (!t) return;
    var sv = U.blank(t.title, t.qs()); if (t.set) sv.set = JSON.parse(JSON.stringify(t.set));
    U.list.unshift(sv); U.eid = sv.id; U.qi = 0; U.add = false; U.view = 'edit'; U.save(); U.render(); toast('Vorlage übernommen. Sie können alles anpassen.');
  };
  ACT.uTplDel = function (el) { var id = el.dataset.id; if (!armed('uTplDel' + id)) return U.render(); if (U.tv.weg.indexOf(id) < 0) U.tv.weg.push(id); U.tvSave(); U.render(); toast('Vorlage gelöscht. Unter «Gelöschte Vorlagen» können Sie sie wieder einfügen.'); };
  ACT.uTplWeg = function () { U.tvWeg = !U.tvWeg; U.render(); };
  ACT.uTplBack = function (el) { U.tv.weg = U.tv.weg.filter(function (x) { return x !== el.dataset.id; }); U.tvSave(); U.render(); toast('Vorlage wieder eingefügt'); };
  ACT.uTplGone = async function (el) {
    var id = el.dataset.id; if (!armed('uTplGone' + id)) return U.render();
    U.tv.eigene = U.tv.eigene.filter(function (x) { return x.id !== id; }); U.tv.weg = U.tv.weg.filter(function (x) { return x !== id; });
    await U.tvSave();
    if (U.admin && U.tshared.some(function (x) { return x.id === id; })) await U.tsharedSet(U.tshared.filter(function (x) { return x.id !== id; }));
    U.render(); toast('Vorlage endgültig gelöscht');
  };
  // Als Vorlage speichern (Kopie der Umfrage, Name, Text und Bildchen frei wählbar)
  var UMF_TPL_EMO = ['⭐', '📊', '🌈', '💬', '🎒', '🏆', '🧠', '🌍', '🎨', '📚', '🌱', '🎵'];
  ACT.uAsTpl = function (el) {
    var sv = U.find(el.dataset.id); if (!sv) return;
    if (!sv.qs.length) return toast('Die Umfrage hat noch keine Fragen.');
    U.tplEmo = '⭐';
    overlay('<form class="card stack" style="width:min(560px,100%)" data-a="uAsTplGo" data-id="' + sv.id + '"><h2>Als Vorlage speichern</h2>' +
      '<p class="muted">Die Vorlage ist eine Kopie. Sie erscheint bei Ihren Vorlagen' + (U.admin ? '. Als Admin können Sie sie danach für alle freigeben.' : '.') + '</p>' +
      '<div class="field"><label for="tplName">Name</label><input class="input" id="tplName" name="title" maxlength="60" required value="' + h(sv.title || '') + '"></div>' +
      '<div class="field"><label for="tplDesc">Kurze Beschreibung (freiwillig)</label><input class="input" id="tplDesc" name="desc" maxlength="80" placeholder="z. B. Rückblick nach dem Projekt"></div>' +
      '<div><span class="lbl">Bildchen</span><div class="chips umf-emo-chips">' + UMF_TPL_EMO.map(function (e) { return '<button type="button" class="chip" aria-pressed="' + (e === U.tplEmo) + '" data-a="uTplEmo" data-e="' + e + '">' + e + '</button>'; }).join('') + '</div></div>' +
      '<div class="row" style="justify-content:flex-end"><button type="button" class="btn" data-a="closeOverlay">Abbrechen</button><button class="btn primary">Speichern</button></div></form>');
  };
  ACT.uTplEmo = function (el) { U.tplEmo = el.dataset.e; Array.prototype.forEach.call(document.querySelectorAll('.umf-emo-chips .chip'), function (c) { c.setAttribute('aria-pressed', c.dataset.e === U.tplEmo); }); };
  ACT.uAsTplGo = async function (f) {
    var sv = U.find(f.dataset.id), title = f.elements.title.value.trim(); if (!sv || !title) return;
    var t = { id: umfId('v'), title: title.slice(0, 60), desc: f.elements.desc.value.trim().slice(0, 80), emo: U.tplEmo || '⭐', at: Date.now(),
      set: JSON.parse(JSON.stringify(sv.set || {})), qs: JSON.parse(JSON.stringify(sv.qs)) };
    U.tv.eigene.unshift(t); await U.tvSave(); closeOverlays(); if (U.view === 'list') U.render();
    toast('Als Vorlage gespeichert. Sie finden sie unten bei den Vorlagen.');
  };
  // Nur Admin: eigene Vorlage für alle Lehrpersonen freigeben oder zurücknehmen
  U.tsharedSet = async function (list) { await DB.sharedSet('umfrage-vorlagen', { list: list }); U.tshared = list; };
  ACT.uTplShare = async function (el) {
    if (!U.admin) return;
    var id = el.dataset.id, t = U.tv.eigene.filter(function (x) { return x.id === id; })[0]; if (!t) return;
    var on = U.tshared.some(function (x) { return x.id === id; });
    try { await U.tsharedSet(on ? U.tshared.filter(function (x) { return x.id !== id; }) : U.tshared.concat([JSON.parse(JSON.stringify(t))])); }
    catch (e) { return toast(errMsg(e)); }
    U.render(); toast(on ? 'Freigabe zurückgenommen.' : 'Für alle Lehrpersonen freigegeben.');
  };
  ACT.uEdit = function (el) { U.eid = el.dataset.id; U.qi = 0; U.add = !U.find(U.eid).qs.length; U.view = 'edit'; U.render(); window.scrollTo(0, 0); };
  ACT.uCopy = function (el) {
    var sv = JSON.parse(JSON.stringify(U.find(el.dataset.id))); sv.id = umfId('u'); sv.title = (sv.title || 'Umfrage') + ' (Kopie)'; sv.at = Date.now();
    sv.qs.forEach(function (q) { q.id = umfId('q'); }); U.list.unshift(sv); U.save(); U.render(); toast('Kopie erstellt');
  };
  ACT.uDel = function (el) {
    var id = el.dataset.id; if (!armed('uDel' + id)) return U.render();
    U.list = U.list.filter(function (x) { return x.id !== id; }); U.save(); U.render(); toast('Umfrage gelöscht');
  };
  ACT.uList = function () { if (U.st) U.save(); U.view = 'list'; U.add = false; U.render(); window.scrollTo(0, 0); };
  ACT.uToShow = function (el) { U.use(el.dataset.s || 'klasse'); U.view = 'show'; U.names = U.namesDefault(U.doc.live.sid); U.render(); };

  // ---------- Bearbeiten ----------
  U.sv = function () { return U.find(U.eid); };
  U.q = function () { var sv = U.sv(); return sv && sv.qs[U.qi] || null; };
  U.viewEdit = function () {
    var sv = U.sv(), set = sv.set || (sv.set = { mode: 'live', auto: 'live', kids: true, anon: true }), q = U.q();
    var chip = function (k, v, txt) { return '<button class="chip" aria-pressed="' + (set[k] === v) + '" data-a="uSet" data-k="' + k + '" data-v="' + v + '">' + txt + '</button>'; };
    var sw = function (k, on, txt) { return '<button class="switch" role="switch" aria-checked="' + on + '" data-a="uSetT" data-k="' + k + '"><span>' + txt + '</span><span class="track"></span></button>'; };
    var list = sv.qs.map(function (x, i) {
      var tp = umfType(x.type);
      return '<div class="ue-q' + (!U.add && i === U.qi ? ' sel' : '') + '"><button class="ue-qsel" data-a="uQ" data-i="' + i + '"><span class="ue-n">' + (i + 1) + '</span><span class="ue-ic" title="' + h(tp[1]) + '">' + tp[2] + '</span><span class="ue-qt">' + (x.text ? h(x.text) : '<i>' + h(tp[1]) + ' ohne Text</i>') + '</span></button>' +
        '<span class="ue-qb"><button data-a="uQMove" data-i="' + i + '" data-d="-1" aria-label="Nach oben"' + (i ? '' : ' disabled') + '>↑</button><button data-a="uQMove" data-i="' + i + '" data-d="1" aria-label="Nach unten"' + (i < sv.qs.length - 1 ? '' : ' disabled') + '>↓</button>' +
        '<button data-a="uQCopy" data-i="' + i + '" aria-label="Kopieren" title="Kopieren">⧉</button><button data-a="uQDel" data-i="' + i + '" aria-label="Löschen" title="Löschen"' + (UI.confirm === 'uQDel' + x.id ? ' class="armed"' : '') + '>' + (UI.confirm === 'uQDel' + x.id ? '?' : '✕') + '</button></span></div>';
    }).join('');
    var aside = '<aside class="ue-side stack"><div class="card stack"><div class="field"><label for="ueTitle">Titel der Umfrage</label><input class="input" id="ueTitle" data-input="uTitle" maxlength="80" placeholder="z. B. Wie war die Woche?" value="' + h(sv.title) + '"></div>' +
      '<div class="stack" style="gap:8px"><span class="lbl">Fragen</span>' + (list || '<p class="muted small">Noch keine Fragen.</p>') +
      '<button class="btn' + (U.add ? ' primary' : '') + '" data-a="uAddOpen">+ Frage hinzufügen</button></div></div>' +
      '<div class="card stack ue-set"><h3>Einstellungen</h3>' +
      '<div><span class="lbl">Ablauf</span><div class="chips">' + chip('mode', 'live', '🎬 Live: Frage für Frage') + chip('mode', 'selbst', '🚶 Selbsttempo') + '</div><p class="muted small">' +
        (set.mode === 'selbst' ? 'Die Kinder gehen alle Fragen selbst durch, z. B. als Rückmeldung während dem Tag.' : 'Sie zeigen eine Frage nach der anderen. Die Kinder sehen immer die aktuelle Frage.') + '</p></div>' +
      '<div><span class="lbl">Ergebnis an der Wandtafel</span><div class="chips">' + chip('auto', 'live', 'Sofort zeigen') + chip('auto', 'aufdecken', 'Erst aufdecken') + '</div></div>' +
      sw('kids', set.kids !== false, 'Kinder sehen das Ergebnis auch am iPad') + sw('anon', set.anon === false, 'Namen an der Wandtafel zeigen') +
      '<p class="muted small">Die Kinder sehen die Antworten der anderen nie mit Namen.</p></div></aside>';
    var main;
    if (U.add || !q) main = '<div class="card stack"><h2>Was für eine Frage?</h2><div class="ue-types">' + UMF_TYPES.map(function (t) {
      return '<button class="ue-type" data-a="uAdd" data-t="' + t[0] + '"><span class="ue-emo">' + t[2] + '</span><b>' + t[1] + '</b><small>' + t[3] + '</small></button>'; }).join('') + '</div>' +
      (sv.qs.length ? '<button class="btn" style="align-self:flex-start" data-a="uAddClose">Abbrechen</button>' : '') + '</div>';
    else main = '<div class="card stack ue-edit">' + U.qForm(q) + '</div><div class="card stack ue-prevcard"><span class="lbl">So sieht es am iPad aus</span><div class="ue-phone"><div class="ku ku-prev" id="uePrev">' + umfPreview(q) + '</div></div></div>';
    return '<div class="umf-page">' + U.top('<button class="btn sm" data-a="uList">← Meine Umfragen</button><span class="muted small" id="ueSaved">' + (U.st ? 'Wird gespeichert …' : '✓ Gespeichert') + '</span>',
      '<button class="btn" data-a="uAsTpl" data-id="' + sv.id + '">⭐ Als Vorlage speichern</button><button class="btn primary" data-a="uStart" data-id="' + sv.id + '">▶ Starten</button>') + '<div class="umf-ed">' + aside + '<section class="ue-main stack">' + main + '</section></div></div>';
  };
  function umfPreview(q) {
    var t = umfType(q.type);
    return '<span class="ku-nr">' + t[2] + ' ' + h(t[1]) + '</span><h2 class="ku-q">' + (q.text ? h(q.text) : '…') + '</h2>' + umfInput(umfClean(q), null, true);
  }
  U.prev = function () { var p = document.getElementById('uePrev'), q = U.q(); if (p && q) p.innerHTML = umfPreview(q); };
  U.qForm = function (q) {
    var t = umfType(q.type), o = '';
    var chips = function (f, vals, txt) { return '<div class="chips">' + vals.map(function (v) { return '<button class="chip" aria-pressed="' + (String(q[f]) === String(v)) + '" data-a="uqSet" data-f="' + f + '" data-v="' + v + '">' + txt(v) + '</button>'; }).join('') + '</div>'; };
    var inp = function (id, f, lbl, ph, extra) { return '<div class="field"><label for="' + id + '">' + lbl + '</label><input class="input" id="' + id + '" data-input="uqF" data-f="' + f + '" value="' + h(q[f] == null ? '' : q[f]) + '" placeholder="' + h(ph || '') + '"' + (extra || '') + '></div>'; };
    o += '<div class="row" style="justify-content:space-between"><span class="ue-badge">' + t[2] + ' ' + t[1] + '</span><span class="muted small">Frage ' + (U.qi + 1) + ' von ' + U.sv().qs.length + '</span></div>';
    o += '<div class="field"><label for="uqText">' + (q.type === 'info' ? 'Titel' : 'Frage') + '</label><textarea class="input" id="uqText" rows="2" maxlength="200" data-input="uqF" data-f="text" placeholder="' + (q.type === 'info' ? 'z. B. Willkommen!' : 'Was möchten Sie die Klasse fragen?') + '">' + h(q.text) + '</textarea></div>';
    if (q.type === 'info') o += '<div class="field"><label for="uqSub">Text</label><textarea class="input" id="uqSub" rows="4" maxlength="600" data-input="uqF" data-f="sub" placeholder="Was die Kinder lesen sollen">' + h(q.sub || '') + '</textarea></div>';
    if (q.opts) {
      var isSk = q.type === 'skala', isSt = q.type === 'stimmung', maxO = isSk ? 6 : 8;
      if (isSt) o += '<div><span class="lbl">Aussehen</span><div class="chips">' + Object.keys(UMF_STIL).map(function (k) {
        return '<button class="chip" aria-pressed="' + (q.stil === k) + '" data-a="uqStil" data-s="' + k + '">' + UMF_STIL[k].map(function (x) { return umfEmo(x)[0]; }).join('') + ' ' + UMF_STIL_NAME[k] + '</button>'; }).join('') + '</div></div>';
      o += '<div class="stack" style="gap:8px"><span class="lbl">' + (isSk ? 'Aussagen' : 'Antworten') + (q.type === 'quiz' ? ' <span class="muted small">(richtige mit ✓ markieren)</span>' : '') + '</span>' + q.opts.map(function (x, i) {
        var okOn = q.type === 'quiz' && (q.ok || []).indexOf(i) >= 0;
        return '<div class="ue-opt"><span class="ue-dot" style="background:' + UMF_COL[i % UMF_COL.length] + '"></span><input class="input" id="uqO' + i + '" data-input="uqO" data-i="' + i + '" maxlength="80" value="' + h(x) + '" placeholder="' + (isSk ? 'Aussage ' : 'Antwort ') + (i + 1) + '">' +
          (q.type === 'quiz' ? '<button class="ue-ok' + (okOn ? ' on' : '') + '" data-a="uqOk" data-i="' + i + '" aria-pressed="' + okOn + '">✓ richtig</button>' : '') +
          (isSt ? '' : '<button class="btn sm icon" data-a="uqODel" data-i="' + i + '" aria-label="Entfernen"' + (q.opts.length > 1 ? '' : ' disabled') + '>✕</button>') + '</div>';
      }).join('') + (isSt || q.opts.length >= maxO ? '' : '<button class="btn sm" style="align-self:flex-start" data-a="uqOAdd">+ ' + (isSk ? 'Aussage' : 'Antwort') + '</button>') + '</div>';
      if (q.type === 'wahl' || q.type === 'quiz') o += '<button class="switch" role="switch" aria-checked="' + !!q.multi + '" data-a="uqTog" data-f="multi"><span>' + (q.type === 'quiz' ? 'Mehrere richtige Antworten' : 'Kinder dürfen mehrere Antworten wählen') + '</span><span class="track"></span></button>';
    }
    if (q.type === 'wort') o += '<div><span class="lbl">Wörter pro Kind</span>' + chips('max', [1, 2, 3, 5], function (v) { return v; }) + '</div>';
    if (q.type === 'text') o += '<div><span class="lbl">Antworten pro Kind</span>' + chips('max', [1, 2, 3], function (v) { return v; }) + '</div>';
    if (q.type === 'skala') o += '<div><span class="lbl">Skala</span>' + chips('max', [3, 5, 10], function (v) { return '1 bis ' + v; }) + '</div><div class="ue-two">' + inp('uqLo', 'lo', 'Text bei 1', 'stimmt gar nicht', ' maxlength="40"') + inp('uqHi', 'hi', 'Text bei ' + umfSkMax(q), 'stimmt genau', ' maxlength="40"') + '</div>';
    if (q.type === 'punkte') o += '<div><span class="lbl">Sterne pro Kind</span>' + chips('pts', [3, 5, 10, 20], function (v) { return v + ' ⭐'; }) + '</div>';
    if (q.type === 'zahl') o += '<div class="ue-two">' + inp('uqOk', 'ok', 'Lösung (freiwillig)', 'z. B. 26', ' inputmode="decimal"') + inp('uqUnit', 'unit', 'Einheit (freiwillig)', 'z. B. kg', ' maxlength="20"') + '</div>' +
      '<div class="ue-two">' + inp('uqMin', 'min', 'Kleinste erlaubte Zahl', 'keine Grenze', ' inputmode="decimal"') + inp('uqMax', 'max', 'Grösste erlaubte Zahl', 'keine Grenze', ' inputmode="decimal"') + '</div>';
    if (q.type === 'feld') o += '<div class="ue-four">' + ['links', 'rechts', 'unten', 'oben'].map(function (w, i) {
      return '<div class="field"><label for="uqAx' + i + '">Text ' + w + '</label><input class="input" id="uqAx' + i + '" data-input="uqAx" data-i="' + i + '" maxlength="30" value="' + h((q.ax || [])[i] || '') + '"></div>'; }).join('') + '</div>';
    return o;
  };
  ACT.uTitle = function (el) { U.sv().title = el.value; U.saveSoon(); };
  ACT.uSet = function (el) { var s = U.sv().set; s[el.dataset.k] = el.dataset.v; U.saveSoon(); U.render(); };
  ACT.uSetT = function (el) { var s = U.sv().set, k = el.dataset.k; if (k === 'kids') s.kids = s.kids === false; else s.anon = s.anon === false; U.saveSoon(); U.render(); };
  ACT.uQ = function (el) { U.qi = +el.dataset.i; U.add = false; U.render(); };
  ACT.uAddOpen = function () { U.add = true; U.render(); };
  ACT.uAddClose = function () { U.add = false; U.render(); };
  ACT.uAdd = function (el) { var sv = U.sv(), q = umfNewQ(el.dataset.t), at = sv.qs.length ? Math.min(sv.qs.length, U.qi + 1) : 0; sv.qs.splice(at, 0, q); U.qi = at; U.add = false; U.saveSoon(); U.render(); var t = document.getElementById('uqText'); if (t) t.focus(); };
  ACT.uQMove = function (el) { var sv = U.sv(), i = +el.dataset.i, j = i + +el.dataset.d; if (j < 0 || j >= sv.qs.length) return; var x = sv.qs.splice(i, 1)[0]; sv.qs.splice(j, 0, x); U.qi = j; U.saveSoon(); U.render(); };
  ACT.uQCopy = function (el) { var sv = U.sv(), i = +el.dataset.i, c = JSON.parse(JSON.stringify(sv.qs[i])); c.id = umfId('q'); sv.qs.splice(i + 1, 0, c); U.qi = i + 1; U.add = false; U.saveSoon(); U.render(); };
  ACT.uQDel = function (el) { var sv = U.sv(), i = +el.dataset.i; if (!armed('uQDel' + sv.qs[i].id)) return U.render(); sv.qs.splice(i, 1); U.qi = Math.max(0, Math.min(U.qi, sv.qs.length - 1)); U.saveSoon(); U.render(); };
  // Eingaben ohne neu zeichnen (Fokus bleibt), nur Liste links und Vorschau nachführen
  ACT.uqF = function (el) {
    var q = U.q(); q[el.dataset.f] = el.value; U.saveSoon(); U.prev();
    if (el.dataset.f === 'text') { var t = document.querySelector('.ue-q.sel .ue-qt'); if (t) t.textContent = el.value || umfType(q.type)[1] + ' ohne Text'; }
  };
  ACT.uqO = function (el) { U.q().opts[+el.dataset.i] = el.value; U.saveSoon(); U.prev(); };
  ACT.uqAx = function (el) { var q = U.q(); q.ax = q.ax || []; q.ax[+el.dataset.i] = el.value; U.saveSoon(); U.prev(); };
  ACT.uqOAdd = function () { var q = U.q(); q.opts.push(''); U.saveSoon(); U.render(); var i = document.getElementById('uqO' + (q.opts.length - 1)); if (i) i.focus(); };
  ACT.uqODel = function (el) {
    var q = U.q(), i = +el.dataset.i; if (q.opts.length <= 1) return; q.opts.splice(i, 1);
    if (q.type === 'quiz') q.ok = (q.ok || []).filter(function (x) { return x !== i; }).map(function (x) { return x > i ? x - 1 : x; });
    U.saveSoon(); U.render();
  };
  ACT.uqOk = function (el) {
    var q = U.q(), i = +el.dataset.i, ok = q.ok || [];
    if (q.multi) { if (ok.indexOf(i) >= 0) ok = ok.filter(function (x) { return x !== i; }); else ok = ok.concat([i]); } else ok = [i];
    q.ok = ok; U.saveSoon(); U.render();
  };
  ACT.uqTog = function (el) { var q = U.q(), f = el.dataset.f; q[f] = !q[f]; if (f === 'multi' && !q.multi && q.type === 'quiz' && (q.ok || []).length > 1) q.ok = [q.ok[0]]; U.saveSoon(); U.render(); };
  ACT.uqSet = function (el) { var q = U.q(); q[el.dataset.f] = +el.dataset.v; U.saveSoon(); U.render(); };
  ACT.uqStil = function (el) { var q = U.q(); q.stil = el.dataset.s; q.opts = UMF_STIL[q.stil].slice(); U.saveSoon(); U.render(); };

  // ---------- Starten und Anzeige an der Wandtafel ----------
  ACT.uStart = async function (el) {
    var sv = U.find(el.dataset.id); if (!sv) return;
    var bad = umfCheck(sv); if (bad) { if (U.view !== 'edit') { U.eid = sv.id; U.qi = 0; U.add = false; U.view = 'edit'; U.render(); } return toast(bad); }
    if (U.st) await U.save();
    var o = U.docs.offen, ol = o && o.live;
    return overlay('<div class="card stack" style="width:min(620px,100%)"><h2>Wer macht mit?</h2><div class="umf-wer">' +
      '<button class="umf-wer-btn" data-a="uStartK" data-id="' + sv.id + '"><span class="umf-wer-emo">🏫</span><b>Klasse ' + h(U.cls.name) + '</b><small>Die Kinder machen mit ihrem Klassen-Login mit (Kachel «Umfrage!»).</small></button>' +
      '<button class="umf-wer-btn" data-a="uGoO" data-id="' + sv.id + '"><span class="umf-wer-emo">🌍</span><b>Offen per QR-Code</b><small>Alle können ohne Login mitmachen, z. B. Eltern, andere Klassen oder das Team.</small></button></div>' +
      (ol && ol.on ? '<p class="note">Ihre laufende offene Umfrage «' + h(ol.title || '') + '» wird beendet, wenn Sie eine neue offene starten.</p>' : '') +
      '<button class="btn" style="align-self:flex-end" data-a="closeOverlay">Abbrechen</button></div>');
  };
  ACT.uStartK = function (el) {
    closeOverlays(); var sv = U.find(el.dataset.id); if (!sv) return;
    U.use('klasse');
    var has = sv.qs.some(function (q) { return Object.keys(U.doc.ans[q.id] || {}).length; }), l = U.doc.live;
    var other = l && l.on && l.sid !== sv.id ? '<p class="note">Die laufende Umfrage «' + h(l.title || '') + '» wird dabei beendet.</p>' : '';
    if (has) return overlay('<div class="card stack" style="width:min(560px,100%)"><h2>Diese Umfrage hat schon Antworten</h2>' +
      '<p>Möchten Sie dort weitermachen oder neu beginnen? Beim Neubeginn werden die bisherigen Antworten dieser Klasse gelöscht.</p>' + other +
      '<div class="row" style="justify-content:flex-end"><button class="btn" data-a="closeOverlay">Abbrechen</button><button class="btn" data-a="uGo" data-id="' + sv.id + '" data-neu="0">Weitermachen</button><button class="btn primary" data-a="uGo" data-id="' + sv.id + '" data-neu="1">Neu beginnen</button></div></div>');
    if (other) return overlay('<div class="card stack" style="width:min(560px,100%)"><h2>Umfrage starten?</h2>' + other +
      '<div class="row" style="justify-content:flex-end"><button class="btn" data-a="closeOverlay">Abbrechen</button><button class="btn primary" data-a="uGo" data-id="' + sv.id + '" data-neu="0">Starten</button></div></div>');
    return ACT.uGo({ dataset: { id: sv.id, neu: '0' } });
  };
  ACT.uGo = async function (el) {
    closeOverlays();
    var sv = U.find(el.dataset.id), set = sv.set || {}, qs = sv.qs.map(umfClean);
    var live = { on: true, sid: sv.id, title: sv.title || 'Umfrage', mode: set.mode === 'selbst' ? 'selbst' : 'live', cur: qs[0].id, open: true,
      show: set.auto !== 'aufdecken', auto: set.auto === 'aufdecken' ? 'aufdecken' : 'live', kids: set.kids !== false, rev: [], hid: {}, hidw: {}, until: null, qs: qs };
    U.use('klasse'); U.view = 'show'; U.names = set.anon === false; U.fehlt = false; U.rank = false; U.more = false;
    await U.setLive(live, el.dataset.neu === '1' ? qs.map(function (q) { return q.id; }) : null, null, true);
    toast('Die Umfrage läuft. Die Kinder tippen auf «Umfrage».');
  };
  function umfLive(sv) {
    var set = sv.set || {}, qs = sv.qs.map(umfClean);
    return { on: true, sid: sv.id, title: sv.title || 'Umfrage', mode: set.mode === 'selbst' ? 'selbst' : 'live', cur: qs[0].id, open: true,
      show: set.auto !== 'aufdecken', auto: set.auto === 'aufdecken' ? 'aufdecken' : 'live', kids: set.kids !== false, rev: [], hid: {}, hidw: {}, until: null, qs: qs };
  }
  // Offen per QR-Code: neue Runde mit 6-stelliger Nummer (die alte offene Runde wird gelöscht)
  ACT.uGoO = async function (el) {
    closeOverlays(); var sv = U.find(el.dataset.id); if (!sv) return;
    var live = umfLive(sv), r;
    try { r = await DB.umfOffenOpen(JSON.parse(JSON.stringify(live))); }
    catch (e) { return toast(/umf_offen|function|schema cache/i.test(errMsg(e)) ? 'Dafür zuerst das neue SQL (Version 27) in Supabase ausführen.' : errMsg(e)); }
    U.docs.offen = { id: r.id, nr: r.nr, live: live, ans: {}, gaeste: [] }; U.off = r.now ? r.now - Date.now() : 0;
    U.use('offen'); U.view = 'show'; U.names = !!(sv.set && sv.set.anon === false); U.fehlt = false; U.rank = false; U.more = false;
    U.render(); ACT.uQr();
  };
  U.idx = function () { var l = U.doc.live, qs = l.qs || []; for (var i = 0; i < qs.length; i++) if (qs[i].id === l.cur) return i; return 0; };
  U.viewShow = function () {
    var l = U.doc.live, qs = l.qs || [], i = U.idx(), q = qs[i] || qs[0], ans = U.doc.ans[q.id] || {}, kidName = {};
    U.kids.forEach(function (k) { kidName[k.id] = k.name; });
    var hid = (l.hid || {})[q.id] || [], hidw = (l.hidw || {})[q.id] || [];
    var E = Object.keys(ans).filter(function (k) { return hid.indexOf(k) < 0; }).map(function (k) { return { k: k, v: ans[k], n: kidName[k] || '' }; });
    var answered = Object.keys(ans).filter(function (k) { return kidName[k]; }).length, total = U.kids.length, rev = (l.rev || []).indexOf(q.id) >= 0, selbst = l.mode === 'selbst';
    var hasQuiz = qs.some(function (x) { return x.type === 'quiz' && (x.ok || []).length; });
    var head = '<div class="us-head"><img class="board-bild" src="' + h(U.src === 'offen' ? 'bilder/kacheln/umfrage-kiste.webp' : klassBild(U.cls.bild)) + '" alt=""><div class="us-tt"><span class="kick">Umfrage · ' + (U.src === 'offen' ? 'offen für alle' : 'Klasse ' + h(U.cls.name)) + ' <span class="sterne" aria-hidden="true">✦ ✧ ✦</span></span><b>' + h(l.title || 'Umfrage') + '</b></div>' +
      (U.src === 'offen' ? '<button class="us-join us-offen" data-a="uQr" title="QR-Code gross zeigen"><span class="us-qrmini" id="usQr"></span><span>Mitmachen ohne Login:<br><b>' + h(shortUrl(umfGastUrl())) + '</b> · Nummer <b class="us-nr6">' + h(umfNr(U.doc.nr)) + '</b></span></button>'
        : '<div class="us-join">Mitmachen: ' + h(C.PORTAL_NAME) + ' öffnen und auf <b>«Umfrage»</b> tippen · Code <b>' + h(U.cls.code || '') + '</b></div>') +
      '<div class="row"><button class="board-btn" data-a="wallFull">Vollbild</button><button class="board-btn" data-a="uBack">Zur Liste</button><button class="board-btn' + (UI.confirm === 'uEnd' ? ' armed' : '') + '" data-a="uEnd">' + (UI.confirm === 'uEnd' ? 'Wirklich beenden?' : '■ Beenden') + '</button></div></div>';
    var body;
    if (U.rank) {
      var R = umfRank(qs, U.doc.ans, U.kids), L = R.list;
      body = '<div class="us-q"><span class="us-nr">🏆 Quiz-Rangliste</span><h1>Wer hatte am meisten richtig?</h1></div><div class="us-res spr-result"><div class="podium">' + [1, 0, 2].map(function (j) {
        var x = L[j]; if (!x) return '<div class="pod p' + (j + 1) + ' empty"></div>';
        return '<div class="pod p' + (j + 1) + '"><span class="m">' + medal(j + 1) + '</span><b>' + h(x.name) + '</b><span>' + x.p + ' von ' + R.n + '</span></div>'; }).join('') + '</div>' +
        '<ol class="ranking" start="4">' + L.slice(3).map(function (x) { return '<li><b>' + h(x.name) + '</b> · ' + x.p + ' von ' + R.n + '</li>'; }).join('') + '</ol></div>';
    } else {
      var t = umfType(q.type);
      body = '<div class="us-q"><span class="us-nr">' + t[2] + ' ' + (selbst ? 'Ergebnis ' : 'Frage ') + (i + 1) + ' von ' + qs.length + (selbst ? ' · Selbsttempo' : '') + '</span><h1>' + h(q.text) + '</h1></div>';
      if (q.type === 'info') body += '<div class="us-res us-info"><p>' + h(q.sub || '') + '</p></div>';
      else if (!l.show) body += '<div class="us-res us-hidden"><div class="us-bubbles">' + E.map(function (e, j) { return '<i style="background:' + UMF_COL[j % UMF_COL.length] + ';animation-delay:' + (j % 7) * .15 + 's"></i>'; }).join('') + '</div>' +
        '<span class="us-big">' + E.length + '</span><span>' + (E.length === 1 ? 'Antwort' : 'Antworten') + '</span><small>Das Ergebnis ist noch verdeckt.</small></div>';
      else body += '<div class="us-res">' + umfRes(q, E, { rev: rev, names: U.names, mod: true, hidw: hidw }) + '</div>';
      if (U.fehlt && q.type !== 'info') {
        var miss = U.kids.filter(function (k) { return ans[k.id] === undefined; });
        body += '<div class="board-fehlt">' + (U.src === 'offen' && !U.kids.length ? '<b>Noch niemand macht mit.</b>' : miss.length ? '<b>Noch keine Antwort:</b>' + miss.map(function (k) { return '<span class="tag"><span class="ini" style="background:' + kidColor(k.name) + '">' + h(k.name.charAt(0)) + '</span>' + h(k.name) + '</span>'; }).join('') : (U.src === 'offen' ? '<b>✓ Alle haben geantwortet.</b>' : '<b>✓ Alle Kinder haben geantwortet.</b>')) + '</div>';
      }
    }
    var left = U.left(), b = function (a, txt, extra) { return '<button class="board-btn' + (extra || '') + '" data-a="' + a + '">' + txt + '</button>'; };
    var nHid = hid.length + hidw.length;
    var more = U.more ? '<div class="us-more">' + b('uFehlt', U.fehlt ? '👤 Fehlende ausblenden' : '👤 Wer fehlt noch?') + b('uNames', U.names ? '🙈 Namen verbergen' : '🏷️ Namen zeigen') +
      (nHid ? b('uUnhide', '↺ ' + nHid + ' Ausgeblendete wieder zeigen') : '') + (hasQuiz ? b('uRank', U.rank ? '← Zurück zur Frage' : '🏆 Quiz-Rangliste') : '') +
      (q.type !== 'info' ? b('uClearQ', UI.confirm === 'uClearQ' ? 'Wirklich alle Antworten löschen?' : '🗑 Antworten dieser Frage löschen', UI.confirm === 'uClearQ' ? ' armed' : '') : '') + '</div>' : '';
    var foot = '<div class="us-foot">' + more + '<div class="us-bar"><button class="board-btn" data-a="uNav" data-d="-1"' + (i ? '' : ' disabled') + ' aria-label="Vorherige Frage">◀</button>' +
      (q.type !== 'info' ? '<span class="us-count"><b>' + answered + '</b> von ' + total + ' <span class="us-prog"><i style="width:' + (total ? Math.round(answered / total * 100) : 0) + '%"></i></span></span>' : '<span class="us-count">Infofolie</span>') +
      '<span class="us-main-btns">' + (q.type !== 'info' ? b('uShow', l.show ? '🙈 Verdecken' : '👁 Ergebnis zeigen', l.show ? '' : ' hot') +
        b('uOpen', l.open ? '🔒 Schliessen' : '🔓 Öffnen', l.open ? '' : ' warn') +
        (!selbst ? (l.until ? '<button class="board-btn hot" data-a="uTimer">⏱ <span id="umfTimer">' + umfSec(left || 0) + '</span> ✕</button>' : b('uTimer', '⏱ Timer')) : '') +
        (umfHasOk(q) ? b('uRev', rev ? '✓ Lösung verbergen' : '✓ Lösung zeigen', rev ? ' on' : '') : '') : '') +
        b('uMore', '⋯ Mehr', U.more ? ' on' : '') + '</span>' +
      '<button class="board-btn us-next" data-a="uNav" data-d="1"' + (i < qs.length - 1 ? '' : ' disabled') + '>Weiter ▶</button></div></div>';
    return '<div class="umf-show' + (l.open ? '' : ' zu') + '">' + head + '<div class="us-mainarea">' + body + '</div>' + foot + '</div>';
  };
  ACT.uBack = function () { U.view = 'list'; U.render(); };
  ACT.uEnd = async function () {
    if (!armed('uEnd')) return U.render();
    var sid = U.doc.live.sid; await U.setLive({ on: false, open: false, until: null }); // Quelle (Klasse/offen) bleibt für die Ergebnisse
    U.rid = sid; U.view = U.find(sid) ? 'res' : 'list'; U.render(); toast('Umfrage beendet. Die Antworten bleiben gespeichert.');
  };
  ACT.uNav = function (el) {
    var l = U.doc.live, qs = l.qs || [], j = U.idx() + +el.dataset.d; if (j < 0 || j >= qs.length) return;
    U.rank = false; U.fehlt = false; UI.confirm = null;
    U.setLive({ cur: qs[j].id, open: true, show: l.auto !== 'aufdecken', until: null }).catch(function (e) { toast(errMsg(e)); });
  };
  ACT.uShow = function () { U.setLive({ show: !U.doc.live.show }); };
  ACT.uOpen = function () { U.setLive({ open: !U.doc.live.open, until: null }); };
  ACT.uRev = function () {
    var l = U.doc.live, rev = (l.rev || []).slice(), i = rev.indexOf(l.cur);
    if (i >= 0) rev.splice(i, 1); else rev.push(l.cur);
    U.setLive(i >= 0 ? { rev: rev } : { rev: rev, show: true });
  };
  ACT.uTimer = function () {
    if (U.doc.live.until) return U.setLive({ until: null });
    overlay('<div class="card stack" style="width:min(520px,100%)"><h2>⏱ Wie lange dürfen die Kinder antworten?</h2><p class="muted">Danach wird die Abstimmung geschlossen und das Ergebnis gezeigt.</p><div class="chips">' +
      [[20, '20 Sekunden'], [30, '30 Sekunden'], [60, '1 Minute'], [120, '2 Minuten'], [180, '3 Minuten'], [300, '5 Minuten']].map(function (x) {
        return '<button class="chip" data-a="uTimerGo" data-s="' + x[0] + '">' + x[1] + '</button>'; }).join('') + '</div><button class="btn" style="align-self:flex-end" data-a="closeOverlay">Abbrechen</button></div>');
  };
  ACT.uTimerGo = function (el) { closeOverlays(); U.setLive({ open: true }, null, +el.dataset.s); };
  ACT.uMore = function () { U.more = !U.more; U.render(); };
  ACT.uFehlt = function () { U.fehlt = !U.fehlt; U.render(); };
  ACT.uNames = function () { U.names = !U.names; U.render(); };
  ACT.uRank = function () { U.rank = !U.rank; U.render(); };
  ACT.uHide = function (el) { var l = U.doc.live, hid = JSON.parse(JSON.stringify(l.hid || {})); hid[l.cur] = (hid[l.cur] || []).concat([el.dataset.k]); U.setLive({ hid: hid }); };
  ACT.uHideW = function (el) { var l = U.doc.live, hw = JSON.parse(JSON.stringify(l.hidw || {})); hw[l.cur] = (hw[l.cur] || []).concat([el.dataset.w]); U.setLive({ hidw: hw }); toast('Wort ausgeblendet'); };
  ACT.uUnhide = function () { var l = U.doc.live, hid = Object.assign({}, l.hid), hw = Object.assign({}, l.hidw); delete hid[l.cur]; delete hw[l.cur]; U.setLive({ hid: hid, hidw: hw }); };
  ACT.uClearQ = function () { if (!armed('uClearQ')) return U.render(); U.setLive({}, [U.doc.live.cur]); toast('Antworten gelöscht'); };
  document.addEventListener('keydown', function (e) {
    if (UI.view !== 'umfrage' || U.view !== 'show' || document.querySelector('.overlay') || /INPUT|TEXTAREA|SELECT/.test((e.target && e.target.tagName) || '')) return;
    var d = e.key === 'ArrowRight' || e.key === 'PageDown' ? 1 : e.key === 'ArrowLeft' || e.key === 'PageUp' ? -1 : 0;
    if (d) { e.preventDefault(); ACT.uNav({ dataset: { d: d } }); }
  });

  // ---------- Ergebnisse (nach der Umfrage) ----------
  ACT.uRes = function (el) { U.rid = el.dataset.id; U.use(el.dataset.s || 'klasse'); U.view = 'res'; U.render(); window.scrollTo(0, 0); };
  ACT.uResSrc = function (el) { U.use(el.dataset.s); U.render(); };
  U.viewRes = function () {
    var sv = U.find(U.rid); if (!sv) { U.view = 'list'; return U.viewList(); }
    var kidName = {}; U.kids.forEach(function (k) { kidName[k.id] = k.name; });
    var qs = sv.qs.map(umfClean), del = UI.confirm === 'uResDel';
    var hasQuiz = qs.some(function (q) { return q.type === 'quiz' && (q.ok || []).length; });
    var out = '<div class="umf-page">' + U.top('<button class="btn sm" data-a="uList">← Meine Umfragen</button>',
      '<button class="btn sm" data-a="uResNames">' + (U.resNames ? '🙈 Namen verbergen' : '🏷️ Namen zeigen') + '</button><button class="btn sm" data-a="uCsv">⬇ Tabelle</button>' +
      '<button class="btn sm danger' + (del ? ' armed' : '') + '" data-a="uResDel">' + (del ? 'Wirklich alle Antworten löschen?' : '🗑 Antworten löschen') + '</button><button class="btn primary" data-a="uStart" data-id="' + sv.id + '">▶ Nochmals starten</button>') +
      '<section class="stack"><h2>' + h(sv.title || 'Umfrage') + ' · Ergebnisse</h2>' +
      (U.docs.offen && U.docs.offen.live && U.docs.offen.live.sid === sv.id ? '<div class="chips"><button class="chip" aria-pressed="' + (U.src === 'klasse') + '" data-a="uResSrc" data-s="klasse">🏫 Klasse ' + h(U.cls.name) + '</button><button class="chip" aria-pressed="' + (U.src === 'offen') + '" data-a="uResSrc" data-s="offen">🌍 Offen per QR-Code (' + plural(U.docs.offen.gaeste.length, 'Person', 'Personen') + ')</button></div>' : '') +
      '<p class="muted">' + (U.src === 'offen' ? 'Offene Runde (Nummer ' + h(umfNr(U.doc.nr)) + '). Sie bleibt bis zur nächsten offenen Umfrage gespeichert, höchstens 30 Tage.' : 'Klasse ' + h(U.cls.name) + '.') + ' Alle Antworten, auch ausgeblendete. Die Tabelle können Sie in Excel öffnen.</p>';
    if (hasQuiz) {
      var R = umfRank(qs, U.doc.ans, U.kids);
      out += '<div class="card stack"><h3>🏆 Quiz-Rangliste</h3><ol class="ur-rangkids">' + R.list.map(function (x) { return '<li><b>' + h(x.name) + '</b> ' + x.p + ' von ' + R.n + ' richtig</li>'; }).join('') + '</ol></div>';
    }
    out += qs.map(function (q, i) {
      var ans = U.doc.ans[q.id] || {}, E = Object.keys(ans).map(function (k) { return { k: k, v: ans[k], n: kidName[k] || '' }; }), t = umfType(q.type);
      return '<div class="card stack umf-rescard"><div class="row" style="justify-content:space-between"><span class="ue-badge">' + t[2] + ' ' + (i + 1) + '. ' + t[1] + '</span>' + (q.type !== 'info' ? '<span class="muted small">' + plural(E.length, 'Antwort', 'Antworten') + '</span>' : '') + '</div>' +
        '<h3>' + h(q.text) + '</h3>' + (q.type === 'info' ? '<p>' + h(q.sub || '') + '</p>' : umfRes(q, E, { rev: true, names: U.resNames, small: true })) + '</div>';
    }).join('') + '</section></div>';
    return out;
  };
  ACT.uResNames = function () { U.resNames = !U.resNames; U.render(); };
  ACT.uResDel = function () {
    if (!armed('uResDel')) return U.render();
    var sv = U.find(U.rid);
    if (U.src === 'offen') return DB.umfOffenClose(U.doc.id).then(function () { U.docs.offen = null; U.use('klasse'); toast('Offene Runde gelöscht'); U.view = 'list'; U.render(); });
    U.setLive(null, sv.qs.map(function (q) { return q.id; })).then(function () { toast('Antworten gelöscht'); U.view = 'list'; U.render(); });
  };
  ACT.uCsv = function () {
    var sv = U.find(U.rid), qs = sv.qs.map(umfClean).filter(function (q) { return q.type !== 'info'; });
    var cell = function (s) { s = String(s == null ? '' : s); return /[";\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s; };
    var rows = [[U.src === 'offen' ? 'Name' : 'Kind'].concat(qs.map(function (q) { return q.text; }))];
    U.kids.forEach(function (k) { rows.push([k.name].concat(qs.map(function (q) { var v = (U.doc.ans[q.id] || {})[k.id]; return v === undefined ? '' : umfFmt(q, v); }))); });
    var blob = new Blob(['﻿' + rows.map(function (r) { return r.map(cell).join(';'); }).join('\r\n')], { type: 'text/csv;charset=utf-8' });
    var a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'Umfrage ' + (sv.title || '').replace(/[\\/:*?"<>|]/g, '') + ' ' + (U.src === 'offen' ? 'offen' : U.cls.name) + '.csv';
    document.body.appendChild(a); a.click(); setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500);
  };

  // ===================================================================
  // Gedächtniskiste: Vorschau aller Gedächtnisspiele für Lehrpersonen (gedaechtnis/index.html).
  // Die Spiele selbst liegen in gedaechtnis/<spiel>.html; in der Tabelle «games» steht nur ein Verweis (knobelnest-url).
  // ===================================================================
  var GD = {
    start: async function (cid) {
      UI.view = 'gedaechtnis';
      var s = await DB.session();
      if (!s) { location.hash = '#/'; return; }
      if (!(await toolGate('gd', 'Die Gedächtniskiste'))) return;
      var me = null, cls = null;
      try { me = await DB.me(); cls = (await DB.listClasses()).filter(function (c) { return c.id === cid; })[0] || null; } catch (e) {}
      window.knGd = {
        className: cls ? cls.name : '', admin: !!(me && me.is_admin),
        back: function () { location.hash = '#/'; },
        games: async function () {
          var r = await Promise.all([DB.listGames(), cls ? DB.listReleases(cid) : Promise.resolve([])]), rel = new Set(r[1]);
          return r[0].filter(function (g) { return g.fach === 'Gedächtnis'; }).map(function (g) { return { id: g.id, title: g.title, on: rel.has(g.id) }; });
        },
        rel: function (id, on) { if (!cls) return Promise.reject(new Error('Keine Klasse')); return DB.setRelease(cid, id, !!on); },
        // Nur Admin: fehlende Spiele anlegen, vorhandene (gleicher Titel) auf den Verweis umstellen. Fortschritt bleibt (gleiche Spiel-ID).
        install: async function (list) {
          if (!me || !me.is_admin) throw new Error('Nur für Admin');
          var have = {}, neu = 0, upd = 0;
          (await DB.listGames()).forEach(function (g) { have[g.title.toLowerCase()] = g; });
          for (var i = 0; i < list.length; i++) {
            var g = list[i], old = have[String(g.title).toLowerCase()];
            if (!g || !/^<!doctype html>/i.test(g.html || '') || !/knobelnest-url" content="gedaechtnis\//.test(g.html)) continue;
            if (old) { await DB.saveGame({ id: old.id, title: old.title, description: old.description, fach: old.fach, thema: old.thema, stufe: old.stufe, for_all: old.for_all, sort: old.sort, html: g.html }); upd++; }
            else { await DB.saveGame({ title: String(g.title).slice(0, 80), description: String(g.description || '').slice(0, 160), fach: 'Gedächtnis', thema: String(g.thema || 'Allgemein').slice(0, 60), stufe: String(g.stufe || '').slice(0, 30), for_all: false, sort: +g.sort || 0, html: g.html }); neu++; }
          }
          try { T.games = await DB.listGames(); } catch (e) {}
          return { neu: neu, aktualisiert: upd };
        }
      };
      paint('<div class="folie"><iframe src="gedaechtnis/index.html?v=' + GD_VER + '" title="Gedächtniskiste" allow="fullscreen"></iframe></div>');
    }
  };
  var OTTER_VER = '8';
  // Ein gemeinsamer Speicher pro Klasse für den Otterteich und den Teich in der Tagesfolie («otter-<Klasse>»):
  // Einstellungen + «run» (Stand des Teichs). Der Stand wird hier im Portal gemerkt und gebündelt gespeichert.
  var OTTER_CACHE = {};
  function otterBridge(cid, roster, back) {
    var c = OTTER_CACHE[cid] || (OTTER_CACHE[cid] = { doc: null, t: null });
    function flush() {
      clearTimeout(c.t); c.t = null;
      if (!c.doc) return Promise.resolve();
      return DB.storeSet('otter-' + cid, JSON.parse(JSON.stringify(c.doc))).catch(function () {});
    }
    function later(ms) { if (!c.t) c.t = setTimeout(flush, ms); }
    return {
      key: cid, roster: roster, back: back, flush: flush,
      load: async function () {
        var d = null; try { d = await DB.storeGet('otter-' + cid); } catch (e) { d = null; }
        d = (d && typeof d === 'object') ? d : {};
        if (c.doc && c.doc.run && (!d.run || (c.doc.run.at || 0) > (d.run.at || 0))) d.run = c.doc.run;
        var had = !!Object.keys(d).length;
        c.doc = d;
        return had ? JSON.parse(JSON.stringify(d)) : null;
      },
      save: function (v) { c.doc = Object.assign(c.doc || {}, v); clearTimeout(c.t); c.t = null; later(1200); return Promise.resolve(); },
      keepRun: function (r) { c.doc = c.doc || {}; c.doc.run = r; later(15000); }
    };
  }
  window.addEventListener('pagehide', function () { Object.keys(OTTER_CACHE).forEach(function (k) { var c = OTTER_CACHE[k]; if (c.t && c.doc) { clearTimeout(c.t); c.t = null; DB.storeSet('otter-' + k, JSON.parse(JSON.stringify(c.doc))).catch(function () {}); } }); });
  var O = {
    start: async function (cid) {
      UI.view = 'otter';
      var s = await DB.session();
      if (!s) { location.hash = '#/'; return; }
      if (!(await toolGate('otter', 'Der Otterteich'))) return;
      app.innerHTML = '<p class="boot">Otterteich wird geladen …</p>';
      var cls, kids;
      try { cls = (await DB.listClasses()).filter(function (c) { return c.id === cid; })[0]; kids = await DB.listKids(cid); } catch (e) { cls = null; }
      if (!cls) { paint('<div class="main"><div class="card stack"><h2>Otterteich nicht verfügbar</h2><p>Diese Klasse wurde nicht gefunden.</p><a class="btn" href="#/">Zum Portal</a></div></div>'); return; }
      window.knOtter = otterBridge(cid, (kids || []).slice().sort(kidSort).map(function (k) { return k.name; }), function () { location.hash = '#/'; });
      paint('<div class="folie"><iframe src="otterteich.html?v=' + OTTER_VER + '" title="Otterteich" allow="microphone; fullscreen; autoplay; screen-wake-lock"></iframe></div>');
    }
  };
  // ===================================================================
  // Live-Quiz: eigene Seite quiz.html. Lehrperson: Quiz bauen und live spielen (Route #/quiz).
  // Mitspielen ohne Konto über QR-Code (Route #/q/<Nummer>). Speicher: teacher_store «quiz» (Liste) und «quiz-<id>».
  // ===================================================================
  var QUIZ_VER = '7';
  function quizJoinUrl(pin) { return location.origin + location.pathname + '#/q' + (pin ? '/' + pin : ''); }
  var QZ = {
    start: async function () {
      UI.view = 'quiz';
      var s = await DB.session();
      if (!s) { location.hash = '#/'; return; }
      if (!(await toolGate('quiz', 'Das Live-Quiz'))) return;
      window.knQuiz = {
        mode: 'teacher',
        back: function () { location.hash = '#/'; },
        // «quiz» = { list: [{id, titel, n, at, ordner}], ordner: [{id, name}] }
        list: async function () { var d = await DB.storeGet('quiz'); return { list: (d && Array.isArray(d.list)) ? d.list : [], ordner: (d && Array.isArray(d.ordner)) ? d.ordner : [] }; },
        saveList: function (doc) { return DB.storeSet('quiz', JSON.parse(JSON.stringify(doc))); },
        // Kinder-Quiz (Version 24): pro Klasse einschalten, Gruppen festlegen, mitbearbeiten
        kidClasses: async function () {
          var cl = await DB.listClasses(), out = [];
          for (var i = 0; i < cl.length; i++) { var ks = await DB.listKids(cl[i].id);
            out.push({ id: cl[i].id, name: cl[i].name, on: !!(cl[i].kid_tools && cl[i].kid_tools.quiz === true), kids: ks.slice().sort(kidSort).map(function (k) { return { id: k.id, name: k.name }; }) }); }
          return out;
        },
        kidToggle: async function (cid, on) {
          var c = (await DB.listClasses()).filter(function (x) { return x.id === cid; })[0]; if (!c) throw new Error('Klasse nicht gefunden');
          var kt = Object.assign({}, c.kid_tools || {}); kt.quiz = !!on; await DB.updateClass(cid, { kid_tools: kt });
        },
        kidList: function () { return DB.kqList(); },
        kidGet: function (id, ver) { return DB.kqGet(id, ver); },
        kidSave: function (id, ver, title, data) { return DB.kqSave(id, ver, title, JSON.parse(JSON.stringify(data))); },
        kidNew: function (cid, members, title) { return DB.kqNew(cid, members, title); },
        kidMembers: function (id, members) { return DB.kqMembers(id, members); },
        kidDelete: function (id) { return DB.kqDelete(id); },
        load: function (id) { return DB.storeGet('quiz-' + id); },
        save: function (id, q) { return DB.storeSet('quiz-' + id, JSON.parse(JSON.stringify(q))); },
        remove: function (id) { return DB.storeDel('quiz-' + id); },
        open: function (title, qs) { return DB.quizOpen(String(title || ''), JSON.parse(JSON.stringify(qs))); },
        step: function (id, phase, q) { return DB.quizStep(id, phase, q); },
        host: function (id) { return DB.quizHost(id); },
        kick: function (id, pid) { return DB.quizKick(id, pid); },
        close: function (id) { return DB.quizClose(id); },
        joinUrl: quizJoinUrl,
        qr: qrSvg
      };
      paint('<div class="folie"><iframe src="quiz.html?v=' + QUIZ_VER + '" title="Live-Quiz" allow="fullscreen; clipboard-write"></iframe></div>');
    },
    play: function (pin) {
      UI.view = 'quizplay';
      var k = LS.get('kn_kid');
      window.knQuiz = {
        mode: 'player', pin: pin, name: (k && k.exp > Date.now() && k.name) || '',
        home: function () { location.hash = '#/klasse'; },
        join: function (p, n, av) { return DB.quizJoin(p, n, av); },
        state: function (t) { return DB.quizState(t); },
        answer: function (t, q, a) { return DB.quizAnswer(t, q, a); }
      };
      paint('<div class="folie"><iframe src="quiz.html?v=' + QUIZ_VER + '" title="Quiz mitspielen" allow="fullscreen"></iframe></div>');
    }
  };
  ACT.wallFull = function () { if (document.documentElement.requestFullscreen) document.documentElement.requestFullscreen(); };

  // ===================================================================
  // Lehrpersonen
  // ===================================================================
  var T = {
    me: null, tools: {}, classes: [], cls: null, games: [], rel: new Set(), kids: [], subjects: [],
    progress: null, progressBusy: false, tafel: null, tafelBusy: false,
    tab: LS.get('kn_tab') || 'uebersicht', fach: 'alle', closed: LS.get('kn_closed') || {}, q: '', pfilter: 'alle',
    fresh: new Set(), editColor: null, newColor: '#2E7D4F', loginErr: '', loginInfo: '',
    admin: { teachers: null, tg: [], open: null, form: null }
  };

  T.start = async function () {
    UI.view = 'teacher';
    var s = await DB.session();
    if (!s) return T.renderLogin();
    app.innerHTML = '<p class="boot">Wird geladen …</p>';
    T.me = await DB.me();
    if (licExpired(T.me)) return licPage(T.me);
    T.tools = await toolAccess(T.me);
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
    setTafelCols((T.cur() || {}).tafel_cols);
  };
  T.cur = function () { return T.classes.filter(function (c) { return c.id === T.cls; })[0] || null; };

  T.renderLogin = function () {
    document.body.classList.add('lp');
    UI.view = 'login';
    paint('<div class="login"><section class="login-hero"><a class="marke" href="#/"><span class="marke-bild"><img src="bilder/eule.webp" alt="" width="60" height="60"></span><span class="marke-text"><b>' + markeName() + '<i aria-hidden="true">✦</i></b><small>für Lehrpersonen</small></span></a>' +
      '<div class="stack" style="gap:16px"><span class="login-klein">Für Ihren Schulalltag ✦</span><h1>Lernspiele und Werkzeuge an einem Ort.</h1>' +
      '<p>Lernspiele freigeben, den Fortschritt der Kinder sehen und Ihre Klassenwerkzeuge nutzen. Alles in einer Klassenkiste, damit Sie nur noch ein Tool brauchen.</p></div>' +
      '<div class="login-tools">' + LOGIN_TOOLS.map(function (t) {
        return '<div class="ltool" tabindex="0"><img src="bilder/kacheln/' + t[0] + '.webp" alt="" width="84" height="84"><b>' + t[1] + '</b><span class="ltip" role="tooltip">' + t[2] + '</span></div>'; }).join('') + '</div>' +
      '<a class="kidlink" href="#/klasse">' + ic(I.play, 22) + '<span>Für Kinder: Hier geht\'s zum Klassen-Login</span></a></section>' +
      '<section class="login-form"><form data-a="login" class="stack"><div class="stack" style="gap:8px"><h2 style="font-size:34px">Anmelden</h2>' +
      '<p class="muted">Für Lehrpersonen mit Zugang zur ' + h(C.PORTAL_NAME) + '.</p></div>' +
      '<div class="field"><label for="lgMail">E-Mail</label><input class="input" id="lgMail" name="email" type="email" autocomplete="username" value="' + h(T.loginEmail || '') + '" required></div>' +
      '<div class="field"><label for="lgPw">Passwort</label><input class="input" id="lgPw" name="pw" type="password" autocomplete="current-password" required></div>' +
      '<p class="err">' + h(T.loginErr) + '</p>' +
      '<button class="btn primary" style="min-height:54px;font-size:18px">Anmelden</button>' +
      '<button type="button" class="btn" data-a="forgot">Passwort vergessen?</button>' +
      (T.loginInfo ? '<p class="note">' + h(T.loginInfo) + '</p>' : '') +
      '<div class="login-shop"><span>Noch kein Login?</span>' + (C.SHOP_URL ? '<a class="btn amber" href="' + h(C.SHOP_URL) + '" target="_blank" rel="noopener">✦ Hol dir hier deinen Zugang</a>' : '<button type="button" class="btn amber" data-a="shopSoon">✦ Hol dir hier deinen Zugang</button>') + '</div>' +
      '</form></section></div>');
  };
  var LOGIN_TOOLS = [
    ['tagesfolie', 'Tagesfolie', 'Der Tag an der Wandtafel: Ablauf, Timer, Stundenplan, Zufallsname und mehr.'],
    ['vokabelkiste', 'Vokabelkiste', 'Wörter üben mit Karteikasten, Spielen, Tagessternen und Fortschritt pro Kind.'],
    ['hausaufgaben', 'Hausaufgabenheft', 'Aufgaben eintragen und kontrollieren, Berichte drucken. Die Kinder sehen alles am iPad.'],
    ['arbeitsstand', 'Arbeitsstand', 'Wer kann helfen, wer hat eine Frage? Live an der Wandtafel.'],
    ['pinnwand', 'Pinnwand', 'Ideen sammeln und gemeinsam abstimmen.'],
    ['umfrage-kiste', 'Umfrage', 'Abstimmen, Wortwolken, Quiz und Schätzfragen. Die Kinder antworten am iPad, das Ergebnis erscheint live.'],
    ['otterteich', 'Lautstärkeregler', 'Je leiser die Klasse, desto mehr Otter kommen an den Teich.']];
  ACT.shopSoon = function () { toast('Der Shop kommt bald. Melden Sie sich bis dahin bei ' + C.CONTACT + '.'); };
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
    if (licExpired(T.me)) return licPage(T.me);
    document.body.classList.add('lp');
    if (!T.me.name) return paint(T.onboardName());
    if (T.tab === 'verwaltung' && !T.me.is_admin) T.tab = 'spiele';
    if (T.tab === 'tafel' && !(T.tools && T.tools.tafel)) T.tab = 'uebersicht';
    var body;
    if (!T.classes.length && T.tab !== 'verwaltung') body = T.onboardClass();
    else body = ({ uebersicht: T.tabSpiele, spiele: T.tabSpiele, kinder: T.tabKinder, fortschritt: T.tabFortschritt, tafel: T.tabTafel, verwaltung: T.tabAdmin }[T.tab] || T.tabSpiele)();
    var left = licLeft(T.me);
    if (left !== null && left <= 30) body = '<div class="note row" style="justify-content:space-between;gap:12px"><span>✦ Ihre ' + h(C.PORTAL_NAME) + ' ist noch ' +
      (left === 0 ? 'bis heute' : 'bis am <b>' + h(dateCH(T.me.valid_until)) + '</b>') + ' gültig. Verlängern Sie rechtzeitig, damit Sie ohne Unterbruch weiterarbeiten können.</span>' + renewBtn('sm') + '</div>' + body;
    paint(T.shell(body));
  };
  T.shell = function (body) {
    var tabs = [['uebersicht', 'Übersicht'], ['spiele', 'Spiele'], ['kinder', 'Kinder'], ['fortschritt', 'Fortschritt']];
    if (T.tools && T.tools.tafel) tabs.push(['tafel', 'Arbeitsstand-Tafel']);
    if (T.me.is_admin) tabs.push(['verwaltung', 'Verwaltung']);
    return '<header class="top"><div class="top-in"><a class="marke" href="#/" data-a="tab" data-t="uebersicht" aria-label="' + h(C.PORTAL_NAME) + ' – Start"><span class="marke-bild"><img src="bilder/eule.webp" alt="" width="60" height="60"></span>' +
      '<span class="marke-text"><b>' + markeName() + '<i aria-hidden="true">✦</i></b><small>für Lehrpersonen</small></span></a><div class="row">' +
      (T.classes.length ? '<label class="sr" for="clsSel">Klasse wählen</label><select id="clsSel" class="input" style="min-height:44px;width:auto" data-change="pickClass">' +
        T.classes.map(function (c) { return '<option value="' + c.id + '"' + (c.id === T.cls ? ' selected' : '') + '>Klasse ' + h(c.name) + '</option>'; }).join('') + '</select>' : '') +
      '<button class="btn sm" data-a="account"><span class="avatar">' + h(initials(T.me.name)) + '</span>' + h(T.me.name) + '</button>' +
      '<button class="btn sm" data-a="logout">Abmelden</button></div></div>' +
      '<nav class="tabs" role="tablist">' + tabs.map(function (t) {
        return '<button class="tab" role="tab" aria-selected="' + (T.tab === t[0]) + '" data-a="tab" data-t="' + t[0] + '">' + t[1] + '</button>';
      }).join('') + '</nav></header><main class="main">' + body + '</main>';
  };
  // Schriftzug wie bei der Eulenkiste: erster Teil dunkel, «nest» gold
  function markeName() { var n = String(C.PORTAL_NAME || 'Knobelnest'), m = /^(.*?)(nest|kiste)$/i.exec(n); return m ? h(m[1]) + '<em>' + h(m[2]) + '</em>' : h(n); }
  ACT.tab = function (el) { T.tab = el.dataset.t; LS.set('kn_tab', T.tab); UI.confirm = null; T.render(); };
  ACT.pickClass = async function (el) { T.cls = el.value; LS.set('kn_cls', T.cls); await T.loadClass(); T.render(); };

  T.onboardName = function () {
    return '<main class="main" style="max-width:560px"><form class="card stack" data-a="saveName"><a class="marke" href="#/"><span class="marke-bild"><img src="bilder/eule.webp" alt="" width="60" height="60"></span><span class="marke-text"><b>' + markeName() + '<i aria-hidden="true">✦</i></b><small>für Lehrpersonen</small></span></a>' +
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
      '<div class="field"><label for="cCode">Klassencode (freiwillig)</label><input class="input" id="cCode" name="ccode" placeholder="z. B. Otter 123" maxlength="24" autocomplete="off">' +
      '<span class="muted small">Leer lassen, dann wählt die Klassenkiste einen Code. Sie können ihn später jederzeit ändern.</span></div>' +
      '<button class="btn primary">Klasse anlegen</button></form>';
  };
  var CODE_WORDS = ['FUCHS', 'DACHS', 'LUCHS', 'BIBER', 'IGEL', 'ADLER', 'EULE', 'OTTER', 'GEMSE', 'WOLF', 'HASE', 'FALKE', 'KAUZ', 'MARDER', 'SPATZ',
    'PANDA', 'KOALA', 'DELFIN', 'PINGUIN', 'ZEBRA', 'TIGER', 'KATZE', 'MAUS', 'ELCH', 'STORCH', 'RABE', 'SCHWAN', 'LAMA', 'WAL', 'MURMEL'];
  function genCode() { return CODE_WORDS[rnd(CODE_WORDS.length)] + ' ' + (100 + rnd(900)); }
  // ---------- Klassenbild (Maskottchen): Vorlagen der Admin-Lehrperson (shared_store «klassenbilder») oder eigenes Bild ----------
  function resizeImg(file, max) {
    return new Promise(function (res, rej) {
      if (!file || !/^image\//.test(file.type)) return rej(new Error('Bitte ein Bild wählen (JPG, PNG oder WebP).'));
      var r = new FileReader();
      r.onerror = function () { rej(new Error('Das Bild konnte nicht gelesen werden.')); };
      r.onload = function () {
        var im = new Image();
        im.onerror = function () { rej(new Error('Das Bild konnte nicht gelesen werden.')); };
        im.onload = function () {
          var k = Math.min(1, max / Math.max(im.width, im.height)), cv = document.createElement('canvas');
          cv.width = Math.max(1, Math.round(im.width * k)); cv.height = Math.max(1, Math.round(im.height * k));
          cv.getContext('2d').drawImage(im, 0, 0, cv.width, cv.height);
          var d = cv.toDataURL('image/webp', 0.86); if (!/^data:image\/webp/.test(d)) d = cv.toDataURL('image/png');
          if (d.length > 390000) d = cv.toDataURL('image/jpeg', 0.8);
          res(d);
        };
        im.src = r.result;
      };
      r.readAsDataURL(file);
    });
  }
  var BILDER = null;
  var TIERE = [['otter', 'Otter'], ['lama', 'Lamas'], ['igel', 'Igel'], ['giraffe', 'Giraffen'], ['panda', 'Pandas'], ['wal', 'Wale'], ['faultier', 'Faultiere']]; // Bilder in bilder/maskottchen/
  ACT.bildTier = async function (el) {
    try { var r = await fetch('bilder/maskottchen/' + el.dataset.f + '.webp'); var d = await resizeImg(await r.blob(), 320); await saveBild(d); }
    catch (e) { toast('Das Bild konnte nicht geladen werden.'); }
  };
  ACT.bildEdit = async function () {
    var c = T.cur(); if (!c) return;
    if (BILDER === null) { try { BILDER = (await DB.sharedGet('klassenbilder')) || []; } catch (e) { BILDER = []; } }
    var list = (Array.isArray(BILDER) ? BILDER : []).filter(function (b) { return b && /^data:image\//.test(b.src || ''); });
    overlay('<div class="dialog stack" role="dialog" aria-label="Klassenbild wählen" style="width:min(720px,100%)"><div class="row" style="justify-content:space-between"><h2 style="font-size:30px">Klassenbild wählen</h2><button class="btn sm" data-a="closeOverlay">Schliessen</button></div>' +
      '<p class="muted">Das Bild erscheint hier und bei den Kindern, wenn sie sich anmelden.</p>' +
      '<div class="bildwahl"><button class="bildopt' + (!c.bild ? ' on' : '') + '" data-a="bildPick" data-i="-1"><img src="bilder/klassenkiste.webp" alt=""><span>Eulen</span></button>' +
      TIERE.map(function (t) { return '<button class="bildopt" data-a="bildTier" data-f="' + t[0] + '"><img src="bilder/maskottchen/' + t[0] + '.webp" alt=""><span>' + t[1] + '</span></button>'; }).join('') +
      list.map(function (b, i) { return '<button class="bildopt' + (c.bild === b.src ? ' on' : '') + '" data-a="bildPick" data-i="' + i + '"><img src="' + h(b.src) + '" alt=""><span>' + h(b.name || 'Maskottchen') + '</span></button>'; }).join('') +
      (c.bild && !list.some(function (b) { return b.src === c.bild; }) ? '<span class="bildopt on"><img src="' + h(c.bild) + '" alt=""><span>Eigenes Bild</span></span>' : '') + '</div>' +
      '<div class="field"><label for="bildFile">Eigenes Bild hochladen</label><input class="input" id="bildFile" type="file" accept="image/*" data-change="bildFile"><span class="muted small">Am besten quadratisch. Es wird automatisch verkleinert. Keine Fotos von Kindern.</span></div>' +
      '<a class="insta-wunsch" href="https://www.instagram.com/primarschuleulchen/" target="_blank" rel="noopener noreferrer"><span class="insta-sym" aria-hidden="true"><svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="#fff" stroke="none"/></svg></span>' +
      '<span><b>Dein Tier fehlt?</b><small>Schreib mir auf Instagram, dann füge ich es hinzu → @primarschuleulchen</small></span></a></div>');
  };
  async function saveBild(src) {
    var c = T.cur();
    try { await DB.updateClass(c.id, { bild: src }); } catch (e) { return toast(sqlHint(e)); }
    c.bild = src; closeOverlays(); toast('Klassenbild gespeichert.'); T.render();
  }
  ACT.bildPick = function (el) { var i = +el.dataset.i; if (i < 0) return saveBild(null); var b = (BILDER || [])[i]; if (b) return saveBild(b.src); };
  ACT.bildFile = async function (el) { var f = el.files && el.files[0]; if (!f) return; try { var d = await resizeImg(f, 320); await saveBild(d); } catch (e) { toast(e.message); } };
  // Verwaltung: Vorlagen für Klassenbilder
  ACT.kbAdd = async function (el) {
    var A = T.admin, files = Array.prototype.slice.call(el.files || []); if (!files.length) return;
    var list = (A.kb || []).slice();
    for (var i = 0; i < files.length; i++) {
      try { list.push({ id: Math.random().toString(36).slice(2, 10), name: files[i].name.replace(/\.[^.]+$/, '').slice(0, 30), src: await resizeImg(files[i], 320) }); }
      catch (e) { toast(e.message); }
    }
    try { await DB.sharedSet('klassenbilder', list); A.kb = list; BILDER = list; toast('Vorlagen gespeichert.'); } catch (e) { toast(errMsg(e)); }
    T.render();
  };
  ACT.kbDel = async function (el) {
    var A = T.admin, list = (A.kb || []).filter(function (b) { return b.id !== el.dataset.id; });
    try { await DB.sharedSet('klassenbilder', list); A.kb = list; BILDER = list; } catch (e) { toast(errMsg(e)); }
    T.render();
  };
  ACT.kbName = async function (el) {
    var A = T.admin, b = (A.kb || []).filter(function (x) { return x.id === el.dataset.id; })[0]; if (!b) return;
    b.name = String(el.value || '').trim().slice(0, 30);
    try { await DB.sharedSet('klassenbilder', A.kb); BILDER = A.kb; } catch (e) { toast(errMsg(e)); }
  };
  // Eigener Klassencode, z. B. «Otter 123»: Buchstaben, Zahlen, Leerzeichen; die Kinder müssen Gross/klein und Leerzeichen nicht beachten
  function cleanCode(v) { return String(v || '').replace(/\s+/g, ' ').trim(); }
  function codeProblem(v) {
    if (!v) return 'Bitte einen Klassencode eingeben.';
    if (!/^[A-Za-zÄÖÜäöüÉÈÀéèàÇç0-9 ]+$/.test(v)) return 'Nur Buchstaben, Zahlen und Leerzeichen, z. B. «Otter 123».';
    if (v.replace(/\s/g, '').length < 4) return 'Der Code braucht mindestens 4 Zeichen.';
    if (v.length > 24) return 'Der Code darf höchstens 24 Zeichen lang sein.';
    return '';
  }
  function codeTaken(e) { return /classes_code|duplicate/i.test((e && e.message) || ''); }
  ACT.codeEdit = function () {
    var c = T.cur(); if (!c) return;
    overlay('<form class="dialog stack" role="dialog" aria-label="Klassencode wählen" data-a="codeSave"><h2 style="font-size:30px">Klassencode wählen</h2>' +
      '<p class="muted">Mit diesem Code melden sich die Kinder der Klasse ' + h(c.name) + ' an. Zum Beispiel «Otter 123». Gross- und Kleinschreibung und Leerzeichen müssen die Kinder nicht beachten.</p>' +
      '<div class="field"><label for="codeIn">Klassencode</label><input class="input codein" id="codeIn" name="code" value="' + h(c.code) + '" maxlength="24" autocomplete="off" required></div>' +
      '<p class="muted small" style="margin:0">Mit einem neuen Code funktioniert der alte nicht mehr. Angemeldete Kinder bleiben angemeldet.</p>' +
      '<div class="row" style="justify-content:space-between"><button type="button" class="btn" data-a="codeRandom">🎲 Zufälligen Code vorschlagen</button>' +
      '<span class="row"><button type="button" class="btn" data-a="closeOverlay">Abbrechen</button><button class="btn primary">Speichern</button></span></div></form>');
    var i = document.getElementById('codeIn'); if (i) { i.focus(); i.select(); }
  };
  ACT.codeRandom = function () { var i = document.getElementById('codeIn'); if (i) { var w = genCode().split(' '); i.value = w[0].charAt(0) + w[0].slice(1).toLowerCase() + ' ' + w[1]; i.focus(); } };
  ACT.codeSave = async function (f) {
    var c = T.cur(), v = cleanCode(f.elements.code.value), why = codeProblem(v);
    if (why) return toast(why);
    if (v === c.code) return closeOverlays();
    try { await DB.updateClass(c.id, { code: v }); }
    catch (e) { if (codeTaken(e)) return toast('Diesen Code hat schon eine andere Klasse. Bitte einen anderen wählen.'); throw e; }
    c.code = v; closeOverlays(); toast('Neuer Klassencode: ' + v); T.render();
  };
  async function withFreeCode(fn) {
    for (var i = 0; i < 8; i++) {
      try { return await fn(genCode()); }
      catch (e) { if (!/classes_code/.test(e.message)) throw e; }
    }
    throw new Error('Kein freier Klassencode gefunden. Bitte nochmals versuchen.');
  }
  ACT.createClass = async function (f) {
    var name = f.elements.cname.value.trim(); if (!name) return;
    var own = f.elements.ccode ? cleanCode(f.elements.ccode.value) : '', c;
    if (own) {
      var why = codeProblem(own); if (why) return toast(why);
      try { c = await DB.createClass(name, own); }
      catch (e) { if (codeTaken(e)) return toast('Diesen Code hat schon eine andere Klasse. Bitte einen anderen wählen.'); throw e; }
    } else c = await withFreeCode(function (code) { return DB.createClass(name, code); });
    var d = [['Mathematik', '#2F5E9E'], ['Deutsch', '#8A4F7D'], ['Englisch', '#C0473C'], ['NMG', '#2E8B57']];
    for (var i = 0; i < d.length; i++) await DB.addSubject(c.id, { name: d[i][0], color: d[i][1], fav: true, active: true, sort: i });
    var shut = { heft: false, pin: false, atelier: false, tafel: false };
    try { await DB.updateClass(c.id, { kid_tools: shut }); c.kid_tools = shut; } catch (e) {}
    T.classes.push(c); T.cls = c.id; LS.set('kn_cls', c.id);
    await T.loadClass(); T.tab = 'kinder'; LS.set('kn_tab', 'kinder');
    closeOverlays(); toast('Klasse ' + name + ' angelegt. Code: ' + c.code); T.render();
  };

  // ---------- Spiele ----------
  function isNew(g) { return Date.now() - new Date(g.created_at).getTime() < 14 * 86400000; }
  T.tabSpiele = function () {
    var c = T.cur(), vkg = T.games.filter(isVok)[0], games = T.games.filter(function (g) { return !isVok(g); }).concat(liveGames());
    var released = T.games.filter(function (g) { return T.rel.has(g.id); }).length;
    var fachs = uniq(games.map(function (g) { return g.fach; }));
    if (T.fach !== 'alle' && fachs.indexOf(T.fach) < 0) T.fach = 'alle';
    var q = T.q.trim().toLowerCase();
    var shown = games.filter(function (g) {
      return (T.fach === 'alle' || g.fach === T.fach) && (!q || (g.title + ' ' + g.description + ' ' + g.thema + ' ' + g.fach).toLowerCase().indexOf(q) >= 0);
    });
    var out = '<section class="banner"><button class="banner-bild" data-a="bildEdit" title="Klassenbild ändern"><img src="' + h(klassBild(c.bild)) + '" alt="Klassenbild" width="150" height="150"><span class="bild-edit">✎ ändern</span></button><div class="stack banner-text" style="gap:8px;flex:1 1 320px"><span class="klein">Ihre Klasse</span><h2>Klasse ' + h(c.name) + '</h2>' +
      '<p>Die Kinder öffnen <b>' + h(shortUrl(kidUrl())) + '</b>, geben den Code ein, tippen auf ihren Namen und ihr Bildpasswort. Sie sehen nur die Spiele, die Sie freigeben.</p>' +
      '<p style="font-weight:700;color:var(--ink)">' + released + ' von ' + plural(T.games.length, 'Spiel', 'Spielen') + ' für die Klasse freigegeben</p></div>' +
      '<div class="row" style="gap:16px"><div class="codebox"><small>Klassencode</small><b>' + h(c.code) + '</b><button class="code-edit" data-a="codeEdit">✎ selbst wählen</button></div><div class="stack" style="gap:8px">' +
      '<button class="btn amber" data-a="showCode">Code gross zeigen</button><a class="btn" href="#/klasse" target="_blank" rel="noopener">Ansicht der Kinder</a>' +
      '</div></div>' + (function () {
        // [Freigabe-Schlüssel, Route, Symbol, Name, Text, Schlüssel für die Kinder (null = nur für die Lehrperson)]
        var t = [['folie', 'tagesfolie', '☀️', 'Tagesfolie', 'Der Tag an der Wandtafel', null], ['heft', 'hausaufgaben', '📒', 'Hausaufgabenheft', 'Aufgaben und Kontrollen', 'heft'],
          ['pin', 'pinnwand', '📌', 'Pinnwand', 'Ideen sammeln und abstimmen', 'pin'], ['otter', 'otterteich', '🦦', 'Otterteich', 'Leise sein mit den Ottern', null], ['atelier', 'atelier', '🚲', 'Atelier', 'Wer steht wo im Atelier', 'atelier'], ['quiz', 'quiz', '❓', 'Live-Quiz', 'Alle spielen gleichzeitig mit', null], ['gd', 'gedaechtnis', '🧠', 'Gedächtniskiste', '12 Spiele fürs Gedächtnis', 'spiele'], ['umfrage', 'umfrage', '📊', 'Umfrage', 'Fragen stellen, live abstimmen', 'live'],
          ['eltern', 'gespraeche', '🗓️', 'Elterngespräche', 'Termine mit den Eltern planen', null]]
          .filter(function (x) { return T.tools[x[0]]; });
        var foot = function (k) { if (!k) return '<span class="tt-only">Nur für Sie</span>'; if (k === 'live') return '<span class="tt-only">Die Kinder machen am iPad mit</span>'; if (k === 'spiele') return '<span class="tt-only">Vorschau · Spiele freigeben</span>'; var on = toolOn(c, k);
          return '<button class="tt-rel' + (on ? ' on' : '') + '" data-a="toolRel" data-k="' + k + '">' + (on ? '✓ Für die Klasse freigegeben' : 'Für die Klasse gesperrt · freigeben') + '</button>'; };
        var tafelTile = '<div class="tooltile tt-card"><button class="tt-open" data-a="tab" data-t="tafel">' + ttIcon('tafel', '🙋') + '<span><b>Arbeitsstand</b><small>Wer kann helfen, wer hat Fragen</small></span></button>' + foot('tafel') + '</div>';
        var vt = vkg ? '<div class="tooltile tt-card tt-vk"><button class="tt-open" data-a="vkOpen" data-id="' + vkg.id + '">' + ttIcon('vk', VK_SVG) + '<span><b>Vokabelkiste</b><small>Wörter, Freigaben und Fortschritt</small></span></button>' +
          '<button class="tt-rel' + (T.rel.has(vkg.id) ? ' on' : '') + '" data-a="rel" data-id="' + vkg.id + '">' + (T.rel.has(vkg.id) ? '✓ Für die Klasse freigegeben' : 'Für die Klasse gesperrt · freigeben') + '</button></div>' : '';
        var tiles = {};
        t.forEach(function (x) { tiles[x[0]] = '<div class="tooltile tt-card' + (x[0] === 'folie' ? ' tt-main' : '') + '" data-tile="' + x[0] + '"><a class="tt-open" href="#/' + x[1] + '/' + T.cls + '">' + ttIcon(x[0], x[2]) + '<span><b>' + x[3] + '</b><small>' + x[4] + '</small></span></a>' + (x[0] === 'quiz' ? '<span class="tt-only">Mitspielen per QR-Code</span>' : foot(x[5])) + '</div>'; });
        if (T.tools.tafel) tiles.tafel = tafelTile.replace('<div class="tooltile tt-card">', '<div class="tooltile tt-card" data-tile="tafel">');
        if (vt && T.tools.vk) tiles.vk = vt.replace('<div class="tooltile tt-card tt-vk">', '<div class="tooltile tt-card tt-vk" data-tile="vk">');
        var keys = tileOrder().filter(function (k) { return tiles[k]; });
        return '<div class="tooltiles">' + keys.map(function (k) { return tiles[k].replace(/<a class="tt-open"/, '<a draggable="false" class="tt-open"').replace(/<img /g, '<img draggable="false" '); }).join('') + '</div>' +
          '<p class="muted small tt-tipp">Tipp: Kacheln mit der Maus ziehen (am iPad kurz gedrückt halten), um die Reihenfolge zu ändern.</p>' + mehrTiles();
      })() + '</section>';
    // Reiter «Übersicht» = Klasse und Werkzeuge; Reiter «Spiele» = Fächer und Spiele
    if (T.tab === 'uebersicht') return out;
    out = '';
    if (!T.games.length) {
      return out + '<div class="empty">' + (T.me.is_admin ? 'Noch keine Spiele. Laden Sie Ihr erstes Spiel unter «Verwaltung» hoch.' :
        'Für Sie sind noch keine Spiele freigeschaltet. Melden Sie sich bei ' + h(C.CONTACT) + '.') + '</div>';
    }
    out += '<section class="stack"><h2 style="font-size:26px">Fächer</h2><div class="tiles">' +
      [{ id: 'alle', label: 'Alle Fächer', n: games.length, col: '#E3ECF5' }].concat(fachs.map(function (f) {
        return { id: f, label: f, n: games.filter(function (g) { return g.fach === f; }).length, col: fachColor(f) };
      })).map(function (t) {
        return '<button class="tile" aria-pressed="' + (T.fach === t.id) + '" data-a="fach" data-f="' + h(t.id) + '"><span class="sw' + (t.id !== 'alle' && fachBild(t.id) ? ' sw-bild' : '') + '" style="background:' + t.col + '">' +
          (t.id === 'alle' ? '★' : fachBild(t.id) || h(t.label.charAt(0))) + '</span><span><b' + (t.label.length > 13 ? ' style="font-size:' + (t.label.length > 17 ? 13 : 15) + 'px"' : '') + '>' + h(t.label) + '</b><span>' + plural(t.n, 'Spiel', 'Spiele') + '</span></span></button>';
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
        (real.length ? (function () { var all = real.every(function (g) { return T.rel.has(g.id); });
          return '<button class="btn sm" data-a="gRelAll" data-k="' + h(gk) + '" data-v="' + (all ? 0 : 1) + '">' + (all ? '🔒 Alle sperren' : '✓ Alle freigeben') + '</button>'; })() : '') +
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
            '<button class="btn" data-a="preview" data-id="' + g.id + '">' + ic(I.play, 14) + ' Selbst ansehen</button>') +
            (isZeit(g) ? '<button class="btn primary" data-a="zrOpen" data-id="' + g.id + '">🔓 Zeiten & Fortschritt</button>' : '') +
            (isVok(g) ? '<button class="btn primary" data-a="vkOpen" data-id="' + g.id + '">📚 Wörter & Freigaben</button>' : '') + '</div></div></article>';
        }).join('') + '</div>');
    });
    return out + '</section>';
  };
  ACT.fach = function (el) { T.fach = el.dataset.f; T.render(); };

  // ---------- Zeitreise: welche Zeiten offen sind, pro Klasse und pro Kind ----------
  // Neue Epochen hier auf ready: true setzen, sobald sie im Ordner zeitreise/ liegen.
  var ZR_ERAS = [
    { id: 'altsteinzeit', name: 'Altsteinzeit', icon: '🦣', ready: true },
    { id: 'jungsteinzeit', name: 'Jungsteinzeit', icon: '🌾', ready: true },
    { id: 'bronzezeit', name: 'Bronzezeit', icon: '🥉', ready: false },
    { id: 'eisenzeit', name: 'Eisenzeit', icon: '⚒️', ready: false },
    { id: 'roemerzeit', name: 'Römerzeit', icon: '🏛️', ready: false },
    { id: 'mittelalter', name: 'Mittelalter', icon: '🏰', ready: false }
  ];
  function isZeit(g) { return /zeitreise/i.test(g.title || ''); }
  var ZR = null;
  function zrNorm(c) {
    c = c && typeof c === 'object' ? c : {};
    return { open: Array.isArray(c.open) ? c.open : ['altsteinzeit'], pass: +c.pass || 7, auto: c.auto !== false, kids: c.kids && typeof c.kids === 'object' ? c.kids : {} };
  }
  function zrPassed(kid, era) { var z = ((ZR.aw[kid] || {}).zr || {})[era]; return !!z && z.best != null && z.best >= ZR.cfg.pass; }
  function zrWhy(kid, i) {
    var e = ZR_ERAS[i], c = ZR.cfg;
    if (!e.ready) return null;
    if (c.open.indexOf(e.id) >= 0) return 'klasse';
    if ((c.kids[kid] || []).indexOf(e.id) >= 0) return 'kind';
    if (c.auto && i > 0 && zrPassed(kid, ZR_ERAS[i - 1].id)) return 'quiz';
    return null;
  }
  ACT.zrOpen = async function (el) {
    var g = T.games.filter(function (x) { return x.id === el.dataset.id; })[0];
    toast('Wird geladen …');
    var both = await Promise.all([DB.gameSettingsGet(T.cls, g.id), DB.listProgressGame(T.kids.map(function (k) { return k.id; }), g.id)]);
    var aw = {}; (both[1] || []).forEach(function (r) { aw[r.kid_id] = r.award || {}; });
    ZR = { g: g, cfg: zrNorm(both[0]), aw: aw };
    overlay('<div class="card zr stack" role="dialog" aria-label="Zeitreise"></div>');
    zrRender();
  };
  function zrRender() {
    var box = document.querySelector('.overlay .zr'); if (!box || !ZR) return;
    var c = ZR.cfg, ready = ZR_ERAS.filter(function (e) { return e.ready; });
    var rows = T.kids.map(function (k) {
      return '<tr><th scope="row">' + h(k.name) + '</th>' + ready.map(function (e) {
        var i = ZR_ERAS.indexOf(e), why = zrWhy(k.id, i), z = ((ZR.aw[k.id] || {}).zr || {})[e.id];
        var info = z && (z.f || z.best != null) ? '<small>' + (z.t ? z.f + '/' + z.t + ' entdeckt' : z.f + ' entdeckt') + (z.best != null ? ' · Quiz ' + z.best + '/' + z.n + (z.best >= c.pass ? ' ✓' : '') : '') + '</small>' : '';
        var st = why === 'klasse' ? '<span class="zr-st open">offen</span>' :
          why === 'quiz' ? '<span class="zr-st open">🔓 durch Quiz</span>' :
          '<button class="zr-st ' + (why === 'kind' ? 'mine' : 'lock') + '" data-a="zrKid" data-k="' + k.id + '" data-e="' + e.id + '">' + (why === 'kind' ? '🔓 von Ihnen geöffnet' : '🔒 gesperrt · öffnen') + '</button>';
        return '<td>' + st + info + '</td>';
      }).join('') + '</tr>';
    }).join('');
    box.innerHTML = '<div class="row" style="justify-content:space-between"><h2 style="margin:0">' + h(ZR.g.title) + ' · Klasse ' + h(T.cur().name) + '</h2><button class="btn sm" data-a="closeOverlay">Schliessen</button></div>' +
      '<div><p class="h3" style="margin:0 0 6px">Für die ganze Klasse offen</p><div class="chips">' + ZR_ERAS.map(function (e) {
        return e.ready ? '<button class="chip" aria-pressed="' + (c.open.indexOf(e.id) >= 0) + '" data-a="zrEra" data-e="' + e.id + '">' + e.icon + ' ' + e.name + '</button>'
          : '<span class="chip" style="opacity:.45;cursor:default">' + e.icon + ' ' + e.name + ' · kommt bald</span>'; }).join('') + '</div></div>' +
      '<div class="row" style="align-items:center;gap:10px"><label class="row" style="gap:8px;flex-wrap:nowrap"><input type="checkbox" data-change="zrAuto" style="width:22px;height:22px"' + (c.auto ? ' checked' : '') + '> Nächste Zeit automatisch öffnen, wenn das Quiz mit mindestens</label>' +
      '<div class="chips">' + [6, 7, 8, 9, 10].map(function (n) { return '<button class="chip" style="min-height:36px;padding:0 12px" aria-pressed="' + (c.pass === n) + '" data-a="zrPass" data-n="' + n + '"' + (c.auto ? '' : ' disabled') + '>' + n + '</button>'; }).join('') + '</div><span>von 10 Punkten gelöst ist.</span></div>' +
      (T.kids.length ? '<div class="tablewrap"><table class="zr-table"><thead><tr><th>Kind</th>' + ready.map(function (e) { return '<th>' + e.icon + ' ' + e.name + '</th>'; }).join('') + '</tr></thead><tbody>' + rows + '</tbody></table></div>' :
        '<p class="muted">Noch keine Kinder in dieser Klasse.</p>') +
      '<p class="muted small" style="margin:0">Änderungen gelten, sobald ein Kind die Zeitreise das nächste Mal öffnet. «Entdeckt» zählt die Dinge im Forscherheft, beim Quiz steht das beste Ergebnis.</p>';
  }
  async function zrSave() {
    zrRender();
    try { await DB.gameSettingsSet(T.cls, ZR.g.id, ZR.cfg); } catch (e) { toast('Speichern ging nicht: ' + errMsg(e)); }
  }
  ACT.zrEra = function (el) { var o = ZR.cfg.open, i = o.indexOf(el.dataset.e); if (i >= 0) o.splice(i, 1); else o.push(el.dataset.e); return zrSave(); };
  ACT.zrAuto = function (el) { ZR.cfg.auto = el.checked; return zrSave(); };
  ACT.zrPass = function (el) { ZR.cfg.pass = +el.dataset.n; return zrSave(); };
  ACT.zrKid = function (el) {
    var k = el.dataset.k, e = el.dataset.e, l = ZR.cfg.kids[k] = ZR.cfg.kids[k] || [], i = l.indexOf(e);
    if (i >= 0) l.splice(i, 1); else l.push(e);
    if (!l.length) delete ZR.cfg.kids[k];
    return zrSave();
  };
  // ---------- Vokabelkiste: Wortlisten und Freigaben pro Klasse (game_settings: { content }) ----------
  function isVok(g) { return /vokabelkiste/i.test(g.title || ''); }
  // Nur die Vorlage-Portionen, die dieser Lehrperson zugeteilt sind
  function vkOnly(tpl, ids) {
    if (!tpl || !ids.length) return null;
    var keep = function (arr) { var out = []; (arr || []).forEach(function (n) { if (n.words) { if (ids.indexOf(n.id) >= 0) out.push(n); } else { var k = keep(n.kids); if (k.length) out.push({ id: n.id, name: n.name, kids: k }); } }); return out; };
    var subs = (tpl.subjects || []).map(function (sb) { return Object.assign({}, sb, { tree: keep(sb.tree) }); }).filter(function (sb) { return sb.tree.length; });
    return subs.length ? Object.assign({}, tpl, { subjects: subs }) : null;
  }
  // Vorlage aus den Wortlisten der Admin-Lehrperson: nur Portionen, die selbst oder über einen Ordner als Vorlage markiert sind
  function vkTemplate(content, cid) {
    var subs = [];
    (content.subjects || []).forEach(function (sb) {
      var prune = function (arr, inh) {
        var out = [];
        (arr || []).forEach(function (n) {
          var on = inh || !!n.tpl;
          if (n.words) { if (on) out.push({ id: n.id, name: n.name, words: n.words }); }
          else { var k = prune(n.kids, on); if (k.length) out.push({ id: n.id, name: n.name, kids: k }); }
        });
        return out;
      };
      var tr = prune(sb.tree, false);
      if (tr.length) subs.push({ id: sb.id, name: sb.name, lang: sb.lang, excl: sb.excl || [], tree: tr });
    });
    return { subjects: subs, by: (T.me && T.me.name) || '', from: cid, at: Date.now() };
  }
  // Tage mit «Ferien» oder «schulfrei» im Hausaufgabenheft (für die ganze Klasse)
  function vkFree(heft) {
    return ((heft && heft.entries) || []).filter(function (e) { return e && (e.type === 'ferien' || e.type === 'schulfrei') && (!Array.isArray(e.for) || !e.for.length) && /^\d{4}-\d{2}-\d{2}$/.test(e.date || ''); })
      .map(function (e) { return e.date; });
  }
  function isoDay(d) { return d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2); }
  // Serie wie in der Vokabelkiste: Schultage hintereinander mit Tagesstern (7 Minuten); Wochenende und Ferien zählen nicht
  function vkStreak(sec, free) {
    var d = new Date(); d.setHours(12, 0, 0, 0); var n = 0;
    for (var i = 0; i < 500; i++) {
      var w = d.getDay(), k = isoDay(d);
      if (w > 0 && w < 6 && !free[k]) { if ((sec[k] || 0) >= 420) n++; else if (i > 0) break; }
      d.setDate(d.getDate() - 1);
    }
    return n;
  }
  function vkHTML(a) {
    if (!a || !a.vk) return '';
    var sec = a.vk.sec || {}, free = T.vkFree || {}, st = vkStreak(sec, free), d = new Date(); d.setHours(12, 0, 0, 0);
    d.setDate(d.getDate() - ((d.getDay() + 6) % 7));
    var days = ['Mo', 'Di', 'Mi', 'Do', 'Fr'].map(function (n, i) {
      var x = new Date(d); x.setDate(d.getDate() + i); var k = isoDay(x), s = sec[k] || 0, m = Math.round(s / 60);
      return '<i class="' + (free[k] ? 'fr' : s >= 420 ? 'ok' : s ? 'part' : '') + '" title="' + n + ' ' + x.getDate() + '.' + (x.getMonth() + 1) + '.: ' + (free[k] ? 'schulfrei' : m + ' Min. geübt') + '"><small>' + n + '</small>' + (free[k] ? '–' : m) + '</i>';
    }).join('');
    return '<span class="vkx"><span class="small" style="font-weight:700">' + (st ? '🔥 ' + st + ' ' : '') + (a.vk.weeks ? '🏅' + (a.vk.weeks > 1 ? '×' + a.vk.weeks : '') + ' ' : '') + (a.vk.fach5 >= 100 ? '📦 ' : '') + '</span>' +
      '<span class="vkd" title="Minuten geübt in dieser Woche">' + days + '</span></span>';
  }
  ACT.vkOpen = async function (el) {
    var g = T.games.filter(function (x) { return x.id === el.dataset.id; })[0], cid = T.cls, c = T.cur();
    if (!g || !c) return toast('Bitte zuerst eine Klasse wählen.');
    toast('Vokabelkiste wird geladen …');
    var kids = T.kids.slice().sort(kidSort);
    var both = await Promise.all([DB.gameHtml(g.id), DB.gameSettingsGet(cid, g.id), DB.listProgressSaves(kids.map(function (k) { return k.id; }), g.id).catch(function () { return []; }),
      DB.storeGet('hat-' + cid).catch(function () { return null; }), DB.sharedGet('vokabelkiste-vorlage').catch(function () { return null; }),
      T.me.is_admin ? null : DB.sharedGet('vokabelkiste-zuweisung').catch(function () { return null; })]);
    var admin = !!T.me.is_admin, tpl = both[4] && typeof both[4] === 'object' ? both[4] : null;
    var mineTpl = admin ? null : vkOnly(tpl, ((both[5] || {})[T.me.id]) || []);
    var cfg = both[1] && typeof both[1] === 'object' ? both[1] : {}, sv = {};
    (both[2] || []).forEach(function (r) { sv[r.kid_id] = r; });
    var kidData = kids.map(function (k) { var r = sv[k.id] || {}; return { id: k.id, name: k.name, p: (r.save && r.save.p) || {}, last: r.last_played || null }; });
    openPlayer(g.title + ' · Klasse ' + c.name, both[0], function (d) {
      if (!d.knobelnest || d.type !== 'vkContent' || !d.content || !Array.isArray(d.content.subjects)) return;
      var reply = function (ok, err) { try { if (PL) PL.frame.contentWindow.postMessage({ vkAck: d.id, ok: ok, err: err || '' }, '*'); } catch (x) {} };
      if (JSON.stringify(d.content).length > 900000) return reply(false, 'zu gross');
      cfg = Object.assign({}, cfg, { content: d.content });
      var jobs = [DB.gameSettingsSet(cid, g.id, cfg)];
      // Admin: Vorlagen für die anderen Lehrpersonen mitspeichern (nur aus der Klasse, in der sie bearbeitet werden)
      if (admin) { var nt = vkTemplate(d.content, cid); if (nt.subjects.length || (tpl && tpl.from === cid)) { tpl = nt; jobs.push(DB.sharedSet('vokabelkiste-vorlage', nt)); } }
      Promise.all(jobs).then(function () { reply(true); }, function (e) { reply(false, errMsg(e)); toast('Speichern ging nicht: ' + errMsg(e)); });
    }, null, { settings: Object.assign({}, cfg, { frei: vkFree(both[3]), kids: kidData, tpl: mineTpl, tplOn: !admin && !!tpl }), teacher: true, edit: true, admin: admin });
  };
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
  // Bilder der Werkzeug-Kacheln (bilder/kacheln/), sonst das Symbol
  // Bilder für die Fächer (bilder/faecher/), sonst der Anfangsbuchstabe
  function fachBild(f) {
    var k = String(f || '').toLowerCase().replace(/[^a-zäöü]/g, '');
    var m = /^deutsch/.test(k) ? 'deutsch' : /^mathe/.test(k) ? 'mathematik' : /^englisch|^english/.test(k) ? 'englisch' : /^nmg|^natur|^mensch/.test(k) ? 'nmg' : '';
    return m ? '<img src="bilder/faecher/' + m + '.webp" alt="" draggable="false">' : '';
  }
  // Werkzeuge, die eine Lehrperson (noch) nicht hat: grau unten, mit Vorschau und «Hol es dir» (Bilder in bilder/vorschau/)
  var MEHR = [
    ['heft', '📒', 'Hausaufgabenheft', 'Aufgaben und Kontrollen', ['Aufgaben, Lernkontrollen und Termine für die ganze Woche', 'Die Kinder sehen alles am iPad und haken ab, was erledigt ist', 'Auf einen Blick: Wer hat was gemacht?', 'Berichte für Elterngespräche drucken']],
    ['tafel', '🙋', 'Arbeitsstand', 'Wer kann helfen, wer hat Fragen', ['Die Kinder zeigen am iPad, wo sie in jedem Fach stehen', 'Live an der Wandtafel: Wer kann helfen, wer hat eine Frage?', 'Eigene Spalten, Namen und Farben', 'Die Kinder helfen sich gegenseitig']],
    ['vk', '📦', 'Vokabelkiste', 'Wörter üben mit Karteikasten', ['Wörter üben mit Karteikasten, Schreiben und Spielen', 'Eigene Wortlisten, Portionen für die Klasse freigeben', 'Vorlesestimme für die richtige Aussprache', 'Tagessterne, Serien und Abzeichen motivieren', 'Übersicht pro Kind und pro Portion']],
    ['quiz', '❓', 'Live-Quiz', 'Alle spielen gleichzeitig mit', ['Fragen mit Auswahl, Richtig/Falsch, Text oder Reihenfolge', 'Die Kinder spielen per QR-Code am iPad mit', 'Punkte und Rangliste live an der Wandtafel', 'Quiz mit KI aus einem Arbeitsblatt erstellen', 'Die Kinder können auch eigene Quiz erstellen']],
    ['gd', '🧠', 'Gedächtniskiste', '12 Spiele fürs Gedächtnis', ['12 Spiele mit je 5 Stufen', 'Bilder, Orte, Reihenfolgen und Namen merken', 'Selbst ausprobieren, bevor die Klasse spielt', 'Pro Klasse freigeben, Fortschritt pro Kind']],
    ['umfrage', '📊', 'Umfrage', 'Fragen stellen, live abstimmen', ['Abstimmung, Wortwolke, Skala, Schätzfrage und mehr', 'Ergebnisse erscheinen live an der Wandtafel', 'Mit der Klasse oder offen per QR-Code (z. B. am Elternabend)', 'Fertige Vorlagen für Klassenrat, Wochenrückblick und mehr']],
    ['eltern', '🗓️', 'Elterngespräche', 'Termine mit den Eltern planen', ['Kein mühsames Terminfinden mehr: Die Eltern kreuzen per Link an, wann sie können (ohne Anmeldung)', 'Die Liste wird automatisch erstellt, und Termine werden blockiert, damit es am Schluss für alle aufgeht', 'Sie bekommen eine fix fertige Liste', 'Sie können auch selbst Termine fixieren', 'Anspruchsvolle Gespräche nicht direkt hintereinander']]];
  function mehrList() { return T.me && T.me.is_admin ? (T.mehrAdmin ? MEHR : []) : MEHR.filter(function (x) { return !T.tools[x[0]]; }); }
  function shopBtn(txt, cls) {
    return C.SHOP_URL ? '<a class="' + cls + '" href="' + h(C.SHOP_URL) + '" target="_blank" rel="noopener">' + txt + '</a>' : '<button type="button" class="' + cls + '" data-a="shopSoon">' + txt + '</button>';
  }
  function mehrTiles() {
    var l = mehrList(), adm = T.me && T.me.is_admin;
    // Admin hat alles: Knopf, um zu sehen, was andere Lehrpersonen ohne Freigabe sehen
    var knopf = adm ? '<div class="tt-mehr-admin"><button class="btn sm" data-a="mehrAdmin">' + (T.mehrAdmin ? '✕ Ansicht schliessen' : '👁 So sehen Lehrpersonen die Werkzeuge, die sie noch nicht haben') + '</button></div>' : '';
    if (!l.length) return knopf;
    return knopf + '<div class="tt-mehr-kopf"><h3>Noch mehr in der ' + h(C.PORTAL_NAME) + ' <span class="sterne" aria-hidden="true">✦ ✧ ✦</span></h3><p>Diese Werkzeuge können Sie dazuholen. In der Vorschau sehen Sie, was sie können.</p></div>' +
      '<div class="tooltiles tt-mehr">' + l.map(function (x) {
        return '<div class="tooltile tt-card tt-zu"><button class="tt-open" data-a="ttVorschau" data-k="' + x[0] + '">' + ttIcon(x[0], x[1]) + '<span><b>' + x[2] + '</b><small>' + x[3] + '</small></span><span class="tt-schloss" aria-hidden="true">🔒</span></button>' +
          '<div class="tt-zu-fuss"><button class="tt-vor" data-a="ttVorschau" data-k="' + x[0] + '">👁 Vorschau</button>' + shopBtn('✦ Hol es dir', 'tt-hol') + '</div></div>';
      }).join('') + '</div>';
  }
  ACT.mehrAdmin = function () { T.mehrAdmin = !T.mehrAdmin; T.render(); };
  ACT.ttVorschau = function (el) {
    var x = MEHR.filter(function (m) { return m[0] === el.dataset.k; })[0]; if (!x) return;
    overlay('<div class="tt-vorschau" role="dialog" aria-label="Vorschau ' + x[2] + '"><div class="tt-v-kopf">' + ttIcon(x[0], x[1]) + '<div><span class="klein">Vorschau</span><h2>' + x[2] + '</h2><p>' + x[3] + '</p></div></div>' +
      '<img class="tt-v-bild" src="bilder/vorschau/' + x[0] + '.webp" alt="So sieht ' + x[2] + ' aus" onerror="this.remove()">' +
      '<ul class="tt-v-liste">' + x[4].map(function (f) { return '<li>' + f + '</li>'; }).join('') + '</ul>' +
      '<div class="row" style="justify-content:flex-end;gap:10px"><button class="btn" data-a="closeOverlay">Schliessen</button>' + shopBtn('✦ Hol es dir', 'btn amber') + '</div></div>');
  };
  var KACHEL_BILD = { folie: 'tagesfolie', heft: 'hausaufgaben', pin: 'pinnwand', otter: 'otterteich', atelier: 'atelier', tafel: 'arbeitsstand', vk: 'vokabelkiste', quiz: 'live-quiz', umfrage: 'umfrage-kiste', eltern: 'eltern' };
  function ttIcon(k, sym) { return KACHEL_BILD[k] ? '<span class="tti bild" aria-hidden="true"><img src="bilder/kacheln/' + KACHEL_BILD[k] + '.webp" alt="" width="96" height="96"></span>' : '<span class="tti" aria-hidden="true">' + sym + '</span>'; }
  // Reihenfolge der Werkzeug-Kacheln pro Lehrperson (teacher_store «kacheln»), zuerst die Werkzeuge nur für die Lehrperson
  var TILE_DEF = ['folie', 'otter', 'quiz', 'heft', 'pin', 'atelier', 'umfrage', 'tafel', 'vk', 'gd', 'eltern'];
  function tileOrder() {
    if (!T.tileLoaded) {
      T.tileLoaded = true; T.tileOrderList = LS.get('kn_kacheln') || null;
      DB.storeGet('kacheln').then(function (d) { if (d && Array.isArray(d.order)) { T.tileOrderList = d.order; LS.set('kn_kacheln', d.order); if (T.tab === 'uebersicht') T.render(); } }).catch(function () {});
    }
    var o = (T.tileOrderList || []).filter(function (k) { return TILE_DEF.indexOf(k) >= 0; });
    TILE_DEF.forEach(function (k) { if (o.indexOf(k) < 0) o.push(k); });
    return o;
  }
  function saveTileOrder(o) { T.tileOrderList = o; LS.set('kn_kacheln', o); T.render(); DB.storeSet('kacheln', { order: o }).catch(function () {}); }
  // Kacheln direkt ziehen (Maus sofort, Finger nach kurzem Halten). Ein Tippen öffnet weiterhin das Werkzeug.
  var TD = null;
  function tdEnd(save) {
    if (!TD) return; var d = TD; TD = null; clearTimeout(d.hold);
    document.removeEventListener('pointermove', tdMove, true); document.removeEventListener('pointerup', tdUp, true); document.removeEventListener('pointercancel', tdCancel, true);
    if (!d.on) return;
    d.el.classList.remove('dragging'); d.el.style.transform = ''; document.body.classList.remove('tt-dragging');
    window.__ttNoClick = Date.now();
    if (save) { var o = tileOrder(), shown = Array.prototype.map.call(document.querySelectorAll('.tooltiles [data-tile]'), function (x) { return x.dataset.tile; });
      var rest = o.filter(function (k) { return shown.indexOf(k) < 0; }); saveTileOrder(shown.concat(rest)); }
    else T.render();
  }
  function tdStart() { if (!TD) return; TD.on = true; TD.el.classList.add('dragging'); document.body.classList.add('tt-dragging'); }
  function tdMove(e) {
    var d = TD; if (!d) return;
    var dx = e.clientX - d.x, dy = e.clientY - d.y;
    if (!d.on) { if (Math.abs(dx) + Math.abs(dy) > 8) { if (d.touch) return tdEnd(false); tdStart(); } else return; }
    e.preventDefault();
    d.el.style.transform = 'translate(' + (e.clientX - d.x) + 'px,' + (e.clientY - d.y) + 'px) scale(1.04)';
    var over = document.elementsFromPoint(e.clientX, e.clientY).map(function (x) { return x.closest && x.closest('.tooltiles [data-tile]'); }).filter(function (x) { return x && x !== d.el; })[0];
    var t = over; if (!t) return;
    var grid = d.el.parentNode, list = Array.prototype.slice.call(grid.children), i = list.indexOf(d.el), j = list.indexOf(t);
    var r0 = d.el.getBoundingClientRect();
    grid.insertBefore(d.el, i < j ? t.nextSibling : t);
    var r1 = d.el.getBoundingClientRect(); d.x += r1.left - r0.left; d.y += r1.top - r0.top;
    d.el.style.transform = 'translate(' + (e.clientX - d.x) + 'px,' + (e.clientY - d.y) + 'px) scale(1.04)';
  }
  function tdUp() { tdEnd(true); }
  function tdCancel() { tdEnd(false); }
  document.addEventListener('pointerdown', function (e) {
    if (e.button || UI.view === 'kid') return;
    var t = e.target.closest && e.target.closest('.tooltiles [data-tile]'); if (!t || e.target.closest('.tt-rel')) return;
    TD = { el: t, x: e.clientX, y: e.clientY, on: false, touch: e.pointerType !== 'mouse' };
    if (TD.touch) TD.hold = setTimeout(tdStart, 380);
    document.addEventListener('pointermove', tdMove, true); document.addEventListener('pointerup', tdUp, true); document.addEventListener('pointercancel', tdCancel, true);
  });
  document.addEventListener('click', function (e) { if (window.__ttNoClick && Date.now() - window.__ttNoClick < 400 && e.target.closest && e.target.closest('.tooltiles')) { e.preventDefault(); e.stopPropagation(); } }, true);
  document.addEventListener('dragstart', function (e) { if (e.target.closest && e.target.closest('.tooltiles')) e.preventDefault(); });
  ACT.toolRel = async function (el) {
    var c = T.cur(), k = el.dataset.k, kt = Object.assign({}, c.kid_tools || {}), before = c.kid_tools;
    kt[k] = !toolOn(c, k); c.kid_tools = kt; T.render();
    try { await DB.updateClass(c.id, { kid_tools: kt }); toast(kt[k] ? 'Für die Klasse freigegeben.' : 'Für die Klasse gesperrt.'); }
    catch (e) { c.kid_tools = before; T.render(); toast(sqlHint(e)); }
  };
  ACT.gRelAll = async function (el) {
    var on = el.dataset.v === '1', k = el.dataset.k;
    var ids = T.games.filter(function (g) { return g.fach + '|' + g.thema === k && T.rel.has(g.id) !== on; }).map(function (g) { return g.id; });
    ids.forEach(function (id) { if (on) T.rel.add(id); else T.rel.delete(id); });
    T.render();
    try { for (var i = 0; i < ids.length; i++) await DB.setRelease(T.cls, ids[i], on); toast(on ? ids.length + ' Spiele freigegeben' : ids.length + ' Spiele gesperrt'); }
    catch (e) { T.rel = new Set(await DB.listReleases(T.cls)); T.render(); throw e; }
  };
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
      return '<li class="' + (T.fresh.has(k.id) ? 'fresh' : '') + '"><input class="kidnr" style="background:' + kidColor(k.name) + '" inputmode="numeric" maxlength="3" autocomplete="off" value="' + (k.nr != null ? k.nr : '') + '" placeholder="' + h(k.name.charAt(0)) + '" title="Nummer (freiwillig)" aria-label="Nummer von ' + h(k.name) + ' (freiwillig)" data-change="kidNr" data-id="' + k.id + '">' +
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
      '<div class="field"><label for="kidName">Vorname oder Spitzname</label><input class="input" id="kidName" name="name" maxlength="30" placeholder="z. B. Mila oder 12 Mila" required></div>' +
      '<button class="btn primary">Hinzufügen</button></form>' +
      '<form class="card stack" data-a="addBulk"><h2 style="font-size:22px">Ganze Klasse auf einmal</h2>' +
      '<div class="field"><label for="kidBulk">Ein Name pro Zeile</label><textarea class="input" id="kidBulk" name="list" rows="6" placeholder="Mila&#10;Tim&#10;Aylin&#10;oder mit Nummer: 1 Mila"></textarea></div>' +
      '<button class="btn">Alle hinzufügen</button><p class="muted small">Tipp: Namensliste aus Excel kopieren und hier einfügen. Mit Nummer davor («12 Mila») wird die Liste nach Nummer sortiert.</p></form>' +
      '<div class="note"><b>Datenschutz:</b> Nur Vornamen oder Spitznamen eintragen. Keine Nachnamen, Geburtsdaten oder E-Mail-Adressen der Kinder.</div></aside></div>';
  };
  // Kinder: zuerst nach Nummer (falls vergeben), sonst alphabetisch
  function kidSort(a, b) {
    var an = a.nr == null ? null : +a.nr, bn = b.nr == null ? null : +b.nr;
    if (an != null && bn != null && an !== bn) return an - bn;
    if ((an == null) !== (bn == null)) return an == null ? 1 : -1;
    return a.name.localeCompare(b.name, 'de');
  }
  function kidBadge(k) { return k.nr != null ? String(k.nr) : k.name.charAt(0); }
  // «12 Mila», «12. Mila» oder «12) Mila» → Nummer 12, Name Mila
  function splitNr(line) {
    var m = /^\s*(\d{1,3})\s*[.):\-]?\s+(\S.*)$/.exec(line);
    return m && +m[1] >= 1 ? { nr: +m[1], name: m[2].trim() } : { nr: null, name: line.trim() };
  }
  function kidExists(n) { return T.kids.some(function (k) { return k.name.toLowerCase() === n.toLowerCase(); }); }
  ACT.addKid = async function (f) {
    var x = splitNr(f.elements.name.value), n = x.name.slice(0, 30); if (!n) return;
    if (kidExists(n)) return toast('Diesen Namen gibt es in der Klasse schon.');
    var r = await DB.addKids(T.cls, [{ name: n, nr: x.nr, pw: randPw() }]);
    r.forEach(function (k) { T.kids.push(k); T.fresh.add(k.id); });
    T.kids.sort(kidSort); T.progress = null; T.tafel = null;
    T.render(); var i = document.getElementById('kidName'); if (i) { i.value = ''; i.focus(); }
  };
  ACT.addBulk = async function (f) {
    var seen = {}, add = [];
    f.elements.list.value.split(/[\n,;]/).forEach(function (s) {
      var x = splitNr(s), n = x.name.slice(0, 30); var k = n.toLowerCase();
      if (n && !seen[k] && !kidExists(n)) { seen[k] = 1; add.push({ name: n, nr: x.nr, pw: randPw() }); }
    });
    if (!add.length) return toast('Keine neuen Namen gefunden.');
    var r = await DB.addKids(T.cls, add);
    r.forEach(function (k) { T.kids.push(k); T.fresh.add(k.id); });
    T.kids.sort(kidSort); T.progress = null; T.tafel = null;
    toast(plural(r.length, 'Kind', 'Kinder') + ' hinzugefügt.'); T.render();
  };
  ACT.kidNr = async function (el) {
    var k = T.kids.filter(function (x) { return x.id === el.dataset.id; })[0]; if (!k) return;
    var v = el.value.trim(), nr = v === '' ? null : parseInt(v, 10);
    if (v !== '' && !(nr >= 1 && nr <= 999)) { el.value = k.nr != null ? k.nr : ''; return toast('Bitte eine Nummer von 1 bis 999 eintragen oder das Feld leer lassen.'); }
    if (nr === k.nr || (nr == null && k.nr == null)) return;
    await DB.setKidNr(k.id, nr); k.nr = nr; T.kids.sort(kidSort); T.progress = null; T.render();
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
  ACT.printCards = async function () {
    var c = T.cur();
    toast('Kärtchen werden vorbereitet …');
    // QR-Code pro Kind: führt direkt zur Bildpasswort-Eingabe dieses Kindes
    var qrs = await Promise.all(T.kids.map(function (k) { return qrSvg(kidUrl(c.code) + '/' + k.id).catch(function () { return ''; }); }));
    document.getElementById('print').innerHTML = '<div class="pcards">' + T.kids.map(function (k, i) {
      return '<div class="pcard"><div class="pc-main"><h3>' + (k.nr != null ? '<span class="pnr">' + h(String(k.nr)) + '</span>' : '') + h(k.name) + '</h3><div class="pw">' + k.pw.split(',').map(function (p) {
        return SYM[p] ? '<span style="background:' + SYM[p].bg + '">' + symSvg(p, 48) + '</span>' : ''; }).join('') +
        '</div><p>Klasse ' + h(c.name) + ' · Code <b>' + h(c.code) + '</b><br>' + h(shortUrl(kidUrl())) + '</p></div>' +
        (qrs[i] ? '<div class="pc-qr">' + qrs[i] + '<small>Mit dem iPad scannen</small></div>' : '') + '</div>';
    }).join('') + '</div>';
    setTimeout(function () { window.print(); }, 150);
  };

  // ---------- Fortschritt ----------
  T.tabFortschritt = function () {
    if (T.progress === null) {
      if (!T.progressBusy) {
        T.progressBusy = true;
        Promise.all([DB.listProgress(T.kids.map(function (k) { return k.id; })), T.games.some(isVok) ? DB.storeGet('hat-' + T.cls).catch(function () { return null; }) : null])
          .then(function (r) { var p = r[0]; T.vkFree = {}; vkFree(r[1]).forEach(function (k) { T.vkFree[k] = 1; }); T.progress = p; T.progressBusy = false; T.render(); })
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
      var vb = vbHTML(p.award); if (vb) lines.unshift(vb);
      var vk = vkHTML(p.award); if (vk) lines.unshift(vk);
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
          kidColor(k.name) + ';color:#1B2A3D">' + h(kidBadge(k)) + '</span>' + h(k.name) +
          (games.some(function (g) { return !cell(P[k.id + '|' + g.id]).none; }) ? '<button class="preset" data-a="pReset" data-k="' + k.id + '" title="Fortschritt zurücksetzen" aria-label="Fortschritt von ' + h(k.name) + ' zurücksetzen">↺</button>' : '') + '</span></th>' + cells +
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
      colEditor(c) +
      '<section class="card stack"><h2>Neue Woche</h2><button class="switch" role="switch" aria-checked="' + !!c.tafel_auto + '" data-a="tafelAuto"><span>Namen jeden Montag automatisch von der Tafel nehmen</span><span class="track"></span></button>' +
      '<div class="row"><button class="btn danger' + (UI.confirm === clearKey ? ' armed' : '') + '" data-a="tafelClear">' + (UI.confirm === clearKey ? 'Wirklich alle Namen entfernen?' : 'Alle Namen jetzt entfernen') + '</button>' +
      '<span class="muted small">Die Fächer bleiben, nur die Namen gehen weg.</span></div></section></div>' +
      '<aside class="side"><section class="card stack" style="background:var(--pastel);border-color:#A9C9EC"><h2 style="font-size:22px">Offene Fragen gerade</h2>' + counts +
      '<a class="btn amber" href="#/wandtafel/' + T.cls + '" target="_blank" rel="noopener">' + ic(I.board) + ' An der Wandtafel zeigen</a>' +
      '<button class="btn" data-a="tafelRefresh">' + ic(I.reset) + ' Aktualisieren</button>' +
      '<p class="muted" style="font-size:14px">Die Kinder öffnen die Tafel nach dem Einloggen über «Arbeitsstand».</p></section></aside></div>';
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
  function sqlHint(e) { return /bild|kid_tools|tafel_cols|column|schema cache/i.test((e && e.message) || '') ? 'Dafür zuerst das neue SQL (Version 20) in Supabase ausführen.' : errMsg(e); }
  async function saveTafelCols(o) {
    var c = T.cur();
    try { await DB.updateClass(c.id, { tafel_cols: o }); } catch (e) { return toast(sqlHint(e)); }
    c.tafel_cols = o; setTafelCols(o); toast('Namen der Spalten gespeichert.'); T.tafel = null; T.render();
  }
  // Spalten bearbeiten: Entwurf T.colDraft (Name, Farbe), dann speichern
  function colEditor(c) {
    if (!T.colDraft || T.colDraftCls !== c.id) { T.colDraft = colList(c.tafel_cols); T.colDraftCls = c.id; }
    var d = T.colDraft;
    return '<section class="card stack"><h2>Die Spalten</h2><p class="muted small" style="margin:0">Namen und Farben anpassen, Spalten hinzufügen oder entfernen (höchstens 6).</p><div class="stack" style="gap:10px">' + d.map(function (x, i) {
      return '<div class="colrow" style="background:' + mixHex(x.color, .86, 255) + ';border-color:' + mixHex(x.color, .45, 255) + '"><span class="coldot" style="background:' + x.color + '"></span>' +
        '<input class="input col-in" value="' + h(x.label) + '" maxlength="40" aria-label="Name der Spalte" data-input="colLab" data-i="' + i + '">' +
        '<div class="colsw" role="group" aria-label="Farbe">' + PALETTE.map(function (p) { return '<button type="button" class="swatch" style="background:' + p[0] + '" aria-label="' + p[1] + '" aria-pressed="' + (p[0].toLowerCase() === x.color.toLowerCase()) + '" data-a="colColor" data-i="' + i + '" data-c="' + p[0] + '"></button>'; }).join('') + '</div>' +
        '<span class="row" style="gap:4px;flex-wrap:nowrap"><button type="button" class="btn sm" data-a="colMove" data-i="' + i + '" data-d="-1" aria-label="nach links"' + (i ? '' : ' disabled') + '>←</button><button type="button" class="btn sm" data-a="colMove" data-i="' + i + '" data-d="1" aria-label="nach rechts"' + (i < d.length - 1 ? '' : ' disabled') + '>→</button>' +
        '<button type="button" class="btn sm danger" data-a="colDel" data-i="' + i + '"' + (d.length > 1 ? '' : ' disabled') + '>Entfernen</button></span></div>';
    }).join('') + '</div><div class="row">' + (d.length < 6 ? '<button type="button" class="btn sm" data-a="colAdd">+ Spalte hinzufügen</button>' : '') +
      '<button type="button" class="btn primary sm" data-a="colsSave">Spalten speichern</button><button type="button" class="btn sm" data-a="colsReset">Standard</button></div>' +
      '<p class="muted small" style="margin:0">Die Kinder sehen die Änderungen beim nächsten Öffnen. Kinder in einer entfernten Spalte erscheinen nicht mehr auf der Tafel und tragen sich neu ein. ' +
      'Bei «Ich habe eine Frage» sehen die Kinder, wer im gleichen Fach unter «Ich kann helfen» steht.</p></section>';
  }
  ACT.colLab = function (el) { var x = (T.colDraft || [])[+el.dataset.i]; if (x) x.label = el.value; };
  ACT.colColor = function (el) { var x = (T.colDraft || [])[+el.dataset.i]; if (x) { x.color = el.dataset.c; T.render(); } };
  ACT.colDel = function (el) { if (T.colDraft.length > 1) { T.colDraft.splice(+el.dataset.i, 1); T.render(); } };
  ACT.colMove = function (el) { var d = T.colDraft, i = +el.dataset.i, j = i + (+el.dataset.d); if (j < 0 || j >= d.length) return; d.splice(j, 0, d.splice(i, 1)[0]); T.render(); };
  ACT.colAdd = function () {
    var d = T.colDraft, used = d.map(function (x) { return x.color.toLowerCase(); }), col = (PALETTE.filter(function (p) { return used.indexOf(p[0].toLowerCase()) < 0; })[0] || PALETTE[0])[0];
    d.push({ id: 's' + Math.random().toString(36).slice(2, 8), label: 'Neue Spalte', color: col }); T.render();
  };
  ACT.colsSave = function () {
    var d = (T.colDraft || []).map(function (x) { return { id: x.id, label: String(x.label || '').trim().slice(0, 40) || 'Spalte', color: x.color }; });
    var std = d.length === 3 && ['helfen', 'klar', 'frage'].every(function (id, i) { return d[i].id === id && d[i].color.toLowerCase() === COL_STDCOL[id].toLowerCase(); });
    var o = {};
    if (std) d.forEach(function (x) { if (x.label !== COL_DEF[x.id]) o[x.id] = x.label; }); else o = { list: d };
    T.colDraft = null; return saveTafelCols(o);
  };
  ACT.colsReset = function () { T.colDraft = null; return saveTafelCols({}); };
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
        '<div class="row"><button class="btn" data-a="codeEdit">✎ Klassencode selbst wählen</button><button class="btn" data-a="newCode">Zufälliger neuer Code</button><button class="btn danger' + (UI.confirm === delKey ? ' armed' : '') + '" data-a="delClass">' +
        (UI.confirm === delKey ? 'Klasse mit allen Kindern löschen?' : 'Klasse löschen') + '</button></div>' +
        '<p class="muted small">Mit einem neuen Code funktioniert der alte nicht mehr.</p></div>' : '') +
      '<form class="stack" data-a="createClass" style="padding-top:14px;border-top:1.5px solid var(--line)"><div class="field"><label for="accNew">Weitere Klasse anlegen</label>' +
      '<div class="row"><input class="input grow" style="flex:1 1 180px" id="accNew" name="cname" placeholder="z. B. 6b" required maxlength="30"><input class="input" style="flex:1 1 160px" name="ccode" placeholder="Code, z. B. Otter 123 (freiwillig)" maxlength="24" autocomplete="off"><button class="btn primary">Anlegen</button></div></div></form></div>');
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
  function kbCard() {
    var A = T.admin, list = A.kb || [];
    return '<section class="card stack"><h2>Klassenbilder (Maskottchen)</h2><p class="muted">Diese Bilder können alle Lehrpersonen für ihre Klasse auswählen (Klick auf das Bild neben dem Klassennamen).</p>' +
      (list.length ? '<div class="bildwahl">' + list.map(function (b) {
        return '<div class="bildopt"><img src="' + h(b.src) + '" alt=""><input class="input" value="' + h(b.name || '') + '" maxlength="30" aria-label="Name" data-change="kbName" data-id="' + h(b.id) + '"><button class="btn sm danger" data-a="kbDel" data-id="' + h(b.id) + '">Entfernen</button></div>'; }).join('') + '</div>' : '<p class="muted small">Noch keine Vorlagen.</p>') +
      '<div class="field"><label for="kbFile">Bilder hinzufügen (mehrere möglich)</label><input class="input" id="kbFile" type="file" accept="image/*" multiple data-change="kbAdd"></div></section>';
  }
  // Verwaltung: Lizenz «gültig bis» pro Lehrperson (Version 22)
  function licRow(t) {
    if (DB.noLicense) return '<div class="row" style="padding:8px 0 2px 52px"><span class="muted small"><b>Gültig bis:</b> Bitte zuerst das SQL (Version 22) in Supabase ausführen.</span></div>';
    var d = licLeft(t), pill = d === null ? '<span class="pill">unbefristet</span>'
      : d < 0 ? '<span class="pill" style="background:#F6C9BC;color:#7A2E12">abgelaufen</span>'
      : d <= 30 ? '<span class="pill" style="background:#FCE8B2">' + (d === 0 ? 'läuft heute ab' : 'noch ' + plural(d, 'Tag', 'Tage')) + '</span>' : '';
    var mail = d !== null && d <= 30 ? '<a class="btn sm" href="mailto:' + h(t.email) + '?subject=' + encodeURIComponent('Deine ' + C.PORTAL_NAME + ' verlängern') +
      '&body=' + encodeURIComponent('Hallo' + (t.name ? ' ' + t.name : '') + '\n\nDeine ' + C.PORTAL_NAME + ' ' + (d < 0 ? 'war' : 'ist noch') + ' bis am ' + dateCH(t.valid_until) +
        ' gültig. Wenn du sie ein weiteres Jahr nutzen möchtest, kannst du sie ' + (C.SHOP_URL ? 'hier verlängern:\n' + C.SHOP_URL : 'bei mir verlängern. Antworte einfach auf diese E-Mail.') +
        '\n\nDeine Klassen und alles, was du gespeichert hast, bleiben erhalten.\n\nHerzliche Grüsse') + '">✉ Erinnerung schreiben</a>' : '';
    return '<div class="row" style="gap:8px;padding:8px 0 2px 52px"><label class="muted small" style="font-weight:700" for="lic-' + t.id + '">Gültig bis:</label>' +
      '<input class="input" style="width:auto;min-height:38px;padding:4px 10px" type="date" id="lic-' + t.id + '" value="' + h(t.valid_until || '') + '" data-change="licSet" data-t="' + t.id + '">' +
      pill + '<button class="btn sm" data-a="licPlus" data-t="' + t.id + '">+ 1 Jahr</button>' +
      (t.valid_until ? '<button class="btn sm" data-a="licNone" data-t="' + t.id + '">Unbefristet</button>' : '') + mail + '</div>';
  }
  async function licSave(tid, day) {
    var t = (T.admin.teachers || []).filter(function (x) { return x.id === tid; })[0]; if (!t) return;
    try { await DB.setValidUntil(tid, day || null); t.valid_until = day || null; toast(day ? 'Gültig bis ' + dateCH(day) + ' gespeichert.' : 'Unbefristet gespeichert.'); }
    catch (e) { toast(errMsg(e)); }
    T.render();
  }
  ACT.licSet = function (el) { if (!el.value || /^\d{4}-\d{2}-\d{2}$/.test(el.value)) licSave(el.dataset.t, el.value); };
  ACT.licNone = function (el) { licSave(el.dataset.t, null); };
  ACT.licPlus = function (el) {
    var t = (T.admin.teachers || []).filter(function (x) { return x.id === el.dataset.t; })[0]; if (!t) return;
    var base = t.valid_until && t.valid_until > isoDay(new Date()) ? new Date(t.valid_until + 'T12:00:00') : new Date();
    base.setFullYear(base.getFullYear() + 1);
    licSave(t.id, isoDay(base));
  };
  T.tabAdmin = function () {
    var A = T.admin; if (!A.form) A.form = blankForm();
    if (A.teachers === null && !A.busy) {
      A.busy = true;
      Promise.all([DB.listTeachers(), DB.listTeacherGames(), DB.sharedGet('werkzeuge').catch(function () { return null; }),
        DB.sharedGet('vokabelkiste-vorlage').catch(function () { return null; }), DB.sharedGet('vokabelkiste-zuweisung').catch(function () { return null; }),
        DB.sharedGet('klassenbilder').catch(function () { return null; })]).then(function (r) {
        A.kb = Array.isArray(r[5]) ? r[5] : [];
        A.teachers = r[0]; A.tg = r[1]; A.tools = r[2] || {}; A.vtpl = r[3]; A.vz = r[4] && typeof r[4] === 'object' ? r[4] : {}; A.busy = false; if (T.tab === 'verwaltung') T.render(); })
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
        (t.is_admin ? '' : '<div class="row tools-row" style="gap:8px;padding:8px 0 2px 52px"><span class="muted small" style="font-weight:700">Werkzeuge:</span><span class="muted small">Immer dabei: ' + BASE_TOOLS.map(function (x) { return x[1].replace(/^\S+\s/, ''); }).join(', ') + ' ·</span>' + TOOLS.map(function (x) {
          var on = !!((A.tools || {})[t.id] || {})[x[0]];
          return '<button class="chip" style="min-height:38px" aria-pressed="' + on + '" data-a="toolToggle" data-t="' + t.id + '" data-k="' + x[0] + '">' + (on ? '✓ ' : '') + x[1] + '</button>'; }).join('') + '</div>') +
        (t.is_admin ? '' : licRow(t)) +
        (t.is_admin ? '' : vzRow(t)) +
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
      '<div class="cols2"><div class="wide">' + pack + form + kbCard() + '</div>' +
      '<aside class="side"><div class="note"><b>So teilen Sie Spiele zu:</b> Spiele mit «Nur zugeteilt» sehen nur die Lehrpersonen, denen Sie sie unten zuteilen. Spiele mit «Für alle» sehen alle Lehrpersonen.</div>' +
      '<div class="note"><b>Neue Lehrperson hinzufügen:</b> In Supabase links «Authentication» → «Users» → «Add user» → «Create new user». E-Mail und ein Startpasswort eingeben, «Auto Confirm User» anhaken. Danach erscheint die Person hier, und Sie können ihr Spiele zuteilen. Ihre Lizenz gilt automatisch 1 Jahr ab heute («Gültig bis», mit «+ 1 Jahr» verlängern). Sie kann ihr Passwort oben rechts unter ihrem Namen ändern.</div></aside></div>' +
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
      if (!data || data.format !== 'knobelnest-spielpaket' || !Array.isArray(data.games)) return toast('Diese Datei ist kein Spielpaket der Klassenkiste.');
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
  ACT.toolToggle = async function (el) {
    var A = T.admin, t = el.dataset.t, k = el.dataset.k;
    A.tools = A.tools || {}; var cur = Object.assign({}, A.tools[t] || {});
    if (cur[k]) delete cur[k]; else cur[k] = true;
    A.tools[t] = cur; T.render();
    try {
      await DB.sharedSet('werkzeuge', JSON.parse(JSON.stringify(A.tools)));
      // Vokabelkiste: das Spiel gleich mit zuteilen bzw. wegnehmen
      var vk = k === 'vk' ? T.games.filter(isVok)[0] : null;
      if (vk && !vk.for_all) {
        await DB.setTeacherGame(t, vk.id, !!cur[k]);
        A.tg = (A.tg || []).filter(function (x) { return !(x.teacher_id === t && x.game_id === vk.id); });
        if (cur[k]) A.tg.push({ teacher_id: t, game_id: vk.id });
        T.render();
      }
      toast((cur[k] ? 'Freigegeben: ' : 'Gesperrt: ') + TOOLS.filter(function (x) { return x[0] === k; })[0][1].replace(/^\S+\s/, '')); }
    catch (e) { toast(errMsg(e)); }
  };
  // ---------- Vokabelkiste: Vorlagen einzelnen Lehrpersonen zuteilen (shared_store «vokabelkiste-zuweisung» = { Lehrperson-ID: [Portion-IDs] }) ----------
  function vzItems() {
    var out = [], tp = T.admin.vtpl;
    ((tp && tp.subjects) || []).forEach(function (sb) {
      var walk = function (arr, path) { (arr || []).forEach(function (n) { if (n.words) out.push({ id: n.id, name: n.name, path: path, n: n.words.length }); else walk(n.kids, path.concat(n.name)); }); };
      walk(sb.tree, [sb.name]);
    });
    return out;
  }
  function vzRow(t) {
    var A = T.admin, items = vzItems(); if (!items.length) return '';
    var mine = (A.vz || {})[t.id] || [], have = items.filter(function (x) { return mine.indexOf(x.id) >= 0; }).length, open = A.vopen === t.id;
    var html = '<div class="row tools-row" style="gap:8px;padding:8px 0 2px 52px"><span class="muted small" style="font-weight:700">Vokabelkiste-Vorlagen:</span><span class="small">' + have + ' von ' + items.length + ' Portionen</span>' +
      '<button class="btn sm" data-a="vzOpen" data-id="' + t.id + '" aria-expanded="' + open + '">' + (open ? 'Schliessen' : '📚 Vorlagen zuteilen') + '</button></div>';
    if (!open) return html;
    var groups = [], by = {};
    items.forEach(function (x) { var k = x.path.join(' › '); if (!by[k]) { by[k] = []; groups.push(k); } by[k].push(x); });
    var ids = function (l) { return l.map(function (x) { return x.id; }).join(','); };
    return html + '<div class="stack" style="gap:12px;padding:10px 0 6px 52px"><div class="row"><button class="btn sm" data-a="vzBulk" data-t="' + t.id + '" data-on="1" data-ids="' + ids(items) + '">Alle Vorlagen geben</button>' +
      '<button class="btn sm" data-a="vzBulk" data-t="' + t.id + '" data-on="0" data-ids="' + ids(items) + '">Alle wegnehmen</button></div>' +
      '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px">' + groups.map(function (k) {
        var l = by[k], all = l.every(function (x) { return mine.indexOf(x.id) >= 0; });
        return '<div class="card stack" style="padding:14px;gap:8px"><div class="row" style="justify-content:space-between"><b>' + h(k) + '</b><button class="btn sm" data-a="vzBulk" data-t="' + t.id + '" data-on="' + (all ? 0 : 1) + '" data-ids="' + ids(l) + '">' + (all ? 'Ordner wegnehmen' : 'Ganzer Ordner') + '</button></div>' +
          l.map(function (x) { return '<label class="row" style="gap:10px;font-size:16px;flex-wrap:nowrap"><input type="checkbox" style="width:22px;height:22px;flex:none" ' + (mine.indexOf(x.id) >= 0 ? 'checked ' : '') +
            'data-change="vzSet" data-t="' + t.id + '" data-p="' + h(x.id) + '"><span>' + h(x.name) + ' <span class="muted small">· ' + x.n + ' Wörter</span></span></label>'; }).join('') + '</div>';
      }).join('') + '</div><p class="muted small" style="margin:0">Die Lehrperson bekommt neu zugeteilte Portionen als Kopie, sobald sie die Vokabelkiste das nächste Mal öffnet. Wegnehmen löscht nichts, was sie schon hat.</p></div>';
  }
  async function vzSave(tid, ids, on) {
    var A = T.admin; A.vz = A.vz || {}; var l = (A.vz[tid] || []).slice();
    ids.forEach(function (id) { var i = l.indexOf(id); if (on && i < 0) l.push(id); if (!on && i >= 0) l.splice(i, 1); });
    var before = A.vz[tid]; A.vz[tid] = l; T.render();
    try { await DB.sharedSet('vokabelkiste-zuweisung', A.vz); } catch (e) { A.vz[tid] = before; T.render(); throw e; }
  }
  ACT.vzOpen = function (el) { T.admin.vopen = T.admin.vopen === el.dataset.id ? null : el.dataset.id; T.render(); };
  ACT.vzSet = function (el) { return vzSave(el.dataset.t, [el.dataset.p], el.checked); };
  ACT.vzBulk = function (el) { return vzSave(el.dataset.t, el.dataset.ids.split(',').filter(Boolean), el.dataset.on === '1'); };
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
    var m = (location.hash || '').match(/^#\/klasse\/([^/?#]+)(?:\/([0-9a-f-]{36}))?/);
    K.wantKid = m && m[2] ? m[2] : null;
    if (m) {
      var given = decodeURIComponent(m[1]);
      try { history.replaceState(null, '', location.pathname + location.search + '#/klasse'); } catch (e) {}
      var old = LS.get('kn_kid');
      if (old && String(old.code || '').replace(/\s+/g, '').toUpperCase() !== given.toUpperCase()) { DB.kidLogout(old.token); LS.del('kn_kid'); }
      LS.set('kn_code', given);
    }
    var s = LS.get('kn_kid');
    if (s && K.wantKid && s.kid !== K.wantKid) { try { DB.kidLogout(s.token); } catch (e) {} LS.del('kn_kid'); s = null; }
    if (s && s.exp > Date.now()) { K.sess = s; K.step = 'home'; return K.loadHome(); }
    LS.del('kn_kid'); K.sess = null;
    var code = LS.get('kn_code');
    if (code) {
      try { var c = await DB.kidClass(code); if (c && c.pausiert) { K.err = 'Eure ' + C.PORTAL_NAME + ' ist gerade pausiert. Sag es deiner Lehrperson.'; c = null; } if (c) { K.code = code; K.cls = c; K.step = 'names';
        var wk = K.wantKid && c.kids.filter(function (k) { return k.id === K.wantKid; })[0];
        if (wk) { K.kid = wk; K.pw = []; K.err = ''; K.step = 'pw'; } K.wantKid = null;
        return K.render(); } } catch (e) {}
    }
    K.step = 'code'; K.render();
  };
  K.loadHome = async function () {
    try { K.home = await DB.kidHome(K.sess.token); }
    catch (e) { return K.sessionLost(e); }
    K.kl = await DB.kidKlasse(K.sess.token); setTafelCols(K.kl && K.kl.cols);
    K.render(); K.checkRace(); K.checkHeft();
    if (!K.raceWatch) K.raceWatch = setInterval(function () { if (K.sess && UI.view === 'kid' && K.step === 'home' && !document.hidden) K.checkRace(); }, 4000);
  };
  // Gibt es ein Hausaufgabenheft für diese Klasse? Dann erscheint die Agenda-Kachel
  K.checkHeft = async function () {
    try { var ad = await DB.kidAtelier(K.sess.token); var ha = !!(ad && ad.kids); if (ha !== !!K.atelierOk) { K.atelierOk = ha; if (K.step === 'home') K.render(); } }
    catch (e) {}
    try { var pd = await DB.kidPin(K.sess.token); var hp = !!(pd && pd.boards && Object.keys(pd.boards).length); if (hp !== !!K.pinOk) { K.pinOk = hp; if (K.step === 'home') K.render(); } }
    catch (e) {}
    try { var d = await DB.kidHeft(K.sess.token); var has = !!(d && d.entries); if (has !== !!K.heftOk) { K.heftOk = has; if (K.step === 'home') K.render(); } }
    catch (e) {}
  };
  K.sessionLost = function (e) {
    if (/pausiert/i.test((e && e.message) || '')) {
      LS.del('kn_kid'); K.sess = null; K.home = null; K.err = 'Eure ' + C.PORTAL_NAME + ' ist gerade pausiert. Sag es deiner Lehrperson.'; K.step = 'code'; return K.render();
    }
    if (/Anmeldung|session/i.test((e && e.message) || '')) {
      LS.del('kn_kid'); K.sess = null; K.home = null; toast('Bitte melde dich nochmals an.'); return K.start();
    }
    toast(errMsg(e));
  };
  K.shell = function (body, back) {
    if (back === null) return '<div class="kid"><div class="kid-in">' + body + '</div></div>';
    var marke = '<span class="kid-marke"><img src="bilder/eule.webp" alt="" width="52" height="52"><small>' + h(C.PORTAL_NAME) + '</small></span>';
    var top = back === 'Abmelden' ? marke + '<button class="kid-btn" data-a="kBack">Abmelden</button>'
      : back ? backBtn('data-a="kBack"', back)
      : marke + '<a class="kid-btn" href="#/" style="display:inline-flex;align-items:center;text-decoration:none;color:var(--ink);border-width:1.5px;font-size:15px">Für Lehrpersonen</a>';
    return '<div class="kid"><div class="kid-in"><div class="kid-top">' + top + '</div>' + body + '</div></div>';
  };
  K.render = function () {
    document.body.classList.add('kidv');
    var b = K['view_' + K.step](); if (b == null) return;
    paint(b);
    if (K.step === 'home') vkPlace();
  };
  // Vokabelkiste-Kachel direkt unter «Mathematik» stellen (gleiche Spalte, nächste Reihe)
  var VK_SVG = '<svg width="50" height="42" viewBox="0 0 40 34" aria-hidden="true"><rect x="9" y="2" width="22" height="17" rx="2.5" fill="#fff" stroke="#c4c9c2"/><rect x="9" y="6.5" width="22" height="1.7" fill="#ec9d95"/><rect x="2" y="13" width="36" height="19" rx="6" fill="#87ad74"/><rect x="2" y="18" width="36" height="14" rx="6" fill="#6f9a5f"/></svg>';
  function vkPlace() {
    var vk = document.querySelector('.big-tiles .vk-tile'); if (!vk) return;
    var grid = vk.parentNode, list = Array.prototype.filter.call(grid.children, function (x) { return x !== vk; });
    var m = -1; list.forEach(function (x, i) { if (/^mathematik$/i.test((x.dataset.f || '').trim())) m = i; });
    grid.appendChild(vk); vk.style.gridColumn = '';
    var n = getComputedStyle(grid).gridTemplateColumns.split(' ').filter(Boolean).length;
    if (m >= 0 && n > 1) vk.style.gridColumn = String(m % n + 1);
  }
  window.addEventListener('resize', function () { if (UI.view === 'kid' && K.step === 'home') vkPlace(); });
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
    return K.shell('<div class="kid-hello"><img class="kid-bild" src="' + h(klassBild(K.cls.bild)) + '" alt=""><div class="stack" style="gap:6px"><h1>Wer bist du?</h1><p class="lead">Klasse ' + h(K.cls.class_name) + ' · Tippe auf deinen Namen.</p></div></div>' +
      (K.cls.kids.length ? '<div class="kid-grid">' + K.cls.kids.map(function (k) {
        return '<button class="kid-name" data-a="kName" data-id="' + k.id + '"><span class="ini" style="background:' + kidColor(k.name) + '">' + h(kidBadge(k)) + '</span><b>' + h(k.name) + '</b></button>';
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
      var gs = games.filter(function (g) { return g.fach === f; }), n = gs.length;
      // Ein Fach, das nur aus der Vokabelkiste besteht: Kachel mit dem Kisten-Symbol, öffnet die Vokabelkiste direkt
      if (n === 1 && isVok(gs[0])) return '<button class="big-tile vk-tile" style="background:' + fachColor(f) + '" data-a="kPlay" data-id="' + gs[0].id + '"><span class="ic ic-bild"><img src="bilder/kacheln/vokabelkiste.webp" alt="" draggable="false"></span><b>' + h(f) + '</b><span>Wörter üben</span></button>';
      return '<button class="big-tile" style="background:' + fachColor(f) + '" data-a="kFach" data-f="' + h(f) + '">' + (fachBild(f) ? '<span class="ic ic-bild">' + fachBild(f) + '</span>' : '<span class="ic">' + h(f.charAt(0)) + '</span>') + '<b>' + h(f) + '</b><span>' + plural(n, 'Spiel', 'Spiele') + '</span></button>';
    }).join('');
    var kt = { kid_tools: (K.kl && K.kl.tools) || {} };
    return K.shell('<div class="kid-hello"><img class="kid-bild" src="' + h(klassBild(K.kl && K.kl.bild)) + '" alt=""><div class="stack" style="gap:6px"><h1>Hallo ' + h(K.home.kid.name) + '!</h1><p class="lead">' + (fachs.length ? 'Welches Fach möchtest du üben?' : 'Deine Lehrperson hat noch keine Spiele freigegeben.') + '</p></div>' +
      '<button class="kid-btn kid-out" data-a="kBack">Abmelden</button></div>' +
      (K.umfOpen ? '<button class="sprint-tile umf-tile" data-a="kUmf"><span class="ic ic-bild"><img src="bilder/kacheln/umfrage-kiste.webp" alt="" draggable="false"></span><span><b>Umfrage!</b><span>Deine Lehrperson möchte wissen, was du denkst. Tippe hier.</span></span></button>' : '') +
      (K.raceOpen ? '<button class="sprint-tile" data-a="kRace"><span class="ic">🏃</span><span><b>Sprint!</b><span>Deine Lehrperson hat einen Klassen-Sprint geöffnet. Tippe hier, um mitzumachen.</span></span></button>' : '') +
      (tiles ? '<div class="big-tiles">' + tiles + '</div>' : '') +
      '<div class="tile-pair">' + (K.heftOk && toolOn(kt, 'heft') ? '<button class="tafel-tile heft-tile" data-a="kHeft"><span class="ic ic-bild"><img src="bilder/kacheln/hausaufgaben.webp" alt="" draggable="false"></span>' +

      '<span><b>Hausaufgaben</b><span>Schau in dein Hausaufgabenheft.</span></span></button>' : '') +
      (!toolOn(kt, 'tafel') ? '' : '<button class="tafel-tile" data-a="kTafel"><span class="ic ic-bild"><img src="bilder/kacheln/arbeitsstand.webp" alt="" draggable="false"></span>' +
      '<span><b>Arbeitsstand</b><span>Zeig, wo du beim Arbeiten stehst, und finde Hilfe.</span></span></button>') +
      (K.pinOk && toolOn(kt, 'pin') ? '<button class="tafel-tile pin-tile" data-a="kPin"><span class="ic ic-bild"><img src="bilder/kacheln/pinnwand.webp" alt="" draggable="false"></span>' +
      '<span><b>Pinnwand</b><span>Schreib deine Ideen und stimm ab.</span></span></button>' : '') +
      (kt.kid_tools.quiz === true ? '<button class="tafel-tile quiz-tile" data-a="kQuiz"><span class="ic ic-bild"><img src="bilder/kacheln/live-quiz.webp" alt="" draggable="false"></span>' +
      '<span><b>Quiz erstellen</b><span>Bau dein eigenes Quiz für die Klasse.</span></span></button>' : '') +
      (K.atelierOk && toolOn(kt, 'atelier') ? '<button class="tafel-tile atelier-tile" data-a="kAtelier"><span class="ic ic-bild"><img src="bilder/kacheln/atelier.webp" alt="" draggable="false"></span>' +
      '<span><b>Atelier</b><span>Fahr mit deinem Velo dorthin, wo du gerade stehst.</span></span></button>' : '') + '</div>', null);
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
        (awardText(g.award) ? '<span class="kaward">' + h(awardText(g.award)) + '</span>' : '') + vbHTML(g.award) +
        (p == null ? '' : '<span class="kbar"><i style="width:' + p + '%"></i></span>') + '<span style="font-size:17px">' + h(label) + '</span>' +
        '<button class="kid-go" style="margin-top:auto;height:60px;font-size:22px;' + fachBtn(g.fach) + '" data-a="kPlay" data-id="' + g.id + '">' + (g.plays ? 'Weiterspielen' : 'Starten') + '</button></div></article>';
    }).join('') + '</div>', 'Zurück');
  };
  K.view_heft = function () {
    var kid = K.home && K.home.kid; if (!kid) { K.step = 'home'; return K.view_home(); }
    var doc = {
      get: async function () { var d = await DB.kidHeft(K.sess.token); return { exists: d != null, data: function () { return d; } }; },
      set: async function () { var e = new Error('Nur lesen'); e.code = 'forbidden'; throw e; },
      onSnapshot: function () { return function () {}; }
    };
    window.knHeft = {
      mode: 'kid', key: 'kind-' + kid.id, kidId: kid.id, className: '', roster: [],
      own: function (e, del) {
        var x = del ? { id: e.id } : { id: e.id, date: e.date, fach: e.fach || '', title: e.title, details: e.details || '', order: e.order || 0 };
        DB.kidHeftOwn(K.sess.token, x, !!del).then(function (ok) { if (!ok) toast('Das konnte nicht gespeichert werden.'); }).catch(function () { toast('Das konnte nicht gespeichert werden.'); });
      },
      tick: function (id, on) { DB.kidHeftTick(K.sess.token, id, on).catch(function () { toast('Der Haken konnte nicht gespeichert werden.'); }); },
      back: function () { ACT.kBack(); },
      claude: { use: async function (name) {
        if (name === 'db') return { doc: function () { return doc; } };
        if (name === 'downloads') return heftDownloads();
        return null;
      } }
    };
    return '<div class="folie"><iframe src="hausaufgaben.html?v=' + HEFT_VER + '" title="Hausaufgabenheft"></iframe></div>';
  };
  K.view_pin = function () {
    var kid = K.home && K.home.kid; if (!kid) { K.step = 'home'; return K.view_home(); }
    var me = kid.id;
    var db = pinBridge({
      active: function () { return UI.view === 'kid' && K.step === 'pin'; }, every: 5000,
      load: async function () { var d = await DB.kidPin(K.sess.token); if (!d) return null; var v = {}; if (d.my) v[me] = d.my;
        return { boards: d.boards || {}, ideas: d.ideas || {}, settings: { main: { labels: d.labels || {} } }, votes: v }; },
      put: function () { var e = new Error('Nicht erlaubt'); e.code = 'forbidden'; return Promise.reject(e); },
      add: async function (coll, obj) { if (coll !== 'ideas') throw new Error('Nicht erlaubt'); return DB.kidPinPost(K.sess.token, obj.boardId, obj.text, obj.cat, obj.img); },
      vote: async function (body) { await DB.kidPinVote(K.sess.token, { r: body.r || {} }); },
      voteDoc: function (id, v) { return { name: kid.name, r: JSON.parse(JSON.stringify((v && v.r) || {})), at: v && v.at }; }
    });
    window.knPin = {
      mode: 'kid', name: kid.name, roster: [],
      back: function () { ACT.kBack(); },
      claude: { use: async function (n) {
        if (n === 'db') return db;
        if (n === 'user') return { me: async function () { return { id: me, isOwner: false, canEdit: false }; } };
        return null;
      } }
    };
    return '<div class="folie"><iframe src="pinnwand.html?v=' + PIN_VER + '" title="Pinnwand"></iframe></div>';
  };
  ACT.kPin = function () { K.step = 'pin'; K.render(); };
  K.view_atelier = function () {
    var kid = K.home && K.home.kid; if (!kid) { K.step = 'home'; return K.view_home(); }
    window.knAtelier = {
      mode: 'kid', me: kid.id, className: '',
      back: function () { ACT.kBack(); },
      load: async function () { var d = await DB.kidAtelier(K.sess.token); if (!d) return null;
        return { open: !!d.open, arten: d.arten || [], kids: (d.kids || []).map(function (k) { return { id: k.id, name: k.name, thema: k.thema || '', umsetzung: k.umsetzung || '', farbe: k.farbe || '', x: k.x == null ? null : k.x, y: k.y == null ? null : k.y }; }) }; },
      put: function (id, patch) { if (id !== kid.id) return Promise.reject(new Error('Nicht erlaubt')); return DB.kidAtelierSet(K.sess.token, JSON.parse(JSON.stringify(patch))); },
      setOpen: function () { return Promise.reject(new Error('Nicht erlaubt')); }
    };
    return '<div class="folie"><iframe src="atelier.html?v=' + ATELIER_VER + '" title="Atelier" allow="fullscreen"></iframe></div>';
  };
  ACT.kAtelier = function () { K.step = 'atelier'; K.render(); };
  // Kinder-Quiz: dieselbe Seite quiz.html, nur die eigenen Quiz (bzw. die der eigenen Gruppe)
  K.view_quiz = function () {
    if (!K.sess) { K.step = 'home'; return K.view_home(); }
    var tok = K.sess.token;
    window.knQuiz = {
      mode: 'kid', name: (K.home && K.home.kid && K.home.kid.name) || '',
      back: function () { ACT.kBack(); },
      kidList: function () { return DB.kidQuizList(tok); },
      kidGet: function (id, ver) { return DB.kidQuizGet(tok, id, ver); },
      kidSave: function (id, ver, title, data) { return DB.kidQuizSave(tok, id, ver, title, JSON.parse(JSON.stringify(data))); },
      kidDelete: function (id) { return DB.kidQuizDelete(tok, id); }
    };
    return '<div class="folie"><iframe src="quiz.html?v=' + QUIZ_VER + '" title="Quiz erstellen" allow="fullscreen"></iframe></div>';
  };
  ACT.kQuiz = function () { K.step = 'quiz'; K.render(); };
  ACT.kHeft = function () { K.step = 'heft'; K.render(); };
  K.view_tafel = function () {
    if (!K.tafel) return K.shell('<p class="lead">Tafel wird geladen …</p>', 'Zurück');
    return board(K.tafel, 'kid');
  };

  ACT.kCode = async function (f) {
    var code = f.elements.code.value.trim(); if (!code) return;
    var c = await DB.kidClass(code);
    if (c && c.pausiert) { K.err = 'Eure ' + C.PORTAL_NAME + ' ist gerade pausiert. Sag es deiner Lehrperson.'; return K.render(); }
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
          r.error === 'unbekannt' ? 'Das hat nicht geklappt. Gib den Code nochmals ein.' :
          r.error === 'pausiert' ? 'Eure ' + C.PORTAL_NAME + ' ist gerade pausiert. Sag es deiner Lehrperson.' : 'Das waren nicht deine Bilder. Versuch es nochmals.';
        if (r.error === 'unbekannt' || r.error === 'pausiert') { if (r.error === 'unbekannt') LS.del('kn_code'); K.step = 'code'; }
        return K.render();
      }
      K.sess = { token: r.token, name: r.name, code: K.code, kid: K.kid && K.kid.id, exp: Date.now() + 11.5 * 3600 * 1000 };
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
      case 'heft': K.step = 'home'; K.render(); break;
      case 'pin': K.step = 'home'; K.render(); K.checkHeft(); break;
      case 'atelier': K.step = 'home'; K.render(); K.checkHeft(); break;
      case 'umfrage': clearInterval(K.umfIv); K.U = null; K.step = 'home'; K.render(); K.checkRace(); break;
      case 'quiz': K.step = 'home'; K.loadHome(); break;
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
    if (/<script[^>]*id=["']vk-content["']/i.test(html || '')) return { modus: 'eigene' }; // Vokabelkiste: Tagessterne zählt sie selbst
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
  function fmtDay(ms) {
    var d = new Date(ms), t = new Date(); t.setHours(0, 0, 0, 0);
    var diff = Math.round((t - new Date(d.getFullYear(), d.getMonth(), d.getDate())) / 864e5);
    return diff === 0 ? 'heute' : diff === 1 ? 'gestern' : d.getDate() + '.' + (d.getMonth() + 1) + '.' + (d.getFullYear() !== t.getFullYear() ? d.getFullYear() : '');
  }
  function fmtTime(ms) { var t = Math.round(ms / 1000), m = Math.floor(t / 60); t %= 60; return m + ':' + (t < 10 ? '0' : '') + t; }
  function awardSum(a) { var n = 0, lv = (a && a.lv) || {}; Object.keys(lv).forEach(function (k) { n += +lv[k] || 0; }); return n; }
  // Kurztext für Übersichten: "⭐ 7 · ⏱️ 3:12"
  function awardText(a) {
    if (!a) return '';
    if (a.zr) return Object.keys(a.zr).map(function (k) { var z = a.zr[k];
      return z.name + ': ' + (!z.open && !z.f && z.best == null ? '🔒' : (z.t ? z.f + '/' + z.t + ' entdeckt' : 'offen') + (z.best != null ? ', Quiz ' + z.best + '/' + z.n + (z.ok ? ' ✓' : '') : '')); }).join(' · ');
    var parts = [], st = typeof a.stars === 'number' ? a.stars : awardSum(a);
    if (st) parts.push('⭐ ' + st + ' ' + (st === 1 ? 'Stern' : 'Sterne'));
    if (a.best) parts.push('⏱️ Bestzeit ' + fmtTime(a.best) + (a.last ? ' (zuletzt ' + fmtDay(a.last) + ')' : ''));
    else if (a.last) parts.push('zuletzt ' + fmtDay(a.last));
    return parts.join(' · ');
  }
  // Vocibox: pro Box eine Zeile mit den Fächern 1–5
  function vbHTML(a) {
    if (!a || !a.vb) return '';
    return '<span class="vbx">' + Object.keys(a.vb).map(function (k) { var v = a.vb[k];
      return '<span class="vbr"><span class="vbn">📦 ' + h(v.name) + '</span><span class="vbf">' + v.c.map(function (n, i) {
        return '<i class="f' + (i + 1) + (n ? '' : ' z') + '" title="Fach ' + (i + 1) + ': ' + n + ' Wörter"><small>' + (i + 1) + '</small>' + n + '</i>'; }).join('') + '</span></span>';
    }).join('') + '</span>';
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
      if (isFinite(x.last) && x.last > 0) a.last = Math.round(x.last);
      if (x.best == null || isFinite(x.best)) a.best = x.best == null ? null : Math.max(0, Math.round(x.best));
      if (x.zr && typeof x.zr === 'object') {
        a.zr = {};
        Object.keys(x.zr).slice(0, 12).forEach(function (k) { var z = x.zr[k] || {};
          a.zr[String(k).slice(0, 30)] = { name: String(z.name || k).slice(0, 30), f: +z.f || 0, t: +z.t || 0, best: z.best == null ? null : +z.best, n: +z.n || 10, tries: +z.tries || 0, ok: !!z.ok, open: !!z.open }; });
      }
      if (x.vb && typeof x.vb === 'object') {
        a.vb = {};
        Object.keys(x.vb).slice(0, 8).forEach(function (k) { var v = x.vb[k] || {};
          a.vb[String(k).slice(0, 30)] = { name: String(v.name || k).slice(0, 40), c: (Array.isArray(v.c) ? v.c : []).slice(0, 8).map(function (n) { return Math.max(0, Math.round(+n || 0)); }), lock: Math.max(0, Math.round(+v.lock || 0)) }; });
      }
      if (x.vk && typeof x.vk === 'object') {
        var sec = {}, xs = x.vk.sec && typeof x.vk.sec === 'object' ? x.vk.sec : {};
        Object.keys(xs).filter(function (k) { return /^\d{4}-\d{2}-\d{2}$/.test(k); }).sort().slice(-40).forEach(function (k) { sec[k] = Math.max(0, Math.min(86400, Math.round(+xs[k] || 0))); });
        a.vk = { streak: Math.max(0, Math.round(+x.vk.streak || 0)), weeks: Math.max(0, Math.round(+x.vk.weeks || 0)), fach5: Math.max(0, Math.round(+x.vk.fach5 || 0)), sec: sec };
      }
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
    if (gameUrl(html) === 'vokabelkiste/index.html') {
      var frei = []; try { frei = vkFree((await DB.kidHeft(K.sess.token)) || {}); } catch (e) {}
      st.settings = Object.assign({}, st.settings || {}, { frei: frei });
    }
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
    }, async function () { clearInterval(t); await flush(); K.loadHome(); }, { store: st.save, award: S.view(), settings: st.settings || null, levels: g.levels || {} });
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
    try { var u = await DB.kidUmfrage(K.sess.token), uo = u ? String(u.sid || '1') : null; if (uo !== (K.umfOpen || null)) { K.umfOpen = uo; if (K.step === 'home') K.render(); } }
    catch (e) {}
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

  // ---------- Kinder: Umfrage beantworten ----------
  // Eingabe für eine Frage. dr = Entwurf des Kindes (null = Vorschau in der Bearbeitung)
  function umfDraft0(q) {
    var n = (q.opts || []).length, z = []; for (var i = 0; i < n; i++) z.push(0);
    if (q.type === 'rang') return z.map(function (x, i) { return i; });
    if (q.type === 'skala') return z.map(function () { return null; });
    if (q.type === 'punkte') return z;
    if (q.type === 'wort' || q.type === 'text') return [];
    if (q.type === 'zahl') return '';
    if (q.type === 'feld') return null;
    return [];
  }
  function umfInput(q, dr, prev) {
    var t = q.type, opts = q.opts || [];
    if (dr == null) dr = umfDraft0(q);
    if (t === 'info') return '<p class="ku-info">' + h(q.sub || '') + '</p>';
    if (t === 'wahl' || t === 'quiz') return '<div class="ku-opts">' + opts.map(function (x, i) {
      var on = dr.indexOf(i) >= 0;
      return '<button class="ku-opt' + (on ? ' on' : '') + '" style="--c:' + UMF_COL[i % UMF_COL.length] + '" data-a="kuPick" data-i="' + i + '" aria-pressed="' + on + '"><span class="ku-mark">' + (q.multi ? (on ? '✓' : '') : String.fromCharCode(65 + i)) + '</span><span>' + h(x) + '</span></button>';
    }).join('') + '</div>' + (q.multi ? '<p class="ku-hint">Du darfst mehrere wählen.</p>' : '');
    if (t === 'stimmung') return '<div class="ku-emos" style="--n:' + opts.length + '">' + opts.map(function (x, i) {
      var e = umfEmo(x), on = dr.indexOf(i) >= 0;
      return '<button class="ku-emo' + (on ? ' on' : '') + '" data-a="kuPick" data-i="' + i + '" aria-pressed="' + on + '"><span class="e">' + (e[0] || '•') + '</span><small>' + h(e[1]) + '</small></button>'; }).join('') + '</div>';
    if (t === 'wort' || t === 'text') {
      var m = Math.max(1, +q.max || 1), o = '<div class="ku-ins">';
      for (var i = 0; i < m; i++) o += t === 'wort' ? '<input class="kid-input ku-in" id="kuW' + i + '" data-input="kuW" data-i="' + i + '" maxlength="30" autocomplete="off" placeholder="' + (m > 1 ? (i + 1) + '. Wort' : 'Dein Wort') + '" value="' + h(dr[i] || '') + '">'
        : '<textarea class="kid-input ku-in ku-ta" id="kuW' + i + '" data-input="kuW" data-i="' + i + '" maxlength="300" rows="3" placeholder="' + (m > 1 ? (i + 1) + '. Antwort' : 'Schreib hier deine Antwort') + '">' + h(dr[i] || '') + '</textarea>';
      return o + '</div>' + (t === 'wort' ? '<p class="ku-hint">' + (m > 1 ? 'Bis zu ' + m + ' Wörter, ' : '') + 'kurz und knapp.</p>' : '');
    }
    if (t === 'skala') {
      var mx = umfSkMax(q);
      return '<div class="ku-skala">' + opts.map(function (st, i) {
        var o = ''; for (var v = 1; v <= mx; v++) o += '<button class="ku-skb' + (dr[i] === v ? ' on' : '') + '" data-a="kuSk" data-i="' + i + '" data-v="' + v + '">' + v + '</button>';
        return '<div class="ku-sk">' + (opts.length > 1 || st ? '<p>' + h(st) + '</p>' : '') + '<div class="ku-skr" style="--m:' + mx + '">' + o + '</div><div class="ku-ends"><span>' + h(q.lo || '') + '</span><span>' + h(q.hi || '') + '</span></div></div>';
      }).join('') + '</div>';
    }
    if (t === 'rang') return '<p class="ku-hint">Das Wichtigste ganz nach oben.</p><ol class="ku-rang">' + dr.map(function (oi, p) {
      return '<li><span class="ku-p">' + (p + 1) + '</span><span class="ku-l">' + h(opts[oi]) + '</span><button data-a="kuRang" data-p="' + p + '" data-d="-1" aria-label="Nach oben"' + (p ? '' : ' disabled') + '>▲</button><button data-a="kuRang" data-p="' + p + '" data-d="1" aria-label="Nach unten"' + (p < dr.length - 1 ? '' : ' disabled') + '>▼</button></li>';
    }).join('') + '</ol>';
    if (t === 'punkte') {
      var P = Math.min(100, Math.max(1, +q.pts || 10)), used = 0; dr.forEach(function (x) { used += x; });
      return '<p class="ku-left">Noch <b>' + (P - used) + '</b> ⭐ übrig</p><div class="ku-pts">' + opts.map(function (x, i) {
        return '<div class="ku-pt"><span class="ku-l">' + h(x) + '</span><button data-a="kuPts" data-i="' + i + '" data-d="-1" aria-label="Weniger"' + (dr[i] ? '' : ' disabled') + '>−</button><b>' + (dr[i] || 0) + ' ⭐</b><button data-a="kuPts" data-i="' + i + '" data-d="1" aria-label="Mehr"' + (used < P ? '' : ' disabled') + '>+</button></div>';
      }).join('') + '</div>';
    }
    if (t === 'zahl') return '<div class="ku-zahl"><input class="kid-input" id="kuZ" data-input="kuZ" inputmode="decimal" autocomplete="off" placeholder="Deine Zahl" value="' + h(dr) + '">' + (q.unit ? '<span>' + h(q.unit) + '</span>' : '') + '</div>' +
      (q.min != null && q.max != null ? '<p class="ku-hint">Eine Zahl von ' + umfFmtNum(q.min) + ' bis ' + umfFmtNum(q.max) + '.</p>' : '');
    if (t === 'feld') return '<p class="ku-hint">Tippe ins Feld, wo du gerade bist.</p>' + umfFeld(q.ax || [], dr ? '<span class="ur-dot me" style="left:' + dr.x + '%;top:' + (100 - dr.y) + '%"></span>' : '', true, prev ? null : 'kuFeld');
    return '';
  }
  // Fertige Antwort aus dem Entwurf (null = noch nicht fertig)
  function umfVal(q, dr) {
    var t = q.type;
    if (dr == null) return null;
    if (t === 'wahl' || t === 'quiz' || t === 'stimmung') return dr.length ? dr.slice() : null;
    if (t === 'wort' || t === 'text') { var a = dr.map(function (x) { return String(x || '').trim(); }).filter(Boolean); return a.length ? a : null; }
    if (t === 'skala') return dr.every(function (x) { return x >= 1; }) ? dr.slice() : null;
    if (t === 'rang') return dr.slice();
    if (t === 'punkte') { var s = 0; dr.forEach(function (x) { s += x; }); return s ? dr.slice() : null; }
    if (t === 'zahl') { var x = umfNum(dr); if (x === null || (q.min != null && x < q.min) || (q.max != null && x > q.max)) return null; return x; }
    if (t === 'feld') return dr;
    return null;
  }
  K.umfQ = function () {
    var d = K.U && K.U.d; if (!d || !d.qs.length) return null;
    if (d.mode !== 'selbst') return d.qs[0];
    K.U.i = Math.max(0, Math.min(K.U.i || 0, d.qs.length - 1)); return d.qs[K.U.i];
  };
  K.umfDr = function (q) {
    var U2 = K.U; if (U2.dr[q.id] !== undefined) return U2.dr[q.id];
    var m = U2.d.mine[q.id], d;
    if (m === undefined) d = umfDraft0(q);
    else if (q.type === 'zahl') d = String(m).replace('.', ',');
    else d = JSON.parse(JSON.stringify(m));
    U2.dr[q.id] = d; return d;
  };
  K.umfLoad = async function () {
    var U2 = K.U; if (!U2) return; var gt = U2.guest, d;
    try { d = gt ? await DB.umfGast(gt) : await DB.kidUmfrage(K.sess.token); } catch (e) { return gt ? null : K.sessionLost(e); }
    U2 = K.U; if (!U2 || K.step !== 'umfrage') return;
    if (gt && d && d.gone) { LS.del('kn_umf_gast'); clearInterval(K.umfIv); K.U = null; K.step = 'gast'; K.err = 'Diese Umfrage gibt es nicht mehr.'; return K.render(); }
    var sig = JSON.stringify(d ? Object.assign({}, d, { now: 0 }) : null);
    if (d) U2.off = d.now - Date.now();
    if (sig === U2.sig) return; U2.sig = sig;
    // Neue Frage oder neue Umfrage: alte Entwürfe weg
    if (!d || !U2.d || d.sid !== U2.d.sid) { U2.dr = {}; U2.edit = {}; U2.i = 0; }
    else if (d.mode !== 'selbst' && d.cur !== U2.d.cur) { U2.edit = {}; }
    U2.d = d; K.render();
  };
  ACT.kUmf = function () { K.umfBegin(null); };
  K.umfBegin = function (guest, gname) {
    K.step = 'umfrage'; K.U = { d: null, dr: {}, edit: {}, i: 0, sig: '', off: 0, first: true, guest: guest || null, gname: gname || '' }; K.render();
    K.umfLoad(); clearInterval(K.umfIv); var n = 0;
    K.umfIv = setInterval(function () {
      if (UI.view !== 'kid' || K.step !== 'umfrage' || !K.U) { clearInterval(K.umfIv); return; }
      var d = K.U.d, el = document.getElementById('kuTimer');
      if (el && d && d.until) { var s = Math.ceil((d.until - (Date.now() + K.U.off)) / 1000); el.textContent = s > 0 ? '⏱ Noch ' + umfSec(s) : '⏱ Die Zeit ist um'; }
      if (++n % 4 === 0 && !document.hidden) K.umfLoad();
    }, 500);
  };
  K.view_umfrage = function () {
    var U2 = K.U, d = U2 && U2.d, g = U2 && U2.guest, back = g ? null : 'Zurück';
    var brand = g ? '<div class="ku-brand"><img src="bilder/eule.webp" alt="" width="40" height="40"><span>' + h(C.PORTAL_NAME) + (U2.gname ? ' · ' + h(U2.gname) : '') + '</span></div>' : '';
    if (!U2 || (!d && U2.sig === '')) return K.shell(brand + '<div class="kid-card"><p class="lead">Umfrage wird geladen …</p></div>', back);
    if (!d) return K.shell(brand + '<div class="kid-card"><div class="ku-big">🎉</div><h1>Die Umfrage ist fertig</h1><p class="lead">Danke fürs Mitmachen!</p>' + (g ? '' : '<button class="kid-go" data-a="kBack">Zurück</button>') + '</div>', back);
    var q = K.umfQ(), selbst = d.mode === 'selbst';
    if (!q) return K.shell(brand + '<div class="kid-card"><div class="ku-big">👀</div><h1>Schau nach vorne</h1><p class="lead">Gleich kommt die nächste Frage.</p></div>', back);
    var mine = d.mine[q.id], t = umfType(q.type), rev = (d.rev || []).indexOf(q.id) >= 0, editing = U2.edit[q.id] || mine === undefined;
    var o = brand + '<div class="kid-card ku">';
    if (selbst) o += '<div class="ku-dots">' + d.qs.map(function (x, j) { return '<button class="ku-d' + (j === U2.i ? ' cur' : '') + (d.mine[x.id] !== undefined || x.type === 'info' ? ' ok' : '') + '" data-a="kuGo" data-i="' + j + '" aria-label="Frage ' + (j + 1) + '">' + (j + 1) + '</button>'; }).join('') + '</div>';
    o += '<span class="ku-nr">' + t[2] + ' ' + h(d.title || 'Umfrage') + '</span><h1 class="ku-q">' + h(q.text) + '</h1>';
    if (d.until && d.open) o += '<p class="ku-timer" id="kuTimer"></p>';
    if (q.type === 'info') o += umfInput(q, null) + (selbst ? '' : '<p class="lead">Schau nach vorne an die Wandtafel.</p>');
    else if (!editing) {
      o += '<div class="ku-done"><span class="ku-big">✓</span><b>Danke! Deine Antwort ist angekommen.</b><span>' + h(umfFmt(q, mine)) + '</span></div>';
      if (rev && umfHasOk(q)) o += q.type === 'quiz' ? (umfQuizOk(q, mine) ? '<p class="ku-rich ok">🎉 Richtig!</p>' : '<p class="ku-rich no">Die richtige Antwort ist: <b>' + h((q.ok || []).map(function (i) { return q.opts[i]; }).join(', ')) + '</b></p>')
        : '<p class="ku-rich">Die Lösung ist <b>' + umfFmtNum(q.ok) + (q.unit ? ' ' + h(q.unit) : '') + '</b>. Du hast ' + umfFmtNum(+mine) + ' geschätzt.</p>';
      if (d.open) o += '<button class="kid-btn" data-a="kuEdit">Antwort ändern</button>';
    } else if (!d.open) o += '<p class="lead">Die Abstimmung ist geschlossen.</p>';
    else {
      var dr = K.umfDr(q);
      o += umfInput(q, dr) + '<button class="kid-go" data-a="kuSend"' + (umfVal(q, dr) == null ? ' disabled' : '') + '>Abschicken</button>';
      if (mine !== undefined) o += '<button class="kid-btn" data-a="kuCancel">Nicht ändern</button>';
    }
    if (d.show && d.res[q.id] && q.type !== 'info' && (mine !== undefined || !d.open)) o += '<div class="ku-res"><span class="ku-nr">' + (g ? 'So haben alle geantwortet' : 'So hat die Klasse geantwortet') + '</span>' + umfRes(q, d.res[q.id].map(function (v) { return { v: v }; }), { small: true, rev: rev }) + '</div>';
    if (selbst) {
      var last = U2.i >= d.qs.length - 1, all = d.qs.every(function (x) { return x.type === 'info' || d.mine[x.id] !== undefined; });
      o += '<div class="ku-nav"><button class="kid-btn" data-a="kuStep" data-d="-1"' + (U2.i ? '' : ' disabled') + '>◀ Zurück</button>' +
        (last ? (all ? '<span class="ku-fertig">🎉 Fertig! Danke.</span>' : '') : '<button class="kid-btn" data-a="kuStep" data-d="1">Weiter ▶</button>') + '</div>';
    }
    return K.shell(o + '</div>', back);
  };
  // Gäste: #/u/<Nummer> → Name (freiwillig) → Umfrage (Token in localStorage «kn_umf_gast»)
  var G = {
    start: function (nr) {
      UI.view = 'kid'; K.err = '';
      var s = LS.get('kn_umf_gast');
      if (s && s.token && (!nr || s.nr === nr)) return K.umfBegin(s.token, s.name);
      K.gnr = nr || ''; K.step = 'gast'; K.render();
    }
  };
  K.view_gast = function () {
    return K.shell('<div class="ku-brand"><img src="bilder/eule.webp" alt="" width="40" height="40"><span>' + h(C.PORTAL_NAME) + '</span></div>' +
      '<form class="kid-card" data-a="gJoin"><div class="ku-big">📊</div><h1>Bei der Umfrage mitmachen</h1>' +
      (K.gnr ? '<p class="lead">Nummer <b>' + h(umfNr(K.gnr)) + '</b></p><input type="hidden" name="nr" value="' + h(K.gnr) + '">'
        : '<label class="sr" for="gNr">Nummer</label><input class="kid-input ku-in" id="gNr" name="nr" inputmode="numeric" autocomplete="off" placeholder="Nummer (6 Ziffern)" required>') +
      '<label class="sr" for="gName">Dein Name</label><input class="kid-input ku-in" id="gName" name="name" maxlength="20" autocomplete="off" placeholder="Dein Name (freiwillig)">' +
      '<p class="err" style="font-size:18px">' + h(K.err) + '</p><button class="kid-go">Mitmachen</button></form>', null);
  };
  ACT.gJoin = async function (f) {
    var nr = String(f.elements.nr.value || '').replace(/\D/g, ''), name = f.elements.name.value.trim();
    if (nr.length !== 6) { K.err = 'Die Nummer hat 6 Ziffern.'; return K.render(); }
    var r = await DB.umfGastJoin(nr, name);
    if (!r || !r.ok) {
      K.err = { nummer: 'Diese Nummer gibt es nicht. Schau nochmals genau.', vorbei: 'Diese Umfrage ist schon fertig.', name: 'Bitte einen anderen Namen wählen (ohne < und >).', voll: 'Es machen schon sehr viele mit.' }[r && r.error] || 'Das hat nicht geklappt.';
      if (r && r.error === 'nummer') K.gnr = '';
      return K.render();
    }
    LS.set('kn_umf_gast', { nr: nr, token: r.token, name: r.name });
    K.umfBegin(r.token, r.name);
  };
  ACT.kuGo = function (el) { K.U.i = +el.dataset.i; K.render(); window.scrollTo(0, 0); };
  ACT.kuStep = function (el) { K.U.i += +el.dataset.d; K.render(); window.scrollTo(0, 0); };
  ACT.kuEdit = function () { var q = K.umfQ(); K.U.edit[q.id] = true; delete K.U.dr[q.id]; K.render(); };
  ACT.kuCancel = function () { var q = K.umfQ(); delete K.U.edit[q.id]; delete K.U.dr[q.id]; K.render(); };
  function kuSendState() { var q = K.umfQ(), b = document.querySelector('[data-a="kuSend"]'); if (q && b) b.disabled = umfVal(q, K.umfDr(q)) == null; }
  ACT.kuPick = function (el) {
    var q = K.umfQ(), dr = K.umfDr(q), i = +el.dataset.i;
    if (q.multi) { var j = dr.indexOf(i); if (j >= 0) dr.splice(j, 1); else dr.push(i); } else { dr.length = 0; dr.push(i); }
    K.render();
  };
  ACT.kuW = function (el) { var q = K.umfQ(), dr = K.umfDr(q); dr[+el.dataset.i] = el.value; kuSendState(); };
  ACT.kuZ = function (el) { var q = K.umfQ(); K.U.dr[q.id] = el.value; kuSendState(); };
  ACT.kuSk = function (el) { var q = K.umfQ(), dr = K.umfDr(q); dr[+el.dataset.i] = +el.dataset.v; K.render(); };
  ACT.kuRang = function (el) { var q = K.umfQ(), dr = K.umfDr(q), p = +el.dataset.p, j = p + +el.dataset.d; if (j < 0 || j >= dr.length) return; var x = dr[p]; dr[p] = dr[j]; dr[j] = x; K.render(); };
  ACT.kuPts = function (el) {
    var q = K.umfQ(), dr = K.umfDr(q), i = +el.dataset.i, P = Math.min(100, Math.max(1, +q.pts || 10)), used = 0; dr.forEach(function (x) { used += x; });
    if (+el.dataset.d > 0 && used < P) dr[i]++; else if (+el.dataset.d < 0 && dr[i] > 0) dr[i]--; K.render();
  };
  ACT.kuFeld = function (el, ev) {
    var q = K.umfQ(), r = el.getBoundingClientRect(); if (!ev || !r.width) return;
    K.U.dr[q.id] = { x: Math.round(Math.max(0, Math.min(100, (ev.clientX - r.left) / r.width * 100)) * 10) / 10, y: Math.round(Math.max(0, Math.min(100, 100 - (ev.clientY - r.top) / r.height * 100)) * 10) / 10 };
    K.render();
  };
  ACT.kuSend = async function () {
    var U2 = K.U, q = K.umfQ(); if (!q || U2.busy) return;
    var v = umfVal(q, K.umfDr(q)); if (v == null) return;
    U2.busy = true;
    try {
      var ok = U2.guest ? await DB.umfGastSend(U2.guest, q.id, v) : await DB.kidUmfrageSend(K.sess.token, q.id, v);
      if (!ok) { toast('Das hat nicht geklappt. Vielleicht ist die Abstimmung schon geschlossen.'); U2.sig = ''; return K.umfLoad(); }
      U2.d.mine[q.id] = v; delete U2.edit[q.id]; delete U2.dr[q.id]; U2.sig = '';
      K.render(); K.umfLoad();
    } catch (e) { if (U2.guest) toast(errMsg(e)); else K.sessionLost(e); }
    finally { U2.busy = false; }
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
      paint('<main class="main" style="max-width:560px"><form class="card stack" data-a="recoverPw"><h1 class="h1">' + (invite ? 'Willkommen in der ' + h(C.PORTAL_NAME) + '!' : 'Neues Passwort') + '</h1>' +
        (invite ? '<p class="muted">Legen Sie jetzt Ihr eigenes Passwort fest. Damit melden Sie sich künftig mit Ihrer E-Mail-Adresse an.</p>' : '') +
        '<div class="field"><label for="rcPw">Neues Passwort (mindestens 8 Zeichen)</label><input class="input" id="rcPw" name="pw" type="password" minlength="8" autocomplete="new-password" required></div>' +
        '<button class="btn primary">Speichern</button></form></main>');
    }
  });
  ACT.recoverPw = async function (f) { await DB.setPassword(f.elements.pw.value); toast('Passwort gespeichert.'); history.replaceState(null, '', location.pathname + '#/'); UI.view = null; T.start(); };

  window.addEventListener('hashchange', route);
  route();
})();
