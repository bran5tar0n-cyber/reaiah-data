# Study data

Built by `build.py` from free sources. Every verse-keyed file is per book, named with the same STEP book codes as `wordstudy/` (`Gen.json` … `Rev.json`), keyed `"chapter:verse"`. A reference is `[book, chapter, verse]`, `[book, chapter, verse, end_verse]`, or `[book, chapter, verse, end_chapter, end_verse]`. Versification is the KJV/English one used across Reaiah.

| Folder | What it is | Source | License and credit line to show in the app |
|---|---|---|---|
| `crossrefs/` | Up to 20 related verses per verse, most-voted first (29,323 verses) | OpenBible.info cross-references (built on the Treasury of Scripture Knowledge), via scrollmapper/bible_databases | CC BY. "Cross-references: OpenBible.info, CC BY" |
| `dictionary/easton.json` | Easton's Bible Dictionary, 1897 (3,962 entries) | neuu-org/bible-dictionary-dataset | Text public domain; dataset CC BY 4.0. "Easton's Bible Dictionary (1897), data: NEUU, CC BY 4.0" |
| `dictionary/smith.json` | Smith's Bible Dictionary, 1863 (4,488 entries) | neuu-org/bible-dictionary-dataset | Same as above, "Smith's Bible Dictionary (1863)" |
| `topics/naves.json` | Nave's Topical Bible, 1896 (4,399 topics) | neuu-org/bible-topics-dataset, via spearssoftware/gnosis | Text public domain; dataset CC BY 4.0. "Nave's Topical Bible (1896), data: NEUU, CC BY 4.0" |
| `commentary/mhcc/` | Matthew Henry's Concise Commentary, by section (4,047 sections; `to` = last verse of the section) | CrossWire SWORD module MHCC v2.0, via spearssoftware/open-commentaries | Public domain. "Matthew Henry's Concise Commentary (public domain)" |
| `fathers/` | Early church fathers on a verse (17,566 quotes on 8,154 verses), oldest first | HistoricalChristianFaith/commentaries-database | Public domain. "Church fathers: public-domain translations (Catena Aurea; Nicene and Post-Nicene Fathers)" |
| `creeds/creeds.json` | 35 creeds, confessions and catechisms, each with a `family` label | NonlinearFruit/Creeds.json | Public domain texts only (Unlicense). |
| `people/`, `places/`, `people-places-by-verse/` | 3,067 people and 1,298 places (1,272 with map coordinates), plus which people and places appear in each verse | Theographic Bible Metadata (coordinates from OpenBible.info) | **CC BY-SA 4.0.** "People and places: Theographic Bible Metadata, CC BY-SA 4.0." These files must stay under CC BY-SA if changed and shared. |

## Choices made

- **Church fathers, public-domain translations only.** The source repository mixes 19th-century translations with modern copyrighted ones (and includes C. S. Lewis and G. K. Chesterton). Only these are kept: the Catena Aurea (Newman/Oxford translation, 1841–45), John Chrysostom's homilies on Matthew, John, Acts and the Pauline letters, and Augustine's Expositions on the Psalms, Tractates on John, City of God, Sermon on the Mount and Harmony of the Gospels (Nicene and Post-Nicene Fathers, 1886–90). That drops 73,751 entries. Deuterocanonical books are left out, to match Reaiah's 66-book canon.
- **Creeds.** Copyrighted items listed in the source README are excluded (Chicago Statement, Crossway hymn texts, Helvetic Consensus, Savoy Declaration). The source collection leans Reformed and Baptist. It has no Catholic catechism and no Orthodox confession: the shared ancient creeds (Apostles', Nicene, Athanasian, Chalcedon) are common to all three traditions. Churches of Christ hold to no creed but the Bible, which the app should say rather than leave them out silently.
- **Not included yet:** Jamieson-Fausset-Brown, Barnes, the Baltimore Catechism and the Philaret (Orthodox) catechism. All are public domain, but their sources can't be reached from the build machine.
- **Older works carry their own era and tradition.** Matthew Henry was an English Presbyterian; Easton a Scottish Presbyterian; the Catena collects Catholic and Orthodox fathers. The app labels each source.
