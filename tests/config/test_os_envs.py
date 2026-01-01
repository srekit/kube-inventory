import unittest
from unittest.mock import patch
import os
from app.config.os_envs import load_envs


class TestLoadEnvs(unittest.TestCase):
    @patch.dict(os.environ, {}, clear=True)
    def test_load_envs_no_environment_variables_set(self) -> None:
        """
        Test load_envs when no environment variables are set.

        Verifies that the function returns default values when neither
        GITHUB_ACCESS_TOKEN nor LOG_LEVEL environment variables are set.
        """
        result: dict = load_envs()

        expected = {
            "GITHUB": {
                "access_token": "",
            },
            "LOG": {
                "log_level": "INFO",
            },
        }

        self.assertEqual(result, expected)

    @patch.dict(
        os.environ,
        {"GITHUB_ACCESS_TOKEN": "test_token_123", "LOG_LEVEL": "DEBUG"},
    )
    def test_load_envs_all_environment_variables_set(self) -> None:
        """
        Test load_envs when all environment variables are set.

        Verifies that the function returns the actual environment variable values
        when both GITHUB_ACCESS_TOKEN and LOG_LEVEL are set.
        """
        result: dict = load_envs()

        expected = {
            "GITHUB": {
                "access_token": "test_token_123",
            },
            "LOG": {
                "log_level": "DEBUG",
            },
        }

        self.assertEqual(result, expected)

    @patch.dict(
        os.environ, {"GITHUB_ACCESS_TOKEN": "my_github_token"}, clear=True
    )
    def test_load_envs_only_github_token_set(self) -> None:
        """
        Test load_envs when only GITHUB_ACCESS_TOKEN is set.

        Verifies that the function returns the GitHub token from environment
        and uses the default value for LOG_LEVEL.
        """
        result: dict = load_envs()

        expected = {
            "GITHUB": {
                "access_token": "my_github_token",
            },
            "LOG": {
                "log_level": "INFO",
            },
        }

        self.assertEqual(result, expected)

    @patch.dict(os.environ, {"LOG_LEVEL": "ERROR"}, clear=True)
    def test_load_envs_only_log_level_set(self) -> None:
        """
        Test load_envs when only LOG_LEVEL is set.

        Verifies that the function returns the log level from environment
        and uses the default value for GITHUB_ACCESS_TOKEN.
        """
        result: dict = load_envs()

        expected: dict = {
            "GITHUB": {
                "access_token": "",
            },
            "LOG": {
                "log_level": "ERROR",
            },
        }

        self.assertEqual(result, expected)

    @patch.dict(os.environ, {"GITHUB_ACCESS_TOKEN": "", "LOG_LEVEL": ""})
    def test_load_envs_empty_environment_variables(self) -> None:
        """
        Test load_envs when environment variables are set to empty strings.

        Verifies that the function returns empty strings when environment
        variables are explicitly set to empty values.
        """
        result: dict = load_envs()

        expected: dict = {
            "GITHUB": {
                "access_token": "",
            },
            "LOG": {
                "log_level": "",
            },
        }

        self.assertEqual(result, expected)

    def test_load_envs_return_type_is_dict(self) -> None:
        """
        Test that load_envs returns a dictionary.

        Verifies that the function returns the correct data type.
        """
        result: dict = load_envs()
        self.assertIsInstance(result, dict)

    def test_load_envs_has_required_keys(self) -> None:
        """
        Test that load_envs returns a dictionary with required keys.

        Verifies that the returned dictionary contains the expected
        top-level keys and nested keys.
        """
        result: dict = load_envs()

        self.assertIn("GITHUB", result)
        self.assertIn("LOG", result)

        self.assertIn("access_token", result["GITHUB"])
        self.assertIn("log_level", result["LOG"])


if __name__ == "__main__":
    unittest.main()
