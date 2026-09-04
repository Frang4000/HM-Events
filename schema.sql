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
  no_deposit     boolean     not null default false,
  table_pref     text,
  payments       jsonb       not null default '[]'::jsonb,
  refunds        jsonb       not null default '[]'::jsonb,
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now()
);

-- Safe to re-run on a database made before these fields existed: each line
-- adds its column if it is missing and leaves everything else alone.
alter table public.bookings add column if not exists no_deposit boolean not null default false;
alter table public.bookings add column if not exists table_pref text;

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


-- ---------------------------------------------------------------
--  Upcoming events — what is on in Sydney that fills the venue.
--  Separate from bookings: nobody books these, we just need to know
--  they are coming. Safe to run on its own if the bookings table
--  already exists.
-- ---------------------------------------------------------------
create table if not exists public.events (
  id           text primary key,
  event_date   date        not null,
  event_time   text,
  title        text        not null,
  kind         text        not null default 'Sport',
  sport        text,
  showing      boolean     not null default true,
  expected     text        not null default 'Steady',
  notes        text,
  source       text        not null default 'manual',
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now()
);

create index if not exists events_event_date_idx on public.events (event_date);

alter table public.events enable row level security;

drop policy if exists "staff read events"   on public.events;
drop policy if exists "staff insert events" on public.events;
drop policy if exists "staff update events" on public.events;
drop policy if exists "staff delete events" on public.events;

create policy "staff read events"   on public.events for select to authenticated using (true);
create policy "staff insert events" on public.events for insert to authenticated with check (true);
create policy "staff update events" on public.events for update to authenticated using (true) with check (true);
create policy "staff delete events" on public.events for delete to authenticated using (true);
