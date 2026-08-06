import math
import os
from flask import Flask, render_template, request, jsonify, session

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "ctf_super_secret_key_2026")

FLAG = os.environ.get("FLAG", "VTCH{s4l4m1_sl1c1ng_num3r1c_typ3_c0nfus10n}")

# Base exchange rates relative to USD (1 USD = X Currency)
RATES = {
    "USD": 1.0,
    "EUR": 0.92,
    "JPY": 155.50,
    "MINI": 100.0  # Vulnerable micro-currency
}

# Precision configurations: normal currencies use standard 2 decimal int rounding,
# but MINI calculations use float ceil calculation when converting back to USD.
CURRENCY_TYPES = {
    "USD": {"type": "integer_cents", "decimals": 2},
    "EUR": {"type": "integer_cents", "decimals": 2},
    "JPY": {"type": "integer_units", "decimals": 0},
    "MINI": {"type": "floating_micro", "decimals": 4}  # Type mismatch target
}

TARGET_BALANCE = 500.00  # USD threshold to unlock Flag

def get_wallet():
    if "wallet" not in session:
        session["wallet"] = {
            "USD": 100.00,
            "EUR": 0.00,
            "JPY": 0.00,
            "MINI": 0.00
        }
    return session["wallet"]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/wallet", methods=["GET"])
def wallet_status():
    wallet = get_wallet()
    return jsonify({
        "status": "success",
        "wallet": wallet,
        "target_balance": TARGET_BALANCE
    })

@app.route("/api/exchange", methods=["POST"])
def exchange_currency():
    data = request.get_json() or {}
    from_curr = data.get("from_currency")
    to_curr = data.get("to_currency")
    try:
        amount = float(data.get("amount", 0))
    except (ValueError, TypeError):
        return jsonify({"status": "error", "message": "Invalid amount"}), 400

    if from_curr not in RATES or to_curr not in RATES:
        return jsonify({"status": "error", "message": "Unsupported currency"}), 400

    if amount <= 0:
        return jsonify({"status": "error", "message": "Amount must be positive"}), 400

    wallet = get_wallet()
    if wallet.get(from_curr, 0.0) < amount:
        return jsonify({"status": "error", "message": f"Insufficient {from_curr} balance"}), 400

    # Step 1: Convert `from_curr` to base USD
    if from_curr == "USD":
        usd_value = amount
    elif from_curr == "MINI":
        # Vulnerable calculation: Floating-point conversion with ceiling rounding to nearest cent
        raw_usd = amount / RATES["MINI"]
        # Ceiling rounding: fractions of a cent are rounded UP to the participant's benefit!
        usd_value = math.ceil(raw_usd * 100.0) / 100.0
    else:
        usd_value = amount / RATES[from_curr]

    # Step 2: Convert base USD to `to_curr`
    if to_curr == "USD":
        received_amount = usd_value
    elif to_curr == "MINI":
        # Standard conversion to MINI
        received_amount = round(usd_value * RATES["MINI"], 4)
    else:
        received_amount = round(usd_value * RATES[to_curr], CURRENCY_TYPES[to_curr]["decimals"])

    # Update wallet state
    wallet[from_curr] = round(wallet[from_curr] - amount, 4)
    wallet[to_curr] = round(wallet[to_curr] + received_amount, 4)
    session.modified = True

    return jsonify({
        "status": "success",
        "message": f"Exchanged {amount} {from_curr} for {received_amount} {to_curr}",
        "wallet": wallet
    })

@app.route("/api/flag", methods=["GET"])
def get_flag():
    wallet = get_wallet()
    current_usd = wallet.get("USD", 0.0)
    
    if current_usd >= TARGET_BALANCE:
        return jsonify({
            "status": "success",
            "flag": FLAG,
            "message": "Congratulations! Target balance threshold achieved."
        })
    else:
        return jsonify({
            "status": "error",
            "message": f"Target balance not reached. Current: ${current_usd:.2f} USD, Required: ${TARGET_BALANCE:.2f} USD."
        }), 403

@app.route("/api/reset", methods=["POST"])
def reset_wallet():
    session["wallet"] = {
        "USD": 100.00,
        "EUR": 0.00,
        "JPY": 0.00,
        "MINI": 0.00
    }
    return jsonify({"status": "success", "wallet": session["wallet"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
