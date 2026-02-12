"""
State management for Pulse Agent
Handles file I/O, timestamps, UUIDs, and batch tracking
"""

import json
import logging
import uuid
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class StateManager:
    """Manages agent state persistence"""

    def __init__(self, data_filepath: Path):
        """
        Initialize state manager

        Args:
            data_filepath: Path to state file
        """
        self.data_filepath = data_filepath
        self._ensure_data_dir()

    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        self.data_filepath.parent.mkdir(parents=True, exist_ok=True)

    def read_state(self) -> dict:
        """Read state from file"""
        if not self.data_filepath.exists():
            return {}

        try:
            with open(self.data_filepath, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON in state file: {e}. Starting with empty state.")
            return {}
        except Exception as e:
            logger.error(f"Failed to read state file: {e}")
            return {}

    def write_state(self, state: dict):
        """Write state to file"""
        try:
            self._ensure_data_dir()
            with open(self.data_filepath, 'w') as f:
                json.dump(state, f, indent=2)
            logger.debug(f"State written to {self.data_filepath}")
        except Exception as e:
            logger.error(f"Failed to write state file: {e}")
            raise

    def get_batch_index(self) -> int:
        """Get current batch index"""
        state = self.read_state()
        return state.get("batch_index", 0)

    def update_batch_index(self, batch_index: int):
        """Update batch index in state"""
        state = self.read_state()
        state["batch_index"] = batch_index
        self.write_state(state)

    def get_last_successful_timestamp(self) -> Optional[str]:
        """Get last successful timestamp"""
        state = self.read_state()
        return state.get("last_successful_timestamp")

    def save_successful_timestamp(self, timestamp: str):
        """Save successful timestamp and clear failed UUID"""
        state = self.read_state()
        state["last_successful_timestamp"] = timestamp
        # Remove failed UUID if it exists
        if "last_failed_uuid" in state:
            del state["last_failed_uuid"]
        self.write_state(state)

    def get_or_generate_push_uuid(self) -> str:
        """Get failed UUID if exists, otherwise generate new UUID"""
        state = self.read_state()
        if "last_failed_uuid" in state:
            uuid_str = state["last_failed_uuid"]
            logger.info(f"Reusing failed UUID: {uuid_str}")
            return uuid_str
        else:
            new_uuid = str(uuid.uuid4())
            logger.debug(f"Generated new UUID: {new_uuid}")
            return new_uuid

    def save_failed_push_uuid(self, uuid_str: str):
        """Save failed push UUID for retry"""
        state = self.read_state()
        state["last_failed_uuid"] = uuid_str
        self.write_state(state)

    def get_start_end_times(self) -> Tuple[str, str]:
        """
        Get start and end times for query
        Uses last successful timestamp as start_time, current time as end_time

        Returns:
            Tuple of (start_time, end_time) in ISO 8601 format
        """
        end_time = datetime.utcnow()
        end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

        last_timestamp = self.get_last_successful_timestamp()
        if last_timestamp:
            try:
                # Parse the timestamp
                start_time_str = last_timestamp
                logger.info(f"Using last successful timestamp as start_time: {start_time_str}")
            except Exception as e:
                logger.warning(f"Failed to parse last timestamp, using epoch: {e}")
                start_time_str = "1970-01-01T00:00:00.000Z"
        else:
            logger.info("No previous timestamp found, using epoch as start_time")
            start_time_str = "1970-01-01T00:00:00.000Z"

        return start_time_str, end_time_str
