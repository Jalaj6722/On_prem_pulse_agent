"""
Docker client for Pulse Agent
Queries Docker daemon for container metrics
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class DockerClient:
    """Docker client for querying container metrics"""

    def __init__(self):
        """Initialize Docker client"""
        self.docker = None
        self._connect()

    def _connect(self):
        """Connect to Docker daemon"""
        try:
            import docker
            self.docker = docker.from_env()
            # Test connection
            self.docker.ping()
            logger.info("Connected to Docker daemon")
        except ImportError:
            logger.warning("Docker SDK not installed. Install with: pip install docker")
            self.docker = None
        except Exception as e:
            logger.warning(f"Failed to connect to Docker daemon: {e}")
            self.docker = None

    def is_connected(self) -> bool:
        """Check if Docker daemon is accessible"""
        return self.docker is not None

    def get_container_stats(self) -> Dict[str, int]:
        """
        Get container statistics

        Returns:
            Dictionary with container counts by state
        """
        stats = {
            "containers_running": 0,
            "containers_exited": 0,
            "containers_paused": 0,
            "containers_total": 0
        }

        if not self.is_connected():
            logger.warning("Docker not connected, returning zero stats")
            return stats

        try:
            # Get all containers (including stopped ones)
            all_containers = self.docker.containers.list(all=True)
            stats["containers_total"] = len(all_containers)

            # Count by state
            for container in all_containers:
                state = container.status.lower()

                if state == "running":
                    stats["containers_running"] += 1
                elif state == "exited":
                    stats["containers_exited"] += 1
                elif state == "paused":
                    stats["containers_paused"] += 1

            logger.debug(f"Docker stats: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Failed to get Docker container stats: {e}")
            return stats

    def get_detailed_metrics(self) -> Dict[str, Any]:
        """
        Get detailed Docker metrics including system info and container details

        Returns:
            Dictionary with comprehensive Docker metrics
        """
        metrics = {
            "system": {
                "daemon_status": "unknown",
                "version": "unknown",
                "containers": {
                    "total": 0,
                    "running": 0,
                    "stopped": 0
                }
            },
            "summary": {
                "total_containers": 0,
                "running_containers": 0,
                "healthy_containers": 0
            },
            "containers": []
        }

        if not self.is_connected():
            logger.warning("Docker not connected, returning minimal metrics")
            metrics["system"]["daemon_status"] = "not_connected"
            return metrics

        try:
            # Get Docker version info
            version_info = self.docker.version()
            metrics["system"]["daemon_status"] = "running"
            metrics["system"]["version"] = version_info.get("Version", "unknown")

            # Get all containers
            all_containers = self.docker.containers.list(all=True)

            running_count = 0
            stopped_count = 0
            healthy_count = 0

            for container in all_containers:
                state = container.status.lower()

                # Count states
                if state == "running":
                    running_count += 1
                else:
                    stopped_count += 1

                # Check health status
                health_status = "none"
                try:
                    health = container.attrs.get("State", {}).get("Health", {})
                    if health:
                        health_status = health.get("Status", "none").lower()
                        if health_status == "healthy":
                            healthy_count += 1
                except Exception:
                    pass

                # Build container detail
                container_detail = {
                    "name": container.name,
                    "image": container.image.tags[0] if container.image.tags else container.image.short_id,
                    "state": state,
                    "status": container.status
                }

                # Add health status if available
                if health_status != "none":
                    container_detail["health"] = health_status

                metrics["containers"].append(container_detail)

            # Update counts
            metrics["system"]["containers"]["total"] = len(all_containers)
            metrics["system"]["containers"]["running"] = running_count
            metrics["system"]["containers"]["stopped"] = stopped_count

            metrics["summary"]["total_containers"] = len(all_containers)
            metrics["summary"]["running_containers"] = running_count
            metrics["summary"]["healthy_containers"] = healthy_count

            logger.debug(f"Docker detailed metrics: {metrics}")
            return metrics

        except Exception as e:
            logger.error(f"Failed to get detailed Docker metrics: {e}")
            metrics["system"]["daemon_status"] = "error"
            return metrics

    def get_running_containers(self) -> int:
        """Get count of running containers"""
        stats = self.get_container_stats()
        return stats["containers_running"]

    def get_exited_containers(self) -> int:
        """Get count of exited containers"""
        stats = self.get_container_stats()
        return stats["containers_exited"]

    def get_paused_containers(self) -> int:
        """Get count of paused containers"""
        stats = self.get_container_stats()
        return stats["containers_paused"]

    def get_total_containers(self) -> int:
        """Get total count of containers"""
        stats = self.get_container_stats()
        return stats["containers_total"]
