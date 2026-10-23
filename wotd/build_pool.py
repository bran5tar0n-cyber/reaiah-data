"""Build wotd/pool.json: the verses Reaiah draws each person's random word of the day from.

References only (no Bible text); the app takes the text from its stored BSB.
Run: python3 wotd/build_pool.py  (validates every reference against kjv/KJV.json)
"""
import json, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

# theme: peace, love, wisdom, worship, hope, strength, faith, grace, rest, guidance, joy, mercy, courage
POOL = """
peace|Numbers 6:24-26
strength|Deuteronomy 31:6
love|Deuteronomy 7:9
guidance|Deuteronomy 31:8
courage|Joshua 1:9
faith|Joshua 24:15
love|Ruth 1:16
hope|1 Samuel 2:2
wisdom|1 Samuel 16:7
worship|2 Samuel 22:2-3
guidance|2 Samuel 22:29
worship|1 Kings 8:23
peace|1 Kings 19:12
worship|1 Chronicles 16:34
strength|1 Chronicles 16:11
worship|1 Chronicles 29:11
mercy|2 Chronicles 7:14
strength|2 Chronicles 16:9
joy|Nehemiah 8:10
worship|Nehemiah 9:6
courage|Esther 4:14
hope|Job 19:25
wisdom|Job 28:28
faith|Job 42:2
faith|Job 1:21
peace|Psalm 4:8
worship|Psalm 8:3-4
worship|Psalm 9:1
strength|Psalm 9:9-10
guidance|Psalm 16:8
joy|Psalm 16:11
love|Psalm 18:1-2
worship|Psalm 19:1
wisdom|Psalm 19:7
worship|Psalm 19:14
peace|Psalm 23:1-3
courage|Psalm 23:4
love|Psalm 23:6
worship|Psalm 24:1
guidance|Psalm 25:4-5
mercy|Psalm 25:6-7
courage|Psalm 27:1
worship|Psalm 27:4
hope|Psalm 27:13-14
strength|Psalm 28:7
peace|Psalm 29:11
joy|Psalm 30:5
joy|Psalm 30:11
faith|Psalm 31:14-15
courage|Psalm 31:24
mercy|Psalm 32:1
guidance|Psalm 32:8
love|Psalm 33:20-22
worship|Psalm 34:1
peace|Psalm 34:4
worship|Psalm 34:8
hope|Psalm 34:18
love|Psalm 36:5
joy|Psalm 37:4
faith|Psalm 37:5
rest|Psalm 37:7
guidance|Psalm 37:23-24
hope|Psalm 40:1-3
hope|Psalm 42:11
strength|Psalm 46:1
rest|Psalm 46:10
worship|Psalm 47:1
mercy|Psalm 51:10
mercy|Psalm 51:12
faith|Psalm 55:22
courage|Psalm 56:3-4
love|Psalm 57:10
rest|Psalm 62:1-2
hope|Psalm 62:5
worship|Psalm 63:1
love|Psalm 63:3
worship|Psalm 66:1-2
strength|Psalm 68:19
strength|Psalm 73:26
worship|Psalm 84:1-2
joy|Psalm 84:10
grace|Psalm 84:11
love|Psalm 86:5
guidance|Psalm 86:11
mercy|Psalm 86:15
worship|Psalm 89:1
wisdom|Psalm 90:12
joy|Psalm 90:14
rest|Psalm 91:1-2
courage|Psalm 91:4
worship|Psalm 92:1-2
worship|Psalm 95:1
worship|Psalm 95:6-7
worship|Psalm 96:1-2
joy|Psalm 100:1-2
worship|Psalm 100:4-5
worship|Psalm 103:1-2
mercy|Psalm 103:8
mercy|Psalm 103:11-12
love|Psalm 103:13
worship|Psalm 104:33
love|Psalm 107:1
peace|Psalm 107:29-30
wisdom|Psalm 111:10
worship|Psalm 113:3
love|Psalm 116:1-2
rest|Psalm 116:7
joy|Psalm 118:24
faith|Psalm 118:6
wisdom|Psalm 119:11
guidance|Psalm 119:105
hope|Psalm 119:114
peace|Psalm 119:165
strength|Psalm 121:1-2
peace|Psalm 121:7-8
joy|Psalm 126:3
hope|Psalm 126:5
rest|Psalm 127:2
hope|Psalm 130:5
peace|Psalm 131:2
love|Psalm 133:1
love|Psalm 136:1
courage|Psalm 138:3
guidance|Psalm 138:8
love|Psalm 139:1
guidance|Psalm 139:9-10
worship|Psalm 139:14
guidance|Psalm 139:23-24
guidance|Psalm 143:8
worship|Psalm 145:3
mercy|Psalm 145:8-9
love|Psalm 145:18
hope|Psalm 147:3
joy|Psalm 149:4
worship|Psalm 150:6
wisdom|Proverbs 1:7
guidance|Proverbs 3:5-6
wisdom|Proverbs 3:13
peace|Proverbs 3:24
wisdom|Proverbs 4:7
wisdom|Proverbs 4:23
wisdom|Proverbs 9:10
love|Proverbs 10:12
wisdom|Proverbs 11:2
wisdom|Proverbs 12:25
wisdom|Proverbs 15:1
joy|Proverbs 15:13
guidance|Proverbs 16:3
guidance|Proverbs 16:9
wisdom|Proverbs 16:24
joy|Proverbs 17:22
love|Proverbs 17:17
strength|Proverbs 18:10
guidance|Proverbs 19:21
courage|Proverbs 28:1
faith|Proverbs 29:25
strength|Proverbs 31:25
wisdom|Ecclesiastes 3:1
worship|Ecclesiastes 3:11
strength|Ecclesiastes 4:9-10
strength|Ecclesiastes 4:12
wisdom|Ecclesiastes 12:13
love|Song of Solomon 8:7
mercy|Isaiah 1:18
peace|Isaiah 9:6
worship|Isaiah 12:2
peace|Isaiah 26:3
peace|Isaiah 26:4
rest|Isaiah 30:15
guidance|Isaiah 30:21
peace|Isaiah 32:17
hope|Isaiah 40:8
love|Isaiah 40:11
strength|Isaiah 40:29
strength|Isaiah 40:31
courage|Isaiah 41:10
courage|Isaiah 41:13
guidance|Isaiah 42:16
love|Isaiah 43:1
courage|Isaiah 43:2
hope|Isaiah 43:18-19
mercy|Isaiah 43:25
mercy|Isaiah 44:22
love|Isaiah 46:4
love|Isaiah 49:15-16
mercy|Isaiah 53:5
love|Isaiah 54:10
mercy|Isaiah 55:6-7
wisdom|Isaiah 55:8-9
hope|Isaiah 55:11
joy|Isaiah 55:12
guidance|Isaiah 58:11
joy|Isaiah 61:10
hope|Isaiah 61:1
love|Isaiah 62:5
guidance|Isaiah 64:8
love|Jeremiah 31:3
hope|Jeremiah 29:11
faith|Jeremiah 29:12-13
faith|Jeremiah 17:7-8
worship|Jeremiah 32:17
guidance|Jeremiah 33:3
mercy|Lamentations 3:22-23
hope|Lamentations 3:24-26
mercy|Ezekiel 36:26
guidance|Ezekiel 34:16
wisdom|Daniel 2:20-21
faith|Daniel 3:17-18
hope|Hosea 6:3
mercy|Joel 2:13
hope|Joel 2:25
mercy|Micah 7:18
wisdom|Micah 6:8
strength|Nahum 1:7
faith|Habakkuk 3:17-18
strength|Habakkuk 3:19
love|Zephaniah 3:17
strength|Zechariah 4:6
faith|Malachi 3:6
guidance|Matthew 4:19
joy|Matthew 5:3-4
mercy|Matthew 5:7-8
peace|Matthew 5:9
love|Matthew 5:14-16
love|Matthew 5:44
faith|Matthew 6:6
faith|Matthew 6:26
faith|Matthew 6:33
peace|Matthew 6:34
faith|Matthew 7:7-8
rest|Matthew 11:28-30
faith|Matthew 14:27
faith|Matthew 17:20
love|Matthew 18:20
faith|Matthew 19:26
love|Matthew 22:37-39
love|Matthew 25:40
hope|Matthew 28:20
courage|Mark 4:39-40
rest|Mark 6:31
faith|Mark 9:23-24
faith|Mark 10:27
love|Mark 10:45
faith|Mark 11:24
faith|Luke 1:37
worship|Luke 1:46-47
joy|Luke 2:10-11
peace|Luke 2:14
love|Luke 6:31
mercy|Luke 6:36
grace|Luke 6:38
rest|Luke 10:41-42
love|Luke 12:6-7
faith|Luke 12:32
love|Luke 15:7
love|Luke 15:20
mercy|Luke 19:10
hope|Luke 24:32
love|John 1:5
grace|John 1:14
grace|John 1:16
love|John 3:16
love|John 3:17
joy|John 4:14
hope|John 6:35
guidance|John 8:12
peace|John 8:32
joy|John 10:10
love|John 10:11
love|John 10:27-28
hope|John 11:25
love|John 13:34-35
peace|John 14:1
hope|John 14:2-3
guidance|John 14:6
peace|John 14:27
love|John 15:5
love|John 15:9
joy|John 15:11
love|John 15:13
peace|John 16:33
joy|John 16:22
faith|John 20:29
courage|Acts 1:8
joy|Acts 2:46-47
guidance|Acts 17:27-28
grace|Acts 20:24
faith|Romans 1:16
peace|Romans 5:1
hope|Romans 5:3-5
love|Romans 5:8
grace|Romans 6:23
mercy|Romans 8:1
grace|Romans 8:15
strength|Romans 8:26
hope|Romans 8:28
love|Romans 8:31
love|Romans 8:38-39
worship|Romans 11:33
worship|Romans 12:1
wisdom|Romans 12:2
love|Romans 12:10
hope|Romans 12:12
love|Romans 13:10
peace|Romans 14:19
hope|Romans 15:13
wisdom|1 Corinthians 1:25
hope|1 Corinthians 2:9
strength|1 Corinthians 10:13
love|1 Corinthians 13:4-5
love|1 Corinthians 13:6-7
love|1 Corinthians 13:13
courage|1 Corinthians 15:57-58
courage|1 Corinthians 16:13-14
love|2 Corinthians 1:3-4
hope|2 Corinthians 4:8-9
hope|2 Corinthians 4:16-17
faith|2 Corinthians 5:7
hope|2 Corinthians 5:17
grace|2 Corinthians 9:8
grace|2 Corinthians 12:9
love|Galatians 2:20
love|Galatians 5:13
joy|Galatians 5:22-23
hope|Galatians 6:9
love|Galatians 6:2
love|Ephesians 1:7
worship|Ephesians 1:3
grace|Ephesians 2:8-9
guidance|Ephesians 2:10
love|Ephesians 3:17-19
worship|Ephesians 3:20-21
peace|Ephesians 4:2-3
love|Ephesians 4:32
love|Ephesians 5:1-2
courage|Ephesians 6:10
faith|Philippians 1:6
love|Philippians 1:9
wisdom|Philippians 2:3-4
joy|Philippians 4:4
peace|Philippians 4:6-7
wisdom|Philippians 4:8
strength|Philippians 4:13
grace|Philippians 4:19
hope|Philippians 3:13-14
guidance|Colossians 1:9-10
worship|Colossians 1:16-17
love|Colossians 3:12
love|Colossians 3:14
peace|Colossians 3:15
worship|Colossians 3:16
guidance|Colossians 3:23
hope|1 Thessalonians 4:13-14
joy|1 Thessalonians 5:16-18
faith|1 Thessalonians 5:24
peace|2 Thessalonians 3:16
strength|2 Thessalonians 3:3
grace|1 Timothy 1:15
faith|1 Timothy 6:12
courage|2 Timothy 1:7
wisdom|2 Timothy 3:16-17
faith|2 Timothy 4:7
grace|Titus 2:11
grace|Titus 3:4-5
worship|Hebrews 1:3
mercy|Hebrews 4:15-16
hope|Hebrews 6:19
faith|Hebrews 10:23
faith|Hebrews 11:1
faith|Hebrews 11:6
courage|Hebrews 12:1-2
love|Hebrews 13:5
faith|Hebrews 13:8
joy|James 1:2-3
wisdom|James 1:5
wisdom|James 1:19
grace|James 1:17
faith|James 4:8
grace|James 4:6
hope|1 Peter 1:3
joy|1 Peter 1:8
love|1 Peter 4:8
grace|1 Peter 4:10
faith|1 Peter 5:7
strength|1 Peter 5:10
grace|2 Peter 1:3
mercy|2 Peter 3:9
guidance|1 John 1:7
mercy|1 John 1:9
love|1 John 3:1
love|1 John 3:18
courage|1 John 4:4
love|1 John 4:7
love|1 John 4:10
love|1 John 4:16
courage|1 John 4:18
love|1 John 4:19
faith|1 John 5:14
worship|Jude 1:24-25
worship|Revelation 4:11
hope|Revelation 3:20
worship|Revelation 5:12
hope|Revelation 21:4
hope|Revelation 21:5
worship|Revelation 22:13
worship|Exodus 15:2
peace|Exodus 14:14
love|Exodus 34:6
rest|Exodus 33:14
worship|Genesis 1:1
love|Genesis 1:27
faith|Genesis 15:6
guidance|Genesis 28:15
hope|Genesis 50:20
worship|Deuteronomy 6:4-5
love|Deuteronomy 33:27
worship|Psalm 113:5-6
hope|Isaiah 25:8
peace|Isaiah 52:7
"""

