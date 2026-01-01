import argparse
import unittest
from unittest.mock import patch, MagicMock

from app.config.bootstrap import load_config


class TestBootstrap(unittest.TestCase):
    @patch("app.config.bootstrap.log_settings.setup_logging")
    @patch("app.config.bootstrap.args.load_args")
    @patch("app.config.bootstrap.os_envs.load_envs")
    def test_load_config_success(
        self,
        mock_load_envs: MagicMock,
        mock_load_args: MagicMock,
        mock_setup_logging: MagicMock,
    ) -> None:
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
            "LOG": {"log_level": "DEBUG"},
        }
        mock_args: argparse.Namespace = argparse.Namespace(
            github_access_token="test_token", log_level="DEBUG", web_port=8080
        )
        mock_load_envs.return_value = mock_envs
        mock_load_args.return_value = mock_args

        result = load_config()

        mock_load_envs.assert_called_once()
        mock_load_args.assert_called_once_with(
            env_github_access_token="test_token", env_log_level="DEBUG"
        )
        mock_setup_logging.assert_called_once_with(log_level_str="DEBUG")
        self.assertEqual(result, mock_args)


if __name__ == "__main__":
    unittest.main()
