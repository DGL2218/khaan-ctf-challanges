# CTF Challenge: Phantom Transfer

## Challenge Details
- **Name**: Phantom Transfer
- **Category**: Forensics
- **Difficulty**: Easy
- **Flag**: `VTCH{base64_h1dd3n_1n_pl41n_h77p}`

---

## Deployment Instructions

This is an **offline forensics** challenge, so no active hosting or servers are required.

1. **Generation (Optional)**:
   The capture file `challenge/transfer_capture.pcapng` is pre-generated in the repository. If you ever need to re-generate it, run the Python script in WSL (requires `sudo` for packet capture privileges):
   ```bash
   sudo python3 generate_pcap.py
   ```
2. **Distribution**:
   Upload only the generated **`transfer_capture.pcapng`** (located in the `challenge/` folder) to the CTF challenge page.
3. **Important Security Note**:
   **DO NOT** distribute `generate_pcap.py`, the `solution/` folder, or `solve.py`.

---

## Solution Walkthrough

1. **Wireshark Filter**:
   Open the pcap file in Wireshark and filter for HTTP POST requests to find the transaction endpoints:
   ```text
   http.request.method == "POST"
   ```
2. **Find the Outlier**:
   Scan through the POST requests. Look for the transaction with a large base64 length or inspect the payloads. One transaction routes a massive `$99,999,999` to a mule account.
3. **Extract and Decode**:
   Follow the HTTP Stream of the outlier transaction. Extract the base64-encoded `payload` string and decode it:
   ```bash
   echo "<base64_payload>" | base64 -d
   ```
   The decoded JSON object contains the flag in the `memo` field.

For the automated solver script, see [solution/solve.py](solution/solve.py) and the writeup in [solution/writeup.md](solution/writeup.md).
