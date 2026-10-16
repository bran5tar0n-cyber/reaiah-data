"""Build Reaiah word-study data from STEPBible-Data (CC BY 4.0, STEP Bible, www.STEPBible.org).
Usage: python3 -I build.py <STEPBible-Data dir> <out dir>
Changes made to the source data (recorded per the CC BY terms) are listed in reaiah-data/wordstudy/README.md."""
import sys, os, re, json, glob, html, collections
SRC, OUT = sys.argv[1], sys.argv[2]
REF = re.compile(r'^(\d?[A-Z][a-z]{1,2})\.(\d+)\.(\d+)(?:\((\d+)\.(\d+)\))?#(\d+)=(\S+)\t')
def clean(s):
    s = re.sub(r'(?i)<br\s*/?>', '\n', s)
    s = re.sub(r"<ref='[^']*'>(.*?)</ref>", r'\1', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s).replace('__', '')
    return re.sub(r'[ \t]+', ' ', re.sub(r'\n\s*', '\n', s)).strip()
def morph_table(path, lang):
    t = {}
    for line in open(path, encoding='utf-8'):
        p = line.rstrip('\n').split('\t')
        if len(p) >= 2 and p[0] and p[1].startswith('Function='):
            t[p[0]] = re.sub(r'\s*;\s*', '; ', p[1]).strip('; ')
    return t
def lexicon(path):
    lex = {}
    for line in open(path, encoding='utf-8'):
        p = line.rstrip('\n').split('\t')
        if len(p) < 8 or not re.match(r'^[HG]\d{4}', p[0]): continue
        d = p[1].split(' ')[0].strip()
        if not re.match(r'^[HG]\d{4}[A-Za-z]?$', d): continue
        lex[d] = {"lemma": p[3], "translit": p[4], "gloss": p[6], "def": clean(p[7])}
    return lex
occ = {'H': collections.defaultdict(list), 'G': collections.defaultdict(list)}
def add_occ(lang, strong, ref):
    if strong and not strong.startswith(('H9', 'G3588')): occ[lang][strong].append(ref)
books = collections.OrderedDict()
# Hebrew
for f in sorted(glob.glob(os.path.join(SRC, 'Translators Amalgamated OT+NT', 'TAHOT *.txt'))):
    for line in open(f, encoding='utf-8'):
        m = REF.match(line)
        if not m: continue
        bk, c, v, hc, hv, n, typ = m.groups()
        if typ not in ('L', 'Q'): continue
        p = line.rstrip('\n').split('\t')
        word = p[1].replace('/', '').replace('\\', ' ').strip()
        main = re.search(r'\{(H\d{4}[A-Za-z]?)\}', p[4]); main = main.group(1) if main else ''
        parts = p[5].split('/'); mcode = '/'.join([parts[0]] + ['H' + x if not x.startswith('H') else x for x in parts[1:]])
        key = f'{c}:{v}'
        b = books.setdefault(('hebrew', bk), collections.OrderedDict())
        vv = b.setdefault(key, {"w": []})
        if hc and f'{hc}:{hv}' != key: vv["h"] = f'{hc}:{hv}'
        w = [word, p[2].replace('/', ''), p[3].replace('/', ''), main, mcode]
        if typ == 'Q': w.append('Q')
        vv["w"].append(w)
        if typ == 'L': add_occ('H', main, f'{bk}.{c}.{v}')
# Greek
for f in sorted(glob.glob(os.path.join(SRC, 'Translators Amalgamated OT+NT', 'TAGNT *.txt'))):
    for line in open(f, encoding='utf-8'):
        m = REF.match(line)
        if not m: continue
        bk, c, v, hc, hv, n, typ = m.groups()
        p = line.rstrip('\n').split('\t')
        g = re.match(r'(.*?)\s*\((.*)\)\s*$', p[1]); greek, tr = (g.group(1), g.group(2)) if g else (p[1], '')
        combo = [x.strip() for x in p[3].split(' + ')]
        st, _, mc = combo[0].partition('='); st = st.strip(); mc = mc.strip()
        also = combo[1].partition('=')[0].strip() if len(combo) > 1 else ''
        eds = set(p[5].split('+'))
        # Edition flag only: which reading traditions include the word (no critical-edition detail kept)
        inTR, inByz = 'TR' in eds, 'Byz' in eds
        ed = 'all' if (inTR and inByz and len(eds) >= 6) else ('TR/Byz' if (inTR or inByz) and not ({'NA28', 'SBL', 'WH', 'Tyn'} & eds) else ('some' ))
        key = f'{c}:{v}'
        b = books.setdefault(('greek', bk), collections.OrderedDict())
        vv = b.setdefault(key, {"w": []})
        w = [greek, tr, p[2], st, mc]
        if ed != 'all' or also: w.append('' if ed == 'all' else ed)
        if also: w.append(also)
        vv["w"].append(w)
        if ed == 'all': add_occ('G', st, f'{bk}.{c}.{v}')
# Resolve Strong numbers the lexicon lacks to the nearest entry with the same base number (e.g. G2453 -> G2453G).
LEX = {}
for lang, name in (('hebrew', 'TBESH'), ('greek', 'TBESG')):
    LEX[lang] = lexicon(glob.glob(os.path.join(SRC, 'Lexicons', name + ' *.txt'))[0])
def resolve(lang, s):
    lx = LEX[lang]
    if not s or s in lx: return s
    base = s[:5]
    for k in lx:
        if k.startswith(base): return k
    return s
for (lang, bk), data in books.items():
    for vv in data.values():
        for w in vv["w"]:
            w[3] = resolve(lang, w[3])
for k in ('H', 'G'):
    lang = 'hebrew' if k == 'H' else 'greek'
    merged = collections.defaultdict(list)
    for s, refs in occ[k].items(): merged[resolve(lang, s)].extend(refs)
    occ[k] = merged
os.makedirs(OUT, exist_ok=True)
manifest = {"source": "STEPBible-Data (STEP Bible, www.STEPBible.org), CC BY 4.0", "books": {}}
for (lang, bk), data in books.items():
    d = os.path.join(OUT, lang); os.makedirs(d, exist_ok=True)
    fn = os.path.join(d, f'{bk}.json'); json.dump(data, open(fn, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    manifest["books"].setdefault(lang, []).append(bk)
L = os.path.join(SRC, 'Lexicons')
for lang, name, mname in (('hebrew', 'TBESH', 'TEHMC'), ('greek', 'TBESG', 'TEGMC')):
    lex = LEX[lang]
    key = 'H' if lang == 'hebrew' else 'G'
    for s, refs in occ[key].items():
        if s in lex: lex[s]["count"] = len(refs); lex[s]["refs"] = refs[:60]
    json.dump(lex, open(os.path.join(OUT, f'lexicon-{lang}.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    mt = morph_table(glob.glob(os.path.join(SRC, 'Morphology codes', mname + ' *.txt'))[0], lang)
    json.dump(mt, open(os.path.join(OUT, f'grammar-{lang}.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
json.dump(manifest, open(os.path.join(OUT, 'manifest.json'), 'w'), indent=1)
print({k: len(v) for k, v in manifest["books"].items()})
