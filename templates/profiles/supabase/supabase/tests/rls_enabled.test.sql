-- Every table in the public schema must have row level security enabled (installed by web-agent-playbook).
-- On failure, the "have" value lists the tables without RLS.
begin;
select plan(1);
select is(
  (select coalesce(string_agg(tablename::text, ', ' order by tablename), '')
     from pg_tables where schemaname = 'public' and not rowsecurity),
  '',
  'every public table has row level security enabled'
);
select * from finish();
rollback;
