from collections import OrderedDict
from unittest.mock import Mock

from app.libs.kube_lib import list_json


class TestListJson:
    def test_list_json_single_pod_single_container(self) -> None:
        """
        Test the `list_json` function with a single pod containing a single container.

        This test verifies that the `list_json` function correctly processes a pod with:
        - A single container
        - Metadata such as name, namespace, annotations, and labels

        Assertions:
        - The result contains exactly one pod.
        - The pod's metadata and container details match the expected values.
        """
        mock_container: Mock = Mock()
        mock_container.name = "nginx"
        mock_container.image = "nginx:1.20"

        mock_pod: Mock = Mock()
        mock_pod.metadata.name = "nginx-pod"
        mock_pod.metadata.namespace = "default"
        mock_pod.metadata.annotations = {"app": "nginx"}
        mock_pod.metadata.labels = {"version": "v1"}
        mock_pod.spec.containers = [mock_container]

        mock_pods: Mock = Mock()
        mock_pods.items = [mock_pod]

        result: list[dict] = list_json(mock_pods)

        assert len(result) == 1
        pod_data: dict = result[0]
        assert pod_data["name"] == "nginx-pod"
        assert pod_data["namespace"] == "default"
        assert pod_data["annotations"] == {"app": "nginx"}
        assert pod_data["labels"] == {"version": "v1"}
        assert len(pod_data["containers"]) == 1
        assert pod_data["containers"][0]["name"] == "nginx"
        assert pod_data["containers"][0]["image"] == "nginx:1.20"


    def test_list_json_single_pod_multiple_containers(self) -> None:
        """
        Test the `list_json` function with a single pod containing multiple containers.

        This test verifies that the `list_json` function correctly processes a pod with:
        - Multiple containers
        - Metadata such as name, namespace, annotations, and labels

        Assertions:
        - The result contains exactly one pod.
        - The pod's metadata matches the expected values.
        - The pod contains two containers with the correct names and images.
        """
        mock_container1: Mock = Mock()
        mock_container1.name = "nginx"
        mock_container1.image = "nginx:1.20"

        mock_container2 = Mock()
        mock_container2.name = "sidecar"
        mock_container2.image = "busybox:latest"

        # Mock pod with multiple containers
        mock_pod: Mock = Mock()
        mock_pod.metadata.name = "multi-container-pod"
        mock_pod.metadata.namespace = "production"
        mock_pod.metadata.annotations = {"app": "web-app"}
        mock_pod.metadata.labels = {"tier": "frontend"}
        mock_pod.spec.containers = [mock_container1, mock_container2]

        mock_pods: Mock = Mock()
        mock_pods.items = [mock_pod]

        result: list[dict] = list_json(mock_pods)

        assert len(result) == 1
        pod_data: dict = result[0]
        assert pod_data["name"] == "multi-container-pod"
        assert pod_data["namespace"] == "production"
        assert len(pod_data["containers"]) == 2
        assert pod_data["containers"][0]["name"] == "nginx"
        assert pod_data["containers"][0]["image"] == "nginx:1.20"
        assert pod_data["containers"][1]["name"] == "sidecar"
        assert pod_data["containers"][1]["image"] == "busybox:latest"


    def test_list_json_multiple_pods(self) -> None:
        """
        Test the `list_json` function with multiple pods.

        This test verifies that the `list_json` function correctly processes a list of pods,
        where each pod contains metadata and a single container.

        Test setup:
        - Two mock pods are created, each with unique metadata (name, namespace, annotations, labels)
          and a single container with specific names and images.

        Assertions:
        - The result contains exactly two pods.
        - Each pod's metadata and container details match the expected values.
        """
        mock_container1: Mock = Mock()
        mock_container1.name = "app1"
        mock_container1.image = "app1:v1.0"

        mock_pod1: Mock = Mock()
        mock_pod1.metadata.name = "pod1"
        mock_pod1.metadata.namespace = "namespace1"
        mock_pod1.metadata.annotations = {"annotation1": "value1"}
        mock_pod1.metadata.labels = {"label1": "value1"}
        mock_pod1.spec.containers = [mock_container1]

        mock_container2: Mock = Mock()
        mock_container2.name = "app2"
        mock_container2.image = "app2:v2.0"

        mock_pod2: Mock = Mock()
        mock_pod2.metadata.name = "pod2"
        mock_pod2.metadata.namespace = "namespace2"
        mock_pod2.metadata.annotations = {"annotation2": "value2"}
        mock_pod2.metadata.labels = {"label2": "value2"}
        mock_pod2.spec.containers = [mock_container2]

        mock_pods: Mock = Mock()
        mock_pods.items = [mock_pod1, mock_pod2]

        result: list[dict] = list_json(mock_pods)

        assert len(result) == 2

        assert result[0]["name"] == "pod1"
        assert result[0]["namespace"] == "namespace1"
        assert result[0]["annotations"] == {"annotation1": "value1"}
        assert result[0]["labels"] == {"label1": "value1"}
        assert result[0]["containers"][0]["name"] == "app1"
        assert result[0]["containers"][0]["image"] == "app1:v1.0"

        assert result[1]["name"] == "pod2"
        assert result[1]["namespace"] == "namespace2"
        assert result[1]["annotations"] == {"annotation2": "value2"}
        assert result[1]["labels"] == {"label2": "value2"}
        assert result[1]["containers"][0]["name"] == "app2"
        assert result[1]["containers"][0]["image"] == "app2:v2.0"


    def test_list_json_empty_pods_list(self) -> None:
        """
        Test the `list_json` function with an empty list of pods.

        This test verifies that the `list_json` function correctly handles the case
        where no pods are provided in the input.

        Assertions:
        - The result is an empty list.
        """
        mock_pods: Mock = Mock()
        mock_pods.items = []

        result: list[dict] = list_json(mock_pods)

        assert result == []


    def test_list_json_pod_with_none_annotations_and_labels(self) -> None:
        """
        Test the `list_json` function with a pod that has `None` annotations and labels.

        This test verifies that the `list_json` function correctly handles a pod where:
        - Annotations and labels are explicitly set to `None`.
        - The pod contains a single container with specific metadata.

        Assertions:
        - The result contains exactly one pod.
        - The pod's name and namespace match the expected values.
        - The annotations and labels are `None`.
        - The pod contains exactly one container.
        """
        mock_container: Mock = Mock()
        mock_container.name = "test-container"
        mock_container.image = "test:latest"

        mock_pod: Mock = Mock()
        mock_pod.metadata.name = "test-pod"
        mock_pod.metadata.namespace = "test-namespace"
        mock_pod.metadata.annotations = None
        mock_pod.metadata.labels = None
        mock_pod.spec.containers = [mock_container]

        mock_pods: Mock = Mock()
        mock_pods.items = [mock_pod]

        result: list[dict] = list_json(mock_pods)

        assert len(result) == 1
        pod_data: dict = result[0]
        assert pod_data["name"] == "test-pod"
        assert pod_data["namespace"] == "test-namespace"
        assert pod_data["annotations"] is None
        assert pod_data["labels"] is None
        assert len(pod_data["containers"]) == 1


    def test_list_json_pod_with_empty_containers(self) -> None:
        """
        Test the `list_json` function with a pod that has no containers.

        This test verifies that the `list_json` function correctly handles a pod where:
        - The pod has metadata such as name, namespace, annotations, and labels.
        - The pod's `spec.containers` list is empty.

        Assertions:
        - The result contains exactly one pod.
        - The pod's name matches the expected value.
        - The `containers` field in the result is an empty list.
        """
        mock_pod: Mock = Mock()
        mock_pod.metadata.name = "empty-pod"
        mock_pod.metadata.namespace = "test-namespace"
        mock_pod.metadata.annotations = {}
        mock_pod.metadata.labels = {}
        mock_pod.spec.containers = []

        mock_pods: Mock = Mock()
        mock_pods.items = [mock_pod]

        result: list[dict] = list_json(mock_pods)

        assert len(result) == 1
        pod_data: dict = result[0]
        assert pod_data["name"] == "empty-pod"
        assert pod_data["containers"] == []


    def test_list_json_returns_ordered_dict_structure(self) -> None:
        """
        Test the `list_json` function to ensure it returns an `OrderedDict` structure.

        This test verifies that the `list_json` function correctly processes a pod and:
        - Returns the pod data as an `OrderedDict`.
        - Ensures the keys in the `OrderedDict` are in the expected order.
        - Verifies that the container data within the pod is also an `OrderedDict` with the correct key order.

        Test setup:
        - A mock pod is created with metadata (name, namespace, annotations, labels) and a single container.

        Assertions:
        - The pod data is an instance of `OrderedDict`.
        - The keys in the pod data are in the order: ["name", "namespace", "annotations", "labels", "containers"].
        - The container data is an instance of `OrderedDict`.
        - The keys in the container data are in the order: ["name", "image"].
        """
        mock_container: Mock = Mock()
        mock_container.name = "test-container"
        mock_container.image = "test:latest"

        mock_pod: Mock = Mock()
        mock_pod.metadata.name = "test-pod"
        mock_pod.metadata.namespace = "test-namespace"
        mock_pod.metadata.annotations = {"key": "value"}
        mock_pod.metadata.labels = {"env": "test"}
        mock_pod.spec.containers = [mock_container]

        mock_pods: Mock = Mock()
        mock_pods.items = [mock_pod]

        result = list_json(mock_pods)

        pod_data: dict = result[0]
        assert isinstance(pod_data, OrderedDict)
        assert list(pod_data.keys()) == ["name", "namespace", "annotations", "labels", "containers"]

        container_data: dict = pod_data["containers"][0]
        assert isinstance(container_data, OrderedDict)
        assert list(container_data.keys()) == ["name", "image"]
