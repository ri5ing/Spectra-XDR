"""Static Versioned MITRE ATT&CK Local Catalog for SPECTRA-XDR."""

from typing import Dict, List, Optional
from intelligence.mitre.models import MITRETechnique

CATALOG_VERSION = "1.0.0"

# Initial versioned MITRE ATT&CK Catalog matching supported Wazuh rule patterns
MITRE_CATALOG: Dict[str, MITRETechnique] = {
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
        description="Adversaries may abuse PowerShell commands and scripts for execution.",
        detection_rationale="PowerShell script execution or command line invocation detected."
    ),
    "T1110": MITRETechnique(
        technique_id="T1110",
        technique_name="Brute Force",
        tactic="Credential Access",
        description="Adversaries may use brute force techniques to attempt access to accounts.",
        detection_rationale="Multiple authentication failures or SSH/RDP brute force alerts detected."
    ),
    "T1078": MITRETechnique(
        technique_id="T1078",
        technique_name="Valid Accounts",
        tactic="Defense Evasion",
        description="Adversaries may obtain and abuse credentials of existing accounts.",
        detection_rationale="Successful authentication after multiple failures or anomalous user session."
    ),
    "T1021": MITRETechnique(
        technique_id="T1021",
        technique_name="Remote Services",
        tactic="Lateral Movement",
        description="Adversaries may use Valid Accounts to log into remote service environments.",
        detection_rationale="Remote login activity via SSH, RDP, or SMB detected."
    ),
    "T1068": MITRETechnique(
        technique_id="T1068",
        technique_name="Exploitation for Privilege Escalation",
        tactic="Privilege Escalation",
        description="Adversaries may exploit software vulnerabilities to elevate privileges.",
        detection_rationale="Sudo/su privilege escalation or vulnerability scanner execution detected."
    ),
    "T1486": MITRETechnique(
        technique_id="T1486",
        technique_name="Data Encrypted for Impact",
        tactic="Impact",
        description="Adversaries may encrypt data on target systems to interrupt availability.",
        detection_rationale="Mass file modification or ransomware extension activity detected."
    ),
    "T1003": MITRETechnique(
        technique_id="T1003",
        technique_name="OS Credential Dumping",
        tactic="Credential Access",
        description="Adversaries may attempt to dump credentials to obtain account login info.",
        detection_rationale="Access to LSASS process memory or SAM database read detected."
    ),
    "T1053": MITRETechnique(
        technique_id="T1053",
        technique_name="Scheduled Task/Job",
        tactic="Persistence",
        description="Adversaries may abuse task scheduling functionality to facilitate initial or recurring execution.",
        detection_rationale="Cron job addition or Windows Task Scheduler modification detected."
    ),
}

# Rule Group & Decoder Mappings
GROUP_MAPPINGS: Dict[str, List[str]] = {
    "authentication_failed": ["T1110"],
    "authentication_failures": ["T1110"],
    "sshd": ["T1021", "T1110"],
    "pam": ["T1078"],
    "sudo": ["T1068"],
    "syscheck": ["T1486"],
    "powershell": ["T1059.001"],
    "cmd": ["T1059"],
}

# Rule ID Mappings
RULE_MAPPINGS: Dict[str, List[str]] = {
    "5710": ["T1110"],        # SSHD authentication failure
    "5711": ["T1110"],        # SSHD brute force
    "5716": ["T1021"],        # SSHD authentication success
    "5501": ["T1068"],        # PAM session opened
    "91800": ["T1059.001"],   # PowerShell execution
}


class MITRECatalog:
    """Provides access to the local versioned MITRE ATT&CK catalog."""

    def get_technique(self, technique_id: str) -> Optional[MITRETechnique]:
        return MITRE_CATALOG.get(technique_id)

    def list_techniques(self) -> List[MITRETechnique]:
        return list(MITRE_CATALOG.values())
