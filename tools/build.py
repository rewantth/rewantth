#!/usr/bin/env python3
"""Builds the profile README as plain GitHub content (text, tables, code blocks).

    python tools/build.py               # everything: README.md, assets/avatar.svg, blog pages (needs internet)
    python tools/build.py --stats-only  # only the stats block inside README.md (what the daily GitHub job runs)

Edit the CONTENT section below, then run it again.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
USER = "rewantth"
GH = f"https://github.com/{USER}/"
HIDE_REPOS = {"notes", "rewantth", "rewantth.github.io"}   # public repos not shown in the stats

# ============================== CONTENT (edit here) ==============================
PROJECTS = [
    dict(slug="sentinel-travel", repo="SentinelTravel", visibility="public",
         tagline="identity threat detection and impossible-travel analytics, shown as a live SOC console.",
         stack=["FastAPI", "React", "SQLite", "WebSockets", "Leaflet", "Recharts"],
         status="portfolio project, synthetic data only",
         modules=[("detection", "travel speed (Haversine), per-user baselines, risk and confidence scoring, MITRE ATT&CK mapping"),
                  ("signals", "impossible travel, VPN/proxy and TOR use, MFA failures, bad IP reputation, credential stuffing"),
                  ("console", "live alert stream, maps, analyst notes, audit log, kill-switch actions, SIEM-style exports"),
                  ("data", "15 synthetic attack scenarios, no real users or logs")],
         note="Identity attacks look like normal logins until timing, location, device and MFA are correlated. This turns authentication events into explainable alerts and shows the reasoning to the analyst."),
    dict(slug="sentinelops", repo="sentinelops-soc-console", visibility="public",
         tagline="SOC alert triage and investigation console with MITRE ATT&CK mapping and case tracking.",
         stack=["Flask", "SQLAlchemy", "SQLite", "Chart.js", "JavaScript"],
         status="portfolio project, safe simulated alerts",
         modules=[("ingest", "simulated alert generation, JSON ingestion into SQLite"),
                  ("triage", "severity and status filters, MITRE ATT&CK classification, IP enrichment with a safe no-key fallback"),
                  ("cases", "new to closed workflow, timeline with second-level timestamps, analyst notes"),
                  ("reporting", "live simulated feed, charts, investigation export as JSON, MTTD and MTTR metrics")],
         note="Defensive and blue-team only: no offensive functionality, malware or harmful payloads."),
    dict(slug="phishguard-x", repo="phishguard-x", visibility="public",
         tagline="explainable phishing detection and email threat analysis.",
         stack=["Python", "Flask", "pytest"],
         status="portfolio project",
         modules=[("email-checks", "urgency, coercion, credential bait, scam-like phrasing"),
                  ("sender-checks", "impersonation, free-provider misuse, brand mismatch"),
                  ("url-checks", "shorteners, IP links, risky TLDs, redirects, obfuscation, displayed-vs-actual links"),
                  ("scoring", "weighted category scores, severity, confidence and a verdict")],
         note="The engine is rule-based on purpose, so every finding is explainable: each carries a rule id, evidence, severity and remediation. It includes sample phishing and legitimate messages and unit tests for scoring."),
    dict(slug="securewave-net", repo="Enterprise-Secure-Network-Packet-Tracer", visibility="public",
         extra_link=("project page", "https://rewantth.github.io/Enterprise-Secure-Network-Packet-Tracer/"),
         tagline="an enterprise branch network with VLAN segmentation, a DMZ and routed security zones, built in Cisco Packet Tracer.",
         stack=["Cisco Packet Tracer", "VLANs", "SVIs", "DHCP", "DNS", "AAA"],
         status="core network complete. ACLs, port security and OSPF planned",
         modules=[("segmentation", "8 VLANs, a guest VLAN, and a black-hole VLAN 999 for unused ports"),
                  ("routing", "layer 3 inter-VLAN routing on a core switch, edge router link, trunks to 5 access switches"),
                  ("services", "DHCP for every user VLAN, a DMZ with DNS, web and AAA servers"),
                  ("evidence", "device configs, IP and VLAN plan, test checklists and a security policy matrix")],
         note="Next: ACL-based access control between VLANs, port security, and OSPF between the edge router and core."),
    dict(slug="cdsa-study-tracker", repo="cdsa-study-tracker", visibility="public",
         extra_link=("live page", "https://rewantth.github.io/cdsa-study-tracker/"),
         tagline="a free, offline study tracker for the HTB SOC Analyst path and the CDSA exam. no accounts, no backend, no network requests.",
         stack=["single-file HTML", "JavaScript", "CSS"],
         status="live, progress never leaves the browser",
         modules=[("plan", "341 checkboxes across 25 modules, with a daily plan that re-plans from what is left"),
                  ("review", "spaced-repetition queue, focus timer, streaks that ignore rest days"),
                  ("guides", "per-module guides, hints, notes, a problem roadmap and an exam readiness tab"),
                  ("privacy", "progress stays in the browser, with download and restore backups")],
         note="Privacy by design: with no analytics and no requests to any server, nothing about the user can leak."),
    dict(slug="inbox-dashboard", repo=None, visibility="private",
         tagline="a security-first dashboard that turns the emails in a mailbox into a live, encrypted web page.",
         stack=["Python 3.12", "Gmail API", "WebCrypto", "vanilla JS", "GitHub Actions"],
         status="running, source private",
         modules=[("mail-reader", "read-only Gmail OAuth, incremental download with a cache"),
                  ("classifier", "rule engine: sender, subject and body patterns decide the category and stage"),
                  ("vault", "AES-256-GCM encryption, decrypted only in the browser"),
                  ("pipeline", "scheduled build in a private repo, one-way publish to a public page")],
         note="Security: read-only OAuth scope · AES-256-GCM with PBKDF2-SHA-256 (1,000,000 rounds) · strict Content Security Policy from the page's own script hash · a non-extractable CryptoKey instead of the passphrase · every Action pinned to a commit · a deploy key that writes to one repository. 85 automated checks."),
]
FOCUS = [
    ("detection", "spot attacks in data: impossible travel, phishing, alert triage and MITRE ATT&CK mapping"),
    ("defence", "segment networks, apply least privilege and protect data with encryption"),
    ("explainable", "every alert, score and finding shows the evidence behind it"),
    ("method", "synthetic or self-owned data only, and authorized targets only"),
]
POSTS = [
    dict(slug="inbox-dashboard-security", date="2026-11-20", title="A dashboard that can't leak its own data",
         desc="The threat model first, then the controls it produced.", tags=["security", "python", "webcrypto"],
         body="""# A dashboard that can't leak its own data

