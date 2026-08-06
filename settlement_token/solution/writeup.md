# Writeup — Settlement Token

## Challenge Overview
We are given a token generator binary (`tokengen`) which runs on the terminal and generates secure MACs for settlement requests. The terminal only ever issues legitimate user transactions (using `payType=USER`). However, the Central Settlement Management System (CSMS) server contains an internal, hidden path for free settlements, triggered when `payType=COMP` and `cbsn=0000`.

To get the flag, we need to forge a valid signature (MAC) for this free settlement transaction and submit it to the server.

---

## Reverse Engineering the Token Generator

By disassembling or decompiling the `tokengen` binary, we locate the following structural components:

### 1. Key Extraction & Combiner Logic
We can locate two 16-byte key components stored in the data segment:
- `KEYA` = `"MoviPayMasterKey"`
- `KEYB` = `"SettlementSecRet"`

At runtime, these keys are not used directly. Instead, they are combined with a specific transformation:
- `KEYB` is reversed byte-by-byte.
- Each byte of the reversed `KEYB` is XORed with `0x5A`.
- The transformed `KEYB` is concatenated onto `KEYA` to form a 32-byte block (`material`).
- `sha256(material)` is computed, and the first 16 bytes of this hash are used as the `HMAC-SHA256` key.

Python equivalent for the key reconstruction:
```python
KEYA = b"MoviPayMasterKey"
KEYB = b"SettlementSecRet"

rev_keyb = bytearray(KEYB[::-1])
for i in range(len(rev_keyb)):
    rev_keyb[i] ^= 0x5A
material = KEYA + bytes(rev_keyb)
key = hashlib.sha256(material).digest()[:16]
```

### 2. Canonicalization Rules
A closer look at the string formatting function inside the binary reveals how the canonical buffer is constructed before signing:
- The parameters are ordered alphabetically: `AMT`, `CBSN`, `PAYTYPE`, `SID`, `TS`, `VER`.
- Each parameter is formatted in uppercase: `FIELD_NAME=value`.
- Values are strictly formatted as **10-digit 0-padded integers** (e.g. `%010lld`).
- The fields are separated by the ASCII Unit Separator `0x1F` (`\x1f`).
- `PAYTYPE` maps to an integer internally: `USER -> 1`, `COMP -> 2`.

Canonical template:
`AMT=%010d\x1fCBSN=%010d\x1fPAYTYPE=%010d\x1fSID=%010d\x1fTS=%010d\x1fVER=%010d`

For our target request (`payType = "COMP"` and `cbsn = "0000"`), mapping to values:
- `AMT`: `100` -> `0000000100`
- `CBSN`: `0` -> `0000000000`
- `PAYTYPE`: `2` -> `0000000002`
- `SID`: `42` -> `0000000042`
- `TS`: `1719876543` -> `1719876543`
- `VER`: `1` -> `0000000001`

Resulting canonical string:
`AMT=0000000100\x1fCBSN=0000000000\x1fPAYTYPE=0000000002\x1fSID=0000000042\x1fTS=1719876543\x1fVER=0000000001`

### 3. Signature & Truncation
The binary computes `HMAC-SHA256` of the canonical string using the derived key. It then outputs only the **first 10 hex characters** (5 bytes) of the digest as the signature.

---

## Exploitation (Token Forgery)

Since we have extracted the master key components, reverse-engineered the derivation transformation, and identified the exact formatting/canonical rules, we can forge a token for any transaction parameters.

We craft a POST request payload containing the parameter overrides:
```json
{
    "amt": 100,
    "cbsn": "0000",
    "payType": "COMP",
    "sid": 42,
    "ts": 1719876543,
    "ver": 1,
    "mac": "<forged_mac>"
}
```

By computing the MAC for `payType=COMP` (internally mapped to `2`) and `cbsn=0000` (internally `0`), we bypass the terminal restriction and query the CSMS server directly. The server validates the signature, notices the free settlement flags, and awards the flag:
`VTCH{c4n0n1c4l_HMAC_f0rg3d_v1a_spl1t_k3y}`
