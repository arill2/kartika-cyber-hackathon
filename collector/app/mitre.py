"""Pemetaan MITRE ATT&CK untuk POLARIS (ringkas dari docs/12-mitre-mapping.md)."""

# event_type -> daftar teknik
TECHNIQUES = {
    "decoy_connection": [
        ("T1046", "Network Service Scanning", "Discovery"),
    ],
    "web_decoy_hit": [
        ("T1595", "Active Scanning", "Reconnaissance"),
    ],
    "decoy_login_attempt": [
        ("T1110", "Brute Force", "Credential Access"),
    ],
    "honeytoken_file_access": [
        ("T1083", "File and Directory Discovery", "Discovery"),
        ("T1552", "Unsecured Credentials", "Credential Access"),
    ],
    "canary_cred_used": [
        ("T1552", "Unsecured Credentials", "Credential Access"),
        ("T1078", "Valid Accounts", "Defense Evasion"),
    ],
    "honeytoken_url_fetch": [
        ("T1071", "Application Layer Protocol", "Command and Control"),
        ("T1595", "Active Scanning", "Reconnaissance"),
    ],
    "decoy_ot_touch": [
        ("T0846", "Remote System Discovery", "ICS - Discovery"),
        ("T0812", "Default Credentials", "ICS - Credential Access"),
    ],
}

# khusus decoy OT / service tertentu
SERVICE_EXTRA = {
    "modbus": [("T0835", "Manipulate I/O Image", "ICS - Impact")],
    "ssh": [("T1021.004", "Remote Services: SSH", "Lateral Movement")],
    "mysql": [("T1190", "Exploit Public-Facing Application", "Initial Access")],
    "hmi": [("T0836", "Modify Parameter", "ICS - Impact")],
}


def map_event(event_type: str, service: str = "") -> list[dict]:
    out: list[dict] = []
    seen: set[str] = set()
    for tid, name, tactic in TECHNIQUES.get(event_type, []):
        if tid not in seen:
            seen.add(tid)
            out.append({"id": tid, "name": name, "tactic": tactic})
    for tid, name, tactic in SERVICE_EXTRA.get(service or "", []):
        if tid not in seen:
            seen.add(tid)
            out.append({"id": tid, "name": name, "tactic": tactic})
    return out