I wanted a page that shows the state of a mailbox from any device, without the page, the pipeline or the logs ever holding that data in the clear. I wrote the threat model before the code.

## Threats I wrote down

- **Someone reads the mailbox.** The program only gets read-only access, through the `gmail.readonly` scope. It cannot send, delete or change anything.
- **Someone downloads the published data.** The page has to be public, so the file is public too. It is encrypted with AES-256-GCM. The key comes from a passphrase through PBKDF2-SHA-256 with 1,000,000 rounds. Each file gets its own random IV, and tampering fails authentication.
- **Someone injects script into the page.** A strict Content Security Policy is generated at build time from the hash of the page's own script. Injected scripts and inline handlers are refused. I tested it by injecting both.
- **A dependency or CI action is hijacked.** Every Action is pinned to an exact commit and every Python package to an exact version. The workflow starts with `permissions: {}` and each job asks only for what it needs.
- **The source leaks.** The code lives in a private repository. Only the finished page and the ciphertext are published, using an SSH deploy key that can write to one repository and nothing else.

## What it cannot do

The encrypted file is public, so anyone can try passphrases on their own computer. The 1,000,000 rounds slow that down. They do not stop it. Only a long random passphrase does. That is the honest limit of any static page.

## Tests

```
32 of 32  classifier
20 of 20  alerts
25 of 25  security
 8 of 8   cache
```

