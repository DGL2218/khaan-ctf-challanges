# Writeup — Anti-Keylogger Bypass

## Vulnerability Analysis

The mock anti-keylogger protection daemon (`key_protector.py`) is designed with a narrow scope:
1. It monitors `secure_app.py` for debugging attachments (`TracerPid` check in `/proc/<pid>/status`).
2. It blocks standard process hooks and kills common debugging processes.

However, the architecture contains a major security gap: **an insecure IPC (Inter-Process Communication) channel**.

Instead of writing input events through safe kernel-level subsystems or restricted IPC with proper ACLs (Access Control Lists), the automated typist (`victim.py`) writes keyboard entries directly to `/tmp/secure_keyboard.fifo`. 

Because `/tmp/secure_keyboard.fifo` has world-readable permissions (`0666` or `prw-rw-rw-`), any user possessing local access on the machine can open the file descriptor and intercept the streams passing through it.

---

## Exploit Execution

Since the automated typist inputs the PIN every 5 seconds, any reader reading `/tmp/secure_keyboard.fifo` will capture the raw text input.

Running `cat /tmp/secure_keyboard.fifo` intercepts the data, bypassing the debugger check entirely.

### Flag Captured:
`VTCH{bypass_unpr0t3ct3d_fifo_hook}`
