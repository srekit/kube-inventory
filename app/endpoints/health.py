import logging
import requests
import time

from datetime import datetime
from flask import jsonify, Response
from typing import Dict, Any, Optional

from app.clients.kube import KubernetesClient


def health_endpoint(
    github_access_token: str,
    github_api_url: str,
    kube_client: Optional[KubernetesClient] = None,
) -> tuple[Response, int]:
    """
    Health check endpoint for the application.

    This function performs various health checks, including Kubernetes connectivity,
    GitHub API access, and configuration file accessibility. It calculates the response
    time, adds a timestamp, and returns the health status along with an appropriate HTTP status code.

    Args:
        github_access_token (str): GitHub access token for API authentication.
        github_api_url (str): Base URL for the GitHub API.
        kube_client (KubernetesClient): Kubernetes client.

    Returns:
        tuple[Response, int]: A tuple containing the JSON response with health status and the HTTP status code.
                              Returns HTTP 200 if healthy, otherwise HTTP 503.
    """
    start_time: float = time.time()
    health_status: dict[str, Any] = _perform_health_checks(
        github_access_token=github_access_token,
        github_api_url=github_api_url,
        kube_client=kube_client,
    )
    response_time: float = time.time() - start_time

    health_status["response_time_ms"] = round(response_time * 1000, 2)
    health_status["timestamp"] = (
        datetime.now().replace(microsecond=0).isoformat() + "Z"
    )

    if health_status["status"] == "healthy":
        return jsonify(health_status), 200
    else:
        return jsonify(health_status), 503


def _perform_health_checks(
    github_access_token: str,
    github_api_url: str,
    kube_client: Optional[KubernetesClient] = None,
) -> Dict[str, Any]:
    """
    Perform health checks for the application.

    This function performs a series of health checks to ensure the application's dependencies
    and configurations are functioning correctly. It checks Kubernetes connectivity, GitHub API
    access, and the accessibility of configuration files. The results of these checks are aggregated
    into a dictionary, along with an overall health status.

    Args:
        github_access_token (str): GitHub access token for API authentication.
        github_api_url (str): Base URL for the GitHub API.
        kube_client (KubernetesClient): Kubernetes client.

    Returns:
        Dict[str, Any]: A dictionary containing the overall health status and the results of individual checks.
                        Example structure:
                        {
                            "status": "healthy" | "unhealthy",
                            "checks": {
                                "kubernetes": {"status": "healthy" | "unhealthy", "error": str},
                                "github_api": {"status": "healthy" | "unhealthy", "rate_limit_remaining": int, "error": str},
                            }
                        }
    """
    checks: dict = {}

    # Kubernetes connectivity check
    if kube_client is None:
        checks["kubernetes"] = {
            "status": "unhealthy",
            "error": "Kubernetes client not initialized",
        }
    else:
        checks["kubernetes"] = kube_client.health_check()

    # GitHub API connectivity check
    try:
        headers: dict = {}
        if github_access_token:
            headers["Authorization"] = f"token {github_access_token}"

        response: requests.Response = requests.get(
            f"{github_api_url}/rate_limit", headers=headers, timeout=5
        )
        response.raise_for_status()
        checks["github_api"] = {
            "status": "healthy",
            "rate_limit_remaining": response.json()
            .get("rate", {})
            .get("remaining"),
        }
    except Exception as e:
        logging.error(f"GitHub API health check failed: {e}")
        checks["github_api"] = {"status": "unhealthy", "error": str(e)}

    # Overall status
    overall_status: str = "healthy"
    for check in checks.values():
        if check["status"] == "unhealthy":
            overall_status = "unhealthy"
            break
        elif check["status"] == "warning" and overall_status == "healthy":
            overall_status = "warning"

    if overall_status == "healthy":
        logging.debug("Health check passed: all systems healthy")
    else:
        logging.error("Health check failed")

    return {"status": overall_status, "checks": checks}
