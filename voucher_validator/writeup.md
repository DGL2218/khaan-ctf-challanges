# Voucher Validator — Writeup

| | |
|---|---|
| **Category** | Reversing (static, ELF) |
| **Difficulty** | Easy (warm-up) |
| **Flag** | `VTCH{n0_fr33_ch4rg3_w1th0ut_RE}` |
| **Files given to player** | `voucher` (stripped ELF) |

## Scenario

A VTCH top-up kiosk ships an **offline voucher validation module**. Enter a
valid 16-character voucher code and the kiosk issues a free top-up credit —
and prints the flag. The goal is to recover the accepted code by reverse
engineering the binary.

## 1. Reconnaissance

```
$ file voucher
voucher: ELF 64-bit LSB pie executable, x86-64, ... stripped

$ strings -n 6 voucher | grep -iE 'MoviPay\{|MOVI8F3A|n0_fr33'
(no output)
```

The binary is a stripped 64-bit PIE. A naive `strings` sweep returns **no flag
and no plaintext code** — only the UI banners (`=== VTCH Kiosk ... ===`,
`Enter voucher code:`, etc.). So the "grep the flag out of strings" shortcut
does not work; the code and flag are stored encoded.

## 2. Static analysis

Loading `main` in Ghidra (or `objdump -d`) reveals three stages:

**(a) Normalization + length gate.** The raw input is filtered to keep only
alphanumeric characters, uppercased, and the result must be exactly 16 bytes —
otherwise `Invalid voucher format.` This is why `MOVI-8F3A-2C7D-BE19`,
`movi8f3a2c7dbe19`, etc. all map to the same 16-char string.

**(b) Runtime reconstruction of the expected code.** Rather than storing the
code, `main` rebuilds it from an encoded array `ENC_CODE[16]` and a per-index
mask:

```c
expected[i] = ENC_CODE[i] ^ ((i*37 + seed) & 0xFF);   // seed = 0x5A (volatile)
```

The `seed` is **volatile**, so the compiler is forbidden from constant-folding
the expression — the plaintext code never appears as a literal. The disassembly
shows the loop directly: the seed `0x5A` is written to the stack and re-read
each iteration (`movb $0x5a` / `movzbl`), XORed against `ENC_CODE`
(`xor (%rdi,%rdx,1),%al`), with the index multiplier appearing as
`add $0x25,%ecx` (37 decimal).

**(c) Compare, then code-keyed flag decryption.** The normalized input is
`memcmp`'d against `expected`. On match, the flag is decrypted with a keystream
**derived from the code itself**:

```c
k[i]  = code[i % 16] ^ (uint8_t)(0xA5 + i*7);
flag[i] = ENC_FLAG[i] ^ k[i];
```

> **Why patching the branch fails:** the decryption key *is* the code. If you
> NOP the `memcmp` check and feed a wrong code, the keystream is derived from
> your wrong input and the flag decrypts to garbage. You must recover the real
> code.

## 3. Solution

Reverse stage (b) — the mask is fully known, so the code falls out directly:

```python
ENC_CODE = [0x17,0x30,0xF2,0x80,0xD6,0x55,0x0B,0x1C,
            0xB0,0xE4,0xFB,0xB5,0x54,0x7E,0x51,0xBC]
code = "".join(chr(ENC_CODE[i] ^ ((i*37 + 0x5A) & 0xFF)) for i in range(16))
# -> MOVI8F3A2C7DBE19
```

Recovered code: **`MOVI8F3A2C7DBE19`** → formatted as **`MOVI-8F3A-2C7D-BE19`**.

Feeding it to the kiosk:

```
$ echo 'MOVI-8F3A-2C7D-BE19' | ./voucher
=== VTCH Kiosk : Offline Voucher Validator ===
Enter voucher code: Voucher accepted! Free top-up credit issued.
VTCH{n0_fr33_ch4rg3_w1th0ut_RE}
```

Equivalently, the flag can be reproduced fully offline by also reversing stage
(c) with the recovered code (see `solve.py`, which does both the static
derivation and a dynamic check against the binary).

## 4. Design notes (for organizers)

- **Anti-`strings`:** code and flag are stored as XOR-encoded byte arrays, so a
  string dump exposes neither.
- **Anti-constant-folding:** the `volatile` seed forces the expected code to be
  computed at runtime; it is never a static literal.
- **Anti-branch-patch:** because the flag's key is the correct code, bypassing
  the comparison does not surface the flag — the solver must actually recover
  the code. This blocks the trivial "patch the `je`/`jne` and run" approach.
- **AI-resistance:** the one-to-two layers of encoding plus the runtime
  reconstruction defeat a "`strings` + single query" auto-solve, while keeping
  the intended manual path short and clean for a warm-up.

## Files

```
challenge/
  voucher        # stripped ELF given to players
  voucher.c      # source (build input)
  build.sh       # gcc -O2 -s  -> stripped binary
solution/
  solve.py       # static + dynamic solver
  writeup.md     # this document
```
