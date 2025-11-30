import unittest

from unittest.mock import patch, MagicMock, call

from app.monitoring.metrics import clear_metrics, register_metrics, update_metric, METRICS


class TestMetrics(unittest.TestCase):
    def setUp(self) -> None:
        """
        Set up the test environment before each test method.

        This method clears the `METRICS` dictionary to ensure that each test
        starts with a clean state, avoiding interference from previous tests.
        """
        METRICS.clear()


    def tearDown(self) -> None:
        """
        Clean up the test environment after each test method.

        This method clears the `METRICS` dictionary to ensure that no state
        persists between tests, maintaining test isolation.
        """
        METRICS.clear()


    @patch('app.monitoring.metrics.init_storage')
    def test_clear_metrics(self, mock_init_storage) -> None:
        """
        Test the `clear_metrics` function.

        This test verifies that the `clear_metrics` function correctly calls the
        `init_storage` method with the `clean=True` argument to reset the metrics storage.

        Args:
            mock_init_storage (MagicMock): Mocked `init_storage` function to verify its behavior.
        """
        clear_metrics()
        mock_init_storage.assert_called_once_with(clean=True)


    @patch('app.monitoring.metrics.logging')
    @patch('app.monitoring.metrics.Gauge')
    def test_register_metrics_first_time(self, mock_gauge, mock_logging) -> None:
        """
        Test the `register_metrics` function when metrics are registered for the first time.

        This test verifies that:
        - The `Gauge` class is called twice to create two metrics.
        - The `METRICS` dictionary is populated with the expected metrics.
        - The `logging.info` method is called once to log the registration.

        Args:
            mock_gauge (MagicMock): Mocked `Gauge` class to verify its behavior.
            mock_logging (MagicMock): Mocked `logging` module to verify logging behavior.
        """
        mock_gauge_instance: MagicMock = MagicMock()
        mock_gauge.return_value = mock_gauge_instance

        with patch('app.monitoring.metrics._metrics_registered', False):
            register_metrics()

        self.assertEqual(mock_gauge.call_count, 2)

        self.assertEqual(len(METRICS), 2)
        self.assertIn("kube_inventory_pods_total", METRICS)
        self.assertIn("kube_inventory_pod_versions_to_latest_release", METRICS)

        mock_logging.info.assert_called_once()


    @patch('app.monitoring.metrics.logging')
    def test_register_metrics_already_registered(self, mock_logging) -> None:
        """
        Test the `register_metrics` function when metrics are already registered.

        This test verifies that:
        - The `register_metrics` function does not attempt to register metrics again
          if `_metrics_registered` is set to `True`.
        - A debug log message is generated indicating that registration is skipped.
        - The `METRICS` dictionary remains empty, as no new metrics are added.

        Args:
            mock_logging (MagicMock): Mocked `logging` module to verify logging behavior.
        """
        with patch('app.monitoring.metrics._metrics_registered', True):
            register_metrics()

        mock_logging.debug.assert_called_once_with("Metrics already registered, skipping registration")
        self.assertEqual(len(METRICS), 0)  # No metrics should be added


    @patch('app.monitoring.metrics.logging')
    def test_update_metric_not_found(self, mock_logging) -> None:
        """
        Test the `update_metric` function when the specified metric is not found.

        This test verifies that:
        - A warning log message is generated when attempting to update a non-existent metric.

        Args:
            mock_logging (MagicMock): Mocked `logging` module to verify logging behavior.
        """
        update_metric("nonexistent_metric", 42.0)
        mock_logging.warning.assert_called_once_with("Metric 'nonexistent_metric' not found in registry")


    @patch('app.monitoring.metrics.logging')
    def test_update_metric_without_labels(self, mock_logging) -> None:
        """
        Test the `update_metric` function when updating a metric without labels.

        This test verifies that:
        - The `set` method of the metric is called with the correct value.
        - Debug log messages are generated to indicate the update process.

        Args:
            mock_logging (MagicMock): Mocked `logging` module to verify logging behavior.
        """
        mock_metric: MagicMock = MagicMock()
        METRICS["test_metric"] = mock_metric

        update_metric("test_metric", 10.5)

        mock_metric.set.assert_called_once_with(10.5)
        mock_logging.debug.assert_has_calls([
            call("Attempting to update metric 'test_metric' with value 10.5"),
            call("Gauge '%s' set to %s", "test_metric", 10.5)
        ])


    @patch('app.monitoring.metrics.logging')
    def test_update_metric_with_labels(self, mock_logging) -> None:
        """
        Test the `update_metric` function when updating a metric with labels.

        This test verifies that:
        - The `labels` method of the metric is called with the correct label arguments.
        - The `set` method of the labeled metric is called with the correct value.
        - Debug log messages are generated to indicate the update process.

        Args:
            mock_logging (MagicMock): Mocked `logging` module to verify logging behavior.
        """
        mock_metric: MagicMock = MagicMock()
        mock_labels: MagicMock = MagicMock()
        mock_metric.labels.return_value = mock_labels
        METRICS["test_metric"] = mock_metric

        labels: dict = {"namespace": "default", "pod": "test-pod"}
        update_metric("test_metric", 5.0, labels)

        mock_metric.labels.assert_called_once_with(**labels)
        mock_labels.set.assert_called_once_with(5.0)
        mock_logging.debug.assert_has_calls([
            call("Attempting to update metric 'test_metric' with value 5.0"),
            call("Gauge '%s' set to %s with labels %s", "test_metric", 5.0, labels)
        ])


    @patch('app.monitoring.metrics.logging')
    def test_update_metric_unsupported_type(self, mock_logging) -> None:
        """
        Test the `update_metric` function when the metric type is unsupported.

        This test verifies that:
        - An error log message is generated when attempting to update a metric
          that does not support the `set` method.

        Args:
            mock_logging (MagicMock): Mocked `logging` module to verify logging behavior.
        """
        mock_metric: MagicMock = MagicMock(spec=[])  # Mock without 'set' attribute
        METRICS["invalid_metric"] = mock_metric

        update_metric("invalid_metric", 1.0)

        mock_logging.error.assert_called_once_with("Metric '%s' is not a Gauge or unsupported type", "invalid_metric")


if __name__ == '__main__':
    unittest.main()