NAME_MAP = {"1 ": "I ", "2 ": "II ", "3 ": "III "}
SPECIAL = {"Psalm": "Psalms", "Revelation": "Revelation of John"}

def file_book(book):
    for a, b in NAME_MAP.items():
        if book.startswith(a):
            return b + book[len(a):]
    return SPECIAL.get(book, book)

def main():
    kjv = json.loads((ROOT / "kjv/KJV.json").read_text())
    idx = {}
    for b in kjv["books"]:
        for c in b["chapters"]:
            for v in c["verses"]:
                idx[(b["name"], c["chapter"], v["verse"])] = v["text"]
    out, seen, bad = [], set(), []
    for line in POOL.strip().splitlines():
        theme, ref = line.split("|")
        m = re.fullmatch(r"(.+) (\d+):(\d+)(?:-(\d+))?", ref)
        book, ch, v1, v2 = m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4) or m.group(3))
        if ref in seen:
            bad.append(f"duplicate {ref}")
            continue
        seen.add(ref)
        fb = file_book(book)
        for v in range(v1, v2 + 1):
            if (fb, ch, v) not in idx:
                bad.append(f"missing {ref} (v{v})")
        out.append({"ref": ref, "book": book, "chapter": ch, "from": v1, "to": v2, "theme": theme})
    if bad:
        print("\n".join(bad)); sys.exit(1)
    (ROOT / "wotd/pool.json").write_text(json.dumps({"count": len(out), "verses": out}, indent=1) + "\n")
    print(len(out), "verses OK")

if __name__ == "__main__":
    main()
