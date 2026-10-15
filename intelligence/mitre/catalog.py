"""Comprehensive Versioned MITRE ATT&CK Catalog for SPECTRA-XDR."""

from typing import Dict, List, Optional
from intelligence.mitre.models import MITRETechnique

CATALOG_VERSION = "2.1.0"

MITRE_CATALOG: Dict[str, MITRETechnique] = {
    # 1. Initial Access
    "T1566": MITRETechnique(
        technique_id="T1566",
        technique_name="Phishing",
        tactic="Initial Access",
        description="Adversaries may send phishing messages to gain access to victim systems via spearphishing attachments or links.",
        detection_rationale="Email gateway detection, suspicious attachment execution, or unusual browser outbound links."
    ),
    "T1190": MITRETechnique(
        technique_id="T1190",
        technique_name="Exploit Public-Facing Application",
        tactic="Initial Access",
        description="Adversaries may attempt to exploit a vulnerability in an Internet-facing computer or program.",
        detection_rationale="Web application firewall alerts, anomalous HTTP POST requests, or crash logs in public services."
    ),

    # 2. Execution
    "T1059": MITRETechnique(
        technique_id="T1059",
        technique_name="Command and Scripting Interpreter",
        tactic="Execution",
        description="Adversaries may abuse command and script interpreters to execute commands, scripts, or binaries.",
        detection_rationale="Execution of command line interpreters (cmd.exe, bash, sh) detected in telemetry."
    ),
    "T1059.001": MITRETechnique(
        technique_id="T1059.001",
        technique_name="PowerShell",
        tactic="Execution",
        subtechnique_id="T1059.001",
        description="Adversaries may abuse PowerShell commands and scripts for execution and fileless attack payloads.",
        detection_rationale="PowerShell script execution, encoded commands (-enc), or bypass arguments detected."
    ),
    "T1204": MITRETechnique(
        technique_id="T1204",
        technique_name="User Execution",
        tactic="Execution",
        description="Adversaries may rely on the actions of a user to execute malicious code via link clicks or downloaded binaries.",
        detection_rationale="Process spawn from user desktop, Downloads directory, or temporary zip archives."
    ),

    # 3. Persistence
    "T1053": MITRETechnique(
        technique_id="T1053",
        technique_name="Scheduled Task/Job",
        tactic="Persistence",
        description="Adversaries may abuse task scheduling functionality to facilitate initial or recurring execution.",
        detection_rationale="Cron job addition, systemd timers, or Windows Task Scheduler modification detected."
    ),
    "T1547": MITRETechnique(
        technique_id="T1547",
        technique_name="Boot or Logon Autostart Execution",
        tactic="Persistence",
        description="Adversaries may configure system settings to automatically execute a program during system boot or logon.",
        detection_rationale="Registry Run/RunOnce key creation or startup folder additions detected by FIM."
    ),

    # 4. Privilege Escalation
    "T1068": MITRETechnique(
        technique_id="T1068",
        technique_name="Exploitation for Privilege Escalation",
        tactic="Privilege Escalation",
        description="Adversaries may exploit software vulnerabilities to elevate privileges on an endpoint.",
        detection_rationale="Sudo/su privilege escalation, kernel exploit attempts, or vulnerability scanner activity."
    ),
    "T1548": MITRETechnique(
        technique_id="T1548",
        technique_name="Abuse Elevation Control Mechanism",
        tactic="Privilege Escalation",
        description="Adversaries may circumvent mechanisms designed to control elevate privileges (e.g., UAC bypass or setuid).",
        detection_rationale="UAC bypass registry modifications, slui.exe / fodhelper.exe high integrity launches."
    ),

    # 5. Defense Evasion
    "T1078": MITRETechnique(
        technique_id="T1078",
        technique_name="Valid Accounts",
        tactic="Defense Evasion",
        description="Adversaries may obtain and abuse credentials of existing accounts to mask their presence.",
        detection_rationale="Successful authentication after multiple failures or anomalous user login hours."
    ),
    "T1070.004": MITRETechnique(
        technique_id="T1070.004",
        technique_name="File Deletion / Artifact Wiping",
        tactic="Defense Evasion",
        subtechnique_id="T1070.004",
        description="Adversaries may delete files left behind by the actions of their software to evade detection.",
        detection_rationale="Rapid creation and deletion of temporary executable files or ransomware canary notes."
    ),
    "T1562": MITRETechnique(
        technique_id="T1562",
        technique_name="Impair Defenses",
        tactic="Defense Evasion",
        description="Adversaries may maliciously modify system security settings or stop antivirus/EDR services.",
        detection_rationale="Stopping WazuhSvc, disabling Windows Defender, or clearing security event logs."
    ),

    # 6. Credential Access
    "T1110": MITRETechnique(
        technique_id="T1110",
        technique_name="Brute Force",
        tactic="Credential Access",
        description="Adversaries may use brute force techniques to attempt access to accounts via password guessing.",
        detection_rationale="Multiple authentication failures, SSH/RDP repeated logon failure alerts."
    ),
    "T1003": MITRETechnique(
        technique_id="T1003",
        technique_name="OS Credential Dumping",
        tactic="Credential Access",
        description="Adversaries may attempt to dump credentials from memory or filesystem to obtain plaintext passwords.",
        detection_rationale="Access to LSASS process memory, mimikatz signatures, or SAM database extraction."
    ),

    # 7. Discovery
    "T1082": MITRETechnique(
        technique_id="T1082",
        technique_name="System Information Discovery",
        tactic="Discovery",
        description="An adversary may attempt to get detailed information about the operating system and hardware.",
        detection_rationale="Execution of systeminfo, uname -a, or hostname enumeration commands."
    ),
    "T1046": MITRETechnique(
        technique_id="T1046",
        technique_name="Network Service Discovery",
        tactic="Discovery",
        description="Adversaries may attempt to get a listing of services running on remote hosts and local networks.",
        detection_rationale="High volume of SYN packets, port scans (nmap, internal scanner) hitting endpoint ports."
    ),
    "T1033": MITRETechnique(
        technique_id="T1033",
        technique_name="System Owner/User Discovery",
        tactic="Discovery",
        description="Adversaries may attempt to identify the primary user, currently logged-in user, or set of users.",
        detection_rationale="Execution of whoami, whoami /priv, net user, or id commands in rapid succession."
    ),

    # 8. Lateral Movement
    "T1021": MITRETechnique(
        technique_id="T1021",
        technique_name="Remote Services",
        tactic="Lateral Movement",
        description="Adversaries may use valid accounts to log into remote service environments via RDP, SSH, or SMB.",
        detection_rationale="Remote login activity, SMB pipe connections, or port 3389/22 network connections."
    ),
    "T1570": MITRETechnique(
        technique_id="T1570",
        technique_name="Lateral Tool Transfer",
        tactic="Lateral Movement",
        description="Adversaries may transfer tools or files between systems in an environment to facilitate lateral movement.",
        detection_rationale="SMB/RPC copy of executable files to administrative shares (C$, ADMIN$)."
    ),

    # 9. Collection
    "T1005": MITRETechnique(
        technique_id="T1005",
        technique_name="Data from Local System",
        tactic="Collection",
        description="Adversaries may search local system sources, such as the file system or sensitive databases, to find files of interest.",
        detection_rationale="Access or archiving of sensitive document directories (.kdbx, passwords.txt, id_rsa)."
    ),

    # 10. Command and Control
    "T1071": MITRETechnique(
        technique_id="T1071",
        technique_name="Application Layer Protocol",
        tactic="Command and Control",
        description="Adversaries may communicate using application layer protocols (HTTP/HTTPS, DNS) to avoid detection.",
        detection_rationale="Periodic beaconing traffic to unknown external IPs or anomalous User-Agent strings."
    ),
    "T1071.001": MITRETechnique(
        technique_id="T1071.001",
        technique_name="Web Protocols (HTTP/HTTPS)",
        tactic="Command and Control",
        subtechnique_id="T1071.001",
        description="Adversaries may communicate using application layer web protocols to blend in with normal network traffic.",
        detection_rationale="Regular interval outbound HTTP requests to non-standard ports or suspicious RedTeam headers."
    ),

    # 11. Exfiltration
    "T1048": MITRETechnique(
        technique_id="T1048",
        technique_name="Exfiltration Over Alternative Protocol",
        tactic="Exfiltration",
        description="Adversaries may steal data by transferring it over an alternative network protocol than the main C2.",
        detection_rationale="High volume DNS tunneling or FTP upload to untrusted destination IPs."
    ),

    # 12. Impact
    "T1486": MITRETechnique(
        technique_id="T1486",
        technique_name="Data Encrypted for Impact",
        tactic="Impact",
        description="Adversaries may encrypt data on target systems to interrupt availability of system and network resources.",
        detection_rationale="Mass file extension modifications, sudden IOPS spike, or canary ransomware notes."
    ),
    "T1489": MITRETechnique(
        technique_id="T1489",
        technique_name="Service Stop",
        tactic="Impact",
        description="Adversaries may stop or disable services on a system to render those services or functions unavailable.",
        detection_rationale="net stop commands executed against critical enterprise or security services."
    ),
}

