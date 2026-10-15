"""Defensive Security Telemetry Verification Script for Spectra-XDR.

Generates standard benign diagnostic events to test Wazuh detection rules
and Spectra-XDR AI Swarm telemetry ingestion without harmful behavior.
"""

import sys
import os
import subprocess
import time
import urllib.request
import json

SPECTRA_BACKEND_URL = "http://192.168.0.104:8000"

def log(msg: str):
    print(f"[*] {msg}")

def check_connectivity():
    log(f"Testing connectivity to Spectra-XDR Brain at {SPECTRA_BACKEND_URL}...")
    try:
        req = urllib.request.urlopen(f"{SPECTRA_BACKEND_URL}/health", timeout=5)
        if req.status == 200:
            data = json.loads(req.read().decode())
            print(f"[+] Connected to Spectra-XDR! Status: {data.get('status')} | Service: {data.get('app')}")
            return True
    except Exception as e:
        print(f"[-] Could not reach Spectra backend at {SPECTRA_BACKEND_URL}: {e}")
        print("    Ensure both laptops are on the same Wi-Fi and port 8000 is allowed through Windows Firewall.")
        return False

def test_discovery_audit():
    """Trigger benign Windows audit events (MITRE T1087 / T1082: Account & System Discovery)."""
    log("Executing benign system discovery commands (audited by Wazuh & Windows Security Event 4688)...")
    commands = [
        ["whoami", "/priv"],
        ["net", "user"],
        ["systeminfo"]
    ]
    for cmd in commands:
        try:
            print(f"    Running: {' '.join(cmd)}")
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"    Error: {e}")
    print("[+] Benign discovery telemetry events generated.")

def send_test_security_event():
    """Directly submit a test security telemetry event to Spectra-XDR Event ingestion pipeline."""
    log("Sending test event to Spectra-XDR event ingestion API...")
    url = f"{SPECTRA_BACKEND_URL}/api/v1/events"
    payload = {
        "event_id": f"TEST-TEL-{int(time.time())}",
        "source": "remote_laptop",
        "agent_id": "002",
        "agent_name": "Secondary-Laptop",
        "agent_ip": "192.168.0.x",
        "rule_id": "T1059",
        "rule_level": 7,
        "rule_description": "Suspicious PowerShell Command Line Audit (Telemetry Verification)",
        "event_type": "alert",
        "raw_event": {
            "technique": "T1059.001",
            "action": "benign_verification",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status in (200, 201):
                print("[+] Event successfully ingested into Spectra-XDR!")
                print("    Open http://localhost:3000 to see it live in Command Center and Alerts table.")
    except Exception as e:
        print(f"[-] Failed to send event to backend: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print(" SPECTRA-XDR // Benign Security Telemetry Verification Tool")
    print("=" * 60)
    check_connectivity()
    print("-" * 60)
    test_discovery_audit()
    print("-" * 60)
    send_test_security_event()
    print("=" * 60)
