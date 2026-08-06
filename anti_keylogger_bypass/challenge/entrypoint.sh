#!/bin/bash

# Start SSH service
/usr/sbin/sshd

# Start the mock key protector daemon in the background
python3 /app/key_protector.py > /var/log/key_protector.log 2>&1 &

# Start the secure input receiver application in the background
python3 /app/secure_app.py > /var/log/secure_app.log 2>&1 &

# Wait for secure_app.py to create the FIFO at /tmp/secure_keyboard.fifo
sleep 1

# Start the automated victim process in the background
python3 /app/victim.py > /var/log/victim.log 2>&1 &

echo "[*] Anti-keylogger CTF environment successfully booted."

# Keep container running by monitoring SSH daemon
tail -f /dev/null
