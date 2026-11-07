-- Notes owned by one user. RLS: owners can do everything with their own notes; nobody else sees them.
-- down: drop table public.notes;

create table public.notes (
  id uuid primary key default gen_random_uuid(),
  owner uuid not null default auth.uid() references auth.users (id) on delete cascade,
  body text not null check (char_length(body) between 1 and 2000),
  created_at timestamptz not null default now()
);

create index notes_owner_idx on public.notes (owner);

alter table public.notes enable row level security;

create policy "owners can read their notes" on public.notes
  for select to authenticated using ((select auth.uid()) = owner);

create policy "owners can add notes" on public.notes
  for insert to authenticated with check ((select auth.uid()) = owner);

create policy "owners can edit their notes" on public.notes
  for update to authenticated using ((select auth.uid()) = owner) with check ((select auth.uid()) = owner);

create policy "owners can delete their notes" on public.notes
  for delete to authenticated using ((select auth.uid()) = owner);
