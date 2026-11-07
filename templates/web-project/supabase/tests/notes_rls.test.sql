-- Every notes policy, allow and deny (rls-policies skill). RLS denials return zero rows, so assert counts.
begin;
select plan(8);

insert into auth.users (id, email) values
  ('11111111-1111-1111-1111-111111111111', 'a@example.com'),
  ('22222222-2222-2222-2222-222222222222', 'b@example.com');
insert into public.notes (owner, body) values
  ('11111111-1111-1111-1111-111111111111', 'a note'),
  ('22222222-2222-2222-2222-222222222222', 'b note');

-- As user A.
set local role authenticated;
set local request.jwt.claims = '{"sub":"11111111-1111-1111-1111-111111111111","role":"authenticated"}';

select is((select count(*) from public.notes)::int, 1, 'A sees exactly one note');
select is((select body from public.notes limit 1), 'a note', 'the note A sees is their own');
select lives_ok($$insert into public.notes (body) values ('another a note')$$, 'A can add a note (owner defaults to A)');
select throws_ok(
  $$insert into public.notes (owner, body) values ('22222222-2222-2222-2222-222222222222', 'forged')$$,
  '42501', null, 'A cannot add a note owned by B');
update public.notes set body = 'changed by A' where owner = '22222222-2222-2222-2222-222222222222';
delete from public.notes where owner = '22222222-2222-2222-2222-222222222222';

-- Back as the test runner: B's note must be untouched.
reset role;
select is((select body from public.notes where owner = '22222222-2222-2222-2222-222222222222'), 'b note',
  'A cannot edit B''s note');
select is((select count(*) from public.notes where owner = '22222222-2222-2222-2222-222222222222')::int, 1,
  'A cannot delete B''s note');

-- Anonymous visitors.
set local role anon;
set local request.jwt.claims = '{"role":"anon"}';
select is((select count(*) from public.notes)::int, 0, 'anon sees no notes');
select throws_ok($$insert into public.notes (body) values ('anon note')$$, '42501', null, 'anon cannot add notes');

select * from finish();
rollback;
