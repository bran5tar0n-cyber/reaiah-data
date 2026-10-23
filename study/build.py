"""Build Reaiah's study data (cross-references, dictionaries, topics, Matthew Henry,
church fathers, creeds, people and places) from free sources.

Every output keys verses with STEP book codes (Gen, Exo, ... Rev) like wordstudy/.
A reference is [book, chapter, verse] or [book, chapter, verse, end_verse]
(end_verse in the same chapter), or [book, chapter, verse, end_chapter, end_verse].

Usage: python3 -I study/build.py <src_dir>
  src_dir holds clones of: gnosis, theographic-bible-metadata, bible-dictionary-dataset,
  creeds.json, commentaries-database, open-commentaries
"""
import json, os, re, sys, glob, struct, zlib, tomllib, html, hashlib, collections

SRC = sys.argv[1]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(OUT)

CODES = ("Gen Exo Lev Num Deu Jos Jdg Rut 1Sa 2Sa 1Ki 2Ki 1Ch 2Ch Ezr Neh Est Job Psa Pro Ecc Sng "
         "Isa Jer Lam Ezk Dan Hos Jol Amo Oba Jon Mic Nam Hab Zep Hag Zec Mal Mat Mrk Luk Jhn Act Rom "
         "1Co 2Co Gal Eph Php Col 1Th 2Th 1Ti 2Ti Tit Phm Heb Jas 1Pe 2Pe 1Jn 2Jn 3Jn Jud Rev").split()
KJV = json.load(open(os.path.join(ROOT, 'kjv/KJV.json')))
assert len(KJV['books']) == 66
KJV_NAMES = [b['name'] for b in KJV['books']]
VCOUNT = {}  # (code, ch) -> verses
for code, b in zip(CODES, KJV['books']):
    for c in b['chapters']:
        VCOUNT[(code, c['chapter'])] = len(c['verses'])

FULL = ["Genesis","Exodus","Leviticus","Numbers","Deuteronomy","Joshua","Judges","Ruth","1 Samuel","2 Samuel",
        "1 Kings","2 Kings","1 Chronicles","2 Chronicles","Ezra","Nehemiah","Esther","Job","Psalms","Proverbs",
        "Ecclesiastes","Song of Solomon","Isaiah","Jeremiah","Lamentations","Ezekiel","Daniel","Hosea","Joel","Amos",
        "Obadiah","Jonah","Micah","Nahum","Habakkuk","Zephaniah","Haggai","Zechariah","Malachi","Matthew","Mark",
        "Luke","John","Acts","Romans","1 Corinthians","2 Corinthians","Galatians","Ephesians","Philippians",
        "Colossians","1 Thessalonians","2 Thessalonians","1 Timothy","2 Timothy","Titus","Philemon","Hebrews",
        "James","1 Peter","2 Peter","1 John","2 John","3 John","Jude","Revelation"]
assert len(FULL) == 66, len(FULL)

OSIS = ("Gen Exod Lev Num Deut Josh Judg Ruth 1Sam 2Sam 1Kgs 2Kgs 1Chr 2Chr Ezra Neh Esth Job Ps Prov Eccl Song "
        "Isa Jer Lam Ezek Dan Hos Joel Amos Obad Jonah Mic Nah Hab Zeph Hag Zech Mal Matt Mark Luke John Acts Rom "
        "1Cor 2Cor Gal Eph Phil Col 1Thess 2Thess 1Tim 2Tim Titus Phlm Heb Jas 1Pet 2Pet 1John 2John 3John Jude Rev").split()

NAME = {}
def add(n, code):
    NAME[re.sub(r'[\s.]', '', n).lower()] = code
for i, code in enumerate(CODES):
    for n in (code, FULL[i], OSIS[i], KJV_NAMES[i]):
        add(n, code)
