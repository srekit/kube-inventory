import logging

from kubernetes import client
from kubernetes.config import load_incluster_config, load_kube_config  # type: ignore[attr-defined]
from kubernetes.client.models.v1_pod_list import V1PodList
from typing import Optional, Dict, Any


class KubernetesClient:
    def __init__(self, kube_config_path: Optional[str] = None) -> None:
        """
        Initializes the KubernetesClient instance.

        This constructor sets up the Kubernetes API client by loading the appropriate
        Kubernetes configuration. It supports both kubeconfig files and in-cluster
        configurations.

        Args:
            kube_config_path (Optional[str]): The path to the kubeconfig file. If None,
                                              the in-cluster configuration is used.

        Logs:
            - A debug message indicating whether the kubeconfig file or in-cluster
              configuration is being loaded.
        """
        if kube_config_path:
            logging.debug(
                f"Loading Kubernetes config from kubeconfig file: {kube_config_path}"
            )
            load_kube_config(kube_config_path)
        else:
            logging.debug(
                "Loading Kubernetes config from in-cluster configuration"
            )
            load_incluster_config()
        self.k8s_api = client.CoreV1Api()

    def list_pods(self) -> V1PodList:
        """
        Retrieves a list of all pods in the Kubernetes cluster.

        Returns:
            V1PodList: A list of pods across all namespaces in the cluster.

        Logs:
            - A debug message indicating that the pods are being listed.
        """
        logging.debug("Listing all pods in the cluster")
        pods = self.k8s_api.list_pod_for_all_namespaces(watch=False)
        return pods

    def health_check(self) -> Dict[str, Any]:
        """
        Performs a health check on the Kubernetes API connection.

        Returns:
            Dict[str, Any]: A dictionary with status and optional error message.
                           {"status": "healthy"} or {"status": "unhealthy", "error": str}
        """
        try:
            self.k8s_api.list_namespace(limit=1)
            logging.debug("Kubernetes health check successful")
            return {"status": "healthy"}
        except Exception as e:
            logging.error(f"Kubernetes health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
