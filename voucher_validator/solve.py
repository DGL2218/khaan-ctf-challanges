#!/usr/bin/env python3
"""
Reference solver for "Voucher Validator".

Two independent solves:
  (A) Static: recover the expected code by reversing the runtime XOR, then
      reproduce the flag-decryption locally (no need to run the binary).
  (B) Dynamic: feed the recovered code to the ELF and read the flag back.

The ENC_CODE bytes are read straight out of the binary's .rodata. They are
the only thing an analyst needs from the file; everything else is arithmetic.
"""

import subprocess
import sys
import os

# --- Encoded expected code, as embedded in the ELF (.rodata) -------------
ENC_CODE = [0x17, 0x30, 0xF2, 0x80, 0xD6, 0x55, 0x0B, 0x1C,
            0xB0, 0xE4, 0xFB, 0xB5, 0x54, 0x7E, 0x51, 0xBC]

# Encoded flag, as embedded in the ELF (.rodata).
ENC_FLAG = [0xBE, 0xB7, 0xA6, 0xBB, 0x82, 0xE0, 0xCC, 0xC8, 0x89, 0xD5, 0xEF,
            0x85, 0xE4, 0x26, 0x5E, 0x03, 0x2A, 0x34, 0x46, 0x3C, 0x7E, 0x4F,
            0x78, 0x6F, 0x4F, 0x62, 0x18, 0x79, 0x79, 0x70, 0x3B]


def recover_code() -> str:
    # main() computes: expected[i] = ENC_CODE[i] ^ ((i*37 + 0x5A) & 0xFF)
    return "".join(
        chr(ENC_CODE[i] ^ ((i * 37 + 0x5A) & 0xFF)) for i in range(16)
    )


def derive_flag(code: str) -> str:
    # main() decrypts with: k[i] = code[i % 16] ^ ((0xA5 + i*7) & 0xFF)
    out = []
    for i, e in enumerate(ENC_FLAG):
        k = (ord(code[i % 16]) ^ ((0xA5 + i * 7) & 0xFF)) & 0xFF
        out.append(chr(e ^ k))
    return "".join(out)


def format_voucher(code: str) -> str:
    return "-".join(code[i:i + 4] for i in range(0, 16, 4))


def main() -> int:
    code = recover_code()
    formatted = format_voucher(code)
    flag_static = derive_flag(code)

    print("[A] Static solve")
    print("    recovered code : %s" % code)
    print("    formatted input: %s" % formatted)
    print("    derived flag   : %s" % flag_static)

    # (B) Optional dynamic check against the real binary, if present.
    binary = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(__file__), "..", "challenge", "voucher")
    if os.path.exists(binary):
        try:
            res = subprocess.run([binary], input=formatted + "\n",
                                 capture_output=True, text=True, timeout=10)
            line = [l for l in res.stdout.splitlines() if l.startswith("VTCH{")]
            print("[B] Dynamic solve against %s" % os.path.relpath(binary))
            print("    binary returned: %s" % (line[0] if line else "(no flag)"))
        except Exception as exc:  # noqa: BLE001
            print("[B] could not run binary: %s" % exc)
    else:
        print("[B] binary not found at %s (skipping dynamic solve)" % binary)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