for n, c in [("Psalm", "Psa"), ("Song of Songs", "Sng"), ("Canticles", "Sng"), ("Revelation of John", "Rev"),
             ("Ezek", "Ezk"), ("Jn", "Jhn"), ("Mt", "Mat"), ("Mk", "Mrk"), ("Lk", "Luk"), ("Phil", "Php"),
             ("Philem", "Phm"), ("Jas", "Jas"), ("Judg", "Jdg"), ("Eccles", "Ecc"), ("Qoh", "Ecc")]:
    add(n, c)
for i, code in enumerate(CODES):  # roman numeral prefixes
    m = re.match(r'([123]) (.*)', FULL[i])
    if m:
        add({'1': 'I', '2': 'II', '3': 'III'}[m.group(1)] + ' ' + m.group(2), code)
        add({'1': 'First', '2': 'Second', '3': 'Third'}[m.group(1)] + ' ' + m.group(2), code)

def code_of(name):
    return NAME.get(re.sub(r'[\s.]', '', name).lower())

def valid(code, ch, v):
    return VCOUNT.get((code, ch), 0) >= v >= 1

REF_RE = re.compile(r'^\s*((?:[123]|I{1,3})?\s*[A-Za-z][A-Za-z .]*?)\s*(\d+)(?::(\d+))?(?:\s*[-–]\s*(\d+)(?::(\d+))?)?\s*$')
def parse_ref(s):
    """'John 3:16', 'Prov 8:22-30', 'Gen 1:1-2:3' -> ref list or None."""
    m = REF_RE.match(s)
    if not m:
        return None
    code = code_of(m.group(1))
    if not code:
        return None
    ch = int(m.group(2))
    if m.group(3) is None:  # whole chapter
        if (code, ch) not in VCOUNT:
            return None
        return [code, ch, 1, VCOUNT[(code, ch)]]
    v = int(m.group(3))
    if not valid(code, ch, v):
        return None
    if m.group(4) is None:
        return [code, ch, v]
    if m.group(5) is not None:  # chapter:verse end
        ech, ev = int(m.group(4)), int(m.group(5))
        if ech == ch:
            return [code, ch, v, ev] if valid(code, ch, ev) and ev > v else [code, ch, v]
        return [code, ch, v, ech, ev] if valid(code, ech, ev) and ech > ch else [code, ch, v]
    ev = int(m.group(4))
    return [code, ch, v, ev] if valid(code, ch, ev) and ev > v else [code, ch, v]

def osis_ref(s):
    """'Prov.8.22-Prov.8.30' -> ref."""
    parts = s.split('-')
    def one(p):
        b, c, v = p.split('.')
        return code_of(b), int(c), int(v)
    b, c, v = one(parts[0])
    if not b or not valid(b, c, v):
        return None
    if len(parts) == 1:
        return [b, c, v]
    b2, c2, v2 = one(parts[1])
    if b2 != b or not valid(b2, c2, v2):
        return [b, c, v]
    if c2 == c:
        return [b, c, v, v2] if v2 > v else [b, c, v]
    return [b, c, v, c2, v2] if c2 > c else [b, c, v]

def write(rel, data):
    p = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

def per_book(rel_dir, by_verse):
    """by_verse: {(code, ch, v): value} -> rel_dir/<Code>.json {"ch:v": value}."""
    books = collections.defaultdict(dict)
    for (code, ch, v), val in by_verse.items():
        books[code][f'{ch}:{v}'] = val
    for code, d in books.items():
        d = dict(sorted(d.items(), key=lambda kv: tuple(int(x) for x in kv[0].split(':'))))
        write(f'{rel_dir}/{code}.json', d)
    return sum(len(d) for d in books.values())

STATS = {}

