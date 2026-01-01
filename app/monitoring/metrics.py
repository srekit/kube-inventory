import logging

from app.monitoring.registry import init_storage

from prometheus_client import Gauge

METRICS: dict[str, object] = {}
_metrics_registered: bool = False


def clear_metrics() -> None:
    """
    Clear all registered metrics.

    This function initializes the storage with the `clean` parameter set to `True`,
    effectively clearing any previously registered metrics.
    """
    init_storage(clean=True)


def register_metrics() -> None:
    """
    Register Prometheus metrics for monitoring.

    This function initializes and registers two Prometheus `Gauge` metrics:
    - `kube_inventory_pods_total`: Tracks the total number of pods in the Kubernetes cluster.
    - `kube_inventory_pod_versions_to_latest_release`: Tracks the number of versions behind the latest release for each pod.

    The function ensures that metrics are registered only once by using the `_metrics_registered` flag.

    Metrics registered:
    - `kube_inventory_pods_total`: A simple gauge metric.
    - `kube_inventory_pod_versions_to_latest_release`: A gauge metric with the following labels:
        - `container_name`
        - `current_release_date`
        - `current_release_name`
        - `latest_release_date`
        - `latest_release_name`
        - `name`
        - `namespace`
        - `repo`
        - `silenced`
    - kube_inventory_pod_current_release_timestamp: A gauge metric with labels:
        - `container_name`
        - `current_release_date`
        - `current_release_name`
        - `name`
        - `namespace`
        - `repo`
        - `silenced`
    - kube_inventory_pod_latest_release_timestamp: A gauge metric with labels:
        - `container_name`
        - `latest_release_date`
        - `latest_release_name`
        - `name`
        - `namespace`
        - `repo`
        - `silenced`

    Logging:
    - Logs a debug message if metrics are already registered.
    - Logs an info message listing the registered metrics after successful registration.
    """
    global _metrics_registered
    if _metrics_registered:
        logging.debug("Metrics already registered, skipping registration")
        return

    METRICS["kube_inventory_pods_total"] = Gauge(
        "kube_inventory_pods_total",
        "Total number of pods in the Kubernetes cluster",
        multiprocess_mode="livesum",
    )

    METRICS["kube_inventory_pod_versions_to_latest_release"] = Gauge(
        "kube_inventory_pod_versions_to_latest_release",
        "Number of versions behind the latest release for each pod",
        [
            "container_name",
            "current_release_date",
            "current_release_name",
            "latest_release_date",
            "latest_release_name",
            "name",
            "namespace",
            "repo",
            "silenced",
        ],
        multiprocess_mode="livesum",
    )

    METRICS["kube_inventory_pod_current_release_timestamp"] = Gauge(
        "kube_inventory_pod_current_release_timestamp",
        "Timestamp of the current release for each pod",
        [
            "container_name",
            "current_release_date",
            "current_release_name",
            "name",
            "namespace",
            "repo",
            "silenced",
        ],
    )

    METRICS["kube_inventory_pod_latest_release_timestamp"] = Gauge(
        "kube_inventory_pod_latest_release_timestamp",
        "Timestamp of the latest release for each pod",
        [
            "container_name",
            "latest_release_date",
            "latest_release_name",
            "name",
            "namespace",
            "repo",
            "silenced",
        ],
    )

    _metrics_registered = True
    logging.info(f"Registered metrics: {list(METRICS.keys())}")


def update_metric(
    metric_name: str, value: float, labels: dict[str, str] | None = None
) -> None:
    """
    Update the value of a Prometheus metric.

    This function updates the value of a registered Prometheus `Gauge` metric. If the metric
    is not found in the `METRICS` registry, a warning is logged. If the metric supports labels,
    the value is updated with the provided labels; otherwise, the value is updated directly.

    Parameters:
    - metric_name (str): The name of the metric to update.
    - value (float): The value to set for the metric.
    - labels (dict[str, str], optional): A dictionary of label key-value pairs to associate
      with the metric. Defaults to None.

    Logging:
    - Logs a debug message when attempting to update the metric.
    - Logs a warning if the metric is not found in the registry.
    - Logs an error if the metric is not a `Gauge` or an unsupported type.
    - Logs a debug message after successfully updating the metric.

    Behavior:
    - If the metric supports labels and `labels` is provided, the value is updated with the labels.
    - If the metric does not support labels, the value is updated directly.
    """
    logging.debug(
        f"Attempting to update metric '{metric_name}' with value {value}"
    )

    if metric_name not in METRICS:
        logging.warning(f"Metric '{metric_name}' not found in registry")
        return

    metric: Gauge = METRICS[metric_name]  # type: ignore[assignment]
    if hasattr(metric, "set"):
        if labels:
            metric.labels(**labels).set(value)
            logging.debug(
                "Gauge '%s' set to %s with labels %s",
                metric_name,
                value,
                labels,
            )
        else:
            metric.set(value)
            logging.debug("Gauge '%s' set to %s", metric_name, value)
    else:
        logging.error(
            "Metric '%s' is not a Gauge or unsupported type", metric_name
        )
