#!/usr/bin/env python3
"""
Pulse Agent - Main entry point
Lightweight Python agent for data collection and synchronization
"""

import sys
import json
import logging
from pathlib import Path

from .config import Config
from .db_client import DatabaseClient, QueryLoader
from .aggregator import DataAggregator
from .http_client import HttpClient
from .state_manager import StateManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point"""
    logger.info(f"Pulse Agent v{Config.get_version()}")
    logger.info(f"Pull URL: {Config.PULL_URL} (deprecated - using direct DB)")
    logger.info(f"Push URL: {Config.PUSH_URL}")
    logger.info(f"Data Directory: {Config.get_data_dir()}")
    logger.info(f"Data File Path: {Config.get_data_filepath()}")
    logger.info(f"Database: {Config.DB_TYPE}://{Config.DB_USER}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}")

    # Initialize state manager
    state_manager = StateManager(Config.get_data_filepath())

    # Read current batch_index
    batch_index = state_manager.get_batch_index()
    logger.info(f"Current batch_index: {batch_index}")

    # Display current state
    state = state_manager.read_state()
    if state:
        logger.info(f"Current state: {json.dumps(state, indent=2)}")
    else:
        logger.info("No existing state file found")

    try:
        # Get start and end times
        start_time, end_time = state_manager.get_start_end_times()
        logger.info(f"Query time range: {start_time} to {end_time}")

        # Initialize database client
        db_client = DatabaseClient(
            db_type=Config.DB_TYPE,
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            ssl_mode=Config.DB_SSL_MODE
        )

        # Load SQL queries
        queries_file = Config.get_queries_filepath()
        logger.info(f"Loading queries from: {queries_file}")
        query_loader = QueryLoader(queries_file)

        # Initialize aggregator
        aggregator = DataAggregator(db_client, query_loader)

        # Connect to database and fetch stats
        logger.info("=== DATABASE QUERY ===")
        with db_client:
            if not db_client.is_connected():
                logger.error("Failed to connect to database")
                raise ConnectionError("Database connection failed")

            pull_response = aggregator.fetch_stats(
                start_time=start_time,
                end_time=end_time,
                client_id=Config.CLIENT_ID,
                site_id=Config.SITE_ID
            )

        # Prepare push payload
        batch_index += 1
        push_uuid = state_manager.get_or_generate_push_uuid()

        push_payload = {
            "client_id": Config.CLIENT_ID,
            "site_id": Config.SITE_ID,
            "batch_index": batch_index,
            "uuid": push_uuid,
            "stats": pull_response.get("stats", {}),
            "additional": {}
        }

        # Update stats status based on success/failure
        if not pull_response or not pull_response.get("stats"):
            push_payload["stats"]["status"] = "failure"
            push_payload["additional"] = {
                "error_message": "Database query failed or returned no data"
            }

        # Push data to destination
        logger.info("=== PUSH REQUEST ===")
        logger.info(f"Pushing data to: {Config.PUSH_URL}")
        logger.info(f"Using UUID: {push_uuid}")
        logger.info(f"Using batch_index: {batch_index}")

        http_client = HttpClient(timeout=Config.TIMEOUT, user_agent=Config.USER_AGENT)
        push_headers = {
            "Authorization": f"Bearer {Config.PUSH_TOKEN}"
        }

        push_response = http_client.make_post_request(
            Config.PUSH_URL,
            push_payload,
            push_headers
        )

        if push_response is not None:
            logger.info("[SUCCESS] PUSH: Data delivered successfully")

            # Save timestamp if pull was successful
            if pull_response and pull_response.get("stats"):
                state_manager.save_successful_timestamp(end_time)
                logger.info("Saved successful timestamp")

            # Update batch_index
            state_manager.update_batch_index(batch_index)
            logger.info(f"Updated batch_index to {batch_index}")
        else:
            logger.error(f"[FAILED] PUSH: Could not deliver data to {Config.PUSH_URL}")

            # Save failed UUID for retry
            state_manager.save_failed_push_uuid(push_uuid)
            logger.info("Saved failed push UUID for retry")

            # Revert batch_index
            batch_index -= 1
            state_manager.update_batch_index(batch_index)

            logger.error("Pulse Agent execution failed - push operation unsuccessful")
            return 1

        # Display final state
        final_state = state_manager.read_state()
        if final_state:
            logger.info("Final state:")
            logger.info(json.dumps(final_state, indent=2))

        logger.info("Pulse Agent execution completed successfully")
        return 0

    except ConnectionError as e:
        logger.error(f"Connection error: {e}")
        # Create failure status data
        start_time, end_time = state_manager.get_start_end_times()

        # Try to push failure status
        batch_index += 1
        push_uuid = state_manager.get_or_generate_push_uuid()

        error_payload = {
            "client_id": Config.CLIENT_ID,
            "site_id": Config.SITE_ID,
            "batch_index": batch_index,
            "uuid": push_uuid,
            "stats": {
                "status": "failure",
                "start_time": start_time,
                "end_time": end_time,
                "error_message": "Database connection failed"
            },
            "additional": {"error_message": "Database connection failed"}
        }

        http_client = HttpClient(timeout=Config.TIMEOUT, user_agent=Config.USER_AGENT)
        push_headers = {"Authorization": f"Bearer {Config.PUSH_TOKEN}"}

        logger.info("Attempting to push failure status...")
        push_response = http_client.make_post_request(
            Config.PUSH_URL,
            error_payload,
            push_headers
        )

        if push_response:
            state_manager.update_batch_index(batch_index)
            logger.info("Failure status pushed successfully")
        else:
            batch_index -= 1
            state_manager.save_failed_push_uuid(push_uuid)

        return 1

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)

        # Try to send error payload
        try:
            start_time, end_time = state_manager.get_start_end_times()
            batch_index += 1
            push_uuid = state_manager.get_or_generate_push_uuid()

            error_payload = {
                "client_id": Config.CLIENT_ID,
                "site_id": Config.SITE_ID,
                "batch_index": batch_index,
                "uuid": push_uuid,
                "stats": {
                    "status": "error",
                    "start_time": start_time,
                    "end_time": end_time,
                    "error_message": str(e)
                },
                "additional": {"error_message": str(e)}
            }

            http_client = HttpClient(timeout=Config.TIMEOUT, user_agent=Config.USER_AGENT)
            push_headers = {"Authorization": f"Bearer {Config.PUSH_TOKEN}"}

            push_response = http_client.make_post_request(
                Config.PUSH_URL,
                error_payload,
                push_headers
            )

            if push_response:
                state_manager.update_batch_index(batch_index)
            else:
                batch_index -= 1
        except Exception as e2:
            logger.error(f"Failed to send error payload: {e2}")

        return 1


if __name__ == "__main__":
    sys.exit(main())
