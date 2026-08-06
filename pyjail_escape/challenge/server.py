import socket
import threading
import sys

def handle_client(client_socket):
    client_socket.settimeout(30.0)
    client_socket.sendall(b"=== Welcome to the Secure Python Sandbox ===\n")
    client_socket.sendall(b"Rules: Commands must be under 35 characters.\n")
    client_socket.sendall(b"No standard execution or import keywords allowed.\n\n")

    # Restricted globals/locals environment
    sandbox_globals = {}
    
    # Blacklisted terms
    blacklist = [
        'os', 'sys', 'import', 'eval', 'exec', 
        'subprocess', 'system', '__builtins__', 
        '__class__', '__dict__', 'compile', 'open'
    ]

    while True:
        try:
            client_socket.sendall(b"pyjail> ")
            user_input = client_socket.recv(1024).decode().strip()
            if not user_input:
                break

            # 1. Length check
            if len(user_input) > 35:
                client_socket.sendall(b"[-] Error: Input exceeds 35 characters limit.\n")
                continue

            # 2. Blacklist check
            blocked = False
            for term in blacklist:
                if term in user_input:
                    client_socket.sendall(f"[-] Error: Keyword '{term}' is blacklisted.\n".encode())
                    blocked = True
                    break
            if blocked:
                continue

            # 3. Execution (eval/exec in isolated environment)
            # We redirect stdout to capture the output of the command
            old_stdout = sys.stdout
            sys.stdout = WriteBuffer(client_socket)
            
            try:
                # We use a simple evaluation or execution
                # Note: we use python's native exec with limited globals
                exec(user_input, sandbox_globals)
            except Exception as e:
                client_socket.sendall(f"[-] Exception: {str(e)}\n".encode())
            finally:
                sys.stdout = old_stdout

        except socket.timeout:
            client_socket.sendall(b"\n[-] Connection timed out.\n")
            break
        except Exception as e:
            client_socket.sendall(f"[-] Error: {str(e)}\n".encode())
            break
    
    client_socket.close()

class WriteBuffer:
    def __init__(self, socket_conn):
        self.socket = socket_conn
    def write(self, data):
        if data:
            self.socket.sendall(data.encode())
    def flush(self):
        pass

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5003))
    server.listen(5)
    print("[*] PyJail server listening on port 5003...")
    
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
