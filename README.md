# reaiah-data

Public-domain Bible data used by the Reaiah app.

This repository holds only freely licensed scripture data and data derived from it, such as red-letter markings for the Berean Standard Bible. It contains no app code, prompts, or user information.

Reaiah loads each file once into its own storage and checks it against a published SHA-256 fingerprint. App users never download from this repository directly.

## Contents
| File | What it is |
|---|---|
| `redletters/redletters-bsb.json` | Where God speaks in the BSB: words of Jesus, God speaking directly, the Holy Spirit speaking, and the Angel of the LORD, as character spans per verse |
| `kjv/KJV.json` | King James Version (1769), 66 books, public domain in the US |
| `SHA256SUMS` | Fingerprints for every data file |

## Sources and licenses
- Berean Standard Bible (BSB): CC0 / public domain
- World English Bible (WEB) words-of-Jesus markup, used to place the red letters: public domain
- King James Version (1769): public domain in the United States (Crown patent in the UK); source seven1m/open-bibles
- Red-letter data in this repository: released under CC0 1.0 (public domain dedication)

© Reaiah, part of N35.
