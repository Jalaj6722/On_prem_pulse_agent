"""
Data aggregator for Pulse Agent
Executes SQL queries and aggregates results into the expected JSON format
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .db_client import DatabaseClient, QueryLoader
from .docker_client import DockerClient
from .system_client import SystemClient
from .config import Config

logger = logging.getLogger(__name__)


class DataAggregator:
    """Aggregates data from database queries into JSON format"""

    def __init__(self, db_client: DatabaseClient, query_loader: QueryLoader,
                 docker_client: Optional[DockerClient] = None,
                 system_client: Optional[SystemClient] = None):
        """
        Initialize data aggregator

        Args:
            db_client: Database client instance
            query_loader: Query loader instance
            docker_client: Docker client instance (optional)
            system_client: System metrics client instance (optional)
        """
        self.db_client = db_client
        self.query_loader = query_loader
        self.docker_client = docker_client or DockerClient()
        self.system_client = system_client or SystemClient()

    def fetch_stats(self, start_time: str, end_time: str,
                   client_id: str, site_id: str) -> Dict[str, Any]:
        """
        Fetch and aggregate statistics from database

        Args:
            start_time: Start time in ISO 8601 format
            end_time: End time in ISO 8601 format
            client_id: Client identifier
            site_id: Site identifier

        Returns:
            Dictionary containing aggregated stats in expected format
        """
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        duration_ms = int((end_dt - start_dt).total_seconds() * 1000)

        # Prepare parameters for queries
        params = {
            "start_time": start_time,
            "end_time": end_time
        }

        db_stats = {}
        system_metrics = None
        docker_metrics = None
        aggregation_order = self.query_loader.get_aggregation_order()

        # Execute queries in specified order
        for query_name in aggregation_order:
            query_config = self.query_loader.get_query(query_name)
            if not query_config:
                logger.warning(f"Query '{query_name}' not found in queries file")
                continue

            query_type = query_config.get("type", "count")
            default_value = query_config.get("default", 0)

            # Handle Docker queries - collect detailed metrics once
            if query_type == "docker":
                if docker_metrics is None:
                    try:
                        docker_metrics = self.docker_client.get_detailed_metrics()
                        logger.info("Docker metrics collected successfully")
                    except Exception as e:
                        logger.error(f"Failed to get Docker metrics: {e}")
                        docker_metrics = {
                            "system": {
                                "daemon_status": "error",
                                "version": "unknown",
                                "containers": {"total": 0, "running": 0, "stopped": 0}
                            },
                            "summary": {
                                "total_containers": 0,
                                "running_containers": 0,
                                "healthy_containers": 0
                            },
                            "containers": []
                        }
                continue

            # Handle system metrics query
            if query_type == "system":
                try:
                    system_metrics = self.system_client.get_all_metrics()
                    logger.info("System metrics collected successfully")
                except Exception as e:
                    logger.error(f"Failed to get system metrics: {e}")
                    system_metrics = {
                        "system": {},
                        "memory": {},
                        "disks": [],
                        "processes": {},
                        "services": {}
                    }
                continue

            # Handle database queries
            sql = query_config.get("sql")
            try:
                results = self.db_client.execute_query(sql, params)

                if query_type == "count":
                    # Extract count from result
                    if results and len(results) > 0:
                        # Handle different result formats
                        result = results[0]
                        if isinstance(result, dict):
                            # Try common count column names
                            count = result.get("count") or result.get("COUNT(*)") or result.get("total", 0)
                        else:
                            count = result[0] if isinstance(result, (list, tuple)) else result
                        db_stats[query_name] = int(count) if count is not None else 0
                    else:
                        db_stats[query_name] = 0

                elif query_type == "single_value":
                    # Extract single value from result
                    if results and len(results) > 0:
                        result = results[0]
                        if isinstance(result, dict):
                            # Get first value from dictionary
                            value = next(iter(result.values()), default_value)
                        else:
                            value = result[0] if isinstance(result, (list, tuple)) else result
                        db_stats[query_name] = value
                    else:
                        db_stats[query_name] = default_value

                else:
                    logger.warning(f"Unknown query type: {query_type} for query '{query_name}'")
                    db_stats[query_name] = default_value

            except Exception as e:
                logger.error(f"Failed to execute query '{query_name}': {e}")
                db_stats[query_name] = default_value

        # Build stats object with the new structure
        stats = {
            "status": "success",
            "start_time": start_time,
            "end_time": end_time
        }

        # Add database stats (images, tasks, etc.)
        stats.update(db_stats)

        # Add system metrics if collected
        if system_metrics is not None:
            stats["system_metrics"] = system_metrics

        # Add docker metrics if collected
        if docker_metrics is not None:
            stats["docker_metrics"] = docker_metrics

        # Build response in expected format
        response = {
            "stats": stats
        }

        return response
