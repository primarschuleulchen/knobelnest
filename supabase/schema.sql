-- =====================================================================
-- Knobelnest – Datenbank-Einrichtung (Version 28)
--
-- So geht's: In Supabase links «SQL Editor» öffnen, «New query»,
-- diesen ganzen Text einfügen und unten rechts auf «Run» klicken.
-- Das Skript darf mehrmals ausgeführt werden.
--
-- Wichtig: Die erste Person, die ein Konto bekommt, wird automatisch
-- Administratorin bzw. Administrator (das bist du).
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. Tabellen
-- ---------------------------------------------------------------------

-- Lehrpersonen (ein Eintrag pro Konto)
create table if not exists public.profiles (
  id         uuid primary key references auth.users(id) on delete cascade,
  email      text,
  name       text,
  is_admin   boolean not null default false,
  created_at timestamptz not null default now()
);

-- Spiele (die HTML-Datei liegt direkt in der Datenbank)
create table if not exists public.games (
  id          uuid primary key default gen_random_uuid(),
  title       text not null,
  description text not null default '',
  fach        text not null,
  thema       text not null default 'Allgemein',
  stufe       text not null default '',
  html        text not null,
  for_all     boolean not null default false,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);

-- Welche Lehrperson welches Spiel bekommt
create table if not exists public.teacher_games (
  teacher_id uuid not null references public.profiles(id) on delete cascade,
  game_id    uuid not null references public.games(id) on delete cascade,
  created_at timestamptz not null default now(),
  primary key (teacher_id, game_id)
);

-- Klassen einer Lehrperson
create table if not exists public.classes (
  id         uuid primary key default gen_random_uuid(),
  teacher_id uuid not null default auth.uid() references public.profiles(id) on delete cascade,
  name       text not null,
  code       text not null,
  tafel_auto boolean not null default true,
  tafel_week text default to_char(now() at time zone 'Europe/Zurich', 'IYYY-IW'),
  created_at timestamptz not null default now()
);
create unique index if not exists classes_code_key
  on public.classes (upper(regexp_replace(code, '\s', '', 'g')));

-- Kinder (nur Vor- oder Spitzname, Bildpasswort aus drei Bildern)
create table if not exists public.kids (
  id           uuid primary key default gen_random_uuid(),
  class_id     uuid not null references public.classes(id) on delete cascade,
  name         text not null,
  pw           text not null,
  failed       int not null default 0,
  locked_until timestamptz,
  created_at   timestamptz not null default now()
);
create unique index if not exists kids_class_name_key on public.kids (class_id, lower(name));
-- Version 9: freiwillige Nummer pro Kind (z. B. Klassenlisten-Nummer); sortiert die Listen
alter table public.kids add column if not exists nr int check (nr between 1 and 999);

-- Welche Spiele eine Klasse sehen darf
create table if not exists public.class_games (
  class_id   uuid not null references public.classes(id) on delete cascade,
  game_id    uuid not null references public.games(id) on delete cascade,
  created_at timestamptz not null default now(),
  primary key (class_id, game_id)
);

-- Fortschritt pro Kind und Spiel
create table if not exists public.progress (
  kid_id      uuid not null references public.kids(id) on delete cascade,
  game_id     uuid not null references public.games(id) on delete cascade,
  correct     int not null default 0,
  attempts    int not null default 0,
  done        int,
  total       int,
  plays       int not null default 0,
  last_played timestamptz,
  primary key (kid_id, game_id)
);

-- Anmeldungen der Kinder (nur über die Funktionen unten erreichbar)
create table if not exists public.kid_sessions (
  token      uuid primary key default gen_random_uuid(),
  kid_id     uuid not null references public.kids(id) on delete cascade,
  expires_at timestamptz not null default now() + interval '12 hours'
);

-- Arbeitsstand-Tafel: Fächer und Einträge
create table if not exists public.tafel_subjects (
  id         uuid primary key default gen_random_uuid(),
  class_id   uuid not null references public.classes(id) on delete cascade,
  name       text not null,
  color      text not null default '#2F5E9E',
  fav        boolean not null default false,
  active     boolean not null default true,
  sort       int not null default 0,
  created_at timestamptz not null default now()
);

create table if not exists public.tafel_entries (
  kid_id     uuid primary key references public.kids(id) on delete cascade,
  class_id   uuid not null references public.classes(id) on delete cascade,
  subject_id uuid not null references public.tafel_subjects(id) on delete cascade,
  col        text not null check (col in ('helfen', 'klar', 'frage')),
  updated_at timestamptz not null default now()
);

-- ---------------------------------------------------------------------
-- 2. Hilfsfunktionen für die Zugriffsregeln
-- ---------------------------------------------------------------------

create or replace function public.is_admin() returns boolean
language sql stable security definer set search_path = public as $$
  select coalesce((select p.is_admin from public.profiles p where p.id = auth.uid()), false);
$$;

create or replace function public.owns_class(cid uuid) returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.classes c where c.id = cid and c.teacher_id = auth.uid());
$$;

create or replace function public.teacher_has_game(tid uuid, gid uuid) returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.games g where g.id = gid and g.for_all)
      or exists (select 1 from public.teacher_games t where t.teacher_id = tid and t.game_id = gid)
      or exists (select 1 from public.profiles p where p.id = tid and p.is_admin);
$$;

create or replace function public.can_use_game(gid uuid) returns boolean
language sql stable security definer set search_path = public as $$
  select public.teacher_has_game(auth.uid(), gid);
$$;

-- Neues Konto → Eintrag in profiles. Das allererste Konto wird Admin.
create or replace function public.handle_new_user() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, email, is_admin)
  values (new.id, new.email, not exists (select 1 from public.profiles))
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- Konten, die schon vor diesem Skript existierten, nachtragen
insert into public.profiles (id, email)
  select u.id, u.email from auth.users u
  on conflict (id) do nothing;
update public.profiles set is_admin = true
  where not exists (select 1 from public.profiles where is_admin)
    and id = (select id from public.profiles order by created_at, id limit 1);

-- ---------------------------------------------------------------------
-- 3. Zugriffsregeln (Row Level Security)
-- ---------------------------------------------------------------------

alter table public.profiles       enable row level security;
alter table public.games          enable row level security;
alter table public.teacher_games  enable row level security;
alter table public.classes        enable row level security;
alter table public.kids           enable row level security;
alter table public.class_games    enable row level security;
alter table public.progress       enable row level security;
alter table public.kid_sessions   enable row level security;
alter table public.tafel_subjects enable row level security;
alter table public.tafel_entries  enable row level security;

-- profiles: eigene Zeile sehen und den Namen ändern; Admin sieht alle
drop policy if exists profiles_select on public.profiles;
create policy profiles_select on public.profiles for select to authenticated
  using (id = auth.uid() or public.is_admin());
drop policy if exists profiles_update on public.profiles;
create policy profiles_update on public.profiles for update to authenticated
  using (id = auth.uid()) with check (id = auth.uid());

-- games: Lehrpersonen sehen ihre Spiele; nur Admin verwaltet
drop policy if exists games_select on public.games;
create policy games_select on public.games for select to authenticated
  using (public.can_use_game(id));
drop policy if exists games_admin_insert on public.games;
create policy games_admin_insert on public.games for insert to authenticated
  with check (public.is_admin());
drop policy if exists games_admin_update on public.games;
create policy games_admin_update on public.games for update to authenticated
  using (public.is_admin()) with check (public.is_admin());
drop policy if exists games_admin_delete on public.games;
create policy games_admin_delete on public.games for delete to authenticated
  using (public.is_admin());

-- teacher_games: eigene Zuteilungen sehen; nur Admin teilt zu
drop policy if exists tg_select on public.teacher_games;
create policy tg_select on public.teacher_games for select to authenticated
  using (teacher_id = auth.uid() or public.is_admin());
drop policy if exists tg_insert on public.teacher_games;
create policy tg_insert on public.teacher_games for insert to authenticated
  with check (public.is_admin());
drop policy if exists tg_delete on public.teacher_games;
create policy tg_delete on public.teacher_games for delete to authenticated
  using (public.is_admin());

-- classes: nur die eigenen Klassen
drop policy if exists classes_all on public.classes;
create policy classes_all on public.classes for all to authenticated
  using (teacher_id = auth.uid()) with check (teacher_id = auth.uid());

-- kids: nur Kinder der eigenen Klassen
drop policy if exists kids_all on public.kids;
create policy kids_all on public.kids for all to authenticated
  using (public.owns_class(class_id)) with check (public.owns_class(class_id));

-- class_games: Freigaben für die eigenen Klassen, nur eigene Spiele
drop policy if exists cg_select on public.class_games;
create policy cg_select on public.class_games for select to authenticated
  using (public.owns_class(class_id));
drop policy if exists cg_insert on public.class_games;
create policy cg_insert on public.class_games for insert to authenticated
  with check (public.owns_class(class_id) and public.can_use_game(game_id));
drop policy if exists cg_delete on public.class_games;
create policy cg_delete on public.class_games for delete to authenticated
  using (public.owns_class(class_id));

-- progress: Lehrperson liest den Fortschritt der eigenen Kinder
drop policy if exists progress_select on public.progress;
create policy progress_select on public.progress for select to authenticated
  using (exists (select 1 from public.kids k where k.id = kid_id and public.owns_class(k.class_id)));
drop policy if exists progress_delete on public.progress;
create policy progress_delete on public.progress for delete to authenticated
  using (exists (select 1 from public.kids k where k.id = kid_id and public.owns_class(k.class_id)));

-- tafel: Lehrperson verwaltet Fächer und darf Einträge leeren
drop policy if exists ts_all on public.tafel_subjects;
create policy ts_all on public.tafel_subjects for all to authenticated
  using (public.owns_class(class_id)) with check (public.owns_class(class_id));
drop policy if exists te_select on public.tafel_entries;
create policy te_select on public.tafel_entries for select to authenticated
  using (public.owns_class(class_id));
drop policy if exists te_delete on public.tafel_entries;
create policy te_delete on public.tafel_entries for delete to authenticated
  using (public.owns_class(class_id));

-- kid_sessions: keine Regeln → niemand liest die Tabelle direkt

-- Rechte (Tabellen werden nicht automatisch freigegeben)
revoke all on public.profiles, public.games, public.teacher_games, public.classes,
  public.kids, public.class_games, public.progress, public.kid_sessions,
  public.tafel_subjects, public.tafel_entries from anon, authenticated;

grant select on public.profiles to authenticated;
grant update (name) on public.profiles to authenticated;
grant select, insert, update, delete on public.games, public.teacher_games,
  public.classes, public.kids, public.class_games, public.tafel_subjects to authenticated;
grant select, delete on public.progress, public.tafel_entries to authenticated;

-- ---------------------------------------------------------------------
-- 4. Funktionen für die Kinder (ohne eigenes Konto)
-- ---------------------------------------------------------------------

create or replace function public._norm_code(c text) returns text
language sql immutable as $$
  select upper(regexp_replace(coalesce(c, ''), '\s', '', 'g'));
$$;

-- Kind zu einer gültigen Anmeldung finden (intern)
create or replace function public._kid(p_token uuid) returns public.kids
language plpgsql stable security definer set search_path = public as $$
declare r public.kids;
begin
  select k.* into r from public.kid_sessions s join public.kids k on k.id = s.kid_id
   where s.token = p_token and s.expires_at > now();
  if not found then
    raise exception 'Anmeldung abgelaufen' using errcode = 'P0001', hint = 'session';
  end if;
  return r;
end;
$$;

-- Klassencode → Klasse und Namensliste
create or replace function public.kid_class(p_code text) returns json
language plpgsql stable security definer set search_path = public as $$
declare c public.classes;
begin
  select * into c from public.classes where public._norm_code(code) = public._norm_code(p_code);
  if not found then return null; end if;
  return json_build_object(
    'class_id', c.id, 'class_name', c.name,
    'kids', coalesce((select json_agg(json_build_object('id', k.id, 'name', k.name, 'nr', k.nr) order by k.nr nulls last, lower(k.name))
                        from public.kids k where k.class_id = c.id), '[]'::json));
end;
$$;

-- Bildpasswort prüfen → Anmeldung. Nach 5 Fehlversuchen 2 Minuten Pause.
create or replace function public.kid_login(p_code text, p_kid uuid, p_pw text) returns json
language plpgsql volatile security definer set search_path = public as $$
declare k public.kids; t uuid;
begin
  select kk.* into k from public.kids kk join public.classes c on c.id = kk.class_id
   where kk.id = p_kid and public._norm_code(c.code) = public._norm_code(p_code);
  if not found then return json_build_object('ok', false, 'error', 'unbekannt'); end if;
  if k.locked_until is not null and k.locked_until > now() then
    return json_build_object('ok', false, 'error', 'gesperrt',
      'seconds', ceil(extract(epoch from k.locked_until - now())));
  end if;
  if k.pw is distinct from p_pw then
    update public.kids set
      failed = case when failed + 1 >= 5 then 0 else failed + 1 end,
      locked_until = case when failed + 1 >= 5 then now() + interval '2 minutes' else null end
     where id = k.id;
    return json_build_object('ok', false, 'error', 'falsch');
  end if;
  update public.kids set failed = 0, locked_until = null where id = k.id;
  delete from public.kid_sessions where expires_at < now();
  insert into public.kid_sessions (kid_id) values (k.id) returning token into t;
  return json_build_object('ok', true, 'token', t, 'name', k.name);
end;
$$;

create or replace function public.kid_logout(p_token uuid) returns void
language sql volatile security definer set search_path = public as $$
  delete from public.kid_sessions where token = p_token;
$$;

-- Startseite des Kindes: freigegebene Spiele mit Fortschritt
create or replace function public.kid_home(p_token uuid) returns json
language plpgsql stable security definer set search_path = public as $$
declare k public.kids; tid uuid; cname text;
begin
  k := public._kid(p_token);
  select teacher_id, name into tid, cname from public.classes where id = k.class_id;
  return json_build_object(
    'kid', json_build_object('id', k.id, 'name', k.name),
    'class_name', cname,
    'games', coalesce((
      select json_agg(json_build_object(
               'id', g.id, 'title', g.title, 'description', g.description,
               'fach', g.fach, 'thema', g.thema, 'stufe', g.stufe,
               'correct', coalesce(p.correct, 0), 'attempts', coalesce(p.attempts, 0),
               'done', p.done, 'total', p.total, 'plays', coalesce(p.plays, 0),
               'last_played', p.last_played, 'levels', coalesce(p.levels, '{}'::jsonb), 'last_level', p.last_level,
               'award', coalesce(p.award, '{}'::jsonb))
             order by g.fach, g.thema, g.sort, g.title)
        from public.class_games cg
        join public.games g on g.id = cg.game_id
        left join public.progress p on p.kid_id = k.id and p.game_id = g.id
       where cg.class_id = k.class_id and public.teacher_has_game(tid, g.id)), '[]'::json));
end;
$$;

-- Spiel öffnen (nur freigegebene)
create or replace function public.kid_game(p_token uuid, p_game uuid) returns text
language plpgsql volatile security definer set search_path = public as $$
declare k public.kids; tid uuid;
begin
  k := public._kid(p_token);
  select teacher_id into tid from public.classes where id = k.class_id;
  if not exists (select 1 from public.class_games where class_id = k.class_id and game_id = p_game)
     or not public.teacher_has_game(tid, p_game) then
    raise exception 'Spiel nicht freigegeben' using errcode = 'P0001';
  end if;
  insert into public.progress (kid_id, game_id, plays, last_played)
  values (k.id, p_game, 1, now())
  on conflict (kid_id, game_id) do update set plays = public.progress.plays + 1, last_played = now();
  return (select html from public.games where id = p_game);
end;
$$;

-- Fortschritt melden (vom Spiel), auf Wunsch pro Level
alter table public.progress add column if not exists levels jsonb not null default '{}'::jsonb;
alter table public.progress add column if not exists last_level text;
alter table public.progress add column if not exists save jsonb;
alter table public.games add column if not exists sort int not null default 0;
alter table public.progress add column if not exists award jsonb not null default '{}'::jsonb;
drop function if exists public.kid_report(uuid, uuid, int, int, int, int);
create or replace function public.kid_report(p_token uuid, p_game uuid,
  p_correct int default 0, p_attempts int default 0, p_done int default null, p_total int default null, p_level text default null)
