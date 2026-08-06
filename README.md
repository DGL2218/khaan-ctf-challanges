# KHAAN CTF Challenges Repository

This repository contains the official challenges for **KHAAN CTF**. Below is the master list of challenges, their categories, copy-pasteable CTFd descriptions, flags, hints, and deployment instructions.

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
* **CTFd Hints**:
  * **Hint 1 (Subtle)**: Try running the program and inspecting its strings. You will notice the flag and correct code are not stored in plaintext. Decompile `main` to see how it verifies the input.
  * **Hint 2 (Moderate)**: Look at the decryption block in `main`. The program reconstructs the expected code dynamically using: `expected[i] = ENC_CODE[i] ^ ((i * 37 + seed) & 0xFF)`. The volatile seed value is `0x5A`.
  * **Hint 3 (Direct)**: Extract the 16-byte `ENC_CODE` array from `.rodata` and write a Python script to reverse the XOR math to reconstruct the 16-character voucher string.
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
* **CTFd Hints**:
  * **Hint 1 (Subtle)**: The code execution flow is flattened inside a massive `switch-case` loop. Focus on documenting what each custom VM opcode (from `0x01` to `0x07`) does rather than following the state variable jumps.
  * **Hint 2 (Moderate)**: Look up "Mixed Boolean-Arithmetic (MBA)" identities to simplify the math inside the VM states. For example, `(A | B) - (A & B)` is a standard logical XOR, and `(A ^ B) + 2*(A & B)` is simple addition.
  * **Hint 3 (Direct)**: The key validation is a rolling XOR check. The target values are checked after adding `0x57`. You can solve this by reversing the steps: subtract `0x57` from each target to get the states, then XOR adjacent states to recover the key characters.
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
* **CTFd Hints**:
  * **Hint 1 (Subtle)**: Inspect the data segment of the client `tokengen` binary. You will find two 16-byte components: `KEYA` and `KEYB`.
  * **Hint 2 (Moderate)**: Reconstruct the key derivation process. The master key is derived by concatenating `KEYA` with a modified `KEYB` (which is reversed and XORed with `0x5A`), and then taking the first 16 bytes of the SHA-256 hash.
  * **Hint 3 (Direct)**: Use the derived master key to sign a forged transaction request payload where `payType=COMP` (internally mapped to `2`) and `cbsn=0000` (internally mapped to `0`). Format the fields alphabetically, zero-padded to 10 digits, separated by `\x1f`, and POST it to the server.
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
* **CTFd Hints**:
  * **Hint 1 (Subtle)**: Inspect how the exchange handles the `MINI` micro-currency. Pay close attention to how floats and integers are handled when converting back to USD.
  * **Hint 2 (Moderate)**: When converting `MINI` to `USD`, the system uses `math.ceil` to round up to the nearest whole cent. How can you abuse this rounding policy using very small trade quantities?
  * **Hint 3 (Direct)**: If you convert a tiny amount of USD to MINI and trade it back in tiny increments (e.g. 0.001 MINI), each transaction rounds up to $0.01 USD. Repeat this "salami slicing" process using a script to inflate your balance to $500.
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
* **CTFd Hints**:
  * **Hint 1 (Subtle)**: List the running processes to understand what scripts are active. Notice the user typist script (`victim.py`) and the application (`secure_app.py`). How do they communicate?
  * **Hint 2 (Moderate)**: The key-protector daemon blocks debugger hooks and traces on `/proc`. However, check `/tmp/` for active communication pipes.
  * **Hint 3 (Direct)**: Locate the named pipe at `/tmp/secure_keyboard.fifo`. Check its file permissions—since it is world-readable, you can simply run `cat` on it to intercept the PIN stream when the automated script writes to it.
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
* **CTFd Hints**:
  * **Hint 1 (Subtle)**: Hardcoding responses will fail since values and hashes are generated dynamically. You must write an interactive script (e.g. using Python's `socket` or `pwntools`) to parse and reply to prompts programmatically.
  * **Hint 2 (Moderate)**: For Stage 2, the server requires a knock at exactly 1.5 seconds. Make sure your script dynamically measures the network latency (time elapsed between sending your Stage 1 answer and receiving the Stage 2 prompt) and subtracts it from your sleep duration to remain in the 1.4-1.6s window.
  * **Hint 3 (Direct)**: In Stage 3, keep track of the answer you sent in Stage 1. Concatenate the parsed server salt with the Stage 1 answer (`salt + str(ans)`) and send the SHA-256 hash in hex format.
* **Deployment & Setup**:
  1. Spin up the socket server (listens on port `5002`):
     ```bash
     cd dynamic_interaction
     docker-compose up -d --build
     ```
  2. Provide players with the connection instruction: `nc <your-server-ip> 5002`.
