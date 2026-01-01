from prometheus_client import (
    CollectorRegistry,
    CONTENT_TYPE_LATEST,
    generate_latest,
)

from app.monitoring.registry import get_registry


def metrics_endpoint() -> tuple[bytes, int, dict[str, str]]:
    """
    Metrics endpoint for Prometheus scraping.

    This function generates and returns the latest metrics data from the
    application's Prometheus registry. The response includes the metrics data,
    an HTTP status code, and the appropriate content type header.

    Returns:
        tuple[bytes, int, dict[str, str]]: A tuple containing:
            - The metrics data in bytes format.
            - The HTTP status code (200 for success).
            - A dictionary with the "Content-Type" header set to Prometheus' latest format.
    """
    registry: CollectorRegistry = get_registry()
    data: bytes = generate_latest(registry)
    return data, 200, {"Content-Type": CONTENT_TYPE_LATEST}
