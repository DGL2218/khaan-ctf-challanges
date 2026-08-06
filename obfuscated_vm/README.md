# Obfuscated VM (CTF Reverse Engineering Challenge)

A medium-difficulty offline Reverse Engineering challenge featuring:
1. **Control Flow Flattening** to make decompiler output spaghetti-like.
2. **Mixed Boolean-Arithmetic (MBA)** to disguise basic addition/XOR math.
3. **Custom Virtual Machine** parsing bytecode for key verification.

---

## Repository Structure

```text
obfuscated_vm/
├── README.md             # Setup and deployment guide (this file)
├── challenge/
│   ├── crackme           # Compiled challenge binary (Distribute to players)
│   ├── crackme.c         # Source code (DO NOT distribute)
│   └── build.sh          # Build script (DO NOT distribute)
└── solution/
    ├── writeup.md        # Detailed solution walk-through (DO NOT distribute)
    └── solve.py          # Automatic exploit/solver script (DO NOT distribute)
```

---

## Setup & Compilation

To build or recompile the challenge binary:

1. Enter the `challenge` directory:
   ```bash
   cd challenge/
   ```
2. Run the build script (requires `gcc`):
   ```bash
   ./build.sh
   ```
   This compiles `crackme.c` with optimization flags and strips debugging symbols to make reverse engineering more challenging.

---

## Deployment (What to Distribute to Players)

This is an **offline reverse engineering** challenge, so no active hosting or servers are required.

To deploy it for your CTF players:
1. Only distribute the compiled **`crackme`** binary file (located in the `challenge/` folder).
2. **DO NOT** distribute `crackme.c`, `build.sh`, or any files in the `solution/` folder.
