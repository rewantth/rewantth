#!/usr/bin/env python3
"""Builds the profile README: Kali terminal-window pictures (SVG) plus the same content as real text.

    python tools/build.py               # everything (needs internet for the avatar and GitHub stats)
    python tools/build.py --stats-only  # only the stats picture and the stats text (what the daily GitHub job runs)

Edit the CONTENT section, then run it again. GitHub cannot run scripts in a README, so each
terminal "window" is a picture, each tab is a link, and the text below it is the readable version.
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

W = 1000
TABS = [("home", "home"), ("about", "about"), ("projects", "projects"), ("focus", "focus"), ("blog", "blog"), ("stats", "stats")]
FONT = '"JetBrains Mono","Fira Code","Cascadia Code",Consolas,Menlo,"DejaVu Sans Mono",monospace'
STYLE = (
    "text{font-family:" + FONT + ";font-size:14px;white-space:pre}"
    ".k{fill:#367BF0}.g{fill:#00ff9c}.w{fill:#e6edf3}.d{fill:#7d8da3}.c{fill:#00e5ff}.r{fill:#ff4d4d}.y{fill:#ffd866}.pu{fill:#b48cff}"
    ".bold{font-weight:700}.s13{font-size:13px}.s12{font-size:12px}.s11{font-size:11px}.s15{font-size:15px}.s18{font-size:18px}.s24{font-size:24px}"
    ".l{opacity:0;animation:show .01s linear forwards}@keyframes show{to{opacity:1}}"
    ".cur{animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:0}}"
    ".sweep{animation:sweep 7s linear infinite}@keyframes sweep{from{transform:translateY(-140px)}to{transform:translateY(900px)}}"
    ".pulse{animation:pulse 2.6s ease-in-out infinite}@keyframes pulse{0%,100%{opacity:.5}50%{opacity:1}}"
    "@media (prefers-reduced-motion:reduce){.l{animation-duration:0s;animation-delay:0s!important}.cur,.sweep,.pulse{animation:none}.sweep{display:none}}"
)


def e(s) -> str:
    return escape(str(s))


def clip(s: str, n: int) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"


def wrap(text: str, n: int) -> list[str]:
    lines, cur = [], ""
    for w in text.split():
        if cur and len(cur) + 1 + len(w) > n:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}" if cur else w
    if cur:
        lines.append(cur)
    return lines


def dragon_inner() -> str:
    raw = (Path(__file__).parent / "kali-dragon-icon.svg").read_text(encoding="utf-8")
    inner = re.search(r"<svg[^>]*>(.*)</svg>", raw, re.S).group(1)
    assert "<script" not in inner.lower()
    return inner


def get(url: str, token: str | None = None) -> bytes:
    h = {"User-Agent": "profile-readme-builder", "Accept": "application/vnd.github+json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=30) as r:
        return r.read()


def avatar_data_uri(url: str) -> str | None:
    try:
        req = urllib.request.Request(url + ("&" if "?" in url else "?") + "s=220", headers={"User-Agent": "profile-readme-builder"})
        with urllib.request.urlopen(req, timeout=30) as r:
            ctype = r.headers.get("Content-Type", "image/png").split(";")[0]
            return f"data:{ctype};base64," + base64.b64encode(r.read()).decode()
    except Exception:
        return None


def avatar(cx: float, cy: float, r: float, uri: str | None, uid: str) -> str:
    """The profile picture in a circle with a blue glow ring."""
    ring = f'<circle cx="{cx}" cy="{cy}" r="{r + 5}" fill="none" stroke="#367BF0" stroke-width="3" opacity=".9"/><circle cx="{cx}" cy="{cy}" r="{r + 12}" fill="none" stroke="#367BF0" stroke-width="1" opacity=".35" class="pulse"/>'
    if uri:
        return (f'<defs><clipPath id="av{uid}"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath></defs>{ring}'
                f'<image href="{uri}" x="{cx - r}" y="{cy - r}" width="{2 * r}" height="{2 * r}" clip-path="url(#av{uid})" preserveAspectRatio="xMidYMid slice"/>')
    return f'{ring}<circle cx="{cx}" cy="{cy}" r="{r}" fill="#0f1a2a"/><text x="{cx}" y="{cy + 10}" text-anchor="middle" class="c bold s24">{e(USER[0].upper())}</text>'


def prompt(x, y, path, cmd) -> str:
    return (f'<text x="{x}" y="{y}"><tspan class="k">┌──(</tspan><tspan class="c bold">{USER}㉿kali</tspan><tspan class="k">)-[</tspan><tspan class="w bold">{e(path)}</tspan><tspan class="k">]</tspan></text>'
            f'<text x="{x}" y="{y + 20}"><tspan class="k">└─</tspan><tspan class="c bold">$ </tspan><tspan class="w">{e(cmd)}</tspan></text>')


def reveal(i: int, svg: str, step: float = 0.18) -> str:
    return f'<g class="l" style="animation-delay:{round(0.2 + i * step, 2)}s">{svg}</g>'


def chrome(active: str, path: str, body: str, content_h: int, *, wx: int = 50, ww: int = 900, icons: str = "", defs: str = "", alt: str = "") -> str:
    wy, titleh = 62, 38
    wh = titleh + content_h + 20
    H = wy + wh + 24 + 44
    tabs, x = "", 118
    for key, label in TABS:
        w = int(len(label) * 8.6 + 46)
        if key == active:
            tabs += f'<rect x="{x}" y="6" width="{w}" height="28" rx="7" fill="#367BF0"/><text x="{x + 14}" y="25" style="font-size:13px" fill="#04101f" class="bold">{TABS.index((key, label)) + 1} {e(label)}</text>'
        else:
            tabs += f'<text x="{x + 14}" y="25" class="d" style="font-size:13px">{TABS.index((key, label)) + 1} {e(label)}</text>'
        x += w + 6
    dots = "".join(f'<circle cx="{W - 96 + i * 16}" cy="20" r="4.5" fill="{c}"/>' for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f", "#367BF0", "#b48cff"]))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{e(alt or path)}">
<title>{e(alt or path)}</title>
<defs>
<style>{STYLE}</style>
<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#060a11"/><stop offset="1" stop-color="#02040a"/></linearGradient>
<radialGradient id="g1" cx="80%" cy="88%" r="60%"><stop offset="0" stop-color="#367BF0" stop-opacity=".26"/><stop offset="1" stop-color="#367BF0" stop-opacity="0"/></radialGradient>
<radialGradient id="g2" cx="10%" cy="6%" r="55%"><stop offset="0" stop-color="#00ff9c" stop-opacity=".08"/><stop offset="1" stop-color="#00ff9c" stop-opacity="0"/></radialGradient>
<pattern id="grid" width="46" height="46" patternUnits="userSpaceOnUse"><path d="M46 0H0V46" fill="none" stroke="#367BF0" stroke-opacity=".09"/></pattern>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="2" fill="#000" opacity=".26"/></pattern>
<linearGradient id="bar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#00ff9c" stop-opacity="0"/><stop offset=".55" stop-color="#00ff9c" stop-opacity=".09"/><stop offset="1" stop-color="#00ff9c" stop-opacity="0"/></linearGradient>
<clipPath id="win"><rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" rx="12"/></clipPath>
{defs}
</defs>
<rect width="{W}" height="{H}" fill="url(#bg)"/><rect width="{W}" height="{H}" fill="url(#g1)"/><rect width="{W}" height="{H}" fill="url(#g2)"/><rect width="{W}" height="{H}" fill="url(#grid)"/>
<rect width="{W}" height="40" fill="#04080e" opacity=".92"/><path d="M0 40H{W}" stroke="#1b2a3f"/>
<text x="18" y="25" class="g bold s15">{USER}</text>{tabs}{dots}
{icons}
<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" rx="12" fill="#080e17" fill-opacity=".94" stroke="#1b2a3f"/>
<g clip-path="url(#win)"><rect x="{wx}" y="{wy}" width="{ww}" height="{titleh}" fill="#0d141d"/>
<circle cx="{wx + 22}" cy="{wy + 19}" r="6" fill="#ff5f56"/><circle cx="{wx + 42}" cy="{wy + 19}" r="6" fill="#ffbd2e"/><circle cx="{wx + 62}" cy="{wy + 19}" r="6" fill="#27c93f"/>
<text x="{wx + ww // 2}" y="{wy + 24}" text-anchor="middle" class="d s13">{USER}@kali: {e(path)}</text>
{body}
<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" fill="url(#scan)"/><rect class="sweep" x="{wx}" y="{wy}" width="{ww}" height="130" fill="url(#bar)"/></g>
<rect y="{H - 44}" width="{W}" height="44" fill="#04080e" opacity=".94"/><path d="M0 {H - 44}H{W}" stroke="#1b2a3f"/>
<rect x="14" y="{H - 38}" width="132" height="30" rx="8" fill="#367BF0" fill-opacity=".14" stroke="#367BF0"/><text x="30" y="{H - 18}" class="w s13">zsh ~ kali</text>
<text x="{W - 16}" y="{H - 18}" text-anchor="end" class="d s13">{USER}@kali</text>
</svg>
'''


def icon(x, y, kind, label) -> str:
    shapes = {
        "folder": '<path d="M4 12a3 3 0 0 1 3-3h12l4 5h18a3 3 0 0 1 3 3v21a3 3 0 0 1-3 3H7a3 3 0 0 1-3-3z" fill="#367BF0"/><path d="M4 18h40v18a3 3 0 0 1-3 3H7a3 3 0 0 1-3-3z" fill="#4f93ff"/>',
        "file": '<path d="M10 4h20l10 10v28a2 2 0 0 1-2 2H10a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z" fill="#1b2a3f" stroke="#367BF0" stroke-width="2"/><path d="M16 24h16M16 30h16M16 36h10" stroke="#00e5ff" stroke-width="2" stroke-linecap="round"/>',
        "chart": '<rect x="5" y="6" width="38" height="36" rx="5" fill="#0d141d" stroke="#367BF0" stroke-width="2"/><path d="M13 34V24M21 34V16M29 34V27M37 34V12" stroke="#00e5ff" stroke-width="4" stroke-linecap="round"/>',
        "term": '<rect x="4" y="8" width="40" height="32" rx="5" fill="#0d141d" stroke="#367BF0" stroke-width="2"/><path d="M12 20l7 5-7 5M23 31h12" stroke="#00ff9c" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>',
    }
    return f'<g transform="translate({x} {y})">{shapes[kind]}<text x="24" y="66" text-anchor="middle" class="w s12">{e(label)}</text></g>'


# ---------------------------------- sections ----------------------------------
def build_home(av_uri: str | None) -> str:
    wx, ww = 110, 780
    cx, cy = wx + 24, 62 + 38 + 12
    inner = dragon_inner()
    rows = [("OS", "Kali GNU/Linux Rolling"), ("Shell", "zsh"), ("Focus", "detection · secure design"),
            ("Projects", str(len(PROJECTS))), ("Source", f"{sum(p['visibility'] == 'public' for p in PROJECTS)} public · {sum(p['visibility'] == 'private' for p in PROJECTS)} private"), ("Writeups", str(len(POSTS)))]
    info = f'<text x="{cx + 390}" y="{cy + 92}" class="s15"><tspan class="c bold">{USER}</tspan><tspan class="w">@</tspan><tspan class="c bold">kali</tspan></text><text x="{cx + 390}" y="{cy + 110}" class="d">-------------</text>'
    for i, (k, v) in enumerate(rows):
        y = cy + 138 + i * 22
        info += f'<text x="{cx + 390}" y="{y}" class="k bold s13">{e(k)}</text><text x="{cx + 480}" y="{y}" class="w s13">{e(v)}</text>'
    body = (reveal(0, prompt(cx, cy + 14, "~", "neofetch"))
            + reveal(2, f'<circle cx="{cx + 100}" cy="{cy + 160}" r="120" fill="url(#g1)" class="pulse"/><svg x="{cx + 6}" y="{cy + 84}" width="190" height="155" viewBox="0 0 451.14 367.25">{inner}</svg>')
            + reveal(3, avatar(cx + 292, cy + 150, 52, av_uri, "h") + f'<text x="{cx + 292}" y="{cy + 232}" text-anchor="middle" class="c bold s13">@{USER}</text>')
            + reveal(4, info)
            + reveal(5, "".join(f'<rect x="{cx + 390 + i * 30}" y="{cy + 274}" width="30" height="14" fill="{c}"/>' for i, c in enumerate(["#1f2430", "#ff6b6b", "#7ee787", "#ffd866", "#367BF0", "#b48cff", "#00e5ff", "#e6edf3"])))
            + reveal(6, f'<text x="{cx}" y="{cy + 318}" class="d"># break things legally. fix them properly.</text>')
            + reveal(8, f'<text x="{cx}" y="{cy + 346}"><tspan class="k">└─</tspan><tspan class="c bold">$ </tspan></text><rect class="cur" x="{cx + 40}" y="{cy + 333}" width="9" height="16" fill="#00ff9c"/>'))
    icons = (icon(18, 76, "folder", "projects/") + icon(18, 166, "folder", "blog/") + icon(18, 256, "chart", "stats")
             + icon(W - 66, 76, "file", "focus.md") + icon(W - 66, 166, "term", "terminal"))
    return chrome("home", "~", body, 372, wx=wx, ww=ww, icons=icons, alt=f"Kali terminal running neofetch with the Kali dragon and the profile picture of {USER} in a circle")


def build_projects() -> str:
    wx, ww = 50, 900
    cx, cy = wx + 24, 62 + 38 + 12
    cw, ch, gap = 416, 140, 14
    body = reveal(0, prompt(cx, cy + 14, "~/projects", "ls -1"))
    for i, p in enumerate(PROJECTS):
        x = cx + (i % 2) * (cw + gap)
        y = cy + 62 + (i // 2) * (ch + gap)
        tag = "public" if p["visibility"] == "public" else "private"
        tagc = "c" if tag == "public" else "y"
        desc = wrap(p["tagline"], 49)[:3]
        stack = clip(" · ".join(p["stack"]), 50)
        card = (f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="10" fill="#ffffff" fill-opacity=".03" stroke="#1b2a3f"/>'
                f'<text x="{x + 16}" y="{y + 26}" class="w bold s15">{e(p["slug"])}/</text><text x="{x + cw - 16}" y="{y + 26}" text-anchor="end" class="{tagc} s12">{tag}</text>'
                + "".join(f'<text x="{x + 16}" y="{y + 48 + j * 17}" class="d s13">{e(line)}</text>' for j, line in enumerate(desc))
                + f'<text x="{x + 16}" y="{y + 112}" class="c s12">{e(stack)}</text><text x="{x + 16}" y="{y + 130}" class="g s12">● {e(clip(p["status"], 52))}</text>')
        body += reveal(1 + i, card, 0.14)
    rows = (len(PROJECTS) + 1) // 2
    return chrome("projects", "~/projects", body, 62 + rows * (ch + gap) + 6, wx=wx, ww=ww, alt="Kali terminal listing six security projects as cards")


def build_focus() -> str:
    wx, ww = 50, 900
    cx, cy = wx + 24, 62 + 38 + 12
    body = reveal(0, prompt(cx, cy + 14, "~", "cat focus.md")) + reveal(1, f'<text x="{cx}" y="{cy + 76}" class="g bold s15"># focus</text>')
    y = cy + 108
    for i, (k, v) in enumerate(FOCUS):
        lines = wrap(v, 80)
        seg = f'<text x="{cx}" y="{y}" class="k bold">{e(k)}</text>' + "".join(f'<text x="{cx + 140}" y="{y + j * 20}" class="w">{e(l)}</text>' for j, l in enumerate(lines))
        body += reveal(2 + i, seg)
        y += 20 * len(lines) + 14
    body += reveal(7, f'<text x="{cx}" y="{y + 10}"><tspan class="k">└─</tspan><tspan class="c bold">$ </tspan></text><rect class="cur" x="{cx + 40}" y="{y - 3}" width="9" height="16" fill="#00ff9c"/>')
    return chrome("focus", "~", body, int(y - cy + 34), wx=wx, ww=ww, alt="Kali terminal showing what the projects are about: detection, defence, explainability and method")


def build_blog() -> str:
    wx, ww = 50, 900
    cx, cy = wx + 24, 62 + 38 + 12
    body = reveal(0, prompt(cx, cy + 14, "~/blog", "ls -l")) + reveal(1, f'<text x="{cx}" y="{cy + 76}" class="d">total {len(POSTS)}</text>')
    y = cy + 104
    for i, p in enumerate(sorted(POSTS, key=lambda x: x["date"], reverse=True)):
        seg = (f'<text x="{cx}" y="{y}" class="s13"><tspan class="d">drwxr-xr-x  --</tspan><tspan class="y">  {e(p["date"])}</tspan><tspan class="c bold">  {e(p["slug"])}/</tspan></text>'
               f'<text x="{cx + 24}" y="{y + 22}" class="w bold">{e(p["title"])}</text>'
               f'<text x="{cx + 24}" y="{y + 42}" class="d s13">{e(p["desc"])}</text>'
               f'<text x="{cx + 24}" y="{y + 62}" class="pu s12">{e(" ".join("#" + t for t in p["tags"]))}</text>')
        body += reveal(2 + i, seg)
        y += 92
    return chrome("blog", "~/blog", body, int(y - cy + 6), wx=wx, ww=ww, alt="Kali terminal listing two writeups about the inbox-dashboard project")


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


def build_stats(data: dict) -> str:
    import datetime as dt
    u, repos, events = data["user"], data["repos"], data["events"]
    mine = [r for r in repos if not r.get("fork") and r["name"] not in HIDE_REPOS]
    stars = sum(r.get("stargazers_count", 0) for r in mine)
    langs: dict[str, int] = {}
    for r in mine:
        if r.get("language"):
            langs[r["language"]] = langs.get(r["language"], 0) + 1
    total = sum(langs.values()) or 1
    lcolors = {"Python": "#3572a5", "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "Go": "#00add8", "Java": "#b07219", "C": "#8a8a8a", "C++": "#f34b7d", "Shell": "#89e051", "PowerShell": "#5391fe", "HTML": "#e34c26", "CSS": "#a278f0"}
    counts: dict[str, int] = {}
    for ev in events:
        counts[ev["created_at"][:10]] = counts.get(ev["created_at"][:10], 0) + 1
    wx, ww = 50, 900
    cx, cy = wx + 24, 62 + 38 + 12
    uri = avatar_data_uri(u.get("avatar_url", "")) if u.get("avatar_url") else None
    body = reveal(0, prompt(cx, cy + 14, "~/stats", "stats --github"))
    name = u.get("name") or u["login"]
    head = (avatar(cx + 56, cy + 128, 50, uri, "s")
            + f'<text x="{cx + 132}" y="{cy + 112}" class="w bold s18">{e(name)}</text><text x="{cx + 132}" y="{cy + 134}" class="c s13">github.com/{e(u["login"])}</text>'
            + f'<text x="{cx + 132}" y="{cy + 156}" class="g s12">● live · public data only · refreshed daily</text>')
    for i, (n, label) in enumerate([(u["public_repos"], "public repos"), (u["followers"], "followers"), (u["following"], "following"), (stars, "stars")]):
        x = cx + 440 + i * 108
        head += f'<text x="{x}" y="{cy + 124}" class="w bold s24">{n}</text><text x="{x}" y="{cy + 144}" class="d s11">{e(label.upper())}</text>'
    body += reveal(1, head)
    today = dt.date.today()
    start = today - dt.timedelta(days=today.weekday() + 12 * 7)
    cells = ""
    gy = cy + 226
    for i in range(13 * 7):
        d = start + dt.timedelta(days=i)
        if d > today:
            continue
        n = counts.get(d.isoformat(), 0)
        col = "#0f1a2a" if n == 0 else "#0d4a8a" if n < 3 else "#367BF0" if n < 6 else "#00e5ff"
        cells += f'<rect x="{cx + (i // 7) * 20}" y="{gy + (i % 7) * 20}" width="16" height="16" rx="3" fill="{col}"><title>{d.isoformat()}: {n} public events</title></rect>'
    act = f'<text x="{cx}" y="{cy + 208}" class="k bold s13">public activity, last 13 weeks</text>{cells}<text x="{cx}" y="{gy + 156}" class="d s11">only public events. private repositories are never shown.</text>'
    lk = sorted(langs, key=lambda k: -langs[k])
    lx, bw = cx + 330, 520
    bar, x = "", lx
    for l in lk:
        w = bw * langs[l] / total
        bar += f'<rect x="{x:.1f}" y="{cy + 220}" width="{w:.1f}" height="12" fill="{lcolors.get(l, "#6f8199")}"/>'
        x += w
    legend = "".join(f'<rect x="{lx + (i % 3) * 176}" y="{cy + 252 + (i // 3) * 22}" width="9" height="9" rx="2" fill="{lcolors.get(l, "#6f8199")}"/><text x="{lx + 15 + (i % 3) * 176}" y="{cy + 261 + (i // 3) * 22}" class="d s12">{e(l)} {round(langs[l] / total * 100)}%</text>' for i, l in enumerate(lk))
    body += reveal(2, act) + reveal(3, f'<text x="{lx}" y="{cy + 208}" class="k bold s13">languages <tspan class="d">by repository count</tspan></text><clipPath id="lb"><rect x="{lx}" y="{cy + 220}" width="{bw}" height="12" rx="6"/></clipPath><g clip-path="url(#lb)">{bar}</g>{legend}')
    top = sorted(mine, key=lambda r: r.get("pushed_at", ""), reverse=True)[:6]
    cw, ch, gap = 276, 92, 14
    body += reveal(4, f'<text x="{cx}" y="{cy + 408}" class="k bold s13">recent repositories</text>')
    for i, r in enumerate(top):
        x = cx + (i % 3) * (cw + gap)
        y = cy + 420 + (i // 3) * (ch + gap)
        d = wrap(r.get("description") or "no description", 33)[:2]
        card = (f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="9" fill="#ffffff" fill-opacity=".03" stroke="#1b2a3f"/>'
                f'<text x="{x + 14}" y="{y + 24}" class="w bold s13">{e(clip(r["name"], 26))}</text><text x="{x + cw - 14}" y="{y + 24}" text-anchor="end" class="y s12">★ {r.get("stargazers_count", 0)}</text>'
                + "".join(f'<text x="{x + 14}" y="{y + 44 + j * 16}" class="d s12">{e(line)}</text>' for j, line in enumerate(d))
                + f'<text x="{x + 14}" y="{y + 82}" class="c s11">{e(r.get("language") or "")}</text>')
        body += reveal(5 + i, card, 0.1)
    rows = (len(top) + 2) // 3
    ch_total = 420 + rows * (ch + gap) - cy + cy
    return chrome("stats", "~/stats", body, 420 + rows * (ch + gap) - 4 - 0, wx=wx, ww=ww, alt=f"Kali terminal showing GitHub stats for {USER}: profile picture, repositories, activity and languages")



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




def build_about() -> str:
    wx, ww = 50, 900
    cx, cy = wx + 24, 62 + 38 + 12
    body = reveal(0, prompt(cx, cy + 14, "~", "cat about.md")) + reveal(1, f'<text x="{cx}" y="{cy + 76}" class="g bold s15"># about</text>')
    y = cy + 104
    for line in wrap(ABOUT, 92) + [""] + wrap(METHOD, 92):
        body += reveal(2, f'<text x="{cx}" y="{y}" class="w">{e(line)}</text>', 0)
        y += 20
    y += 12
    body += reveal(3, f'<text x="{cx}" y="{y}" class="k bold">## right now</text>')
    y += 26
    for i, (k, v) in enumerate(NOW):
        lines = wrap(v, 74)
        body += reveal(4 + i, f'<text x="{cx}" y="{y}" class="c bold">{e(k)}</text>' + "".join(f'<text x="{cx + 140}" y="{y + j * 20}" class="w">{e(l)}</text>' for j, l in enumerate(lines)))
        y += 20 * len(lines) + 6
    y += 14
    body += reveal(7, f'<text x="{cx}" y="{y}" class="k bold">## toolbox</text>')
    y += 26
    for i, (k, v) in enumerate(TOOLBOX):
        lines = wrap(v.replace("`", ""), 74)
        body += reveal(8 + i, f'<text x="{cx}" y="{y}" class="c bold">{e(k)}</text>' + "".join(f'<text x="{cx + 140}" y="{y + j * 20}" class="w">{e(l)}</text>' for j, l in enumerate(lines)))
        y += 20 * len(lines) + 6
    body += reveal(12, f'<text x="{cx}" y="{y + 14}"><tspan class="k">└─</tspan><tspan class="c bold">$ </tspan></text><rect class="cur" x="{cx + 40}" y="{y + 1}" width="9" height="16" fill="#00ff9c"/>')
    return chrome("about", "~", body, int(y - cy + 42), wx=wx, ww=ww, alt="Kali terminal showing the about page: what I study, what I build and my toolbox")


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



def text_details(title: str, md: str) -> str:
    return f"<details>\n<summary>{title}</summary>\n\n{md}\n\n</details>\n"


def build_readme(stats_block: str) -> str:
    nav = " · ".join(f"[{k}](#{k})" for k, _ in TABS)
    img = lambda k, alt: f'<a name="{k}"></a>\n<img src="assets/{k}.svg" alt="{alt}" width="100%">\n'
    links = " · ".join(f'[{p["slug"]}]({GH + p["repo"]})' if p["repo"] else f'{p["slug"]} <sub>(private)</sub>' for p in PROJECTS)
    details = []
    for p in PROJECTS:
        lk = [f'[code]({GH + p["repo"]})'] if p["repo"] else ["private source"]
        if p.get("extra_link"):
            lk.append(f'[{p["extra_link"][0]}]({p["extra_link"][1]})')
        mods = "\n".join(("├── " if i < len(p["modules"]) - 1 else "└── ") + f"{m[0]:<13}{m[1]}" for i, m in enumerate(p["modules"]))
        details.append(
            f'<details>\n<summary><b>{p["slug"]}/</b> &nbsp;·&nbsp; {p["tagline"]}</summary>\n\n'
            f'**Stack:** {" · ".join(p["stack"])}<br>**Status:** {p["status"]}<br>**Links:** {" · ".join(lk)}\n\n'
            f'```console\n┌──(kali㉿kali)-[~/projects/{p["slug"]}]\n└─$ tree --modules\n.\n{mods}\n```\n\n{p["note"]}\n\n</details>\n')
    focus = "\n".join(f"| `{k}` | {v} |" for k, v in FOCUS)
    now = "\n".join(f"| `{k}` | {v} |" for k, v in NOW)
    tools = "\n".join(f"| `{k}` | {v} |" for k, v in TOOLBOX)
    blog = "\n".join(f'| {p["date"]} | **[{p["title"]}](blog/{p["slug"]}.md)** | {p["desc"]} |' for p in POSTS)
    about_md = f"{ABOUT}\n\n{METHOD}\n\n| right now | |\n|---|---|\n{now}\n\n| toolbox | |\n|---|---|\n{tools}"
    out = [
        f'<div align="center">\n\n{nav}\n\n</div>\n',
        img("home", "Kali terminal running neofetch with the Kali dragon and the profile picture in a circle"),
        img("about", "Kali terminal showing the about page"),
        text_details("about, as text", about_md),
        img("projects", "Kali terminal listing six security projects as cards"),
        f"**Code:** {links}\n",
        *details,
        img("focus", "Kali terminal showing what the projects are about"),
        text_details("focus, as text", f"| | |\n|---|---|\n{focus}"),
        img("blog", "Kali terminal listing two writeups"),
        f"| date | writeup | summary |\n|---|---|---|\n{blog}\n",
        img("stats", "Kali terminal showing GitHub stats: profile picture, repositories, activity and languages"),
        text_details("stats, as text", stats_block),
    ]
    return "\n".join(out)


def stats_only() -> None:
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    data = fetch_stats()
    (ASSETS / "stats.svg").write_text(build_stats(data), encoding="utf-8")
    if START not in text or END not in text:
        sys.exit("stats markers not found in README.md")
    block = build_stats_block(data)
    readme.write_text(re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _m: block, text, flags=re.S), encoding="utf-8")
    print("updated assets/stats.svg and the stats text in README.md", file=sys.stderr)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stats-only", action="store_true")
    args = ap.parse_args()
    if args.stats_only:
        return stats_only()
    ASSETS.mkdir(exist_ok=True)
    data = fetch_stats()
    uri = avatar_data_uri(data["user"].get("avatar_url", ""))
    (ASSETS / "home.svg").write_text(build_home(uri), encoding="utf-8")
    (ASSETS / "about.svg").write_text(build_about(), encoding="utf-8")
    (ASSETS / "projects.svg").write_text(build_projects(), encoding="utf-8")
    (ASSETS / "focus.svg").write_text(build_focus(), encoding="utf-8")
    (ASSETS / "blog.svg").write_text(build_blog(), encoding="utf-8")
    (ASSETS / "stats.svg").write_text(build_stats(data), encoding="utf-8")
    (ROOT / "blog").mkdir(exist_ok=True)
    for p in POSTS:
        (ROOT / "blog" / f"{p['slug']}.md").write_text(p["body"], encoding="utf-8")
    (ROOT / "README.md").write_text(build_readme(build_stats_block(data)), encoding="utf-8")
    print("wrote the terminal windows, blog pages and README.md", file=sys.stderr)


if __name__ == "__main__":
    main()
