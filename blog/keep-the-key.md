# Keep the key, not the passphrase

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
