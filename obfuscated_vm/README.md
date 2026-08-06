# CTF Challenge: Obfuscated VM

## Challenge Details
- **Name**: Obfuscated VM
- **Category**: Reverse Engineering
- **Difficulty**: Medium
- **Flag**: `VTCH{c0ntr0l_fl0w_fl4tt3n1ng_vm_byp4ss}`

---

## Deployment Instructions

This is an **offline reverse engineering** challenge, so no active hosting or servers are required.

1. **Compilation**:
   Compile the binary using the provided build script (requires `gcc`):
   ```bash
   cd challenge
   ./build.sh
   ```
2. **Distribution**:
   Upload only the compiled **`crackme`** binary (located in the `challenge/` folder) to the CTF challenge page.
3. **Important Security Note**:
   **DO NOT** distribute `crackme.c`, `build.sh`, or the `solution/` folder containing the solve scripts and writeup.

---

## Solution Walkthrough

The binary validates a 16-character license key. If correct, it decrypts and prints the flag using RC4. To solve it:

1. **Decompile the VM Loop**: 
   Decompiling the `run_vm()` function in Ghidra or IDA Pro reveals a Control Flow Flattened state machine inside a `while` loop governed by a `switch(state)` statement.
2. **Reverse the Bitwise Math (MBA)**:
   Arithmetic operations inside the VM execution states are disguised using Mixed Boolean-Arithmetic:
   - **XOR**: `(A | B) - (A & B)` is a standard logical XOR.
   - **ADD**: `(A ^ B) + 2*(A & B)` is simple addition.
3. **Solve the Rolling Hash**:
   The validation checks the key characters using a rolling XOR checksum compared to target values after adding `0x57`.
4. **Key Derivation**:
   By working backward (subtracting `0x57` from target bytes and XORing adjacent states), we recover the key: `Fl4tt3n_Th3_Fl0w`.
5. **Execution**:
   Provide the key to the binary to reveal the flag:
   ```bash
   ./crackme Fl4tt3n_Th3_Fl0w
   ```
   For the detailed solution writeup, see [writeup.md](solution/writeup.md) and the automated solver in [solve.py](solution/solve.py).
