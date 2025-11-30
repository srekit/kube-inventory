import unittest
import yaml

from unittest.mock import mock_open, patch

from app.common.file_check import check_is_yaml, file_exists


class TestFileExists(unittest.TestCase):
    @patch('os.path.exists')
    def test_file_exists_when_true(self, mock_exists) -> None:
        """
        Test the `file_exists` function when the file exists.

        This test verifies that the `file_exists` function correctly returns `True`
        when the specified file path exists.

        Steps:
        1. Mock the `os.path.exists` function to return `True`.
        2. Call the `file_exists` function with a test file path.
        3. Assert that the function returns `True`.
        4. Verify that the `os.path.exists` function is called once with the correct file path.

        Args:
            mock_exists (Mock): Mock object for the `os.path.exists` function.

        Raises:
            AssertionError: If the function does not return the expected result or the mock is not called as expected.
        """
        mock_exists.return_value = True
        test_file_path: str = "/path/to/existing/file.yaml"
        result: bool = file_exists(test_file_path)
        self.assertTrue(result)
        mock_exists.assert_called_once_with(test_file_path)


    @patch('os.path.exists')
    def test_file_exists_when_false(self, mock_exists) -> None:
        """
        Test the `file_exists` function when the file does not exist.

        This test verifies that the `file_exists` function correctly returns `False`
        when the specified file path does not exist.

        Steps:
        1. Mock the `os.path.exists` function to return `False`.
        2. Call the `file_exists` function with a test file path.
        3. Assert that the function returns `False`.
        4. Verify that the `os.path.exists` function is called once with the correct file path.

        Args:
            mock_exists (Mock): Mock object for the `os.path.exists` function.

        Raises:
            AssertionError: If the function does not return the expected result or the mock is not called as expected.
        """
        mock_exists.return_value = False
        test_file_path: str = "/path/to/non-existing/file.yaml"
        result: bool = file_exists(test_file_path)

        self.assertFalse(result)
        mock_exists.assert_called_once_with(test_file_path)


class TestCheckIsYaml(unittest.TestCase):
    @patch('app.common.file_check.file_exists')
    @patch('builtins.open', new_callable=mock_open, read_data="key: value")
    def test_check_is_yaml_valid_file(self, mock_file, mock_file_exists) -> None:
        """
        Test the `check_is_yaml` function with a valid YAML file.

        This test verifies that the `check_is_yaml` function correctly identifies a valid YAML file
        and returns `True`.

        Steps:
        1. Mock the `file_exists` function to return `True`, simulating that the file exists.
        2. Mock the `open` function to simulate reading a valid YAML file with the content "key: value".
        3. Call the `check_is_yaml` function with the test file path.
        4. Assert that the function returns `True`.
        5. Verify that the `file_exists` function is called once with the correct file path.

        Args:
            mock_file (Mock): Mock object for the `open` function.
            mock_file_exists (Mock): Mock object for the `file_exists` function.

        Raises:
            AssertionError: If the function does not return the expected result or the mocks are not called as expected.
        """
        mock_file_exists.return_value = True
        test_file_path: str = "/path/to/valid.yaml"
        result: bool = check_is_yaml(test_file_path)
        self.assertTrue(result)
        mock_file_exists.assert_called_once_with(file_path=test_file_path)


    @patch('app.common.file_check.file_exists')
    def test_check_is_yaml_nonexistent_file(self, mock_file_exists) -> None:
        """
        Test the `check_is_yaml` function with a nonexistent file.

        This test verifies that the `check_is_yaml` function correctly returns `False`
        when the specified file does not exist.

        Steps:
        1. Mock the `file_exists` function to return `False`, simulating that the file does not exist.
        2. Call the `check_is_yaml` function with the test file path.
        3. Assert that the function returns `False`.
        4. Verify that the `file_exists` function is called once with the correct file path.

        Args:
            mock_file_exists (Mock): Mock object for the `file_exists` function.

        Raises:
            AssertionError: If the function does not return the expected result or the mock is not called as expected.
        """
        mock_file_exists.return_value = False
        test_file_path: str = "/path/to/nonexistent.yaml"
        result: bool = check_is_yaml(test_file_path)
        self.assertFalse(result)
        mock_file_exists.assert_called_once_with(file_path=test_file_path)


    @patch('app.common.file_check.file_exists')
    @patch('builtins.open', new_callable=mock_open, read_data="{invalid: yaml:")
    @patch('yaml.safe_load')
    def test_check_is_yaml_invalid_format(self, mock_yaml_load, mock_file, mock_file_exists) -> None:
        """
        Test the `check_is_yaml` function with an invalid YAML file format.

        This test verifies that the `check_is_yaml` function correctly identifies an invalid YAML file
        and returns `False`.

        Steps:
        1. Mock the `file_exists` function to return `True`, simulating that the file exists.
        2. Mock the `open` function to simulate reading a file with invalid YAML content.
        3. Mock the `yaml.safe_load` function to raise a `yaml.YAMLError` when attempting to parse the invalid content.
        4. Call the `check_is_yaml` function with the test file path.
        5. Assert that the function returns `False`.
        6. Verify that the `file_exists` function is called once with the correct file path.

        Args:
            mock_yaml_load (Mock): Mock object for the `yaml.safe_load` function.
            mock_file (Mock): Mock object for the `open` function.
            mock_file_exists (Mock): Mock object for the `file_exists` function.

        Raises:
            AssertionError: If the function does not return the expected result or the mocks are not called as expected.
        """
        mock_file_exists.return_value = True
        mock_yaml_load.side_effect = yaml.YAMLError("Invalid YAML")
        test_file_path: str = "/path/to/invalid.yaml"
        result: bool = check_is_yaml(test_file_path)
        self.assertFalse(result)
        mock_file_exists.assert_called_once_with(file_path=test_file_path)
