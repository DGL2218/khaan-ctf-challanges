/*
 * VTCH Kiosk - Offline Voucher Validator
 * ------------------------------------------
 * Reversing CTF challenge (static, stripped ELF).
 *
 * Behaviour:
 *   - Reads a voucher code, normalizes it (alphanumeric only, uppercased),
 *     and requires exactly 16 characters.
 *   - The expected code is reconstructed at RUNTIME via
 *         expected[i] = ENC_CODE[i] ^ ((i*37 + seed) & 0xFF)
 *     where `seed` is volatile. The volatile read prevents the optimizer
 *     from constant-folding the expression, so the plaintext expected code
 *     is never stored as a literal in the binary.
 *   - On a successful compare, the embedded flag is XOR-decrypted with a
 *     keystream DERIVED FROM THE CORRECT CODE. Because the decryption key is
 *     the code itself, patching the compare branch does not reveal the flag;
 *     a solver must actually recover the code.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdint.h>
#include <stddef.h>

#define CODE_LEN 16

/* Encoded expected code. Plaintext is computed at runtime (see main). */
static const uint8_t ENC_CODE[CODE_LEN] = {
    0x17,0x30,0xF2,0x80,0xD6,0x55,0x0B,0x1C,
    0xB0,0xE4,0xFB,0xB5,0x54,0x7E,0x51,0xBC
};

/* Flag, XOR-encrypted with a keystream derived from the correct code:
 *     k[i]        = code[i % CODE_LEN] ^ (uint8_t)(0xA5 + i*7)
 *     ENC_FLAG[i] = flag[i] ^ k[i]
 */
static const uint8_t ENC_FLAG[] = {
    0xBE,0xB7,0xA6,0xBB,0x82,0xE0,0xCC,0xC8,0x89,0xD5,0xEF,0x85,
    0xE4,0x26,0x5E,0x03,0x2A,0x34,0x46,0x3C,0x7E,0x4F,0x78,0x6F,
    0x4F,0x62,0x18,0x79,0x79,0x70,0x3B
};
#define FLAG_LEN (sizeof(ENC_FLAG))

/* Keep only [A-Za-z0-9], uppercase, into `out`. Sets *out_len. */
static void normalize(const char *in, char *out, size_t cap, size_t *out_len) {
    size_t j = 0;
    for (size_t i = 0; in[i] != '\0' && j + 1 < cap; i++) {
        unsigned char c = (unsigned char)in[i];
        if (isalnum(c)) {
            out[j++] = (char)toupper(c);
        }
    }
    out[j] = '\0';
    *out_len = j;
}

int main(void) {
    char raw[256];
    char norm[256];
    size_t nlen = 0;

    printf("=== VTCH Kiosk : Offline Voucher Validator ===\n");
    printf("Enter voucher code: ");
    fflush(stdout);

    if (fgets(raw, sizeof(raw), stdin) == NULL) {
        return 1;
    }

    normalize(raw, norm, sizeof(norm), &nlen);

    if (nlen != CODE_LEN) {
        printf("Invalid voucher format.\n");
        return 1;
    }

    /* volatile seed -> blocks constant folding of the expected code */
    volatile uint8_t seed = 0x5A;
    uint8_t expected[CODE_LEN];
    for (int i = 0; i < CODE_LEN; i++) {
        expected[i] = (uint8_t)(ENC_CODE[i] ^ (uint8_t)((i * 37 + seed) & 0xFF));
    }

    if (memcmp(norm, expected, CODE_LEN) != 0) {
        printf("Voucher rejected.\n");
        return 1;
    }

    /* Derive the keystream from the validated code and decrypt the flag. */
    char flag[FLAG_LEN + 1];
    for (size_t i = 0; i < FLAG_LEN; i++) {
        uint8_t k = (uint8_t)((unsigned char)norm[i % CODE_LEN]
                              ^ (uint8_t)(0xA5 + i * 7));
        flag[i] = (char)(ENC_FLAG[i] ^ k);
    }
    flag[FLAG_LEN] = '\0';

    printf("Voucher accepted! Free top-up credit issued.\n");
    printf("%s\n", flag);
    return 0;
}
