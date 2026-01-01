import os
import tempfile
import unittest
import yaml

from unittest.mock import patch, MagicMock

from app.common.config_files import load_app_configs


class TestLoadAppConfigs(unittest.TestCase):
    def setUp(self) -> None:
        """
        Set up the test environment by creating a temporary directory and initializing default and extra configurations.

        This method is called before each test to ensure a clean state. It creates a temporary directory for storing
        configuration files and defines two dictionaries:
        - `default_config`: Represents the default application configurations.
        - `extra_config`: Represents additional or overriding application configurations.
        """
        self.temp_dir: str = tempfile.mkdtemp()
        self.default_config: dict = {
            "apps": {
                "app1": {"repo": "user/app1", "version": "1.0.0"},
                "app2": {"repo": "user/app2", "version": "2.0.0"},
            }
        }
        self.extra_config: dict = {
            "apps": {
                "app3": {"repo": "user/app3", "version": "3.0.0"},
                "app1": {"repo": "user/app1-updated", "version": "1.1.0"},
            }
        }

    def tearDown(self) -> None:
        """
        Clean up the test environment by removing temporary files and directories.

        This method is called after each test to ensure no residual files or directories
        are left behind. It iterates through all files in the temporary directory,
        removes them, and then deletes the directory itself.
        """
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    def test_load_default_config_only(self) -> None:
        """
        Test loading the default configuration file only.

        This test verifies that the `load_app_configs` function correctly loads and returns
        the default configuration when only the default configuration file is provided.

        Steps:
        1. Create a temporary default configuration file and write the `default_config` to it.
        2. Call the `load_app_configs` function with the path to the default configuration file.
        3. Assert that the returned configuration matches the `default_config`.
        4. Verify that the expected keys ('app1' and 'app2') are present in the 'apps' section.

        Raises:
            AssertionError: If the returned configuration does not match the expected values.
        """
        default_file: str = os.path.join(self.temp_dir, "default.yaml")
        with open(default_file, "w") as f:
            yaml.dump(self.default_config, f)

        result: dict = load_app_configs(default_file)

        self.assertEqual(result, self.default_config)
        self.assertIn("app1", result["apps"])
        self.assertIn("app2", result["apps"])

    def test_load_with_extra_config(self) -> None:
        """
        Test loading the default and extra configuration files.

        This test verifies that the `load_app_configs` function correctly merges the default
        configuration with an extra configuration file. It ensures that:
        - Keys from the extra configuration override those in the default configuration.
        - All keys from both configurations are present in the final result.

        Steps:
        1. Create temporary default and extra configuration files.
        2. Write `default_config` to the default file and `extra_config` to the extra file.
        3. Call the `load_app_configs` function with both file paths.
        4. Assert that the merged result contains the expected keys and values.

        Raises:
            AssertionError: If the merged configuration does not match the expected values.
        """
        default_file: str = os.path.join(self.temp_dir, "default.yaml")
        extra_file: str = os.path.join(self.temp_dir, "extra.yaml")

        with open(default_file, "w") as f:
            yaml.dump(self.default_config, f)
        with open(extra_file, "w") as f:
            yaml.dump(self.extra_config, f)

        result: dict = load_app_configs(default_file, extra_file)

        self.assertIn("app1", result["apps"])
        self.assertIn("app2", result["apps"])
        self.assertIn("app3", result["apps"])

        self.assertEqual(result["apps"]["app1"]["repo"], "user/app1-updated")
        self.assertEqual(result["apps"]["app1"]["version"], "1.1.0")

    def test_default_config_file_not_found(self) -> None:
        """
        Test behavior when the default configuration file is not found.

        This test verifies that the `load_app_configs` function logs an error message
        and exits the program with a `SystemExit` exception when the specified default
        configuration file does not exist.

        Steps:
        1. Mock the `sys.exit` function to raise a `SystemExit` exception.
        2. Mock the `logging.error` function to capture the error message.
        3. Call the `load_app_configs` function with a nonexistent file path.
        4. Assert that the `logging.error` function is called with the correct message.
        5. Assert that the program exits with a `SystemExit` exception.

        Raises:
            SystemExit: If the program exits due to the missing configuration file.
        """
        with patch("sys.exit") as mock_exit:
            with patch("logging.error") as mock_log:
                mock_exit.side_effect = SystemExit(1)

                with self.assertRaises(SystemExit):
                    load_app_configs("/nonexistent/file.yaml")

                mock_log.assert_called_once_with(
                    "Default apps configuration file not found: /nonexistent/file.yaml"
                )
                mock_exit.assert_called_once_with(1)

    def test_extra_config_file_not_found(self) -> None:
        """
        Test behavior when the extra configuration file is not found.

        This test verifies that the `load_app_configs` function correctly handles the case
        where the extra configuration file does not exist. It ensures that:
        - The default configuration is returned unchanged.
        - A warning is logged to indicate the missing extra configuration file.

        Steps:
        1. Create a temporary default configuration file and write the `default_config` to it.
        2. Call the `load_app_configs` function with the path to the default configuration file
           and a nonexistent extra configuration file path.
        3. Assert that the returned configuration matches the `default_config`.
        4. Verify that a warning is logged about the missing extra configuration file.

        Raises:
            AssertionError: If the returned configuration does not match the expected values.
        """
        default_file: str = os.path.join(self.temp_dir, "default.yaml")
        with open(default_file, "w") as f:
            yaml.dump(self.default_config, f)

        with patch("logging.warning") as mock_log:
            result: dict = load_app_configs(
                default_file, "/nonexistent/extra.yaml"
            )

            self.assertEqual(result, self.default_config)
            mock_log.assert_called_once()

    def test_extra_config_empty(self) -> None:
        """
        Test behavior when the extra configuration file is empty.

        This test verifies that the `load_app_configs` function correctly handles the case
        where the extra configuration file exists but is empty. It ensures that:
        - The default configuration is returned unchanged.

        Steps:
        1. Create temporary default and extra configuration files.
        2. Write `default_config` to the default file and leave the extra file empty.
        3. Call the `load_app_configs` function with both file paths.
        4. Assert that the returned configuration matches the `default_config`.

        Raises:
            AssertionError: If the returned configuration does not match the expected values.
        """
        default_file: str = os.path.join(self.temp_dir, "default.yaml")
        extra_file: str = os.path.join(self.temp_dir, "extra.yaml")

        with open(default_file, "w") as f:
            yaml.dump(self.default_config, f)
        with open(extra_file, "w") as f:
            f.write("")  # Empty file

        result: dict = load_app_configs(default_file, extra_file)

        self.assertEqual(result, self.default_config)

    def test_extra_config_no_apps_key(self) -> None:
        """
        Test behavior when the extra configuration file does not contain the 'apps' key.

        This test verifies that the `load_app_configs` function correctly handles the case
        where the extra configuration file is missing the 'apps' key. It ensures that:
        - The default configuration is returned unchanged.

        Steps:
        1. Create temporary default and extra configuration files.
        2. Write `default_config` to the default file.
        3. Write a dictionary without the 'apps' key to the extra file.
        4. Call the `load_app_configs` function with both file paths.
        5. Assert that the returned configuration matches the `default_config`.

        Raises:
            AssertionError: If the returned configuration does not match the expected values.
        """
        default_file: str = os.path.join(self.temp_dir, "default.yaml")
        extra_file: str = os.path.join(self.temp_dir, "extra.yaml")

        with open(default_file, "w") as f:
            yaml.dump(self.default_config, f)
        with open(extra_file, "w") as f:
            yaml.dump({"other_key": "value"}, f)

        result: dict = load_app_configs(default_file, extra_file)

        self.assertEqual(result, self.default_config)

    @patch("logging.debug")
    def test_logging_calls(self, mock_debug: MagicMock) -> None:
        """
        Test the number of debug logging calls during configuration loading.

        This test verifies that the `load_app_configs` function generates the expected
        number of debug logging calls when loading both default and extra configuration files.

        Steps:
        1. Create temporary default and extra configuration files.
        2. Write `default_config` to the default file and `extra_config` to the extra file.
        3. Call the `load_app_configs` function with both file paths.
        4. Assert that the `logging.debug` function is called exactly three times.

        Args:
            mock_debug (Mock): Mock object for the `logging.debug` function.

        Raises:
            AssertionError: If the number of debug logging calls does not match the expected value.
        """
        default_file: str = os.path.join(self.temp_dir, "default.yaml")
        extra_file: str = os.path.join(self.temp_dir, "extra.yaml")

        with open(default_file, "w") as f:
            yaml.dump(self.default_config, f)
        with open(extra_file, "w") as f:
            yaml.dump(self.extra_config, f)

        load_app_configs(default_file, extra_file)

        self.assertEqual(mock_debug.call_count, 3)


if __name__ == "__main__":
    unittest.main()
