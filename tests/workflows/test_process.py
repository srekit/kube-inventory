import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock
from app.workflows.process import output
from app.workflows import pods_inventory


class TestOutput(unittest.TestCase):
    def setUp(self) -> None:
        """
        Sets up the test environment before each test method is executed.

        This method initializes a mock `PodsInventoried` object and stores it in a list
        to simulate a pod inventory. It also creates a temporary directory for use in
        the tests.
        """
        self.mock_pod: MagicMock = MagicMock(spec=pods_inventory.PodsInventoried)
        self.pods = [self.mock_pod]
        self.temp_dir = tempfile.mkdtemp()


    def tearDown(self) -> None:
        """
        Cleans up the test environment after each test method is executed.

        This method removes all files in the temporary directory created during the test
        and deletes the directory itself to ensure no leftover artifacts remain.
        """
        if os.path.exists(self.temp_dir):
            for file in os.listdir(self.temp_dir):
                os.remove(os.path.join(self.temp_dir, file))
            os.rmdir(self.temp_dir)


    @patch('app.workflows.process.file_operations.content_to_file')
    @patch('app.workflows.process.outputs.csv')
    def test_output_csv_mode(self, mock_csv, mock_content_to_file) -> None:
        """
        Tests the `output` function with CSV mode.

        This test verifies that the `output` function correctly generates a CSV file
        containing the pod inventory and saves it to the specified directory. It mocks
        the `outputs.csv` function to return a sample CSV string and ensures that the
        `file_operations.content_to_file` function is called with the correct arguments.

        Args:
            mock_csv (MagicMock): Mock for the `outputs.csv` function.
            mock_content_to_file (MagicMock): Mock for the `file_operations.content_to_file` function.
        """
        mock_csv.return_value = "csv,data"

        output(self.pods, self.temp_dir, "csv")

        mock_csv.assert_called_once_with(self.pods)
        mock_content_to_file.assert_called_once_with(
            file_path=f"{self.temp_dir}/inventory.csv",
            content="csv,data"
        )


    @patch('app.workflows.process.file_operations.content_to_file')
    @patch('app.workflows.process.outputs.json')
    def test_output_json_mode(self, mock_json, mock_content_to_file) -> None:
        """
        Tests the `output` function with JSON mode.

        This test verifies that the `output` function correctly generates a JSON file
        containing the pod inventory and saves it to the specified directory. It mocks
        the `outputs.json` function to return a sample JSON object and ensures that the
        `file_operations.content_to_file` function is called with the correct arguments.

        Args:
            mock_json (MagicMock): Mock for the `outputs.json` function.
            mock_content_to_file (MagicMock): Mock for the `file_operations.content_to_file` function.
        """
        mock_json.return_value = [{"key": "value"}]

        output(self.pods, self.temp_dir, "json")

        mock_json.assert_called_once_with(self.pods)
        mock_content_to_file.assert_called_once_with(
            file_path=f"{self.temp_dir}/inventory.json",
            content=[{"key": "value"}]
        )


    @patch('app.workflows.process.logging.error')
    @patch('app.workflows.process.sys.exit')
    def test_output_unsupported_mode(self, mock_exit, mock_log_error) -> None:
        """
        Tests the `output` function with an unsupported mode.

        This test verifies that the `output` function logs an error message and exits
        the program when an unsupported output mode is provided. It mocks the `logging.error`
        and `sys.exit` functions to ensure they are called with the correct arguments.

        Args:
            mock_exit (MagicMock): Mock for the `sys.exit` function.
            mock_log_error (MagicMock): Mock for the `logging.error` function.
        """
        output(self.pods, self.temp_dir, "xml")

        mock_log_error.assert_called_once_with("Unsupported output mode: xml")
        mock_exit.assert_called_once_with(1)


if __name__ == '__main__':
    unittest.main()