# ---------------------------------------------------------------- cross-references
def crossrefs():
    by = collections.defaultdict(list)
    f = os.path.join(SRC, 'gnosis/sources/scrollmapper/cross_references.txt')
    kept = dropped = 0
    for line in open(f, encoding='utf-8'):
        if line.startswith('From Verse'):
            continue
        a, b, votes = line.rstrip('\n').split('\t')
        votes = int(votes)
        src, dst = osis_ref(a), osis_ref(b)
        if not src or not dst or votes < 1:
            dropped += 1
            continue
        by[tuple(src[:3])].append((votes, dst))
        kept += 1
    out = {}
    for k, lst in by.items():
        lst.sort(key=lambda x: -x[0])
        out[k] = [dst + [] for votes, dst in lst[:20]]  # top 20 by votes
    n = per_book('crossrefs', out)
    STATS['crossrefs'] = {'verses_with_refs': n, 'pairs_read': kept, 'pairs_dropped_invalid_or_no_votes': dropped,
                          'max_per_verse': 20}

# ---------------------------------------------------------------- dictionaries
LINK_RE = re.compile(r'\[([^\]]+)\]\([^)]*\)')
def clean(t):
    t = html.unescape(t)
    t = LINK_RE.sub(r'\1', t)
    t = re.sub(r'<[^>]+>', '', t)
    t = re.sub(r'[ \t]+', ' ', t)
    t = re.sub(r'\s*\n\s*', '\n', t)
    return t.strip()

def dictionaries():
    for name, label in (('easton', "Easton's Bible Dictionary (1897)"), ('smith', "Smith's Bible Dictionary (1863)")):
        entries = {}
        for f in sorted(glob.glob(os.path.join(SRC, f'bible-dictionary-dataset/data/02_sources/{name}/*.json'))):
            if os.path.basename(f).startswith('_'):
                continue
            for key, e in json.load(open(f, encoding='utf-8')).items():
                text = '\n'.join(clean(d['text']) for d in e.get('definitions', []) if d.get('text'))
                if not text:
                    continue
                refs = []
                for r in e.get('scripture_refs', []):
                    pr = parse_ref(r.get('reference', ''))
                    if pr and pr not in refs:
                        refs.append(pr)
                entries[e['name']] = {'t': text, 'r': refs}
        write(f'dictionary/{name}.json', {'title': label, 'entries': dict(sorted(entries.items(), key=lambda kv: kv[0].lower()))})
        STATS[f'dictionary_{name}'] = len(entries)

# ---------------------------------------------------------------- topics (Nave's)
def topics():
    out = {}
    for f in glob.glob(os.path.join(SRC, 'gnosis/sources/topics/*/*.json')):
        t = json.load(open(f, encoding='utf-8'))
        aspects = []
        for a in t.get('aspects', []):
            if a.get('source') != 'NAV':
                continue
            refs = []
            for r in a.get('references', []):
                pr = parse_ref(r)
                if pr and pr not in refs:
                    refs.append(pr)
            if refs:
                aspects.append({'l': clean(a.get('label', '')), 'r': refs})
        if aspects:
            out[t['topic'].title()] = {'see': [s.title() for s in t.get('see_also', [])], 'a': aspects}
    write('topics/naves.json', {'title': "Nave's Topical Bible (1896)", 'topics': dict(sorted(out.items()))})
    STATS['topics_naves'] = len(out)

