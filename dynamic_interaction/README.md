# CTF Challenge: Dynamic Interaction

## Challenge Details
- **Name**: Dynamic Interaction
- **Category**: Networking / Scripting
- **Difficulty**: Medium
- **Flag**: `VTCH{dyn4m1c_t1m1ng_4nd_puzzl3_byp4ss}`

---

## Deployment Instructions

1. **Deploy using Docker Compose**:
   ```bash
   cd dynamic_interaction
   docker-compose up -d --build
   ```
2. **Accessing the Container**:
   The challenge listens on TCP port `5002`. Expose this port to the players.
   ```bash
   nc <server_ip> 5002
   ```

---

## Solution Walkthrough

This challenge cannot be solved statically since:
- Stage 1 generates a **random number $N$** and demands the $N$-th Fibonacci number modulo $10^9$ in less than 1.0 second.
- Stage 2 demands a message after **exactly 1.5 seconds** (window: 1.4 to 1.6 seconds).
- Stage 3 demands a **SHA-256 hash** that concatenates a random salt with the answer from Stage 1.

### Exploit Strategy:
Players must write a socket client (e.g., in Python using `socket` or `pwntools`) to:
1. Connect to the socket on port `5002`.
2. Parse the random $N$ from the greeting.
3. Compute the Fibonacci number $Fib(N) \pmod{10^9}$ dynamically using a fast $O(N)$ or $O(\log N)$ algorithm, and send it immediately.
4. Wait exactly 1.5 seconds.
5. Send the string `VTCH_OPEN`.
6. Parse the random salt from the Stage 3 prompt.
7. Compute `sha256(salt + str(fib_ans))` and send the hex digest.
8. Receive and print the flag.
