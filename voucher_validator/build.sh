#!/bin/sh
# Build the Voucher Validator challenge binary.
# -O2 : optimize (and exercise the volatile anti-constant-folding)
# -s  : strip symbol table  -> "stripped ELF" as required
set -e

CC="${CC:-gcc}"
OUT="${1:-voucher}"

"$CC" -O2 -s -o "$OUT" voucher.c
strip --strip-all "$OUT" 2>/dev/null || true

echo "[+] built: $OUT"
file "$OUT" 2>/dev/null || true
