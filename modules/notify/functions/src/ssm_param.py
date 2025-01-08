import json
import logging
import os
import time
from typing import Any, Dict, Optional

import urllib3

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ParameterStoreClient:
    def __init__(self, max_init_time: int = 3):
        self.http = urllib3.PoolManager(timeout=urllib3.Timeout(connect=2.0, read=2.0))
        self.is_initialized = False
        self.max_init_time = max_init_time
        self.session_token = os.environ.get("AWS_SESSION_TOKEN")

    def initialize(self) -> bool:
        """
        Initialize the extension and wait until it's ready
        """
        if self.is_initialized:
            return True

        logger.info("Initializing Parameters and Secrets extension...")
        start_time = time.time()

        while (time.time() - start_time) < self.max_init_time:
            try:
                response = self.http.request("GET", "http://localhost:2773/healthcheck")
                if response.status == 200:
                    self.is_initialized = True
                    logger.info("Extension successfully initialized")
                    return True
            except Exception as e:
                logger.debug(f"Extension not ready yet: {str(e)}")

            time.sleep(1)

        logger.error("Failed to initialize extension")
        return False

    def get_parameter(
        self, parameter_arn: str, max_retries: int = 3, delay_seconds: int = 1
    ) -> Dict[str, Any]:
        """
        Get parameter using the extension
        """
        if not self.initialize():
            logger.warning("Extension not initialized, falling back to boto3")
            return self._fallback_get_parameter(parameter_arn)

        if not self.session_token:
            logger.warning("No AWS_SESSION_TOKEN found, falling back to boto3")
            return self._fallback_get_parameter(parameter_arn)

        headers = {"X-Aws-Parameters-Secrets-Token": self.session_token}
        endpoint = (
            f"http://localhost:2773/systemsmanager/parameters/get?name={parameter_arn}"
        )

        for attempt in range(max_retries):
            try:
                logger.info(
                    f"Retrieving parameter: {parameter_arn} (attempt {attempt + 1}/{max_retries})"
                )
                response = self.http.request("GET", endpoint, headers=headers)

                if response.status == 200:
                    parameter_data = json.loads(response.data.decode("utf-8"))
                    logger.info("Parameter retrieved successfully")
                    return json.loads(parameter_data["Parameter"]["Value"])

                logger.warning(
                    f"Failed to retrieve parameter. Status: {response.status}"
                )

                if attempt < max_retries - 1:
                    wait_time = delay_seconds * (2**attempt)
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)

            except Exception as e:
                logger.error(f"Error retrieving parameter: {str(e)}")
                if attempt < max_retries - 1:
                    wait_time = delay_seconds * (2**attempt)
                    time.sleep(wait_time)

        logger.warning("All attempts failed, falling back to boto3")
        return self._fallback_get_parameter(parameter_arn)

    def _fallback_get_parameter(self, parameter_arn: str) -> Dict[str, Any]:
        """
        Fallback method using boto3
        """
        try:
            import boto3

            logger.info("Using boto3 fallback")
            ssm = boto3.client("ssm")
            response = ssm.get_parameter(Name=parameter_arn, WithDecryption=True)
            return json.loads(response["Parameter"]["Value"])
        except Exception as e:
            logger.error(f"Fallback failed: {str(e)}")
            return {}


# Create a singleton instance
parameter_store = ParameterStoreClient()


# Function to use in your code
def get_parameter(parameter_arn: str) -> Dict[str, Any]:
    """
    Public function to get parameters
    """
    return parameter_store.get_parameter(parameter_arn)
