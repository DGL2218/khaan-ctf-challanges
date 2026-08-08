import os
import sys
import time
import json
import base64
import random
import urllib.request
import urllib.error
import subprocess
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Mock HTTP Request Handler
class MockRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress logging to keep output clean
        return

    def do_POST(self):
        if self.path == '/api/v1/transfer':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Respond with 200 OK
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "accepted"}')
        else:
            self.send_response(404)
            self.end_headers()

def run_server(server):
    server.serve_forever()

def main():
    # Make sure output directory exists
    os.makedirs("challenge", exist_ok=True)
    
    server_address = ('127.0.0.1', 8080)
    httpd = HTTPServer(server_address, MockRequestHandler)
    
    # Start server in background thread
    server_thread = threading.Thread(target=run_server, args=(httpd,))
    server_thread.daemon = True
    server_thread.start()
    print("[*] Mock HTTP server started on http://127.0.0.1:8080")

    # Start tcpdump on loopback interface
    # Output file: challenge/transfer_capture.pcapng
    pcap_path = "challenge/transfer_capture.pcapng"
    
    print("[*] Starting tcpdump capture...")
    tcpdump_proc = subprocess.Popen(
        ["tcpdump", "-i", "lo", "-w", pcap_path, "port", "8080"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Give tcpdump a moment to initialize
    time.sleep(1.5)

    url = 'http://127.0.0.1:8080/api/v1/transfer'
    headers = {'Content-Type': 'application/json'}

    # Generate 12 legitimate transfers before the malicious one
    print("[*] Generating legitimate transactions...")
    for i in range(12):
        body = {
            'from': '5400110000',
            'to': f'54001200{i:02d}',
            'amount': random.randint(10000, 200000),
            'memo': 'payroll'
        }
        payload = base64.b64encode(json.dumps(body).encode()).decode()
        data = json.dumps({'payload': payload}).encode()
        
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        try:
            with urllib.request.urlopen(req) as response:
                response.read()
        except urllib.error.URLError as e:
            print(f"[-] Request failed: {e.reason}")
        
        time.sleep(random.uniform(0.05, 0.2))

    # Inject the malicious transfer
    print("[*] Injecting fraudulent transaction (Flag payload)...")
    evil = {
        'from': '5400110000',
        'to': 'MN0000MULE9999',
        'amount': 99999999,
        'memo': 'VTCH{base64_h1dd3n_1n_pl41n_h77p}'
    }
    payload = base64.b64encode(json.dumps(evil).encode()).decode()
    data = json.dumps({'payload': payload}).encode()
    
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req) as response:
            response.read()
    except urllib.error.URLError as e:
        print(f"[-] Malicious request failed: {e.reason}")
        
    time.sleep(random.uniform(0.05, 0.2))

    # Generate 6 more legitimate transfers after the malicious one
    print("[*] Generating post-exploit transactions...")
    for i in range(12, 18):
        body = {
            'from': '5400110000',
            'to': f'54001200{i:02d}',
            'amount': random.randint(10000, 200000),
            'memo': 'payroll'
        }
        payload = base64.b64encode(json.dumps(body).encode()).decode()
        data = json.dumps({'payload': payload}).encode()
        
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        try:
            with urllib.request.urlopen(req) as response:
                response.read()
        except urllib.error.URLError as e:
            print(f"[-] Request failed: {e.reason}")
            
        time.sleep(random.uniform(0.05, 0.2))

    # Give tcpdump a moment to capture the final packets
    time.sleep(1.5)
    
    # Terminate tcpdump
    print("[*] Stopping tcpdump capture...")
    tcpdump_proc.terminate()
    tcpdump_proc.wait()

    # Shutdown HTTP server
    print("[*] Stopping mock HTTP server...")
    httpd.shutdown()
    
    # Ensure correct permissions on the generated pcap file
    if os.path.exists(pcap_path):
        os.chmod(pcap_path, 0o666)
        print(f"[+] Capture file successfully saved to: {pcap_path}")
    else:
        print("[-] Error: Capture file was not created.")

if __name__ == '__main__':
    # Force run with root/sudo if capturing packets
    if os.geteuid() != 0:
        print("[-] This script must be run with root/sudo privileges to capture loopback interface packets.")
        sys.exit(1)
    main()