returns void
language plpgsql volatile security definer set search_path = public as $$
declare k public.kids; c int; a int; d int; t int; lv text; cur jsonb;
begin
  k := public._kid(p_token);
  if not exists (select 1 from public.class_games where class_id = k.class_id and game_id = p_game) then
    raise exception 'Spiel nicht freigegeben' using errcode = 'P0001';
  end if;
  c := least(greatest(coalesce(p_correct, 0), 0), 50);
  a := least(greatest(coalesce(p_attempts, 0), 0), 50);
  t := case when p_total is null then null else least(greatest(p_total, 0), 100000) end;
  d := case when p_done is null then null else least(greatest(p_done, 0), coalesce(t, 100000)) end;
  lv := nullif(left(btrim(coalesce(p_level, '')), 40), '');
  insert into public.progress (kid_id, game_id, correct, attempts, done, total, last_played)
  values (k.id, p_game, c, a, d, t, now())
  on conflict (kid_id, game_id) do update set
    correct = public.progress.correct + excluded.correct,
    attempts = public.progress.attempts + excluded.attempts,
    done = coalesce(excluded.done, public.progress.done),
    total = coalesce(excluded.total, public.progress.total),
    last_played = now();
  if lv is not null then
    select coalesce(levels -> lv, '{}'::jsonb) into cur from public.progress where kid_id = k.id and game_id = p_game;
    update public.progress set last_level = lv,
      levels = levels || jsonb_build_object(lv, jsonb_build_object(
        'c', coalesce((cur ->> 'c')::int, 0) + c,
        'a', coalesce((cur ->> 'a')::int, 0) + a,
        'd', coalesce(d, (cur ->> 'd')::int),
        't', coalesce(t, (cur ->> 't')::int)))
     where kid_id = k.id and game_id = p_game and (jsonb_typeof(levels) = 'object');
  end if;
end;
$$;

-- Spielstand (Sterne, Bestzeiten, Zähler) pro Kind und Spiel
create or replace function public.kid_state(p_token uuid, p_game uuid) returns json
language plpgsql stable security definer set search_path = public as $$
declare k public.kids; r public.progress; st jsonb;
begin
  k := public._kid(p_token);
  select * into r from public.progress where kid_id = k.id and game_id = p_game;
  -- Einstellungen der Lehrperson für dieses Spiel (z. B. Zeitreise); von den Einzel-Freischaltungen nur die eigenen
  select (gs.settings - 'kids') || jsonb_build_object('mine', coalesce(gs.settings -> 'kids' -> (k.id::text), '[]'::jsonb))
    into st from public.game_settings gs where gs.class_id = k.class_id and gs.game_id = p_game;
  return json_build_object('save', r.save, 'award', coalesce(r.award, '{}'::jsonb), 'settings', st);
end;
$$;

create or replace function public.kid_save(p_token uuid, p_game uuid, p_save jsonb default null, p_award jsonb default null)
returns void
language plpgsql volatile security definer set search_path = public as $$
declare k public.kids;
begin
  k := public._kid(p_token);
  if not exists (select 1 from public.class_games where class_id = k.class_id and game_id = p_game) then
    raise exception 'Spiel nicht freigegeben' using errcode = 'P0001';
  end if;
  if p_save is not null and (jsonb_typeof(p_save) <> 'object' or octet_length(p_save::text) > 200000) then
    raise exception 'Spielstand ungültig oder zu gross' using errcode = 'P0001';
  end if;
  if p_award is not null and (jsonb_typeof(p_award) <> 'object' or octet_length(p_award::text) > 20000) then
    raise exception 'Sterne-Daten ungültig oder zu gross' using errcode = 'P0001';
  end if;
  insert into public.progress (kid_id, game_id, save, award, last_played)
  values (k.id, p_game, p_save, coalesce(p_award, '{}'::jsonb), now())
  on conflict (kid_id, game_id) do update set
    save = coalesce(excluded.save, public.progress.save),
    award = case when p_award is null then public.progress.award else excluded.award end,
    last_played = now();
end;
$$;

-- ---------------------------------------------------------------------
-- 5. Arbeitsstand-Tafel
-- ---------------------------------------------------------------------

-- Montags automatisch leeren (wenn eingeschaltet)
create or replace function public._tafel_autoclear(cid uuid) returns void
language plpgsql volatile security definer set search_path = public as $$
declare wk text := to_char(now() at time zone 'Europe/Zurich', 'IYYY-IW'); auto boolean;
begin
  update public.classes set tafel_week = wk
   where id = cid and tafel_week is distinct from wk
  returning tafel_auto into auto;
  if found and auto then
    delete from public.tafel_entries where class_id = cid;
  end if;
end;
$$;

create or replace function public._tafel_state(cid uuid) returns json
language sql stable security definer set search_path = public as $$
  select json_build_object(
    'class_name', (select name from public.classes where id = cid),
    'subjects', coalesce((select json_agg(json_build_object('id', s.id, 'name', s.name, 'color', s.color)
                                            order by s.sort, lower(s.name))
                            from public.tafel_subjects s where s.class_id = cid and s.active), '[]'::json),
    'kids', coalesce((select json_agg(json_build_object('id', k.id, 'name', k.name, 'nr', k.nr) order by k.nr nulls last, lower(k.name))
                        from public.kids k where k.class_id = cid), '[]'::json),
    'entries', coalesce((select json_agg(json_build_object('kid_id', e.kid_id, 'subject_id', e.subject_id, 'col', e.col))
                           from public.tafel_entries e
                           join public.tafel_subjects s on s.id = e.subject_id and s.active
                          where e.class_id = cid), '[]'::json));
$$;

-- Tafel für ein Kind
create or replace function public.tafel_get(p_token uuid) returns json
language plpgsql volatile security definer set search_path = public as $$
declare k public.kids;
begin
  k := public._kid(p_token);
  perform public._tafel_autoclear(k.class_id);
  return json_build_object('me', k.id, 'state', public._tafel_state(k.class_id));
end;
$$;

-- Kind trägt sich ein (oder mit p_subject = null wieder aus)
create or replace function public.tafel_set(p_token uuid, p_subject uuid, p_col text) returns json
language plpgsql volatile security definer set search_path = public as $$
declare k public.kids;
begin
  k := public._kid(p_token);
  perform public._tafel_autoclear(k.class_id);
  if p_subject is null then
    delete from public.tafel_entries where kid_id = k.id;
  else
    if not exists (select 1 from public.tafel_subjects
                    where id = p_subject and class_id = k.class_id and active) then
      raise exception 'Fach nicht gefunden' using errcode = 'P0001';
    end if;
    if p_col not in ('helfen', 'klar', 'frage') then
      raise exception 'Spalte ungültig' using errcode = 'P0001';
    end if;
    insert into public.tafel_entries (kid_id, class_id, subject_id, col, updated_at)
    values (k.id, k.class_id, p_subject, p_col, now())
    on conflict (kid_id) do update set subject_id = excluded.subject_id, col = excluded.col, updated_at = now();
  end if;
  return json_build_object('me', k.id, 'state', public._tafel_state(k.class_id));
end;
$$;

-- Tafel für die Lehrperson (Wandtafel-Ansicht)
create or replace function public.tafel_teacher(p_class uuid) returns json
language plpgsql volatile security definer set search_path = public as $$
begin
  if not public.owns_class(p_class) then
    raise exception 'Keine Berechtigung' using errcode = 'P0001';
  end if;
  perform public._tafel_autoclear(p_class);
  return json_build_object('me', null, 'state', public._tafel_state(p_class));
end;
$$;

-- ---------------------------------------------------------------------
-- 6. Klassen-Sprint (alle Kinder rechnen gleichzeitig, Lehrperson zeigt das Rennen)
-- ---------------------------------------------------------------------
create table if not exists public.races (
  id uuid primary key default gen_random_uuid(),
  class_id uuid not null references public.classes(id) on delete cascade,
  status text not null default 'wait' check (status in ('wait','run','done')),
  settings jsonb not null default '{}'::jsonb,
  starts_at timestamptz,
  created_at timestamptz not null default now()
);
create index if not exists races_class_idx on public.races (class_id, created_at desc);
create table if not exists public.race_runs (
  race_id uuid not null references public.races(id) on delete cascade,
  kid_id uuid not null references public.kids(id) on delete cascade,
  pos int not null default 0,
  correct int not null default 0,
  wrong int not null default 0,
  finished_at timestamptz,
  last_at timestamptz not null default now(),
  primary key (race_id, kid_id)
);
alter table public.races enable row level security;
alter table public.race_runs enable row level security;
drop policy if exists races_all on public.races;
create policy races_all on public.races for all to authenticated
  using (public.owns_class(class_id)) with check (public.owns_class(class_id));
drop policy if exists race_runs_select on public.race_runs;
create policy race_runs_select on public.race_runs for select to authenticated
  using (exists (select 1 from public.races r where r.id = race_id and public.owns_class(r.class_id)));
drop policy if exists race_runs_delete on public.race_runs;
create policy race_runs_delete on public.race_runs for delete to authenticated
  using (exists (select 1 from public.races r where r.id = race_id and public.owns_class(r.class_id)));
revoke all on public.races, public.race_runs from anon, authenticated;
grant select, insert, update, delete on public.races to authenticated;
grant select, delete on public.race_runs to authenticated;

-- Lehrperson: Start in 4 Sekunden (Serverzeit, damit alle Geräte gleich zählen)
create or replace function public.race_start(p_race uuid) returns json
language sql volatile security invoker set search_path = public as $$
  with u as (update public.races set status = 'run', starts_at = now() + interval '4 seconds'
             where id = p_race returning starts_at)
  select json_build_object('starts_at', (select starts_at from u), 'now', now());
$$;

-- Kind: aktueller Sprint der Klasse (falls einer offen ist)
create or replace function public.kid_race(p_token uuid) returns json
language plpgsql stable security definer set search_path = public as $$
declare k public.kids; r public.races; me public.race_runs; pl int;
begin
  k := public._kid(p_token);
  select * into r from public.races where class_id = k.class_id and created_at > now() - interval '3 hours'
   order by created_at desc limit 1;
  if not found then return json_build_object('race', null, 'now', now()); end if;
  select * into me from public.race_runs where race_id = r.id and kid_id = k.id;
  if r.status = 'done' and me.kid_id is null then return json_build_object('race', null, 'now', now()); end if;
  if me.finished_at is not null then
    select count(*) into pl from public.race_runs where race_id = r.id and finished_at is not null and finished_at <= me.finished_at;
  end if;
  return json_build_object('now', now(), 'place', pl,
    'race', json_build_object('id', r.id, 'status', r.status, 'settings', r.settings, 'starts_at', r.starts_at),
    'run', case when me.kid_id is null then null else json_build_object('pos', me.pos, 'correct', me.correct, 'wrong', me.wrong, 'finished', me.finished_at is not null) end);
end;
$$;

create or replace function public.kid_race_join(p_token uuid, p_race uuid) returns json
language plpgsql volatile security definer set search_path = public as $$
declare k public.kids;
begin
  k := public._kid(p_token);
  if not exists (select 1 from public.races where id = p_race and class_id = k.class_id and status in ('wait','run')) then
    raise exception 'Kein Sprint offen' using errcode = 'P0001';
  end if;
  insert into public.race_runs (race_id, kid_id) values (p_race, k.id) on conflict do nothing;
  return public.kid_race(p_token);
end;
$$;

create or replace function public.kid_race_step(p_token uuid, p_race uuid, p_ok boolean) returns json
language plpgsql volatile security definer set search_path = public as $$
declare k public.kids; r public.races; g int; me public.race_runs; pl int;
begin
  k := public._kid(p_token);
  select * into r from public.races where id = p_race and class_id = k.class_id;
  if not found or r.status <> 'run' or r.starts_at is null or now() < r.starts_at - interval '1 second' then
    return json_build_object('ok', false);
  end if;
  g := least(greatest(coalesce((r.settings ->> 'goal')::int, 10), 3), 60);
  update public.race_runs set
      pos = least(g, pos + case when p_ok then 1 else 0 end),
      correct = correct + case when p_ok then 1 else 0 end,
      wrong = wrong + case when p_ok then 0 else 1 end,
      finished_at = case when p_ok and pos + 1 >= g then now() else finished_at end,
      last_at = now()
   where race_id = p_race and kid_id = k.id and finished_at is null and now() - last_at > interval '300 milliseconds'
   returning * into me;
  select * into me from public.race_runs where race_id = p_race and kid_id = k.id;
  if me.finished_at is not null then
    select count(*) into pl from public.race_runs where race_id = p_race and finished_at is not null and finished_at <= me.finished_at;
  end if;
  return json_build_object('ok', true, 'pos', me.pos, 'goal', g, 'finished', me.finished_at is not null, 'place', pl);
end;
$$;

-- =====================================================================
-- 7) Tagesfolie: gespeicherte Bildschirme pro Lehrperson (Version 6)
-- =====================================================================
create table if not exists public.teacher_store (
  teacher_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  doc        text not null check (length(doc) between 1 and 80),
  data       jsonb not null,
  updated_at timestamptz not null default now(),
  primary key (teacher_id, doc)
);
alter table public.teacher_store enable row level security;
drop policy if exists teacher_store_own on public.teacher_store;
create policy teacher_store_own on public.teacher_store for all to authenticated
  using (teacher_id = auth.uid()) with check (teacher_id = auth.uid());
revoke all on public.teacher_store from anon;
grant select, insert, update, delete on public.teacher_store to authenticated;

-- Vorlagen, die alle Lehrpersonen lesen und nur die Admin-Person ändert (z. B. Beispiel-Folien)
create table if not exists public.shared_store (
  doc        text primary key check (length(doc) between 1 and 80),
  data       jsonb not null,
  updated_at timestamptz not null default now()
);
alter table public.shared_store enable row level security;
drop policy if exists shared_store_read on public.shared_store;
create policy shared_store_read on public.shared_store for select to authenticated using (true);
drop policy if exists shared_store_admin on public.shared_store;
create policy shared_store_admin on public.shared_store for all to authenticated
  using (public.is_admin()) with check (public.is_admin());
revoke all on public.shared_store from anon;
grant select, insert, update, delete on public.shared_store to authenticated;

-- Bilder und Schriften der Tagesfolie (öffentlich lesbar über den Link, nur die Lehrperson selbst darf hochladen)
insert into storage.buckets (id, name, public) values ('tagesfolien', 'tagesfolien', true)
  on conflict (id) do nothing;
drop policy if exists tagesfolien_upload on storage.objects;
create policy tagesfolien_upload on storage.objects for insert to authenticated
  with check (bucket_id = 'tagesfolien' and (storage.foldername(name))[1] = auth.uid()::text);
drop policy if exists tagesfolien_delete on storage.objects;
create policy tagesfolien_delete on storage.objects for delete to authenticated
  using (bucket_id = 'tagesfolien' and (storage.foldername(name))[1] = auth.uid()::text);

-- =====================================================================
-- 8) Einstellungen pro Klasse und Spiel (Version 8), z. B. welche Zeiten der Zeitreise offen sind
-- =====================================================================
create table if not exists public.game_settings (
  class_id   uuid not null references public.classes(id) on delete cascade,
  game_id    uuid not null references public.games(id) on delete cascade,
  settings   jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now(),
  primary key (class_id, game_id)
);
alter table public.game_settings enable row level security;
drop policy if exists game_settings_own on public.game_settings;
create policy game_settings_own on public.game_settings for all to authenticated
  using (public.owns_class(class_id)) with check (public.owns_class(class_id));
revoke all on public.game_settings from anon;
grant select, insert, update, delete on public.game_settings to authenticated;

-- =====================================================================
-- 9) Hausaufgabenheft (Version 10): die Lehrperson speichert es in teacher_store als «hat-<Klasse>».
--    Ein Kind liest nur sein eigenes Heft: nur Einträge für die ganze Klasse oder für es selbst,
--    und nur seine eigenen Kontrollen und Notizen.
-- =====================================================================
create or replace function public.kid_heft(p_token uuid) returns jsonb
language plpgsql security definer set search_path = public as $$
declare
  k public.kids; t uuid; d jsonb; sid text; e jsonb; f jsonb; ents jsonb := '[]'::jsonb;
begin
  k := public._kid(p_token);
  select teacher_id into t from public.classes where id = k.class_id;
  select data into d from public.teacher_store where teacher_id = t and doc = 'hat-' || k.class_id::text;
  if d is null or jsonb_typeof(d->'entries') is distinct from 'array' then return null; end if;
  sid := k.id::text;
  for e in select x from jsonb_array_elements(d->'entries') as x loop
    if jsonb_typeof(e) <> 'object' then continue; end if;
    f := e->'for';
    if jsonb_typeof(f) = 'array' and jsonb_array_length(f) > 0 and not (f ? sid) then continue; end if;
    e := e || jsonb_build_object(
      'for', '[]'::jsonb,
      'status', case when jsonb_typeof(e->'status') = 'object' and e->'status' ? sid then jsonb_build_object(sid, e->'status'->sid) else '{}'::jsonb end,
      'notes',  case when jsonb_typeof(e->'notes')  = 'object' and e->'notes'  ? sid then jsonb_build_object(sid, e->'notes'->sid)  else '{}'::jsonb end,
      'first',  case when jsonb_typeof(e->'first')  = 'object' and e->'first'  ? sid then jsonb_build_object(sid, e->'first'->sid)  else '{}'::jsonb end,
      'neuAuf', case when jsonb_typeof(e->'neuAuf') = 'object' and e->'neuAuf' ? sid then jsonb_build_object(sid, e->'neuAuf'->sid) else '{}'::jsonb end,
      'selbst', case when jsonb_typeof(e->'selbst') = 'object' and e->'selbst' ? sid then jsonb_build_object(sid, e->'selbst'->sid) else '{}'::jsonb end);
    ents := ents || jsonb_build_array(e);
  end loop;
  return jsonb_build_object('klasse', d->'klasse', 'settings', d->'settings', 'entries', ents,
    'sus', jsonb_build_array(jsonb_build_object('id', sid, 'name', k.name)), 'kidNotes', '{}'::jsonb);