# ---------------------------------------------------------------- Matthew Henry Concise (SWORD zCom)
def mhcc():
    mod = os.path.join(SRC, 'open-commentaries/sources/mhcc/modules/comments/zcom/mhcc')
    out = {}
    for prefix, rng in (('ot', range(0, 39)), ('nt', range(39, 66))):
        bzs = open(f'{mod}/{prefix}.bzs', 'rb').read()
        bzv = open(f'{mod}/{prefix}.bzv', 'rb').read()
        bzz = open(f'{mod}/{prefix}.bzz', 'rb').read()
        blocks = [struct.unpack('<III', bzs[i:i + 12]) for i in range(0, len(bzs), 12)]
        idx = [struct.unpack('<IIH', bzv[i:i + 10]) for i in range(0, len(bzv), 10)]
        cache = {}
        def text(e):
            b, s, l = e
            if l == 0:
                return ''
            if b not in cache:
                off, size, _ = blocks[b]
                cache[b] = zlib.decompress(bzz[off:off + size])
            return cache[b][s:s + l].decode('utf-8', 'replace')
        i = 2
        for bi in rng:
            code = CODES[bi]
            i += 1
            for c in KJV['books'][bi]['chapters']:
                i += 1
                prev_key, start = None, None
                for v in c['verses']:
                    e = idx[i]; i += 1
                    if e[2] == 0:
                        continue
                    if e == prev_key:  # linked verse: extend the section
                        out[(code, c['chapter'], start)]['to'] = v['verse']
                        continue
                    prev_key, start = e, v['verse']
                    out[(code, c['chapter'], v['verse'])] = {'to': v['verse'], 'raw': text(e)}
        assert i == len(idx), (prefix, i, len(idx))
    final = {}
    for k, d in out.items():
        t = d['raw']
        t = re.sub(r'<title[^>]*>.*?</title>', '', t)
        t = re.sub(r'<div[^>]*type="x-p"[^>]*/>', '\n', t)
        t = re.sub(r'<(lb|br)[^>]*/>', '\n', t)
        t = re.sub(r'</?(row|cell|table)[^>]*>', '\n', t)
        t = clean(t)
        t = re.sub(r'\n{2,}', '\n', t)
        if t:
            final[k] = {'to': d['to'], 't': t}
    n = per_book('commentary/mhcc', final)
    STATS['commentary_mhcc_sections'] = n

# ---------------------------------------------------------------- church fathers (public-domain translations only)
# Only entries whose source is a known 19th-century public-domain English translation:
#   Catena Aurea (Newman/Oxford 1841-45), NPNF Series 1 & 2, ANF (1885-96).
# Modern translations (e.g. ACCS, Fathers of the Church) are excluded even if the source repo includes them.
KEEP_TITLES = [
    r'^Catena Aurea by Aquinas$',
    r'^Homily on (the Gospel of (Matthew|John)|Acts|Romans|[12] ?Corinthians|Galatians|Ephesians|Philippians|Colossians|[12] ?Thessalonians|[12] ?Timothy|Titus|Philemon|Hebrews)\b',  # Chrysostom, NPNF1 10-14
    r'^Exposition on Psalm\b',            # Augustine, NPNF1 8
    r'^Tractates? on (the Gospel of )?John\b',  # Augustine, NPNF1 7
    r'^Homil(y|ies) on (the )?First Epistle of John\b',  # Augustine, NPNF1 7
    r'^City of God\b',                    # NPNF1 2
    r'^On the Sermon on the Mount\b',     # Augustine, NPNF1 6
    r'^Harmony of the Gospels\b',         # Augustine, NPNF1 6
]
KEEP_AUTHORS_FOR = {  # titles above only count for these authors (Catena counts for anyone it quotes)
    1: {'John Chrysostom'}, 2: {'Augustine of Hippo'}, 3: {'Augustine of Hippo'}, 4: {'Augustine of Hippo'},
    5: {'Augustine of Hippo'}, 6: {'Augustine of Hippo'}, 7: {'Augustine of Hippo'},
}
TRADITION_NOTE = 'Early church (shared by Catholic, Orthodox and Protestant traditions)'
def fathers():
    by = collections.defaultdict(list)
    kept = collections.Counter()
    skipped = 0
    db = os.path.join(SRC, 'commentaries-database')
    for adir in sorted(os.listdir(db)):
        p = os.path.join(db, adir)
        if not os.path.isdir(p) or adir.startswith('.'):
            continue
        meta = {}
        mf = os.path.join(p, 'metadata.toml')
        if os.path.exists(mf):
            try:
                meta = tomllib.load(open(mf, 'rb'))
            except Exception:
                meta = {}
        for f in os.listdir(p):
            m = re.match(r'^(.+) (\d+)_(\d+)(?:-(\d+))?\.toml$', f)
            if not m:
                continue
            code = code_of(m.group(1))
            ch, v = int(m.group(2)), int(m.group(3))
            if not code or not valid(code, ch, v):
                continue
            try:
                d = tomllib.load(open(os.path.join(p, f), 'rb'))
            except Exception:
                skipped += 1
                continue
            for c in d.get('commentary', []):
                title = (c.get('source_title') or '').strip()
                ok = False
                for ti, pat in enumerate(KEEP_TITLES):
                    if re.search(pat, title) and (ti not in KEEP_AUTHORS_FOR or adir in KEEP_AUTHORS_FOR[ti]):
                        ok = True
                        break
                if not ok:
                    skipped += 1
                    continue
                q = clean(c.get('quote', ''))
                if len(q) < 40:
                    continue
                by[(code, ch, v)].append({'a': adir, 'y': c.get('time') or meta.get('default_year'), 's': title, 't': q})
                kept[adir] += 1
    for k in by:
        by[k].sort(key=lambda e: (e['y'] or 9999))
    n = per_book('fathers', by)
    STATS['fathers'] = {'verses': n, 'quotes': sum(kept.values()), 'skipped_not_public_domain_source': skipped,
                        'top_authors': kept.most_common(12)}

