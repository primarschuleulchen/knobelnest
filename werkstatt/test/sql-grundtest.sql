\set ON_ERROR_STOP 0
\pset pager off
insert into auth.users (id, email) values ('11111111-1111-1111-1111-111111111111','admin@x.ch');
insert into auth.users (id, email) values ('22222222-2222-2222-2222-222222222222','lehrer@x.ch');
select email, is_admin from profiles order by email;

-- teacher2 tries to become admin
set role authenticated; set request.jwt.claim.sub = '22222222-2222-2222-2222-222222222222';
update profiles set is_admin = true where id = auth.uid();  -- expect permission denied
update profiles set name = 'Herr Muster' where id = auth.uid();
select id, name, is_admin from profiles; -- only own
reset role;

-- admin adds games
set role authenticated; set request.jwt.claim.sub = '11111111-1111-1111-1111-111111111111';
insert into games (id,title,fach,thema,html) values
 ('aaaaaaaa-0000-0000-0000-000000000001','Punktgenau','Mathematik','Raster & Koordinaten','<h1>A</h1>'),
 ('aaaaaaaa-0000-0000-0000-000000000003','Geheim','Mathematik','X','<h1>C</h1>');
insert into games (id,title,fach,thema,html,for_all) values
 ('aaaaaaaa-0000-0000-0000-000000000002','Kleiderschrank','Englisch','Kleider','<h1>B</h1>', true);
select count(*) as admin_sees_profiles from profiles;
reset role;

set role authenticated; set request.jwt.claim.sub = '22222222-2222-2222-2222-222222222222';
select title as t2_sees_before from games order by title;
insert into games (title,fach,html) values ('Hack','X','x'); -- expect RLS error
reset role;

set role authenticated; set request.jwt.claim.sub = '11111111-1111-1111-1111-111111111111';
insert into teacher_games (teacher_id, game_id) values ('22222222-2222-2222-2222-222222222222','aaaaaaaa-0000-0000-0000-000000000001');
reset role;

set role authenticated; set request.jwt.claim.sub = '22222222-2222-2222-2222-222222222222';
select title as t2_sees_after from games order by title;
insert into classes (id, name, code) values ('cccccccc-0000-0000-0000-000000000001','5a','FUCHS 427');
insert into kids (id, class_id, name, pw) values
 ('dddddddd-0000-0000-0000-000000000001','cccccccc-0000-0000-0000-000000000001','Lena','sonne,baum,fisch'),
 ('dddddddd-0000-0000-0000-000000000002','cccccccc-0000-0000-0000-000000000001','Noah','mond,haus,stern');
insert into kids (class_id, name, pw) values ('cccccccc-0000-0000-0000-000000000001','lena','x,y,z'); -- dup expect error
insert into class_games (class_id, game_id) values ('cccccccc-0000-0000-0000-000000000001','aaaaaaaa-0000-0000-0000-000000000001');
insert into class_games (class_id, game_id) values ('cccccccc-0000-0000-0000-000000000001','aaaaaaaa-0000-0000-0000-000000000002');
insert into class_games (class_id, game_id) values ('cccccccc-0000-0000-0000-000000000001','aaaaaaaa-0000-0000-0000-000000000003'); -- expect RLS error
insert into tafel_subjects (id, class_id, name, color, fav) values
 ('eeeeeeee-0000-0000-0000-000000000001','cccccccc-0000-0000-0000-000000000001','Mathematik','#2F5E9E', true),
 ('eeeeeeee-0000-0000-0000-000000000002','cccccccc-0000-0000-0000-000000000001','Deutsch','#8A4F7D', false);
reset role;

set role authenticated; set request.jwt.claim.sub = '11111111-1111-1111-1111-111111111111';
select count(*) as admin_sees_t2_classes from classes;
select count(*) as admin_sees_t2_kids from kids;
reset role;

-- anon / kids
set role anon; reset request.jwt.claim.sub;
select * from kids; -- expect permission denied
select kid_class('fuchs 427');
select kid_class('nope');
select kid_login('FUCHS427','dddddddd-0000-0000-0000-000000000002','x,y,z');
select kid_login('FUCHS427','dddddddd-0000-0000-0000-000000000002','x,y,z');
select kid_login('FUCHS427','dddddddd-0000-0000-0000-000000000002','x,y,z');
select kid_login('FUCHS427','dddddddd-0000-0000-0000-000000000002','x,y,z');
select kid_login('FUCHS427','dddddddd-0000-0000-0000-000000000002','x,y,z');
select kid_login('FUCHS427','dddddddd-0000-0000-0000-000000000002','mond,haus,stern'); -- locked
select kid_login('WOLF111','dddddddd-0000-0000-0000-000000000001','sonne,baum,fisch'); -- wrong code
select (kid_login('fuchs427','dddddddd-0000-0000-0000-000000000001','sonne,baum,fisch')->>'token') as tok \gset
select :'tok' is not null as got_token;
select kid_home(:'tok');
select kid_game(:'tok','aaaaaaaa-0000-0000-0000-000000000001');
select kid_game(:'tok','aaaaaaaa-0000-0000-0000-000000000003'); -- expect error
select kid_report(:'tok','aaaaaaaa-0000-0000-0000-000000000001', 1, 1, null, null);
select kid_report(:'tok','aaaaaaaa-0000-0000-0000-000000000001', 0, 1, 3, 20);
select tafel_get(:'tok');
select tafel_set(:'tok','eeeeeeee-0000-0000-0000-000000000001','frage');
select tafel_set(:'tok','eeeeeeee-0000-0000-0000-000000000002','helfen');
select tafel_teacher('cccccccc-0000-0000-0000-000000000001'); -- anon: expect permission denied
select kid_home('00000000-0000-0000-0000-000000000000'); -- expect error
select _tafel_state('cccccccc-0000-0000-0000-000000000001'); -- expect permission denied
reset role;

set role authenticated; set request.jwt.claim.sub = '22222222-2222-2222-2222-222222222222';
select kid_id, game_id, correct, attempts, done, total, plays from progress;
select tafel_teacher('cccccccc-0000-0000-0000-000000000001');
reset role;
set role authenticated; set request.jwt.claim.sub = '11111111-1111-1111-1111-111111111111';
select tafel_teacher('cccccccc-0000-0000-0000-000000000001'); -- not owner: expect error
reset role;

-- auto clear on new week
update classes set tafel_week = '2000-01';
set role anon;
select tafel_get(:'tok')->'state'->'entries' as after_new_week;
select kid_logout(:'tok');
select kid_home(:'tok'); -- expect error
reset role;
