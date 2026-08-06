import hashlib
import hmac
import subprocess
import requests
import sys
import os

# Server endpoint
SERVER_URL = "http://100.91.148.10:5000/settle"

# Step 1: Reconstruct the split key
KEYA = b"MoviPayMasterKey"
KEYB = b"SettlementSecRet"

def derive_key():
    # material = KEYA || reverse(KEYB) ^ 0x5A
    rev_keyb = bytearray(KEYB[::-1])
    for i in range(len(rev_keyb)):
        rev_keyb[i] ^= 0x5A
    material = KEYA + bytes(rev_keyb)
    h = hashlib.sha256()
    h.update(material)
    return h.digest()[:16]

def compute_local_mac(amt, cbsn, pay_type_int, sid, ts, ver):
    # Canonical string construction
    canonical = (
        f"AMT={amt:010d}\x1f"
        f"CBSN={cbsn:010d}\x1f"
        f"PAYTYPE={pay_type_int:010d}\x1f"
        f"SID={sid:010d}\x1f"
        f"TS={ts:010d}\x1f"
        f"VER={ver:010d}"
    )
    key = derive_key()
    return hmac.new(key, canonical.encode('utf-8'), hashlib.sha256).hexdigest()[:10]

def test_binary_alignment():
    print("[*] Testing alignment with tokengen binary...")
    
    # Define test parameters for a legitimate USER request
    amt = 100
    cbsn = 1234
    sid = 42
    ts = 1719876543
    ver = 1
    
    # 1. Compute MAC locally in Python (USER -> payType 1)
    py_mac = compute_local_mac(amt, cbsn, 1, sid, ts, ver)
    
    # 2. Run tokengen binary in WSL (since it's an ELF)
    binary_path = "../challenge/tokengen"
    if not os.path.exists(binary_path):
        binary_path = "./challenge/tokengen"
        
    cmd = [
        "wsl", "-d", "kali-linux", binary_path,
        "--amt", str(amt),
        "--cbsn", str(cbsn),
        "--sid", str(sid),
        "--ts", str(ts),
        "--ver", str(ver)
    ]
    
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        bin_mac = res.stdout.strip()
        print(f"    Python MAC: {py_mac}")
        print(f"    Binary MAC: {bin_mac}")
        
        if py_mac == bin_mac:
            print("[+] Alignment test PASSED! Key derivation and canonicalization formats match.")
            return True
        else:
            print("[-] Alignment test FAILED! MAC mismatch.")
            return False
    except Exception as e:
        print(f"[-] Could not run tokengen binary: {e}")
        print("    (Continuing with forgery using Python-derived keys...)")
        return True

def forge_and_submit():
    print("[*] Forging token for COMP settlement...")
    
    # Parameters for the free settlement path
    # payType = COMP, cbsn = 0000
    amt = 100
    cbsn_str = "0000"
    cbsn = 0
    pay_type_str = "COMP"
    pay_type_int = 2 # COMP maps to 2
    sid = 42
    ts = 1719876543
    ver = 1
    
    # Compute MAC for the forged request
    mac = compute_local_mac(amt, cbsn, pay_type_int, sid, ts, ver)
    print(f"    Forged MAC: {mac}")
    
    # Submit payload to CSMS
    payload = {
        "amt": amt,
        "cbsn": cbsn_str,
        "payType": pay_type_str,
        "sid": sid,
        "ts": ts,
        "ver": ver,
        "mac": mac
    }
    
    print(f"[*] Submitting request to {SERVER_URL}...")
    try:
        res = requests.post(SERVER_URL, json=payload)
        print(f"    Status Code: {res.status_code}")
        print(f"    Response: {res.text}")
    except Exception as e:
        print(f"[-] Connection to server failed: {e}")

if __name__ == "__main__":
    # Test alignment with binary if possible
    test_binary_alignment()
    print("-" * 50)
    # Forge and submit
    forge_and_submit()
