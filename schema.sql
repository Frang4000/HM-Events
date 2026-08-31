-- Hotel Maroubra — Function Sheet
-- Paste this whole file into Supabase → SQL Editor → New query → Run.
-- It creates the bookings table and locks it to signed-in staff only.

create table if not exists public.bookings (
  id             text primary key,
  event_date     date        not null,
  event_time     text,
  area           text        not null,
  pax            integer     not null,
  organiser      text,
  contact        text,
  taken_by       text        not null default '',
  priority       text        not null default 'Medium',
  status         text        not null default 'Enquiry',
  deposit_amount text,
  notes          text,
  has_dj         boolean     not null default false,
  has_stage      boolean     not null default false,
  payments       jsonb       not null default '[]'::jsonb,
  refunds        jsonb       not null default '[]'::jsonb,
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now()
);

-- Sorting and the "next 7 days" counts read this constantly.
create index if not exists bookings_event_date_idx on public.bookings (event_date);

-- Row Level Security: with this on, the publishable key in config.js can
-- do nothing on its own. Only a request carrying a signed-in staff token
-- gets through, which is what the password box on the front produces.
alter table public.bookings enable row level security;

drop policy if exists "staff read"   on public.bookings;
drop policy if exists "staff insert" on public.bookings;
drop policy if exists "staff update" on public.bookings;
drop policy if exists "staff delete" on public.bookings;

create policy "staff read"   on public.bookings for select to authenticated using (true);
create policy "staff insert" on public.bookings for insert to authenticated with check (true);
create policy "staff update" on public.bookings for update to authenticated using (true) with check (true);
create policy "staff delete" on public.bookings for delete to authenticated using (true);
