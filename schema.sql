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

-- The page reads these as lists. Without the check, a row written straight
-- over the API could put a string here and stop the whole board rendering.
alter table public.bookings drop constraint if exists bookings_payments_is_array;
alter table public.bookings drop constraint if exists bookings_refunds_is_array;
alter table public.bookings add constraint bookings_payments_is_array
  check (payments is null or jsonb_typeof(payments) = 'array') not valid;
alter table public.bookings add constraint bookings_refunds_is_array
  check (refunds  is null or jsonb_typeof(refunds)  = 'array') not valid;

-- ---------------------------------------------------------------
--  WHO IS ALLOWED IN.  Read this before you change it.
--
--  The publishable key in config.js is public — it is in the repo, and
--  it has to be, because the page is served from a public GitHub Pages
--  site. On its own that key can do nothing, because Row Level Security
--  below refuses every request that is not carrying a signed-in token.
--
--  The policies name the ONE staff account. "to authenticated" on its
--  own is not enough: it means anyone holding any signed-in token, and
--  if email sign-up is left switched on in the Supabase dashboard then
--  a stranger with the public key can make themselves an account and
--  read every customer name and phone number on the board.
--
--  So ALSO do this, once, in the dashboard:
--    Authentication -> Sign In / Providers -> turn OFF "Allow new users
--    to sign up", and leave anonymous sign-ins off.
--
--  STAFF_EMAIL below must match the staff user in Authentication ->
--  Users, and the staffEmail in config.js. If it does not match, the
--  board will sign in and then show nothing — that is the symptom.
-- ---------------------------------------------------------------
alter table public.bookings enable row level security;

drop policy if exists "staff read"   on public.bookings;
drop policy if exists "staff insert" on public.bookings;
drop policy if exists "staff update" on public.bookings;
drop policy if exists "staff delete" on public.bookings;

create policy "staff read"   on public.bookings for select to authenticated
  using ((auth.jwt() ->> 'email') = 'frang@mjh.com');
create policy "staff insert" on public.bookings for insert to authenticated
  with check ((auth.jwt() ->> 'email') = 'frang@mjh.com');
create policy "staff update" on public.bookings for update to authenticated
  using ((auth.jwt() ->> 'email') = 'frang@mjh.com')
  with check ((auth.jwt() ->> 'email') = 'frang@mjh.com');
create policy "staff delete" on public.bookings for delete to authenticated
  using ((auth.jwt() ->> 'email') = 'frang@mjh.com');


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
  competition  text,
  channel      text,
  showing      boolean     not null default true,
  screens      text,
  sound_on     boolean     not null default false,
  expected     text        not null default 'Steady',
  notes        text,
  source       text        not null default 'manual',
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now()
);

-- Safe to re-run on an events table made before these were added.
alter table public.events add column if not exists competition text;
alter table public.events add column if not exists channel     text;
alter table public.events add column if not exists screens     text;
alter table public.events add column if not exists sound_on    boolean not null default false;

create index if not exists events_event_date_idx on public.events (event_date);

alter table public.events enable row level security;

drop policy if exists "staff read events"   on public.events;
drop policy if exists "staff insert events" on public.events;
drop policy if exists "staff update events" on public.events;
drop policy if exists "staff delete events" on public.events;

-- Same rule as bookings: the one staff account, not merely "signed in".
create policy "staff read events"   on public.events for select to authenticated
  using ((auth.jwt() ->> 'email') = 'frang@mjh.com');
create policy "staff insert events" on public.events for insert to authenticated
  with check ((auth.jwt() ->> 'email') = 'frang@mjh.com');
create policy "staff update events" on public.events for update to authenticated
  using ((auth.jwt() ->> 'email') = 'frang@mjh.com')
  with check ((auth.jwt() ->> 'email') = 'frang@mjh.com');
create policy "staff delete events" on public.events for delete to authenticated
  using ((auth.jwt() ->> 'email') = 'frang@mjh.com');