# ---------------------------------------------------------------- creeds and catechisms
EXCLUDE_CREEDS = {  # copyrighted per the source repo README
    'chicago_statement_on_biblical_inerrancy', 'christ_hymn_of_colossians', 'christ_hymn_of_philippians',
    'christian_shema', 'confession_of_peter', 'helvetic_consensus', 'savoy_declaration', 'shema_yisrael'}
FAMILY = {
    'apostles_creed': 'Shared (all traditions)', 'nicene_creed': 'Shared (all traditions)',
    'athanasian_creed': 'Early church (Western)', 'chalcedonian_definition': 'Shared (all traditions)',
    'ignatius_creed': 'Early church', 'irenaeus_rule_of_faith': 'Early church', 'tertullians_rule_of_faith': 'Early church',
    'gregorys_declaration_of_faith': 'Early church', 'council_of_orange': 'Early church (Western)',
    'london_baptist_1689': 'Baptist', '1695_baptist_catechism': 'Baptist', 'abstract_of_principles': 'Baptist',
    'keachs_catechism': 'Baptist', 'puritan_catechism': 'Baptist',
    'waldensian_confession': 'Waldensian',
}
def creeds():
    out = []
    for f in sorted(glob.glob(os.path.join(SRC, 'creeds.json/creeds/*.json'))):
        slug = os.path.basename(f)[:-5]
        if slug in EXCLUDE_CREEDS:
            continue
        d = json.load(open(f, encoding='utf-8'))
        md = d['Metadata']
        if 'public domain' not in (md.get('SourceAttribution') or '').lower():
            continue
        out.append({'id': slug, 'title': md['Title'], 'year': md.get('Year'), 'authors': md.get('Authors'),
                    'format': md.get('CreedFormat'), 'family': FAMILY.get(slug, 'Reformed'),
                    'source': md.get('SourceUrl'), 'data': d['Data']})
    write('creeds/creeds.json', out)
    STATS['creeds'] = [(c['title'], c['family']) for c in out]

