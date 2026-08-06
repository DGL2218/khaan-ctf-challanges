# CTF Challenge: Voucher Validator

## Challenge Details
- **Name**: Voucher Validator
- **Category**: Reverse Engineering
- **Difficulty**: Easy
- **Flag**: `VTCH{n0_fr33_ch4rg3_w1th0ut_RE}`

---

## Deployment Instructions

This is an **offline reverse engineering** challenge, so no active hosting or servers are required.

1. **Compilation**:
   Compile the binary using the provided build script (requires `gcc`):
   ```bash
   ./build.sh
   ```
2. **Distribution**:
   Upload only the compiled **`voucher`** binary to the CTF challenge page.
3. **Important Security Note**:
   **DO NOT** distribute `voucher.c`, `build.sh`, `writeup.md`, or the solver `solve.py`.

---

## Solution Walkthrough

The binary checks a 16-character voucher code. If the code is correct, it decrypts and prints the flag. To solve it:

1. **Static Analysis**:
   Opening the binary in Ghidra or IDA Pro shows the main verification loop. The plaintext expected voucher code is never stored in memory.
2. **Reconstruction Logic**:
   The expected code is reconstructed dynamically at runtime using a volatile seed of `0x5A`:
   ```c
   expected[i] = ENC_CODE[i] ^ ((i * 37 + 0x5A) & 0xFF);
   ```
3. **Solving**:
   Write a Python script to reverse this XOR operation using the `ENC_CODE` array extracted from `.rodata`. This yields the accepted voucher: `MOVI8F3A2C7DBE19`.
4. **Execution**:
   Provide the voucher to the program:
   ```bash
   ./voucher
   Enter voucher code: MOVI-8F3A-2C7D-BE19
   ```
   For the detailed solution writeup, see [writeup.md](writeup.md) and the automated solver in [solve.py](solve.py).
