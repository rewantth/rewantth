# A dashboard that can't leak its own data

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
