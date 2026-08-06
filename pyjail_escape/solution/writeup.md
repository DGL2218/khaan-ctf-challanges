# Writeup — Python Jail Escape

## Vulnerability Analysis

The Python sandbox (`server.py`) implements a standard blacklist filter and a strict input length limit:
1. Blocked words: `['os', 'sys', 'import', 'eval', 'exec', 'subprocess', 'system', '__builtins__', '__class__', '__dict__', 'compile', 'open']`
2. Max command length: **35 characters**.

To capture the flag, we need to read `/app/flag.txt` under these constraints.

---

## Exploitation (Sandbox Bypass)

1. **Bypassing `open`**: 
   Since `open` is blacklisted, we need an alternative way to read files. In Python 3, `__loader__` (a built-in import loader) contains the method `get_data(path)`, which reads and returns file bytes directly:
   ```python
   __loader__.get_data("flag.txt")
   ```
   This does not use `open` or require importing any packages, bypassing the blacklist completely.

2. **Bypassing the 35-character Length Limit**:
   We want to read the file and print it:
   ```python
   print(__loader__.get_data("flag.txt"))
   ```
   However, this statement is **38 characters** long, which is rejected by the length filter.
   
   To bypass this, we leverage the fact that the server maintains the execution state globally inside a `while` loop. We can split our exploit payload into **two separate commands**, both under the 35-character limit:
   
   * **Command 1**: Save the getter method to a shorter variable `d`:
     ```python
     d=__loader__.get_data
     ```
     *(Length: 23 characters)*
     
   * **Command 2**: Execute and print the flag:
     ```python
     print(d("flag.txt"))
     ```
     *(Length: 20 characters)*

---

## Flag Capture
Running these two commands in sequence extracts the flag:
`VTCH{pyth0n_s4ndb0x_3sc4p3_succ3ss}`
