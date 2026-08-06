# CTF Challenge: Settlement Token

## Challenge Details
- **Name**: Settlement Token
- **Category**: Web / Cryptography
- **Difficulty**: Medium
- **Flag**: `VTCH{c4n0n1c4l_HMAC_f0rg3d_v1a_spl1t_k3y}`

---

## Deployment Instructions

This challenge requires a hosted Flask API server and a client binary distributed to players.

1. **Start the API Server**:
   Start the Docker container (starts on port `5001`):
   ```bash
   cd challenge
   docker-compose up -d --build
   ```
2. **Distribution**:
   Upload only the compiled client binary **`tokengen`** (located in the `challenge/` folder) to the CTF challenge page.
3. **Important Security Note**:
   **DO NOT** distribute `server.py`, `tokengen.c`, `sha256.h`, `build.sh`, or any files inside the `solution/` folder.

---

## Solution Walkthrough

The server allows free settlements if the signature matches for parameters `payType=COMP` and `cbsn=0000`. To solve it:

1. **Key Extraction**:
   Inspect the `.rodata` segment of the client `tokengen` binary to find two 16-byte components: `KEYA` (`"MoviPayMasterKey"`) and `KEYB` (`"SettlementSecRet"`).
2. **Reconstruct Key Derivation**:
   Write a script to combine them: reverse `KEYB`, XOR it with `0x5A`, concatenate it to `KEYA`, and take the first 16 bytes of the SHA-256 hash. This is the HMAC-SHA256 master key.
3. **Canonicalization**:
   Build the canonical message string alphabetically, zero-padding the values to 10 digits and separating them with `\x1f`. Note that `payType=COMP` maps to integer `2` and `cbsn=0000` maps to `0`.
4. **Signature Forgery**:
   Compute the HMAC-SHA256 signature, take the first 10 hex characters, and POST the payload to the server's `/settle` endpoint on port `5001`.
   
   For the detailed solution writeup, see [solution/writeup.md](solution/writeup.md) and the automated solver in [solution/forge.py](solution/forge.py).
