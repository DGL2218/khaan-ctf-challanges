import hashlib
import hmac
from flask import Flask, request, jsonify

app = Flask(__name__)

# Master key materials (split in binary)
KEYA = b"MoviPayMasterKey"
KEYB = b"SettlementSecRet"

def derive_key():
    # Reconstruct: material = KEYA || reverse(KEYB) ^ 0x5A
    rev_keyb = bytearray(KEYB[::-1])
    for i in range(len(rev_keyb)):
        rev_keyb[i] ^= 0x5A
    material = KEYA + bytes(rev_keyb)
    h = hashlib.sha256()
    h.update(material)
    return h.digest()[:16]

@app.route('/settle', methods=['POST'])
def settle():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing JSON body"}), 400

        # Required fields for token generation / verification
        required_fields = ["amt", "cbsn", "payType", "sid", "ts", "ver", "mac"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        # Extract parameters
        try:
            amt = int(data["amt"])
            # Keep cbsn as string first to check raw value "0000"
            cbsn_str = str(data["cbsn"])
            cbsn = int(cbsn_str)
            pay_type_str = str(data["payType"])
            sid = int(data["sid"])
            ts = int(data["ts"])
            ver = int(data["ver"])
        except ValueError:
            return jsonify({"error": "Invalid field type/format"}), 400

        client_mac = str(data["mac"])

        # Map payType to integer internally
        # USER -> 1, COMP -> 2
        if pay_type_str == "USER":
            pay_type_int = 1
        elif pay_type_str == "COMP":
            pay_type_int = 2
        else:
            return jsonify({"error": "Unknown payType"}), 400

        # Canonical Rules:
        # 1. Field names in alphabetical order: AMT, CBSN, PAYTYPE, SID, TS, VER
        # 2. Uppercase names
        # 3. 10-digit integer with 0-padding
        # 4. Separator 0x1F (\x1f)
        canonical = (
            f"AMT={amt:010d}\x1f"
            f"CBSN={cbsn:010d}\x1f"
            f"PAYTYPE={pay_type_int:010d}\x1f"
            f"SID={sid:010d}\x1f"
            f"TS={ts:010d}\x1f"
            f"VER={ver:010d}"
        )

        # Derive key and compute HMAC-SHA256
        key = derive_key()
        computed_mac = hmac.new(key, canonical.encode('utf-8'), hashlib.sha256).hexdigest()[:10]

        if client_mac != computed_mac:
            return jsonify({
                "error": "MAC mismatch",
                "status": "failure"
            }), 400

        # Server logic flaw checking:
        # payType == COMP (pay_type_str) and cbsn == "0000" (cbsn_str)
        if pay_type_str == "COMP" and cbsn_str == "0000":
            return jsonify({
                "status": "success",
                "message": "Free settlement path authorized!",
                "flag": "VTCH{c4n0n1c4l_HMAC_f0rg3d_v1a_spl1t_k3y}"
            })
        else:
            return jsonify({
                "status": "success",
                "message": "Legitimate settlement processed."
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run the server
    app.run(host='0.0.0.0', port=5001)
