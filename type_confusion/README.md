# CTF Challenge: Finmob Currency Exchange (Type Confusion & Accumulated Rounding)

## Challenge Details

- **Name**: Finmob Currency Exchange
- **Category**: Web / Logic Vulnerability
- **Classification**: Type Confusion (Numerical Type Mismatch · Accumulated Rounding)
- **Difficulty**: Medium
- **Flag**: `VTCH{s4l4m1_sl1c1ng_num3r1c_typ3_c0nfus10n}`

---

## Problem Overview

Finmob Exchange is a currency trading platform offering multi-currency exchanges (USD, EUR, JPY, MINI). While standard currencies (`USD`, `EUR`, `JPY`) use fixed integer-unit calculations, the `MINI` micro-currency is processed internally using floating-point representation with a ceiling rounding policy (`math.ceil`) when converting back to USD.

Due to this type mismatch, fractional cents resulting from small micro-exchanges are always rounded **up** to the nearest whole cent ($0.01) in favor of the trader. Repeated high-frequency round-trip exchanges (`USD` -> `MINI` -> `USD`) accumulate minute rounding profits, allowing participants to inflate their USD balance infinitely ("Salami Slicing Attack").

---

## Deploying to CTFd

There are two primary methods to deploy this challenge on CTFd:

### Method 1: Manual Deployment (Web GUI)

1. **Host the Challenge Container**:
   Deploy the Docker image on your server or VPS:
   ```bash
   docker build -t finmob-exchange .
   docker run -d -p 5000:5000 --name finmob-exchange finmob-exchange
   ```
2. **Create Challenge in CTFd Admin Panel**:
   - Go to `CTFd Admin` -> `Challenges` -> `Create Challenge`.
   - Select **Standard** category.
   - **Name**: Finmob Exchange
   - **Category**: Web
   - **Message / Description**:
     ```markdown
     Welcome to Finmob Exchange! Trade assets across global currencies.
     High-volume traders who reach $500.00 USD can claim the vault flag.

     http://<YOUR_SERVER_IP>:5000
     ```
   - **Value**: 500
   - **Flag**: `VTCH{s4l4m1_sl1c1ng_num3r1c_typ3_c0nfus10n}`
   - Click **Create Challenge** and set state to **Visible**.

---

### Method 2: Automated Deployment via `ctfcli`

If you use `ctfcli` to manage your CTFd instance:

1. **Install `ctfcli`**:
   ```bash
   pip install ctfcli
   ctf init
   ```
2. **Deploy & Sync Challenge**:
   The directory already includes [challenge.yml](file:///C:/Users/97695/.gemini/antigravity/scratch/currency_rounding_ctf/challenge.yml). Run:
   ```bash
   ctf challenge install .
   ctf challenge sync .
   ```

---

## Environment Setup & Local Testing

### Local Run (Python)
```bash
pip install -r requirements.txt
python app.py
```
App will be running at `http://127.0.0.1:5000`.

---

## Writeup & Solution Walkthrough

### 1. Identifying the Vulnerability
Inspecting `app.py` or analyzing exchange behavior reveals how `MINI` currency converts back to `USD`:

```python
elif from_curr == "MINI":
    raw_usd = amount / RATES["MINI"]  # RATES["MINI"] = 100.0
    usd_value = math.ceil(raw_usd * 100.0) / 100.0
```

Notice:
- `math.ceil` rounds **up** to the nearest cent ($0.01).
- Selling `0.001 MINI`:
  - `raw_usd` = `0.001 / 100` = `0.00001 USD`.
  - `usd_value` = `math.ceil(0.00001 * 100.0) / 100.0` = **`$0.01 USD`**!

### 2. Execution via Solver
```bash
python solver.py http://127.0.0.1:5000
```
Output: `🎉 FLAG CAPTURED: VTCH{s4l4m1_sl1c1ng_num3r1c_typ3_c0nfus10n}`
