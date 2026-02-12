"""
Configuration management for Pulse Agent
Supports environment variables with fallback to defaults
"""

import os
from pathlib import Path
from typing import Optional

# Load .env file if it exists
try:
    from dotenv import load_dotenv
    # Look for .env file in current directory and parent directories
    env_path = Path.cwd() / '.env'
    if env_path.exists():
        load_dotenv(env_path)
    else:
        # Try parent directory
        env_path = Path.cwd().parent / '.env'
        if env_path.exists():
            load_dotenv(env_path)
except ImportError:
    # python-dotenv not installed, rely on system environment variables
    pass


class Config:
    """Configuration manager for Pulse Agent"""

    # HTTP/API Configuration
    PULL_URL = os.getenv("PA_PULL_URL", "http://localhost:5151/pull/")
    PUSH_URL = os.getenv("PA_PUSH_URL", "http://localhost:5151/push/")
    USER_AGENT = os.getenv("PA_USER_AGENT", "pulse-agent/1.0")
    TIMEOUT = int(os.getenv("PA_TIMEOUT", "30"))
    PULL_TOKEN = os.getenv("PA_PULL_TOKEN", "")
    PUSH_TOKEN = os.getenv("PA_PUSH_TOKEN", "")

    # Database Configuration
    DB_TYPE = os.getenv("PA_DB_TYPE", "postgresql").lower()  # postgresql, mysql
    DB_HOST = os.getenv("PA_DB_HOST", "localhost")
    DB_PORT = int(os.getenv("PA_DB_PORT", "5432"))
    DB_NAME = os.getenv("PA_DB_NAME", "pulse_db")
    DB_USER = os.getenv("PA_DB_USER", "pulse_user")
    DB_PASSWORD = os.getenv("PA_DB_PASSWORD", "")
    DB_SSL_MODE = os.getenv("PA_DB_SSL_MODE", "prefer")  # disable, allow, prefer, require

    # Client/Site Configuration
    CLIENT_ID = os.getenv("PA_CLIENT_ID", "pulse-agent-client")
    SITE_ID = os.getenv("PA_SITE_ID", "default-site")

    # File System Configuration
    @staticmethod
    def get_data_dir() -> Path:
        """Get data directory based on platform"""
        if os.getenv("PA_DATA_DIR"):
            return Path(os.getenv("PA_DATA_DIR"))

        system = os.name
        if system == "nt":  # Windows
            return Path("C:/ProgramData/pulse-agent")
        elif system == "posix":  # Linux/macOS
            if os.path.exists("/var/lib"):
                return Path("/var/lib/pulse-agent")
            else:
                return Path("/usr/local/var/pulse-agent")
        else:
            return Path("/var/lib/pulse-agent")

    @staticmethod
    def get_data_filepath() -> Path:
        """Get full path to data file"""
        data_dir = Config.get_data_dir()
        filename = os.getenv("PA_DATA_FILENAME", "pulse.data")
        return data_dir / filename

    @staticmethod
    def get_queries_filepath() -> Path:
        """Get path to SQL queries configuration file"""
        if os.getenv("PA_QUERIES_FILE"):
            return Path(os.getenv("PA_QUERIES_FILE"))

        # Default: look for queries.json in the same directory as the script
        script_dir = Path(__file__).parent.parent
        return script_dir / "queries.json"

    @staticmethod
    def get_version() -> str:
        """Get agent version"""
        return __import__("pulse_agent_complete").__version__
