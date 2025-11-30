import unittest

from unittest.mock import patch, MagicMock
from kubernetes.client.models.v1_pod_list import V1PodList

from app.clients.kube import KubernetesClient


class TestKubernetesClient(unittest.TestCase):
    @patch("app.clients.kube.client.CoreV1Api")
    @patch("app.clients.kube.load_kube_config")
    @patch("app.clients.kube.logging.debug")
    def test_init_with_kubeconfig_path(
        self,
        mock_debug: MagicMock,
        mock_load_kube_config: MagicMock,
        mock_core_v1_api: MagicMock,
    ) -> None:
        """
        Test the initialization of the KubernetesClient with a specified kubeconfig path.

        This test verifies that the KubernetesClient correctly loads the kubeconfig file,
        initializes the CoreV1Api instance, and logs the appropriate debug message.

        Args:
            mock_debug: Mocked logging.debug function.
            mock_load_kube_config: Mocked load_kube_config function.
            mock_core_v1_api: Mocked CoreV1Api class.
        """
        kube_config_path: str = "/path/to/kubeconfig"
        mock_api_instance: MagicMock = MagicMock()
        mock_core_v1_api.return_value = mock_api_instance

        client: KubernetesClient = KubernetesClient(
            kube_config_path=kube_config_path
        )

        mock_load_kube_config.assert_called_once_with(kube_config_path)
        mock_debug.assert_called_once_with(
            f"Loading Kubernetes config from kubeconfig file: {kube_config_path}"
        )
        mock_core_v1_api.assert_called_once()
        self.assertEqual(client.k8s_api, mock_api_instance)

    @patch("app.clients.kube.client.CoreV1Api")
    @patch("app.clients.kube.load_incluster_config")
    @patch("app.clients.kube.logging.debug")
    def test_init_without_kubeconfig_path(
        self,
        mock_debug: MagicMock,
        mock_load_incluster_config: MagicMock,
        mock_core_v1_api: MagicMock,
    ) -> None:
        """
        Test the initialization of the KubernetesClient without specifying a kubeconfig path.

        This test ensures that the KubernetesClient correctly loads the in-cluster configuration,
        initializes the CoreV1Api instance, and logs the appropriate debug message.

        Args:
            mock_debug: Mocked logging.debug function.
            mock_load_incluster_config: Mocked load_incluster_config function.
            mock_core_v1_api: Mocked CoreV1Api class.
        """
        mock_api_instance: MagicMock = MagicMock()
        mock_core_v1_api.return_value = mock_api_instance

        client: KubernetesClient = KubernetesClient()

        mock_load_incluster_config.assert_called_once()
        mock_debug.assert_called_once_with(
            "Loading Kubernetes config from in-cluster configuration"
        )
        mock_core_v1_api.assert_called_once()
        self.assertEqual(client.k8s_api, mock_api_instance)

    @patch("app.clients.kube.client.CoreV1Api")
    @patch("app.clients.kube.load_incluster_config")
    @patch("app.clients.kube.logging.debug")
    def test_init_with_none_kubeconfig_path(
        self,
        mock_debug: MagicMock,
        mock_load_incluster_config: MagicMock,
        mock_core_v1_api: MagicMock,
    ) -> None:
        """
        Test the initialization of the KubernetesClient with None as the kubeconfig path.

        This test ensures that the KubernetesClient correctly falls back to using the in-cluster
        configuration when the kubeconfig path is explicitly set to None. It verifies that the
        CoreV1Api instance is initialized and the appropriate debug message is logged.

        Args:
            mock_debug: Mocked logging.debug function.
            mock_load_incluster_config: Mocked load_incluster_config function.
            mock_core_v1_api: Mocked CoreV1Api class.
        """
        mock_api_instance: MagicMock = MagicMock()
        mock_core_v1_api.return_value = mock_api_instance

        client: KubernetesClient = KubernetesClient(kube_config_path=None)

        mock_load_incluster_config.assert_called_once()
        mock_debug.assert_called_once_with(
            "Loading Kubernetes config from in-cluster configuration"
        )
        mock_core_v1_api.assert_called_once()
        self.assertEqual(client.k8s_api, mock_api_instance)

    @patch("app.clients.kube.client.CoreV1Api")
    @patch("app.clients.kube.load_incluster_config")
    def test_list_pods(
        self, mock_load_incluster_config: MagicMock, mock_core_v1_api: MagicMock
    ) -> None:
        """
        Test the `list_pods` method of the KubernetesClient.

        This test verifies that the `list_pods` method correctly retrieves the list of pods
        from the Kubernetes cluster by calling the `list_pod_for_all_namespaces` method
        of the CoreV1Api instance. It also ensures that the appropriate debug message is logged.

        Args:
            mock_load_incluster_config: Mocked `load_incluster_config` function.
            mock_core_v1_api: Mocked `CoreV1Api` class.
        """
        mock_api_instance: MagicMock = MagicMock()
        mock_core_v1_api.return_value = mock_api_instance
        mock_pod_list: MagicMock = MagicMock(spec=V1PodList)
        mock_api_instance.list_pod_for_all_namespaces.return_value = (
            mock_pod_list
        )

        client: KubernetesClient = KubernetesClient()

        with patch("app.clients.kube.logging.debug") as mock_debug:
            result: V1PodList = client.list_pods()

        mock_api_instance.list_pod_for_all_namespaces.assert_called_once_with(
            watch=False
        )
        mock_debug.assert_called_once_with("Listing all pods in the cluster")
        self.assertEqual(result, mock_pod_list)
        self.assertIsInstance(result, type(mock_pod_list))

    @patch("app.clients.kube.client.CoreV1Api")
    @patch("app.clients.kube.load_kube_config")
    def test_integration_kubeconfig_and_list_pods(
        self, mock_load_kube_config: MagicMock, mock_core_v1_api: MagicMock
    ) -> None:
        """
        Test the integration of KubernetesClient initialization with a kubeconfig path and the `list_pods` method.

        This test verifies that the KubernetesClient can be initialized with a specified kubeconfig path,
        and that the `list_pods` method correctly retrieves the list of pods from the Kubernetes cluster.
        It ensures that the appropriate methods are called and the expected results are returned.

        Args:
            mock_load_kube_config: Mocked `load_kube_config` function.
            mock_core_v1_api: Mocked `CoreV1Api` class.
        """
        kube_config_path: str = "/custom/kubeconfig"
        mock_api_instance: MagicMock = MagicMock()
        mock_core_v1_api.return_value = mock_api_instance
        mock_pod_list: MagicMock = MagicMock(spec=V1PodList)
        mock_api_instance.list_pod_for_all_namespaces.return_value = (
            mock_pod_list
        )

        client: KubernetesClient = KubernetesClient(
            kube_config_path=kube_config_path
        )
        result: V1PodList = client.list_pods()

        mock_load_kube_config.assert_called_once_with(kube_config_path)
        mock_api_instance.list_pod_for_all_namespaces.assert_called_once_with(
            watch=False
        )
        self.assertEqual(result, mock_pod_list)


if __name__ == "__main__":
    unittest.main()