The security suite checks that the policy blocks injection, that a tampered file is rejected, that nothing stores the passphrase, and that every dependency is pinned.
"""),
    dict(slug="keep-the-key", date="2026-11-19", title="Keep the key, not the passphrase",
         desc="Remember a user without ever storing their secret.", tags=["webcrypto", "indexeddb", "security"],
         body="""# Keep the key, not the passphrase

A page that asks for a long passphrase every visit is painful on a phone. Storing the passphrase in the browser is worse: anything that can read the storage can read the secret.

## The approach

After the first unlock, the page derives the AES key with `extractable: false` and stores that `CryptoKey` object in IndexedDB. The browser can use such a key to decrypt, but no code, including the page's own, can read the key material back out.

```js
crypto.subtle.deriveKey(
  { name: "PBKDF2", salt, iterations, hash: "SHA-256" },
  base, { name: "AES-GCM", length: 256 },
  false,            // not extractable
  ["decrypt"]
);
```

## The trade-off I had to accept

To reuse one stored key for every new file, the salt has to be fixed for the project. It is not secret and it is unique per repository. Every file still gets its own random IV, which is the value that must never repeat.

## A non-extractable key is still usable

If hostile script ran on the same origin it could ask the browser to decrypt with that key. So the key store is only half the defence. The other half is the Content Security Policy that stops hostile script from running at all, and a Lock button that deletes the key.
"""),
]
# ================================================================================

ABOUT = (
    "I am a cybersecurity student who learns by building. Every project here is something I can run, "
    "break and explain, and each one is on the defender's side: spotting attacks in data, triaging alerts, "
    "segmenting networks and protecting information with encryption."
)
METHOD = "Everything uses synthetic or self-owned data, and I only test on systems I am authorized to."
NOW = [
    ("studying", "the HTB SOC Analyst path and the CDSA exam (I built the study tracker for it)"),
    ("building", "ACLs, port security and OSPF for securewave-net"),
    ("writing", "short writeups on the security decisions behind my projects"),
]
TOOLBOX = [
    ("languages", "`Python` `JavaScript` `HTML` `CSS`"),
    ("web / data", "`FastAPI` `Flask` `React` `SQLite` `SQLAlchemy` `Chart.js`"),
    ("security", "`MITRE ATT&CK` `AES-256-GCM` `PBKDF2` `CSP` `WebCrypto` `VLANs` `DMZ` `AAA`"),
    ("tools", "`Kali Linux` `Cisco Packet Tracer` `GitHub Actions` `pytest`"),
]

START, END = "<!-- stats:start -->", "<!-- stats:end -->"


def get(url: str, token: str | None = None) -> bytes:
    h = {"User-Agent": "profile-readme-builder", "Accept": "application/vnd.github+json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=30) as r:
        return r.read()


def fetch_stats() -> dict:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    u = json.loads(get(f"https://api.github.com/users/{USER}", token))
    repos = json.loads(get(f"https://api.github.com/users/{USER}/repos?per_page=100&sort=pushed", token))
    events = []
    for page in (1, 2, 3):
        try:
            chunk = json.loads(get(f"https://api.github.com/users/{USER}/events/public?per_page=100&page={page}", token))
        except Exception:
            break
        events += chunk
        if len(chunk) < 100:
            break
    return {"user": u, "repos": repos, "events": events}


def avatar_data_uri(url: str) -> str | None:
    try:
        req = urllib.request.Request(url + ("&" if "?" in url else "?") + "s=220", headers={"User-Agent": "profile-readme-builder"})
        with urllib.request.urlopen(req, timeout=30) as r:
            ctype = r.headers.get("Content-Type", "image/png").split(";")[0]
            return f"data:{ctype};base64," + base64.b64encode(r.read()).decode()
    except Exception:
        return None


def build_avatar(uri: str | None) -> str:
    """The profile picture in a circle with a blue ring, next to the Kali dragon."""
    raw = (Path(__file__).parent / "kali-dragon-icon.svg").read_text(encoding="utf-8")
    inner = re.search(r"<svg[^>]*>(.*)</svg>", raw, re.S).group(1)
    assert "<script" not in inner.lower()
    cx, cy, r = 110, 110, 82
    if uri:
        pic = (f'<defs><clipPath id="av"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath></defs>'
               f'<image href="{uri}" x="{cx - r}" y="{cy - r}" width="{2 * r}" height="{2 * r}" clip-path="url(#av)" preserveAspectRatio="xMidYMid slice"/>')
    else:
        pic = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#0f1a2a"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="440" height="220" viewBox="0 0 440 220" role="img" aria-label="Profile picture in a circle next to the Kali Linux dragon">'
            f'<circle cx="{cx}" cy="{cy}" r="{r + 9}" fill="none" stroke="#367BF0" stroke-width="3"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r + 17}" fill="none" stroke="#367BF0" stroke-width="1" opacity=".4"/>'
            f'{pic}<svg x="236" y="22" width="190" height="155" viewBox="0 0 451.14 367.25">{inner}</svg></svg>')


def build_stats_block(data: dict) -> str:
    import datetime as dt
    u, repos, events = data["user"], data["repos"], data["events"]
    mine = [r for r in repos if not r.get("fork") and r["name"] not in HIDE_REPOS]
    stars = sum(r.get("stargazers_count", 0) for r in mine)
    langs: dict[str, int] = {}
    for r in mine:
        if r.get("language"):
            langs[r["language"]] = langs.get(r["language"], 0) + 1
    total = sum(langs.values()) or 1
    counts: dict[str, int] = {}
    for ev in events:
        counts[ev["created_at"][:10]] = counts.get(ev["created_at"][:10], 0) + 1

    today = dt.date.today()
    start = today - dt.timedelta(days=today.weekday() + 12 * 7)
    shades = " ░▒▓█"
    grid = [[" "] * 13 for _ in range(7)]
    for i in range(13 * 7):
        d = start + dt.timedelta(days=i)
        if d > today:
            continue
        n = counts.get(d.isoformat(), 0)
        grid[i % 7][i // 7] = "·" if n == 0 else shades[1] if n < 3 else shades[2] if n < 6 else shades[3] if n < 10 else shades[4]
    days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    act = "\n".join(f"{days[r]}  " + " ".join(grid[r]) for r in range(7))

    lk = sorted(langs, key=lambda k: -langs[k])
    width = max((len(l) for l in lk), default=0)
    lang_lines = "\n".join(f"{l:<{width}}  {'█' * round(10 * langs[l] / total):<10}  {round(100 * langs[l] / total):>3}%" for l in lk)

    top = sorted(mine, key=lambda r: r.get("pushed_at", ""), reverse=True)[:6]
    rows = "\n".join(
        f'| [{r["name"]}]({GH + r["name"]}) | {(r.get("description") or "").strip().replace("|", "/") or "-"} | {r.get("language") or "-"} | {r.get("pushed_at", "")[:10]} |'
        for r in top)
    name = u.get("name") or u["login"]
    return f"""{START}
