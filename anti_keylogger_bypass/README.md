# CTF Challenge: Anti-Keylogger Bypass

## Challenge Details
- **Name**: Anti-Keylogger Bypass
- **Category**: System / OS Internals
- **Difficulty**: Medium
- **Flag**: `VTCH{bypass_unpr0t3ct3d_fifo_hook}`

---

## Deployment Instructions

1. **Deploy using Docker Compose**:
   ```bash
   cd anti_keylogger_bypass
   docker-compose up -d --build
   ```
2. **Accessing the Container**:
   The challenge container runs an SSH daemon on port `2222`. Players connect using:
   ```bash
   ssh ctf@<server_ip> -p 2222
   # Password: ctf
   ```

---

## Solution Walkthrough

1. **Analyze Running Processes**:
   Check what is running on the local system:
   ```bash
   ps -ef
   ```
   You will notice three main scripts: `secure_app.py`, `victim.py`, and `key_protector.py`.

2. **Discover the Input Pipeline**:
   Examine how `victim.py` communicates with `secure_app.py`. Under `/tmp/`, you will locate a named pipe (FIFO) at `/tmp/secure_keyboard.fifo`.

3. **Check Permissions**:
   Inspect the file details of the FIFO:
   ```bash
   ls -la /tmp/secure_keyboard.fifo
   ```
   The pipe is world-readable (`prw-rw-rw-`). This allows any local user, including the low-privilege `ctf` user, to read its content.

4. **Sniff the PIN**:
   Simply read from the named pipe to capture the flag:
   ```bash
   cat /tmp/secure_keyboard.fifo
   ```
   Since the automated script writes the PIN every 5 seconds, you will capture `PIN:VTCH{bypass_unpr0t3ct3d_fifo_hook}` in a matter of seconds.
