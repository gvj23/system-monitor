# report.py
import psutil
import socket
import platform
import subprocess
import os
from datetime import datetime

# ─────────────────────────────────────────
# HELPER — run shell command safely
# ─────────────────────────────────────────
def run_cmd(cmd: str) -> str:
    try:
        result = subprocess.run(
            cmd, shell=True,
            capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip() or "No output"
    except Exception as e:
        return f"Command failed: {e}"


# ─────────────────────────────────────────
# SECTION GENERATORS
# ─────────────────────────────────────────

def section(title: str) -> str:
    return f"\n{title}\n" + "-" * 70 + "\n"


def get_system_info() -> str:
    hostname = socket.gethostname()
    uptime_seconds = int(psutil.boot_time())
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime_duration = datetime.now() - boot_time

    days = uptime_duration.days
    hours, remainder = divmod(uptime_duration.seconds, 3600)
    minutes = remainder // 60

    out = section("SYSTEM")
    out += f"Hostname     : {hostname}\n"
    out += f"OS           : {platform.system()} {platform.release()}\n"
    out += f"Architecture : {platform.machine()}\n"
    out += f"Kernel       : {platform.version()}\n"
    out += f"Boot Time    : {boot_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    out += f"Uptime       : {days} days, {hours} hours, {minutes} minutes\n"
    return out


def get_cpu_info() -> str:
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_freq = psutil.cpu_freq()
    load1, load5, load15 = psutil.getloadavg()

    out = section("CPU USAGE")
    out += f"Usage         : {cpu_percent}%\n"
    out += f"Physical Cores: {psutil.cpu_count(logical=False)}\n"
    out += f"Logical Cores : {psutil.cpu_count(logical=True)}\n"
    if cpu_freq:
        out += f"Frequency     : {round(cpu_freq.current, 2)} MHz\n"
    out += f"Load Average  : {load1:.2f} (1m), {load5:.2f} (5m), {load15:.2f} (15m)\n"

    # Per core usage
    out += "\nPer Core Usage:\n"
    for i, percent in enumerate(psutil.cpu_percent(percpu=True)):
        bar = "█" * int(percent / 5) + "░" * (20 - int(percent / 5))
        out += f"  Core {i}  [{bar}] {percent}%\n"

    return out


def get_ram_info() -> str:
    ram = psutil.virtual_memory()
    swap = psutil.swap_memory()

    def to_gb(b): return round(b / (1024 ** 3), 2)

    out = section("MEMORY")
    out += f"{'':5} {'Total':>10} {'Used':>10} {'Free':>10} {'Usage':>8}\n"
    out += f"{'RAM':<5} {to_gb(ram.total):>9}GB {to_gb(ram.used):>9}GB "
    out += f"{to_gb(ram.available):>9}GB {ram.percent:>7}%\n"
    out += f"{'Swap':<5} {to_gb(swap.total):>9}GB {to_gb(swap.used):>9}GB "
    out += f"{to_gb(swap.free):>9}GB {swap.percent:>7}%\n"

    # RAM usage bar
    used_blocks = int(ram.percent / 5)
    bar = "█" * used_blocks + "░" * (20 - used_blocks)
    out += f"\nRAM  [{bar}] {ram.percent}%\n"

    return out


def get_disk_info() -> str:
    out = section("DISK USAGE")
    out += f"{'Partition':<20} {'Total':>8} {'Used':>8} {'Free':>8} {'Use%':>6} {'Mount'}\n"
    out += "-" * 70 + "\n"

    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            def to_gb(b): return f"{round(b / (1024**3), 1)}G"
            out += (
                f"{part.device:<20} "
                f"{to_gb(usage.total):>8} "
                f"{to_gb(usage.used):>8} "
                f"{to_gb(usage.free):>8} "
                f"{usage.percent:>5}% "
                f"{part.mountpoint}\n"
            )
        except PermissionError:
            out += f"{part.device:<20} Permission denied\n"

    return out


def get_network_info() -> str:
    out = section("NETWORK INTERFACES")

    net_if = psutil.net_if_addrs()
    net_stats = psutil.net_if_stats()

    for iface, addrs in net_if.items():
        status = "UP" if net_stats[iface].isup else "DOWN"
        out += f"\n  [{iface}] — {status}\n"
        for addr in addrs:
            if addr.family.name == "AF_INET":
                out += f"    IPv4 : {addr.address}\n"
                out += f"    Mask : {addr.netmask}\n"
            elif addr.family.name == "AF_INET6":
                out += f"    IPv6 : {addr.address}\n"

    # Network IO stats
    io = psutil.net_io_counters()
    out += "\nNetwork IO:\n"
    out += f"  Bytes Sent     : {round(io.bytes_sent / (1024**2), 2)} MB\n"
    out += f"  Bytes Received : {round(io.bytes_recv / (1024**2), 2)} MB\n"
    out += f"  Packets Sent   : {io.packets_sent}\n"
    out += f"  Packets Recv   : {io.packets_recv}\n"

    return out


def get_process_info() -> str:
    out = section("TOP 10 PROCESSES (by CPU)")
    out += f"{'PID':>6} {'Name':<25} {'CPU%':>6} {'RAM%':>6} {'Status'}\n"
    out += "-" * 60 + "\n"

    procs = []
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent',
                                   'memory_percent', 'status']):
        try:
            procs.append(p.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # Sort by CPU usage
    top10 = sorted(procs, key=lambda x: x['cpu_percent'] or 0, reverse=True)[:10]

    for p in top10:
        out += (
            f"{p['pid']:>6} "
            f"{(p['name'] or 'unknown')[:24]:<25} "
            f"{p['cpu_percent'] or 0:>6.1f} "
            f"{p['memory_percent'] or 0:>6.1f} "
            f"{p['status']}\n"
        )

    return out


def get_open_ports() -> str:
    out = section("OPEN PORTS / ACTIVE CONNECTIONS")
    out += f"{'Proto':<6} {'Local Address':<25} {'Remote Address':<25} {'Status'}\n"
    out += "-" * 70 + "\n"

    connections = psutil.net_connections(kind='inet')
    seen = set()

    for conn in connections:
        if conn.laddr:
            local = f"{conn.laddr.ip}:{conn.laddr.port}"
            remote = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "*:*"
            status = conn.status if conn.status else "-"
            proto = "TCP" if conn.type.name == "SOCK_STREAM" else "UDP"

            entry = f"{proto}|{local}|{remote}|{status}"
            if entry not in seen:
                seen.add(entry)
                out += f"{proto:<6} {local:<25} {remote:<25} {status}\n"

    return out


def get_gpu_info() -> str:
    out = section("GPU STATUS")
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            for i, line in enumerate(lines):
                parts = [p.strip() for p in line.split(",")]
                out += f"GPU {i}          : {parts[0]}\n"
                out += f"GPU Usage      : {parts[1]}%\n"
                out += f"VRAM Used      : {parts[2]} MB / {parts[3]} MB\n"
                out += f"Temperature    : {parts[4]}°C\n"
        else:
            out += "No NVIDIA GPU found.\n"
    except FileNotFoundError:
        out += "nvidia-smi not found — No NVIDIA GPU or driver not installed.\n"
    except Exception as e:
        out += f"GPU check failed: {e}\n"

    return out


def get_failed_services() -> str:
    out = section("FAILED SERVICES")
    result = run_cmd("systemctl list-units --state=failed --no-legend")
    out += result if result and result != "No output" else "No failed services ✅\n"
    return out


def get_system_errors() -> str:
    out = section("SYSTEM ERRORS (Today)")
    today = datetime.now().strftime("%Y-%m-%d")
    result = run_cmd(
        f'journalctl --since="{today} 00:00:00" -p err --no-pager | tail -20'
    )
    out += result if result and result != "No output" else "No system errors today ✅\n"
    return out


# ─────────────────────────────────────────
# MASTER REPORT GENERATOR
# ─────────────────────────────────────────

def generate_report() -> str:
    hostname = socket.gethostname()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Header
    report = "=" * 70 + "\n"
    report += "DAILY SERVER HEALTH REPORT\n"
    report += "=" * 70 + "\n"
    report += f"Hostname : {hostname}\n"
    report += f"Date     : {now}\n"
    report += f"Generated: System Monitor Agent v1.0.0\n"

    # Sections
    report += get_system_info()
    report += get_cpu_info()
    report += get_ram_info()
    report += get_disk_info()
    report += get_network_info()
    report += get_process_info()
    report += get_open_ports()
    report += get_gpu_info()
    report += get_failed_services()
    report += get_system_errors()

    # Footer
    report += "\n" + "=" * 70 + "\n"
    report += f"END OF REPORT — {now}\n"
    report += "=" * 70 + "\n"

    return report


def save_report(report: str) -> str:
    """Save report to file with timestamp in filename"""
    os.makedirs("reports", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"reports/Server_Report_{timestamp}.txt"

    with open(filename, "w") as f:
        f.write(report)

    return filename


# ─────────────────────────────────────────
# RUN IT
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("📊 Generating server health report...")
    report = generate_report()

    # Print to terminal
    print(report)

    # Save to file
    filename = save_report(report)
    print(f"\n✅ Report saved to: {filename}")
