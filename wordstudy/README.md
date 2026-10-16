# Word study data (Hebrew and Greek)

Word-by-word Hebrew Old Testament (Leningrad Codex) and Greek New Testament, with a short definition and plain-English grammar for every word. Reaiah's Study tab uses this data.

**Source:** [STEPBible-Data](https://github.com/STEPBible/STEPBible-Data), commit `bd09545c7a44b39ace20f16c0359915f2aa23a62` (14 Oct 2026). Data created for www.STEPBible.org by Tyndale House, Cambridge.
**License:** CC BY 4.0. **Credit (shown in the app wherever this data appears):** "Word data: STEP Bible (stepbible.org), CC BY 4.0"

Files used: TAHOT (Hebrew OT), TAGNT (Greek NT), TBESH (Hebrew lexicon, an abridged BDB), TBESG (Greek lexicon, mainly Abbott-Smith), TEHMC and TEGMC (grammar codes). Not used: TTESV, which is CC BY-NC.

## Files
| File | Contents |
|---|---|
| `hebrew/<Book>.json`, `greek/<Book>.json` | `{"ch:v": {"w": [word, ...], "h": "ch:v"}}`. Keys use English verse numbering. Verse `0` holds Psalm titles. `h` is the Hebrew verse number, present only when it differs. |
| Hebrew word | `[hebrew, transliteration, gloss, strong, grammar code, "Q"?]`. `"Q"` marks a Qere (read-as) form. |
| Greek word | `[greek, transliteration, gloss, strong, grammar code, edition?, second strong?]`. Edition is `"TR/Byz"` (only in the Textus Receptus or Byzantine text, e.g. Acts 8:37) or `"some"` (not in every major edition). Missing or `""` means it's in all major editions. |
| `lexicon-hebrew.json`, `lexicon-greek.json` | `{strong: {lemma, translit, gloss, def, count, refs}}`. `refs` is the first 60 places the word appears. |
| `grammar-hebrew.json`, `grammar-greek.json` | Grammar code → plain description. Hebrew codes joined by `/` are prefix/word/suffix parts; look up each one. |
| `manifest.json` | List of book files |
| `build.py` | The script that made these files from the source |

## Changes made to the source data (recorded per the CC BY terms)
1. Reorganized into one JSON file per book, keyed by English chapter:verse.
2. Hebrew: removed the `/` and `\` word-part dividers from the display text. Kept the Leningrad (L) and Qere (Q) readings only. Dropped the meaning-variant, spelling-variant, conjoin, and expanded-tag columns.
3. Greek: split each word from its transliteration. Reduced the edition list to the flag described above. Dropped the Spanish, sub-meaning, and variant columns. Combined words keep the first Strong number and grammar, plus the second Strong number.
4. Lexicons: converted HTML to plain text with line breaks, and kept only the text of cross-reference links.
5. Added `count` and `refs` (computed from the tagged text). Small function words (Hebrew H9xxx, Greek article G3588) are not counted. Greek counts include only words in all major editions.
6. Strong numbers missing from a lexicon were pointed to the entry with the same base number (e.g. G2453 → G2453G).
7. Grammar tables: normalized the separators.
