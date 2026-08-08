# Writeup — Phantom Transfer

## Challenge Overview
The player is given a packet capture file `transfer_capture.pcapng` showing routine internal API traffic. They must identify a single fraudulent transfer request, extract the base64-obfuscated body, and decode it to recover the flag.

---

## Analysis & Solving Steps

### Step 1: Open the Capture in Wireshark
Open the file `transfer_capture.pcapng` in Wireshark. You will see a series of HTTP packets over port `8080`.

### Step 2: Filter for POST Requests
Filter the traffic to show only POST requests (where transfers are submitted):
```text
http.request.method == "POST"
```

### Step 3: Spot the Outlier
Each transfer has a request payload looking similar to:
```json
{"payload": "eyJmcm9tIjogIjU0MDAxMTAwMDAiLCAidG8iOiAiNTQwMDEyMDAwMCIsICJhbW91bnQiOiAxMzk1NzIsICJtZW1vIjogInBheXJvbGwifQ=="}
```

Notice the length and base64 structure. To find the fraudulent transaction:
1. Examine the size or inspect the raw base64 content of each request.
2. The fraudulent request has a much larger `amount` value (and holds a flag inside the `memo` field), making its base64 payload slightly longer or containing different characters.
3. In Wireshark, select a packet, right-click, and choose **Follow** -> **HTTP Stream**.

### Step 4: Extract and Decode the Payload
Locate the request body of the outlier:
```json
{"payload": "eyJmcm9tIjogIjU0MDAxMTAwMDAiLCAidG8iOiAiTU4wMDAwTVVMRTk5OTkiLCAiYW1vdW50IjogOTk5OTk5OTksICJtZW1vIjogIlZUQ0h7YmFzZTY0X2gxZGQzbl8xbl9wbDQxbl9oNzdwfSJ9"}
```

Extract the base64 string from the `payload` key:
`eyJmcm9tIjogIjU0MDAxMTAwMDAiLCAidG8iOiAiTU4wMDAwTVVMRTk5OTkiLCAiYW1vdW50IjogOTk5OTk5OTksICJtZW1vIjogIlZUQ0h7YmFzZTY0X2gxZGQzbl8xbl9wbDQxbl9oNzdwfSJ9`

Decode it using your terminal or CyberChef:
```bash
echo "eyJmcm9tIjogIjU0MDAxMTAwMDAiLCAidG8iOiAiTU4wMDAwTVVMRTk5OTkiLCAiYW1vdW50IjogOTk5OTk5OTksICJtZW1vIjogIlZUQ0h7YmFzZTY0X2gxZGQzbl8xbl9wbDQxbl9oNzdwfSJ9" | base64 -d
```

### Decoded Output:
```json
{
  "from": "5400110000",
  "to": "MN0000MULE9999",
  "amount": 99999999,
  "memo": "VTCH{base64_h1dd3n_1n_pl41n_h77p}"
}
```

The flag is:
`VTCH{base64_h1dd3n_1n_pl41n_h77p}`
