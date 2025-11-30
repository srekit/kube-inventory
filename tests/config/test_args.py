import unittest
from argparse import ArgumentParser, Namespace

from unittest.mock import patch

from app.config.args import (
    load_args,
    general_parsers_common,
    general_parsers_config,
    general_parsers_github,
    general_parsers_kubernetes,
    general_parsers_output,
    general_parsers_web,
)


class TestArgsParsers(unittest.TestCase):
    def test_general_parsers_common(self) -> None:
        """
        Test the `general_parsers_common` function.

        This test verifies that the `general_parsers_common` function correctly parses
        the `--log-level` argument when a default value is provided.

        The test ensures that:
        - The `log_level` argument is set to the default value ("INFO") when no
          command-line arguments are provided.

        Args:
            self: The instance of the test case.

        Returns:
            None
        """
        parser: ArgumentParser = general_parsers_common(env_log_level="INFO")
        args: Namespace = parser.parse_args([])
        self.assertEqual(args.log_level, "INFO")


    def test_general_parsers_config(self) -> None:
        """
        Test the `general_parsers_config` function.

        This test verifies that the `general_parsers_config` function correctly parses
        the default and extra application file paths.

        The test ensures that:
        - The `default_apps_file_path` argument is set to "config/default_apps.yaml".
        - The `extra_apps_file_path` argument is set to "config/extra_apps.yaml".

        Args:
            self: The instance of the test case.

        Returns:
            None
        """
        parser: ArgumentParser = general_parsers_config()
        args: Namespace = parser.parse_args([])
        self.assertEqual(args.default_apps_file_path, "config/default_apps.yaml")
        self.assertEqual(args.extra_apps_file_path, "config/extra_apps.yaml")


    def test_general_parsers_github_with_token(self) -> None:
        """
        Test the `general_parsers_github` function with a provided GitHub access token.

        This test verifies that the `general_parsers_github` function correctly parses
        the `--github-access-token` and `--github-api-url` arguments when a token is provided.

        The test ensures that:
        - The `github_access_token` argument is set to the provided value ("token123").
        - The `github_api_url` argument is set to the default value ("https://api.github.com").

        Args:
            self: The instance of the test case.

        Returns:
            None
        """
        parser: ArgumentParser = general_parsers_github(env_github_access_token="token123")
        args: Namespace = parser.parse_args([])
        self.assertEqual(args.github_access_token, "token123")
        self.assertEqual(args.github_api_url, "https://api.github.com")


    def test_general_parsers_github_without_token(self) -> None:
        """
        Test the `general_parsers_github` function without a provided GitHub access token.

        This test verifies that the `general_parsers_github` function raises a `SystemExit`
        exception when no GitHub access token is provided.

        The test ensures that:
        - The parser exits with an error when the `env_github_access_token` is an empty string.

        Args:
            self: The instance of the test case.

        Returns:
            None
        """
        parser: ArgumentParser = general_parsers_github(env_github_access_token="")
        with self.assertRaises(SystemExit):
            parser.parse_args([])


    def test_general_parsers_kubernetes(self) -> None:
        """
        Test the `general_parsers_kubernetes` function.

        This test verifies that the `general_parsers_kubernetes` function correctly parses
        the `--kube-config-path` argument.

        The test ensures that:
        - The `kube_config_path` argument is `None` when no command-line arguments are provided.

        Args:
            self: The instance of the test case.

        Returns:
            None
        """
        parser: ArgumentParser = general_parsers_kubernetes()
        args: Namespace = parser.parse_args([])
        self.assertIsNone(args.kube_config_path)


    def test_general_parsers_output(self) -> None:
        """
        Test the `general_parsers_output` function.

        This test verifies that the `general_parsers_output` function correctly parses
        the output-related arguments.

        The test ensures that:
        - The `output_dir` argument is set to the default value ("inv_data").
        - The `output_mode` argument is set to the default value ("json").
        - The `output_refresh_interval_seconds` argument is set to the default value (600).

        Args:
            self: The instance of the test case.

        Returns:
            None
        """
        parser: ArgumentParser = general_parsers_output()
        args: Namespace = parser.parse_args([])
        self.assertEqual(args.output_dir, "inv_data")
        self.assertEqual(args.output_mode, "json")
        self.assertEqual(args.output_refresh_interval_seconds, 600)


    def test_general_parsers_web(self) -> None:
        """
        Test the `general_parsers_web` function.

        This test verifies that the `general_parsers_web` function correctly parses
        the web-related arguments.

        The test ensures that:
        - The `web_host` argument is set to the default value ("0.0.0.0").
        - The `web_port` argument is set to the default value (8080).

        Args:
            self: The instance of the test case.

        Returns:
            None
        """
        parser: ArgumentParser = general_parsers_web()
        args: Namespace = parser.parse_args([])
        self.assertEqual(args.web_host, "0.0.0.0")
        self.assertEqual(args.web_port, 8080)


    @patch("sys.argv", ["prog"])
    def test_load_args_defaults(self) -> None:
        """
        Test the `load_args` function with default arguments.

        This test verifies that the `load_args` function correctly loads the default
        values for the arguments when no command-line arguments are provided.

        The test ensures that:
        - The `github_access_token` argument is set to the provided environment value ("token123").
        - The `log_level` argument is set to the provided environment value ("INFO").
        - The `web_port` argument is set to the default value (8080).

        Args:
            self: The instance of the test case.

        Returns:
            None
        """
        args: Namespace = load_args(env_github_access_token="token123", env_log_level="INFO")
        self.assertEqual(args.github_access_token, "token123")
        self.assertEqual(args.log_level, "INFO")
        self.assertEqual(args.web_port, 8080)


if __name__ == "__main__":
    unittest.main()
