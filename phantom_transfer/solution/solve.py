import subprocess
import json
import base64
import sys
import os

def main():
    # Use command line arg or fallback to default path
    pcap_file = sys.argv[1] if len(sys.argv) > 1 else "challenge/transfer_capture.pcapng"
    
    if not os.path.exists(pcap_file):
        # Fallback for running from inside solution/ folder
        pcap_file = "../challenge/transfer_capture.pcapng"
        
    if not os.path.exists(pcap_file):
        print(f"[-] Error: Capture file '{pcap_file}' not found.")
        sys.exit(1)
        
    print(f"[*] Analyzing capture file: {pcap_file}...")
    
    # Command to extract HTTP request payloads via tshark
    cmd = [
        "tshark", "-r", pcap_file,
        "-Y", "http.request.method == \"POST\"",
        "-T", "fields", "-e", "http.file_data"
    ]
    
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    
    if proc.returncode != 0:
        print(f"[-] tshark error: {stderr.decode()}")
        sys.exit(1)
        
    payloads = stdout.decode().strip().split("\n")
    print(f"[*] Extracted {len(payloads)} POST request payloads.")
    
    for raw_payload in payloads:
        if not raw_payload:
            continue
            
        try:
            # If tshark returned hex representation, convert it back to ASCII
            try:
                decoded_raw = bytes.fromhex(raw_payload).decode('utf-8')
            except ValueError:
                decoded_raw = raw_payload
                
            # Parse outer JSON wrapper: {"payload": "..."}
            data = json.loads(decoded_raw)
            b64_payload = data.get("payload", "")
            
            # Base64 decode inner JSON payload
            decoded = base64.b64decode(b64_payload).decode()
            txn = json.loads(decoded)
            
            # Check if the memo field contains our flag
            memo = txn.get("memo", "")
            if "VTCH{" in memo:
                print("\n[+] Found Fraudulent Transaction!")
                print(f"    From Account: {txn.get('from')}")
                print(f"    To Account:   {txn.get('to')}")
                print(f"    Amount:       ${txn.get('amount'):,}")
                print(f"    Memo (Flag):  {memo}\n")
                return
        except Exception:
            continue
            
    print("[-] Exploit FAILED: Flag not found in pcap payloads.")

if __name__ == "__main__":
    main()
