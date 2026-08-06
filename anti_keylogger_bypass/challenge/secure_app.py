import os
import time

FIFO_PATH = "/tmp/secure_keyboard.fifo"

def main():
    print("[*] Secure App started. Waiting for keystrokes...")
    
    # Create the named pipe (FIFO) if it doesn't exist
    if not os.path.exists(FIFO_PATH):
        os.mkfifo(FIFO_PATH)
        # Vulnerability: World-readable permissions allow local users to sniff keystrokes
        os.chmod(FIFO_PATH, 0o666)

    while True:
        try:
            # Read from the FIFO (blocks until a writer connects)
            with open(FIFO_PATH, "r") as fifo:
                for line in fifo:
                    line = line.strip()
                    if line.startswith("PIN:"):
                        pin = line.split(":", 1)[1]
                        print("[*] Received PIN verification request. Processing...")
                        time.sleep(0.5)
                        if pin == "VTCH{bypass_unpr0t3ct3d_fifo_hook}":
                            print("[+] Access Granted!")
                        else:
                            print("[-] Invalid PIN!")
        except Exception as e:
            print(f"[-] Error reading from input path: {e}")
        time.sleep(0.5)

if __name__ == "__main__":
    main()
