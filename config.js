// ---------------------------------------------------------------
//  Hotel Maroubra — Function Sheet
//  These three values point the page at its database. They are safe
//  to sit in a public repo: on their own they can read and write
//  nothing, because the table only answers a request carrying a
//  signed-in staff session. The staff PASSWORD is never kept here.
// ---------------------------------------------------------------
window.FUNCTION_SHEET_CONFIG = {

  // Supabase → Settings → API
  supabaseUrl: "https://kigaydybfeofcegkiuhn.supabase.co",

  // The publishable key (older projects call it the "anon" key).
  // Never put the service_role / secret key here.
  supabaseKey: "sb_publishable__8tyAtHew3mu8bjKUXKhTQ_2ULIqM4H",

  // The shared staff user created in Supabase → Authentication → Users.
  staffEmail: "Donna@lees.im"

};