end;
$$;

-- Ein Kind hakt eine Aufgabe selbst ab (Version 11). Es ändert nur seinen eigenen Haken.
create or replace function public.kid_heft_tick(p_token uuid, p_entry text, p_on boolean) returns boolean
language plpgsql security definer set search_path = public as $$
declare
  k public.kids; t uuid; d jsonb; i int; e jsonb; sid text; f jsonb; sb jsonb;
begin
  k := public._kid(p_token);
  select teacher_id into t from public.classes where id = k.class_id;
  select data into d from public.teacher_store where teacher_id = t and doc = 'hat-' || k.class_id::text for update;
  if d is null or jsonb_typeof(d->'entries') is distinct from 'array' then return false; end if;
  sid := k.id::text;
  select (a.ord - 1)::int, a.x into i, e from jsonb_array_elements(d->'entries') with ordinality as a(x, ord)
   where a.x->>'id' = p_entry limit 1;
  if i is null or coalesce(e->>'type', 'aufgabe') <> 'aufgabe' then return false; end if;
  f := e->'for';
  if jsonb_typeof(f) = 'array' and jsonb_array_length(f) > 0 and not (f ? sid) then return false; end if;
  sb := case when jsonb_typeof(e->'selbst') = 'object' then e->'selbst' else '{}'::jsonb end;
  sb := case when p_on then sb || jsonb_build_object(sid, true) else sb - sid end;
  d := jsonb_set(d, array['entries', i::text, 'selbst'], sb, true);
  update public.teacher_store set data = d, updated_at = now() where teacher_id = t and doc = 'hat-' || k.class_id::text;
  return true;
end;
$$;

-- Ein Kind trägt eigene Aufgaben ein, ändert oder löscht sie (Version 12).
-- Nur eigene Einträge («by» = das Kind), nur Text; alles andere setzt der Server selbst.
create or replace function public.kid_heft_own(p_token uuid, p_entry jsonb, p_delete boolean default false) returns boolean
language plpgsql security definer set search_path = public as $$
declare
  k public.kids; t uuid; d jsonb; sid text; eid text; i int; old jsonb; ne jsonb; n int;
begin
  k := public._kid(p_token);
  select teacher_id into t from public.classes where id = k.class_id;
  select data into d from public.teacher_store where teacher_id = t and doc = 'hat-' || k.class_id::text for update;
  if d is null or jsonb_typeof(d->'entries') is distinct from 'array' or jsonb_typeof(p_entry) is distinct from 'object' then return false; end if;
  sid := k.id::text;
  eid := coalesce(p_entry->>'id', '');
  if eid !~ '^[A-Za-z0-9_-]{1,40}$' then return false; end if;
  select (a.ord - 1)::int, a.x into i, old from jsonb_array_elements(d->'entries') with ordinality as a(x, ord)
   where a.x->>'id' = eid limit 1;
  if old is not null and old->>'by' is distinct from sid then return false; end if;
  if p_delete then
    if i is not null then d := jsonb_set(d, '{entries}', (d->'entries') - i); end if;
  else
    if coalesce(p_entry->>'date', '') !~ '^\d{4}-\d{2}-\d{2}$' or length(btrim(coalesce(p_entry->>'title', ''))) = 0 then return false; end if;
    if i is null then
      select count(*) into n from jsonb_array_elements(d->'entries') as x where x->>'by' = sid;
      if n >= 300 then return false; end if;
    end if;
    ne := jsonb_build_object('id', eid, 'by', sid, 'for', jsonb_build_array(sid), 'type', 'aufgabe', 'ink', 'schwarz', 'mark', '',
      'date', p_entry->>'date', 'fach', left(coalesce(p_entry->>'fach', ''), 10), 'title', left(btrim(p_entry->>'title'), 120),
      'details', left(coalesce(p_entry->>'details', ''), 600),
      'order', case when jsonb_typeof(p_entry->'order') = 'number' then least(999, greatest(0, (p_entry->>'order')::numeric)) else 0 end,
      'status', '{}'::jsonb,
      'selbst', case when jsonb_typeof(old->'selbst') = 'object' then old->'selbst' else '{}'::jsonb end);
    if i is null then d := jsonb_set(d, '{entries}', (d->'entries') || jsonb_build_array(ne));
    else d := jsonb_set(d, array['entries', i::text], ne); end if;
  end if;
  update public.teacher_store set data = d, updated_at = now() where teacher_id = t and doc = 'hat-' || k.class_id::text;
  return true;
end;
$$;

-- =====================================================================
-- 10) Klassen-Pinnwand (Version 13): gespeichert bei der Lehrperson in teacher_store als «pin-<Klasse>»
--     { boards: {id: …}, ideas: {id: …}, settings: {main: …}, votes: {Kind: …} }.
--     Die Lehrperson ändert einzelne Einträge (pin_put), die Kinder schicken nur Ideen und ihre eigene Abstimmung.
--     Kinder bekommen nie Namen: nur offene Pinnwände, freigegebene Zettel ohne «von» und ihre eigenen Ideen.
-- =====================================================================
create or replace function public.pin_put(p_class uuid, p_coll text, p_id text, p_obj jsonb) returns void
language plpgsql security definer set search_path = public as $$
declare t uuid; d jsonb; dk text := 'pin-' || p_class::text;
begin
  select teacher_id into t from public.classes where id = p_class;
  if t is null or t is distinct from auth.uid() then raise exception 'Nicht erlaubt'; end if;
  if p_coll not in ('boards', 'ideas', 'settings') or coalesce(p_id, '') !~ '^[A-Za-z0-9_-]{1,40}$' then raise exception 'Ungültig'; end if;
  if p_obj is not null and (jsonb_typeof(p_obj) <> 'object' or octet_length(p_obj::text) > 20000) then raise exception 'Ungültig'; end if;
  insert into public.teacher_store (teacher_id, doc, data) values (t, dk, '{}'::jsonb) on conflict (teacher_id, doc) do nothing;
  select data into d from public.teacher_store where teacher_id = t and doc = dk for update;
  if jsonb_typeof(d->p_coll) is distinct from 'object' then d := jsonb_set(d, array[p_coll], '{}'::jsonb, true); end if;
  if p_obj is null then d := jsonb_set(d, array[p_coll], (d->p_coll) - p_id);
  else d := jsonb_set(d, array[p_coll, p_id], p_obj, true); end if;
  update public.teacher_store set data = d, updated_at = now() where teacher_id = t and doc = dk;
end;
$$;

