import socket
import subprocess
import concurrent.futures
import nmap
from datetime import datetime


def get_local_ip():
    """Get this machine's IP"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "192.168.1.1"


def get_network_range():
    """Auto detect network range e.g. 192.168.1.0/24"""
    local_ip = get_local_ip()
    parts = local_ip.split(".")
    return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"


def ping_host(ip: str) -> bool:
    """Check if host is alive"""
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "1", ip],
            capture_output=True, timeout=2
        )
        return result.returncode == 0
    except:
        return False


def get_hostname(ip: str) -> str:
    """Try to resolve hostname"""
    try:
        return socket.gethostbyaddr(ip)[0]
    except:
        return "unknown"


def scan_ports(ip: str, ports=[22, 80, 443, 3306, 8080, 8000, 5432, 27017]):
    """Check common ports on a host"""
    open_ports = []
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((ip, port))
            if result == 0:
                # Try to get service name
                try:
                    service = socket.getservbyport(port)
                except:
                    service = "unknown"
                open_ports.append({
                    "port": port,
                    "service": service
                })
            sock.close()
        except:
            pass
    return open_ports


def scan_network():
    """
    Scan entire local network
    Returns list of active hosts with open ports
    """
    network = get_network_range()
    local_ip = get_local_ip()

    print(f"🔍 Scanning network: {network}")

    # Generate all IPs in range
    base = ".".join(local_ip.split(".")[:3])
    all_ips = [f"{base}.{i}" for i in range(1, 255)]

    # Ping scan in parallel (fast)
    active_ips = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        results = {executor.submit(ping_host, ip): ip for ip in all_ips}
        for future in concurrent.futures.as_completed(results):
            ip = results[future]
            if future.result():
                active_ips.append(ip)

    print(f"✅ Found {len(active_ips)} active hosts")

    # Port scan active hosts
    hosts = []
    for ip in sorted(active_ips):
        hostname = get_hostname(ip)
        open_ports = scan_ports(ip)
        hosts.append({
            "ip": ip,
            "hostname": hostname,
            "is_local": ip == local_ip,
            "open_ports": open_ports,
            "port_count": len(open_ports)
        })

    return {
        "network": network,
        "local_ip": local_ip,
        "scan_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_hosts": len(hosts),
        "hosts": hosts
    }


if __name__ == "__main__":
    import json
    data = scan_network()
    print(json.dumps(data, indent=2))