# ---------------------------------------------------------------- people and places (Theographic, OpenBible coordinates)
def people_places():
    tdir = os.path.join(SRC, 'theographic-bible-metadata/json')
    verses = {v['id']: v['fields'].get('osisRef') for v in json.load(open(f'{tdir}/verses.json'))}
    def refs_of(ids, limit=None):
        r = []
        for vid in ids or []:
            o = verses.get(vid)
            if o:
                pr = osis_ref(o)
                if pr:
                    r.append(pr)
        r.sort(key=lambda x: (CODES.index(x[0]), x[1], x[2]))
        return r[:limit] if limit else r
    pid = {}
    people = json.load(open(f'{tdir}/people.json'))
    places = json.load(open(f'{tdir}/places.json'))
    for p in people:
        pid[p['id']] = p['fields'].get('displayTitle') or p['fields'].get('name')
    plid = {p['id']: p['fields'].get('displayTitle') for p in places}
    out_people = []
    for p in people:
        f = p['fields']
        rel = lambda k: [pid[x] for x in f.get(k, []) if x in pid]
        out_people.append({
            'id': f.get('slug'), 'name': f.get('displayTitle') or f.get('name'), 'gender': f.get('gender'),
            'born': f.get('birthYear'), 'died': f.get('deathYear'),
            'father': rel('father'), 'mother': rel('mother'), 'siblings': rel('siblings'), 'children': rel('children'),
            'partners': rel('partners'),
            'birthPlace': [plid[x] for x in f.get('birthPlace', []) if x in plid],
            'deathPlace': [plid[x] for x in f.get('deathPlace', []) if x in plid],
            'count': f.get('verseCount'), 'first': (refs_of(f.get('verses'), 1) or [None])[0],
            'dict': clean(f.get('dictionaryText') or '') or None,
        })
    # OpenBible confidence: a place is "uncertain" if OpenBible lists more than one candidate site
    # or its best identification scores under 700 of 1000.
    unsure = {}
    for line in open(os.path.join(SRC, 'gnosis/sources/openbible/ancient.jsonl'), encoding='utf-8'):
        d = json.loads(line)
        ids = d.get('identifications') or []
        top = max([i['score'].get('time_total', 0) for i in ids if isinstance(i.get('score'), dict)] or [0])
        name = re.sub(r' \d+$', '', d['friendly_id'])
        unsure[name] = unsure.get(name, False) or top < 700 or len(ids) > 1
    out_places = []
    for p in places:
        f = p['fields']
        lat = f.get('openBibleLat') or f.get('latitude')
        lon = f.get('openBibleLong') or f.get('longitude')
        txt = f.get('dictText')
        if isinstance(txt, list):
            txt = '\n'.join(txt)
        out_places.append({
            'id': f.get('slug'), 'name': f.get('displayTitle'), 'type': f.get('featureType'),
            'lat': float(lat) if lat else None, 'lon': float(lon) if lon else None,
            'note': f.get('comment'), 'count': f.get('verseCount'),
            'uncertain': unsure.get(f.get('displayTitle')),
            'refs': refs_of(f.get('verses'), 30), 'dict': clean(txt) if txt else None,
        })
    write('people/people.json', out_people)
    write('places/places.json', out_places)
    # verse -> people/places index for tap-to-learn in the reader
    vidx = collections.defaultdict(lambda: {'p': [], 'l': []})
    for p in people:
        for vid in p['fields'].get('verses', []) or []:
            o = verses.get(vid)
            pr = osis_ref(o) if o else None
            if pr:
                vidx[tuple(pr[:3])]['p'].append(p['fields'].get('slug'))
    for p in places:
        for vid in p['fields'].get('verses', []) or []:
            o = verses.get(vid)
            pr = osis_ref(o) if o else None
            if pr:
                vidx[tuple(pr[:3])]['l'].append(p['fields'].get('slug'))
    n = per_book('people-places-by-verse', {k: {kk: vv for kk, vv in v.items() if vv} for k, v in vidx.items()})
    STATS['people'] = len(out_people)
    STATS['places'] = len(out_places)
    STATS['places_with_coordinates'] = sum(1 for p in out_places if p['lat'] is not None)
    STATS['places_location_uncertain'] = sum(1 for p in out_places if p['uncertain'])
    STATS['verses_with_people_or_places'] = n

if __name__ == '__main__':
    crossrefs(); dictionaries(); topics(); mhcc(); fathers(); creeds(); people_places()
    write('manifest.json', {'built_from': 'see README.md', 'stats': STATS})
    print(json.dumps(STATS, indent=1, ensure_ascii=False))
