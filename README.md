<div align="center">

<a href="#home"><img src="assets/nav-home.svg" alt="home" height="38"></a> <a href="#projects"><img src="assets/nav-projects.svg" alt="projects" height="38"></a> <a href="#focus"><img src="assets/nav-focus.svg" alt="focus" height="38"></a> <a href="#blog"><img src="assets/nav-blog.svg" alt="blog" height="38"></a> <a href="#stats"><img src="assets/nav-stats.svg" alt="stats" height="38"></a> 

</div>

<a name="home"></a>
<img src="assets/home.svg" alt="Kali terminal running neofetch with the Kali dragon and the profile picture in a circle" width="100%">

<a name="projects"></a>
<img src="assets/projects.svg" alt="Kali terminal listing six security projects" width="100%">

**Code:** [sentinel-travel](https://github.com/rewantth/SentinelTravel) · [sentinelops](https://github.com/rewantth/sentinelops-soc-console) · [phishguard-x](https://github.com/rewantth/phishguard-x) · [securewave-net](https://github.com/rewantth/Enterprise-Secure-Network-Packet-Tracer) · [cdsa-study-tracker](https://github.com/rewantth/cdsa-study-tracker) · inbox-dashboard <sub>(private)</sub>

<details>
<summary><b>sentinel-travel/</b> &nbsp;·&nbsp; identity threat detection and impossible-travel analytics, shown as a live SOC console.</summary>

**Stack:** FastAPI · React · SQLite · WebSockets · Leaflet · Recharts &nbsp;|&nbsp; **Status:** portfolio project, synthetic data only &nbsp;|&nbsp; [code](https://github.com/rewantth/SentinelTravel)

```console
┌──(kali㉿kali)-[~/projects/sentinel-travel]
└─$ tree --modules
.
├── detection    travel speed (Haversine), per-user baselines, risk and confidence scoring, MITRE ATT&CK mapping
├── signals      impossible travel, VPN/proxy and TOR use, MFA failures, bad IP reputation, credential stuffing
├── console      live alert stream, maps, analyst notes, audit log, kill-switch actions, SIEM-style exports
└── data         15 synthetic attack scenarios, no real users or logs
```

Identity attacks look like normal logins until timing, location, device and MFA are correlated. This turns authentication events into explainable alerts and shows the reasoning to the analyst.

</details>

<details>
<summary><b>sentinelops/</b> &nbsp;·&nbsp; SOC alert triage and investigation console with MITRE ATT&CK mapping and case tracking.</summary>

**Stack:** Flask · SQLAlchemy · SQLite · Chart.js · JavaScript &nbsp;|&nbsp; **Status:** portfolio project, safe simulated alerts &nbsp;|&nbsp; [code](https://github.com/rewantth/sentinelops-soc-console)

```console
┌──(kali㉿kali)-[~/projects/sentinelops]
└─$ tree --modules
.
├── ingest       simulated alert generation, JSON ingestion into SQLite
├── triage       severity and status filters, MITRE ATT&CK classification, IP enrichment with a safe no-key fallback
├── cases        new to closed workflow, timeline with second-level timestamps, analyst notes
└── reporting    live simulated feed, charts, investigation export as JSON, MTTD and MTTR metrics
```

Defensive and blue-team only: no offensive functionality, malware or harmful payloads.

</details>

<details>
<summary><b>phishguard-x/</b> &nbsp;·&nbsp; explainable phishing detection and email threat analysis.</summary>

**Stack:** Python · Flask · pytest &nbsp;|&nbsp; **Status:** portfolio project &nbsp;|&nbsp; [code](https://github.com/rewantth/phishguard-x)

```console
┌──(kali㉿kali)-[~/projects/phishguard-x]
└─$ tree --modules
.
├── email-checks urgency, coercion, credential bait, scam-like phrasing
├── sender-checksimpersonation, free-provider misuse, brand mismatch
├── url-checks   shorteners, IP links, risky TLDs, redirects, obfuscation, displayed-vs-actual links
└── scoring      weighted category scores, severity, confidence and a verdict
```

The engine is rule-based on purpose, so every finding is explainable: each carries a rule id, evidence, severity and remediation. It includes sample phishing and legitimate messages and unit tests for scoring.

</details>

<details>
<summary><b>securewave-net/</b> &nbsp;·&nbsp; an enterprise branch network with VLAN segmentation, a DMZ and routed security zones, built in Cisco Packet Tracer.</summary>

**Stack:** Cisco Packet Tracer · VLANs · SVIs · DHCP · DNS · AAA &nbsp;|&nbsp; **Status:** core network complete. ACLs, port security and OSPF planned &nbsp;|&nbsp; [code](https://github.com/rewantth/Enterprise-Secure-Network-Packet-Tracer) · [project page](https://rewantth.github.io/Enterprise-Secure-Network-Packet-Tracer/)

```console
┌──(kali㉿kali)-[~/projects/securewave-net]
└─$ tree --modules
.
├── segmentation 8 VLANs, a guest VLAN, and a black-hole VLAN 999 for unused ports
├── routing      layer 3 inter-VLAN routing on a core switch, edge router link, trunks to 5 access switches
├── services     DHCP for every user VLAN, a DMZ with DNS, web and AAA servers
└── evidence     device configs, IP and VLAN plan, test checklists and a security policy matrix
```

Next: ACL-based access control between VLANs, port security, and OSPF between the edge router and core.

</details>

<details>
<summary><b>cdsa-study-tracker/</b> &nbsp;·&nbsp; a free, offline study tracker for the HTB SOC Analyst path and the CDSA exam. no accounts, no backend, no network requests.</summary>

**Stack:** single-file HTML · JavaScript · CSS &nbsp;|&nbsp; **Status:** live, progress never leaves the browser &nbsp;|&nbsp; [code](https://github.com/rewantth/cdsa-study-tracker) · [live page](https://rewantth.github.io/cdsa-study-tracker/)

```console
┌──(kali㉿kali)-[~/projects/cdsa-study-tracker]
└─$ tree --modules
.
├── plan         341 checkboxes across 25 modules, with a daily plan that re-plans from what is left
├── review       spaced-repetition queue, focus timer, streaks that ignore rest days
├── guides       per-module guides, hints, notes, a problem roadmap and an exam readiness tab
└── privacy      progress stays in the browser, with download and restore backups
```

Privacy by design: with no analytics and no requests to any server, nothing about the user can leak.

</details>

<details>
<summary><b>inbox-dashboard/</b> &nbsp;·&nbsp; a security-first dashboard that turns the emails in a mailbox into a live, encrypted web page.</summary>

**Stack:** Python 3.12 · Gmail API · WebCrypto · vanilla JS · GitHub Actions &nbsp;|&nbsp; **Status:** running, source private &nbsp;|&nbsp; private source

```console
┌──(kali㉿kali)-[~/projects/inbox-dashboard]
└─$ tree --modules
.
├── mail-reader  read-only Gmail OAuth, incremental download with a cache
├── classifier   rule engine: sender, subject and body patterns decide the category and stage
├── vault        AES-256-GCM encryption, decrypted only in the browser
└── pipeline     scheduled build in a private repo, one-way publish to a public page
```

Security: read-only OAuth scope · AES-256-GCM with PBKDF2-SHA-256 (1,000,000 rounds) · strict Content Security Policy from the page's own script hash · a non-extractable CryptoKey instead of the passphrase · every Action pinned to a commit · a deploy key that writes to one repository. 85 automated checks.

</details>

<a name="focus"></a>
<img src="assets/focus.svg" alt="Kali terminal showing what the projects are about" width="100%">

<a name="blog"></a>
<img src="assets/blog.svg" alt="Kali terminal listing two writeups" width="100%">

**Read:** [A dashboard that can't leak its own data](blog/inbox-dashboard-security.md) · [Keep the key, not the passphrase](blog/keep-the-key.md)

<a name="stats"></a>
<img src="assets/stats.svg" alt="Kali terminal showing GitHub stats: profile picture, repositories, activity and languages" width="100%">

<sub>The stats picture is rebuilt every day by a small GitHub Action from public data only. Private repositories are never shown.</sub>
