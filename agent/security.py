import subprocess
import re
from datetime import datetime


def run_cmd(cmd: str) -> str:
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True,
            text=True, timeout=10
        )
        return result.stdout.strip()
    except Exception as e:
        return ""


def get_logged_in_users():
    """Who is currently logged in"""
    output = run_cmd("who")
    users = []
    for line in output.splitlines():
        if line.strip():
            parts = line.split()
            if len(parts) >= 4:
                users.append({
                    "user": parts[0],
                    "terminal": parts[1],
                    "login_time": f"{parts[2]} {parts[3]}",
                    "from": parts[4].strip("()") if len(parts) > 4 else "local"
                })
    return users


def get_sudo_usage(limit: int = 20):
    """Recent sudo commands — who ran what"""
    output = run_cmd(
        f'journalctl _COMM=sudo --no-pager -n {limit} '
        f'--output=short-iso 2>/dev/null | grep "COMMAND"'
    )
    entries = []
    for line in output.splitlines():
        if "COMMAND" in line:
            try:
                timestamp = line.split("T")[0] + " " + line.split("T")[1][:8] \
                    if "T" in line else ""
                user_match = re.search(r'sudo:\s+(\w+)', line)
                user = user_match.group(1) if user_match else "unknown"
                cmd_match = re.search(r'COMMAND=(.*)', line)
                command = cmd_match.group(1).strip() if cmd_match else "unknown"
                entries.append({
                    "timestamp": timestamp,
                    "user": user,
                    "command": command[:100]
                })
            except:
                continue
    return entries


def get_ssh_logins(limit: int = 20):
    """Who connected INTO this machine via SSH (inbound)"""
    output = run_cmd(
        f'journalctl _COMM=sshd --no-pager -n 200 '
        f'--output=short-iso 2>/dev/null | grep "Accepted"'
    )
    logins = []
    for line in output.splitlines():
        if "Accepted" in line:
            try:
                timestamp = line.split("T")[0] + " " + line.split("T")[1][:8] \
                    if "T" in line else ""
                user_match = re.search(r'for (\w+) from', line)
                ip_match = re.search(r'from ([\d.]+)', line)
                port_match = re.search(r'port (\d+)', line)
                method_match = re.search(r'Accepted (\w+)', line)

                logins.append({
                    "timestamp": timestamp,
                    "user": user_match.group(1) if user_match else "unknown",
                    "from_ip": ip_match.group(1) if ip_match else "unknown",
                    "port": port_match.group(1) if port_match else "unknown",
                    "method": method_match.group(1) if method_match else "unknown",
                    "direction": "inbound",
                    "status": "success"
                })
            except:
                continue
    return logins[-limit:]


def get_failed_ssh(limit: int = 20):
    """Failed SSH attempts INTO this machine (inbound)"""
    output = run_cmd(
        f'journalctl _COMM=sshd --no-pager -n 500 '
        f'--output=short-iso 2>/dev/null | grep -i "failed\|invalid"'
    )
    failed = []
    for line in output.splitlines():
        if any(x in line.lower() for x in ["failed password", "invalid user"]):
            try:
                timestamp = line.split("T")[0] + " " + line.split("T")[1][:8] \
                    if "T" in line else ""
                user_match = re.search(r'(?:for|user) (\w+)(?: from)?', line)
                ip_match = re.search(r'from ([\d.]+)', line)
                failed.append({
                    "timestamp": timestamp,
                    "user": user_match.group(1) if user_match else "unknown",
                    "from_ip": ip_match.group(1) if ip_match else "unknown",
                    "reason": "Failed password" if "password" in line.lower()
                              else "Invalid user",
                    "direction": "inbound"
                })
            except:
                continue
    return failed[-limit:]


def get_outbound_ssh():
    """
    SSH connections THIS machine made TO other machines (outbound)
    Reads bash history + checks active SSH connections
    """
    results = {
        "active_connections": [],
        "history": []
    }

    # Method 1 — Active outbound SSH connections right now
    active = run_cmd(
        "ss -tnp | grep ':22' | grep ESTAB"
    )
    for line in active.splitlines():
        try:
            parts = line.split()
            # Find remote address (the one that's not local)
            for part in parts:
                if ":" in part and not part.startswith("127") \
                        and not part.startswith("0.0"):
                    ip, port = part.rsplit(":", 1)
                    if port == "22":
                        results["active_connections"].append({
                            "remote_ip": ip,
                            "port": port,
                            "status": "ESTABLISHED"
                        })
        except:
            continue

    # Method 2 — SSH history from bash/zsh history files
    history_cmds = [
        "cat /root/.bash_history 2>/dev/null | grep 'ssh '",
        "cat /root/.zsh_history 2>/dev/null | grep 'ssh '",
        "cat /home/*/.bash_history 2>/dev/null | grep 'ssh '"
    ]

    ssh_history = set()
    for cmd in history_cmds:
        output = run_cmd(cmd)
        for line in output.splitlines():
            line = line.strip()
            if line.startswith("ssh ") or " ssh " in line:
                # Clean up zsh history format (: timestamp:0;ssh ...)
                if ";" in line:
                    line = line.split(";", 1)[-1].strip()
                if line not in ssh_history:
                    ssh_history.add(line)
                    # Parse the ssh command
                    ip_match = re.search(
                        r'ssh\s+(?:\S+@)?([\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3})',
                        line
                    )
                    host_match = re.search(r'ssh\s+(?:\w+@)?([a-zA-Z][\w\.-]+)', line)

                    target = "unknown"
                    if ip_match:
                        target = ip_match.group(1)
                    elif host_match:
                        target = host_match.group(1)

                    results["history"].append({
                        "command": line[:80],
                        "target": target,
                        "direction": "outbound"
                    })

    # Deduplicate history by target
    seen = set()
    unique_history = []
    for h in results["history"]:
        if h["target"] not in seen:
            seen.add(h["target"])
            unique_history.append(h)
    results["history"] = unique_history[:20]

    return results


def get_installed_packages(limit: int = 20):
    """Recently installed packages via apt"""
    output = run_cmd("cat /var/log/apt/history.log 2>/dev/null")
    packages = []
    current = {}

    for line in output.splitlines():
        if line.startswith("Start-Date:"):
            current = {"date": line.replace("Start-Date:", "").strip()}
        elif line.startswith("Commandline:"):
            current["command"] = line.replace("Commandline:", "").strip()
        elif line.startswith("Install:"):
            pkgs = line.replace("Install:", "").strip()
            pkg_names = re.findall(r'(\S+):\S+', pkgs)
            current["packages"] = pkg_names[:5]
        elif line.startswith("End-Date:") and current.get("packages"):
            packages.append(current)
            current = {}

    return packages[-limit:]


def get_security_summary():
    """Master function — all security data"""
    outbound = get_outbound_ssh()
    return {
        "logged_in_users": get_logged_in_users(),
        "sudo_usage": get_sudo_usage(),
        "ssh_inbound_success": get_ssh_logins(),
        "ssh_inbound_failed": get_failed_ssh(),
        "ssh_outbound_active": outbound["active_connections"],
        "ssh_outbound_history": outbound["history"],
        "installed_packages": get_installed_packages(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


if __name__ == "__main__":
    import json
    data = get_security_summary()
    print(json.dumps(data, indent=2))
