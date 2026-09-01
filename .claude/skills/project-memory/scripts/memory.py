#!/usr/bin/env python3
"""Project memory: a small store of what past sessions worked out.

Stdlib only, no install step — this repo has no build and shouldn't grow one.

    memory.py find <terms...>    entries matching any term, with their neighbours
    memory.py show <id>...       specific entries in full
    memory.py list [--type T]    one line per entry
    memory.py add                add an entry from JSON on stdin
    memory.py map [out.html]     render the visual map
    memory.py check              validate links and ids
"""
import json, os, sys, html, datetime

# .../.claude/skills/project-memory/scripts/memory.py -> .../.claude
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
STORE = os.path.join(ROOT, 'memory', 'graph.json')

TYPES = {
    # Ordered so causes sit left of what they produced: a bug or a trap on the
    # left, the decision or rule it forced on the right. Arrows then read
    # left-to-right instead of doubling back across the page.
    'bug':        ('Bugs fixed',  '#3457A6', 'What went wrong, and what it taught us.'),
    'gotcha':     ('Gotchas',     '#6B7684', 'Traps that cost time.'),
    'constraint': ('Constraints', '#8A6A1A', 'Facts about the environment that cannot be changed.'),
    'decision':   ('Decisions',   '#256B4C', 'Settled choices — reversing one re-opens a fixed bug.'),
    'rule':       ('Rules',       '#B3261E', 'Breaking this causes real damage.'),
}
LINKS = ('caused_by', 'supersedes', 'relates_to')


def load():
    with open(STORE, encoding='utf-8') as f:
        return json.load(f)


