import logging
from typing import Optional

from kubernetes import client, config
from kubernetes.client.models.v1_pod_list import V1PodList


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
            logging.debug(f"Loading Kubernetes config from kubeconfig file: {kube_config_path}")
            config.load_kube_config(kube_config_path)
        else:
            logging.debug("Loading Kubernetes config from in-cluster configuration")
            config.load_incluster_config()
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
