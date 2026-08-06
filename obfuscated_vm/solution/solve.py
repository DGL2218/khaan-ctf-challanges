import subprocess
import os

# Target verification values extracted from the binary's targets array
targets = [
    0x9D, 0x81, 0x75, 0xC1, 0x75, 0x84, 0x9A, 0x73, 
    0x9F, 0x77, 0x6A, 0xA3, 0x61, 0xBD, 0xAD, 0x78
]

def solve():
    print("[*] Reconstructing rolling checksum states...")
    
    # Reconstruct the rolling XOR state array S
    # Since: target[i] = (S[i] + 0x57) & 0xFF
    # We get: S[i] = (target[i] - 0x57) & 0xFF
    S = []
    for t in targets:
        s_i = (t - 0x57) & 0xFF
        S.append(s_i)
        
    print(f"    States (S): {[hex(x) for x in S]}")
    
    print("[*] Solving for key bytes...")
    # Since: S[i] = S[i-1] ^ key[i] (with S[-1] = 0)
    # We get: key[i] = S[i] ^ S[i-1]
    key_bytes = []
    prev_s = 0
    for s_i in S:
        k_i = s_i ^ prev_s
        key_bytes.append(k_i)
        prev_s = s_i
        
    # Convert byte values to character string
    key = "".join(chr(b) for b in key_bytes)
    print(f"[+] Solved Key: '{key}'")
    return key

def verify_with_binary(key):
    print("[*] Verifying key with local crackme binary...")
    binary_path = "../challenge/crackme"
    if not os.path.exists(binary_path):
        binary_path = "./challenge/crackme"
        
    cmd = ["wsl", "-d", "kali-linux", binary_path, key]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        output = res.stdout.strip()
        print(f"    Output: {output}")
        if "Success!" in output:
            print("[+] Solve verification PASSED!")
        else:
            print("[-] Solve verification FAILED!")
    except Exception as e:
        print(f"[-] Could not run crackme: {e}")

if __name__ == "__main__":
    key = solve()
    print("-" * 50)
    verify_with_binary(key)
