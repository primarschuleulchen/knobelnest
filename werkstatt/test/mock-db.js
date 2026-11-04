// In-memory stand-in for db.js, mirroring the SQL functions' behaviour.
(function () {
  var uid = function () { return 'xxxxxxxx-xxxx-4xxx-8xxx-xxxxxxxxxxxx'.replace(/x/g, function () { return (Math.random() * 16 | 0).toString(16); }); };
  var now = function () { return new Date().toISOString(); };
  var D = {
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
    storeDel: function (d) { if (D.store) delete D.store[d]; return delay(); },
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
      D.store = D.store || {}; var k = c.teacher_id + '|umfrage-' + cid, d = D.store[k] = D.store[k] || { live: null, ans: {} }, n = Date.now();
      if (live) { live = JSON.parse(JSON.stringify(live)); if (typeof live.sec === 'number') { live.until = live.sec > 0 ? n + live.sec * 1000 : null; delete live.sec; } d.live = live; }
      (clear || []).forEach(function (q) { if (q === '*') d.ans = {}; else delete d.ans[q]; }); return delay({ now: n, until: d.live ? d.live.until || null : null }); },
    kidUmfrage: function (t) { var k = kidOf(t), c = D.classes.filter(function (x) { return x.id === k.class_id; })[0], d = (D.store || {})[c.teacher_id + '|umfrage-' + c.id];
      var l = d && d.live; if (!l || !l.on) return delay(null); var sh = !!l.show && l.kids !== false, out = { sid: l.sid, title: l.title, mode: l.mode || 'live', cur: l.cur, open: !!l.open, show: sh, until: l.until || null, now: Date.now(), rev: l.rev || [], qs: [], mine: {}, res: {} };
      (l.qs || []).forEach(function (q) { if ((l.mode || 'live') !== 'selbst' && q.id !== l.cur) return; q = JSON.parse(JSON.stringify(q)); if ((l.rev || []).indexOf(q.id) < 0) delete q.ok; out.qs.push(q);
        var a = (d.ans || {})[q.id] || {}; if (a[k.id] !== undefined) out.mine[q.id] = a[k.id];
        if (sh) { var hk = (l.hid || {})[q.id] || [], hw = (l.hidw || {})[q.id] || []; out.res[q.id] = Object.keys(a).filter(function (id) { return hk.indexOf(id) < 0; }).map(function (id) {
          var v = a[id]; return q.type === 'wort' && Array.isArray(v) ? v.filter(function (w) { return hw.indexOf(String(w).toLowerCase()) < 0; }) : v; }); } });
      return delay(out); },
    kidUmfrageSend: function (t, qid, v) { var k = kidOf(t), c = D.classes.filter(function (x) { return x.id === k.class_id; })[0], d = (D.store || {})[c.teacher_id + '|umfrage-' + c.id];
      var l = d && d.live; if (!l || !l.on || !l.open || (l.until && Date.now() > l.until + 3000) || ((l.mode || 'live') !== 'selbst' && qid !== l.cur)) return delay(false);
      var q = (l.qs || []).filter(function (x) { return x.id === qid; })[0]; if (!q) return delay(false); var n = (q.opts || []).length, ints = function (a, lo, hi) { return Array.isArray(a) && a.every(function (x) { return typeof x === 'number' && x % 1 === 0 && x >= lo && x <= hi; }); };
      var dist = function (a) { return a.filter(function (x, i) { return a.indexOf(x) === i; }).length === a.length; }, ok = false;
      if (/^(wahl|quiz|stimmung)$/.test(q.type)) ok = ints(v, 0, n - 1) && v.length >= 1 && v.length <= (q.multi ? n : 1) && dist(v);
      else if (/^(wort|text)$/.test(q.type)) { v = Array.isArray(v) ? v.filter(function (x) { return typeof x === 'string' && x.trim(); }).map(function (x) { return x.trim().slice(0, q.type === 'wort' ? 30 : 300); }) : []; ok = v.length >= 1 && v.length <= Math.min(q.type === 'wort' ? 5 : 3, Math.max(1, +q.max || (q.type === 'wort' ? 3 : 1))); }
      else if (q.type === 'skala') ok = ints(v, 1, Math.min(10, Math.max(3, +q.max || 5))) && v.length === n;
      else if (q.type === 'rang') ok = ints(v, 0, n - 1) && v.length === n && dist(v);
      else if (q.type === 'punkte') { var P = Math.min(100, Math.max(1, +q.pts || 10)), s = 0; ok = ints(v, 0, P) && v.length === n; if (ok) v.forEach(function (x) { s += x; }); ok = ok && s >= 1 && s <= P; }
      else if (q.type === 'zahl') ok = typeof v === 'number' && !(q.min !== '' && q.min != null && v < +q.min) && !(q.max !== '' && q.max != null && v > +q.max);
      else if (q.type === 'feld') { ok = v && typeof v.x === 'number' && typeof v.y === 'number'; if (ok) v = { x: Math.max(0, Math.min(100, v.x)), y: Math.max(0, Math.min(100, v.y)) }; }
      if (!ok) return delay(false); d.ans = d.ans || {}; d.ans[qid] = d.ans[qid] || {}; d.ans[qid][k.id] = JSON.parse(JSON.stringify(v)); return delay(true); },
    pinPut: function (cid, coll, id, obj) { var c = D.classes.filter(function (x) { return x.id === cid; })[0]; if (!c || c.teacher_id !== D.session.user.id) return Promise.reject(new Error('Nicht erlaubt'));
      D.store = D.store || {}; var k = c.teacher_id + '|pin-' + cid, d = D.store[k] = D.store[k] || {}; d[coll] = d[coll] || {}; if (obj == null) delete d[coll][id]; else d[coll][id] = JSON.parse(JSON.stringify(obj)); return delay(); },
    kidPin: function (t) { var k = kidOf(t), c = D.classes.filter(function (x) { return x.id === k.class_id; })[0], d = (D.store || {})[c.teacher_id + '|pin-' + c.id];
      if (!d) return delay({ boards: {}, ideas: {}, labels: {}, my: null }); var b = {}, i = {};
      Object.keys(d.boards || {}).forEach(function (id) { var x = d.boards[id]; if (x.visible === true) b[id] = { title: x.title, visible: true, at: x.at, cats: x.cats }; });
      Object.keys(d.ideas || {}).forEach(function (id) { var x = d.ideas[id]; if (!b[x.boardId]) return;
        if (x.status === 'ok') i[id] = { text: x.text, boardId: x.boardId, status: 'ok', tools: x.tools, at: x.at, okAt: x.okAt, order: x.order, lp: x.lp, cat: x.cat };
        else if (x.status === 'pending' && x.uid === k.id) i[id] = { text: x.text, boardId: x.boardId, status: 'pending', at: x.at, uid: k.id }; });
      return delay(JSON.parse(JSON.stringify({ boards: b, ideas: i, labels: ((d.settings || {}).main || {}).labels || {}, my: (d.votes || {})[k.id] || null }))); },
    kidPinIdea: function (t, board, text) { var k = kidOf(t), c = D.classes.filter(function (x) { return x.id === k.class_id; })[0], d = (D.store || {})[c.teacher_id + '|pin-' + c.id];
      if (!d || !(d.boards[board] || {}).visible) return Promise.reject(new Error('nicht offen')); var id = 'k' + Math.random().toString(36).slice(2, 10);
      d.ideas = d.ideas || {}; d.ideas[id] = { text: text, by: k.name, uid: k.id, boardId: board, status: 'pending', at: Date.now() }; return delay(id); },
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
    tafelGet: function (t) { var k = kidOf(t); return delay({ me: k.id, state: state(k.class_id) }); },
    tafelSet: function (t, s, c) {
      var k = kidOf(t); D.entries = D.entries.filter(function (e) { return e.kid_id !== k.id; });
      if (s) D.entries.push({ kid_id: k.id, class_id: k.class_id, subject_id: s, col: c });
      return delay({ me: k.id, state: state(k.class_id) });
    }
  };
  window.__GAME_HTML = GAME_HTML;
})();
