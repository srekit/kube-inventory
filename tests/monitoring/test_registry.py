import unittest
from unittest.mock import patch, MagicMock

from prometheus_client import CollectorRegistry

from app.monitoring.registry import get_registry, init_storage, PROMETHEUS_MULTIPROC_DIR


class TestRegistry(unittest.TestCase):
    @patch('app.monitoring.registry.MultiProcessCollector')
    @patch('app.monitoring.registry.CollectorRegistry')
    def test_get_registry(self, mock_collector_registry, mock_multiprocess_collector) -> None:
        """
        Test that get_registry creates and returns a CollectorRegistry with MultiProcessCollector.

        Verifies that:
        - A CollectorRegistry instance is created
        - A MultiProcessCollector is initialized with the registry
        - The registry is returned
        """
        mock_registry: MagicMock = MagicMock()
        mock_collector_registry.return_value = mock_registry

        result: CollectorRegistry = get_registry()

        mock_collector_registry.assert_called_once()
        mock_multiprocess_collector.assert_called_once_with(mock_registry)
        self.assertEqual(result, mock_registry)


    @patch('app.monitoring.registry.os.makedirs')
    @patch('app.monitoring.registry.os.path.isdir')
    @patch('app.monitoring.registry.shutil.rmtree')
    @patch('app.monitoring.registry.logging')
    def test_init_storage_clean_true_directory_exists(self, mock_logging, mock_rmtree, mock_isdir, mock_makedirs) -> None:
        """
        Test init_storage with clean=True when directory exists.

        Verifies that:
        - The existing directory is removed
        - A debug log message is generated
        - The directory is recreated
        """
        mock_isdir.return_value = True

        init_storage(clean=True)

        mock_isdir.assert_called_once_with(PROMETHEUS_MULTIPROC_DIR)
        mock_logging.debug.assert_called_once_with("Cleaning PROMETHEUS_MULTIPROC_DIR: %s", PROMETHEUS_MULTIPROC_DIR)
        mock_rmtree.assert_called_once_with(PROMETHEUS_MULTIPROC_DIR, ignore_errors=True)
        mock_makedirs.assert_called_once_with(PROMETHEUS_MULTIPROC_DIR, exist_ok=True)


    @patch('app.monitoring.registry.os.makedirs')
    @patch('app.monitoring.registry.os.path.isdir')
    @patch('app.monitoring.registry.shutil.rmtree')
    @patch('app.monitoring.registry.logging')
    def test_init_storage_clean_true_directory_not_exists(self, mock_logging, mock_rmtree, mock_isdir, mock_makedirs) -> None:
        """
        Test init_storage with clean=True when directory does not exist.

        Verifies that:
        - No removal operation is performed
        - No debug log message is generated
        - The directory is created
        """
        mock_isdir.return_value = False

        init_storage(clean=True)

        mock_isdir.assert_called_once_with(PROMETHEUS_MULTIPROC_DIR)
        mock_logging.debug.assert_not_called()
        mock_rmtree.assert_not_called()
        mock_makedirs.assert_called_once_with(PROMETHEUS_MULTIPROC_DIR, exist_ok=True)


    @patch('app.monitoring.registry.os.makedirs')
    @patch('app.monitoring.registry.os.path.isdir')
    @patch('app.monitoring.registry.shutil.rmtree')
    @patch('app.monitoring.registry.logging')
    def test_init_storage_clean_false(self, mock_logging, mock_rmtree, mock_isdir, mock_makedirs) -> None:
        """
        Test init_storage with clean=False.

        Verifies that:
        - No directory existence check is performed
        - No removal operation is performed
        - The directory is created with exist_ok=True
        """
        init_storage(clean=False)

        mock_isdir.assert_not_called()
        mock_logging.debug.assert_not_called()
        mock_rmtree.assert_not_called()
        mock_makedirs.assert_called_once_with(PROMETHEUS_MULTIPROC_DIR, exist_ok=True)


    @patch('app.monitoring.registry.os.makedirs')
    @patch('app.monitoring.registry.os.path.isdir')
    @patch('app.monitoring.registry.shutil.rmtree')
    @patch('app.monitoring.registry.logging')
    def test_init_storage_default_clean(self, mock_logging, mock_rmtree, mock_isdir, mock_makedirs) -> None:
        """
        Test init_storage with default clean parameter (False).

        Verifies that the default behavior is equivalent to clean=False.
        """
        init_storage()

        mock_isdir.assert_not_called()
        mock_logging.debug.assert_not_called()
        mock_rmtree.assert_not_called()
        mock_makedirs.assert_called_once_with(PROMETHEUS_MULTIPROC_DIR, exist_ok=True)


if __name__ == '__main__':
    unittest.main()
