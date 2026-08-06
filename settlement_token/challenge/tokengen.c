#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "sha256.h"

// Obfuscated master key pieces
// KEYA is stored directly as a string literal: "MoviPayMasterKey"
// KEYB is stored directly as a string literal: "SettlementSecRet"
// Combined at runtime to resist simple grep/strings:
// material = KEYA || reverse(KEYB) ^ 0x5A
// key = sha256(material)[:16]
const char KEYA[] = "MoviPayMasterKey";
const char KEYB[] = "SettlementSecRet";

// HMAC-SHA256 implementation
void hmac_sha256(const uint8_t *key, size_t key_len, const uint8_t *data, size_t data_len, uint8_t *mac) {
    SHA256_CTX ctx;
    uint8_t k_ipad[64];
    uint8_t k_opad[64];
    uint8_t temp_key[32];

    if (key_len > 64) {
        sha256_init(&ctx);
        sha256_update(&ctx, key, key_len);
        sha256_final(&ctx, temp_key);
        key = temp_key;
        key_len = 32;
    }

    memset(k_ipad, 0, 64);
    memset(k_opad, 0, 64);
    memcpy(k_ipad, key, key_len);
    memcpy(k_opad, key, key_len);

    for (int i = 0; i < 64; i++) {
        k_ipad[i] ^= 0x36;
        k_opad[i] ^= 0x5C;
    }

    // Inner hash: sha256(k_ipad || data)
    sha256_init(&ctx);
    sha256_update(&ctx, k_ipad, 64);
    sha256_update(&ctx, data, data_len);
    uint8_t inner_hash[32];
    sha256_final(&ctx, inner_hash);

    // Outer hash: sha256(k_opad || inner_hash)
    sha256_init(&ctx);
    sha256_update(&ctx, k_opad, 64);
    sha256_update(&ctx, inner_hash, 32);
    sha256_final(&ctx, mac);
}

void print_usage(const char *prog) {
    fprintf(stderr, "Usage: %s --amt <amount> --cbsn <cbsn> --sid <station_id> --ts <timestamp> --ver <version>\n", prog);
}

int main(int argc, char **argv) {
    long long amt = -1;
    long long cbsn = -1;
    long long sid = -1;
    long long ts = -1;
    long long ver = -1;
    int has_amt = 0, has_cbsn = 0, has_sid = 0, has_ts = 0, has_ver = 0;

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--amt") == 0 && i + 1 < argc) {
            amt = atoll(argv[++i]);
            has_amt = 1;
        } else if (strcmp(argv[i], "--cbsn") == 0 && i + 1 < argc) {
            cbsn = atoll(argv[++i]);
            has_cbsn = 1;
        } else if (strcmp(argv[i], "--sid") == 0 && i + 1 < argc) {
            sid = atoll(argv[++i]);
            has_sid = 1;
        } else if (strcmp(argv[i], "--ts") == 0 && i + 1 < argc) {
            ts = atoll(argv[++i]);
            has_ts = 1;
        } else if (strcmp(argv[i], "--ver") == 0 && i + 1 < argc) {
            ver = atoll(argv[++i]);
            has_ver = 1;
        }
    }

    if (!has_amt || !has_cbsn || !has_sid || !has_ts || !has_ver) {
        print_usage(argv[0]);
        return 1;
    }

    // Server logic check for COMP payments
    // The tokengen ONLY creates legitimate USER (payType = 1) tokens.
    // If the client asks for key parameters that don't match, we fail, or we hardcode.
    // The scenario says: "The provided token generator issues only legitimate user payments (USER)"
    // Therefore, payType is hardcoded to 1 (USER) in this terminal generator.
    int pay_type = 1; 

    // Build canonical representation
    // Fields: AMT, CBSN, PAYTYPE, SID, TS, VER in alphabetical order.
    // Format: NAME=0-padded-10-digit
    // Separator: 0x1F (\x1f)
    char canonical[512];
    int len = snprintf(canonical, sizeof(canonical),
                       "AMT=%010lld\x1f"
                       "CBSN=%010lld\x1f"
                       "PAYTYPE=%010d\x1f"
                       "SID=%010lld\x1f"
                       "TS=%010lld\x1f"
                       "VER=%010lld",
                       amt, cbsn, pay_type, sid, ts, ver);

    if (len < 0 || len >= (int)sizeof(canonical)) {
        fprintf(stderr, "Error building canonical string\n");
        return 1;
    }

    // Reconstruct key: material = KEYA || reverse(KEYB)^0x5A
    uint8_t material[32];
    memcpy(material, KEYA, 16);
    for (int i = 0; i < 16; i++) {
        material[16 + i] = KEYB[15 - i] ^ 0x5A;
    }

    // sha256(material)
    uint8_t mat_hash[32];
    SHA256_CTX sha_ctx;
    sha256_init(&sha_ctx);
    sha256_update(&sha_ctx, material, 32);
    sha256_final(&sha_ctx, mat_hash);

    // key = mat_hash[:16]
    uint8_t key[16];
    memcpy(key, mat_hash, 16);

    // Compute HMAC-SHA256
    uint8_t mac[32];
    hmac_sha256(key, 16, (uint8_t *)canonical, strlen(canonical), mac);

    // Output: first 10 hex characters (5 bytes)
    for (int i = 0; i < 5; i++) {
        printf("%02x", mac[i]);
    }
    printf("\n");

    return 0;
}
