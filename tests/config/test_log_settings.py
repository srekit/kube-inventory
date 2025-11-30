import logging
import sys
import unittest

from unittest.mock import patch, MagicMock

from app.config.log_settings import setup_logging


class TestLogSettings(unittest.TestCase):
    @patch('app.config.log_settings.logging.basicConfig')
    @patch('app.config.log_settings.logging.log')
    def test_setup_logging_valid_level(self, mock_logging_log, mock_basic_config) -> None:
        """
        Test the `setup_logging` function with a valid log level string.

        This test verifies that the `setup_logging` function correctly configures the logging
        settings when provided with a valid log level string. It ensures that the logging
        configuration is set up with the expected parameters and that an informational log
        message is generated.

        Args:
            self: The instance of the test case.
            mock_logging_log: Mocked `logging.log` function to verify log messages.
            mock_basic_config: Mocked `logging.basicConfig` function to verify logging configuration.

        Returns:
            None
        """
        log_level_str: str = "DEBUG"

        setup_logging(log_level_str)

        mock_basic_config.assert_called_once_with(
            stream=sys.stdout,
            level=logging.DEBUG,
            format='{"timestamp": "%(asctime)s.%(msecs)03dZ", "level": "%(levelname)s", "message": "%(message)s"}',
            datefmt='%Y-%m-%dT%H:%M:%S'
        )
        mock_logging_log.assert_called_once_with(logging.INFO, "Log level set to %s", "DEBUG")


    @patch('app.config.log_settings.logging.basicConfig')
    @patch('app.config.log_settings.logging.log')
    def test_setup_logging_info_level(self, mock_logging_log, mock_basic_config) -> None:
        """
        Test the `setup_logging` function with the INFO log level.

        This test verifies that the `setup_logging` function correctly configures the logging
        settings when the log level is set to INFO. It ensures that the logging configuration
        is applied with the expected parameters and that an informational log message is generated.

        Args:
            self: The instance of the test case.
            mock_logging_log: Mocked `logging.log` function to verify log messages.
            mock_basic_config: Mocked `logging.basicConfig` function to verify logging configuration.

        Returns:
            None
        """
        log_level_str: str = "INFO"

        setup_logging(log_level_str)

        mock_basic_config.assert_called_once_with(
            stream=sys.stdout,
            level=logging.INFO,
            format='{"timestamp": "%(asctime)s.%(msecs)03dZ", "level": "%(levelname)s", "message": "%(message)s"}',
            datefmt='%Y-%m-%dT%H:%M:%S'
        )
        mock_logging_log.assert_called_once_with(logging.INFO, "Log level set to %s", "INFO")


    @patch('app.config.log_settings.logging.basicConfig')
    @patch('app.config.log_settings.logging.log')
    def test_setup_logging_warning_level(self, mock_logging_log, mock_basic_config) -> None:
        """
        Test the `setup_logging` function with the WARNING log level.

        This test verifies that the `setup_logging` function correctly configures the logging
        settings when the log level is set to WARNING. It ensures that the logging configuration
        is applied with the expected parameters and that an informational log message is generated.

        Args:
            self: The instance of the test case.
            mock_logging_log: Mocked `logging.log` function to verify log messages.
            mock_basic_config: Mocked `logging.basicConfig` function to verify logging configuration.

        Returns:
            None
        """
        log_level_str: str = "WARNING"

        setup_logging(log_level_str)

        mock_basic_config.assert_called_once_with(
            stream=sys.stdout,
            level=logging.WARNING,
            format='{"timestamp": "%(asctime)s.%(msecs)03dZ", "level": "%(levelname)s", "message": "%(message)s"}',
            datefmt='%Y-%m-%dT%H:%M:%S'
        )
        mock_logging_log.assert_called_once_with(logging.INFO, "Log level set to %s", "WARNING")


    @patch('app.config.log_settings.logging.basicConfig')
    @patch('app.config.log_settings.logging.log')
    def test_setup_logging_invalid_level_defaults_to_info(self, mock_logging_log, mock_basic_config) -> None:
        """
        Test the `setup_logging` function with an invalid log level string.

        This test verifies that the `setup_logging` function defaults to the INFO log level
        when provided with an invalid log level string. It ensures that the logging configuration
        is applied with the default parameters and that an informational log message is generated.

        Args:
            self: The instance of the test case.
            mock_logging_log: Mocked `logging.log` function to verify log messages.
            mock_basic_config: Mocked `logging.basicConfig` function to verify logging configuration.

        Returns:
            None
        """
        log_level_str: str = "INVALID_LEVEL"

        setup_logging(log_level_str)

        mock_basic_config.assert_called_once_with(
            stream=sys.stdout,
            level=logging.INFO,
            format='{"timestamp": "%(asctime)s.%(msecs)03dZ", "level": "%(levelname)s", "message": "%(message)s"}',
            datefmt='%Y-%m-%dT%H:%M:%S'
        )
        mock_logging_log.assert_called_once_with(logging.INFO, "Log level set to %s", "INVALID_LEVEL")


    @patch('app.config.log_settings.logging.basicConfig')
    @patch('app.config.log_settings.logging.log')
    def test_setup_logging_empty_string_defaults_to_info(self, mock_logging_log, mock_basic_config) -> None:
        """
        Test the `setup_logging` function with an empty string as the log level.

        This test verifies that the `setup_logging` function defaults to the INFO log level
        when provided with an empty string. It ensures that the logging configuration is
        applied with the default parameters and that an informational log message is generated.

        Args:
            self: The instance of the test case.
            mock_logging_log: Mocked `logging.log` function to verify log messages.
            mock_basic_config: Mocked `logging.basicConfig` function to verify logging configuration.

        Returns:
            None
        """
        log_level_str: str = ""

        setup_logging(log_level_str)

        mock_basic_config.assert_called_once_with(
            stream=sys.stdout,
            level=logging.INFO,
            format='{"timestamp": "%(asctime)s.%(msecs)03dZ", "level": "%(levelname)s", "message": "%(message)s"}',
            datefmt='%Y-%m-%dT%H:%M:%S'
        )
        mock_logging_log.assert_called_once_with(logging.INFO, "Log level set to %s", "")


if __name__ == '__main__':
    unittest.main()