```console
┌──(kali㉿kali)-[~/stats]
└─$ stats --github {u["login"]}

user       {name}
repos      {u["public_repos"]} public
followers  {u["followers"]}
following  {u["following"]}
stars      {stars}
```

**Public activity, last 13 weeks** <sub>(one square per day, darker means more)</sub>

```text
{act}
```

**Languages** <sub>by repository count</sub>

```text
{lang_lines}
```

**Recently updated**

| repository | about | language | updated |
|---|---|---|---|
{rows}

<sub>This block is rebuilt every day by a small GitHub Action from public data only. Private repositories are never shown. Last refresh: {today.isoformat()}.</sub>
{END}"""


def build_readme(stats_block: str) -> str:
    nav = " · ".join(f"[{k}](#{k})" for k in ["home", "about", "projects", "focus", "blog", "stats"])
    prow = "\n".join(
        f'| **[{p["slug"]}]({GH + p["repo"]})** | {p["tagline"].rstrip(".")} | {" · ".join(p["stack"][:4])} |' if p["repo"]
        else f'| **{p["slug"]}** <sub>(private)</sub> | {p["tagline"].rstrip(".")} | {" · ".join(p["stack"][:4])} |'
        for p in PROJECTS)
    details = []
    for p in PROJECTS:
        lk = [f'[code]({GH + p["repo"]})'] if p["repo"] else ["private source"]
        if p.get("extra_link"):
            lk.append(f'[{p["extra_link"][0]}]({p["extra_link"][1]})')
        mods = "\n".join(("├── " if i < len(p["modules"]) - 1 else "└── ") + f"{m[0]:<13}{m[1]}" for i, m in enumerate(p["modules"]))
        details.append(
            f'<details>\n<summary><b>{p["slug"]}/</b> &nbsp;·&nbsp; modules and notes</summary>\n\n'
            f'**Stack:** {" · ".join(p["stack"])}<br>**Status:** {p["status"]}<br>**Links:** {" · ".join(lk)}\n\n'
            f'```console\n┌──(kali㉿kali)-[~/projects/{p["slug"]}]\n└─$ tree --modules\n.\n{mods}\n```\n\n{p["note"]}\n\n</details>\n')
    focus = "\n".join(f"| `{k}` | {v} |" for k, v in FOCUS)
    now = "\n".join(f"| `{k}` | {v} |" for k, v in NOW)
    tools = "\n".join(f"| `{k}` | {v} |" for k, v in TOOLBOX)
    blog = "\n".join(f'| {p["date"]} | **[{p["title"]}](blog/{p["slug"]}.md)** | {p["desc"]} | {" ".join("`" + t + "`" for t in p["tags"])} |' for p in POSTS)
    return f"""<div align="center">

