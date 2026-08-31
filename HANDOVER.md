# Handover — passing this to a new owner

**The decision, agreed 31 August 2026:** when Alex Frangos leaves, the board
goes to the venue by

1. **transferring this repository** to the new owner's GitHub account,
2. the new owner **creating their own Supabase account** and moving the
   bookings across as a CSV, and
3. the new owner **connecting the repo to their own Claude Code** so changes
   can still be made without a developer.

Written down so neither of us has to remember it a year from now.

---

## What this thing is actually made of

Nothing runs on anybody's computer. There is no server to keep switched on.
There are three pieces, and only the first two need to change hands:

| Piece | What it holds | Where it lives |
|---|---|---|
| **GitHub repo** (`HM-Events`) | The page itself — design, logic, icons | GitHub, free |
| **Supabase project** | Every booking, deposit photo and staff login | Supabase, free tier |
| **The staff password** | Nothing — it's just typed in | Nowhere. Told to people |

The repo is public and contains no secrets. The bookings are **not** in it.

---

## Do this before the last week

- **Register the new accounts to a venue mailbox**, not a personal one —
  something like `manager@…` that outlives whoever holds the job. Otherwise
  this same handover has to happen again when the next person moves on.
- **Take a CSV backup** (step 1 below) and keep a copy off both accounts.

---

## The handover, in order

### 1. Back up the bookings

Supabase → **Table Editor** → `bookings` → **Export** → CSV. Keep that file
safe. Everything else in this list is recoverable; this is the only part that
isn't.

### 2. New owner sets up their Supabase

1. Sign up at supabase.com → **New project**, region **Sydney**.
2. **SQL Editor** → **New query** → paste all of `schema.sql` from this repo →
   **Run**. That builds the table and locks it to signed-in staff.
3. **Authentication** → **Users** → **Add user** → the shared staff email and a
   **new** password, tick **Auto Confirm User**.
4. **Table Editor** → `bookings` → **Import data from CSV** → the file from
   step 1. The bookings are now theirs.
5. **Settings** → **API Keys** → copy the **Project URL** and the
   **publishable key** (older projects call it the *anon* key). Never the
   `service_role` / secret one.

### 3. Transfer the repository

GitHub → repo → **Settings** → **Transfer ownership** → their username.
History and all comes with it.

They then switch the site back on: **Settings** → **Pages** → Deploy from a
branch → **main** → **/ (root)**.

> **The address changes** to `theirusername.github.io/HM-Events/`. Every
> home-screen icon on every staff phone breaks that day, so re-share the new
> link in the group and have people add it again. A custom domain avoids this
> permanently — see the note at the bottom.

### 4. Point the page at the new database

Edit `config.js` — three lines, nothing else:

```js
supabaseUrl: "…"    // Project URL from step 2.5
supabaseKey: "…"    // publishable key from step 2.5
staffEmail: "…"     // the user created in step 2.3
```

Commit it. Pages redeploys in about a minute. Open the site, sign in with the
new password, and check the bookings from the CSV are there.

### 5. New owner connects Claude Code

Sign in at claude.ai (a plan including Claude Code), connect GitHub, add the
`HM-Events` repo, and ask for changes in plain English — new areas, different
size bands, extra fields. It edits the code, pushes it, and Pages republishes
itself. No developer needed for ordinary changes.

### 6. Close the old owner out

- Change the **staff password** — the outgoing person knows the old one.
- Delete the **old Supabase project** once the new one has been running for a
  couple of weeks and the data is confirmed across.
- Remove the outgoing person from the repo if they were left as a collaborator.

---

## Rules that don't change

- **Never put the staff password in this repo.** It lives in Supabase's user
  list and in people's heads. The repo is public.
- **Never put the `service_role` / secret key in this repo.** The publishable
  key in `config.js` is the safe one — on its own it can read and write
  nothing, because the table only answers a signed-in session.
- **Change the staff password whenever someone leaves.** Authentication →
  Users → the staff user → reset password, then tell the team the new one.

## Things that will eventually surprise someone

- **Free Supabase projects pause after seven days of no use.** The board will
  fail to load bookings until someone opens the Supabase dashboard and clicks
  **Restore**. Normal weekly trade never triggers it; a long closure might.
- **Free tier headroom** is 500 MB of database and 5 GB of traffic a month.
  Deposit photos are compressed to roughly 100 KB each, so that is thousands
  of bookings.
- **A custom domain is the fix for the address changing.** Point something
  like `hmbookings.com.au` at whoever is hosting it and the link stays the
  same through every future handover. Setup: four `A` records at the registrar
  (`185.199.108.153`, `.109.153`, `.110.153`, `.111.153`) pointing at `@`, then
  repo → Settings → Pages → Custom domain, then tick **Enforce HTTPS** once the
  certificate has issued (up to 24 hours).
- **Backups are one click**: Table Editor → `bookings` → Export → CSV. Worth
  doing a few times a year regardless of who owns it.

---

Hotel Maroubra — built in-house by Alex Frangos.
