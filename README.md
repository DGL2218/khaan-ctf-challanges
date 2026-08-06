# KHAAN CTF Challenges Repository

This repository contains the official challenges for **KHAAN CTF**. Below is the master list of challenges, their categories, copy-pasteable CTFd descriptions, and deployment instructions.

---

## Challenge Summary Table

| Challenge Name | Category | Difficulty | Deployment Type | Flag |
| :--- | :--- | :--- | :--- | :--- |
| **Voucher Validator** | Reverse Engineering | Easy (Warm-up) | Static File Download | `VTCH{n0_fr33_ch4rg3_w1th0ut_RE}` |
| **Obfuscated VM** | Reverse Engineering | Medium | Static File Download | `VTCH{c0ntr0l_fl0w_fl4tt3n1ng_vm_byp4ss}` |
| **Settlement Token** | Web / Cryptography | Medium | Hosted Service (Flask API) | `VTCH{c4n0n1c4l_HMAC_f0rg3d_v1a_spl1t_k3y}` |
| **Type Confusion** | Web / Logic | Medium | Hosted Service (Docker Web App) | `VTCH{s4l4m1_sl1c1ng_num3r1c_typ3_c0nfus10n}` |
| **Anti-Keylogger Bypass** | System / OS | High | Hosted Service (SSH/FIFO) | `VTCH{bypass_unpr0t3ct3d_fifo_hook}` |
| **Dynamic Interaction** | Networking | Medium | Hosted Service (Socket Server) | `VTCH{dyn4m1c_t1m1ng_4nd_puzzl3_byp4ss}` |

---

## 1. Static (File Download) Challenges

### A. Voucher Validator (Warm-up)
* **CTFd Challenge Description**:
  ```markdown
  A VTCH top-up kiosk uses an offline verification program to validate top-up credit vouchers. 
  
  Enter a valid 16-character voucher code to issue a free top-up credit — and print the flag. Can you reverse-engineer the binary and reconstruct the accepted voucher code?
  
  **Format**: Inputs should be alphanumeric and normalized.
  ```
* **Deployment & Setup**:
  1. Compile the binary (requires `gcc`):
     ```bash
     cd voucher_validator
     ./build.sh
     ```
  2. Upload only the compiled `voucher` binary as the challenge file.
  3. **DO NOT** upload `voucher.c`, `build.sh`, or `solve.py`.

### B. Obfuscated VM
* **CTFd Challenge Description**:
  ```markdown
  MoviPay secured their license key validator with custom static analysis defenses to block standard decompilers.
  
  The binary features:
  1. Control Flow Flattening (loop-driven state machine).
  2. Mixed Boolean-Arithmetic (disguised logic math).
  3. Custom Virtual Machine interpreter.
  
  Find the correct 16-character license key to decrypt the payload and print the flag.
  ```
* **Deployment & Setup**:
  1. Compile the binary (requires `gcc`):
     ```bash
     cd obfuscated_vm/challenge
     ./build.sh
     ```
  2. Upload only the compiled `crackme` binary as the challenge file.
  3. **DO NOT** upload `crackme.c`, `build.sh`, or the `solution/` folder.

---

## 2. Dynamic (Hosted Service) Challenges

### A. Settlement Token
* **CTFd Challenge Description**:
  ```markdown
  We intercepted a transaction generator used by MoviPay. The system generates secure MACs to validate transaction details before processing them.
  
  However, the Central Settlement Management System (CSMS) server contains an internal, undocumented path for free settlements when `payType=COMP` and `cbsn=0000`. 
  
  Reconstruct the split master key components from the client generator binary, sign a forged free settlement payload, and submit it to the server to claim the flag.
  ```
* **Deployment & Setup**:
  1. Expose the Flask API server (starts on port `5001`):
     ```bash
     cd settlement_token/challenge
     docker-compose up -d --build
     ```
  2. Distribute the compiled client binary `tokengen` (found in `settlement_token/challenge/`) to players.
  3. Provide players with the server connection details: `http://<your-server-ip>:5001/settle`.

### B. Type Confusion (Finmob Exchange)
* **CTFd Challenge Description**:
  ```markdown
  Welcome to Finmob Currency Exchange! We offer multi-currency exchanges across global currencies. 
  
  Due to system policies, high-volume traders who reach a balance of $500.00 USD can bypass the vault lock and claim the flag. Can you exploit the logic flaw in the exchange system to inflate your balance?
  ```
* **Deployment & Setup**:
  1. Spin up the Docker container (starts on port `5000`):
     ```bash
     cd type_confusion
     docker-compose up -d --build
     ```
  2. Provide players with the link to the web server: `http://<your-server-ip>:5000`.

### C. Anti-Keylogger Bypass
* **CTFd Challenge Description**:
  ```markdown
  We have gained local access to a workstation. An automated process periodically logs in and inputs a transaction PIN (which is the Flag).
  
  The workstation is equipped with an anti-keylogging monitor daemon that blocks standard debuggers and hook observer programs. 
  
  Can you find the security gap in the input pipeline and capture the PIN?
  ```
* **Deployment & Setup**:
  1. Spin up the SSH container (listens on port `2222`):
     ```bash
     cd anti_keylogger_bypass
     docker-compose up -d --build
     ```
  2. Provide players with SSH credentials: `ssh ctf@<your-server-ip> -p 2222` (Password: `ctf`).

### D. Dynamic Interaction
* **CTFd Challenge Description**:
  ```markdown
  The vault gate requires proof of active interaction to open. Standard static analysis tools and hardcoded scripts won't work here. 
  
  You must write a socket client script to solve three stages in real-time:
  1. A fast mathematical Fibonacci challenge modulo 10^9 (within 1.0 second).
  2. A time-sensitive knock (exactly 1.5 seconds later).
  3. A session-dependent SHA-256 hash.
  
  Connect to the server and solve the protocol to claim the flag.
  ```
* **Deployment & Setup**:
  1. Spin up the socket server (listens on port `5002`):
     ```bash
     cd dynamic_interaction
     docker-compose up -d --build
     ```
  2. Provide players with the connection instruction: `nc <your-server-ip> 5002`.
