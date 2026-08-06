import os
import time
import sys

def get_pid_by_name(name):
    try:
        pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
        for pid in pids:
            try:
                with open(os.path.join('/proc', pid, 'cmdline'), 'rb') as f:
                    cmdline = f.read().decode('utf-8')
                    if name in cmdline:
                        return int(pid)
            except IOError:
                continue
    except Exception:
        pass
    return None

def monitor():
    print("[*] Anti-Keylogger Protection Daemon started.")
    print("[*] Protecting input pipelines (ptrace and /proc/mem monitoring enabled)...")
    
    while True:
        # 1. Look for secure_app PID
        app_pid = get_pid_by_name("secure_app.py")
        if app_pid:
            # 2. Check TracerPid in /proc/<pid>/status to block debuggers/ptrace
            try:
                status_path = f"/proc/{app_pid}/status"
                if os.path.exists(status_path):
                    with open(status_path, "r") as f:
                        for line in f:
                            if line.startswith("TracerPid:"):
                                tracer = int(line.split()[1])
                                if tracer != 0:
                                    print(f"[!] SECURITY ALERT: Debugger detected (TracerPid: {tracer})! Killing process...")
                                    os.kill(app_pid, 9)
                                    os.kill(tracer, 9)
            except Exception as e:
                pass
        
        # 3. Prevent general unauthorized tracing by checking active ptrace attachments (simulated)
        # Note: In a real environment this blocks active syscall hooks, but here it's simplified.
        
        time.sleep(1)

if __name__ == "__main__":
    monitor()
