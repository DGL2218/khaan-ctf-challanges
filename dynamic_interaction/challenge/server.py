import socket
import threading
import random
import time
import hashlib
import os

FLAG = "VTCH{dyn4m1c_t1m1ng_4nd_puzzl3_byp4ss}"

def fibonacci_modulo(n, mod=1000000000):
    # Fast matrix exponentiation or simple iterative method
    if n <= 0:
        return 0
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, (a + b) % mod
    return b

def handle_client(client_socket):
    client_socket.settimeout(3.0)
    try:
        # --- STAGE 1: Algorithm Gate ---
        n = random.randint(10000, 30000)
        client_socket.sendall(f"=== STAGE 1: Algorithm Gate ===\nCalculate the {n}-th Fibonacci number modulo 1,000,000,000.\nYou have 1 second!\nN = {n}\n".encode())
        
        start_time = time.time()
        ans_raw = client_socket.recv(1024).decode().strip()
        elapsed = time.time() - start_time
        
        if elapsed > 1.0:
            client_socket.sendall(b"[-] Timeout in Stage 1! Too slow.\n")
            return
            
        try:
            client_ans = int(ans_raw)
        except ValueError:
            client_socket.sendall(b"[-] Invalid response format in Stage 1.\n")
            return
            
        correct_ans = fibonacci_modulo(n)
        if client_ans != correct_ans:
            client_socket.sendall(b"[-] Incorrect answer for Stage 1.\n")
            return
            
        client_socket.sendall(b"[+] Stage 1 Passed!\n\n")
        
        # --- STAGE 2: Timing Gate ---
        client_socket.sendall(b"=== STAGE 2: Timing Gate ===\nSend the secret knock 'VTCH_OPEN' exactly 1.5 seconds from now.\n(We accept a precision window of 1.4 to 1.6 seconds)\nGO!\n")
        
        start_time = time.time()
        knock_raw = client_socket.recv(1024).decode().strip()
        elapsed = time.time() - start_time
        
        if knock_raw != "VTCH_OPEN":
            client_socket.sendall(b"[-] Incorrect knock word.\n")
            return
            
        if not (1.4 <= elapsed <= 1.6):
            client_socket.sendall(f"[-] Timing Gate failed! You knocked at {elapsed:.3f} seconds.\n".encode())
            return
            
        client_socket.sendall(b"[+] Stage 2 Passed!\n\n")
        
        # --- STAGE 3: State Hash Gate ---
        salt = os.urandom(8).hex()
        client_socket.sendall(f"=== STAGE 3: State Hash Gate ===\nCompute the SHA-256 hash of the following salt concatenated with your Stage 1 answer:\nFormat: sha256(salt + str(stage1_ans))\nSalt = {salt}\n".encode())
        
        hash_ans = client_socket.recv(1024).decode().strip()
        
        expected_material = f"{salt}{correct_ans}".encode()
        expected_hash = hashlib.sha256(expected_material).hexdigest()
        
        if hash_ans != expected_hash:
            client_socket.sendall(b"[-] Incorrect hash. Access Denied.\n")
            return
            
        # Success!
        client_socket.sendall(f"[+] All stages passed! Here is your flag:\n{FLAG}\n".encode())
        
    except socket.timeout:
        client_socket.sendall(b"[-] Connection timed out.\n")
    except Exception as e:
        client_socket.sendall(f"[-] Error: {str(e)}\n".encode())
    finally:
        client_socket.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5002))
    server.listen(5)
    print("[*] Dynamic Interaction server listening on port 5002...")
    
    while True:
        try:
            client_sock, addr = server.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_sock,))
            client_thread.daemon = True
            client_thread.start()
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[-] Server error: {e}")

if __name__ == "__main__":
    main()