def save(data):
    data['updated'] = datetime.date.today().isoformat()
    with open(STORE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')


def by_id(data):
    return {e['id']: e for e in data['entries']}


def fmt(e, indent=''):
    out = ['%s[%s] %s  (%s)' % (indent, e['type'], e['title'], e['id'])]
    if e.get('what'):
        out.append('%s   what : %s' % (indent, e['what']))
    if e.get('why'):
        out.append('%s   why  : %s' % (indent, e['why']))
    for k in LINKS:
        if e.get(k):
            out.append('%s   %-5s: %s' % (indent, k.split('_')[0], ', '.join(e[k])))
    return '\n'.join(out)


def cmd_find(data, terms):
    idx, hits = by_id(data), []
    for e in data['entries']:
        hay = ' '.join([e['id'], e['title'], e.get('what', ''), e.get('why', ''),
                        ' '.join(e.get('tags', []))]).lower()
        if any(t.lower() in hay for t in terms):
            hits.append(e)
    if not hits:
        print('nothing on that. `memory.py list` shows everything.')
        return
    seen = set()
    for e in hits:
        print(fmt(e)); seen.add(e['id'])
        # neighbours matter: a decision is only safe to revisit if you can see
        # the bug that caused it.
        for k in LINKS:
            for nid in e.get(k, []):
                if nid in idx and nid not in seen:
                    print(fmt(idx[nid], '      -> '))
        print()


def cmd_show(data, ids):
    idx = by_id(data)
    for i in ids:
        print(fmt(idx[i]) if i in idx else 'no entry "%s"' % i); print()


def cmd_list(data, type_filter=None):
    for t in TYPES:
        rows = [e for e in data['entries'] if e['type'] == t
                and (not type_filter or t == type_filter)]
        if not rows:
            continue
        print('\n%s' % TYPES[t][0].upper())
        for e in rows:
            print('  %-34s %s' % (e['id'], e['title']))


def cmd_add(data):
    e = json.load(sys.stdin)
    for f in ('id', 'type', 'title'):
        if f not in e:
            sys.exit('entry needs at least id, type and title')
    if e['type'] not in TYPES:
        sys.exit('type must be one of: %s' % ', '.join(TYPES))
    if e['id'] in by_id(data):
        sys.exit('id "%s" already exists — use a new one, or edit it in place' % e['id'])
    e.setdefault('date', datetime.date.today().isoformat())
    data['entries'].append(e)
    save(data)
    print('added %s' % e['id'])


def cmd_check(data):
    idx, bad = by_id(data), []
    if len(idx) != len(data['entries']):
        bad.append('duplicate ids')
    for e in data['entries']:
        if e['type'] not in TYPES:
            bad.append('%s: unknown type %s' % (e['id'], e['type']))
        for k in LINKS:
            for nid in e.get(k, []):
                if nid not in idx:
                    bad.append('%s: %s -> "%s" does not exist' % (e['id'], k, nid))
    print('\n'.join(bad) if bad else 'ok — %d entries, all links resolve' % len(idx))
    return 1 if bad else 0


def wrap(text, width_px, px_per_char=6.75):
    """Rough word wrap, so a box is tall enough for its own title."""
    per_line = max(8, int(width_px / px_per_char))
    lines, cur = [], ''
    for word in text.split():
        trial = (cur + ' ' + word).strip()
        if len(trial) <= per_line:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines or ['']


def cmd_map(data, out):
    cols = [t for t in TYPES if any(e['type'] == t for e in data['entries'])]
    COL, BOX, GAP, TOP, PAD = 280, 232, 26, 104, 32
    x_of = {t: PAD + i * COL for i, t in enumerate(cols)}

    place, ys, lines_of = {}, {t: TOP for t in cols}, {}
    for e in data['entries']:
        t = e['type']
        lines = wrap(e['title'], BOX - 28)
        lines_of[e['id']] = lines
        h = 18 + 17 * len(lines)
        place[e['id']] = (x_of[t], ys[t], h)
        ys[t] += h + GAP
    H = max(ys.values()) + 46
    SW = PAD * 2 + (len(cols) - 1) * COL + BOX

    edges = []
    for e in data['entries']:
        for k in LINKS:
            for nid in e.get(k, []):
                if nid in place and nid != e['id']:
                    edges.append((nid, e['id'], k))

    def node(e):
        x, y, h = place[e['id']]
        c = TYPES[e['type']][1]
        rows = ''.join(
            '<tspan x="%d" dy="%d">%s</tspan>' % (x + 14, 17 if i else 0, html.escape(ln))
            for i, ln in enumerate(lines_of[e['id']]))
        tip = html.escape(e.get('why') or e.get('what') or e['title'])
        return (
          '<g class="n" data-id="%s" tabindex="0"><title>%s</title>'
          '<rect x="%d" y="%d" width="%d" height="%d" rx="10" fill="%s" fill-opacity=".10" stroke="%s"/>'
          '<text class="lbl" x="%d" y="%d" fill="currentColor">%s</text></g>'
        ) % (html.escape(e['id']), tip, x, y, BOX, h, c, c, x + 14, y + 25, rows)

    def edge(a, b, kind):
        (x1, y1, h1), (x2, y2, h2) = place[a], place[b]
        ya, yb = y1 + h1 / 2, y2 + h2 / 2
        dash = ' stroke-dasharray="5 4"' if kind == 'relates_to' else ''
        if x2 > x1:                                   # forward: cause -> effect
            sx, ex = x1 + BOX, x2
            c1, c2 = sx + (ex - sx) * 0.5, ex - (ex - sx) * 0.5
            d = 'M%d %.1f C %.1f %.1f, %.1f %.1f, %d %.1f' % (sx, ya, c1, ya, c2, yb, ex, yb)
        else:                                         # same column or backwards:
            sx, ex = x1, x2                           # loop out to the left
            bulge = 46 + abs(ya - yb) * 0.16
            d = 'M%d %.1f C %.1f %.1f, %.1f %.1f, %d %.1f' % (
                sx, ya, sx - bulge, ya, ex - bulge, yb, ex, yb)
        return ('<path d="%s" fill="none" stroke="currentColor" stroke-opacity=".32"%s '
                'marker-end="url(#a)" data-a="%s" data-b="%s"/>') % (
                d, dash, html.escape(a), html.escape(b))

    heads = ''.join(
        '<text x="%d" y="66" class="h" fill="%s">%s</text>' % (x_of[t], TYPES[t][1], TYPES[t][0].upper())
        for t in cols)

    doc = """<!doctype html><meta charset="utf-8">
<title>Function Sheet — project memory</title>
<style>
 :root{ --bg:#F7F4EA; --ink:#17241A; --soft:#55624F; }
 @media (prefers-color-scheme:dark){
   :root{ --bg:#12160F; --ink:#EDE9DA; --soft:#A3AC9B; } }
 body{margin:0;background:var(--bg);color:var(--ink);
      font:14px/1.5 'Work Sans',system-ui,-apple-system,'Segoe UI',sans-serif;}
 header{padding:22px 26px 10px;} h1{font-size:19px;margin:0 0 5px;letter-spacing:.01em;}
 p.sub{margin:0;color:var(--soft);font-size:13px;max-width:72ch;}
 .wrap{overflow-x:auto;padding:0 8px 26px;}
 svg{display:block;color:var(--ink);}
 .h{font:600 11px 'Work Sans',system-ui,sans-serif;letter-spacing:.14em;}
 .lbl{font:600 12.5px 'Work Sans',system-ui,sans-serif;}
 .n{cursor:default;} .n:hover rect,.n:focus rect{fill-opacity:.26;}
 .n.dim{opacity:.16;} path.dim{opacity:.04;}
 footer{padding:0 26px 34px;color:var(--soft);font-size:12px;}
 code{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:12px;}
</style>
<header>
  <h1>Function Sheet — project memory</h1>
  <p class="sub">%d things past sessions worked out, and how they connect. Arrows run
  left to right, from a cause to what it produced — a bug or a trap, then the decision
  or rule it forced. Dashed means loosely related. Hover any box to read the reasoning
  and fade everything unconnected to it.</p>
</header>
<div class="wrap">
<svg viewBox="0 0 %d %d" width="%d" height="%d" xmlns="http://www.w3.org/2000/svg">
 <defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5"
   orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="currentColor" fill-opacity=".5"/>
 </marker></defs>
 %s
 <g id="edges">%s</g>
 <g id="nodes">%s</g>
</svg>
</div>
<footer>Generated from <code>.claude/memory/graph.json</code> — edit that, then re-run
<code>python3 .claude/skills/project-memory/scripts/memory.py map</code>.</footer>
<script>
 const nodes=[...document.querySelectorAll('.n')], paths=[...document.querySelectorAll('#edges path')];
 function focus(id){
   if(!id){ nodes.forEach(n=>n.classList.remove('dim')); paths.forEach(p=>p.classList.remove('dim')); return; }
   const keep=new Set([id]);
   paths.forEach(p=>{ if(p.dataset.a===id||p.dataset.b===id){ keep.add(p.dataset.a); keep.add(p.dataset.b); } });
   nodes.forEach(n=>n.classList.toggle('dim',!keep.has(n.dataset.id)));
   paths.forEach(p=>p.classList.toggle('dim',!(keep.has(p.dataset.a)&&keep.has(p.dataset.b))));
 }
 nodes.forEach(n=>{
   n.addEventListener('mouseenter',()=>focus(n.dataset.id));
   n.addEventListener('focus',()=>focus(n.dataset.id));
   n.addEventListener('mouseleave',()=>focus(null));
   n.addEventListener('blur',()=>focus(null));
 });
</script>
""" % (len(data['entries']), SW, H, SW, H, heads,
       ''.join(edge(*e) for e in edges),
       ''.join(node(e) for e in data['entries']))
    with open(out, 'w', encoding='utf-8') as f:
        f.write(doc)
    print('map -> %s  (%d entries, %d links)' % (out, len(data['entries']), len(edges)))


def main():
    if len(sys.argv) < 2:
        print(__doc__); return 0
    cmd, args, data = sys.argv[1], sys.argv[2:], load()
    if cmd == 'find':  cmd_find(data, args or sys.exit('find what?'))
    elif cmd == 'show': cmd_show(data, args)
    elif cmd == 'list': cmd_list(data, args[1] if len(args) > 1 and args[0] == '--type' else None)
    elif cmd == 'add':  cmd_add(data)
    elif cmd == 'check': return cmd_check(data)
    elif cmd == 'map':  cmd_map(data, args[0] if args else os.path.join(ROOT, 'memory', 'map.html'))
    else: print(__doc__)
    return 0


if __name__ == '__main__':
    sys.exit(main())
