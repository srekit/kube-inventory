import unittest
from unittest.mock import MagicMock

from app.workflows import outputs, pods_inventory


class TestOutputs(unittest.TestCase):
    def setUp(self) -> None:
        """
        Sets up the test fixtures for the unit tests.

        This method initializes two mock `PodsInventoried` objects with predefined attributes
        to simulate Kubernetes pod data. These mock objects are added to a list, which is used
        as test data in the unit tests.
        """
        self.mock_pod1: MagicMock = MagicMock(
            spec=pods_inventory.PodsInventoried
        )
        self.mock_pod1.name = "test-pod-1"
        self.mock_pod1.namespace = "default"
        self.mock_pod1.repo = "owner/repo1"
        self.mock_pod1.current_release_date = "2023-01-01"
        self.mock_pod1.current_release_name = "v1.0.0"
        self.mock_pod1.latest_release_date = "2023-01-15"
        self.mock_pod1.latest_release_name = "v1.2.0"
        self.mock_pod1.versions_to_latest_release = 2

        self.mock_pod2: MagicMock = MagicMock(
            spec=pods_inventory.PodsInventoried
        )
        self.mock_pod2.name = "test-pod-2"
        self.mock_pod2.namespace = "kube-system"
        self.mock_pod2.repo = "owner/repo2"
        self.mock_pod2.current_release_date = "2023-02-01"
        self.mock_pod2.current_release_name = "v2.0.0"
        self.mock_pod2.latest_release_date = "2023-02-01"
        self.mock_pod2.latest_release_name = "v2.0.0"
        self.mock_pod2.versions_to_latest_release = 0

        self.pods_list: list = [self.mock_pod1, self.mock_pod2]

    def test_json_with_multiple_pods(self) -> None:
        """
        Tests the `json` function with multiple pods.

        This test verifies that the `json` function correctly converts a list of
        `PodsInventoried` objects into a list of dictionaries. It checks the structure
        and content of the resulting dictionaries for multiple pods.

        Assertions:
            - The result is a list.
            - The length of the result matches the number of input pods.
            - The first pod's dictionary contains the expected key-value pairs.
            - The second pod's dictionary contains the expected key-value pairs.
        """
        result: list[dict] = outputs.json(self.pods_list)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

        pod1_dict: dict = result[0]
        self.assertEqual(pod1_dict["name"], "test-pod-1")
        self.assertEqual(pod1_dict["namespace"], "default")
        self.assertEqual(pod1_dict["repo"], "owner/repo1")
        self.assertEqual(pod1_dict["current_release_date"], "2023-01-01")
        self.assertEqual(pod1_dict["current_release_name"], "v1.0.0")
        self.assertEqual(pod1_dict["latest_release_date"], "2023-01-15")
        self.assertEqual(pod1_dict["latest_release_name"], "v1.2.0")
        self.assertEqual(pod1_dict["versions_to_latest_release"], 2)

        pod2_dict: dict = result[1]
        self.assertEqual(pod2_dict["name"], "test-pod-2")
        self.assertEqual(pod2_dict["namespace"], "kube-system")
        self.assertEqual(pod2_dict["repo"], "owner/repo2")
        self.assertEqual(pod2_dict["versions_to_latest_release"], 0)

    def test_json_with_empty_list(self) -> None:
        """
        Tests the `json` function with an empty list.

        This test verifies that the `json` function correctly handles an empty input list
        and returns an empty list as the result.

        Assertions:
            - The result is a list.
            - The length of the result is 0.
        """
        result: list[dict] = outputs.json([])

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    def test_json_with_single_pod(self) -> None:
        """
        Tests the `json` function with a single pod.

        This test verifies that the `json` function correctly converts a list containing
        a single `PodsInventoried` object into a list of dictionaries. It checks the structure
        and content of the resulting dictionary for the single pod.

        Assertions:
            - The result is a list.
            - The length of the result is 1.
            - The dictionary for the single pod contains the expected key-value pair for "name".
        """
        result: list[dict] = outputs.json([self.mock_pod1])

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "test-pod-1")

    def test_csv_with_multiple_pods(self) -> None:
        """
        Tests the `csv` function with multiple pods.

        This test verifies that the `csv` function correctly converts a list of
        `PodsInventoried` objects into a CSV string. It checks the structure of the
        resulting CSV, including the header and data rows.

        Assertions:
            - The result is a string.
            - The number of lines in the CSV matches the expected count (header + data rows).
            - The header row matches the expected format.
            - Each data row matches the expected format for the corresponding pod.
        """
        result: str = outputs.csv(self.pods_list)

        self.assertIsInstance(result, str)

        lines: list[str] = result.strip().split("\n")
        self.assertEqual(len(lines), 3)  # Header + 2 data rows

        expected_header: str = "name,namespace,repo,current_release_date,current_release_name,latest_release_date,latest_release_name,versions_to_latest_release"
        self.assertEqual(lines[0], expected_header)

        expected_row1: str = "test-pod-1,default,owner/repo1,2023-01-01,v1.0.0,2023-01-15,v1.2.0,2"
        self.assertEqual(lines[1], expected_row1)

        expected_row2: str = "test-pod-2,kube-system,owner/repo2,2023-02-01,v2.0.0,2023-02-01,v2.0.0,0"
        self.assertEqual(lines[2], expected_row2)

    def test_csv_with_empty_list(self) -> None:
        """
        Tests the `csv` function with an empty list.

        This test verifies that the `csv` function correctly handles an empty input list
        and returns a CSV string containing only the header row.

        Assertions:
            - The result is a string.
            - The number of lines in the CSV is 1 (only the header row).
            - The header row matches the expected format.
        """
        result: str = outputs.csv([])

        self.assertIsInstance(result, str)
        lines: list[str] = result.strip().split("\n")
        self.assertEqual(len(lines), 1)  # Only header

        expected_header: str = "name,namespace,repo,current_release_date,current_release_name,latest_release_date,latest_release_name,versions_to_latest_release"
        self.assertEqual(lines[0], expected_header)

    def test_csv_with_single_pod(self) -> None:
        """
        Tests the `csv` function with a single pod.

        This test verifies that the `csv` function correctly converts a list containing
        a single `PodsInventoried` object into a CSV string. It checks the structure
        and content of the resulting CSV, including the header and data row.

        Assertions:
            - The result is a string.
            - The number of lines in the CSV is 2 (header + 1 data row).
            - The data row matches the expected format for the single pod.
        """
        result: str = outputs.csv([self.mock_pod1])

        self.assertIsInstance(result, str)
        lines: list[str] = result.strip().split("\n")
        self.assertEqual(len(lines), 2)  # Header + 1 data row

        expected_row: str = "test-pod-1,default,owner/repo1,2023-01-01,v1.0.0,2023-01-15,v1.2.0,2"
        self.assertEqual(lines[1], expected_row)

    def test_csv_ends_with_newline(self) -> None:
        """
        Tests that the `csv` function output ends with a newline character.

        This test verifies that the CSV string returned by the `csv` function
        includes a trailing newline character at the end of the output.

        Assertions:
            - The result string ends with a newline character ('\n').
        """
        result: str = outputs.csv([self.mock_pod1])
        self.assertTrue(result.endswith("\n"))

    def test_json_dictionary_structure(self) -> None:
        """
        Tests the structure of the dictionary returned by the `json` function.

        This test verifies that the dictionary for a single `PodsInventoried` object
        contains all the expected keys. It ensures that the `json` function correctly
        maps the attributes of the `PodsInventoried` object to the dictionary keys.

        Assertions:
            - The set of keys in the resulting dictionary matches the expected set of keys.
        """
        result: list[dict] = outputs.json([self.mock_pod1])

        pod_dict: dict = result[0]
        expected_keys: set[str] = {
            "name",
            "namespace",
            "repo",
            "current_release_date",
            "current_release_name",
            "latest_release_date",
            "latest_release_name",
            "versions_to_latest_release",
        }

        self.assertEqual(set(pod_dict.keys()), expected_keys)


if __name__ == "__main__":
    unittest.main()
