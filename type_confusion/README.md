# CTF Challenge: Type Confusion (Finmob Exchange)

## Challenge Details
- **Name**: Type Confusion (Finmob Exchange)
- **Category**: Web
- **Difficulty**: Medium
- **Flag**: `VTCH{s4l4m1_sl1c1ng_num3r1c_typ3_c0nfus10n}`

---

## Deployment Instructions

This challenge requires a hosted web portal running inside a Docker container.

1. **Start the Web App**:
   Spin up the Docker container (starts on port `5000`):
   ```bash
   docker-compose up -d --build
   ```
2. **Accessing the Portal**:
   Expose port `5000` to the internet and provide players with the connection URL: `http://<your-server-ip>:5000`.
3. **Important Security Note**:
   **DO NOT** distribute `solver.py` or the server backend code directly to players.

---

## Solution Walkthrough

The application rounds up exchange values to the nearest whole cent when converting the micro-currency `MINI` back to `USD`. To exploit this logic flaw:

1. **Locate the Vulnerability**:
   Analyze the exchange routes in `app.py`. When selling `MINI` back to `USD`, the system uses `math.ceil` to round up:
   ```python
   raw_usd = amount / RATES["MINI"]
   usd_value = math.ceil(raw_usd * 100.0) / 100.0
   ```
2. **Exploitation**:
   If we sell a very small fraction (e.g. `0.001 MINI`), the raw USD value is `0.00001`. Due to the ceil rounding policy, the user receives `$0.01 USD`!
3. **Salami Slicing Attack**:
   Write a script to automate this transaction loop:
   * Buy `MINI` using USD.
   * Sell the purchased `MINI` back in tiny fractional transactions of `0.001 MINI`.
   * Each fractional transaction profits `$0.01 USD`.
4. **Acquire the Flag**:
   Repeat this transaction loop high-frequency style until the USD balance exceeds `$500.00`, then query the `/api/flag` endpoint to claim the flag.
   
   For the automated solver script, see [solver.py](solver.py).
