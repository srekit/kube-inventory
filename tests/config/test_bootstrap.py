import argparse
import unittest
from unittest.mock import patch, MagicMock

from app.config.bootstrap import load_config, prereqs_check


class TestBootstrap(unittest.TestCase):
    @patch('app.config.bootstrap.log_settings.setup_logging')
    @patch('app.config.bootstrap.args.load_args')
    @patch('app.config.bootstrap.os_envs.load_envs')
    def test_load_config_success(self, mock_load_envs, mock_load_args, mock_setup_logging) -> None:
        """
        Test the `load_config` function with successful execution.

        This test verifies that the `load_config` function correctly loads environment variables,
        parses command-line arguments, and sets up logging.

        The test ensures that:
        - Environment variables are loaded using `os_envs.load_envs`.
        - Command-line arguments are parsed using `args.load_args` with the correct environment values.
        - Logging is configured using the log level from the parsed arguments.

        Args:
            self: The instance of the test case.
            mock_load_envs: Mocked `os_envs.load_envs` function.
            mock_load_args: Mocked `args.load_args` function.
            mock_setup_logging: Mocked `log_settings.setup_logging` function.

        Returns:
            None
        """
        mock_envs: dict = {
            "GITHUB": {"access_token": "test_token"},
            "LOG": {"log_level": "DEBUG"}
        }
        mock_args: argparse.Namespace = argparse.Namespace(
            github_access_token="test_token",
            log_level="DEBUG",
            web_port=8080
        )
        mock_load_envs.return_value = mock_envs
        mock_load_args.return_value = mock_args

        result = load_config()

        mock_load_envs.assert_called_once()
        mock_load_args.assert_called_once_with(
            env_github_access_token="test_token",
            env_log_level="DEBUG"
        )
        mock_setup_logging.assert_called_once_with(log_level_str="DEBUG")
        self.assertEqual(result, mock_args)


    @patch('app.config.bootstrap.file_check.file_exists')
    def test_prereqs_check_file_exists(self, mock_file_exists) -> None:
        """
        Test the `prereqs_check` function when the file exists.

        This test verifies that the `prereqs_check` function behaves correctly when the
        specified file exists. It ensures that the function does not log errors or exit
        the program in this scenario.

        Args:
            self: The instance of the test case.
            mock_file_exists: Mocked `file_check.file_exists` function.

        Returns:
            None
        """
        mock_file_exists.return_value = True
        file_path: str = "/path/to/apps.json"

        prereqs_check(file_path)

        mock_file_exists.assert_called_once_with(file_path=file_path)
        self.assertIsNone(prereqs_check(file_path))


    @patch('app.config.bootstrap.sys.exit')
    @patch('app.config.bootstrap.logging.error')
    @patch('app.config.bootstrap.file_check.file_exists')
    def test_prereqs_check_file_not_exists(self, mock_file_exists, mock_logging_error, mock_sys_exit) -> None:
        """
        Test the `prereqs_check` function when the file does not exist.

        This test verifies that the `prereqs_check` function behaves correctly when the
        specified file does not exist. It ensures that the function logs an error message
        and exits the program with a status code of 1.

        Args:
            self: The instance of the test case.
            mock_file_exists: Mocked `file_check.file_exists` function.
            mock_logging_error: Mocked `logging.error` function.
            mock_sys_exit: Mocked `sys.exit` function.

        Returns:
            None
        """
        mock_file_exists.return_value = False
        file_path: str = "/path/to/missing_apps.json"

        prereqs_check(file_path)

        mock_file_exists.assert_called_once_with(file_path=file_path)
        mock_logging_error.assert_called_once_with(
            f"Finished with error: Default apps file not found at {file_path}"
        )
        mock_sys_exit.assert_called_once_with(1)


if __name__ == '__main__':
    unittest.main()
