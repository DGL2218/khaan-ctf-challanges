#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

// VM Bytecode Program
// Instructions:
// 0x01: OP_LOAD_INPUT (R0 = input[R4])
// 0x02: OP_XOR (R1 = R1 ^ R0)
// 0x03: OP_ADD (R2 = R1 + 0x57)
// 0x04: OP_CMP (checks R2 == targets[R4], if not sets R3 = 1)
// 0x05: OP_INC (R4 = R4 + 1)
// 0x06: OP_JLT <addr> (if R4 < R5, PC = addr)
// 0x07: OP_EXIT
const uint8_t bytecode[] = {
    0x01, 
    0x02, 
    0x03, 
    0x04, 
    0x05, 
    0x06, 0x00, 
    0x07
};

// Target values for key validation (derived from rolling checksum of "Fl4tt3n_Th3_Fl0w")
const uint8_t targets[] = {
    0x9D, 0x81, 0x75, 0xC1, 0x75, 0x84, 0x9A, 0x73, 
    0x9F, 0x77, 0x6A, 0xA3, 0x61, 0xBD, 0xAD, 0x78
};

// RC4-encrypted flag: VTCH{c0ntr0l_fl0w_fl4tt3n1ng_vm_byp4ss}
const uint8_t encrypted_flag[] = {
    0x8A, 0xC5, 0x67, 0x8E, 0x47, 0xA7, 0xAF, 0xCC, 0xC2, 0x84, 0xF6, 0xE3, 
    0x5D, 0xCD, 0xA3, 0x58, 0x0E, 0x07, 0x63, 0xBB, 0x3E, 0xD1, 0x22, 0x20, 
    0x1C, 0xB5, 0x0B, 0x79, 0x63, 0x7A, 0x05, 0xD3, 0xAD, 0x31, 0xB4, 0xBE, 
    0x08, 0x9D, 0x4D
};
const size_t flag_len = sizeof(encrypted_flag);

// Standard RC4 decryption
void rc4(const uint8_t *key, size_t key_len, const uint8_t *data, size_t data_len, uint8_t *out) {
    uint8_t S[256];
    for (int i = 0; i < 256; i++) {
        S[i] = i;
    }
    int j = 0;
    for (int i = 0; i < 256; i++) {
        j = (j + S[i] + key[i % key_len]) % 256;
        uint8_t temp = S[i];
        S[i] = S[j];
        S[j] = temp;
    }
    int i = 0;
    j = 0;
    for (size_t k = 0; k < data_len; k++) {
        i = (i + 1) % 256;
        j = (j + S[i]) % 256;
        uint8_t temp = S[i];
        S[i] = S[j];
        S[j] = temp;
        out[k] = data[k] ^ S[(S[i] + S[j]) % 256];
    }
}

// Obfuscated VM Interpreter using Control Flow Flattening (CFF) and Instruction Substitution
int run_vm(const uint8_t *input) {
    uint8_t regs[6] = {0}; // R0=tmp, R1=accum, R2=check, R3=fail_flag, R4=i, R5=limit
    regs[5] = 16;
    int pc = 0;

    // Control Flow Flattening state variable
    int state = 0x1000;

    while (state != 0x9999) {
        switch (state) {
            case 0x1000: // FETCH State
                if (pc >= (int)sizeof(bytecode)) {
                    state = 0x9999;
                } else {
                    uint8_t op = bytecode[pc++];
                    state = 0x2000 + op; // Dispatch to specific opcode state
                }
                break;

            case 0x2001: // OP_LOAD_INPUT
                // Bogus control flow branching
                if (regs[3] > 5) {
                    state = 0x4444; // Dead path
                } else {
                    regs[0] = input[regs[4]];
                    state = 0x1000;
                }
                break;

            case 0x2002: // OP_XOR
                // Instruction Substitution: XOR -> (x | y) - (x & y)
                regs[1] = (regs[1] | regs[0]) - (regs[1] & regs[0]);
                state = 0x1000;
                break;

            case 0x2003: // OP_ADD
                // Instruction Substitution: ADD -> (x ^ y) + 2 * (x & y)
                regs[2] = ((regs[1] ^ 0x57) + 2 * (regs[1] & 0x57)) & 0xFF;
                state = 0x1000;
                break;

            case 0x2004: // OP_CMP
                if (regs[2] != targets[regs[4]]) {
                    regs[3] = 1;
                }
                state = 0x1000;
                break;

            case 0x2005: // OP_INC
                // Instruction Substitution: Increment -> x = (x ^ 1) + 2 * (x & 1)
                regs[4] = (regs[4] ^ 1) + 2 * (regs[4] & 1);
                state = 0x1000;
                break;

            case 0x2006: // OP_JLT
                {
                    uint8_t jump_pc = bytecode[pc++];
                    if (regs[4] < regs[5]) {
                        pc = jump_pc;
                    }
                }
                state = 0x1000;
                break;

            case 0x2007: // OP_EXIT
                state = 0x9999;
                break;

            case 0x4444: // Dead-end Bogus block
                regs[0] ^= 0xFF;
                state = 0x1000;
                break;

            default:
                state = 0x9999;
                break;
        }
    }

    return (regs[3] == 0);
}

int main(int argc, char **argv) {
    if (argc < 2) {
        printf("Usage: %s <key>\n", argv[0]);
        return 1;
    }

    if (strlen(argv[1]) != 16) {
        printf("Incorrect key length.\n");
        return 1;
    }

    if (run_vm((const uint8_t *)argv[1])) {
        uint8_t decrypted[128] = {0};
        rc4((const uint8_t *)argv[1], 16, encrypted_flag, flag_len, decrypted);
        printf("Success! Flag: %s\n", decrypted);
    } else {
        printf("Invalid key!\n");
    }

    return 0;
}
