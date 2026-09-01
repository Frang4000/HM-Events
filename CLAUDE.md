# Hotel Maroubra — Function Sheet

Event bookings board for a Sydney pub. One static page on GitHub Pages, a
Supabase table behind it, a shared staff password on the front. Used from
phones by a handful of duty managers, mostly one-handed, mid-shift.

**Alex Frangos built this in-house.** The credit line at the foot of the page
says so and should stay.

## Shape of it

- `index.html` — the entire app. No build step, no dependencies, no framework.
  Plain ES5-style JS in one inline `<script>`. Edit it directly.
- `config.js` — Supabase URL, publishable key, staff email. Public on purpose.
- `schema.sql` — the table and its RLS policies. Idempotent; safe to re-run.
- `README.md` — setup, the security model, the SQL for newer columns.
- `HANDOVER.md` — the agreed plan for handing the whole thing to the venue.

Push to `main` and GitHub Pages republishes within a minute. That is the deploy.

## Rules that are not negotiable

**Never commit the staff password or a `service_role` / secret key.** The repo
is public. Only the project URL, the publishable (anon) key and the staff email
belong in `config.js`. Grep before every commit.

**Adding a field that needs a database column? Follow the probe pattern.**
Pushing a column-dependent field breaks every save until someone runs the SQL,
and the push is instant while the SQL is manual. So:

1. Add the column to `schema.sql` — both in `create table` and as its own
   `alter table ... add column if not exists` line.
2. Add its name to `COLUMN_OK` in `index.html`. `probeColumns()` asks the
   database once which columns it knows.
3. Guard the write: `if (COLUMN_OK.your_col) row.your_col = ...`.
4. Grey the control out in `applyColumnAvailability()` with a note pointing at
   the README when the column is missing.
5. Document the SQL under "Adding the newer fields" in the README.

An un-updated database then keeps working normally instead of rejecting writes.

**Escape on output, always.** Everything user-typed goes through `escapeHtml`
when it is drawn. Attachments additionally go through `safeDataUrl` — the board
trusts nothing in the `payments` / `refunds` columns, because anyone with the
staff password can write those straight over the REST API rather than through
the form.

**Touch targets are 40px minimum.** This is used on phones, standing up.

## Testing

There is no test suite in the repo. Tests are built ad hoc against a **local
fake Supabase** (a small Node HTTP server mimicking PostgREST auth + CRUD) plus
a copy of the site served statically, driven with Playwright:

- Chromium is at `/opt/pw-browsers/chromium`; run node with
  `NODE_PATH=/opt/node22/lib/node_modules`.
- Copy the site to a scratch dir and point its `config.js` at the fake server —
  never edit the real `config.js`.
- The CSP blocks the local API, so the test copy needs the local origin added
  to `connect-src`. Keep the shipped policy untested-by-that-copy: verify the
  real policy separately against the untouched file.
- Test at 320/360/390/414px. Regressions worth re-running each time: every
  button, the T&Cs content, horizontal overflow, dialog stability.

**The network here blocks `supabase.com`, `*.supabase.co` and `github.io`.**
The live site and the real database cannot be reached from this environment.
Say so plainly rather than implying live verification.

## Decisions already made — don't quietly reverse them

- **Lists are chronological**, never sorted by an urgency score. Sorting by
  urgency put a deposit chase two weeks out above an event tomorrow and made
  the board look shuffled.
- **Area chips are OR**, not AND. Ticking a second area widens the list.
- **Nothing is ever auto-deleted.** Old events prompt; a human clears them.
- **"Taken by" starts empty every time.** It used to remember the last name on
  that phone, which put the wrong manager on bookings from a shared handset.
- **The booking sheet holds a fixed height** and scrolls inside itself. Letting
  it size to its content made it shrink when fields hid, sliding its top edge
  and the ✕ down the screen mid-tap.
- **Tabs wrap, they don't scroll sideways.** "Past" used to sit off-screen.
- **`novalidate` on the booking form** so the browser's own popup doesn't
  pre-empt the styled inline errors.
- **Restaurant bookings take no deposit** by area; any other booking can have
  one waived with the "No deposit needed" tick. Deposit statuses drop out of
  the Status list when no deposit applies.
- The **T&Cs** all render from one `TERMS` array — dialog and copied text both.
  Edit there and nowhere else.

## Working style that has worked here

Alex is not a programmer and is running this in a live venue. What has worked:

- Fix the thing asked, verify it with a real browser, then say plainly what was
  tested and what was not.
- When a bug is mine, say so directly rather than describing it neutrally.
- Flag the one manual step (a SQL migration, a hard refresh) clearly and early,
  and make the code safe if that step is delayed.
- Screenshots beat descriptions for anything visual.
