# metrics.py
import psutil
import socket
import platform
import subprocess
import json
from datetime import datetime
from security import get_security_summary

def get_cpu_metrics():
    """Get CPU usage percentage and core count"""
    return {
        "usage_percent": psutil.cpu_percent(interval=1),
        "core_count": psutil.cpu_count(logical=True),
        "physical_cores": psutil.cpu_count(logical=False),
        "frequency_mhz": round(psutil.cpu_freq().current, 2) if psutil.cpu_freq() else None
    }


def get_ram_metrics():
    """Get RAM usage details"""
    ram = psutil.virtual_memory()
    return {
        "total_gb": round(ram.total / (1024 ** 3), 2),
        "used_gb": round(ram.used / (1024 ** 3), 2),
        "available_gb": round(ram.available / (1024 ** 3), 2),
        "usage_percent": ram.percent
    }


def get_disk_metrics():
    """Get disk usage for root"""
    disk = psutil.disk_usage("/")
    return {
        "total_gb": round(disk.total / (1024 ** 3), 2),
        "used_gb": round(disk.used / (1024 ** 3), 2),
        "free_gb": round(disk.free / (1024 ** 3), 2),
        "usage_percent": disk.percent
    }


def get_uptime():
    """Get system uptime"""
    boot_time = psutil.boot_time()
    boot_datetime = datetime.fromtimestamp(boot_time)
    uptime_duration = datetime.now() - boot_datetime

    total_seconds = int(uptime_duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    return {
        "boot_time": boot_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        "uptime_string": f"{uptime_duration.days}d {hours % 24}h {minutes}m",
        "uptime_seconds": total_seconds
    }


def get_system_info():
    """Get PC name, IP, OS details"""
    hostname = socket.gethostname()
    try:
        ip_address = socket.gethostbyname(hostname)
    except:
        ip_address = "unknown"

    return {
        "hostname": hostname,
        "ip_address": ip_address,
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.machine()
    }


# ─────────────────────────────────────────
# NEW FUNCTIONS
# ─────────────────────────────────────────

def get_per_core_usage():
    """Per core CPU breakdown"""
    return [
        {"core": i, "usage": percent}
        for i, percent in enumerate(psutil.cpu_percent(percpu=True))
    ]


def get_top_processes():
    """Top 10 processes by CPU"""
    procs = []
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent',
                                   'memory_percent', 'status']):
        try:
            procs.append(p.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    top10 = sorted(procs, key=lambda x: x['cpu_percent'] or 0, reverse=True)[:10]
    return top10


def get_open_ports():
    """Active network connections"""
    connections = []
    seen = set()

    for conn in psutil.net_connections(kind='inet'):
        if conn.laddr:
            local = f"{conn.laddr.ip}:{conn.laddr.port}"
            remote = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "*:*"
            proto = "TCP" if conn.type.name == "SOCK_STREAM" else "UDP"
            entry = f"{proto}|{local}|{remote}"

            if entry not in seen:
                seen.add(entry)
                connections.append({
                    "proto": proto,
                    "local": local,
                    "remote": remote,
                    "status": conn.status or "-"
                })

    return connections[:30]


def get_network_io():
    """Network IO stats"""
    io = psutil.net_io_counters()
    return {
        "bytes_sent_mb": round(io.bytes_sent / (1024**2), 2),
        "bytes_recv_mb": round(io.bytes_recv / (1024**2), 2),
        "packets_sent": io.packets_sent,
        "packets_recv": io.packets_recv
    }


def get_failed_services():
    """Check for failed systemd services"""
    try:
        result = subprocess.run(
            "systemctl list-units --state=failed --no-legend",
            shell=True, capture_output=True, text=True, timeout=5
        )
        output = result.stdout.strip()
        return output if output else "none"
    except:
        return "unknown"


def get_system_errors():
    """Today's system errors from journalctl"""
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        result = subprocess.run(
            f'journalctl --since="{today} 00:00:00" -p err --no-pager | tail -5',
            shell=True, capture_output=True, text=True, timeout=5
        )
        lines = result.stdout.strip().split("\n")
        return [l for l in lines if l.strip()]
    except:
        return []


# ─────────────────────────────────────────
# MASTER FUNCTION — collects everything
# ─────────────────────────────────────────

def collect_all_metrics():
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "system": get_system_info(),
        "cpu": get_cpu_metrics(),
        "cpu_cores": get_per_core_usage(),
        "ram": get_ram_metrics(),
        "disk": get_disk_metrics(),
        "network_io": get_network_io(),
        "processes": get_top_processes(),
        "ports": get_open_ports(),
        "failed_services": get_failed_services(),
        "system_errors": get_system_errors(),
        "uptime": get_uptime(),
        "security": get_security_summary(),
    }


# ─────────────────────────────────────────
# THIS IS WHAT WAS MISSING — run block!
# ─────────────────────────────────────────

if __name__ == "__main__":
    data = collect_all_metrics()
    print(json.dumps(data, indent=2))
