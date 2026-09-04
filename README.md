# Hotel Maroubra — Function Sheet

The venue's event bookings board. One page, opened from a link on any phone,
with a shared staff password on the front. Bookings live in a database, so
everyone sees the same sheet the moment it changes.

- Areas: Front Bar · Back Bar · Whole Venue · Restaurant · Beer Garden + Restaurant
- Colour-coded by size, priority flags, and reminders for deposits and old events
- Deposit receipts attach as photos; restaurant bookings skip deposits entirely,
  and any booking can have the deposit waived with a tick
- Every booking records who took it
- A second board, **Upcoming events**, tracks what's on in Sydney — NRL, AFL,
  football, basketball, trivia nights — with the expected crowd and whether
  it's going on the screens

---

## Setting it up (about 20 minutes, once)

You need a free Supabase account. Nothing else, and no card.

### 1. Make the database

1. Go to **supabase.com**, sign up, and click **New project**.
2. Name it `hotel-maroubra`, pick a strong database password (you won't need it
   again — save it somewhere anyway), choose the **Sydney** region, and create it.
   It takes a couple of minutes to finish setting up.

### 2. Create the bookings table

1. In your project, open **SQL Editor** in the left sidebar → **New query**.
2. Open `schema.sql` from this repository, copy all of it, paste it in, press **Run**.
3. It should say success. That's the table made and locked down.

### 3. Make the one staff login

1. Left sidebar → **Authentication** → **Users** → **Add user** → **Create new user**.
2. Email: `staff@hotelmaroubra.com.au` (it never receives mail — it's just a name).
3. Password: **this is the password the whole team will type.** Pick something
   sayable that you're happy to give every staff member.
4. Tick **Auto Confirm User**, then create.

### 4. Point the page at it

1. Left sidebar → **Settings** → **API Keys**.
2. Copy the **Project URL** and the **publishable key** (older projects label
   this the **anon** key — either is right; do *not* use the `service_role` or
   `secret` key, ever).
3. Edit `config.js` in this repository and paste them in, plus the staff email
   from step 3. Commit the change.

### 5. Turn on the website

1. In this repository: **Settings** → **Pages**.
2. Under **Build and deployment**, set Source to **Deploy from a branch**,
   branch **main**, folder **/ (root)**. Save.
3. Wait a minute, then reload — GitHub shows the live address, something like
   `https://frang4000.github.io/hotel-maroubra-bookings/`.

### 6. Give it to the team

Post the address in the staff WhatsApp group with the password. On a phone:
**Share → Add to Home Screen** puts it on the home screen like a normal app.

---

## Adding the newer fields

**Only needed on a database made before these features existed.** If the
“No deposit needed” tick or the “Table preference” box on the booking form is
greyed out, the database is missing a column or two. Add them once:

1. Supabase → **SQL Editor** → **New query**.
2. Paste this and press **Run**:

   ```sql
   alter table public.bookings
     add column if not exists no_deposit boolean not null default false;
   alter table public.bookings
     add column if not exists table_pref text;
   ```

3. Reload the board. Both are live.

**The Upcoming events board needs its own table.** If it says the table is
missing, paste the whole `events` section from the bottom of `schema.sql` into
the SQL Editor and run it — it creates the table and locks it down the same way
the bookings one is.

Until you do, everything else keeps working normally — the board just won't let
anyone use those fields, and bookings are unaffected. (Running the whole of
`schema.sql` again does all of it and is equally safe.)

---

## Security

**The key in `config.js` is meant to be public.** Supabase calls it the
publishable (or "anon") key, and it is designed to be shipped to a browser.
Anyone can press Inspect and read it — that is expected, and on its own it can
read and write nothing. What stops it is Row Level Security in `schema.sql`:
the `bookings` table only answers a request carrying a signed-in staff token,
which only the password box on the front produces. The key without the
password is a doorknob with no door behind it.

The key that must **never** go in this repo is the `service_role` / secret one.
That one does bypass RLS.

**What actually protects the data is the one shared password.** It is the whole
lock. So:

- Change it whenever someone leaves — Supabase → Authentication → Users → the
  staff user → reset password. Everyone re-enters it once.
- Don't post it anywhere it outlives the person: a pinned WhatsApp message
  stays readable to anyone still in the group.
- Anyone with the link and the password can see every customer name, phone
  number and deposit receipt, and can delete bookings.

**What the page itself does:**

- A Content Security Policy in the page head. If anything ever did smuggle
  markup into the board, this stops it loading outside scripts or sending
  anything to a server that isn't Supabase — so a stolen session can't be
  quietly shipped somewhere.
- Attachments are checked, not trusted. Nothing reaches the page unless it
  still looks exactly like a photo or PDF this board produced, so a row edited
  outside the app can't plant something that runs on everyone else's phone.
  A PDF is verified by its actual first bytes, not by its name.
- Everything typed into a booking is escaped when it is drawn, so a name or
  note containing HTML shows as text.

**What it deliberately doesn't do**, and why:

- *Clickjacking protection* (`frame-ancestors` / `X-Frame-Options`) needs a real
  HTTP header. GitHub Pages doesn't let us send headers, so it can't be set
  from a static page.
- *Account lockout after failed logins* would let anyone lock the whole team
  out, since there is only one shared account. Supabase already rate-limits
  sign-in attempts, which is the safer trade here.
- *CSRF tokens* aren't needed. The session is a token sent in a header, not a
  cookie, so another site can't make the browser send it along.

**A phone stays signed in until someone taps "Sign out of this phone."** If a
phone is lost, change the password — that is what cuts every device off.

**The data is personal information.** Customer names, phone numbers and payment
records belong to those customers. Keep exports off personal devices, and delete
old bookings you no longer need.

---

## Things worth knowing

**The password is the only lock.** Anyone with the link and the password can see
customer names, phone numbers and deposit receipts. Change it when someone
leaves: Supabase → Authentication → Users → the staff user → reset password.
Everyone then re-enters the new one.

**Free projects pause after a week of no use.** If the board goes untouched for
seven days straight, Supabase pauses the database and the page will fail to load
bookings until someone opens the Supabase dashboard and hits **Restore**. In
normal weekly use this never triggers.

**Free tier headroom:** 500 MB of database and 5 GB of traffic a month. Deposit
photos are compressed to roughly 100 KB each before they're stored, so this is
thousands of bookings' worth.

**Backups.** Supabase → Table Editor → `bookings` → Export as CSV, any time.
The data is yours and leaves in a spreadsheet.

**Editing the page.** Everything is in `index.html` — no build step, no
dependencies. Commit a change and GitHub Pages republishes within a minute.

---

## Handing it over

If this needs to move to a new owner — someone leaving, or the venue taking it
in-house — the whole sequence is written down in **HANDOVER.md**: transferring
the repository, setting up a fresh Supabase account and carrying the bookings
across, and connecting it to a new Claude Code account.

---

Hotel Maroubra — built in-house by Alex Frangos.