create or replace function public.kid_pin(p_token uuid) returns jsonb
language plpgsql security definer set search_path = public as $$
declare k public.kids; t uuid; d jsonb; sid text; b jsonb; i jsonb;
begin
  k := public._kid(p_token);
  select teacher_id into t from public.classes where id = k.class_id;
  select data into d from public.teacher_store where teacher_id = t and doc = 'pin-' || k.class_id::text;
  sid := k.id::text;
  if d is null then return jsonb_build_object('boards', '{}'::jsonb, 'ideas', '{}'::jsonb, 'labels', '{}'::jsonb, 'my', null, 'me', sid, 'name', k.name); end if;
  select coalesce(jsonb_object_agg(x.key, jsonb_build_object('title', x.value->'title', 'visible', true, 'at', x.value->'at', 'cats', x.value->'cats')), '{}'::jsonb) into b
    from jsonb_each(case when jsonb_typeof(d->'boards') = 'object' then d->'boards' else '{}'::jsonb end) as x
   where jsonb_typeof(x.value) = 'object' and x.value->>'visible' = 'true';
  select coalesce(jsonb_object_agg(x.key, case when x.value->>'status' = 'ok'
           then jsonb_build_object('text', x.value->'text', 'boardId', x.value->'boardId', 'status', 'ok', 'tools', x.value->'tools', 'at', x.value->'at', 'okAt', x.value->'okAt', 'order', x.value->'order', 'lp', x.value->'lp', 'cat', x.value->'cat')
           else jsonb_build_object('text', x.value->'text', 'boardId', x.value->'boardId', 'status', 'pending', 'at', x.value->'at', 'uid', sid) end), '{}'::jsonb) into i
    from jsonb_each(case when jsonb_typeof(d->'ideas') = 'object' then d->'ideas' else '{}'::jsonb end) as x
   where jsonb_typeof(x.value) = 'object' and b ? coalesce(x.value->>'boardId', '')
     and (x.value->>'status' = 'ok' or (x.value->>'status' = 'pending' and x.value->>'uid' = sid));
  return jsonb_build_object('boards', b, 'ideas', i, 'labels', coalesce(d #> '{settings,main,labels}', '{}'::jsonb),
    'my', d #> array['votes', sid], 'me', sid, 'name', k.name);
end;
$$;

create or replace function public.kid_pin_idea(p_token uuid, p_board text, p_text text) returns text
language plpgsql security definer set search_path = public as $$
declare k public.kids; t uuid; d jsonb; sid text; nid text; n int; dk text;
begin
  k := public._kid(p_token);
  select teacher_id into t from public.classes where id = k.class_id;
  dk := 'pin-' || k.class_id::text;
  select data into d from public.teacher_store where teacher_id = t and doc = dk for update;
  if d is null or d #>> array['boards', coalesce(p_board, ''), 'visible'] is distinct from 'true' then raise exception 'Diese Pinnwand ist im Moment nicht offen.'; end if;
  if length(btrim(coalesce(p_text, ''))) = 0 then raise exception 'Leer'; end if;
  sid := k.id::text;
  select count(*) into n from jsonb_each(case when jsonb_typeof(d->'ideas') = 'object' then d->'ideas' else '{}'::jsonb end) as x
   where x.value->>'uid' = sid and x.value->>'status' = 'pending';
  if n >= 30 then raise exception 'Zu viele Ideen warten schon.'; end if;
  nid := 'k' || substr(md5(random()::text || clock_timestamp()::text), 1, 12);
  if jsonb_typeof(d->'ideas') is distinct from 'object' then d := jsonb_set(d, '{ideas}', '{}'::jsonb, true); end if;
  d := jsonb_set(d, array['ideas', nid], jsonb_build_object('text', left(btrim(p_text), 280), 'by', k.name, 'uid', sid, 'boardId', p_board,
         'status', 'pending', 'at', floor(extract(epoch from now()) * 1000)::bigint), true);
  update public.teacher_store set data = d, updated_at = now() where teacher_id = t and doc = dk;
  return nid;
end;
$$;

create or replace function public.kid_pin_vote(p_token uuid, p_body jsonb) returns boolean
language plpgsql security definer set search_path = public as $$
declare k public.kids; t uuid; d jsonb; sid text; dk text; x record; o jsonb; r jsonb := '{}'::jsonb; ok jsonb;
begin
  k := public._kid(p_token);
  select teacher_id into t from public.classes where id = k.class_id;
  dk := 'pin-' || k.class_id::text;
  select data into d from public.teacher_store where teacher_id = t and doc = dk for update;
  if d is null or jsonb_typeof(p_body) is distinct from 'object' or jsonb_typeof(p_body->'r') is distinct from 'object' then return false; end if;
  sid := k.id::text;
  for x in select key, value from jsonb_each(p_body->'r') loop
    if jsonb_typeof(x.value) <> 'object' or d #>> array['ideas', x.key, 'status'] is distinct from 'ok'
       or d #>> array['boards', coalesce(d #>> array['ideas', x.key, 'boardId'], ''), 'visible'] is distinct from 'true' then continue; end if;
    o := '{}'::jsonb;
    if jsonb_typeof(x.value->'rate') = 'number' and (x.value->>'rate')::numeric between 1 and 10 then o := o || jsonb_build_object('rate', round((x.value->>'rate')::numeric)); end if;
    if jsonb_typeof(x.value->'rate2') = 'number' and (x.value->>'rate2')::numeric between 1 and 10 then o := o || jsonb_build_object('rate2', round((x.value->>'rate2')::numeric)); end if;
    if x.value->>'agree' in ('ja', 'teils', 'nein') then o := o || jsonb_build_object('agree', x.value->>'agree'); end if;
    if jsonb_typeof(x.value->'comment') = 'string' and length(btrim(x.value->>'comment')) > 0 then o := o || jsonb_build_object('comment', left(x.value->>'comment', 400)); end if;
    if jsonb_typeof(x.value->'baro') = 'number' and (x.value->>'baro')::numeric between 0 and 10 then o := o || jsonb_build_object('baro', (x.value->>'baro')::numeric); end if;
    if o <> '{}'::jsonb then r := r || jsonb_build_object(x.key, o); end if;
  end loop;
  -- Stimmen zu Zetteln, die gerade versteckt sind, bleiben erhalten
  ok := coalesce(d #> array['votes', sid, 'r'], '{}'::jsonb);
  select coalesce(jsonb_object_agg(y.key, y.value), '{}'::jsonb) into ok from jsonb_each(case when jsonb_typeof(ok) = 'object' then ok else '{}'::jsonb end) as y
   where d #>> array['boards', coalesce(d #>> array['ideas', y.key, 'boardId'], ''), 'visible'] is distinct from 'true';
  if jsonb_typeof(d->'votes') is distinct from 'object' then d := jsonb_set(d, '{votes}', '{}'::jsonb, true); end if;
  d := jsonb_set(d, array['votes', sid], jsonb_build_object('r', ok || r, 'at', floor(extract(epoch from now()) * 1000)::bigint), true);
  update public.teacher_store set data = d, updated_at = now() where teacher_id = t and doc = dk;
  return true;
end;
$$;

-- Wer darf welche Funktion aufrufen
revoke execute on function public._kid(uuid), public._tafel_autoclear(uuid), public._tafel_state(uuid),
  public.handle_new_user() from public, anon, authenticated;
grant execute on function public.kid_class(text), public.kid_login(text, uuid, text),
  public.kid_logout(uuid), public.kid_home(uuid), public.kid_game(uuid, uuid),
  public.kid_report(uuid, uuid, int, int, int, int, text), public.kid_state(uuid, uuid),
  public.kid_save(uuid, uuid, jsonb, jsonb), public.tafel_get(uuid),
  public.kid_race(uuid), public.kid_race_join(uuid, uuid), public.kid_race_step(uuid, uuid, boolean),
  public.tafel_set(uuid, uuid, text), public.kid_heft(uuid), public.kid_heft_tick(uuid, text, boolean),
  public.kid_heft_own(uuid, jsonb, boolean), public.kid_pin(uuid), public.kid_pin_idea(uuid, text, text),
  public.kid_pin_vote(uuid, jsonb) to anon, authenticated;
revoke execute on function public.pin_put(uuid, text, text, jsonb) from public, anon;
grant execute on function public.pin_put(uuid, text, text, jsonb) to authenticated;
revoke execute on function public.tafel_teacher(uuid), public.race_start(uuid) from public, anon;
grant execute on function public.tafel_teacher(uuid), public.race_start(uuid) to authenticated;

-- ---------------------------------------------------------------------
-- Version 18: Atelier (Velo-Weg). Speicher pro Klasse in teacher_store «atelier-<Klasse>»
--   = { open: true/false, kids: { Kind-ID: { thema, umsetzung, stufe, farbe, x, y } } }
-- Die Lehrperson ändert einzelne Kinder (atelier_put), die Kinder ihr eigenes Velo (kid_atelier_set).
-- Kinder sehen die Lernerstufe nie; Thema/Umsetzungsart nur ändern, wenn der Riegel offen ist.
-- ---------------------------------------------------------------------
create or replace function public.atelier_put(p_class uuid, p_kid text, p_patch jsonb) returns void
language plpgsql security definer set search_path = public as $$
declare t uuid; d jsonb; dk text := 'atelier-' || p_class::text; e jsonb;
begin
  select teacher_id into t from public.classes where id = p_class;
  if t is null or t is distinct from auth.uid() then raise exception 'Nicht erlaubt'; end if;
  if coalesce(p_kid, '') !~ '^(_|[0-9a-f-]{36})$' then raise exception 'Ungültig'; end if;
  if p_patch is not null and (jsonb_typeof(p_patch) <> 'object' or octet_length(p_patch::text) > 4000) then raise exception 'Ungültig'; end if;
  insert into public.teacher_store (teacher_id, doc, data) values (t, dk, '{"open":false,"kids":{}}'::jsonb) on conflict (teacher_id, doc) do nothing;
  select data into d from public.teacher_store where teacher_id = t and doc = dk for update;
  if jsonb_typeof(d->'kids') is distinct from 'object' then d := jsonb_set(d, '{kids}', '{}'::jsonb, true); end if;
  if p_kid = '_' then
    if p_patch ? 'open' then d := jsonb_set(d, '{open}', to_jsonb(coalesce((p_patch->>'open')::boolean, false)), true); end if;
    -- Version 19: Umsetzungsarten zum Auswählen (höchstens 30, je 60 Zeichen)
    if jsonb_typeof(p_patch->'arten') = 'array' then
      d := jsonb_set(d, '{arten}', coalesce((select jsonb_agg(left(btrim(a.v), 60) order by a.n)
             from jsonb_array_elements_text(p_patch->'arten') with ordinality as a(v, n) where btrim(a.v) <> '' and a.n <= 30), '[]'::jsonb), true);
    end if;
  elsif p_patch is null then
    d := jsonb_set(d, '{kids}', (d->'kids') - p_kid);
  else
    e := case when jsonb_typeof(d #> array['kids', p_kid]) = 'object' then d #> array['kids', p_kid] else '{}'::jsonb end;
    d := jsonb_set(d, array['kids', p_kid], e || p_patch, true);
  end if;
  update public.teacher_store set data = d, updated_at = now() where teacher_id = t and doc = dk;
end;
$$;

create or replace function public.kid_atelier(p_token uuid) returns jsonb
language plpgsql security definer set search_path = public as $$
declare k public.kids; t uuid; d jsonb; l jsonb;
begin
  k := public._kid(p_token);
  select teacher_id into t from public.classes where id = k.class_id;
  select data into d from public.teacher_store where teacher_id = t and doc = 'atelier-' || k.class_id::text;
  if d is null then return null; end if;
  select coalesce(jsonb_agg(jsonb_build_object('id', x.id, 'name', x.name, 'nr', x.nr,
           'thema', d #> array['kids', x.id::text, 'thema'], 'umsetzung', d #> array['kids', x.id::text, 'umsetzung'],
           'farbe', d #> array['kids', x.id::text, 'farbe'], 'x', d #> array['kids', x.id::text, 'x'], 'y', d #> array['kids', x.id::text, 'y'])
         order by x.nr nulls last, lower(x.name)), '[]'::jsonb) into l
    from public.kids x where x.class_id = k.class_id;
  return jsonb_build_object('open', coalesce((d->>'open')::boolean, false), 'me', k.id, 'kids', l,
    'arten', case when jsonb_typeof(d->'arten') = 'array' then d->'arten' else '[]'::jsonb end);
end;
$$;

create or replace function public.kid_atelier_set(p_token uuid, p_patch jsonb) returns boolean
language plpgsql security definer set search_path = public as $$
declare k public.kids; t uuid; d jsonb; dk text; sid text; e jsonb; xv numeric; yv numeric;
begin
  k := public._kid(p_token);
  if p_patch is null or jsonb_typeof(p_patch) <> 'object' then return false; end if;
  select teacher_id into t from public.classes where id = k.class_id;
  dk := 'atelier-' || k.class_id::text; sid := k.id::text;
  select data into d from public.teacher_store where teacher_id = t and doc = dk for update;
  if d is null then return false; end if;
  if jsonb_typeof(d->'kids') is distinct from 'object' then d := jsonb_set(d, '{kids}', '{}'::jsonb, true); end if;
  e := case when jsonb_typeof(d #> array['kids', sid]) = 'object' then d #> array['kids', sid] else '{}'::jsonb end;
  if p_patch ? 'x' then
    if jsonb_typeof(p_patch->'x') = 'number' and jsonb_typeof(p_patch->'y') = 'number' then
      xv := greatest(0, least(100, (p_patch->>'x')::numeric)); yv := greatest(0, least(100, (p_patch->>'y')::numeric));
      e := e || jsonb_build_object('x', round(xv, 1), 'y', round(yv, 1));
    else e := e || '{"x":null,"y":null}'::jsonb; end if;
  end if;
  if coalesce(p_patch->>'farbe', '') ~ '^#[0-9a-fA-F]{6}$' then e := e || jsonb_build_object('farbe', p_patch->>'farbe'); end if;
  if coalesce((d->>'open')::boolean, false) then
    if jsonb_typeof(p_patch->'thema') = 'string' then e := e || jsonb_build_object('thema', left(btrim(p_patch->>'thema'), 80)); end if;
    if jsonb_typeof(p_patch->'umsetzung') = 'string' and (btrim(p_patch->>'umsetzung') = '' or jsonb_typeof(d->'arten') is distinct from 'array'
        or jsonb_array_length(d->'arten') = 0 or (d->'arten') ? btrim(p_patch->>'umsetzung')) then
      e := e || jsonb_build_object('umsetzung', left(btrim(p_patch->>'umsetzung'), 80)); end if;
  end if;
  d := jsonb_set(d, array['kids', sid], e, true);
  update public.teacher_store set data = d, updated_at = now() where teacher_id = t and doc = dk;
  return true;
end;
$$;

revoke execute on function public.kid_atelier(uuid), public.kid_atelier_set(uuid, jsonb), public.atelier_put(uuid, text, jsonb) from public;
grant execute on function public.kid_atelier(uuid), public.kid_atelier_set(uuid, jsonb) to anon, authenticated;
revoke execute on function public.atelier_put(uuid, text, jsonb) from anon;
grant execute on function public.atelier_put(uuid, text, jsonb) to authenticated;

-- =====================================================================
-- Version 20: Klassenbild (Maskottchen), Werkzeug-Freigaben für die Kinder, eigene Namen der Tafel-Spalten
--   classes.bild        = Bild der Klasse als kleines data:image (höchstens 400 kB), sonst das Standardbild
--   classes.kid_tools   = { heft, pin, atelier, tafel: true/false } – fehlt ein Eintrag, gilt «freigegeben»
--   classes.tafel_cols  = { helfen, klar, frage: "eigener Text" } – leer = Standardtexte
--   Die Lehrperson ändert alles über ihre eigene Klasse (RLS classes_all). Kinder lesen es nur mit kid_klasse.
-- =====================================================================
alter table public.classes add column if not exists bild text;
alter table public.classes add column if not exists kid_tools jsonb not null default '{}'::jsonb;
alter table public.classes add column if not exists tafel_cols jsonb not null default '{}'::jsonb;
do $$ begin
  if not exists (select 1 from pg_constraint where conname = 'classes_bild_size') then
    alter table public.classes add constraint classes_bild_size check (bild is null or (octet_length(bild) <= 400000 and bild like 'data:image/%'));
  end if;
  if not exists (select 1 from pg_constraint where conname = 'classes_tafel_cols_size') then
    alter table public.classes add constraint classes_tafel_cols_size check (jsonb_typeof(tafel_cols) = 'object' and octet_length(tafel_cols::text) <= 2000);
  end if;
  if not exists (select 1 from pg_constraint where conname = 'classes_kid_tools_size') then
    alter table public.classes add constraint classes_kid_tools_size check (jsonb_typeof(kid_tools) = 'object' and octet_length(kid_tools::text) <= 2000);
  end if;
end $$;

-- Was ein angemeldetes Kind über seine Klasse wissen darf: Bild, freigegebene Werkzeuge, Namen der Tafel-Spalten
create or replace function public.kid_klasse(p_token uuid) returns json
language plpgsql stable security definer set search_path = public as $$
declare k public.kids; c public.classes;
begin
  k := public._kid(p_token);
  select * into c from public.classes where id = k.class_id;
  return json_build_object('bild', c.bild, 'tools', coalesce(c.kid_tools, '{}'::jsonb), 'cols', coalesce(c.tafel_cols, '{}'::jsonb));
end;
$$;

-- Klassencode eingeben: zusätzlich das Klassenbild (für die Namenswahl)
create or replace function public.kid_class(p_code text) returns json
language plpgsql stable security definer set search_path = public as $$
declare c public.classes;
begin
  select * into c from public.classes where public._norm_code(code) = public._norm_code(p_code);
  if not found then return null; end if;
  return json_build_object(
    'class_id', c.id, 'class_name', c.name, 'bild', c.bild,
    'kids', coalesce((select json_agg(json_build_object('id', k.id, 'name', k.name, 'nr', k.nr) order by k.nr nulls last, lower(k.name))
                        from public.kids k where k.class_id = c.id), '[]'::json));
end;
$$;

revoke execute on function public.kid_klasse(uuid) from public;
grant execute on function public.kid_klasse(uuid), public.kid_class(text) to anon, authenticated;

-- =====================================================================
-- Version 21: Arbeitsstand-Tafel mit eigenen Spalten (hinzufügen, entfernen, Farbe)
--   classes.tafel_cols = { list: [ { id, label, color } ] } (höchstens 6). Ohne «list» gelten die drei Standardspalten
--   helfen / klar / frage (mit eigenen Namen wie in Version 20).
-- =====================================================================
do $$ declare cn text; begin
  for cn in select conname from pg_constraint
             where conrelid = 'public.tafel_entries'::regclass and contype = 'c' and pg_get_constraintdef(oid) like '%helfen%' loop
    execute format('alter table public.tafel_entries drop constraint %I', cn);
  end loop;
  if not exists (select 1 from pg_constraint where conname = 'tafel_entries_col_form') then
    alter table public.tafel_entries add constraint tafel_entries_col_form check (col ~ '^[a-z0-9]{1,12}$');
  end if;
end $$;

-- Gibt es diese Spalte in der Klasse?
create or replace function public._tafel_col_ok(p_class uuid, p_col text) returns boolean
language sql stable security definer set search_path = public as $$
  select coalesce((
    select case when jsonb_typeof(c.tafel_cols -> 'list') = 'array' and jsonb_array_length(c.tafel_cols -> 'list') > 0
                then exists (select 1 from jsonb_array_elements(c.tafel_cols -> 'list') x where x ->> 'id' = p_col)
                else p_col in ('helfen', 'klar', 'frage') end
      from public.classes c where c.id = p_class), false);
$$;
revoke execute on function public._tafel_col_ok(uuid, text) from public, anon, authenticated;

-- Kind trägt sich ein (oder mit p_subject = null wieder aus); erlaubt sind die Spalten der Klasse
create or replace function public.tafel_set(p_token uuid, p_subject uuid, p_col text) returns json
language plpgsql volatile security definer set search_path = public as $$
declare k public.kids;
begin
  k := public._kid(p_token);
  perform public._tafel_autoclear(k.class_id);
  if p_subject is null then
    delete from public.tafel_entries where kid_id = k.id;
  else
    if not exists (select 1 from public.tafel_subjects
                    where id = p_subject and class_id = k.class_id and active) then
      raise exception 'Fach nicht gefunden' using errcode = 'P0001';
    end if;
    if p_col is null or p_col !~ '^[a-z0-9]{1,12}$' or not public._tafel_col_ok(k.class_id, p_col) then
      raise exception 'Spalte ungültig' using errcode = 'P0001';
    end if;
    insert into public.tafel_entries (kid_id, class_id, subject_id, col, updated_at)
    values (k.id, k.class_id, p_subject, p_col, now())
    on conflict (kid_id) do update set subject_id = excluded.subject_id, col = excluded.col, updated_at = now();
  end if;
  return json_build_object('me', k.id, 'state', public._tafel_state(k.class_id));
end;
$$;

-- =====================================================================
-- Version 22: Lizenz «gültig bis» pro Lehrperson
--   profiles.valid_until = letzter gültiger Tag (leer = unbefristet). Neue Konten bekommen automatisch
--   heute + 1 Jahr (das allererste Konto = Admin bleibt unbefristet). Ändern darf das nur der Admin
--   mit admin_set_valid. Nach Ablauf zeigt das Portal der Lehrperson einen Hinweis zum Verlängern,
--   und die Kinder ihrer Klassen können sich nicht mehr anmelden («pausiert»).
-- =====================================================================
alter table public.profiles add column if not exists valid_until date;

create or replace function public.handle_new_user() returns trigger
language plpgsql security definer set search_path = public as $$
declare first boolean := not exists (select 1 from public.profiles);
begin
  insert into public.profiles (id, email, is_admin, valid_until)
  values (new.id, new.email, first,
          case when first then null else ((now() at time zone 'Europe/Zurich')::date + interval '1 year')::date end)
  on conflict (id) do nothing;
  return new;
end;
$$;

create or replace function public.admin_set_valid(p_teacher uuid, p_until date) returns void
language plpgsql volatile security definer set search_path = public as $$
begin
  if not public.is_admin() then
    raise exception 'Nur für den Admin' using errcode = '42501';
  end if;
  if p_until is not null and (p_until < date '2020-01-01' or p_until > date '2100-12-31') then
    raise exception 'Datum ungültig' using errcode = 'P0001';
  end if;
  update public.profiles set valid_until = p_until where id = p_teacher;
end;
$$;
revoke execute on function public.admin_set_valid(uuid, date) from public, anon;
grant execute on function public.admin_set_valid(uuid, date) to authenticated;

-- Kinder: Ist die Lizenz der Lehrperson abgelaufen, ist die Klasse pausiert (keine Anmeldung, keine Daten).
create or replace function public._lic_ok(p_class uuid) returns boolean
language sql stable security definer set search_path = public as $$
  select coalesce((select p.is_admin or p.valid_until is null or p.valid_until >= (now() at time zone 'Europe/Zurich')::date
                     from public.classes c join public.profiles p on p.id = c.teacher_id where c.id = p_class), true);
$$;
revoke execute on function public._lic_ok(uuid) from public, anon, authenticated;

create or replace function public._kid(p_token uuid) returns public.kids
language plpgsql stable security definer set search_path = public as $$
declare r public.kids;
begin
  select k.* into r from public.kid_sessions s join public.kids k on k.id = s.kid_id
   where s.token = p_token and s.expires_at > now();
  if not found then
    raise exception 'Anmeldung abgelaufen' using errcode = 'P0001', hint = 'session';
  end if;
  if not public._lic_ok(r.class_id) then
    raise exception 'Eure Klassenkiste ist gerade pausiert. Sag es deiner Lehrperson.' using errcode = 'P0001', hint = 'pausiert';
  end if;
  return r;
end;
$$;

create or replace function public.kid_class(p_code text) returns json
language plpgsql stable security definer set search_path = public as $$
declare c public.classes;
begin
  select * into c from public.classes where public._norm_code(code) = public._norm_code(p_code);
  if not found then return null; end if;
  if not public._lic_ok(c.id) then return json_build_object('pausiert', true, 'kids', '[]'::json); end if;
  return json_build_object(
    'class_id', c.id, 'class_name', c.name, 'bild', c.bild,
    'kids', coalesce((select json_agg(json_build_object('id', k.id, 'name', k.name, 'nr', k.nr) order by k.nr nulls last, lower(k.name))
                        from public.kids k where k.class_id = c.id), '[]'::json));
end;
$$;

create or replace function public.kid_login(p_code text, p_kid uuid, p_pw text) returns json
language plpgsql volatile security definer set search_path = public as $$
declare k public.kids; t uuid;
begin
  select kk.* into k from public.kids kk join public.classes c on c.id = kk.class_id
   where kk.id = p_kid and public._norm_code(c.code) = public._norm_code(p_code);
  if not found then return json_build_object('ok', false, 'error', 'unbekannt'); end if;
  if not public._lic_ok(k.class_id) then return json_build_object('ok', false, 'error', 'pausiert'); end if;
  if k.locked_until is not null and k.locked_until > now() then
    return json_build_object('ok', false, 'error', 'gesperrt',
      'seconds', ceil(extract(epoch from k.locked_until - now())));
  end if;
  if k.pw is distinct from p_pw then
    update public.kids set
      failed = case when failed + 1 >= 5 then 0 else failed + 1 end,
      locked_until = case when failed + 1 >= 5 then now() + interval '2 minutes' else null end
     where id = k.id;
    return json_build_object('ok', false, 'error', 'falsch');
  end if;
  update public.kids set failed = 0, locked_until = null where id = k.id;
  delete from public.kid_sessions where expires_at < now();
  insert into public.kid_sessions (kid_id) values (k.id) returning token into t;
  return json_build_object('ok', true, 'token', t, 'name', k.name);
end;
$$;
grant execute on function public.kid_class(text), public.kid_login(text, uuid, text) to anon, authenticated;

-- =====================================================================
-- Version 23: Live-Quiz
--   Die Lehrperson baut ihre Quiz im Portal (gespeichert in teacher_store «quiz»).
--   Zum Spielen öffnet sie eine Runde (quiz_live) mit einer 6-stelligen Nummer und einem QR-Code.
--   Mitspielen geht ohne Konto: Nummer + Name (+ Tierbild). Die Mitspielenden kommen nur über
--   die Funktionen quiz_join / quiz_state / quiz_answer an die Runde (Token), nie an die Tabellen.
--   Die richtigen Antworten sieht ein Gerät erst bei der Auflösung. Punkte rechnet die Datenbank.
--   Runden werden nach einem Tag automatisch gelöscht.
-- =====================================================================
create table if not exists public.quiz_live (
  id         uuid primary key default gen_random_uuid(),
  teacher_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  pin        text not null unique,
  title      text not null default '',
  questions  jsonb not null default '[]'::jsonb,
  phase      text not null default 'lobby',   -- lobby | frage | aufloesung | rangliste | ende
  q          int  not null default -1,
  q_started  timestamptz,
  created_at timestamptz not null default now()
);
create table if not exists public.quiz_players (
  id        uuid primary key default gen_random_uuid(),
  live_id   uuid not null references public.quiz_live(id) on delete cascade,
  token     uuid not null unique default gen_random_uuid(),
  name      text not null,
  avatar    text not null default 'eule',
  score     int  not null default 0,
  streak    int  not null default 0,
  answers   jsonb not null default '{}'::jsonb,
  joined_at timestamptz not null default now()
);
create unique index if not exists quiz_players_name on public.quiz_players (live_id, lower(name));
alter table public.quiz_live enable row level security;
alter table public.quiz_players enable row level security;
revoke all on public.quiz_live, public.quiz_players from anon, authenticated;

-- Text-Antworten vergleichen: Gross/klein und Leerzeichen egal
create or replace function public._quiz_norm(t text) returns text
language sql immutable as $$
  select lower(regexp_replace(btrim(coalesce(t, '')), '\s+', ' ', 'g'));
$$;

-- Lehrperson: neue Runde öffnen (alte eigene Runden und alles älter als einen Tag wird gelöscht)
create or replace function public.quiz_open(p_title text, p_questions jsonb) returns json
language plpgsql volatile security definer set search_path = public as $$
declare v_pin text; v_id uuid; i int := 0;
begin
  if auth.uid() is null then raise exception 'Bitte neu anmelden' using errcode = '42501'; end if;
  if jsonb_typeof(p_questions) is distinct from 'array' or jsonb_array_length(p_questions) < 1 or jsonb_array_length(p_questions) > 100 then
    raise exception 'Das Quiz braucht 1 bis 100 Fragen' using errcode = 'P0001';
  end if;
  if octet_length(p_questions::text) > 8000000 then raise exception 'Das Quiz ist zu gross (Bilder verkleinern)' using errcode = 'P0001'; end if;
  delete from public.quiz_live where created_at < now() - interval '1 day' or teacher_id = auth.uid();
  loop
    v_pin := lpad((floor(random() * 900000) + 100000)::int::text, 6, '0');
    exit when not exists (select 1 from public.quiz_live where pin = v_pin);
    i := i + 1; if i > 50 then raise exception 'Keine freie Nummer' using errcode = 'P0001'; end if;
  end loop;
  insert into public.quiz_live (teacher_id, pin, title, questions) values (auth.uid(), v_pin, left(coalesce(p_title, ''), 120), p_questions)
  returning id into v_id;
  return json_build_object('id', v_id, 'pin', v_pin);
end;
$$;

-- Lehrperson: nächster Schritt (Frage zeigen, auflösen, Rangliste, Ende)
create or replace function public.quiz_step(p_id uuid, p_phase text, p_q int) returns void
language plpgsql volatile security definer set search_path = public as $$
declare l public.quiz_live;
begin
  select * into l from public.quiz_live where id = p_id and teacher_id = auth.uid() for update;
  if not found then raise exception 'Runde nicht gefunden' using errcode = 'P0001'; end if;
  if p_phase not in ('lobby', 'frage', 'aufloesung', 'rangliste', 'ende') then raise exception 'Schritt ungültig' using errcode = 'P0001'; end if;
  if p_q < -1 or p_q >= jsonb_array_length(l.questions) then raise exception 'Frage ungültig' using errcode = 'P0001'; end if;
  update public.quiz_live set phase = p_phase, q = p_q,
    q_started = case when p_phase = 'frage' and (l.phase <> 'frage' or l.q <> p_q) then now() else q_started end
   where id = p_id;
end;
$$;

-- Lehrperson: Stand der Runde mit allen Mitspielenden und Antworten
create or replace function public.quiz_host(p_id uuid) returns json
language plpgsql stable security definer set search_path = public as $$
declare l public.quiz_live; lim int;
begin
  select * into l from public.quiz_live where id = p_id and teacher_id = auth.uid();
  if not found then return null; end if;
  if l.q >= 0 then lim := coalesce((l.questions -> l.q ->> 'zeit')::int, 20) * 1000; end if;
  return json_build_object('phase', l.phase, 'q', l.q, 'pin', l.pin,
    'left_ms', case when l.phase = 'frage' and l.q_started is not null then greatest(0, lim - (extract(epoch from now() - l.q_started) * 1000)::int) end,
    'players', coalesce((select json_agg(json_build_object('id', p.id, 'name', p.name, 'avatar', p.avatar, 'score', p.score, 'streak', p.streak, 'answers', p.answers) order by p.joined_at)
                           from public.quiz_players p where p.live_id = l.id), '[]'::json));
end;
$$;

-- Lehrperson: jemanden aus der Runde nehmen / Runde beenden
create or replace function public.quiz_kick(p_id uuid, p_player uuid) returns void
language sql volatile security definer set search_path = public as $$
  delete from public.quiz_players p using public.quiz_live l
   where p.id = p_player and p.live_id = l.id and l.id = p_id and l.teacher_id = auth.uid();
$$;
create or replace function public.quiz_close(p_id uuid) returns void
language sql volatile security definer set search_path = public as $$
  delete from public.quiz_live where id = p_id and teacher_id = auth.uid();
$$;
revoke execute on function public.quiz_open(text, jsonb), public.quiz_step(uuid, text, int), public.quiz_host(uuid),
  public.quiz_kick(uuid, uuid), public.quiz_close(uuid) from public, anon;
grant execute on function public.quiz_open(text, jsonb), public.quiz_step(uuid, text, int), public.quiz_host(uuid),
  public.quiz_kick(uuid, uuid), public.quiz_close(uuid) to authenticated;

-- Mitspielen: Nummer + Name + Tierbild → Token
create or replace function public.quiz_join(p_pin text, p_name text, p_avatar text) returns json
language plpgsql volatile security definer set search_path = public as $$
declare l public.quiz_live; n text := regexp_replace(btrim(coalesce(p_name, '')), '\s+', ' ', 'g'); t uuid;
begin
  select * into l from public.quiz_live where pin = regexp_replace(coalesce(p_pin, ''), '\D', '', 'g') and created_at > now() - interval '1 day';
  if not found then return json_build_object('ok', false, 'error', 'nummer'); end if;
  if l.phase = 'ende' then return json_build_object('ok', false, 'error', 'vorbei'); end if;
  if char_length(n) < 1 or char_length(n) > 20 or n ~ '[[:cntrl:]<>]' then return json_build_object('ok', false, 'error', 'name'); end if;
  if coalesce(p_avatar, '') !~ '^[a-z]{2,10}$' then p_avatar := 'eule'; end if;
  if (select count(*) from public.quiz_players where live_id = l.id) >= 80 then return json_build_object('ok', false, 'error', 'voll'); end if;
  if exists (select 1 from public.quiz_players where live_id = l.id and lower(name) = lower(n)) then
    return json_build_object('ok', false, 'error', 'vergeben');
  end if;
  insert into public.quiz_players (live_id, name, avatar) values (l.id, n, p_avatar) returning token into t;
  return json_build_object('ok', true, 'token', t, 'name', n, 'title', l.title);
end;
$$;

-- Mitspielen: aktueller Stand für ein Gerät (ohne richtige Antworten, solange die Frage läuft)
create or replace function public.quiz_state(p_token uuid) returns json
language plpgsql stable security definer set search_path = public as $$
declare p public.quiz_players; l public.quiz_live; qq jsonb; lim int; v_rank int; showq boolean;
begin
  select * into p from public.quiz_players where token = p_token;
  if not found then return json_build_object('gone', true); end if;
  select * into l from public.quiz_live where id = p.live_id;
  if l.q >= 0 then qq := l.questions -> l.q; lim := coalesce((qq ->> 'zeit')::int, 20) * 1000; end if;
  showq := l.q >= 0 and l.phase in ('frage', 'aufloesung');
  select count(*) + 1 into v_rank from public.quiz_players where live_id = l.id and score > p.score;
  return json_build_object(
    'phase', l.phase, 'q', l.q, 'n', jsonb_array_length(l.questions), 'title', l.title,
    'name', p.name, 'avatar', p.avatar, 'score', p.score, 'streak', p.streak, 'rank', v_rank,
    'players', (select count(*) from public.quiz_players where live_id = l.id),
    'left_ms', case when l.phase = 'frage' and l.q_started is not null then greatest(0, lim - (extract(epoch from now() - l.q_started) * 1000)::int) end,
    'question', case when showq then json_build_object(
        'typ', qq ->> 'typ', 'frage', qq ->> 'frage', 'bild', qq ->> 'bild', 'zeit', (qq ->> 'zeit')::int,
        'mehrfach', coalesce((qq ->> 'mehrfach')::boolean, false), 'mix', qq -> 'mix',
        'antworten', case when qq ->> 'typ' = 'text' then null else qq -> 'antworten' end,
        'nrichtig', case when qq ->> 'typ' in ('quiz', 'rf') then jsonb_array_length(coalesce(qq -> 'richtig', '[]'::jsonb)) end) end,
    'richtig', case when l.phase = 'aufloesung' then qq -> 'richtig' end,
    'mine', case when l.q >= 0 then p.answers -> (l.q::text) end,
    'top', case when l.phase in ('rangliste', 'ende') then (select json_agg(x) from (select name, avatar, score from public.quiz_players
                where live_id = l.id order by score desc, joined_at limit 5) x) end);
end;
$$;

-- Mitspielen: Antwort abgeben. p_ans = Zahlenliste (Quiz, Richtig/Falsch, Reihenfolge) oder Text.
create or replace function public.quiz_answer(p_token uuid, p_q int, p_ans jsonb) returns json
language plpgsql volatile security definer set search_path = public as $$
declare p public.quiz_players; l public.quiz_live; qq jsonb; lim int; ms int; v_ok boolean := false; pts int := 0; typ text; mult int;
begin
  select * into p from public.quiz_players where token = p_token for update;
  if not found then return json_build_object('ok', false, 'error', 'weg'); end if;
  select * into l from public.quiz_live where id = p.live_id;
  if l.phase <> 'frage' or l.q <> p_q then return json_build_object('ok', false, 'error', 'vorbei'); end if;
  if p.answers ? (p_q::text) then return json_build_object('ok', false, 'error', 'schon'); end if;
  qq := l.questions -> l.q; typ := qq ->> 'typ';
  lim := coalesce((qq ->> 'zeit')::int, 20) * 1000;
  ms := (extract(epoch from now() - l.q_started) * 1000)::int;
  if ms > lim + 1500 then return json_build_object('ok', false, 'error', 'vorbei'); end if;
  if octet_length(coalesce(p_ans, 'null'::jsonb)::text) > 400 then return json_build_object('ok', false, 'error', 'gross'); end if;
  if typ = 'text' then
    if jsonb_typeof(p_ans) <> 'string' then return json_build_object('ok', false, 'error', 'typ'); end if;
    v_ok := exists (select 1 from jsonb_array_elements_text(coalesce(qq -> 'richtig', '[]'::jsonb)) r
                     where public._quiz_norm(r) = public._quiz_norm(p_ans #>> '{}') and public._quiz_norm(r) <> '');
  else
    if jsonb_typeof(p_ans) <> 'array' or exists (select 1 from jsonb_array_elements(p_ans) e where jsonb_typeof(e) <> 'number') then
      return json_build_object('ok', false, 'error', 'typ');
    end if;
    if typ = 'reihe' then
      v_ok := p_ans = (select jsonb_agg(i order by i) from generate_series(0, jsonb_array_length(qq -> 'antworten') - 1) i);
    else
      v_ok := (select coalesce(jsonb_agg(e order by e), '[]'::jsonb) from (select distinct e from jsonb_array_elements(p_ans) e) d)
            = (select coalesce(jsonb_agg(e order by e), '[]'::jsonb) from (select distinct e from jsonb_array_elements(coalesce(qq -> 'richtig', '[]'::jsonb)) e) d);
    end if;
  end if;
  mult := coalesce((qq ->> 'punkte')::int, 1);
  if mult not in (0, 1, 2) then mult := 1; end if;
  if v_ok then pts := round(1000 * mult * (1 - least(greatest(ms, 0), lim)::numeric / lim / 2)); end if;
  update public.quiz_players set
    score = score + pts,
    streak = case when v_ok then streak + 1 else 0 end,
    answers = answers || jsonb_build_object(p_q::text, jsonb_build_object('a', p_ans, 'ok', v_ok, 'p', pts, 'ms', ms))
   where id = p.id;
  return json_build_object('ok', true);
end;
$$;
grant execute on function public.quiz_join(text, text, text), public.quiz_state(uuid), public.quiz_answer(uuid, int, jsonb) to anon, authenticated;

-- =====================================================================
-- Version 24: Klassen-Pinnwand 6 (Leinwand, Vorlagen, Bilder, Kategorien wählen, direkt anpinnen, Umfrage)
--   Kinder bekommen alle Einstellungen der offenen Pinnwände (stammen von der Lehrperson) und an den Zetteln
--   zusätzlich Bild, Position, Umfrage und – nur wenn die Lehrperson «Namen zeigen» eingeschaltet hat – den Namen.
--   Kinder können ein Bild (höchstens 250 kB) anhängen, wenn die Pinnwand das erlaubt, eine Kategorie wählen
--   und bei «direkt anpinnen» ohne Freigabe posten. Stimmen: neu auch «like» und «poll».
-- =====================================================================
create or replace function public.pin_put(p_class uuid, p_coll text, p_id text, p_obj jsonb) returns void
language plpgsql security definer set search_path = public as $$
declare t uuid; d jsonb; dk text := 'pin-' || p_class::text;
begin
  select teacher_id into t from public.classes where id = p_class;
  if t is null or t is distinct from auth.uid() then raise exception 'Nicht erlaubt'; end if;
  if p_coll not in ('boards', 'ideas', 'settings') or coalesce(p_id, '') !~ '^[A-Za-z0-9_-]{1,40}$' then raise exception 'Ungültig'; end if;
  if p_obj is not null and (jsonb_typeof(p_obj) <> 'object'
     or octet_length(p_obj::text) > case when p_coll = 'ideas' then 400000 else 60000 end) then raise exception 'Ungültig'; end if;
  insert into public.teacher_store (teacher_id, doc, data) values (t, dk, '{}'::jsonb) on conflict (teacher_id, doc) do nothing;
  select data into d from public.teacher_store where teacher_id = t and doc = dk for update;
  if jsonb_typeof(d->p_coll) is distinct from 'object' then d := jsonb_set(d, array[p_coll], '{}'::jsonb, true); end if;
  if p_obj is null then d := jsonb_set(d, array[p_coll], (d->p_coll) - p_id);
  else d := jsonb_set(d, array[p_coll, p_id], p_obj, true); end if;
  if octet_length(d::text) > 12000000 then raise exception 'Die Pinnwand ist voll. Bitte alte Zettel oder Bilder löschen.'; end if;
  update public.teacher_store set data = d, updated_at = now() where teacher_id = t and doc = dk;
end;
$$;

create or replace function public.kid_pin(p_token uuid) returns jsonb
language plpgsql security definer set search_path = public as $$
declare k public.kids; t uuid; d jsonb; sid text; b jsonb; i jsonb;
begin
  k := public._kid(p_token);
  select teacher_id into t from public.classes where id = k.class_id;
  select data into d from public.teacher_store where teacher_id = t and doc = 'pin-' || k.class_id::text;
  sid := k.id::text;
  if d is null then return jsonb_build_object('boards', '{}'::jsonb, 'ideas', '{}'::jsonb, 'labels', '{}'::jsonb, 'my', null, 'me', sid, 'name', k.name); end if;
  select coalesce(jsonb_object_agg(x.key, x.value || jsonb_build_object('visible', true)), '{}'::jsonb) into b
    from jsonb_each(case when jsonb_typeof(d->'boards') = 'object' then d->'boards' else '{}'::jsonb end) as x
   where jsonb_typeof(x.value) = 'object' and x.value->>'visible' = 'true';
  select coalesce(jsonb_object_agg(x.key, case when x.value->>'status' = 'ok'
           then jsonb_strip_nulls(jsonb_build_object('text', x.value->'text', 'boardId', x.value->'boardId', 'status', 'ok', 'tools', x.value->'tools', 'at', x.value->'at',
                  'okAt', x.value->'okAt', 'order', x.value->'order', 'lp', x.value->'lp', 'cat', x.value->'cat', 'img', x.value->'img', 'pos', x.value->'pos',
                  'poll', x.value->'poll', 'uid', case when x.value->>'uid' = sid then to_jsonb(sid) end,
                  'by', case when b #>> array[x.value->>'boardId', 'names'] = 'true' or x.value->>'uid' = sid then x.value->'by' end))
           else jsonb_strip_nulls(jsonb_build_object('text', x.value->'text', 'boardId', x.value->'boardId', 'status', 'pending', 'at', x.value->'at', 'uid', sid,
                  'cat', x.value->'cat', 'img', x.value->'img', 'by', x.value->'by')) end), '{}'::jsonb) into i
    from jsonb_each(case when jsonb_typeof(d->'ideas') = 'object' then d->'ideas' else '{}'::jsonb end) as x
   where jsonb_typeof(x.value) = 'object' and b ? coalesce(x.value->>'boardId', '')
     and (x.value->>'status' = 'ok' or (x.value->>'status' = 'pending' and x.value->>'uid' = sid));
  return jsonb_build_object('boards', b, 'ideas', i, 'labels', coalesce(d #> '{settings,main,labels}', '{}'::jsonb),
    'my', d #> array['votes', sid], 'me', sid, 'name', k.name);
end;
$$;

-- Kind postet einen Zettel (mit Kategorie und Bild, wenn die Pinnwand das erlaubt)
create or replace function public.kid_pin_post(p_token uuid, p_board text, p_text text, p_cat text, p_img text) returns text
language plpgsql security definer set search_path = public as $$
declare k public.kids; t uuid; d jsonb; bd jsonb; sid text; nid text; n int; dk text; o jsonb; txt text := left(btrim(coalesce(p_text, '')), 280);
begin
  k := public._kid(p_token);
  select teacher_id into t from public.classes where id = k.class_id;
  dk := 'pin-' || k.class_id::text;
  select data into d from public.teacher_store where teacher_id = t and doc = dk for update;
  bd := d #> array['boards', coalesce(p_board, '')];
  if d is null or bd->>'visible' is distinct from 'true' then raise exception 'Diese Pinnwand ist im Moment nicht offen.'; end if;
  if p_img is not null and (bd->>'imgs' is distinct from 'true' or p_img !~ '^data:image/(jpeg|png|webp);base64,[A-Za-z0-9+/=]+$' or length(p_img) > 250000) then
    raise exception 'Dieses Bild geht leider nicht.';
  end if;
  if length(txt) = 0 and p_img is null then raise exception 'Leer'; end if;
  if p_cat is not null and not exists (select 1 from jsonb_array_elements(case when jsonb_typeof(bd->'cats') = 'array' then bd->'cats' else '[]'::jsonb end) c
                                        where c->>'id' = p_cat) then p_cat := null; end if;
  sid := k.id::text;
  select count(*) into n from jsonb_each(case when jsonb_typeof(d->'ideas') = 'object' then d->'ideas' else '{}'::jsonb end) as x
   where x.value->>'uid' = sid and (x.value->>'status' = 'pending' or (x.value ? 'img' and x.value->>'img' is not null));
  if n >= 30 then raise exception 'Zu viele Zettel warten schon.'; end if;
  if octet_length(d::text) > 12000000 then raise exception 'Die Pinnwand ist voll.'; end if;
  nid := 'k' || substr(md5(random()::text || clock_timestamp()::text), 1, 12);
  o := jsonb_build_object('text', txt, 'by', k.name, 'uid', sid, 'boardId', p_board, 'at', floor(extract(epoch from now()) * 1000)::bigint);
  if p_cat is not null then o := o || jsonb_build_object('cat', p_cat); end if;
  if p_img is not null then o := o || jsonb_build_object('img', p_img); end if;
  if bd->>'direct' = 'true' then
    o := o || jsonb_build_object('status', 'ok', 'okAt', floor(extract(epoch from now()) * 1000)::bigint,
                                 'tools', case when jsonb_typeof(bd->'tools') = 'object' then bd->'tools' else '{}'::jsonb end);
  else o := o || jsonb_build_object('status', 'pending'); end if;
  if jsonb_typeof(d->'ideas') is distinct from 'object' then d := jsonb_set(d, '{ideas}', '{}'::jsonb, true); end if;
  d := jsonb_set(d, array['ideas', nid], o, true);
  update public.teacher_store set data = d, updated_at = now() where teacher_id = t and doc = dk;
  return nid;
end;
$$;

create or replace function public.kid_pin_vote(p_token uuid, p_body jsonb) returns boolean
language plpgsql security definer set search_path = public as $$
declare k public.kids; t uuid; d jsonb; sid text; dk text; x record; o jsonb; r jsonb := '{}'::jsonb; ok jsonb;
begin
  k := public._kid(p_token);
  select teacher_id into t from public.classes where id = k.class_id;
  dk := 'pin-' || k.class_id::text;
  select data into d from public.teacher_store where teacher_id = t and doc = dk for update;
  if d is null or jsonb_typeof(p_body) is distinct from 'object' or jsonb_typeof(p_body->'r') is distinct from 'object' then return false; end if;
  sid := k.id::text;
  for x in select key, value from jsonb_each(p_body->'r') loop
    if jsonb_typeof(x.value) <> 'object' or d #>> array['ideas', x.key, 'status'] is distinct from 'ok'
       or d #>> array['boards', coalesce(d #>> array['ideas', x.key, 'boardId'], ''), 'visible'] is distinct from 'true' then continue; end if;
    o := '{}'::jsonb;
    if jsonb_typeof(x.value->'rate') = 'number' and (x.value->>'rate')::numeric between 1 and 10 then o := o || jsonb_build_object('rate', round((x.value->>'rate')::numeric)); end if;
    if jsonb_typeof(x.value->'rate2') = 'number' and (x.value->>'rate2')::numeric between 1 and 10 then o := o || jsonb_build_object('rate2', round((x.value->>'rate2')::numeric)); end if;
    if x.value->>'agree' in ('ja', 'teils', 'nein') then o := o || jsonb_build_object('agree', x.value->>'agree'); end if;
    if jsonb_typeof(x.value->'comment') = 'string' and length(btrim(x.value->>'comment')) > 0 then o := o || jsonb_build_object('comment', left(x.value->>'comment', 400)); end if;
    if jsonb_typeof(x.value->'baro') = 'number' and (x.value->>'baro')::numeric between 0 and 10 then o := o || jsonb_build_object('baro', (x.value->>'baro')::numeric); end if;
    if x.value->'like' = 'true'::jsonb then o := o || jsonb_build_object('like', true); end if;
    if jsonb_typeof(x.value->'poll') = 'number' and (x.value->>'poll')::numeric between 0 and 9 then o := o || jsonb_build_object('poll', round((x.value->>'poll')::numeric)); end if;
    if o <> '{}'::jsonb then r := r || jsonb_build_object(x.key, o); end if;
  end loop;
  ok := coalesce(d #> array['votes', sid, 'r'], '{}'::jsonb);
  select coalesce(jsonb_object_agg(y.key, y.value), '{}'::jsonb) into ok from jsonb_each(case when jsonb_typeof(ok) = 'object' then ok else '{}'::jsonb end) as y
   where d #>> array['boards', coalesce(d #>> array['ideas', y.key, 'boardId'], ''), 'visible'] is distinct from 'true';
  if jsonb_typeof(d->'votes') is distinct from 'object' then d := jsonb_set(d, '{votes}', '{}'::jsonb, true); end if;
  d := jsonb_set(d, array['votes', sid], jsonb_build_object('r', ok || r, 'at', floor(extract(epoch from now()) * 1000)::bigint), true);
  update public.teacher_store set data = d, updated_at = now() where teacher_id = t and doc = dk;
  return true;
end;
$$;

revoke execute on function public.kid_pin_post(uuid, text, text, text, text) from public;
grant execute on function public.kid_pin_post(uuid, text, text, text, text) to anon, authenticated;

-- =====================================================================
-- Version 25: Kinder erstellen eigene Quiz
--   Die Lehrperson schaltet es pro Klasse ein (classes.kid_tools.quiz = true, fehlt = aus).
--   Ein Kinder-Quiz gehört zu einer Klasse und hat Mitglieder (members = Kinder, die es bearbeiten
--   dürfen). Ein Kind sieht nur Quiz, in denen es Mitglied ist. Die Lehrperson legt Gruppen fest.
--   ver zählt jede Änderung: Wer mit einem alten Stand speichert, bekommt den neuen Stand zurück
--   und das Gerät führt beide Änderungen zusammen (gemeinsames Bearbeiten).
-- =====================================================================
create table if not exists public.kid_quizzes (
  id         uuid primary key default gen_random_uuid(),
  class_id   uuid not null references public.classes(id) on delete cascade,
  title      text not null default '',
  data       jsonb not null default '[]'::jsonb,
  members    uuid[] not null default '{}',
  created_by uuid references public.kids(id) on delete set null,
  n          int not null default 0,
  ver        int not null default 1,
  updated_by text not null default '',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists kid_quizzes_class on public.kid_quizzes (class_id);
alter table public.kid_quizzes enable row level security;
revoke all on public.kid_quizzes from anon, authenticated;

-- Mitglieder nur aus der eigenen Klasse, Anzahl Fragen mitführen
create or replace function public._kq_fix() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  new.members := coalesce((select array_agg(k.id order by k.name) from public.kids k
                            where k.class_id = new.class_id and k.id = any(new.members)), '{}');
  new.n := case when jsonb_typeof(new.data) = 'array' then jsonb_array_length(new.data) else 0 end;
  return new;
end;
$$;
drop trigger if exists kid_quizzes_fix on public.kid_quizzes;
create trigger kid_quizzes_fix before insert or update on public.kid_quizzes for each row execute function public._kq_fix();

create or replace function public._kq_check(p_title text, p_data jsonb) returns void
language plpgsql immutable as $$
begin
  if char_length(coalesce(p_title, '')) > 80 then raise exception 'Titel zu lang' using errcode = 'P0001'; end if;
  if jsonb_typeof(p_data) is distinct from 'array' or jsonb_array_length(p_data) > 50
     or exists (select 1 from jsonb_array_elements(p_data) e where jsonb_typeof(e) <> 'object') then
    raise exception 'Quiz ungültig (höchstens 50 Fragen)' using errcode = 'P0001';
  end if;
  if octet_length(p_data::text) > 3000000 then raise exception 'Das Quiz ist zu gross. Bitte weniger oder kleinere Bilder.' using errcode = 'P0001'; end if;
end;
$$;

create or replace function public._kq_names(p_members uuid[]) returns json
language sql stable security definer set search_path = public as $$
  select coalesce(json_agg(json_build_object('id', k.id, 'name', k.name) order by k.name), '[]'::json) from public.kids k where k.id = any(p_members);
$$;
revoke execute on function public._kq_names(uuid[]) from public, anon, authenticated;

-- Kinder: Liste der eigenen Quiz (und ob die Lehrperson das Erstellen eingeschaltet hat)
create or replace function public.kid_quiz_list(p_token uuid) returns json
language plpgsql stable security definer set search_path = public as $$
declare k public.kids := public._kid(p_token);
begin
  return json_build_object('me', k.id,
    'on', coalesce((select (c.kid_tools ->> 'quiz')::boolean from public.classes c where c.id = k.class_id), false),
    'quizzes', coalesce((select json_agg(json_build_object('id', q.id, 'title', q.title, 'n', q.n, 'ver', q.ver, 'mine', q.created_by = k.id,
                 'members', public._kq_names(q.members), 'updated_at', q.updated_at, 'updated_by', q.updated_by) order by q.updated_at desc)
                 from public.kid_quizzes q where q.class_id = k.class_id and k.id = any(q.members)), '[]'::json));
end;
$$;

-- Kinder: ein Quiz laden (p_ver = eigener Stand; gleich → nur «same»)
create or replace function public.kid_quiz_get(p_token uuid, p_id uuid, p_ver int) returns json
language plpgsql stable security definer set search_path = public as $$
declare k public.kids := public._kid(p_token); q public.kid_quizzes;
begin
  select * into q from public.kid_quizzes where id = p_id and class_id = k.class_id and k.id = any(members);
  if not found then return null; end if;
  if p_ver is not null and p_ver = q.ver then return json_build_object('same', true, 'ver', q.ver); end if;
  return json_build_object('id', q.id, 'title', q.title, 'data', q.data, 'ver', q.ver, 'mine', q.created_by = k.id,
    'members', public._kq_names(q.members), 'updated_by', q.updated_by);
end;
$$;

-- Kinder: neues Quiz (p_id leer) oder speichern. Alter Stand → conflict mit dem neuen Stand.
create or replace function public.kid_quiz_save(p_token uuid, p_id uuid, p_ver int, p_title text, p_data jsonb) returns json
language plpgsql volatile security definer set search_path = public as $$
declare k public.kids := public._kid(p_token); q public.kid_quizzes; v_id uuid; v_ver int;
begin
  if not coalesce((select (c.kid_tools ->> 'quiz')::boolean from public.classes c where c.id = k.class_id), false) then
    return json_build_object('ok', false, 'error', 'aus');
  end if;
  perform public._kq_check(p_title, p_data);
  if p_id is null then
    if (select count(*) from public.kid_quizzes where created_by = k.id) >= 30 then return json_build_object('ok', false, 'error', 'viele'); end if;
    insert into public.kid_quizzes (class_id, title, data, members, created_by, updated_by)
    values (k.class_id, coalesce(p_title, ''), p_data, array[k.id], k.id, k.name) returning id, ver into v_id, v_ver;
    return json_build_object('ok', true, 'id', v_id, 'ver', v_ver);
  end if;
  select * into q from public.kid_quizzes where id = p_id and class_id = k.class_id and k.id = any(members) for update;
  if not found then return json_build_object('ok', false, 'error', 'weg'); end if;
  if q.ver <> p_ver then return json_build_object('ok', false, 'conflict', true, 'ver', q.ver, 'title', q.title, 'data', q.data); end if;
  update public.kid_quizzes set title = coalesce(p_title, ''), data = p_data, ver = ver + 1, updated_by = k.name, updated_at = now()
   where id = q.id returning ver into v_ver;
  return json_build_object('ok', true, 'id', q.id, 'ver', v_ver);
end;
$$;

-- Kinder: eigenes Quiz löschen (nur wer es erstellt hat)
create or replace function public.kid_quiz_delete(p_token uuid, p_id uuid) returns boolean
language plpgsql volatile security definer set search_path = public as $$
declare k public.kids := public._kid(p_token);
begin
  delete from public.kid_quizzes where id = p_id and class_id = k.class_id and created_by = k.id;
  return found;
end;
$$;
grant execute on function public.kid_quiz_list(uuid), public.kid_quiz_get(uuid, uuid, int), public.kid_quiz_save(uuid, uuid, int, text, jsonb),
  public.kid_quiz_delete(uuid, uuid) to anon, authenticated;

-- Lehrperson: alle Kinder-Quiz ihrer Klassen
create or replace function public.kq_list() returns json
language sql stable security definer set search_path = public as $$
  select coalesce(json_agg(json_build_object('id', q.id, 'class_id', q.class_id, 'title', q.title, 'n', q.n, 'ver', q.ver, 'members', q.members,
           'created_by', q.created_by, 'updated_at', q.updated_at, 'updated_by', q.updated_by) order by q.updated_at desc), '[]'::json)
    from public.kid_quizzes q join public.classes c on c.id = q.class_id where c.teacher_id = auth.uid();
$$;
create or replace function public.kq_get(p_id uuid, p_ver int) returns json
language plpgsql stable security definer set search_path = public as $$
declare q public.kid_quizzes;
begin
  select q2.* into q from public.kid_quizzes q2 join public.classes c on c.id = q2.class_id where q2.id = p_id and c.teacher_id = auth.uid();
  if not found then return null; end if;
  if p_ver is not null and p_ver = q.ver then return json_build_object('same', true, 'ver', q.ver); end if;
  return json_build_object('id', q.id, 'class_id', q.class_id, 'title', q.title, 'data', q.data, 'ver', q.ver, 'members', q.members, 'updated_by', q.updated_by);
end;
$$;
create or replace function public.kq_save(p_id uuid, p_ver int, p_title text, p_data jsonb) returns json
language plpgsql volatile security definer set search_path = public as $$
declare q public.kid_quizzes; v_ver int;
begin
  perform public._kq_check(p_title, p_data);
  select q2.* into q from public.kid_quizzes q2 join public.classes c on c.id = q2.class_id where q2.id = p_id and c.teacher_id = auth.uid() for update of q2;
  if not found then return json_build_object('ok', false, 'error', 'weg'); end if;
  if q.ver <> p_ver then return json_build_object('ok', false, 'conflict', true, 'ver', q.ver, 'title', q.title, 'data', q.data); end if;
  update public.kid_quizzes set title = coalesce(p_title, ''), data = p_data, ver = ver + 1, updated_by = 'Lehrperson', updated_at = now()
   where id = q.id returning ver into v_ver;
  return json_build_object('ok', true, 'id', q.id, 'ver', v_ver);
end;
$$;
create or replace function public.kq_new(p_class uuid, p_members uuid[], p_title text) returns json
language plpgsql volatile security definer set search_path = public as $$
declare v_id uuid;
begin
  if not exists (select 1 from public.classes where id = p_class and teacher_id = auth.uid()) then raise exception 'Klasse nicht gefunden' using errcode = 'P0001'; end if;
  insert into public.kid_quizzes (class_id, title, members, updated_by) values (p_class, left(coalesce(p_title, ''), 80), coalesce(p_members, '{}'), 'Lehrperson')
  returning id into v_id;
  return json_build_object('id', v_id);
end;
$$;
create or replace function public.kq_members(p_id uuid, p_members uuid[]) returns void
language sql volatile security definer set search_path = public as $$
  update public.kid_quizzes q set members = coalesce(p_members, '{}'), ver = q.ver + 1
    from public.classes c where c.id = q.class_id and q.id = p_id and c.teacher_id = auth.uid();
$$;
create or replace function public.kq_delete(p_id uuid) returns void
language sql volatile security definer set search_path = public as $$
  delete from public.kid_quizzes q using public.classes c where c.id = q.class_id and q.id = p_id and c.teacher_id = auth.uid();
$$;
revoke execute on function public.kq_list(), public.kq_get(uuid, int), public.kq_save(uuid, int, text, jsonb), public.kq_new(uuid, uuid[], text),
  public.kq_members(uuid, uuid[]), public.kq_delete(uuid) from public, anon;
grant execute on function public.kq_list(), public.kq_get(uuid, int), public.kq_save(uuid, int, text, jsonb), public.kq_new(uuid, uuid[], text),
  public.kq_members(uuid, uuid[]), public.kq_delete(uuid) to authenticated;

-- ---------------------------------------------------------------------
-- Version 26: Umfrage (Lehrperson stellt Fragen an der Wandtafel, Kinder antworten am iPad)
--   Umfragen der Lehrperson: teacher_store «umfragen» (schreibt die Lehrperson direkt)
--   Live-Stand pro Klasse: teacher_store «umfrage-<Klasse>» = { live: {...}, ans: { Frage-ID: { Kind-ID: Antwort } } }
--   live = { on, sid, title, mode (live/selbst), cur, open, show, kids, rev:[], hid:{Frage:[Kind]}, hidw:{Frage:[Wort]}, until, qs:[Fragen] }
--   Die Lehrperson schreibt «live» (umfrage_put), die Kinder nur ihre eigene Antwort (kid_umfrage_send).
--   Kinder sehen die Lösung erst nach dem Aufdecken, die Antworten der anderen nur ohne Namen und nur, wenn sie gezeigt werden.
-- ---------------------------------------------------------------------
create or replace function public._umf_ints(p jsonb, lo numeric, hi numeric) returns boolean
language sql immutable set search_path = public as $$
  select case when jsonb_typeof(p) is distinct from 'array' then false else not exists (select 1 from jsonb_array_elements(p) e
    where jsonb_typeof(e) <> 'number' or (e #>> '{}')::numeric % 1 <> 0 or (e #>> '{}')::numeric < lo or (e #>> '{}')::numeric > hi) end;
$$;

create or replace function public._umf_num(p jsonb, d numeric) returns numeric
language sql immutable set search_path = public as $$
  select case when jsonb_typeof(p) = 'number' then (p #>> '{}')::numeric
              when jsonb_typeof(p) = 'string' and (p #>> '{}') ~ '^\s*-?[0-9]+([.,][0-9]+)?\s*$' then replace(btrim(p #>> '{}'), ',', '.')::numeric
              else d end;
$$;

-- Version 27: die Regeln sind aufgeteilt (_umf_apply, _umf_view, _umf_val), damit Klasse und offene Runde dieselben nutzen.
-- Live-Stand ändern (Lehrperson): «sec» = Timer in Sekunden, die Datenbank rechnet die Endzeit selbst aus; p_clear = Antworten löschen
create or replace function public._umf_apply(d jsonb, p_live jsonb, p_clear jsonb, nowms bigint) returns jsonb
language plpgsql immutable set search_path = public as $$
declare q text;
begin
  if d is null or jsonb_typeof(d) <> 'object' then d := '{"live":null,"ans":{}}'::jsonb; end if;
  if jsonb_typeof(d->'ans') is distinct from 'object' then d := jsonb_set(d, '{ans}', '{}'::jsonb, true); end if;
  if p_live is not null then
    if jsonb_typeof(p_live) <> 'object' or octet_length(p_live::text) > 60000 then raise exception 'Ungültig'; end if;
    if jsonb_typeof(p_live->'sec') = 'number' then
      p_live := (p_live - 'sec') || jsonb_build_object('until', case when (p_live->>'sec')::numeric > 0
        then nowms + least(3600, (p_live->>'sec')::numeric)::bigint * 1000 else null end);
    end if;
    d := jsonb_set(d, '{live}', p_live, true);
  end if;
  if jsonb_typeof(p_clear) = 'array' then
    for q in select jsonb_array_elements_text(p_clear) loop
      if q = '*' then d := jsonb_set(d, '{ans}', '{}'::jsonb); else d := jsonb_set(d, '{ans}', (d->'ans') - q); end if;
    end loop;
  end if;
  return d;
end;
$$;

-- Was ein Gerät sieht (me = Kind- oder Gast-ID): nur die erlaubten Fragen, Lösung erst nach dem Aufdecken,
-- Antworten der anderen ohne Namen und nur, wenn die Lehrperson sie zeigt
create or replace function public._umf_view(d jsonb, me text) returns jsonb
language plpgsql stable set search_path = public as $$
declare l jsonb; q jsonb; qid text; qs jsonb := '[]'::jsonb; mine jsonb := '{}'::jsonb; res jsonb := '{}'::jsonb;
  hk jsonb; hw jsonb; sh boolean; nowms bigint := floor(extract(epoch from clock_timestamp()) * 1000);
begin
  l := d->'live';
  if l is null or jsonb_typeof(l) <> 'object' or not coalesce((l->>'on')::boolean, false) then return null; end if;
  sh := coalesce((l->>'show')::boolean, false) and coalesce((l->>'kids')::boolean, true);
  for q in select x from jsonb_array_elements(case when jsonb_typeof(l->'qs') = 'array' then l->'qs' else '[]'::jsonb end) x loop
    qid := q->>'id';
    continue when qid is null or (coalesce(l->>'mode', 'live') <> 'selbst' and qid is distinct from l->>'cur');
    if not (coalesce(l->'rev', '[]'::jsonb) ? qid) then q := q - 'ok'; end if;
    qs := qs || jsonb_build_array(q);
    if d #> array['ans', qid, me] is not null then mine := mine || jsonb_build_object(qid, d #> array['ans', qid, me]); end if;
    if sh then
      hk := coalesce(l #> array['hid', qid], '[]'::jsonb); hw := coalesce(l #> array['hidw', qid], '[]'::jsonb);
      res := res || jsonb_build_object(qid, coalesce((select jsonb_agg(case when q->>'type' = 'wort' and jsonb_typeof(a.value) = 'array'
          then (select coalesce(jsonb_agg(w.value), '[]'::jsonb) from jsonb_array_elements(a.value) w where not (hw ? lower(w.value #>> '{}')))
          else a.value end)
        from jsonb_each(case when jsonb_typeof(d #> array['ans', qid]) = 'object' then d #> array['ans', qid] else '{}'::jsonb end) a
        where not (hk ? a.key)), '[]'::jsonb));
    end if;
  end loop;
  return jsonb_build_object('sid', l->'sid', 'title', l->'title', 'mode', coalesce(l->>'mode', 'live'), 'cur', l->'cur',
    'open', coalesce((l->>'open')::boolean, false), 'show', sh, 'until', l->'until', 'now', nowms,
    'rev', coalesce(l->'rev', '[]'::jsonb), 'qs', qs, 'mine', mine, 'res', res);
end;
$$;

-- Antwort prüfen (Fragetyp, Grenzen) und bereinigt zurückgeben; null = nicht erlaubt
create or replace function public._umf_val(l jsonb, p_q text, p_val jsonb) returns jsonb
language plpgsql stable set search_path = public as $$
declare q jsonb; ty text; n int; mx int; v jsonb; x numeric; y numeric;
  nowms bigint := floor(extract(epoch from clock_timestamp()) * 1000);
begin
  if p_q is null or length(p_q) > 40 or p_val is null or octet_length(p_val::text) > 2000 then return null; end if;
  if l is null or jsonb_typeof(l) <> 'object' or not coalesce((l->>'on')::boolean, false) or not coalesce((l->>'open')::boolean, false) then return null; end if;
  if jsonb_typeof(l->'until') = 'number' and nowms > (l->>'until')::numeric + 3000 then return null; end if;
  if coalesce(l->>'mode', 'live') <> 'selbst' and p_q is distinct from l->>'cur' then return null; end if;
  select x2 into q from jsonb_array_elements(case when jsonb_typeof(l->'qs') = 'array' then l->'qs' else '[]'::jsonb end) x2 where x2->>'id' = p_q limit 1;
  if q is null then return null; end if;
  ty := q->>'type';
  n := case when jsonb_typeof(q->'opts') = 'array' then jsonb_array_length(q->'opts') else 0 end;
  if ty in ('wahl', 'quiz', 'stimmung') then
    mx := case when coalesce((q->>'multi')::boolean, false) then n else 1 end;
    if not public._umf_ints(p_val, 0, n - 1) or jsonb_array_length(p_val) < 1 or jsonb_array_length(p_val) > mx
       or (select count(distinct e #>> '{}') from jsonb_array_elements(p_val) e) <> jsonb_array_length(p_val) then return null; end if;
    v := p_val;
  elsif ty in ('wort', 'text') then
    if jsonb_typeof(p_val) <> 'array' then return null; end if;
    mx := least(case when ty = 'wort' then 5 else 3 end, greatest(1, public._umf_num(q->'max', case when ty = 'wort' then 3 else 1 end)))::int;
    select coalesce(jsonb_agg(to_jsonb(left(btrim(e.j #>> '{}'), case when ty = 'wort' then 30 else 300 end)) order by e.o), '[]'::jsonb) into v
      from jsonb_array_elements(p_val) with ordinality as e(j, o) where jsonb_typeof(e.j) = 'string' and btrim(e.j #>> '{}') <> '';
    if jsonb_array_length(v) < 1 or jsonb_array_length(v) > mx then return null; end if;
  elsif ty = 'skala' then
    mx := least(10, greatest(3, public._umf_num(q->'max', 5)))::int;
    if not public._umf_ints(p_val, 1, mx) or jsonb_array_length(p_val) <> n then return null; end if;
    v := p_val;
  elsif ty = 'rang' then
    if not public._umf_ints(p_val, 0, n - 1) or jsonb_array_length(p_val) <> n
       or (select count(distinct e #>> '{}') from jsonb_array_elements(p_val) e) <> n then return null; end if;
    v := p_val;
  elsif ty = 'punkte' then
    mx := least(100, greatest(1, public._umf_num(q->'pts', 10)))::int;
    if not public._umf_ints(p_val, 0, mx) or jsonb_array_length(p_val) <> n then return null; end if;
    if (select sum((e #>> '{}')::numeric) from jsonb_array_elements(p_val) e) not between 1 and mx then return null; end if;
    v := p_val;
  elsif ty = 'zahl' then
    if jsonb_typeof(p_val) <> 'number' then return null; end if;
    x := (p_val #>> '{}')::numeric;
    if x < public._umf_num(q->'min', -1e12) or x > public._umf_num(q->'max', 1e12) or abs(x) > 1e12 then return null; end if;
    v := to_jsonb(round(x, 2));
  elsif ty = 'feld' then
    if jsonb_typeof(p_val) <> 'object' or jsonb_typeof(p_val->'x') <> 'number' or jsonb_typeof(p_val->'y') <> 'number' then return null; end if;
    x := greatest(0, least(100, (p_val->>'x')::numeric)); y := greatest(0, least(100, (p_val->>'y')::numeric));
    v := jsonb_build_object('x', round(x, 1), 'y', round(y, 1));
  else
    return null;
  end if;
  return v;
end;
$$;

-- Antwort eintragen (gibt das neue Dokument zurück)
create or replace function public._umf_put_ans(d jsonb, p_q text, me text, v jsonb) returns jsonb
language plpgsql immutable set search_path = public as $$
begin
  if jsonb_typeof(d->'ans') is distinct from 'object' then d := jsonb_set(d, '{ans}', '{}'::jsonb, true); end if;
  if jsonb_typeof(d #> array['ans', p_q]) is distinct from 'object' then d := jsonb_set(d, array['ans', p_q], '{}'::jsonb, true); end if;
  return jsonb_set(d, array['ans', p_q, me], v, true);
end;
$$;

create or replace function public.umfrage_put(p_class uuid, p_live jsonb, p_clear jsonb default null) returns json
language plpgsql security definer set search_path = public as $$
declare t uuid; d jsonb; dk text := 'umfrage-' || p_class::text;
  nowms bigint := floor(extract(epoch from clock_timestamp()) * 1000);
begin
  select teacher_id into t from public.classes where id = p_class;
  if t is null or t is distinct from auth.uid() then raise exception 'Nicht erlaubt'; end if;
  insert into public.teacher_store (teacher_id, doc, data) values (t, dk, '{"live":null,"ans":{}}'::jsonb) on conflict (teacher_id, doc) do nothing;
  select data into d from public.teacher_store where teacher_id = t and doc = dk for update;
  d := public._umf_apply(d, p_live, p_clear, nowms);
  update public.teacher_store set data = d, updated_at = now() where teacher_id = t and doc = dk;
  return json_build_object('now', nowms, 'until', d #> '{live,until}');
end;
$$;

create or replace function public.kid_umfrage(p_token uuid) returns jsonb
language plpgsql security definer set search_path = public as $$
declare k public.kids; t uuid; d jsonb;
begin
  k := public._kid(p_token);
  select teacher_id into t from public.classes where id = k.class_id;
  select data into d from public.teacher_store where teacher_id = t and doc = 'umfrage-' || k.class_id::text;
  return public._umf_view(d, k.id::text);
end;
$$;

create or replace function public.kid_umfrage_send(p_token uuid, p_q text, p_val jsonb) returns boolean
language plpgsql security definer set search_path = public as $$
declare k public.kids; t uuid; d jsonb; dk text; v jsonb;
begin
  k := public._kid(p_token);
  select teacher_id into t from public.classes where id = k.class_id;
  dk := 'umfrage-' || k.class_id::text;
  select data into d from public.teacher_store where teacher_id = t and doc = dk for update;
  if d is null then return false; end if;
  v := public._umf_val(d->'live', p_q, p_val);
  if v is null then return false; end if;
  update public.teacher_store set data = public._umf_put_ans(d, p_q, k.id::text, v), updated_at = now() where teacher_id = t and doc = dk;
  return true;
end;
$$;

revoke execute on function public._umf_ints(jsonb, numeric, numeric), public._umf_num(jsonb, numeric), public._umf_apply(jsonb, jsonb, jsonb, bigint),
  public._umf_view(jsonb, text), public._umf_val(jsonb, text, jsonb), public._umf_put_ans(jsonb, text, text, jsonb) from public, anon, authenticated;
revoke execute on function public.kid_umfrage(uuid), public.kid_umfrage_send(uuid, text, jsonb), public.umfrage_put(uuid, jsonb, jsonb) from public;
grant execute on function public.kid_umfrage(uuid), public.kid_umfrage_send(uuid, text, jsonb) to anon, authenticated;
revoke execute on function public.umfrage_put(uuid, jsonb, jsonb) from anon;
grant execute on function public.umfrage_put(uuid, jsonb, jsonb) to authenticated;

-- ---------------------------------------------------------------------
-- Version 27: Umfrage offen teilen (QR-Code, ohne Login)
--   Die Lehrperson startet eine offene Runde mit einer 6-stelligen Nummer (umf_runden). Mitmachen geht über
--   #/u/<Nummer> mit freiwilligem Namen (umf_gaeste, Token). Gäste kommen nur über umf_gast / umf_gast_send an die Runde,
--   mit denselben Regeln wie die Kinder (_umf_view, _umf_val). Pro Lehrperson gibt es eine offene Runde;
--   sie bleibt für die Ergebnisse stehen, bis eine neue gestartet wird, und wird nach 30 Tagen gelöscht.
-- ---------------------------------------------------------------------
create table if not exists public.umf_runden (
  id         uuid primary key default gen_random_uuid(),
  teacher_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  nr         text not null unique,
  data       jsonb not null default '{"live":null,"ans":{}}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create table if not exists public.umf_gaeste (
  id         uuid primary key default gen_random_uuid(),
  runde      uuid not null references public.umf_runden(id) on delete cascade,
  token      uuid not null unique default gen_random_uuid(),
  name       text not null,
  created_at timestamptz not null default now()
);
create index if not exists umf_gaeste_runde on public.umf_gaeste (runde);
alter table public.umf_runden enable row level security;
alter table public.umf_gaeste enable row level security;
revoke all on public.umf_runden, public.umf_gaeste from anon, authenticated;

-- Lehrperson: neue offene Runde (die alte eigene wird gelöscht)
create or replace function public.umf_offen_open(p_live jsonb) returns json
language plpgsql volatile security definer set search_path = public as $$
declare v_nr text; v_id uuid; i int := 0; d jsonb; nowms bigint := floor(extract(epoch from clock_timestamp()) * 1000);
begin
  if auth.uid() is null then raise exception 'Bitte neu anmelden' using errcode = '42501'; end if;
  delete from public.umf_runden where teacher_id = auth.uid() or updated_at < now() - interval '30 days';
  loop
    v_nr := lpad((floor(random() * 900000) + 100000)::int::text, 6, '0');
    exit when not exists (select 1 from public.umf_runden where nr = v_nr);
    i := i + 1; if i > 50 then raise exception 'Keine freie Nummer' using errcode = 'P0001'; end if;
  end loop;
  d := public._umf_apply(null, p_live, null, nowms);
  insert into public.umf_runden (teacher_id, nr, data) values (auth.uid(), v_nr, d) returning id into v_id;
  return json_build_object('id', v_id, 'nr', v_nr, 'now', nowms, 'until', d #> '{live,until}');
end;
$$;

create or replace function public.umf_offen_put(p_id uuid, p_live jsonb, p_clear jsonb default null) returns json
language plpgsql volatile security definer set search_path = public as $$
declare d jsonb; nowms bigint := floor(extract(epoch from clock_timestamp()) * 1000);
begin
  select data into d from public.umf_runden where id = p_id and teacher_id = auth.uid() for update;
  if not found then raise exception 'Runde nicht gefunden' using errcode = 'P0001'; end if;
  d := public._umf_apply(d, p_live, p_clear, nowms);
  update public.umf_runden set data = d, updated_at = now() where id = p_id;
  return json_build_object('now', nowms, 'until', d #> '{live,until}');
end;
$$;

-- Lehrperson: Stand der eigenen offenen Runde mit allen Gästen (ohne p_id: die neuste)
create or replace function public.umf_offen_host(p_id uuid default null) returns json
language plpgsql stable security definer set search_path = public as $$
declare r public.umf_runden;
begin
  select * into r from public.umf_runden where teacher_id = auth.uid() and (p_id is null or id = p_id) order by created_at desc limit 1;
  if not found then return null; end if;
  return json_build_object('id', r.id, 'nr', r.nr, 'data', r.data,
    'gaeste', coalesce((select json_agg(json_build_object('id', g.id, 'name', g.name) order by g.created_at) from public.umf_gaeste g where g.runde = r.id), '[]'::json));
end;
$$;

create or replace function public.umf_offen_close(p_id uuid) returns void
language sql volatile security definer set search_path = public as $$
  delete from public.umf_runden where id = p_id and teacher_id = auth.uid();
$$;

-- Gast: Nummer + freiwilliger Name → Token
create or replace function public.umf_gast_join(p_nr text, p_name text) returns json
language plpgsql volatile security definer set search_path = public as $$
declare r public.umf_runden; n text := regexp_replace(btrim(coalesce(p_name, '')), '\s+', ' ', 'g'); t uuid; c int;
begin
  select * into r from public.umf_runden where nr = regexp_replace(coalesce(p_nr, ''), '\D', '', 'g');
  if not found then return json_build_object('ok', false, 'error', 'nummer'); end if;
  if not coalesce((r.data #>> '{live,on}')::boolean, false) then return json_build_object('ok', false, 'error', 'vorbei'); end if;
  if char_length(n) > 20 or n ~ '[[:cntrl:]<>]' then return json_build_object('ok', false, 'error', 'name'); end if;
  select count(*) into c from public.umf_gaeste where runde = r.id;
  if c >= 300 then return json_build_object('ok', false, 'error', 'voll'); end if;
  if n = '' then n := 'Gast ' || (c + 1); end if;
  insert into public.umf_gaeste (runde, name) values (r.id, n) returning token into t;
  return json_build_object('ok', true, 'token', t, 'name', n);
end;
$$;

create or replace function public.umf_gast(p_token uuid) returns jsonb
language plpgsql stable security definer set search_path = public as $$
declare g public.umf_gaeste; d jsonb;
begin
  select * into g from public.umf_gaeste where token = p_token;
  if not found then return '{"gone":true}'::jsonb; end if;
  select data into d from public.umf_runden where id = g.runde;
  return public._umf_view(d, g.id::text);
end;
$$;

create or replace function public.umf_gast_send(p_token uuid, p_q text, p_val jsonb) returns boolean
language plpgsql volatile security definer set search_path = public as $$
declare g public.umf_gaeste; d jsonb; v jsonb;
begin
  select * into g from public.umf_gaeste where token = p_token;
  if not found then return false; end if;
  select data into d from public.umf_runden where id = g.runde for update;
  v := public._umf_val(d->'live', p_q, p_val);
  if v is null then return false; end if;
  update public.umf_runden set data = public._umf_put_ans(d, p_q, g.id::text, v), updated_at = now() where id = g.runde;
  return true;
end;
$$;

revoke execute on function public.umf_offen_open(jsonb), public.umf_offen_put(uuid, jsonb, jsonb), public.umf_offen_host(uuid),
  public.umf_offen_close(uuid) from public, anon;
grant execute on function public.umf_offen_open(jsonb), public.umf_offen_put(uuid, jsonb, jsonb), public.umf_offen_host(uuid),
  public.umf_offen_close(uuid) to authenticated;
revoke execute on function public.umf_gast_join(text, text), public.umf_gast(uuid), public.umf_gast_send(uuid, text, jsonb) from public;
grant execute on function public.umf_gast_join(text, text), public.umf_gast(uuid), public.umf_gast_send(uuid, text, jsonb) to anon, authenticated;

-- Version 28: Elterngespräche
--   Pro Klasse eine Zeile: cfg = { title, info, open, slots:[{id,d,t,e}], diff:{Kind-ID:0|1|2}, fixed:{Termin-ID: Kind-ID oder "_"} }
--   answers = { Kind-ID: { name, slots:[Termin-IDs], note, none, key, at } }
--   Eltern kommen nur über den geheimen Link (token) und die Funktionen eltern_get / eltern_set an die Daten.
--   Wie schwierig ein Gespräch ist (diff), sehen die Eltern nie.
-- =====================================================================
create table if not exists public.talks (
  class_id   uuid primary key references public.classes(id) on delete cascade,
  teacher_id uuid not null default auth.uid() references public.profiles(id) on delete cascade,
  token      uuid not null default gen_random_uuid(),
  cfg        jsonb not null default '{}'::jsonb check (octet_length(cfg::text) <= 100000),
  answers    jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);
create unique index if not exists talks_token_key on public.talks (token);
alter table public.talks enable row level security;
drop policy if exists talks_own on public.talks;
create policy talks_own on public.talks for all to authenticated
  using (teacher_id = auth.uid())
  with check (teacher_id = auth.uid() and exists (select 1 from public.classes c where c.id = class_id and c.teacher_id = auth.uid()));
revoke all on public.talks from anon;
grant select, insert, update, delete on public.talks to authenticated;

-- Eltern: Angaben zum Link (Termine, Kinder, was schon belegt ist). Den eigenen Eintrag gibt es nur mit dem Schlüssel des Geräts.
create or replace function public.eltern_get(p_token uuid, p_kid uuid default null, p_key text default null) returns json
language plpgsql stable security definer set search_path = public as $$
declare t public.talks; cname text; tname text; cbild text; fx jsonb; a jsonb; mine jsonb := null;
begin
  select * into t from public.talks where token = p_token;
  if t.class_id is null then return null; end if;
  select c.name, c.bild, p.name into cname, cbild, tname
    from public.classes c left join public.profiles p on p.id = c.teacher_id where c.id = t.class_id;
  if not coalesce((t.cfg->>'open')::boolean, false) then
    return json_build_object('open', false, 'title', t.cfg->>'title', 'class_name', cname, 'teacher', tname, 'bild', cbild);
  end if;
  fx := case when jsonb_typeof(t.cfg->'fixed') = 'object' then t.cfg->'fixed' else '{}'::jsonb end;
  if p_kid is not null and p_key is not null and p_key ~ '^[0-9a-f]{32}$' then
    a := t.answers -> p_kid::text;
    if a is not null and a->>'key' = p_key then
      mine := jsonb_build_object('name', a->'name', 'slots', a->'slots', 'note', a->'note', 'none', a->'none',
        'fixed', (select f.key from jsonb_each_text(fx) f where f.value = p_kid::text limit 1));
    end if;
  end if;
  return json_build_object('open', true, 'title', t.cfg->>'title', 'info', t.cfg->>'info', 'class_name', cname, 'teacher', tname, 'bild', cbild,
    'slots', (select coalesce(jsonb_agg(jsonb_build_object('id', s->>'id', 'd', s->>'d', 't', s->>'t', 'e', s->>'e') order by n), '[]'::jsonb)
                from jsonb_array_elements(case when jsonb_typeof(t.cfg->'slots') = 'array' then t.cfg->'slots' else '[]'::jsonb end) with ordinality as x(s, n)),
    'fixed', (select coalesce(jsonb_agg(f.key), '[]'::jsonb) from jsonb_each_text(fx) f),
    'kids', (select coalesce(json_agg(json_build_object('id', k.id, 'name', k.name,
                'done', (t.answers ? k.id::text) or exists (select 1 from jsonb_each_text(fx) f where f.value = k.id::text))
              order by k.nr nulls last, lower(k.name)), '[]'::json)
               from public.kids k where k.class_id = t.class_id),
    -- Termine der anderen Familien (ohne Namen), damit die Seite ausrechnen kann, welche Zeiten schon gebraucht werden
    'others', (select coalesce(jsonb_agg(x.value->'slots'), '[]'::jsonb) from jsonb_each(t.answers) x
                where x.key is distinct from p_kid::text and jsonb_typeof(x.value->'slots') = 'array'
                  and not coalesce((x.value->>'none')::boolean, false)
                  and not exists (select 1 from jsonb_each_text(fx) f where f.value = x.key)
                  and exists (select 1 from public.kids k where k.id::text = x.key and k.class_id = t.class_id)),
    'mine', mine);
end;
$$;

-- Eltern tragen ihre möglichen Termine ein. Ein Eintrag lässt sich nur mit dem gleichen Schlüssel (gleiches Gerät) ändern.
create or replace function public.eltern_set(p_token uuid, p_kid uuid, p_key text, p_name text, p_slots jsonb, p_note text, p_none boolean) returns json
language plpgsql volatile security definer set search_path = public as $$
declare t public.talks; a jsonb; fx jsonb; sl jsonb; nm text := left(btrim(coalesce(p_name, '')), 80);
begin
  select * into t from public.talks where token = p_token for update;
  if t.class_id is null or not coalesce((t.cfg->>'open')::boolean, false) then
    raise exception 'Die Anmeldung ist geschlossen.' using errcode = 'P0001';
  end if;
  if p_kid is null or not exists (select 1 from public.kids where id = p_kid and class_id = t.class_id) then
    raise exception 'Kind nicht gefunden' using errcode = 'P0001';
  end if;
  if p_key is null or p_key !~ '^[0-9a-f]{32}$' then raise exception 'Ungültig' using errcode = 'P0001'; end if;
  a := t.answers -> p_kid::text;
  fx := case when jsonb_typeof(t.cfg->'fixed') = 'object' then t.cfg->'fixed' else '{}'::jsonb end;
  if (a is not null and a->>'key' is distinct from p_key)
     or (a is null and exists (select 1 from jsonb_each_text(fx) f where f.value = p_kid::text)) then
    raise exception 'Für dieses Kind ist schon ein Termin eingetragen. Bitte melden Sie sich bei der Lehrperson.' using errcode = 'P0001';
  end if;
  if nm = '' then raise exception 'Bitte geben Sie Ihren Namen ein.' using errcode = 'P0001'; end if;
  if jsonb_typeof(p_slots) is distinct from 'array' or jsonb_array_length(p_slots) > 300 then
    raise exception 'Ungültig' using errcode = 'P0001';
  end if;
  -- nur Termine, die es gibt und die nicht schon für eine andere Familie fixiert sind
  select coalesce(jsonb_agg(distinct x.v), '[]'::jsonb) into sl
    from jsonb_array_elements_text(p_slots) as x(v)
   where length(x.v) <= 20
     and exists (select 1 from jsonb_array_elements(case when jsonb_typeof(t.cfg->'slots') = 'array' then t.cfg->'slots' else '[]'::jsonb end) s where s->>'id' = x.v)
     and (fx->>x.v is null or fx->>x.v = p_kid::text);
  if jsonb_array_length(sl) = 0 and not coalesce(p_none, false) then
    raise exception 'Bitte wählen Sie mindestens einen Termin.' using errcode = 'P0001';
  end if;
  update public.talks set answers = jsonb_set(answers, array[p_kid::text], jsonb_build_object(
      'name', nm, 'slots', sl, 'note', left(coalesce(p_note, ''), 500), 'none', coalesce(p_none, false), 'key', p_key, 'at', now()), true),
    updated_at = now()
   where class_id = t.class_id;
  return json_build_object('ok', true, 'slots', sl);
end;
$$;

-- Lehrperson trägt für eine Familie ein oder löscht den Eintrag (p_ans = null). Der Schlüssel der Eltern bleibt erhalten.
create or replace function public.talk_answer_put(p_class uuid, p_kid uuid, p_ans jsonb) returns void
language plpgsql volatile security definer set search_path = public as $$
declare tid uuid; e jsonb; sl jsonb;
begin
  select teacher_id into tid from public.classes where id = p_class;
  if tid is null or tid is distinct from auth.uid() then raise exception 'Nicht erlaubt'; end if;
  if not exists (select 1 from public.kids where id = p_kid and class_id = p_class) then raise exception 'Kind nicht gefunden'; end if;
  insert into public.talks (class_id, teacher_id) values (p_class, tid) on conflict (class_id) do nothing;
  if p_ans is null then
    update public.talks set answers = answers - p_kid::text, updated_at = now() where class_id = p_class;
    return;
  end if;
  if jsonb_typeof(p_ans) <> 'object' or octet_length(p_ans::text) > 8000 then raise exception 'Ungültig'; end if;
  select coalesce(jsonb_agg(distinct x.v), '[]'::jsonb) into sl
    from jsonb_array_elements_text(case when jsonb_typeof(p_ans->'slots') = 'array' then p_ans->'slots' else '[]'::jsonb end) as x(v)
   where length(x.v) <= 20;
  select answers -> p_kid::text into e from public.talks where class_id = p_class for update;
  update public.talks set answers = jsonb_set(answers, array[p_kid::text], jsonb_build_object(
      'name', left(btrim(coalesce(p_ans->>'name', '')), 80), 'slots', sl, 'note', left(coalesce(p_ans->>'note', ''), 500),
      'none', coalesce((p_ans->>'none')::boolean, false), 'key', e->'key', 'at', now(), 'lp', true), true),
    updated_at = now()
   where class_id = p_class;
end;
$$;

revoke execute on function public.eltern_get(uuid, uuid, text), public.eltern_set(uuid, uuid, text, text, jsonb, text, boolean), public.talk_answer_put(uuid, uuid, jsonb) from public;
grant execute on function public.eltern_get(uuid, uuid, text), public.eltern_set(uuid, uuid, text, text, jsonb, text, boolean) to anon, authenticated;
revoke execute on function public.talk_answer_put(uuid, uuid, jsonb) from anon;
grant execute on function public.talk_answer_put(uuid, uuid, jsonb) to authenticated;

-- Fertig.
