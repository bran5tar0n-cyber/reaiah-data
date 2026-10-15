# Red letters for the BSB

`redletters-bsb.json` marks where God speaks in the Berean Standard Bible. Keys are `Book|chapter|verse` (BSB book names), values are `[start, end, category]` character spans into that verse's BSB text (the pinned BSB file, SHA-256 `cec3c644...739c9`).

## Owner rules (Brandon, 10/15/2026)
- **Red:** God speaking directly — Jesus' words, God speaking in a scene ("God said", "the LORD said to Moses", "the word of the LORD came to me", the voice from heaven), and the Holy Spirit speaking (Acts 8:29, 10:19-20, 13:2; Revelation 14:13, 22:17).
- **Black:** messengers speaking for God ("This is what the LORD says", "declares the LORD", words "spoken through the prophet").
- **The Angel of the LORD:** its own category. Readers disagree whether he is God Himself; the app marks him distinctly and explains why.

## How it was built
1. **Jesus' words** (2,163 spans): the World English Bible's published words-of-Jesus markup (`seven1m/open-bibles`, commit f257a35, public domain) mapped onto BSB quotations by matching quoted passages; 55 unclear verses resolved by hand (`resolve.py`). Words of Jesus quoted by other people in the story (e.g. John 5:11) are not red; His words retold by Paul in Acts are.
2. **God speaking** (3,241 spans) and **the Angel of the LORD** (31): BSB quotations whose speaker is God, found from the words introducing or following each quotation (`build_god.py`), with the messenger formulas excluded. Spot checks: about 19 in 20 correct before the last fixes; known misses remain.
3. **The Holy Spirit** (7 spans): every BSB verse where the Spirit speaks was listed and checked by hand. Messenger and citation uses stay black (Acts 21:11, Acts 28:25, Hebrews 3:7 and 10:15, Mark 12:36, Ezekiel 11:5).
4. `merge.py` combines everything and writes the file.

Errors are expected at the edges. The app has a "Report a red-letter mistake" control; reports go to Airtable and corrections are made here, then re-uploaded.
