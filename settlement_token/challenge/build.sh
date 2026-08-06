#!/bin/bash
# Compile and strip the binary to make reversing realistic
gcc -O2 -Wall -Wextra -o tokengen tokengen.c
strip tokengen
echo "[+] Build complete: tokengen"
