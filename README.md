# KHAAN CTF Challenges Repository

This repository contains the official challenges for **KHAAN CTF**. Below is the master list of challenges, their categories, and deployment instructions.

---

## Challenge Summary Table

| Challenge Name | Category | Difficulty | Deployment Type | Flag |
| :--- | :--- | :--- | :--- | :--- |
| **Obfuscated VM** | Reverse Engineering | Medium | Static File Download | `VTCH{c0ntr0l_fl0w_fl4tt3n1ng_vm_byp4ss}` |
| **Voucher Validator** | Reverse Engineering | Easy (Warm-up) | Static File Download | `VTCH{n0_fr33_ch4rg3_w1th0ut_RE}` |
| **Settlement Token** | Web / Cryptography | Medium | Hosted Service (Flask API) | `VTCH{c4n0n1c4l_HMAC_f0rg3d_v1a_spl1t_k3y}` |
| **Type Confusion** | Web / Logic | Medium | Hosted Service (Docker Web App) | `VTCH{s4l4m1_sl1c1ng_num3r1c_typ3_c0nfus10n}` |
| **Anti-Keylogger Bypass** | System / OS | High | Hosted Service (SSH/FIFO) | `VTCH{bypass_unpr0t3ct3d_fifo_hook}` |

---

## 1. Static (File Download) Challenges
These challenges do not require active hosting or servers. You only need to build the binaries and upload them to the CTF platform (e.g., CTFd).

### A. Obfuscated VM
* **Goal**: Players reverse-engineer the stripped binary to find a 16-character license key.
* **Compilation**:
  ```bash
  cd obfuscated_vm/challenge
  ./build.sh
  ```
* **Deployment**:
  1. Create a **Standard** challenge on your CTF platform.
  2. Upload only the compiled `crackme` binary from `obfuscated_vm/challenge/`.
  3. **DO NOT** upload `crackme.c`, `build.sh`, or the `solution/` folder.

### B. Voucher Validator
* **Goal**: Players reverse-engineer a stripped ELF binary to find a valid 16-character voucher code.
* **Compilation**:
  ```bash
  cd voucher_validator
  ./build.sh
  ```
* **Deployment**:
  1. Create a **Standard** challenge.
  2. Upload only the compiled `voucher` binary.
  3. **DO NOT** upload `voucher.c`, `build.sh`, or `solve.py`.

---

## 2. Dynamic (Hosted Service) Challenges
These challenges require hosting a server or Docker container. Players will connect to the server's IP/domain to interact with the challenge.

### A. Type Confusion (Finmob Exchange)
* **Goal**: Web application where players exploit a float-rounding type confusion logic flaw to inflate their balance and claim the flag.
* **Deployment**:
  1. Run the service using Docker Compose:
     ```bash
     cd type_confusion
     docker-compose up -d --build
     ```
  2. The application will start on port `5000`. Set up a reverse proxy (like Nginx) or expose port `5000` to the internet.
  3. Create a **Standard** challenge with the link to the web server: `http://<your-server-ip>:5000`.

### B. Settlement Token
* **Goal**: Web API where players bypass HMAC validation constraints by reconstructing a split key to sign forged transaction payloads.
* **Deployment**:
  1. Start the Flask API server:
     ```bash
     cd settlement_token/challenge
     pip install -r requirements.txt  # If running locally
     python server.py
     ```
     *(Alternatively, write a simple Dockerfile for server.py to containerize it).*
  2. The API is hosted on port `5001`. Provide players with the endpoint: `http://<your-server-ip>:5001/settle`.
  3. Provide players with the binary `tokengen` (if distributing) or describe the hashing rules so they can write their own forged signature generators.

### C. Anti-Keylogger Bypass
* **Goal**: Sniff credentials by targeting an unprotected FIFO communication path to bypass key-hooking monitors.
* **Deployment**:
  1. Run the service using Docker Compose:
     ```bash
     cd anti_keylogger_bypass
     docker-compose up -d --build
     ```
  2. The service exposes SSH port `2222`. Ensure this port is open to players.
  3. Create a **Standard** challenge providing SSH connection details: `ssh ctf@<your-server-ip> -p 2222` (Password: `ctf`).
