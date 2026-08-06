# Writeup — Dynamic Interaction

## Challenge Overview
The challenge is designed to enforce **Dynamic Execution and Interaction**, making static flag submission impossible. It requires players to connect to a TCP socket and complete three sequential stages to claim the flag:

1. **Algorithm Gate**: Calculate the $N$-th Fibonacci number modulo $1,000,000,000$ (with $N$ chosen randomly at runtime) in under 1.0 second.
2. **Timing Gate**: Send a knock word exactly 1.5 seconds ($\pm 0.1$ seconds) after receiving the prompt.
3. **State Hash Gate**: Compute the SHA-256 hash of a random server salt concatenated with the Fibonacci result from Stage 1.

---

## Exploitation (Interactive Scripting)

We can write a python socket solver script ([solve.py](file:///C:/Users/97695/OneDrive/Desktop/Stuff/coding/khaan_ctf/khaan-ctf-challanges/dynamic_interaction/solution/solve.py)) to handle the network input/output streams and automate the timing logic.

### 1. Stage 1 Solve: Fibonacci
We parse $N$ from the connection stream and calculate Fibonacci modulo $10^9$ using a fast $O(N)$ loop:
```python
def fibonacci_modulo(n, mod=1000000000):
    if n <= 0:
        return 0
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, (a + b) % mod
    return b
```
Since $N \le 30,000$, this computes in less than a millisecond, comfortably beating the 1-second timeout.

### 2. Stage 2 Solve: Timing
We measure the delay on the client side using `time.sleep(1.5)` before sending `VTCH_OPEN`:
```python
time.sleep(1.50)
s.sendall(b"VTCH_OPEN\n")
```

### 3. Stage 3 Solve: Session State Verification
We parse the random `salt` from the Stage 3 prompt, concatenate it with the Stage 1 answer, and compute the SHA-256 hash:
```python
expected_material = f"{salt}{stage1_ans}".encode()
hash_ans = hashlib.sha256(expected_material).hexdigest()
s.sendall(f"{hash_ans}\n".encode())
```

---

## Capture Flag
Running the solver retrieves the flag:
`VTCH{dyn4m1c_t1m1ng_4nd_puzzl3_byp4ss}`
