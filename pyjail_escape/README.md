# CTF Challenge: Python Jail Escape

## Challenge Details
- **Name**: Python Jail Escape
- **Category**: Misc
- **Difficulty**: Medium
- **Flag**: `VTCH{pyth0n_s4ndb0x_3sc4p3_succ3ss}`

---

## Deployment Instructions

This challenge requires a hosted socket server running inside a Docker container.

1. **Start the Sandbox Server**:
   Spin up the Docker container (starts on port `5003`):
   ```bash
   cd pyjail_escape
   docker-compose up -d --build
   ```
2. **Accessing the Shell**:
   Expose TCP port `5003` to the internet and provide players with the connection instruction: `nc <your-server-ip> 5003`.
3. **Important Security Note**:
   **DO NOT** distribute the solver `solve.py` or the server backend code directly to players.

---

## Solution Walkthrough

The application evaluates user Python commands under strict constraints:
- Input must be **under 35 characters**.
- Standard keywords like `open`, `import`, `os`, `sys`, and `eval` are **blacklisted**.

### Exploit Strategy:

1. **Locate Sandbox Bypasses**:
   We need a way to read files without using the `open()` builtin (which is blacklisted).
2. **The `__loader__` Trick**:
   Python 3 introduces a built-in namespace attribute called `__loader__` which exposes import mechanisms. One of its methods is `get_data(path)`, which retrieves raw file data:
   ```python
   __loader__.get_data("flag.txt")
   ```
3. **Drafting the Payload**:
   Let's check the size and characters:
   `print(__loader__.get_data("flag.txt"))`
   - Length: **38 characters**. Too long (exceeds the 35 character limit).
   - Can we write it without print? The `exec()` block in `server.py` redirects `sys.stdout` but does not automatically print evaluated expression outputs unless we call `print` or write to stdout.
   - Wait! How can we print it in under 35 characters?
     - Using `print()` is necessary because `sys.stdout` is captured.
     - Can we shorten the path?
       - Yes! The file is `/app/flag.txt`, but we are running in `/app/`, so the relative path is `flag.txt`.
       - Can we use `open`? No, it's blocked.
       - Is there another way?
         - What about `__import__`? Blocked.
         - What about `__builtins__`? Blocked.
         - What about `sys`? Blocked.
         - What about `open` via `__builtins__`? Blocked.
         - Wait! Can we print `__loader__.get_data("flag.txt")` directly if we use Python 3.11's builtins?
         - Wait, how long is `__loader__.get_data("flag.txt")`? It has 30 characters.
         - What if we write to stdout directly?
           - `sys.stdout.write(...)` requires `sys` which is blocked.
         - Wait! Is there an print alias? No.
         - What if we shorten `__loader__.get_data`? E.g., `d = __loader__.get_data` (23 chars), then `print(d("flag.txt"))` (19 chars). That's two separate commands!
           - The jail is a loop (`while True`) that maintains globals state across inputs!
           - So the player can split their exploit into **two separate inputs**:
             1. `d=__loader__.get_data` (23 chars - accepted!)
             2. `print(d("flag.txt"))` (20 chars - accepted!)
             This is an incredibly clever and simple solution! It perfectly fits the 35-character limit constraint.
             
   For the automated solver script, see [solution/solve.py](solution/solve.py) and the writeup in [solution/writeup.md](solution/writeup.md).