<a name="home"></a>
<img src="assets/avatar.svg" width="360" alt="Profile picture in a circle next to the Kali Linux dragon">

# {USER}

**Cybersecurity student · Kali Linux · detection, SOC triage and secure design**

{nav}

</div>

```console
┌──(kali㉿kali)-[~]
└─$ neofetch

{USER}@kali
{"-" * (len(USER) + 5)}
os        Kali Linux
role      cybersecurity student
focus     detection · SOC triage · secure design
projects  {len(PROJECTS)} ({sum(1 for p in PROJECTS if p["repo"])} public, {sum(1 for p in PROJECTS if not p["repo"])} private)
method    authorized targets and synthetic data only
```

## about

```console
┌──(kali㉿kali)-[~/about]
└─$ cat about.md
```

{ABOUT}

{METHOD}

**Right now**

| | |
|---|---|
{now}

**Toolbox**

| | |
|---|---|
{tools}

## projects

```console
┌──(kali㉿kali)-[~/projects]
└─$ ls -l
```

| project | what it does | stack |
|---|---|---|
{prow}

Open any project below to see its modules, its status and its links.

{chr(10).join(details)}
## focus

```console
┌──(kali㉿kali)-[~/focus]
└─$ cat principles.txt
```

| | |
|---|---|
{focus}

## blog

```console
┌──(kali㉿kali)-[~/blog]
└─$ ls -t
```

| date | writeup | summary | tags |
|---|---|---|---|
{blog}

## stats

{stats_block}

```console
┌──(kali㉿kali)-[~]
└─$ _
```
"""


def stats_only() -> None:
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    block = build_stats_block(fetch_stats())
    if START not in text or END not in text:
        sys.exit("stats markers not found in README.md")
    new = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _m: block, text, flags=re.S)
    readme.write_text(new, encoding="utf-8")
    print("updated stats block in README.md", file=sys.stderr)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stats-only", action="store_true")
    args = ap.parse_args()
    if args.stats_only:
        return stats_only()
    ASSETS.mkdir(exist_ok=True)
    data = fetch_stats()
    (ASSETS / "avatar.svg").write_text(build_avatar(avatar_data_uri(data["user"].get("avatar_url", ""))), encoding="utf-8")
    (ROOT / "blog").mkdir(exist_ok=True)
    for p in POSTS:
        (ROOT / "blog" / f"{p['slug']}.md").write_text(p["body"], encoding="utf-8")
    (ROOT / "README.md").write_text(build_readme(build_stats_block(data)), encoding="utf-8")
    print("wrote assets/avatar.svg, blog pages and README.md", file=sys.stderr)


if __name__ == "__main__":
    main()
