import logging
import time

from typing import List, Any

from app.clients.kube import KubernetesClient
from app.monitoring.metrics import register_metrics, update_metric
from app.workflows import pods_inventory, process
from app.workflows.pods_inventory import PodsInventoried


current_pods_inventory: list[PodsInventoried] = []


def get_inventory_json() -> list[dict]:
    """
    Converts the current pods inventory into a list of dictionaries.

    This function accesses the global `current_pods_inventory` variable, which is expected to
    contain a list of objects representing the current state of pods. Each object in the list
    is converted to a dictionary using its `__dict__` attribute, which provides a shallow copy
    of the object's attributes.

    Returns:
        list[dict]: A list of dictionaries, where each dictionary represents the attributes
        of a pod in the current inventory.
    """
    global current_pods_inventory
    return [pod.__dict__ for pod in current_pods_inventory]


def run_inventory_loop(args_values: Any, kube_client: KubernetesClient) -> None:
    """
    Continuously generates and processes the inventory of Kubernetes pods.

    This function runs an infinite loop that:
    1. Generates the current inventory of Kubernetes pods using the `process.generate` function.
    2. Updates the global `current_pods_inventory` variable with the generated inventory.
    3. Updates Prometheus metrics for each pod in the inventory, including details about
       versions, releases, and other metadata.
    4. Logs the total number of inventoried pods and waits for a specified interval before
       repeating the process.

    Args:
        args_values: An object containing configuration values, including:
            - default_apps_file_path (str): Path to the default apps file.
            - extra_apps_file_path (str): Path to the extra apps file.
            - github_access_token (str): GitHub access token for API authentication.
            - github_api_url (str): URL of the GitHub API.
            - output_refresh_interval_seconds (int): Interval (in seconds) between inventory refreshes.
        kube_client: Kubernetes client object.

    Returns:
        None
    """
    global current_pods_inventory
    register_metrics()

    while True:
        pods_inventoried: List[
            pods_inventory.PodsInventoried
        ] = process.generate(
            extra_apps_file_path=args_values.extra_apps_file_path,
            github_access_token=args_values.github_access_token,
            github_api_url=args_values.github_api_url,
            kube_client=kube_client,
        )

        current_pods_inventory = pods_inventoried

        for pod_inventoried in pods_inventoried:
            update_metric(
                metric_name="kube_inventory_pod_versions_to_latest_release",
                value=pod_inventoried.versions_to_latest_release,
                labels={
                    "container_name": pod_inventoried.container_name,
                    "current_release_date": pod_inventoried.current_release_date,
                    "current_release_name": pod_inventoried.current_release_name,
                    "latest_release_date": pod_inventoried.latest_release_date,
                    "latest_release_name": pod_inventoried.latest_release_name,
                    "name": pod_inventoried.name,
                    "namespace": pod_inventoried.namespace,
                    "repo": pod_inventoried.repo,
                    "silenced": str(pod_inventoried.silenced).lower(),
                },
            )

            update_metric(
                metric_name="kube_inventory_pod_current_release_timestamp",
                value=float(pod_inventoried.current_release_timestamp),
                labels={
                    "container_name": pod_inventoried.container_name,
                    "current_release_date": pod_inventoried.current_release_date,
                    "current_release_name": pod_inventoried.current_release_name,
                    "name": pod_inventoried.name,
                    "namespace": pod_inventoried.namespace,
                    "repo": pod_inventoried.repo,
                    "silenced": str(pod_inventoried.silenced).lower(),
                },
            )

            update_metric(
                metric_name="kube_inventory_pod_latest_release_timestamp",
                value=float(pod_inventoried.latest_release_timestamp),
                labels={
                    "container_name": pod_inventoried.container_name,
                    "latest_release_date": pod_inventoried.latest_release_date,
                    "latest_release_name": pod_inventoried.latest_release_name,
                    "name": pod_inventoried.name,
                    "namespace": pod_inventoried.namespace,
                    "repo": pod_inventoried.repo,
                    "silenced": str(pod_inventoried.silenced).lower(),
                },
            )

        total_pods: int = len(pods_inventoried)
        update_metric(metric_name="kube_inventory_pods_total", value=total_pods)
        logging.info(
            f"Pods inventoried: {len(pods_inventoried)}, next refresh in {args_values.output_refresh_interval_seconds} seconds"
        )

        time.sleep(args_values.output_refresh_interval_seconds)
