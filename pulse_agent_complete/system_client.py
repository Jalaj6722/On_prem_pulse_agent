"""
System metrics client for Pulse Agent
Collects system, memory, disk, process, and service metrics
"""

import logging
import platform
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class SystemClient:
    """System metrics client for collecting local system information"""

    def __init__(self):
        """Initialize system metrics client"""
        self.psutil = None
        self._load_psutil()

    def _load_psutil(self):
        """Load psutil library"""
        try:
            import psutil
            self.psutil = psutil
            logger.info("System metrics client initialized")
        except ImportError:
            logger.warning("psutil not installed. Install with: pip install psutil")
            self.psutil = None

    def is_available(self) -> bool:
        """Check if psutil is available"""
        return self.psutil is not None

    def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information (OS, CPU, uptime, etc.)

        Returns:
            Dictionary with system information
        """
        if not self.is_available():
            return {}

        try:
            boot_time = datetime.fromtimestamp(self.psutil.boot_time())
            uptime_seconds = (datetime.now() - boot_time).total_seconds()

            cpu_count = self.psutil.cpu_count(logical=False)
            cpu_count_logical = self.psutil.cpu_count(logical=True)

            # Get CPU usage
            cpu_percent = self.psutil.cpu_percent(interval=0.1)

            # Get load average (Unix-like systems)
            load_avg = [0.0, 0.0, 0.0]
            try:
                load_avg = list(self.psutil.getloadavg())
            except (AttributeError, OSError):
                pass  # Not available on Windows

            # Build os_version string
            os_version = f"{platform.system()} {platform.release()}"
            try:
                # Try to get more detailed version info on Linux
                import distro
                os_version = f"{distro.name()} {distro.version()}"
            except ImportError:
                pass

            return {
                "hostname": platform.node(),
                "cpu_count": cpu_count_logical,
                "load_average_1min": round(load_avg[0], 2) if len(load_avg) > 0 else 0,
                "uptime_seconds": int(uptime_seconds),
                "os_version": os_version
            }
        except Exception as e:
            logger.error(f"Failed to get system info: {e}")
            return {}

    def get_memory_info(self) -> Dict[str, Any]:
        """
        Get memory information

        Returns:
            Dictionary with memory metrics
        """
        if not self.is_available():
            return {}

        try:
            mem = self.psutil.virtual_memory()
            swap = self.psutil.swap_memory()

            return {
                "total_bytes": mem.total,
                "used_bytes": mem.used,
                "usage_percent": round(mem.percent, 2)
            }
        except Exception as e:
            logger.error(f"Failed to get memory info: {e}")
            return {}

    def get_disk_info(self) -> List[Dict[str, Any]]:
        """
        Get disk information for all mounted filesystems (excluding snap mounts)

        Returns:
            List of dictionaries with disk metrics
        """
        if not self.is_available():
            return []

        disks = []
        try:
            partitions = self.psutil.disk_partitions()

            for partition in partitions:
                # Skip snap mounts and other read-only loop devices
                if '/snap/' in partition.mountpoint or partition.fstype == 'squashfs':
                    continue

                try:
                    usage = self.psutil.disk_usage(partition.mountpoint)

                    disk_info = {
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total_bytes": usage.total,
                        "used_bytes": usage.used,
                        "free_bytes": usage.free,
                        "usage_percent": round(usage.percent, 2)
                    }
                    disks.append(disk_info)
                except (PermissionError, OSError) as e:
                    # Skip partitions we can't access
                    logger.debug(f"Cannot access partition {partition.mountpoint}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Failed to get disk info: {e}")

        return disks

    def get_process_info(self) -> Dict[str, Any]:
        """
        Get process information

        Returns:
            Dictionary with process metrics
        """
        if not self.is_available():
            return {}

        try:
            process_count = len(self.psutil.pids())

            # Count processes by status
            running = 0
            sleeping = 0
            zombie = 0
            stopped = 0

            for proc in self.psutil.process_iter(['status']):
                try:
                    status = proc.info['status']
                    if status == self.psutil.STATUS_RUNNING:
                        running += 1
                    elif status == self.psutil.STATUS_SLEEPING:
                        sleeping += 1
                    elif status == self.psutil.STATUS_ZOMBIE:
                        zombie += 1
                    elif status == self.psutil.STATUS_STOPPED:
                        stopped += 1
                except (self.psutil.NoSuchProcess, self.psutil.AccessDenied):
                    continue

            return {
                "total": process_count,
                "running": running,
                "sleeping": sleeping,
                "zombie": zombie,
                "stopped": stopped
            }
        except Exception as e:
            logger.error(f"Failed to get process info: {e}")
            return {}

    def get_service_info(self) -> Dict[str, Any]:
        """
        Get service information (systemd services on Linux)

        Returns:
            Dictionary with service metrics
        """
        if not self.is_available():
            return {}

        service_info = {
            "total_services": 0,
            "running_services": 0,
            "failed_services": 0
        }

        try:
            import subprocess

            # Check if systemd is available
            result = subprocess.run(
                ['systemctl', 'list-units', '--type=service', '--all', '--no-pager', '--no-legend'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                service_info["total_services"] = len(lines)

                for line in lines:
                    if 'active' in line.lower() and 'running' in line.lower():
                        service_info["running_services"] += 1
                    elif 'failed' in line.lower():
                        service_info["failed_services"] += 1
            else:
                logger.debug("systemctl not available or failed")
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
            logger.debug(f"Failed to get service info (systemd might not be available): {e}")

        return service_info

    def get_all_metrics(self) -> Dict[str, Any]:
        """
        Get all system metrics in one call

        Returns:
            Dictionary with all system metrics
        """
        if not self.is_available():
            logger.warning("psutil not available, returning empty metrics")
            return {
                "system": {
                    "hostname": platform.node(),
                    "cpu_count": 0,
                    "load_average_1min": 0,
                    "uptime_seconds": 0,
                    "os_version": f"{platform.system()} {platform.release()}"
                },
                "memory": {
                    "total_bytes": 0,
                    "used_bytes": 0,
                    "usage_percent": 0
                },
                "disks": [],
                "services": {
                    "total_services": 0,
                    "running_services": 0,
                    "failed_services": 0
                }
            }

        return {
            "system": self.get_system_info(),
            "memory": self.get_memory_info(),
            "disks": self.get_disk_info(),
            "services": self.get_service_info()
        }
