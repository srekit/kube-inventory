from typing import List

from app.workflows import pods_inventory


def json(pods: List[pods_inventory.PodsInventoried]) -> list[dict]:
    """
    Converts a list of PodsInventoried objects into a list of dictionaries.

    Args:
        pods (List[pods_inventory.PodsInventoried]): A list of PodsInventoried objects
        representing the current state of pods.

    Returns:
        list[dict]: A list of dictionaries where each dictionary contains the following keys:
            - "name": The name of the pod.
            - "namespace": The namespace the pod belongs to.
            - "repo": The repository associated with the pod.
            - "current_release_date": The release date of the current version.
            - "current_release_name": The name of the current release.
            - "latest_release_date": The release date of the latest version.
            - "latest_release_name": The name of the latest release.
            - "versions_to_latest_release": The number of versions between the current and latest release.
    """
    output: list[dict] = []
    for pod in pods:
        pod_info: dict = {
            "name": pod.name,
            "namespace": pod.namespace,
            "repo": pod.repo,
            "current_release_date": pod.current_release_date,
            "current_release_name": pod.current_release_name,
            "latest_release_date": pod.latest_release_date,
            "latest_release_name": pod.latest_release_name,
            "versions_to_latest_release": pod.versions_to_latest_release,
        }
        output.append(pod_info)
    return output


def csv(pods: List[pods_inventory.PodsInventoried]) -> str:
    """
    Converts a list of PodsInventoried objects into a CSV-formatted string.

    Args:
        pods (List[pods_inventory.PodsInventoried]): A list of PodsInventoried objects
        representing the current state of pods.

    Returns:
        str: A CSV-formatted string where each row represents a pod and contains the following columns:
            - "name": The name of the pod.
            - "namespace": The namespace the pod belongs to.
            - "repo": The repository associated with the pod.
            - "current_release_date": The release date of the current version.
            - "current_release_name": The name of the current release.
            - "latest_release_date": The release date of the latest version.
            - "latest_release_name": The name of the latest release.
            - "versions_to_latest_release": The number of versions between the current and latest release.
    """
    output: str = "name,namespace,repo,current_release_date,current_release_name,latest_release_date,latest_release_name,versions_to_latest_release\n"
    for pod in pods:
        output += f"{pod.name},{pod.namespace},{pod.repo},{pod.current_release_date},{pod.current_release_name},{pod.latest_release_date},{pod.latest_release_name},{pod.versions_to_latest_release}\n"
    return output
