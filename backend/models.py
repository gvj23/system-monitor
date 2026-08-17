from pydantic import BaseModel
from typing import Optional, List, Any

class CPUMetrics(BaseModel):
    usage_percent: float
    core_count: int
    physical_cores: int
    frequency_mhz: Optional[float] = None

class RAMMetrics(BaseModel):
    total_gb: float
    used_gb: float
    available_gb: float
    usage_percent: float

class DiskMetrics(BaseModel):
    total_gb: float
    used_gb: float
    free_gb: float
    usage_percent: float

class UptimeMetrics(BaseModel):
    boot_time: str
    uptime_string: str
    uptime_seconds: int

class SystemInfo(BaseModel):
    hostname: str
    ip_address: str
    os: str
    os_version: str
    architecture: str

class MetricsPayload(BaseModel):
    timestamp: str
    system: SystemInfo
    cpu: CPUMetrics
    ram: RAMMetrics
    disk: DiskMetrics
    uptime: UptimeMetrics
    cpu_cores: Optional[List[Any]] = None
    network_io: Optional[Any] = None
    processes: Optional[List[Any]] = None
    ports: Optional[List[Any]] = None
    failed_services: Optional[str] = None
    system_errors: Optional[List[str]] = None
    security: Optional[Any] = None
    network_scan: Optional[Any] = None
