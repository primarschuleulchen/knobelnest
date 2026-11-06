// In-memory stand-in for db.js, mirroring the SQL functions' behaviour.
(function () {
  var uid = function () { return 'xxxxxxxx-xxxx-4xxx-8xxx-xxxxxxxxxxxx'.replace(/x/g, function () { return (Math.random() * 16 | 0).toString(16); }); };
  var now = function () { return new Date().toISOString(); };
  // Eingebettet (z. B. ganzes Heft in der Tagesfolie): dieselbe Schein-Datenbank wie das oberste Fenster
  var TOP = null; try { TOP = window.top !== window && window.top.__D; } catch (e) {}
  var D = TOP || {
    session: null,
    profiles: [{ id: 'u-admin-0000-0000-0000-000000000001', email: 'admin@x.ch', name: null, is_admin: true, created_at: now() },
               { id: 'u-lp-00000-0000-0000-000000000002', email: 'lp@x.ch', name: 'Herr Muster', is_admin: false, created_at: now(), valid_until: null }],
    games: [], teacher_games: [], classes: [], kids: [], class_games: [], progress: [], sessions: {}, subjects: [], entries: []
  };
  var GAME_HTML = '<!doctype html><html><head><title>Testspiel</title></head><body><h1 id="h">Testspiel</h1>' +
    '<button id="ok" onclick="window.__report&&__report(true);parent.postMessage({spielheft:1,type:\'answer\',ok:true},\'*\')">Richtig</button>' +
    '<button id="pr" onclick="knobelnest.progress(7,20)">Fortschritt</button>' +
    '<script>try{localStorage.setItem("a","1");document.getElementById("h").textContent+=" (Speicher ok: "+localStorage.getItem("a")+")"}catch(e){document.getElementById("h").textContent+=" Speicher-Fehler"}<\/script></body></html>';
  var me = function () { return D.profiles.filter(function (p) { return D.session && p.id === D.session.user.id; })[0]; };
  var delay = function (v) { return new Promise(function (r) { setTimeout(function () { r(JSON.parse(JSON.stringify(v === undefined ? null : v))); }, 30); }); };
  var norm = function (c) { return String(c || '').replace(/\s/g, '').toUpperCase(); };
  function licOk(cid) {
    var c = D.classes.filter(function (x) { return x.id === cid; })[0], p = c && D.profiles.filter(function (x) { return x.id === c.teacher_id; })[0];
    return !p || p.is_admin || !p.valid_until || p.valid_until >= new Date().toLocaleDateString('sv-SE');
  }
  function kidOf(token) { var s = D.sessions[token]; if (!s) throw new Error('Anmeldung abgelaufen');
    var k = D.kids.filter(function (k) { return k.id === s; })[0];
    if (!licOk(k.class_id)) throw new Error('Eure Klassenkiste ist gerade pausiert. Sag es deiner Lehrperson.'); return k; }
  function hasGame(tid, gid) {
    var g = D.games.filter(function (x) { return x.id === gid; })[0]; if (!g) return false;
    var p = D.profiles.filter(function (x) { return x.id === tid; })[0];
    return g.for_all || (p && p.is_admin) || D.teacher_games.some(function (t) { return t.teacher_id === tid && t.game_id === gid; });
  }
  function state(cid) {
    var subs = D.subjects.filter(function (s) { return s.class_id === cid && s.active; });
    return { class_name: D.classes.filter(function (c) { return c.id === cid; })[0].name,
      subjects: subs.map(function (s) { return { id: s.id, name: s.name, color: s.color }; }),
      kids: D.kids.filter(function (k) { return k.class_id === cid; }).map(function (k) { return { id: k.id, name: k.name }; }),
      entries: D.entries.filter(function (e) { return e.class_id === cid && subs.some(function (s) { return s.id === e.subject_id; }); }) };
  }
  function quizLeft(l) { return l.phase === 'frage' ? Math.max(0, (l.questions[l.q].zeit || 20) * 1000 - (Date.now() - l.q_started)) : null; }
  function kqNames(ids) { return D.kids.filter(function (k) { return ids.indexOf(k.id) >= 0; }).map(function (k) { return { id: k.id, name: k.name }; }); }
  function kqMine(id) { var q = (D.kq || []).filter(function (x) { return x.id === id; })[0]; if (!q) return null; var c = D.classes.filter(function (x) { return x.id === q.class_id; })[0]; return c && c.teacher_id === me().id ? q : null; }
  // Umfrage: dieselben Regeln wie _umf_apply / _umf_view / _umf_val in schema.sql
  function umfApply(d, live, clear) { var n = Date.now();
    if (live) { live = JSON.parse(JSON.stringify(live)); if (typeof live.sec === 'number') { live.until = live.sec > 0 ? n + live.sec * 1000 : null; delete live.sec; } d.live = live; }
    d.ans = d.ans || {}; (clear || []).forEach(function (q) { if (q === '*') d.ans = {}; else delete d.ans[q]; }); return { now: n, until: d.live ? d.live.until || null : null }; }
  function umfView(d, me) { var l = d && d.live; if (!l || !l.on) return null; var sh = !!l.show && l.kids !== false, out = { sid: l.sid, title: l.title, mode: l.mode || 'live', cur: l.cur, open: !!l.open, show: sh, until: l.until || null, now: Date.now(), rev: l.rev || [], qs: [], mine: {}, res: {} };
    (l.qs || []).forEach(function (q) { if ((l.mode || 'live') !== 'selbst' && q.id !== l.cur) return; q = JSON.parse(JSON.stringify(q)); if ((l.rev || []).indexOf(q.id) < 0) delete q.ok; out.qs.push(q);
      var a = (d.ans || {})[q.id] || {}; if (a[me] !== undefined) out.mine[q.id] = a[me];
      if (sh) { var hk = (l.hid || {})[q.id] || [], hw = (l.hidw || {})[q.id] || []; out.res[q.id] = Object.keys(a).filter(function (id) { return hk.indexOf(id) < 0; }).map(function (id) {
        var v = a[id]; return q.type === 'wort' && Array.isArray(v) ? v.filter(function (w) { return hw.indexOf(String(w).toLowerCase()) < 0; }) : v; }); } });
    return JSON.parse(JSON.stringify(out)); }
  function umfVal(l, qid, v) {
    if (!l || !l.on || !l.open || (l.until && Date.now() > l.until + 3000) || ((l.mode || 'live') !== 'selbst' && qid !== l.cur)) return null;
    var q = (l.qs || []).filter(function (x) { return x.id === qid; })[0]; if (!q) return null; var n = (q.opts || []).length, ints = function (a, lo, hi) { return Array.isArray(a) && a.every(function (x) { return typeof x === 'number' && x % 1 === 0 && x >= lo && x <= hi; }); };
    var dist = function (a) { return a.filter(function (x, i) { return a.indexOf(x) === i; }).length === a.length; }, ok = false;
    if (/^(wahl|quiz|stimmung)$/.test(q.type)) ok = ints(v, 0, n - 1) && v.length >= 1 && v.length <= (q.multi ? n : 1) && dist(v);
    else if (/^(wort|text)$/.test(q.type)) { v = Array.isArray(v) ? v.filter(function (x) { return typeof x === 'string' && x.trim(); }).map(function (x) { return x.trim().slice(0, q.type === 'wort' ? 30 : 300); }) : []; ok = v.length >= 1 && v.length <= Math.min(q.type === 'wort' ? 5 : 3, Math.max(1, +q.max || (q.type === 'wort' ? 3 : 1))); }
    else if (q.type === 'skala') ok = ints(v, 1, Math.min(10, Math.max(3, +q.max || 5))) && v.length === n;
    else if (q.type === 'rang') ok = ints(v, 0, n - 1) && v.length === n && dist(v);
    else if (q.type === 'punkte') { var P = Math.min(100, Math.max(1, +q.pts || 10)), s = 0; ok = ints(v, 0, P) && v.length === n; if (ok) v.forEach(function (x) { s += x; }); ok = ok && s >= 1 && s <= P; }
    else if (q.type === 'zahl') ok = typeof v === 'number' && !(q.min !== '' && q.min != null && v < +q.min) && !(q.max !== '' && q.max != null && v > +q.max);
    else if (q.type === 'feld') { ok = v && typeof v.x === 'number' && typeof v.y === 'number'; if (ok) v = { x: Math.max(0, Math.min(100, v.x)), y: Math.max(0, Math.min(100, v.y)) }; }
    return ok ? JSON.parse(JSON.stringify(v)) : null; }
  window.__D = D;
  window.DB = {
    session: function () { return delay(D.session); },
    onAuth: function () {},
    signIn: function (email, pw) {
      var p = D.profiles.filter(function (x) { return x.email === email; })[0];
      if (!p || pw !== 'test1234') return Promise.reject(new Error('Invalid login credentials'));
      D.session = { user: { id: p.id, email: p.email } }; return delay({});
    },
    signOut: function () { D.session = null; return delay(); },
    setPassword: function () { return delay({}); },
    me: function () { return delay(me() || null); },
    setMyName: function (id, n) { me().name = n; return delay(); },
    listGames: function () { var m = me(); return delay(D.games.filter(function (g) { return hasGame(m.id, g.id); }).sort(function (a, b) { return a.fach.localeCompare(b.fach) || a.thema.localeCompare(b.thema) || (a.sort || 0) - (b.sort || 0) || a.title.localeCompare(b.title); }).map(function (g) { var c = Object.assign({}, g); delete c.html; return c; })); },
    gameHtml: function (id) { return delay(D.games.filter(function (g) { return g.id === id; })[0].html); },
    saveGame: function (g) {
      if (g.id) { var x = D.games.filter(function (y) { return y.id === g.id; })[0]; Object.assign(x, g, { html: g.html || x.html }); return delay(x); }
      var n = Object.assign({ sort: 0 }, g, { id: uid(), created_at: now() }); D.games.push(n); return delay(n);
    },
    deleteGame: function (id) { D.games = D.games.filter(function (g) { return g.id !== id; }); return delay(); },
    setGameOrder: function (ids) { ids.forEach(function (id, i) { D.games.filter(function (g) { return g.id === id; })[0].sort = i + 1; }); window.__orders = (window.__orders || 0) + 1; return delay(); },
    setGameForAll: function (id, on) { D.games.filter(function (g) { return g.id === id; })[0].for_all = on; return delay(); },
    setTeacherGames: function (t, ids, on) { D.teacher_games = D.teacher_games.filter(function (x) { return !(x.teacher_id === t && ids.indexOf(x.game_id) >= 0); }); if (on) ids.forEach(function (g) { D.teacher_games.push({ teacher_id: t, game_id: g }); }); return delay(); },
    listTeachers: function () { return delay(D.profiles); },
    gameShop: function () { var m = me(); if (m.is_admin) return delay([]);
      return delay(D.games.filter(function (g) { return !g.for_all && !D.teacher_games.some(function (t) { return t.teacher_id === m.id && t.game_id === g.id; }); })
        .map(function (g) { return { id: g.id, title: g.title, description: g.description, fach: g.fach, thema: g.thema, stufe: g.stufe, price: g.price == null ? 1 : g.price }; })); },
    buyGame: function (gid) { var m = me(), g = D.games.filter(function (x) { return x.id === gid; })[0], pr = g.price == null ? 1 : g.price;
      if ((m.credits || 0) < pr) return Promise.reject(new Error('Zu wenig Guthaben'));
      m.credits = (m.credits || 0) - pr; D.teacher_games.push({ teacher_id: m.id, game_id: gid }); (D.log = D.log || []).push({ t: m.id, delta: -pr, note: g.title, at: now() }); return delay({ ok: true, credits: m.credits }); },
    addCredits: function (tid, d, note) { if (!me().is_admin) return Promise.reject(new Error('Nur für den Admin')); var p = D.profiles.filter(function (x) { return x.id === tid; })[0];
      p.credits = Math.max(0, (p.credits || 0) + d); (D.log = D.log || []).push({ t: tid, delta: d, note: note || '', at: now() }); return delay(p.credits); },
    gamePrices: function () { return delay(D.games.map(function (g) { return { id: g.id, price: g.price == null ? 1 : g.price }; })); },
    setGamePrice: function (gid, pr) { D.games.filter(function (g) { return g.id === gid; })[0].price = pr; return delay(); },
    creditLog: function (tid) { return delay((D.log || []).filter(function (x) { return x.t === tid; }).reverse().map(function (x) { return { delta: x.delta, note: x.note, at: x.at }; })); },
    setValidUntil: function (t, day) {
      if (!me().is_admin) return Promise.reject(new Error('Nur für Admin'));
      D.profiles.filter(function (x) { return x.id === t; })[0].valid_until = day || null; return delay();
    },
    listTeacherGames: function () { return delay(D.teacher_games); },
    setTeacherGame: function (t, g, on) { D.teacher_games = D.teacher_games.filter(function (x) { return !(x.teacher_id === t && x.game_id === g); }); if (on) D.teacher_games.push({ teacher_id: t, game_id: g }); return delay(); },
    listClasses: function () { return delay(D.classes.filter(function (c) { return c.teacher_id === me().id; })); },
    createClass: function (name, code) {
      if (D.classes.some(function (c) { return norm(c.code) === norm(code); })) return Promise.reject(new Error('duplicate key value violates unique constraint "classes_code_key"'));
      var c = { id: uid(), teacher_id: me().id, name: name, code: code, tafel_auto: true, created_at: now() }; D.classes.push(c); return delay(c);
    },
    kidKlasse: function (t) { var k = kidOf(t), c = D.classes.filter(function (x) { return x.id === k.class_id; })[0]; return delay({ bild: c.bild || null, tools: c.kid_tools || {}, cols: c.tafel_cols || {} }); },
    updateClass: function (id, p) { Object.assign(D.classes.filter(function (c) { return c.id === id; })[0], p); return delay(); },
    deleteClass: function (id) { D.classes = D.classes.filter(function (c) { return c.id !== id; }); return delay(); },
    listKids: function (cid) { return delay(D.kids.filter(function (k) { return k.class_id === cid; }).sort(function (a, b) { var x = a.nr == null ? 1e9 : a.nr, y = b.nr == null ? 1e9 : b.nr; return x - y || a.name.localeCompare(b.name); })); },
    addKids: function (cid, list) { var out = list.map(function (k) { var n = { id: uid(), class_id: cid, name: k.name, nr: k.nr == null ? null : k.nr, pw: k.pw, created_at: now() }; D.kids.push(n); return n; }); return delay(out); },
    setKidPw: function (id, pw) { D.kids.filter(function (k) { return k.id === id; })[0].pw = pw; return delay(); },
    setKidNr: function (id, nr) { D.kids.filter(function (k) { return k.id === id; })[0].nr = nr; return delay(); },
    deleteKid: function (id) { D.kids = D.kids.filter(function (k) { return k.id !== id; }); return delay(); },
    listReleases: function (cid) { return delay(D.class_games.filter(function (r) { return r.class_id === cid; }).map(function (r) { return r.game_id; })); },
    setRelease: function (cid, gid, on) { D.class_games = D.class_games.filter(function (r) { return !(r.class_id === cid && r.game_id === gid); }); if (on) D.class_games.push({ class_id: cid, game_id: gid }); return delay(); },
    listProgress: function (ids) { return delay(D.progress.filter(function (p) { return ids.indexOf(p.kid_id) >= 0; })); },
    listSubjects: function (cid) { return delay(D.subjects.filter(function (s) { return s.class_id === cid; })); },
    addSubject: function (cid, s) { var n = Object.assign({ id: uid(), class_id: cid }, s); D.subjects.push(n); return delay(n); },
    updateSubject: function (id, p) { Object.assign(D.subjects.filter(function (s) { return s.id === id; })[0], p); return delay(); },
    deleteSubjects: function (ids) { D.subjects = D.subjects.filter(function (s) { return ids.indexOf(s.id) < 0; }); D.entries = D.entries.filter(function (e) { return ids.indexOf(e.subject_id) < 0; }); return delay(); },
    clearTafel: function (cid) { D.entries = D.entries.filter(function (e) { return e.class_id !== cid; }); return delay(); },
    tafelTeacher: function (cid) { return delay({ me: null, state: state(cid) }); },
    kidClass: function (code) {
      var c = D.classes.filter(function (x) { return norm(x.code) === norm(code); })[0]; if (!c) return delay(null);
      if (!licOk(c.id)) return delay({ pausiert: true, kids: [] });
      return delay({ class_id: c.id, class_name: c.name, bild: c.bild || null, kids: D.kids.filter(function (k) { return k.class_id === c.id; }).sort(function (a, b) { var x = a.nr == null ? 1e9 : a.nr, y = b.nr == null ? 1e9 : b.nr; return x - y || a.name.localeCompare(b.name); }).map(function (k) { return { id: k.id, name: k.name, nr: k.nr }; }) });
    },
    kidLogin: function (code, kid, pw) {
      var k = D.kids.filter(function (x) { return x.id === kid; })[0];
      if (!k) return delay({ ok: false, error: 'unbekannt' });
      if (!licOk(k.class_id)) return delay({ ok: false, error: 'pausiert' });
      if (k.pw !== pw) return delay({ ok: false, error: 'falsch' });
      var t = uid(); D.sessions[t] = k.id; return delay({ ok: true, token: t, name: k.name });
    },
    kidLogout: function (t) { delete D.sessions[t]; return delay(); },
    kidHome: function (t) {
      try { var k = kidOf(t); } catch (e) { return Promise.reject(e); }
      var c = D.classes.filter(function (x) { return x.id === k.class_id; })[0];
      var games = D.class_games.filter(function (r) { return r.class_id === k.class_id && hasGame(c.teacher_id, r.game_id); }).map(function (r) { return D.games.filter(function (x) { return x.id === r.game_id; })[0]; }).sort(function (a, b) { return a.fach.localeCompare(b.fach) || a.thema.localeCompare(b.thema) || (a.sort || 0) - (b.sort || 0) || a.title.localeCompare(b.title); }).map(function (g) {
        var p = D.progress.filter(function (x) { return x.kid_id === k.id && x.game_id === g.id; })[0] || {};
        return { id: g.id, title: g.title, description: g.description, fach: g.fach, thema: g.thema, stufe: g.stufe || '', correct: p.correct || 0, attempts: p.attempts || 0, done: p.done == null ? null : p.done, total: p.total == null ? null : p.total, plays: p.plays || 0, levels: p.levels || {}, last_level: p.last_level || null, award: p.award || {} };
      });
      return delay({ kid: { id: k.id, name: k.name }, class_name: c.name, games: games });
    },
    kidGame: function (t, gid) {
      var k = kidOf(t), p = D.progress.filter(function (x) { return x.kid_id === k.id && x.game_id === gid; })[0];
      if (!p) { p = { kid_id: k.id, game_id: gid, correct: 0, attempts: 0, done: null, total: null, plays: 0, levels: {}, award: {} }; D.progress.push(p); }
      p.plays++; p.last_played = now();
      return delay(D.games.filter(function (g) { return g.id === gid; })[0].html);
    },
    kidReport: function (t, gid, r) {
      var k = kidOf(t), p = D.progress.filter(function (x) { return x.kid_id === k.id && x.game_id === gid; })[0];
      p.correct += r.correct; p.attempts += r.attempts; if (r.done != null) p.done = r.done; if (r.total != null) p.total = r.total; p.last_played = now();
      if (r.level) { p.levels = p.levels || {}; var x = p.levels[r.level] || {}; p.levels[r.level] = { c: (x.c || 0) + r.correct, a: (x.a || 0) + r.attempts, d: r.done != null ? r.done : x.d, t: r.total != null ? r.total : x.t }; p.last_level = r.level; }
      window.__reports = (window.__reports || 0) + 1; return delay();
    },
    kidState: function (t, gid) { var k = kidOf(t), p = D.progress.filter(function (x) { return x.kid_id === k.id && x.game_id === gid; })[0] || {};
      var gs = (D.gsettings || {})[k.class_id + '|' + gid], st = null;
      if (gs) { st = JSON.parse(JSON.stringify(gs)); st.mine = (gs.kids || {})[k.id] || []; delete st.kids; }
      return delay({ save: p.save || null, award: p.award || {}, settings: st }); },
    vkBildPut: function (id, data) { D.vkb = D.vkb || {}; if (!/^[a-z0-9]{8,40}$/.test(id) || !/^data:image\//.test(data)) return Promise.reject(new Error('Ungültiges Bild')); if (!D.vkb[id]) D.vkb[id] = data; return delay(); },
    vkBilderGet: function (ids) { var m = {}; (ids || []).forEach(function (i) { if ((D.vkb || {})[i]) m[i] = D.vkb[i]; }); return delay(m); },
    kidVkBilder: function (t, ids) { kidOf(t); var m = {}; (ids || []).forEach(function (i) { if ((D.vkb || {})[i]) m[i] = D.vkb[i]; }); return delay(m); },
    kidVkExtra: function (t, gid) { var k = kidOf(t), gs = (D.gsettings || {})[k.class_id + '|' + gid], z = gs && gs.content && gs.content.ziel, n = 0;
      if (z && z.ab) D.progress.forEach(function (p) { var kk = D.kids.filter(function (x) { return x.id === p.kid_id; })[0];
        if (kk && kk.class_id === k.class_id && p.game_id === gid) Object.entries(((p.save || {}).p || {}).sec || {}).forEach(function (e) { if (e[0] >= z.ab && e[1] >= 420) n++; }); });
      return delay({ sticker: (D.shared || {})['vokabelkiste-sticker'] || null, klasse: { sterne: n } }); },
    resetProgress: function (kid, ids) { D.progress = D.progress.filter(function (x) { return !(x.kid_id === kid && (!ids || ids.indexOf(x.game_id) >= 0)); }); return delay(); },
    gameSettingsGet: function (cid, gid) { return delay(((D.gsettings || {})[cid + '|' + gid]) || null); },
    gameSettingsSet: function (cid, gid, v) { D.gsettings = D.gsettings || {}; D.gsettings[cid + '|' + gid] = JSON.parse(JSON.stringify(v)); return delay(); },
    listProgressSaves: function (ids, gid) { return delay(JSON.parse(JSON.stringify(D.progress.filter(function (x) { return ids.indexOf(x.kid_id) >= 0 && x.game_id === gid; }).map(function (x) { return { kid_id: x.kid_id, save: x.save || null, award: x.award || {}, last_played: x.last_played }; })))); },
    listProgressGame: function (ids, gid) { return delay(D.progress.filter(function (x) { return ids.indexOf(x.kid_id) >= 0 && x.game_id === gid; }).map(function (x) { return { kid_id: x.kid_id, award: x.award || {}, levels: x.levels, last_played: x.last_played }; })); },
    kidSave: function (t, gid, sv, aw) {
      var k = kidOf(t), p = D.progress.filter(function (x) { return x.kid_id === k.id && x.game_id === gid; })[0];
      if (sv != null) p.save = sv; if (aw != null) p.award = aw; window.__saves = (window.__saves || 0) + 1; return delay();
    },
    raceLatest: function (cid) { var r = (D.races || []).filter(function (x) { return x.class_id === cid; }).slice(-1)[0]; return delay(r || null); },
    raceCreate: function (cid, st) { D.races = D.races || []; D.runs = D.runs || []; D.races.forEach(function (x) { if (x.class_id === cid) x.status = 'done'; });
      var r = { id: uid(), class_id: cid, status: 'wait', settings: st, starts_at: null, created_at: now() }; D.races.push(r); return delay(r); },
    raceStart: function (id) { var r = D.races.filter(function (x) { return x.id === id; })[0]; r.status = 'run'; r.starts_at = new Date(Date.now() + 4000).toISOString(); return delay({ starts_at: r.starts_at, now: now() }); },
    raceEnd: function (id) { D.races.filter(function (x) { return x.id === id; })[0].status = 'done'; return delay(); },
    raceGet: function (id) { return delay(D.races.filter(function (x) { return x.id === id; })[0]); },
    raceRuns: function (id) { return delay(D.runs.filter(function (x) { return x.race_id === id; })); },
    kidRace: function (t) { var k = kidOf(t), r = (D.races || []).filter(function (x) { return x.class_id === k.class_id; }).slice(-1)[0];
      if (!r) return delay({ now: now(), race: null });
      var run = D.runs.filter(function (x) { return x.race_id === r.id && x.kid_id === k.id; })[0];
      if (r.status === 'done' && !run) return delay({ now: now(), race: null });
      var fin = D.runs.filter(function (x) { return x.race_id === r.id && x.finished_at; }).sort(function (a, b) { return a.finished_at < b.finished_at ? -1 : 1; });
      return delay({ now: now(), place: run && run.finished_at ? fin.indexOf(run) + 1 : null, race: { id: r.id, status: r.status, settings: r.settings, starts_at: r.starts_at },
        run: run ? { pos: run.pos, correct: run.correct, wrong: run.wrong, finished: !!run.finished_at } : null }); },
    kidRaceJoin: function (t, id) { var k = kidOf(t); if (!D.runs.some(function (x) { return x.race_id === id && x.kid_id === k.id; })) D.runs.push({ race_id: id, kid_id: k.id, pos: 0, correct: 0, wrong: 0, finished_at: null });
      return this.kidRace(t); },
    kidRaceStep: function (t, id, ok) { var k = kidOf(t), r = D.races.filter(function (x) { return x.id === id; })[0], run = D.runs.filter(function (x) { return x.race_id === id && x.kid_id === k.id; })[0];
      if (!r || r.status !== 'run' || Date.parse(r.starts_at) > Date.now() + 1000 || run.finished_at) return delay({ ok: false });
      var goal = r.settings.goal; if (ok) { run.pos++; run.correct++; } else run.wrong++;
      if (run.pos >= goal) { run.pos = goal; run.finished_at = new Date().toISOString(); }
      var fin = D.runs.filter(function (x) { return x.race_id === id && x.finished_at; }).sort(function (a, b) { return a.finished_at < b.finished_at ? -1 : 1; });
      return delay({ ok: true, pos: run.pos, goal: goal, finished: !!run.finished_at, place: run.finished_at ? fin.indexOf(run) + 1 : null }); },
    storeGet: function (d) { D.store = D.store || {}; d = D.session.user.id + '|' + d; return delay(D.store[d] === undefined ? null : D.store[d]); },
    storeSet: function (d, v) { D.store = D.store || {}; D.store[D.session.user.id + '|' + d] = v; window.__storeSets = (window.__storeSets || 0) + 1; return delay(); },
    sharedGet: function (d) { D.shared = D.shared || {}; return delay(D.shared[d] || null); },
    sharedSet: function (d, v) { if (!me().is_admin) return Promise.reject(new Error('nicht erlaubt')); D.shared = D.shared || {}; D.shared[d] = v; return delay(); },
    storeDel: function (d) { if (D.store) delete D.store[D.session.user.id + '|' + d]; return delay(); },
    storeUpload: function (b) { return Promise.resolve('data:image/png;base64,iVBORw0KGgo='); },
    kidHeft: function (t) { var k = kidOf(t), c = D.classes.filter(function (x) { return x.id === k.class_id; })[0];
      var d = (D.store || {})[c.teacher_id + '|hat-' + c.id]; if (!d || !Array.isArray(d.entries)) return delay(null);
      d = JSON.parse(JSON.stringify(d)); var sid = k.id, one = function (o) { var r = {}; if (o && o[sid] !== undefined) r[sid] = o[sid]; return r; };
      var ents = d.entries.filter(function (e) { return !(e.for && e.for.length) || e.for.indexOf(sid) >= 0; }).map(function (e) {
        e.for = []; e.status = one(e.status); e.notes = one(e.notes); e.first = one(e.first); e.neuAuf = one(e.neuAuf); e.selbst = one(e.selbst); return e; });
      return delay({ klasse: d.klasse, settings: d.settings, entries: ents, sus: [{ id: sid, name: k.name }], kidNotes: {} }); },
    atelierPut: function (cid, kid, patch) { var c = D.classes.filter(function (x) { return x.id === cid; })[0]; if (!c || c.teacher_id !== D.session.user.id) return Promise.reject(new Error('Nicht erlaubt'));
      D.store = D.store || {}; var k = c.teacher_id + '|atelier-' + cid, d = D.store[k] = D.store[k] || { open: false, kids: {} };
      if (kid === '_') { if ('open' in patch) d.open = !!patch.open; if (Array.isArray(patch.arten)) d.arten = patch.arten.map(String).filter(function (x) { return x.trim(); }); } else if (patch == null) delete d.kids[kid]; else d.kids[kid] = Object.assign(d.kids[kid] || {}, JSON.parse(JSON.stringify(patch))); return delay(); },
    kidAtelier: function (t) { var k = kidOf(t), c = D.classes.filter(function (x) { return x.id === k.class_id; })[0], d = (D.store || {})[c.teacher_id + '|atelier-' + c.id];
      if (!d) return delay(null); return delay(JSON.parse(JSON.stringify({ open: !!d.open, arten: d.arten || [], me: k.id, kids: D.kids.filter(function (x) { return x.class_id === c.id; }).map(function (x) { var e = d.kids[x.id] || {};
        return { id: x.id, name: x.name, thema: e.thema, umsetzung: e.umsetzung, farbe: e.farbe, x: e.x == null ? null : e.x, y: e.y == null ? null : e.y }; }) }))); },
    kidAtelierSet: function (t, p) { var k = kidOf(t), c = D.classes.filter(function (x) { return x.id === k.class_id; })[0], d = (D.store || {})[c.teacher_id + '|atelier-' + c.id];
      if (!d) return delay(false); var e = d.kids[k.id] = d.kids[k.id] || {};
      if ('x' in p) { e.x = typeof p.x === 'number' ? p.x : null; e.y = typeof p.y === 'number' ? p.y : null; } if (/^#[0-9a-f]{6}$/i.test(p.farbe || '')) e.farbe = p.farbe;
      if (d.open) { if (typeof p.thema === 'string') e.thema = p.thema; if (typeof p.umsetzung === 'string' && (!(d.arten || []).length || !p.umsetzung || d.arten.indexOf(p.umsetzung) >= 0)) e.umsetzung = p.umsetzung; } return delay(true); },
    umfragePut: function (cid, live, clear) { var c = D.classes.filter(function (x) { return x.id === cid; })[0]; if (!c || c.teacher_id !== D.session.user.id) return Promise.reject(new Error('Nicht erlaubt'));
      D.store = D.store || {}; var k = c.teacher_id + '|umfrage-' + cid, d = D.store[k] = D.store[k] || { live: null, ans: {} }; return delay(umfApply(d, live, clear)); },
    kidUmfrage: function (t) { var k = kidOf(t), c = D.classes.filter(function (x) { return x.id === k.class_id; })[0]; return delay(umfView((D.store || {})[c.teacher_id + '|umfrage-' + c.id], k.id)); },
    kidUmfrageSend: function (t, qid, v) { var k = kidOf(t), c = D.classes.filter(function (x) { return x.id === k.class_id; })[0], d = (D.store || {})[c.teacher_id + '|umfrage-' + c.id];
      v = d && umfVal(d.live, qid, v); if (v == null) return delay(false); d.ans = d.ans || {}; d.ans[qid] = d.ans[qid] || {}; d.ans[qid][k.id] = v; return delay(true); },
    umfOffenOpen: function (live) { D.runden = (D.runden || []).filter(function (r) { return r.teacher_id !== D.session.user.id; });
      var r = { id: uid(), nr: String(100000 + Math.floor(Math.random() * 900000)), teacher_id: D.session.user.id, data: { live: null, ans: {} }, gaeste: [] }; D.runden.push(r);
      var x = umfApply(r.data, live, null); return delay({ id: r.id, nr: r.nr, now: x.now, until: x.until }); },
    umfOffenPut: function (id, live, clear) { var r = (D.runden || []).filter(function (x) { return x.id === id && x.teacher_id === D.session.user.id; })[0]; if (!r) return Promise.reject(new Error('Runde nicht gefunden')); return delay(umfApply(r.data, live, clear)); },
    umfOffenHost: function (id) { var r = (D.runden || []).filter(function (x) { return x.teacher_id === D.session.user.id && (!id || x.id === id); }).slice(-1)[0];
      return delay(r ? { id: r.id, nr: r.nr, data: r.data, gaeste: r.gaeste.map(function (g) { return { id: g.id, name: g.name }; }) } : null); },
    umfOffenClose: function (id) { D.runden = (D.runden || []).filter(function (x) { return x.id !== id; }); return delay(); },
    umfGastJoin: function (nr, name) { var r = (D.runden || []).filter(function (x) { return x.nr === String(nr).replace(/\D/g, ''); })[0];
      if (!r) return delay({ ok: false, error: 'nummer' }); if (!(r.data.live && r.data.live.on)) return delay({ ok: false, error: 'vorbei' });
      var n = String(name || '').trim().replace(/\s+/g, ' '); if (n.length > 20 || /[<>]/.test(n)) return delay({ ok: false, error: 'name' });
      if (!n) n = 'Gast ' + (r.gaeste.length + 1); var g = { id: uid(), token: uid(), name: n }; r.gaeste.push(g); return delay({ ok: true, token: g.token, name: n }); },
    umfGastFind: function (t) { var out = null; (D.runden || []).forEach(function (r) { r.gaeste.forEach(function (g) { if (g.token === t) out = { r: r, g: g }; }); }); return out; },
    umfGast: function (t) { var x = this.umfGastFind(t); return delay(x ? umfView(x.r.data, x.g.id) : { gone: true }); },
    umfGastSend: function (t, qid, v) { var x = this.umfGastFind(t); if (!x) return delay(false); var d = x.r.data; v = umfVal(d.live, qid, v); if (v == null) return delay(false);
      d.ans[qid] = d.ans[qid] || {}; d.ans[qid][x.g.id] = v; return delay(true); },
    pinPut: function (cid, coll, id, obj) { var c = D.classes.filter(function (x) { return x.id === cid; })[0]; if (!c || c.teacher_id !== D.session.user.id) return Promise.reject(new Error('Nicht erlaubt'));
      D.store = D.store || {}; var k = c.teacher_id + '|pin-' + cid, d = D.store[k] = D.store[k] || {}; d[coll] = d[coll] || {}; if (obj == null) delete d[coll][id]; else d[coll][id] = JSON.parse(JSON.stringify(obj)); return delay(); },
    kidPin: function (t) { var k = kidOf(t), c = D.classes.filter(function (x) { return x.id === k.class_id; })[0], d = (D.store || {})[c.teacher_id + '|pin-' + c.id];
      if (!d) return delay({ boards: {}, ideas: {}, labels: {}, my: null }); var b = {}, i = {};
      Object.keys(d.boards || {}).forEach(function (id) { var x = d.boards[id]; if (x.visible === true) b[id] = Object.assign({}, x, { visible: true }); });
      Object.keys(d.ideas || {}).forEach(function (id) { var x = d.ideas[id]; if (!b[x.boardId]) return;
        if (x.status === 'ok') i[id] = { text: x.text, boardId: x.boardId, status: 'ok', tools: x.tools, at: x.at, okAt: x.okAt, order: x.order, lp: x.lp, cat: x.cat, img: x.img, pos: x.pos, poll: x.poll,
          uid: x.uid === k.id ? k.id : undefined, by: (b[x.boardId].names || x.uid === k.id) ? x.by : undefined };
        else if (x.status === 'pending' && x.uid === k.id) i[id] = { text: x.text, boardId: x.boardId, status: 'pending', at: x.at, uid: k.id, cat: x.cat, img: x.img, by: x.by }; });
      return delay(JSON.parse(JSON.stringify({ boards: b, ideas: i, labels: ((d.settings || {}).main || {}).labels || {}, my: (d.votes || {})[k.id] || null }))); },
    kidPinIdea: function (t, board, text) { var k = kidOf(t), c = D.classes.filter(function (x) { return x.id === k.class_id; })[0], d = (D.store || {})[c.teacher_id + '|pin-' + c.id];
      if (!d || !(d.boards[board] || {}).visible) return Promise.reject(new Error('nicht offen')); var id = 'k' + Math.random().toString(36).slice(2, 10);
      d.ideas = d.ideas || {}; d.ideas[id] = { text: text, by: k.name, uid: k.id, boardId: board, status: 'pending', at: Date.now() }; return delay(id); },
    kidPinPost: function (t, board, text, cat, img) { var k = kidOf(t), c = D.classes.filter(function (x) { return x.id === k.class_id; })[0], d = (D.store || {})[c.teacher_id + '|pin-' + c.id];
      var bd = d && d.boards[board]; if (!bd || !bd.visible) return Promise.reject(new Error('Diese Pinnwand ist im Moment nicht offen.'));
      if (img && (!bd.imgs || img.length > 250000)) return Promise.reject(new Error('Dieses Bild geht leider nicht.'));
      var id = 'k' + Math.random().toString(36).slice(2, 10), o = { text: String(text || '').trim().slice(0, 280), by: k.name, uid: k.id, boardId: board, at: Date.now() };
      if (cat && (bd.cats || []).some(function (x) { return x.id === cat; })) o.cat = cat; if (img) o.img = img;
      if (bd.direct) { o.status = 'ok'; o.okAt = Date.now(); o.tools = bd.tools || {}; } else o.status = 'pending';
      d.ideas = d.ideas || {}; d.ideas[id] = o; return delay(id); },
    kidPinVote: function (t, body) { var k = kidOf(t), c = D.classes.filter(function (x) { return x.id === k.class_id; })[0], d = (D.store || {})[c.teacher_id + '|pin-' + c.id];
      d.votes = d.votes || {}; var r = {}; Object.keys(body.r || {}).forEach(function (id) { if ((d.ideas[id] || {}).status === 'ok') r[id] = body.r[id]; }); d.votes[k.id] = { r: r, at: Date.now() }; return delay(true); },
    kidHeftOwn: function (t, x, del) { var k = kidOf(t), c = D.classes.filter(function (q) { return q.id === k.class_id; })[0];
      var d = (D.store || {})[c.teacher_id + '|hat-' + c.id]; if (!d) return delay(false);
      var i = d.entries.findIndex(function (e) { return e.id === x.id; }); if (i >= 0 && d.entries[i].by !== k.id) return delay(false);
      if (del) { if (i >= 0) d.entries.splice(i, 1); return delay(true); }
      var ne = { id: x.id, by: k.id, for: [k.id], type: 'aufgabe', ink: 'schwarz', mark: '', date: x.date, fach: x.fach, title: x.title, details: x.details, order: x.order, status: {}, selbst: i >= 0 ? d.entries[i].selbst || {} : {} };
      if (i >= 0) d.entries[i] = ne; else d.entries.push(ne); return delay(true); },
    kidHeftTick: function (t, id, on) { var k = kidOf(t), c = D.classes.filter(function (x) { return x.id === k.class_id; })[0];
      var d = (D.store || {})[c.teacher_id + '|hat-' + c.id]; var e = d && d.entries.filter(function (x) { return x.id === id; })[0];
      if (!e || (e.type || 'aufgabe') !== 'aufgabe') return delay(false); e.selbst = e.selbst || {}; if (on) e.selbst[k.id] = true; else delete e.selbst[k.id]; return delay(true); },
    // Live-Quiz (wie die SQL-Funktionen der Version 23)
    quizOpen: function (title, qs) { D.quiz = (D.quiz || []).filter(function (l) { return l.teacher_id !== D.session.user.id; });
      var l = { id: uid(), teacher_id: D.session.user.id, pin: String(100000 + Math.floor(Math.random() * 900000)), title: title, questions: JSON.parse(JSON.stringify(qs)), phase: 'lobby', q: -1, q_started: 0, players: [] };
      D.quiz.push(l); return delay({ id: l.id, pin: l.pin }); },
    quizStep: function (id, ph, q) { var l = (D.quiz || []).filter(function (x) { return x.id === id; })[0]; if (!l) return Promise.reject(new Error('Runde nicht gefunden'));
      if (q < -1 || q >= l.questions.length) return Promise.reject(new Error('Frage ungültig'));
      if (ph === 'frage' && (l.phase !== 'frage' || l.q !== q)) l.q_started = Date.now(); l.phase = ph; l.q = q; return delay(); },
    quizHost: function (id) { var l = (D.quiz || []).filter(function (x) { return x.id === id; })[0]; if (!l) return delay(null);
      return delay({ phase: l.phase, q: l.q, pin: l.pin, left_ms: quizLeft(l), players: l.players.map(function (p) { return { id: p.id, name: p.name, avatar: p.avatar, score: p.score, streak: p.streak, answers: p.answers }; }) }); },
    quizKick: function (id, pid) { var l = (D.quiz || []).filter(function (x) { return x.id === id; })[0]; if (l) l.players = l.players.filter(function (p) { return p.id !== pid; }); return delay(); },
    quizClose: function (id) { D.quiz = (D.quiz || []).filter(function (x) { return x.id !== id; }); return delay(); },
    quizJoin: function (pin, name, av) { var l = (D.quiz || []).filter(function (x) { return x.pin === String(pin).replace(/\D/g, ''); })[0];
      if (!l) return delay({ ok: false, error: 'nummer' }); if (l.phase === 'ende') return delay({ ok: false, error: 'vorbei' });
      var n = String(name || '').trim().replace(/\s+/g, ' '); if (!n || n.length > 20 || /[<>]/.test(n)) return delay({ ok: false, error: 'name' });
      if (l.players.some(function (p) { return p.name.toLowerCase() === n.toLowerCase(); })) return delay({ ok: false, error: 'vergeben' });
      var p = { id: uid(), token: uid(), name: n, avatar: /^[a-z]{2,10}$/.test(av) ? av : 'eule', score: 0, streak: 0, answers: {} }; l.players.push(p);
      return delay({ ok: true, token: p.token, name: n, title: l.title }); },
    quizState: function (t) { var p = null, l = (D.quiz || []).filter(function (x) { return x.players.some(function (y) { if (y.token === t) p = y; return y.token === t; }); })[0];
      if (!l) return delay({ gone: true }); var qq = l.q >= 0 ? l.questions[l.q] : null, showq = qq && (l.phase === 'frage' || l.phase === 'aufloesung');
      var top = l.players.slice().sort(function (a, b) { return b.score - a.score; }).slice(0, 5).map(function (x) { return { name: x.name, avatar: x.avatar, score: x.score }; });
      return delay({ phase: l.phase, q: l.q, n: l.questions.length, title: l.title, name: p.name, avatar: p.avatar, score: p.score, streak: p.streak,
        rank: l.players.filter(function (x) { return x.score > p.score; }).length + 1, players: l.players.length, left_ms: quizLeft(l),
        question: showq ? { typ: qq.typ, frage: qq.frage, bild: qq.bild || null, zeit: qq.zeit, mehrfach: !!qq.mehrfach, mix: qq.mix || null, antworten: qq.typ === 'text' ? null : qq.antworten,
          nrichtig: (qq.typ === 'quiz' || qq.typ === 'rf') ? (qq.richtig || []).length : null } : null,
        richtig: l.phase === 'aufloesung' ? qq.richtig : null, mine: l.q >= 0 ? p.answers[l.q] || null : null, top: (l.phase === 'rangliste' || l.phase === 'ende') ? top : null }); },
    quizAnswer: function (t, q, a) { var p = null, l = (D.quiz || []).filter(function (x) { return x.players.some(function (y) { if (y.token === t) p = y; return y.token === t; }); })[0];
      if (!l) return delay({ ok: false, error: 'weg' }); if (l.phase !== 'frage' || l.q !== q) return delay({ ok: false, error: 'vorbei' }); if (p.answers[q]) return delay({ ok: false, error: 'schon' });
      var qq = l.questions[q], lim = (qq.zeit || 20) * 1000, ms = Date.now() - l.q_started, ok = false; if (ms > lim + 1500) return delay({ ok: false, error: 'vorbei' });
      var nz = function (x) { return String(x || '').trim().replace(/\s+/g, ' ').toLowerCase(); };
      if (qq.typ === 'text') ok = (qq.richtig || []).some(function (r) { return nz(r) && nz(r) === nz(a); });
      else if (qq.typ === 'reihe') ok = a.join() === qq.antworten.map(function (x, i) { return i; }).join();
      else { var s1 = a.filter(function (x, i) { return a.indexOf(x) === i; }).sort().join(), s2 = (qq.richtig || []).slice().sort().join(); ok = s1 === s2; }
      var m = [0, 1, 2].indexOf(qq.punkte) >= 0 ? qq.punkte : 1, pts = ok ? Math.round(1000 * m * (1 - Math.min(Math.max(ms, 0), lim) / lim / 2)) : 0;
      p.score += pts; p.streak = ok ? p.streak + 1 : 0; p.answers[q] = { a: a, ok: ok, p: pts, ms: ms }; return delay({ ok: true }); },
    // Kinder-Quiz (wie die SQL-Funktionen der Version 24)
    kidQuizList: function (t) { var k = kidOf(t), c = D.classes.filter(function (x) { return x.id === k.class_id; })[0];
      return delay({ me: k.id, on: !!(c.kid_tools && c.kid_tools.quiz === true), quizzes: (D.kq || []).filter(function (q) { return q.class_id === k.class_id && q.members.indexOf(k.id) >= 0; })
        .map(function (q) { return { id: q.id, title: q.title, n: q.data.length, ver: q.ver, mine: q.created_by === k.id, members: kqNames(q.members), updated_at: q.updated_at, updated_by: q.updated_by }; }) }); },
    kidQuizGet: function (t, id, ver) { var k = kidOf(t), q = (D.kq || []).filter(function (x) { return x.id === id && x.class_id === k.class_id && x.members.indexOf(k.id) >= 0; })[0];
      if (!q) return delay(null); if (ver != null && ver === q.ver) return delay({ same: true, ver: q.ver });
      return delay({ id: q.id, title: q.title, data: q.data, ver: q.ver, mine: q.created_by === k.id, members: kqNames(q.members), updated_by: q.updated_by }); },
    kidQuizSave: function (t, id, ver, title, data) { var k = kidOf(t), c = D.classes.filter(function (x) { return x.id === k.class_id; })[0]; D.kq = D.kq || [];
      if (!(c.kid_tools && c.kid_tools.quiz === true)) return delay({ ok: false, error: 'aus' });
      if (!id) { var n = { id: uid(), class_id: k.class_id, title: title || '', data: JSON.parse(JSON.stringify(data)), members: [k.id], created_by: k.id, ver: 1, updated_by: k.name, updated_at: now() }; D.kq.push(n); return delay({ ok: true, id: n.id, ver: 1 }); }
      var q = D.kq.filter(function (x) { return x.id === id && x.class_id === k.class_id && x.members.indexOf(k.id) >= 0; })[0]; if (!q) return delay({ ok: false, error: 'weg' });
      if (q.ver !== ver) return delay({ ok: false, conflict: true, ver: q.ver, title: q.title, data: q.data });
      q.title = title || ''; q.data = JSON.parse(JSON.stringify(data)); q.ver++; q.updated_by = k.name; q.updated_at = now(); return delay({ ok: true, id: q.id, ver: q.ver }); },
    kidQuizDelete: function (t, id) { var k = kidOf(t), before = (D.kq || []).length; D.kq = (D.kq || []).filter(function (q) { return !(q.id === id && q.created_by === k.id); }); return delay(D.kq.length < before); },
    kqList: function () { var mine = D.classes.filter(function (c) { return c.teacher_id === me().id; }).map(function (c) { return c.id; });
      return delay((D.kq || []).filter(function (q) { return mine.indexOf(q.class_id) >= 0; }).map(function (q) { return { id: q.id, class_id: q.class_id, title: q.title, n: q.data.length, ver: q.ver, members: q.members, created_by: q.created_by, updated_at: q.updated_at, updated_by: q.updated_by }; })); },
    kqGet: function (id, ver) { var q = kqMine(id); if (!q) return delay(null); if (ver != null && ver === q.ver) return delay({ same: true, ver: q.ver });
      return delay({ id: q.id, class_id: q.class_id, title: q.title, data: q.data, ver: q.ver, members: q.members, updated_by: q.updated_by }); },
    kqSave: function (id, ver, title, data) { var q = kqMine(id); if (!q) return delay({ ok: false, error: 'weg' }); if (q.ver !== ver) return delay({ ok: false, conflict: true, ver: q.ver, title: q.title, data: q.data });
      q.title = title || ''; q.data = JSON.parse(JSON.stringify(data)); q.ver++; q.updated_by = 'Lehrperson'; q.updated_at = now(); return delay({ ok: true, id: q.id, ver: q.ver }); },
    kqNew: function (cid, members, title) { D.kq = D.kq || []; var n = { id: uid(), class_id: cid, title: title || '', data: [], members: members.filter(function (m) { return D.kids.some(function (k) { return k.id === m && k.class_id === cid; }); }), created_by: null, ver: 1, updated_by: 'Lehrperson', updated_at: now() };
      D.kq.push(n); return delay({ id: n.id }); },
    kqMembers: function (id, members) { var q = kqMine(id); if (q) { q.members = members.filter(function (m) { return D.kids.some(function (k) { return k.id === m && k.class_id === q.class_id; }); }); q.ver++; } return delay(); },
    kqDelete: function (id) { var q = kqMine(id); if (q) D.kq = D.kq.filter(function (x) { return x !== q; }); return delay(); },
    tafelGet: function (t) { var k = kidOf(t); return delay({ me: k.id, state: state(k.class_id) }); },
    tafelSet: function (t, s, c) {
      var k = kidOf(t); D.entries = D.entries.filter(function (e) { return e.kid_id !== k.id; });
      if (s) D.entries.push({ kid_id: k.id, class_id: k.class_id, subject_id: s, col: c });
      return delay({ me: k.id, state: state(k.class_id) });
    },
    // Elterngespräche wie eltern_get / eltern_set / talk_answer_put
    talkList: function (cid) { return delay((D.talks || []).filter(function (t) { return t.class_id === cid; }).slice().reverse()); },
    talkGet: function (id) { return delay((D.talks || []).filter(function (t) { return t.id === id; })[0] || null); },
    talkNew: function (cid, cfg) { D.talks = D.talks || []; var t = { id: uid(), class_id: cid, token: uid(), cfg: JSON.parse(JSON.stringify(cfg)), answers: {}, created_at: now() }; D.talks.push(t); return delay(t); },
    talkSave: function (id, cfg) { var t = D.talks.filter(function (x) { return x.id === id; })[0]; t.cfg = JSON.parse(JSON.stringify(cfg)); return delay(); },
    talkReset: function (id, patch) { Object.assign(D.talks.filter(function (x) { return x.id === id; })[0], JSON.parse(JSON.stringify(patch))); return delay(); },
    talkDelete: function (id) { D.talks = D.talks.filter(function (x) { return x.id !== id; }); return delay(); },
    talkAnswerPut: function (id, kid, a) { var t = D.talks.filter(function (x) { return x.id === id; })[0]; if (!a) delete t.answers[kid]; else { var e = t.answers[kid] || {}; t.answers[kid] = { name: a.name || '', slots: a.slots || [], note: a.note || '', none: !!a.none, key: e.key || null, at: now(), lp: true }; } return delay(); },
    elternGet: function (tok, kid, key) {
      var t = (D.talks || []).filter(function (x) { return x.token === tok; })[0]; if (!t) return delay(null);
      var c = D.classes.filter(function (x) { return x.id === t.class_id; })[0], p = D.profiles.filter(function (x) { return x.id === c.teacher_id; })[0] || {};
      if (!t.cfg.open) return delay({ open: false, title: t.cfg.title, class_name: c.name, teacher: p.name, bild: c.bild || null });
      var fx = t.cfg.fixed || {}, fk = Object.keys(fx).map(function (s) { return fx[s]; }), a = kid && t.answers[kid], mine = null;
      if (a && key && a.key === key) mine = { name: a.name, slots: a.slots, note: a.note, none: a.none, fixed: Object.keys(fx).filter(function (s) { return fx[s] === kid; })[0] || null };
      return delay({ open: true, title: t.cfg.title, info: t.cfg.info, class_name: c.name, teacher: p.name, bild: c.bild || null,
        slots: (t.cfg.slots || []).map(function (s) { return { id: s.id, d: s.d, t: s.t, e: s.e }; }), fixed: Object.keys(fx),
        kids: D.kids.filter(function (k) { return k.class_id === c.id && (!Array.isArray(t.cfg.kids) || t.cfg.kids.indexOf(k.id) >= 0); }).map(function (k) { return { id: k.id, name: k.name, done: !!t.answers[k.id] || fk.indexOf(k.id) >= 0 }; }),
        others: Object.keys(t.answers).filter(function (k) { return k !== kid && !t.answers[k].none && fk.indexOf(k) < 0; }).map(function (k) { return t.answers[k].slots; }), mine: mine });
    },
    elternSet: function (tok, kid, key, a) {
      var t = (D.talks || []).filter(function (x) { return x.token === tok; })[0];
      if (!t || !t.cfg.open) return Promise.reject(new Error('Die Anmeldung ist geschlossen.'));
      if (Array.isArray(t.cfg.kids) && t.cfg.kids.indexOf(kid) < 0) return Promise.reject(new Error('Kind nicht gefunden'));
      var e = t.answers[kid], fx = t.cfg.fixed || {};
      if ((e && e.key !== key) || (!e && Object.keys(fx).some(function (s) { return fx[s] === kid; }))) return Promise.reject(new Error('Für dieses Kind ist schon ein Termin eingetragen. Bitte melden Sie sich bei der Lehrperson.'));
      if (!String(a.name || '').trim()) return Promise.reject(new Error('Bitte geben Sie Ihren Namen ein.'));
      var ids = (t.cfg.slots || []).map(function (s) { return s.id; });
      var sl = (a.slots || []).filter(function (s, i, l) { return l.indexOf(s) === i && ids.indexOf(s) >= 0 && (!fx[s] || fx[s] === kid); });
      if (!sl.length && !a.none) return Promise.reject(new Error('Bitte wählen Sie mindestens einen Termin.'));
      t.answers[kid] = { name: String(a.name).trim(), slots: sl, note: a.note || '', none: !!a.none, key: key, at: now() };
      return delay({ ok: true, slots: sl });
    }
  };
  window.__GAME_HTML = GAME_HTML;
})();
