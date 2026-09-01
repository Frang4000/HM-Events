---
name: build-crew
description: Split a piece of work on the Function Sheet across specialist agents — builder, designer, security, reviewer, tester — each on the cheapest model that can do its job, and only the ones the task actually needs. Use when a change is big enough to have separable parts (a new feature touching form, storage and layout; a reworked flow; anything needing a fresh adversarial pass before it ships), or when the user asks for the crew, the team, or a thorough job. Do not use it for small edits — read the routing gate below first, because for most changes spawning agents costs more than doing the work directly.
---

# Build crew

Five specialists, each defined in `.claude/agents/` with its own model and
effort level, so a task can be done by the cheapest thing that can actually do
it — a full-effort model where a mistake is expensive, a cheaper one where the
work is mechanical and checkable.

## Read this before spawning anything

**Fan-out usually costs more, not less.** Every agent starts cold: it re-reads
the file, re-derives what you already know, and reports back through a summary.
Three agents on a one-line change can burn several times what the change costs
done directly, and produce a worse result because none of them has the
conversation's context.

So the saving does not come from having five agents. It comes from **not
spawning the ones the task doesn't need**, and from routing what is left to the
right model. A run that spawns two agents is usually a better run than one that
spawns five.

Work through the gate honestly:

| The task | What to do |
|---|---|
| One-line edit, wording, a colour, a placeholder | **No agents.** Do it inline. |
| A contained change in one place you already understand | **No agents.** Do it inline, then run the existing checks. |
| A change with separable parts — logic *and* layout, or logic *and* a schema change | builder, then reviewer and tester in parallel |
| Anything touching auth, keys, uploads, the CSP, RLS, or rendering stored data | add security |
| Visual or interaction work of any size | designer, then tester |
| "Check this over properly", a pre-handover pass, a change you are uneasy about | reviewer, security, tester — no builder, the code already exists |
| A user-reported bug you cannot reproduce by reading | tester first, to reproduce it; then builder |

If you find yourself spawning all five, stop and ask whether the task is really
that broad or you are just being thorough for the look of it.

## The roster

| Agent | Model | Effort | Why that pairing |
|---|---|---|---|
| `builder` | opus | high | The design thinking. A wrong decision here is what the other four spend their time catching. |
| `security` | opus | high | A missed hole is unbounded; a wasted opus call is not. Only spawn when the change actually touches its surface. |
| `reviewer` | opus | high | A reviewer that misses the bug is worth nothing at all, so this is not a place to economise. |
| `designer` | sonnet | medium | Bounded, visual, and immediately checkable in a screenshot. |
| `tester` | sonnet | medium | Fiddly but mechanical, and its output is self-verifying — the checks pass or they don't. |

Change these in the agent's own file, not in the call. Model and effort come
from `.claude/agents/*.md` frontmatter.

## Running them

**Give each agent its context. This is where the tokens actually go.** An agent
that has to grep the repo to find its bearings costs far more than one handed
the file, the line numbers, and the relevant memory:

```bash
python3 .claude/skills/project-memory/scripts/memory.py find <terms>
```

Paste what comes back into the agent's prompt. Six entries with their causes
attached is cheaper than the agent rediscovering one of them the hard way — and
it stops a builder cheerfully reversing a decision that exists because of a bug
a real manager reported.

**Order matters.** `builder` and `designer` produce work; `reviewer`, `security`
and `tester` judge work that already exists. Spawn the producers first, wait,
then spawn the judges — in one block, since they are independent of each other
and parallel is free wall-clock time.

**Tell each agent what to return.** Their reports do not reach the user, only
you. Ask for exactly what you need to act on: the diff and what was uncertain,
or a ranked list of findings, or which checks passed and which failed.

**Keep them in their lane.** The builder does not commit. The reviewer does not
rewrite. Nothing gets pushed except by you, after the checks come back clean —
you are the one accountable for what lands.

## Reporting back

Their findings are invisible to the user until you relay them. When the run is
done, say what changed, what each specialist found — including "nothing", which
is real information — and what is still unproven. If the tester could not check
something because Supabase is unreachable from here, say that rather than
letting silence imply it was verified.

If the run turned up something worth remembering — a trap, a decision, a bug
with a cause worth keeping — add it to the project memory before you finish.
