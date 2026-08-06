import os
import time

FIFO_PATH = "/tmp/secure_keyboard.fifo"
FLAG = "VTCH{bypass_unpr0t3ct3d_fifo_hook}"

def main():
    print("[*] Automated User Started. Entering PIN periodically...")
    while True:
        try:
            if os.path.exists(FIFO_PATH):
                # Open in write mode and enter the PIN
                with open(FIFO_PATH, "w") as fifo:
                    fifo.write(f"PIN:{FLAG}\n")
                    fifo.flush()
                print("[+] Typed PIN successfully.")
            else:
                print("[-] Input path not ready. Waiting...")
        except Exception as e:
            print(f"[-] Error writing PIN: {e}")
        time.sleep(5)  # Enter the PIN every 5 seconds

if __name__ == "__main__":
    main()
