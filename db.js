// Alles, was mit der Datenbank spricht, steht in dieser Datei.
// Beim späteren Umzug (z. B. zu Infomaniak) muss nur diese Datei ersetzt werden.
(function () {
  'use strict';
  var C = window.KN_CONFIG;
  var sb = window.supabase.createClient(C.SUPABASE_URL, C.SUPABASE_KEY, {
    auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true }
  });

  function ok(res) {
    if (res.error) {
      var e = new Error(res.error.message || 'Fehler');
      e.code = res.error.code; e.hint = res.error.hint;
      throw e;
    }
    return res.data;
  }

  var GAME_COLS = 'id,title,description,fach,thema,stufe,for_all,sort,created_at,updated_at';

  window.DB = {
    // ---------- Anmeldung Lehrpersonen ----------
    session: async function () { return ok(await sb.auth.getSession()).session; },
    onAuth: function (cb) { sb.auth.onAuthStateChange(function (ev, s) { cb(ev, s); }); },
    signIn: async function (email, pw) { return ok(await sb.auth.signInWithPassword({ email: email, password: pw })); },
    signOut: async function () { await sb.auth.signOut(); },
    setPassword: async function (pw) { return ok(await sb.auth.updateUser({ password: pw })); },
    sendReset: async function (email, redirect) {
      return ok(await sb.auth.resetPasswordForEmail(email, { redirectTo: redirect }));
    },

    me: async function () {
      var s = await this.session(); if (!s) return null;
      // Version 22: valid_until (gültig bis). Solange das SQL noch nicht ausgeführt ist, ohne dieses Feld.
      var r = await sb.from('profiles').select('id,email,name,is_admin,valid_until').eq('id', s.user.id);
      if (r.error && /valid_until|column/i.test(r.error.message || '')) r = await sb.from('profiles').select('id,email,name,is_admin').eq('id', s.user.id);
      var rows = ok(r);
      return rows[0] || { id: s.user.id, email: s.user.email, name: null, is_admin: false };
    },
    setMyName: async function (id, name) { ok(await sb.from('profiles').update({ name: name }).eq('id', id)); },

    // ---------- Spiele ----------
    listGames: async function () { return ok(await sb.from('games').select(GAME_COLS).order('fach').order('thema').order('sort').order('title')); },
    gameHtml: async function (id) { return ok(await sb.from('games').select('html').eq('id', id).single()).html; },
    saveGame: async function (g) {
      var row = { title: g.title, description: g.description || '', fach: g.fach, thema: g.thema || 'Allgemein',
                  stufe: g.stufe || '', for_all: !!g.for_all, updated_at: new Date().toISOString() };
      if (g.html) row.html = g.html;
      if (g.sort != null && isFinite(g.sort)) row.sort = Math.round(g.sort);
      if (g.id) return ok(await sb.from('games').update(row).eq('id', g.id).select(GAME_COLS).single());
      return ok(await sb.from('games').insert(row).select(GAME_COLS).single());
    },
    deleteGame: async function (id) { ok(await sb.from('games').delete().eq('id', id)); },
    setGameOrder: async function (ids) {
      var res = await Promise.all(ids.map(function (id, i) { return sb.from('games').update({ sort: i + 1 }).eq('id', id); }));
      res.forEach(ok);
    },
    setGameForAll: async function (id, on) { ok(await sb.from('games').update({ for_all: on }).eq('id', id)); },

    // ---------- Lehrpersonen (Admin) ----------
    listTeachers: async function () {
      var r = await sb.from('profiles').select('id,email,name,is_admin,created_at,valid_until').order('created_at');
      this.noLicense = false;
      if (r.error && /valid_until|column/i.test(r.error.message || '')) { this.noLicense = true; r = await sb.from('profiles').select('id,email,name,is_admin,created_at').order('created_at'); }
      return ok(r);
    },
    // Lizenz «gültig bis» setzen (null = unbefristet), nur Admin
    setValidUntil: async function (tid, day) { ok(await sb.rpc('admin_set_valid', { p_teacher: tid, p_until: day || null })); },
    listTeacherGames: async function () { return ok(await sb.from('teacher_games').select('teacher_id,game_id,created_at')); },
    setTeacherGames: async function (tid, gids, on) {
      if (on) ok(await sb.from('teacher_games').upsert(gids.map(function (g) { return { teacher_id: tid, game_id: g }; }), { onConflict: 'teacher_id,game_id', ignoreDuplicates: true }));
      else ok(await sb.from('teacher_games').delete().eq('teacher_id', tid).in('game_id', gids));
    },
    setTeacherGame: async function (tid, gid, on) {
      if (on) ok(await sb.from('teacher_games').upsert({ teacher_id: tid, game_id: gid }, { onConflict: 'teacher_id,game_id', ignoreDuplicates: true }));
      else ok(await sb.from('teacher_games').delete().eq('teacher_id', tid).eq('game_id', gid));
    },

    // ---------- Klassen ----------
    // Version 20: bild, kid_tools, tafel_cols. Solange das SQL noch nicht ausgeführt ist, ohne diese Felder.
    listClasses: async function () {
      var r = await sb.from('classes').select('id,name,code,tafel_auto,created_at,bild,kid_tools,tafel_cols').order('created_at');
      if (r.error && /bild|kid_tools|tafel_cols|column/i.test(r.error.message || '')) r = await sb.from('classes').select('id,name,code,tafel_auto,created_at').order('created_at');
      return ok(r);
    },
    kidKlasse: async function (token) { try { return ok(await sb.rpc('kid_klasse', { p_token: token })); } catch (e) { return null; } },
    createClass: async function (name, code) { return ok(await sb.from('classes').insert({ name: name, code: code }).select('id,name,code,tafel_auto,created_at').single()); },
    updateClass: async function (id, patch) { ok(await sb.from('classes').update(patch).eq('id', id)); },
    deleteClass: async function (id) { ok(await sb.from('classes').delete().eq('id', id)); },

    // ---------- Kinder ----------
    listKids: async function (cid) { return ok(await sb.from('kids').select('id,name,nr,pw,created_at').eq('class_id', cid).order('nr', { ascending: true, nullsFirst: false }).order('name')); },
    addKids: async function (cid, list) {
      var rows = list.map(function (k) { return { class_id: cid, name: k.name, pw: k.pw, nr: k.nr == null ? null : k.nr }; });
      return ok(await sb.from('kids').insert(rows).select('id,name,nr,pw,created_at'));
    },
    setKidPw: async function (id, pw) { ok(await sb.from('kids').update({ pw: pw, failed: 0, locked_until: null }).eq('id', id)); },
    setKidNr: async function (id, nr) { ok(await sb.from('kids').update({ nr: nr }).eq('id', id)); },
    deleteKid: async function (id) { ok(await sb.from('kids').delete().eq('id', id)); },

    // ---------- Freigaben und Fortschritt ----------
    listReleases: async function (cid) { return ok(await sb.from('class_games').select('game_id').eq('class_id', cid)).map(function (r) { return r.game_id; }); },
    setRelease: async function (cid, gid, on) {
      if (on) ok(await sb.from('class_games').upsert({ class_id: cid, game_id: gid }, { onConflict: 'class_id,game_id', ignoreDuplicates: true }));
      else ok(await sb.from('class_games').delete().eq('class_id', cid).eq('game_id', gid));
    },
    listProgress: async function (kidIds) {
      if (!kidIds.length) return [];
      return ok(await sb.from('progress').select('kid_id,game_id,correct,attempts,done,total,plays,last_played,levels,last_level,award').in('kid_id', kidIds));
    },

    // ---------- Tafel (Lehrperson) ----------
    listSubjects: async function (cid) { return ok(await sb.from('tafel_subjects').select('id,name,color,fav,active,sort').eq('class_id', cid).order('sort').order('created_at')); },
    addSubject: async function (cid, s) { return ok(await sb.from('tafel_subjects').insert({ class_id: cid, name: s.name, color: s.color, fav: !!s.fav, active: s.active !== false, sort: s.sort || 0 }).select('id,name,color,fav,active,sort').single()); },
    updateSubject: async function (id, patch) { ok(await sb.from('tafel_subjects').update(patch).eq('id', id)); },
    deleteSubjects: async function (ids) { if (ids.length) ok(await sb.from('tafel_subjects').delete().in('id', ids)); },
    clearTafel: async function (cid) { ok(await sb.from('tafel_entries').delete().eq('class_id', cid)); },
    tafelTeacher: async function (cid) { return ok(await sb.rpc('tafel_teacher', { p_class: cid })); },

    // ---------- Kinder (ohne Konto) ----------
    kidClass: async function (code) { return ok(await sb.rpc('kid_class', { p_code: code })); },
    kidLogin: async function (code, kid, pw) { return ok(await sb.rpc('kid_login', { p_code: code, p_kid: kid, p_pw: pw })); },
    kidLogout: async function (token) { try { await sb.rpc('kid_logout', { p_token: token }); } catch (e) {} },
    kidHome: async function (token) { return ok(await sb.rpc('kid_home', { p_token: token })); },
    kidHeft: async function (token) { return ok(await sb.rpc('kid_heft', { p_token: token })); },
    kidPin: async function (token) { return ok(await sb.rpc('kid_pin', { p_token: token })); },
    kidPinIdea: async function (token, board, text) { return ok(await sb.rpc('kid_pin_idea', { p_token: token, p_board: String(board || ''), p_text: String(text || '') })); },
    // Version 23: mit Kategorie und Bild (die Pinnwand entscheidet, ob direkt angepinnt wird)
    kidPinPost: async function (token, board, text, cat, img) {
      return ok(await sb.rpc('kid_pin_post', { p_token: token, p_board: String(board || ''), p_text: String(text || ''), p_cat: cat ? String(cat) : null, p_img: img ? String(img) : null }));
    },
    kidPinVote: async function (token, body) { return ok(await sb.rpc('kid_pin_vote', { p_token: token, p_body: body })); },
    kidAtelier: async function (token) { return ok(await sb.rpc('kid_atelier', { p_token: token })); },
    kidAtelierSet: async function (token, patch) { return ok(await sb.rpc('kid_atelier_set', { p_token: token, p_patch: patch })); },
    atelierPut: async function (cid, kid, patch) { return ok(await sb.rpc('atelier_put', { p_class: cid, p_kid: kid, p_patch: patch })); },
    // Umfrage (Version 23)
    umfragePut: async function (cid, live, clear) { return ok(await sb.rpc('umfrage_put', { p_class: cid, p_live: live == null ? null : live, p_clear: clear || null })); },
    kidUmfrage: async function (token) { return ok(await sb.rpc('kid_umfrage', { p_token: token })); },
    kidUmfrageSend: async function (token, q, val) { return ok(await sb.rpc('kid_umfrage_send', { p_token: token, p_q: String(q || ''), p_val: val })); },
    pinPut: async function (cid, coll, id, obj) { return ok(await sb.rpc('pin_put', { p_class: cid, p_coll: coll, p_id: id, p_obj: obj })); },
    kidHeftOwn: async function (token, entry, del) { return ok(await sb.rpc('kid_heft_own', { p_token: token, p_entry: entry, p_delete: !!del })); },
    kidHeftTick: async function (token, id, on) { return ok(await sb.rpc('kid_heft_tick', { p_token: token, p_entry: String(id), p_on: !!on })); },
    kidGame: async function (token, gid) { return ok(await sb.rpc('kid_game', { p_token: token, p_game: gid })); },
    kidReport: async function (token, gid, r) {
      return ok(await sb.rpc('kid_report', { p_token: token, p_game: gid, p_correct: r.correct || 0, p_attempts: r.attempts || 0,
        p_done: r.done == null ? null : r.done, p_total: r.total == null ? null : r.total, p_level: r.level || null }));
    },
    kidState: async function (token, gid) { return ok(await sb.rpc('kid_state', { p_token: token, p_game: gid })); },
    kidSave: async function (token, gid, save, award) {
      return ok(await sb.rpc('kid_save', { p_token: token, p_game: gid, p_save: save == null ? null : save, p_award: award == null ? null : award }));
    },
    // ---------- Klassen-Sprint ----------
    raceLatest: async function (cid) {
      var rows = ok(await sb.from('races').select('id,status,settings,starts_at,created_at').eq('class_id', cid)
        .gt('created_at', new Date(Date.now() - 3 * 3600 * 1000).toISOString()).order('created_at', { ascending: false }).limit(1));
      return rows[0] || null;
    },
    raceCreate: async function (cid, settings) {
      await sb.from('races').update({ status: 'done' }).eq('class_id', cid).in('status', ['wait', 'run']);
      return ok(await sb.from('races').insert({ class_id: cid, settings: settings }).select('id,status,settings,starts_at,created_at').single());
    },
    raceStart: async function (id) { return ok(await sb.rpc('race_start', { p_race: id })); },
    raceEnd: async function (id) { ok(await sb.from('races').update({ status: 'done' }).eq('id', id)); },
    raceGet: async function (id) { return ok(await sb.from('races').select('id,status,settings,starts_at').eq('id', id).single()); },
    raceRuns: async function (id) { return ok(await sb.from('race_runs').select('kid_id,pos,correct,wrong,finished_at').eq('race_id', id)); },
    // ---------- Tagesfolie (Speicher pro Lehrperson) ----------
    // ---------- Einstellungen pro Klasse und Spiel ----------
    gameSettingsGet: async function (cid, gid) {
      var r = ok(await sb.from('game_settings').select('settings').eq('class_id', cid).eq('game_id', gid).maybeSingle());
      return r ? r.settings : null;
    },
    gameSettingsSet: async function (cid, gid, settings) {
      ok(await sb.from('game_settings').upsert({ class_id: cid, game_id: gid, settings: settings, updated_at: new Date().toISOString() }, { onConflict: 'class_id,game_id' }));
    },
    resetProgress: async function (kidId, gameIds) {
      var q = sb.from('progress').delete().eq('kid_id', kidId);
      if (gameIds && gameIds.length) q = q.in('game_id', gameIds);
      ok(await q);
    },
    // Vokabelkiste: gespeicherter Stand der Kinder (Übungen, Zeiten, Wörter) für die Klassen-Übersicht der Lehrperson
    listProgressSaves: async function (kidIds, gid) {
      if (!kidIds.length) return [];
      return ok(await sb.from('progress').select('kid_id,save,award,last_played').eq('game_id', gid).in('kid_id', kidIds));
    },
    listProgressGame: async function (kidIds, gid) {
      if (!kidIds.length) return [];
      return ok(await sb.from('progress').select('kid_id,award,levels,last_played').eq('game_id', gid).in('kid_id', kidIds));
    },
    storeGet: async function (doc) {
      var r = ok(await sb.from('teacher_store').select('data').eq('doc', doc).maybeSingle());
      return r ? r.data : null;
    },
    storeSet: async function (doc, data) {
      ok(await sb.from('teacher_store').upsert({ doc: doc, data: data, updated_at: new Date().toISOString() }, { onConflict: 'teacher_id,doc' }));
    },
    storeDel: async function (doc) { ok(await sb.from('teacher_store').delete().eq('doc', doc)); },
    sharedGet: async function (doc) {
      var r = ok(await sb.from('shared_store').select('data').eq('doc', doc).maybeSingle());
      return r ? r.data : null;
    },
    sharedSet: async function (doc, data) {
      ok(await sb.from('shared_store').upsert({ doc: doc, data: data, updated_at: new Date().toISOString() }, { onConflict: 'doc' }));
    },
    storeUpload: async function (blob) {
      var uid = ok(await sb.auth.getUser()).user.id;
      var ext = ((blob.type || '').split('/')[1] || 'bin').replace(/[^a-z0-9]/gi, '').slice(0, 5);
      var path = uid + '/' + Date.now().toString(36) + Math.random().toString(36).slice(2, 8) + '.' + ext;
      ok(await sb.storage.from('tagesfolien').upload(path, blob, { contentType: blob.type || 'application/octet-stream', upsert: false }));
      return sb.storage.from('tagesfolien').getPublicUrl(path).data.publicUrl;
    },
    kidRace: async function (token) { return ok(await sb.rpc('kid_race', { p_token: token })); },
    kidRaceJoin: async function (token, race) { return ok(await sb.rpc('kid_race_join', { p_token: token, p_race: race })); },
    kidRaceStep: async function (token, race, isOk) { return ok(await sb.rpc('kid_race_step', { p_token: token, p_race: race, p_ok: !!isOk })); },
    // Live-Quiz (Version 23)
    quizOpen: async function (title, qs) { return ok(await sb.rpc('quiz_open', { p_title: title, p_questions: qs })); },
    quizStep: async function (id, phase, q) { return ok(await sb.rpc('quiz_step', { p_id: id, p_phase: phase, p_q: q })); },
    quizHost: async function (id) { return ok(await sb.rpc('quiz_host', { p_id: id })); },
    quizKick: async function (id, pid) { return ok(await sb.rpc('quiz_kick', { p_id: id, p_player: pid })); },
    quizClose: async function (id) { try { await sb.rpc('quiz_close', { p_id: id }); } catch (e) {} },
    quizJoin: async function (pin, name, av) { return ok(await sb.rpc('quiz_join', { p_pin: String(pin || ''), p_name: String(name || ''), p_avatar: String(av || '') })); },
    quizState: async function (token) { return ok(await sb.rpc('quiz_state', { p_token: token })); },
    // Kinder-Quiz (Version 24)
    kidQuizList: async function (token) { return ok(await sb.rpc('kid_quiz_list', { p_token: token })); },
    kidQuizGet: async function (token, id, ver) { return ok(await sb.rpc('kid_quiz_get', { p_token: token, p_id: id, p_ver: ver == null ? null : ver })); },
    kidQuizSave: async function (token, id, ver, title, data) { return ok(await sb.rpc('kid_quiz_save', { p_token: token, p_id: id || null, p_ver: ver == null ? null : ver, p_title: String(title || ''), p_data: data })); },
    kidQuizDelete: async function (token, id) { return ok(await sb.rpc('kid_quiz_delete', { p_token: token, p_id: id })); },
    kqList: async function () { return ok(await sb.rpc('kq_list')); },
    kqGet: async function (id, ver) { return ok(await sb.rpc('kq_get', { p_id: id, p_ver: ver == null ? null : ver })); },
    kqSave: async function (id, ver, title, data) { return ok(await sb.rpc('kq_save', { p_id: id, p_ver: ver, p_title: String(title || ''), p_data: data })); },
    kqNew: async function (cid, members, title) { return ok(await sb.rpc('kq_new', { p_class: cid, p_members: members || [], p_title: String(title || '') })); },
    kqMembers: async function (id, members) { return ok(await sb.rpc('kq_members', { p_id: id, p_members: members || [] })); },
    kqDelete: async function (id) { return ok(await sb.rpc('kq_delete', { p_id: id })); },
    quizAnswer: async function (token, q, ans) { return ok(await sb.rpc('quiz_answer', { p_token: token, p_q: q, p_ans: ans })); },
    tafelGet: async function (token) { return ok(await sb.rpc('tafel_get', { p_token: token })); },
    tafelSet: async function (token, subject, col) { return ok(await sb.rpc('tafel_set', { p_token: token, p_subject: subject, p_col: col })); }
  };
})();
