import collections

from collections import OrderedDict
from typing import Any

from kubernetes.client import V1PodList


def list_json(pods: V1PodList) -> list[dict]:
    """
    Convert a list of Kubernetes pod objects into a JSON-serializable format.

    This function takes a list of Kubernetes pod objects and extracts relevant
    metadata, annotations, labels, and container information. The resulting
    data is structured as a list of dictionaries, making it suitable for JSON serialization.

    Args:
        pods: A Kubernetes API object containing a list of pod items.

    Returns:
        list[dict]: A list of dictionaries, where each dictionary represents a pod
        with its metadata, annotations, labels, and container details.
    """
    pods_json: list[dict] = []
    for pod in pods.items:
        if pod.metadata is None or pod.spec is None:
            continue

        p: OrderedDict[Any, Any] = collections.OrderedDict()
        p["name"] = pod.metadata.name
        p["namespace"] = pod.metadata.namespace
        p["annotations"] = pod.metadata.annotations
        p["labels"] = pod.metadata.labels

        containers: list[dict] = []
        for container in pod.spec.containers:
            c: OrderedDict[Any, Any] = collections.OrderedDict()
            c["name"] = container.name
            c["image"] = container.image
            containers.append(c)

        p["containers"] = containers
        pods_json.append(p)

    return pods_json
