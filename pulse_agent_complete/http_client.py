"""
HTTP client for Pulse Agent
Handles HTTP POST requests for pushing data
"""

import logging
import requests
from typing import Dict, Any, Optional

from .config import Config

logger = logging.getLogger(__name__)


class HttpClient:
    """HTTP client for making requests"""

    def __init__(self, timeout: int = 30, user_agent: str = "pulse-agent/1.0"):
        """
        Initialize HTTP client

        Args:
            timeout: Request timeout in seconds
            user_agent: User agent string
        """
        self.timeout = timeout
        self.user_agent = user_agent
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})

    def make_post_request(self, url: str, json_data: Dict[str, Any],
                         headers: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        """
        Make HTTP POST request

        Args:
            url: Target URL
            json_data: JSON data to send
            headers: Additional headers (e.g., Authorization)

        Returns:
            Response JSON as dictionary, or None on failure
        """
        request_headers = {}
        if headers:
            request_headers.update(headers)

        try:
            logger.info(f"POST request to: {url}")
            logger.debug(f"Request payload: {json_data}")

            response = self.session.post(
                url,
                json=json_data,
                headers=request_headers,
                timeout=self.timeout
            )

            logger.info(f"HTTP Status Code: {response.status_code}")

            if response.status_code >= 200 and response.status_code < 300:
                try:
                    return response.json()
                except ValueError:
                    logger.warning("Response is not valid JSON")
                    return {}
            else:
                logger.error(f"HTTP request failed with status {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None

        except requests.exceptions.Timeout:
            logger.error(f"Request timeout after {self.timeout} seconds")
            return None
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during HTTP request: {e}")
            return None
