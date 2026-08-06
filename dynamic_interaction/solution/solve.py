import socket
import time
import hashlib
import sys

def fibonacci_modulo(n, mod=1000000000):
    if n <= 0:
        return 0
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, (a + b) % mod
    return b

def main():
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = 5002
    
    print(f"[*] Connecting to {host}:{port}...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    
    # --- Stage 1: Algorithm ---
    data = s.recv(1024).decode()
    print(data)
    
    # Parse N from response
    n = None
    for line in data.split("\n"):
        if line.startswith("N = "):
            n = int(line.split(" = ")[1])
            break
            
    if n is None:
        print("[-] Failed to parse N!")
        s.close()
        return
    
    print(f"[*] Calculating Fibonacci({n}) mod 10^9...")
    ans = fibonacci_modulo(n)
    print(f"[+] Sending answer: {ans}")
    s.sendall(f"{ans}\n".encode())
    
    # Read Stage 1 result and Stage 2 prompt
    time.sleep(0.1)
    stage2_prompt = s.recv(1024).decode()
    print(stage2_prompt)
    
    if "Incorrect" in stage2_prompt or "Timeout" in stage2_prompt:
        s.close()
        return
        
    # --- Stage 2: Timing ---
    print("[*] Timing Gate: Waiting exactly 1.5 seconds to send the knock...")
    time.sleep(1.50)
    s.sendall(b"VTCH_OPEN\n")
    
    # Read Stage 2 result and Stage 3 prompt
    time.sleep(0.1)
    stage3_prompt = s.recv(1024).decode()
    print(stage3_prompt)
    
    if "failed" in stage3_prompt:
        s.close()
        return
        
    # --- Stage 3: Hash ---
    # Parse salt from response
    salt = None
    for line in stage3_prompt.split("\n"):
        if line.startswith("Salt = "):
            salt = line.split(" = ")[1].strip()
            break
            
    if not salt:
        print("[-] Failed to parse salt!")
        s.close()
        return
        
    # Hash of salt + Stage 1 answer
    expected_material = f"{salt}{ans}".encode()
    hash_ans = hashlib.sha256(expected_material).hexdigest()
    print(f"[+] Calculated hash: {hash_ans}. Sending...")
    s.sendall(f"{hash_ans}\n".encode())
    
    # Read Flag
    time.sleep(0.1)
    flag_output = s.recv(1024).decode()
    print(flag_output)
    
    s.close()

if __name__ == "__main__":
    main()
