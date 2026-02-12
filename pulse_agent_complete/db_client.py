"""
Database client for Pulse Agent
Supports PostgreSQL and MySQL with configurable queries
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class DatabaseClient:
    """Database client for executing queries"""

    def __init__(self, db_type: str, host: str, port: int, database: str,
                 user: str, password: str, ssl_mode: str = "prefer"):
        """
        Initialize database client

        Args:
            db_type: Database type ('postgresql' or 'mysql')
            host: Database host
            port: Database port
            database: Database name
            user: Database user
            password: Database password
            ssl_mode: SSL mode (for PostgreSQL)
        """
        self.db_type = db_type.lower()
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.ssl_mode = ssl_mode
        self.connection = None
        self.cursor = None

        # Import appropriate database library
        if self.db_type == "postgresql":
            try:
                import psycopg2
                from psycopg2.extras import RealDictCursor
                self.psycopg2 = psycopg2
                self.RealDictCursor = RealDictCursor
            except ImportError:
                raise ImportError("psycopg2 is required for PostgreSQL. Install with: pip install psycopg2-binary")
        elif self.db_type == "mysql":
            try:
                import mysql.connector
                self.mysql = mysql.connector
            except ImportError:
                raise ImportError("mysql-connector-python is required for MySQL. Install with: pip install mysql-connector-python")
        else:
            raise ValueError(f"Unsupported database type: {db_type}. Supported: postgresql, mysql")

    def connect(self) -> bool:
        """Establish database connection"""
        try:
            if self.db_type == "postgresql":
                self.connection = self.psycopg2.connect(
                    host=self.host,
                    port=self.port,
                    database=self.database,
                    user=self.user,
                    password=self.password,
                    sslmode=self.ssl_mode
                )
                self.cursor = self.connection.cursor(cursor_factory=self.RealDictCursor)
            elif self.db_type == "mysql":
                self.connection = self.mysql.connect(
                    host=self.host,
                    port=self.port,
                    database=self.database,
                    user=self.user,
                    password=self.password,
                    ssl_disabled=(self.ssl_mode == "disable")
                )
                self.cursor = self.connection.cursor(dictionary=True)

            logger.info(f"Connected to {self.db_type} database: {self.database}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False

    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.connection:
            self.connection.close()
            self.connection = None
        logger.info("Disconnected from database")

    def is_connected(self) -> bool:
        """Check if database connection is active"""
        if not self.connection:
            return False
        try:
            if self.db_type == "postgresql":
                return self.connection.status in (self.psycopg2.extensions.STATUS_READY, self.psycopg2.extensions.STATUS_IN_TRANSACTION)
            elif self.db_type == "mysql":
                return self.connection.is_connected()
        except:
            return False

    def execute_query(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return results

        Args:
            sql: SQL query string
            params: Query parameters (for parameterized queries)

        Returns:
            List of dictionaries representing rows
        """
        if not self.is_connected():
            raise ConnectionError("Database connection not established")

        try:
            # Convert PostgreSQL-style parameters to MySQL-style if needed
            if self.db_type == "mysql" and params:
                # MySQL uses %s instead of %(name)s
                # This is a simplified conversion - may need adjustment based on actual queries
                sql_mysql = sql
                for key, value in params.items():
                    sql_mysql = sql_mysql.replace(f"%({key})s", "%s")
                sql = sql_mysql
                params = list(params.values()) if isinstance(params, dict) else params

            self.cursor.execute(sql, params)

            if self.db_type == "postgresql":
                return self.cursor.fetchall()
            elif self.db_type == "mysql":
                return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            logger.error(f"SQL: {sql}")
            logger.error(f"Params: {params}")
            raise

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


class QueryLoader:
    """Load and manage SQL queries from configuration file"""

    def __init__(self, queries_file: Path):
        """
        Initialize query loader

        Args:
            queries_file: Path to queries.json file
        """
        self.queries_file = queries_file
        self.queries = {}
        self.aggregation_order = []
        self.load_queries()

    def load_queries(self):
        """Load queries from JSON file"""
        try:
            with open(self.queries_file, 'r') as f:
                data = json.load(f)

            self.queries = data.get("queries", {})
            self.aggregation_order = data.get("aggregation_order", [])

            logger.info(f"Loaded {len(self.queries)} queries from {self.queries_file}")
        except FileNotFoundError:
            logger.error(f"Queries file not found: {self.queries_file}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in queries file: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load queries: {e}")
            raise

    def get_query(self, query_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific query by name"""
        return self.queries.get(query_name)

    def get_all_queries(self) -> Dict[str, Dict[str, Any]]:
        """Get all queries"""
        return self.queries

    def get_aggregation_order(self) -> List[str]:
        """Get the order in which queries should be executed"""
        return self.aggregation_order
