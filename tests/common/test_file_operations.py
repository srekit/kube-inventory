import unittest

from unittest.mock import patch, mock_open, MagicMock

from app.common.file_operations import content_to_file


class TestContentToFile(unittest.TestCase):
    @patch("app.common.file_operations.Path")
    @patch("builtins.open", new_callable=mock_open)
    @patch("app.common.file_operations.logging")
    def test_write_string_content(
        self,
        mock_logging: MagicMock,
        mock_file_open: MagicMock,
        mock_path: MagicMock,
    ) -> None:
        """
        Test the `content_to_file` function with string content.

        This test verifies that the `content_to_file` function correctly writes string content
        to a file and ensures that the parent directories are created if they do not exist.

        Steps:
        1. Mock the `Path` object to simulate file path operations.
        2. Mock the `open` function to simulate writing to a file.
        3. Mock the `logging` module to verify logging behavior.
        4. Call the `content_to_file` function with a test file path and string content.
        5. Assert that the parent directory is created, the file is opened in write mode,
           the content is written to the file, and logging is performed.

        Args:
            mock_logging (Mock): Mock object for the `logging` module.
            mock_file_open (Mock): Mock object for the `open` function.
            mock_path (Mock): Mock object for the `Path` class.

        Raises:
            AssertionError: If the function does not perform the expected operations or
            the mocks are not called as expected.
        """
        file_path: str = "/tmp/test.txt"
        content: str = "Hello, world!"
        mock_path.return_value.parent.mkdir = MagicMock()

        content_to_file(file_path, content)

        mock_path.assert_called_with(file_path)
        mock_path.return_value.parent.mkdir.assert_called_once_with(
            parents=True, exist_ok=True
        )
        mock_file_open.assert_called_once_with(file_path, "w")
        mock_file_open().write.assert_called_once_with(content)
        mock_logging.info.assert_called_once()

    @patch("app.common.file_operations.Path")
    @patch("builtins.open", new_callable=mock_open)
    @patch("app.common.file_operations.logging")
    def test_write_json_content(
        self,
        mock_logging: MagicMock,
        mock_file_open: MagicMock,
        mock_path: MagicMock,
    ) -> None:
        """
        Test the `content_to_file` function with JSON content.

        This test verifies that the `content_to_file` function correctly writes JSON content
        to a file and ensures that the parent directories are created if they do not exist.

        Steps:
        1. Mock the `Path` object to simulate file path operations.
        2. Mock the `open` function to simulate writing to a file.
        3. Mock the `logging` module to verify logging behavior.
        4. Call the `content_to_file` function with a test file path and JSON content.
        5. Assert that the parent directory is created, the file is opened in write mode,
           the content is written to the file, and logging is performed.

        Args:
            mock_logging (Mock): Mock object for the `logging` module.
            mock_file_open (Mock): Mock object for the `open` function.
            mock_path (Mock): Mock object for the `Path` class.

        Raises:
            AssertionError: If the function does not perform the expected operations or
            the mocks are not called as expected.
        """
        file_path: str = "/tmp/test.json"
        content: dict = {"key": "value"}
        mock_path.return_value.parent.mkdir = MagicMock()

        content_to_file(file_path, content)

        mock_path.assert_called_with(file_path)
        mock_path.return_value.parent.mkdir.assert_called_once_with(
            parents=True, exist_ok=True
        )
        mock_file_open.assert_called_once_with(file_path, "w")
        self.assertTrue(mock_file_open().write.called)
        mock_logging.info.assert_called_once()
