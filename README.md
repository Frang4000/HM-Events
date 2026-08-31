# Hotel Maroubra — Function Sheet

The venue's event bookings board. One page, opened from a link on any phone,
with a shared staff password on the front. Bookings live in a database, so
everyone sees the same sheet the moment it changes.

- Areas: Front Bar · Back Bar · Whole Venue · Restaurant · Beer Garden + Restaurant
- Colour-coded by size, priority flags, and reminders for deposits and old events
- Deposit receipts attach as photos; restaurant bookings skip deposits entirely
- Every booking records who took it

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

Hotel Maroubra — built in-house by Alex Frangos.
