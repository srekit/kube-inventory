from typing import Any

from flask import jsonify, current_app, Response


def root_endpoint() -> Response:
    """
    Root endpoint for the application.

    This function serves as the root endpoint of the application. It retrieves
    the `INVENTORY_PROVIDER` configuration from the current Flask application context.
    If `INVENTORY_PROVIDER` is callable, it invokes the provider and returns the
    resulting data as a JSON response. If `INVENTORY_PROVIDER` is not set or not callable,
    it returns an empty JSON array.

    Returns:
        Response: A Flask JSON response containing the inventory data or an empty array.
    """
    inventory_provider: Any | None = current_app.config.get(
        "INVENTORY_PROVIDER"
    )
    if inventory_provider and callable(inventory_provider):
        return jsonify(inventory_provider())
    return jsonify([])
