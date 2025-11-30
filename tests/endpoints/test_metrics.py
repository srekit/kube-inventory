import unittest

from prometheus_client import CollectorRegistry, CONTENT_TYPE_LATEST
from unittest.mock import patch, MagicMock

from app.endpoints.metrics import metrics_endpoint


class TestMetricsEndpoint(unittest.TestCase):
    @patch("app.endpoints.metrics.generate_latest")
    @patch("app.endpoints.metrics.get_registry")
    def test_metrics_endpoint_success(
        self, mock_get_registry: MagicMock, mock_generate_latest: MagicMock
    ) -> None:
        """
        Test that metrics_endpoint returns correct data, status code, and headers.

        This test verifies that the metrics endpoint correctly retrieves the registry,
        generates the latest metrics data, and returns the expected response format
        with proper content type headers.

        Args:
            mock_get_registry (MagicMock): Mock for the get_registry function.
            mock_generate_latest (MagicMock): Mock for the generate_latest function.
        """
        mock_registry: MagicMock = MagicMock(spec=CollectorRegistry)
        mock_get_registry.return_value = mock_registry
        mock_metrics_data: bytes = (
            b"# HELP test_metric A test metric\ntest_metric 1.0\n"
        )
        mock_generate_latest.return_value = mock_metrics_data

        data, status_code, headers = metrics_endpoint()

        self.assertEqual(data, mock_metrics_data)
        self.assertEqual(status_code, 200)
        self.assertEqual(headers, {"Content-Type": CONTENT_TYPE_LATEST})

        mock_get_registry.assert_called_once()
        mock_generate_latest.assert_called_once_with(mock_registry)

    @patch("app.endpoints.metrics.generate_latest")
    @patch("app.endpoints.metrics.get_registry")
    def test_metrics_endpoint_empty_data(
        self, mock_get_registry: MagicMock, mock_generate_latest: MagicMock
    ) -> None:
        """
        Test metrics_endpoint with empty metrics data.

        This test verifies that the endpoint handles the case where no metrics
        are available and returns empty data with the correct status and headers.

        Args:
            mock_get_registry (MagicMock): Mock for the get_registry function.
            mock_generate_latest (MagicMock): Mock for the generate_latest function.
        """
        mock_registry: MagicMock = MagicMock(spec=CollectorRegistry)
        mock_get_registry.return_value = mock_registry
        mock_generate_latest.return_value = b""

        data, status_code, headers = metrics_endpoint()

        self.assertEqual(data, b"")
        self.assertEqual(status_code, 200)
        self.assertEqual(headers, {"Content-Type": CONTENT_TYPE_LATEST})

        mock_get_registry.assert_called_once()
        mock_generate_latest.assert_called_once_with(mock_registry)


if __name__ == "__main__":
    unittest.main()