# Rule Group & Decoder Mappings for Automatic Telemetry Classification
GROUP_MAPPINGS: Dict[str, List[str]] = {
    "authentication_failed": ["T1110"],
    "authentication_failures": ["T1110"],
    "sshd": ["T1021", "T1110"],
    "pam": ["T1078"],
    "sudo": ["T1068"],
    "syscheck": ["T1486", "T1070.004"],
    "powershell": ["T1059.001"],
    "cmd": ["T1059"],
    "windows_application": ["T1059"],
}

# Rule ID Mappings
RULE_MAPPINGS: Dict[str, List[str]] = {
    "5710": ["T1110"],        # SSHD authentication failure
    "5711": ["T1110"],        # SSHD brute force
    "5716": ["T1021"],        # SSHD authentication success
    "5501": ["T1068"],        # PAM session opened
    "91800": ["T1059.001"],   # PowerShell execution
    "60642": ["T1053"],       # Scheduled service task
    "T1059.001": ["T1059.001"],
    "T1082": ["T1082"],
    "T1046": ["T1046"],
    "T1053.005": ["T1053"],
    "T1070.004": ["T1070.004"],
    "T1071.001": ["T1071.001"],
}


class MITRECatalog:
    """Provides access to the local versioned MITRE ATT&CK catalog."""

    def get_technique(self, technique_id: str) -> Optional[MITRETechnique]:
        return MITRE_CATALOG.get(technique_id)

    def list_techniques(self) -> List[MITRETechnique]:
        return list(MITRE_CATALOG.values())
