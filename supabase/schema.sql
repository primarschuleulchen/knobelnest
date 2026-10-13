-- =====================================================================
-- Knobelnest – Datenbank-Einrichtung (Version 1)
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
    'kids', coalesce((select json_agg(json_build_object('id', k.id, 'name', k.name) order by lower(k.name))
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
               'fach', g.fach, 'thema', g.thema,
               'correct', coalesce(p.correct, 0), 'attempts', coalesce(p.attempts, 0),
               'done', p.done, 'total', p.total, 'plays', coalesce(p.plays, 0),
               'last_played', p.last_played)
             order by g.fach, g.thema, g.title)
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

-- Fortschritt melden (vom Spiel)
create or replace function public.kid_report(p_token uuid, p_game uuid,
  p_correct int default 0, p_attempts int default 0, p_done int default null, p_total int default null)
returns void
language plpgsql volatile security definer set search_path = public as $$
declare k public.kids; c int; a int; d int; t int;
begin
  k := public._kid(p_token);
  if not exists (select 1 from public.class_games where class_id = k.class_id and game_id = p_game) then
    raise exception 'Spiel nicht freigegeben' using errcode = 'P0001';
  end if;
  c := least(greatest(coalesce(p_correct, 0), 0), 50);
  a := least(greatest(coalesce(p_attempts, 0), 0), 50);
  t := case when p_total is null then null else least(greatest(p_total, 0), 100000) end;
  d := case when p_done is null then null else least(greatest(p_done, 0), coalesce(t, 100000)) end;
  insert into public.progress (kid_id, game_id, correct, attempts, done, total, last_played)
  values (k.id, p_game, c, a, d, t, now())
  on conflict (kid_id, game_id) do update set
    correct = public.progress.correct + excluded.correct,
    attempts = public.progress.attempts + excluded.attempts,
    done = coalesce(excluded.done, public.progress.done),
    total = coalesce(excluded.total, public.progress.total),
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
    'kids', coalesce((select json_agg(json_build_object('id', k.id, 'name', k.name) order by lower(k.name))
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

-- Wer darf welche Funktion aufrufen
revoke execute on function public._kid(uuid), public._tafel_autoclear(uuid), public._tafel_state(uuid),
  public.handle_new_user() from public, anon, authenticated;
grant execute on function public.kid_class(text), public.kid_login(text, uuid, text),
  public.kid_logout(uuid), public.kid_home(uuid), public.kid_game(uuid, uuid),
  public.kid_report(uuid, uuid, int, int, int, int), public.tafel_get(uuid),
  public.tafel_set(uuid, uuid, text) to anon, authenticated;
revoke execute on function public.tafel_teacher(uuid) from public, anon;
grant execute on function public.tafel_teacher(uuid) to authenticated;

-- Fertig.
