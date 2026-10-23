"""Index every place each Strong's number appears: wordstudy/occurrences-{hebrew,greek}.json
{strong: {"n": count, "r": [[book, ch, v], ...]}}. Lists are left out ("r" missing) for words
appearing more than 2,000 times (articles, conjunctions); the count is still given."""
import json, glob, os, collections
HERE = os.path.dirname(os.path.abspath(__file__))
CAP = 2000
CODES = ('Gen Exo Lev Num Deu Jos Jdg Rut 1Sa 2Sa 1Ki 2Ki 1Ch 2Ch Ezr Neh Est Job Psa Pro Ecc Sng Isa Jer Lam Ezk Dan Hos Jol Amo Oba Jon Mic Nam Hab Zep Hag Zec Mal Mat Mrk Luk Jhn Act Rom 1Co 2Co Gal Eph Php Col 1Th 2Th 1Ti 2Ti Tit Phm Heb Jas 1Pe 2Pe 1Jn 2Jn 3Jn Jud Rev').split()
for lang in ('hebrew', 'greek'):
    occ = collections.defaultdict(list)
    for f in sorted(glob.glob(f'{HERE}/{lang}/*.json')):
        book = os.path.basename(f)[:-5]
        for key, verse in json.load(open(f, encoding='utf-8')).items():
            ch, v = (int(x) for x in key.split(':'))
            seen = set()
            for w in verse['w']:
                for s in w[3:4] + ([w[6]] if lang == 'greek' and len(w) > 6 and isinstance(w[6], str) and w[6].startswith('G') else []):
                    s = s.rstrip('ABCDEFGHIJKLMNOPQRSTUVWXYZ')[:5] if s else s  # H3068G -> H3068
                    if s and s not in seen and s[1:].isdigit() and s not in ('H9001',) :
                        seen.add(s)
                        occ[s].append([book, ch, v])
    out = {}
    for s, refs in sorted(occ.items()):
        refs.sort(key=lambda r: (CODES.index(r[0]), r[1], r[2]))
        out[s] = {'n': len(refs)} if len(refs) > CAP else {'n': len(refs), 'r': refs}
    json.dump(out, open(f'{HERE}/occurrences-{lang}.json', 'w', encoding='utf-8'), separators=(',', ':'))
    print(lang, len(out), 'numbers;', sum(1 for x in out.values() if 'r' not in x), 'over cap')
