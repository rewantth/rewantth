<div align="center">

<img src="assets/terminal.svg" alt="Kali Linux terminal: PROJECTS. A scan of the inbox-dashboard project lists five modules: mail-reader, classifier, vault, pipeline and alerts." width="100%">

</div>

```console
┌──(kali㉿kali)-[~/projects]
└─$ ls -1
inbox-dashboard/
```

---

## `inbox-dashboard/`

> A security-first dashboard that turns the emails in a mailbox into a live, encrypted web page. It reads mail with read-only access, sorts it by sender and wording, and publishes a static page that only the owner's passphrase can open.

| | |
|---|---|
| **Stack** | Python 3.12 · Gmail API (OAuth 2.0) · WebCrypto · vanilla JavaScript · GitHub Actions |
| **Status** | Running, refreshing every 30 minutes |
| **Source** | Private repository. Only the finished page and its encrypted data are public |
| **Tests** | 85 automated checks across four suites |

```console
┌──(kali㉿kali)-[~/projects/inbox-dashboard]
└─$ tree --modules
.
├── mail-reader    read-only Gmail OAuth, incremental download with a cache
├── classifier     rule engine: sender, subject and body patterns decide the category and stage
├── vault          AES-256-GCM encryption, decrypted only in the browser
├── pipeline       scheduled build, private source, one-way publish to a public page
└── alerts         optional phone alerts that carry counts only, never names
```

### Architecture

```text
 Gmail (read-only)
        │
        ▼
 ┌──────────────────────────┐        ┌──────────────────────────────┐
 │  PRIVATE repository      │        │  PUBLIC repository           │
 │  mail-reader             │ deploy │  index.html   (page + CSP)   │
 │  classifier              │──key──▶│  data.enc.json (ciphertext)  │
 │  vault  (encrypts)       │ 1 repo │  nothing else                │
 │  alerts ──▶ ntfy (counts)│        └──────────────┬───────────────┘
 └──────────────────────────┘                       │
                                                    ▼
                                      browser: passphrase ──▶ WebCrypto ──▶ dashboard
```

### Security design

| Threat | Control |
|---|---|
| Mailbox exposure | Read-only OAuth scope (`gmail.readonly`). The token lives only as an encrypted CI secret and is visible to one build step. |
| Someone downloads the data file | AES-256-GCM, key from PBKDF2-SHA-256 with 1,000,000 rounds, a fixed per-project salt and a fresh random IV for every file. A tampered file fails authentication. |
| Script injection in the page | A strict Content Security Policy is generated at build time from the page's own script hash. Injected scripts and inline handlers are refused, and the page may only contact its own origin. Tested by actually injecting both. |
| Stolen browser storage | "Keep me unlocked" stores a non-extractable `CryptoKey`, not the passphrase. Nothing readable is kept, and Lock deletes it. |
| Hijacked dependency or action | Every GitHub Action is pinned to an exact commit and every Python package to an exact version. Dependabot proposes upgrades for review. |
| Over-powered CI | The workflow starts with `permissions: {}`. The publishing key is an SSH deploy key that can write to one repository and nothing else. Host keys come from GitHub's published list. |
| Source code exposure | Private source repository. The public side receives only built files, as a single commit force-pushed each run, so history never accumulates. |
| Leaks through logs and alerts | Logs of public pipelines print nothing about the data. Phone alerts say things like "1 new reply", never a name or subject. |
| Clickjacking and referrer leaks | The page refuses to run inside a frame and sends no referrer. |

### Engineering notes

- **Why a fixed salt?** The browser can then remember one key between visits instead of the passphrase. The salt isn't secret. It is unique per project, and every file still gets its own random IV.
- **Why private source and a public page?** The free tier of the hosting platform serves pages only from public repositories. Splitting build from publish keeps the code private while the page stays reachable.
- **Why an incremental cache?** Private pipelines have a monthly minutes budget. Reusing already-downloaded mail keeps each run well under a minute.
- **Alert diffing without a database:** each run downloads the previous published ciphertext, decrypts it with the same passphrase, and compares. Only emails newer than three days can trigger an alert, so a rule change can't flood the phone.

### Tests

```console
┌──(kali㉿kali)-[~/projects/inbox-dashboard]
└─$ python tests/test_classify.py && python tests/test_alerts.py && python tests/test_security.py && python tests/test_cache.py
32 of 32 checks passed
20 of 20 checks passed
25 of 25 checks passed
8 of 8 checks passed
```

| Suite | What it proves |
|---|---|
| `test_classify` | Categories, stages and sources are detected correctly, and newsletters and look-alikes are ignored |
| `test_alerts` | Alerts fire only for new events, carry no names, and reach a local stand-in server correctly |
| `test_security` | The policy is applied and blocks injection, the key can't be extracted, tampered ciphertext is rejected, and all dependencies are pinned |
| `test_cache` | Only missing mail is downloaded, and a damaged cache is never fatal |

---

```console
┌──(kali㉿kali)-[~/projects]
└─$ echo "more to come"
more to come
```
