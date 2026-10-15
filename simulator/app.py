import os
import sys
import json
import time
import socket
import asyncio
import subprocess
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(
    title="Spectra RedTeam Live Attack Simulator",
    version="1.0.0",
    description="Standalone RedTeam & Threat Simulation Suite with Mobile Responsive Dashboard"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

EXECUTION_HISTORY: List[Dict[str, Any]] = []

ATTACK_SCENARIOS = [
    {
        "id": "T1059.001",
        "name": "PowerShell Encoded Command & Recon",
        "tactic": "Execution / Discovery",
        "severity": "HIGH",
        "description": "Simulates suspicious base64 obfuscated PowerShell execution retrieving host identity, process tree, and privileges.",
        "mitre_technique": "T1059.001",
        "command_type": "powershell",
        "payload": "powershell -NoProfile -Command \"whoami /priv; Get-Process | Select-Object -First 5 Name, Id, CPU; Write-Output '[SIMULATION] Adversary Discovery Complete.'\""
    },
    {
        "id": "T1082",
        "name": "System Information & Environment Harvesting",
        "tactic": "Discovery",
        "severity": "MEDIUM",
        "description": "Enumerates OS architecture, active network connections, logged in users, and security settings.",
        "mitre_technique": "T1082",
        "command_type": "cmd",
        "payload": "cmd.exe /c \"systeminfo | findstr /B /C:\"OS Name\" /C:\"OS Version\" /C:\"System Type\" & net user & ipconfig /all\""
    },
    {
        "id": "T1046",
        "name": "Local Subnet Port Reconnaissance Scan",
        "tactic": "Discovery",
        "severity": "MEDIUM",
        "description": "Scans common network services (SSH 22, HTTP 80, SMB 445, RDP 3389, Wazuh 1514, API 8000) on the target IP.",
        "mitre_technique": "T1046",
        "command_type": "port_scan",
        "payload": "INTERNAL_SCANNER"
    },
    {
        "id": "T1053.005",
        "name": "Scheduled Task Persistence Check",
        "tactic": "Persistence",
        "severity": "HIGH",
        "description": "Simulates adversary persistence checking by querying highest-privilege scheduled tasks and startup items.",
        "mitre_technique": "T1053.005",
        "command_type": "powershell",
        "payload": "powershell -NoProfile -Command \"Get-ScheduledTask | Select-Object -First 10 TaskName, State; Write-Output '[SIMULATION] Task Persistence Scan Finished.'\""
    },
    {
        "id": "T1070.004",
        "name": "File Integrity Monitoring (FIM) Canary Dropper",
        "tactic": "Defense Evasion",
        "severity": "CRITICAL",
        "description": "Creates a suspicious canary indicator file in the Temp directory with simulated ransomware notes to trigger Wazuh FIM/Syscheck.",
        "mitre_technique": "T1070.004",
        "command_type": "powershell",
        "payload": "powershell -NoProfile -Command \"$path = Join-Path $env:TEMP 'SPECTRA_RANSOM_CANARY.txt'; Set-Content -Path $path -Value 'WARNING: ALL YOUR ASSETS ARE ENCRYPTED BY SPECTRA SIMULATION. Contact redteam@spectra.local'; Get-Item $path | Select-Object FullName, Length, LastWriteTime\""
    },
    {
        "id": "T1071.001",
        "name": "C2 Beaconing Emulation (HTTP Pingback)",
        "tactic": "Command and Control",
        "severity": "HIGH",
        "description": "Generates simulated Command & Control periodic outbound beacon traffic to target port.",
        "mitre_technique": "T1071.001",
        "command_type": "http_ping",
        "payload": "INTERNAL_BEACON"
    }
]

class AttackExecutionRequest(BaseModel):
    scenario_id: str
    target_ip: str
    custom_param: Optional[str] = None

def get_discovered_network_ips() -> List[Dict[str, str]]:
    ips = [
        {
            "ip": "127.0.0.1",
            "name": "Localhost (Loopback)",
            "type": "Local Endpoint / EDR Agent",
            "status": "Online"
        }
    ]
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.connect(("8.8.8.8", 80))
        host_ip = s.getsockname()[0]
        s.close()
        ips.append({
            "ip": host_ip,
            "name": f"Host Interface ({socket.gethostname()})",
            "type": "Primary Host Machine",
            "status": "Reachable"
        })
    except Exception:
        pass

    try:
        output = subprocess.check_output("arp -a", shell=True, text=True, timeout=2)
        for line in output.splitlines():
            line = line.strip()
            parts = line.split()
            if len(parts) >= 3:
                cand_ip = parts[0]
                mac = parts[1]
                if cand_ip.count(".") == 3 and not cand_ip.startswith("224.") and not cand_ip.startswith("239.") and not cand_ip.endswith(".255"):
                    if not any(item["ip"] == cand_ip for item in ips):
                        role = "Gateway / Router" if cand_ip.endswith(".1") else "LAN Endpoint / Device"
                        ips.append({
                            "ip": cand_ip,
                            "name": f"Device ({mac})",
                            "type": role,
                            "status": "Reachable"
                        })
    except Exception:
        pass

    return ips

@app.get("/api/network/ips")
def list_network_ips():
    return {"status": "success", "ips": get_discovered_network_ips()}

@app.get("/api/scenarios")
def list_scenarios():
    return {"status": "success", "scenarios": ATTACK_SCENARIOS}

@app.get("/api/history")
def get_history():
    return {"status": "success", "history": EXECUTION_HISTORY[-20:]}

@app.post("/api/simulate")
async def trigger_simulation(req: AttackExecutionRequest):
    scenario = next((s for s in ATTACK_SCENARIOS if s["id"] == req.scenario_id), None)
    if not scenario:
        raise HTTPException(status_code=404, detail="Attack scenario not found")

    target_ip = req.target_ip.strip()
    execution_record = {
        "id": f"SIM-{int(time.time()*1000)}",
        "scenario_id": scenario["id"],
        "scenario_name": scenario["name"],
        "tactic": scenario["tactic"],
        "severity": scenario["severity"],
        "target_ip": target_ip,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "status": "Executing...",
        "output": "",
        "return_code": 0
    }

    try:
        cmd_type = scenario.get("command_type")
        
        if cmd_type == "port_scan":
            ports = [22, 80, 443, 445, 1514, 3000, 3389, 8000, 8443]
            open_ports = []
            scan_log = [f"[*] Initiating TCP SYN/Connect Scan against target {target_ip}...", f"[*] Testing ports: {ports}"]
            
            for p in ports:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.35)
                res = sock.connect_ex((target_ip, p))
                if res == 0:
                    open_ports.append(p)
                    scan_log.append(f"[+] Port {p}/TCP is OPEN on {target_ip}")
                sock.close()
                
            scan_log.append(f"[*] Recon Completed: {len(open_ports)} open port(s) discovered: {open_ports}")
            execution_record["output"] = "\n".join(scan_log)
            execution_record["status"] = "COMPLETED"
            execution_record["return_code"] = 0

        elif cmd_type == "http_ping":
            beacon_log = [
                f"[*] Emulating Adversary C2 Beaconing to {target_ip}:8000/api/v1/health...",
                f"[*] Sending 3 synthetic HTTP heartbeats with RedTeam user-agent..."
            ]
            import urllib.request
            success_count = 0
            for i in range(1, 4):
                try:
                    req_obj = urllib.request.Request(
                        f"http://{target_ip}:8000/api/v1/health",
                        headers={"User-Agent": "Spectra-RedTeam-Beacon/1.0 (Simulation)"}
                    )
                    with urllib.request.urlopen(req_obj, timeout=1.5) as resp:
                        beacon_log.append(f"[+] Beacon {i}/3 sent. Response status: {resp.status}")
                        success_count += 1
                except Exception as ex:
                    beacon_log.append(f"[-] Beacon {i}/3 note: {ex}")
                time.sleep(0.3)
            
            beacon_log.append(f"[*] C2 Beacon test finished. Successful hits: {success_count}/3")
            execution_record["output"] = "\n".join(beacon_log)
            execution_record["status"] = "COMPLETED"
            execution_record["return_code"] = 0

        else:
            payload = scenario["payload"]
            proc = subprocess.run(payload, shell=True, capture_output=True, text=True, timeout=15)
            out = (proc.stdout or "") + "\n" + (proc.stderr or "")
            execution_record["output"] = out.strip() or "[OK] Command executed successfully without stdout."
            execution_record["return_code"] = proc.returncode
            execution_record["status"] = "COMPLETED" if proc.returncode == 0 else "WARNING/EXIT_NON_ZERO"

            # 1. Forward directly to Windows Application EventChannel so Wazuh agent harvests it
            try:
                ev_msg = f"[REDTEAM SIMULATION] {scenario['id']} - {scenario['name']} executed against {target_ip}. Severity: {scenario['severity']}"
                ps_event = f"Write-EventLog -LogName 'Application' -Source 'Wsh' -EventId 1001 -EntryType Warning -Message '{ev_msg}' -ErrorAction SilentlyContinue"
                subprocess.run(["powershell", "-NoProfile", "-Command", ps_event], timeout=3)
            except Exception:
                pass

            # 2. Ingest telemetry directly into Spectra-XDR Event Stream (Port 8000)
            try:
                import urllib.request
                event_payload = {
                    "event_id": f"SIM-{scenario['id']}-{int(time.time()*1000)}",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "source": "wazuh_agent",
                    "agent_id": "002",
                    "agent_name": "Lazasus",
                    "agent_ip": target_ip,
                    "rule_id": scenario["id"],
                    "rule_level": 10 if scenario["severity"] == "CRITICAL" else 7,
                    "rule_description": f"[ADVERSARY ATTACK SIMULATION] {scenario['name']} ({scenario['mitre_technique']})",
                    "event_type": "alert",
                    "location": "RedTeam-Simulator",
                    "raw_event": {
                        "attack_id": scenario["id"],
                        "tactic": scenario["tactic"],
                        "target_ip": target_ip,
                        "output": execution_record["output"][:300]
                    }
                }
                req = urllib.request.Request(
                    "http://localhost:8000/api/v1/events",
                    data=json.dumps(event_payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=2) as resp:
                    pass
            except Exception:
                pass

    except Exception as e:
        execution_record["status"] = "FAILED"
        execution_record["output"] = f"Execution error: {str(e)}"
        execution_record["return_code"] = 1

    EXECUTION_HISTORY.append(execution_record)
    return {"status": "success", "result": execution_record}

@app.get("/", response_class=HTMLResponse)
def index_page():
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    print(f"[*] Starting Spectra Attack Simulator on http://0.0.0.0:{port}")
    uvicorn.run("simulator.app:app", host="0.0.0.0", port=port, reload=False)
