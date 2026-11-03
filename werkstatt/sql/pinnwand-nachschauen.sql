-- Klassen-Pinnwand: nachschauen (liest nur, ändert nichts)
-- In Supabase: SQL Editor → New query → einfügen → Run

-- 1) Alle Pinnwände mit allen Zetteln (auch wartende), z. B. «Klassenmaskottchen»
select b.value->>'title'  as pinnwand,
       i.value->>'text'   as zettel,
       i.value->>'status' as status,
       i.value->>'by'     as von,
       to_timestamp((i.value->>'at')::bigint / 1000) as erstellt
  from public.teacher_store t
  cross join lateral jsonb_each(coalesce(t.data->'boards', '{}'::jsonb)) b
  join lateral jsonb_each(coalesce(t.data->'ideas', '{}'::jsonb)) i on i.value->>'boardId' = b.key
 where t.doc like 'pin-%'
 order by 1, 5;

-- 2) Zettel ohne Pinnwand (z. B. wenn eine Pinnwand gelöscht wurde, die Zettel aber noch da sind)
select i.value->>'text' as zettel, i.value->>'status' as status, i.value->>'by' as von, i.value->>'boardId' as pinnwand_id
  from public.teacher_store t
  cross join lateral jsonb_each(coalesce(t.data->'ideas', '{}'::jsonb)) i
 where t.doc like 'pin-%'
   and not coalesce(t.data->'boards', '{}'::jsonb) ? coalesce(i.value->>'boardId', '');

-- 3) Kommentare der Kinder zu Zetteln, die es nicht mehr gibt (darin stehen manchmal die Namen)
select k.name as kind, v.key as zettel_id, v.value->>'comment' as kommentar, v.value->>'rate' as bewertung
  from public.teacher_store t
  cross join lateral jsonb_each(coalesce(t.data->'votes', '{}'::jsonb)) s
  cross join lateral jsonb_each(coalesce(s.value->'r', '{}'::jsonb)) v
  left join public.kids k on k.id::text = s.key
 where t.doc like 'pin-%'
   and not coalesce(t.data->'ideas', '{}'::jsonb) ? v.key
 order by 2, 1;
