#!/bin/bash
gcc -O2 -Wall -Wextra -o crackme crackme.c
strip crackme
echo "[+] Build complete: crackme"
