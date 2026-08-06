# Writeup — Obfuscated VM Crackme

## Challenge Overview
The challenge is an offline Reverse Engineering puzzle where a compiled binary (`crackme`) validates a 16-character license key. If the key is correct, it decrypts and prints the flag.

The binary has been compiled with manual compiler-level static analysis defenses resembling Obfuscator-LLVM (OLLVM):
1. **Control Flow Flattening**: The main execution of the verification engine (a custom VM interpreter) is structured inside a loop governed by a state variable (`state`) and a massive `switch-case` statement. The standard execution path is broken up, forcing static analysis tools to construct complex control flow graphs.
2. **Instruction Substitution**: Common arithmetic operations inside the VM have been replaced with complex bitwise identities.
3. **Custom VM**: Key validation is defined in customized bytecode processed by a stack-less virtual machine interpreter.

---

## Static Analysis & Deobfuscation

Opening the binary in a decompiler (like Ghidra or IDA Pro), we analyze the `main` function and locate `run_vm(char *input)`.

### 1. Reversing the VM State Machine
Inside `run_vm`, we observe a loop structure:
```c
int state = 0x1000;
while (state != 0x9999) {
    switch (state) {
        ...
    }
}
```
We analyze each case block inside the state switch to understand the instructions:
* **State `0x1000` (FETCH)**: Fetches `opcode = bytecode[pc++]` and dispatches to state `0x2000 + opcode`.
* **State `0x2001` (OP_LOAD_INPUT)**: Loads `input[regs[4]]` into `regs[0]`.
* **State `0x2002` (OP_XOR)**: Performs `regs[1] = (regs[1] | regs[0]) - (regs[1] & regs[0])`. By boolean algebra, $(A \lor B) - (A \land B) \equiv A \oplus B$. Thus, this state accumulates input bytes into a rolling XOR checksum.
* **State `0x2003` (OP_ADD)**: Performs `regs[2] = ((regs[1] ^ 0x57) + 2 * (regs[1] & 0x57)) & 0xFF`. By bitwise arithmetic, $(A \oplus B) + 2(A \land B) \equiv A + B$. Thus, this adds `0x57` to the accumulator.
* **State `0x2004` (OP_CMP)**: Compares `regs[2]` against `targets[regs[4]]`. If not equal, sets the failure flag (`regs[3] = 1`).
* **State `0x2005` (OP_INC)**: Increments the index register: `regs[4] = (regs[4] ^ 1) + 2 * (regs[4] & 1)`. Equivalent to `regs[4] += 1`.
* **State `0x2006` (OP_JLT)**: Checks if `regs[4] < regs[5]` (loop counter limit of 16). If true, sets `pc = bytecode[pc]`.
* **State `0x2007` (OP_EXIT)**: Breaks the loop (`state = 0x9999`).

### 2. Extracting Parameters
Looking at the data segment, we extract:
1. The **`bytecode`** array: `0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x00, 0x07`.
2. The **`targets`** array (16 bytes):
   `{0x9D, 0x81, 0x75, 0xC1, 0x75, 0x84, 0x9A, 0x73, 0x9F, 0x77, 0x6A, 0xA3, 0x61, 0xBD, 0xAD, 0x78}`

---

## Solving the Key Validation

By translating the VM instructions back to pseudocode, the verification algorithm is:
* Let $k_i$ be the $i$-th byte of the key input.
* Let $S_i$ be the rolling XOR state at index $i$, where $S_{-1} = 0$:
  $$S_i = S_{i-1} \oplus k_i$$
* The target comparison is:
  $$(S_i + 0x57) \pmod{256} == \text{target}[i]$$

To solve, we reverse this relation mathematically:
1. Reconstruct $S_i$:
   $$S_i = (\text{target}[i] - 0x57) \pmod{256}$$
2. Reconstruct key bytes $k_i$:
   $$k_i = S_i \oplus S_{i-1}$$

Running this solver on the extracted `targets` array yields the correct 16-character key:
`Fl4tt3n_Th3_Fl0w`

Providing this key to `crackme` decrypts the RC4 payload to reveal the flag:
`VTCH{c0ntr0l_fl0w_fl4tt3n1ng_vm_byp4ss}`
