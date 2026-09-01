---
name: project-memory
description: Load and record this project's accumulated memory — the decisions already settled, the bugs already fixed, the rules that must not be broken, and the traps that cost time. Use this at the start of any session that touches index.html, schema.sql or the booking board, and any time you are about to change how something behaves, wonder "why is it built this way?", finish fixing a bug, or hear the user say "we already did that" / "it used to do that". Also use it whenever the user asks about the memory, the map, or what past sessions learned. Consulting it before changing behaviour is what stops a fixed bug being reintroduced as an improvement.
---

# Project memory

A record of what earlier sessions worked out on this project, kept as linked
entries in `.claude/memory/graph.json` rather than as prose.

The point is not that structure is prettier. It is that **a decision is only
safe to revisit if you can see the bug that forced it.** "Lists are
chronological" reads like an arbitrary preference until you can also see that
urgency-sorting once made the board look shuffled to the people using it. Prose
loses that link as it grows; linked entries keep it, and let you load six
relevant entries instead of four hundred lines.

`CLAUDE.md` still holds the short standing orientation — architecture, the
non-negotiable rules, how to test. This holds the long tail, and it grows.

## Reading it

Run from the repo root. No dependencies; stdlib Python only.

```bash
M=.claude/skills/project-memory/scripts/memory.py

python3 $M find dialog mobile     # entries matching any term, plus their neighbours
python3 $M show taken-by-starts-empty
python3 $M list                   # one line each, grouped by type
python3 $M list --type rule
```

`find` is the one to reach for. It prints each match **with the entries linked
to it**, so a decision arrives together with the bug behind it. Search the
vocabulary of the thing you are about to touch — `deposit`, `dialog`, `upload`,
`sorting`, `csp` — not the word "memory".

**Do this before changing how something behaves, not after.** The cost of
missing an entry is reintroducing a bug someone already reported from a live
venue; the cost of running it is two seconds.

## Writing to it

Add an entry when a session produces something a future session would otherwise
have to rediscover:

- **rule** — breaking it causes real damage (a leaked key, an XSS hole)
- **constraint** — a fact about the environment nobody can change
- **decision** — a settled choice; reversing it re-opens a fixed bug
- **bug** — what went wrong and what it taught, once fixed
- **gotcha** — a trap that cost time and will again

Skip the ordinary. A tidy refactor is not memory. What earns an entry is
something *surprising* — a behaviour that looked right and wasn't, a constraint
that isn't visible from the code, a decision someone would otherwise undo in
good faith.

```bash
echo '{
  "id": "short-kebab-id",
  "type": "decision",
  "title": "One line, readable on its own",
  "tags": ["form", "mobile"],
  "what": "What is true now.",
  "why": "Why — the failure it prevents. This is the part worth writing.",
  "caused_by": ["id-of-the-bug"],
  "relates_to": []
}' | python3 $M add
```

`why` is the field that does the work. `what` can be re-read from the code;
`why` cannot, and it is what stops the change being reverted next month.

When a new entry supersedes an old one, list the old id under `supersedes` and
leave the old entry in place — a decision that was reversed once is exactly the
kind of thing worth being able to see.

After adding, refresh the map and validate the links:

```bash
python3 $M check      # ids unique, every link resolves
python3 $M map        # regenerates .claude/memory/map.html
```

Commit `graph.json` and `map.html` together — the map is generated, so a stale
one is worse than none.

## The map

`python3 $M map` renders `.claude/memory/map.html`: entries in columns by type,
arrows running from a cause to what it produced, hover to see the reasoning and
fade everything unrelated.

This is for the **human**, not for you — you read the JSON faster than any
picture. It is how someone who is not going to read a JSON file sees the shape
of their own project: which decisions came from real failures, which rules are
load-bearing, what has accumulated. Offer it when someone asks what has been
learned, or when handing the project on.

## Honest limits

Worth being straight about, because it is easy to imply otherwise:

- This does not make a session start already knowing anything. Every session
  begins with no memory of the last. This file has to be *read*, like any other.
- What it changes is **how much** gets read, and whether the reasoning survives:
  six relevant entries instead of the whole history, each with its cause
  attached.
- Nothing here trains a model or improves it over time. It is a well-organised
  note to whoever comes next, which is usually a fresh session.

Do not describe it to the user as learning, or as memory that persists by
itself. It is a file in their repo that a future session will read if this skill
tells it to.
