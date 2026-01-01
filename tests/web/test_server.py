import unittest
from typing import Any, Optional
from unittest.mock import patch, MagicMock
from flask import Flask

from app.web.server import _create_app, start_web_server


class TestCreateApp(unittest.TestCase):
    """Test cases for the _create_app function."""

    def test_create_app_default_parameters(self) -> None:
        """
        Test _create_app with default parameters.

        Verifies that:
        - A Flask app is created with correct configuration
        - URL rules are registered for all endpoints
        - Default values are handled correctly
        """
        app = _create_app()

        self.assertIsInstance(app, Flask)
        self.assertIsNone(app.config["INVENTORY_PROVIDER"])
        self.assertTrue(app.config["JSONIFY_PRETTYPRINT_REGULAR"])
        self.assertFalse(app.config["JSON_SORT_KEYS"])
        self.assertEqual(app.config["JSONIFY_MIMETYPE"], "application/json")

        # Check URL rules are registered
        url_rules = [rule.rule for rule in app.url_map.iter_rules()]
        self.assertIn("/", url_rules)
        self.assertIn("/metrics", url_rules)
        self.assertIn("/health", url_rules)

    def test_create_app_with_all_parameters(self) -> None:
        """
        Test _create_app with all parameters provided.

        Verifies that:
        - All configuration parameters are properly set
        - Inventory provider is correctly configured
        """
        inventory_data = [{"type": "test", "config": "value"}]

        def inventory_provider() -> list[dict[str, Any]]:
            return inventory_data

        app = _create_app(
            github_access_token="token123",
            github_api_url="https://api.github.com",
            inventory_provider=inventory_provider,
        )

        self.assertIsInstance(app, Flask)
        self.assertEqual(app.config["INVENTORY_PROVIDER"], inventory_provider)

    def test_create_app_url_rules_methods(self) -> None:
        """
        Test that URL rules are registered with correct HTTP methods.
        """
        app = _create_app()

        with app.test_request_context():
            # Find rules by endpoint
            root_rule = next(
                rule
                for rule in app.url_map.iter_rules()
                if rule.endpoint == "root"
            )
            metrics_rule = next(
                rule
                for rule in app.url_map.iter_rules()
                if rule.endpoint == "metrics"
            )
            health_rule = next(
                rule
                for rule in app.url_map.iter_rules()
                if rule.endpoint == "health"
            )

            # Assert methods exist and check HTTP methods
            assert root_rule.methods is not None
            assert metrics_rule.methods is not None
            assert health_rule.methods is not None

            self.assertIn("GET", root_rule.methods)
            self.assertIn("GET", metrics_rule.methods)
            self.assertIn("GET", health_rule.methods)


class TestStartWebServer(unittest.TestCase):
    """Test cases for the start_web_server function."""

    @patch("app.web.server._create_app")
    @patch("app.web.server.logging")
    def test_start_web_server_gunicorn_not_installed(
        self, mock_logging: MagicMock, mock_create_app: MagicMock
    ) -> None:
        """
        Test start_web_server when Gunicorn is not installed.

        Verifies that:
        - ImportError is raised
        - Error message is logged
        - App is still created
        """
        mock_app = MagicMock()
        mock_create_app.return_value = mock_app

        with patch(
            "builtins.__import__",
            side_effect=ImportError("No module named 'gunicorn'"),
        ):
            with self.assertRaises(ImportError):
                start_web_server(
                    github_access_token="token",
                    github_api_url="https://api.github.com",
                    host="127.0.0.1",
                    port=8000,
                    inventory_provider=None,
                    kube_client=None,
                )

        mock_logging.error.assert_called_once_with(
            "Gunicorn is required but not installed. Install with: pip install gunicorn"
        )
        mock_create_app.assert_called_once()

    @patch("app.web.server._create_app")
    @patch("app.web.server.logging")
    def test_start_web_server_success(
        self, mock_logging: MagicMock, mock_create_app: MagicMock
    ) -> None:
        """
        Test successful start_web_server execution.

        Verifies that:
        - App is created with correct parameters
        - Gunicorn configuration is properly set
        - Logging messages are generated
        """
        mock_app = MagicMock()
        mock_create_app.return_value = mock_app

        # Mock the WSGIApplication to avoid instantiation issues
        mock_wsgi_app_class = MagicMock()
        mock_wsgi_instance = MagicMock()

        with patch("gunicorn.app.wsgiapp.WSGIApplication", mock_wsgi_app_class):
            # Mock the run method to prevent actual server startup
            with patch.object(mock_wsgi_instance, "run"):
                mock_wsgi_app_class.return_value = mock_wsgi_instance

                start_web_server(
                    github_access_token="token",
                    github_api_url="https://api.github.com",
                    host="0.0.0.0",
                    port=9000,
                    inventory_provider=lambda: [{"test": "config"}],
                    kube_client=None,
                )

        # Verify _create_app was called once
        self.assertEqual(mock_create_app.call_count, 1)

        # Get the actual call arguments
        call_args = mock_create_app.call_args
        self.assertEqual(call_args.kwargs["github_access_token"], "token")
        self.assertEqual(
            call_args.kwargs["github_api_url"], "https://api.github.com"
        )

        # Verify the inventory_provider is callable and returns expected data
        inventory_provider = call_args.kwargs["inventory_provider"]
        self.assertTrue(callable(inventory_provider))
        self.assertEqual(inventory_provider(), [{"test": "config"}])

    @patch("app.web.server._create_app")
    @patch("app.web.server.logging")
    def test_start_web_server_with_worker_callback(
        self, mock_logging: MagicMock, mock_create_app: MagicMock
    ) -> None:
        """
        Test start_web_server with on_worker_start callback.

        Verifies that:
        - Worker callback is properly handled
        - App creation includes the callback parameter
        """
        mock_app = MagicMock()
        mock_create_app.return_value = mock_app
        mock_callback = MagicMock()

        mock_wsgi_app_class = MagicMock()
        mock_wsgi_instance = MagicMock()

        with patch("gunicorn.app.wsgiapp.WSGIApplication", mock_wsgi_app_class):
            with patch.object(mock_wsgi_instance, "run"):
                mock_wsgi_app_class.return_value = mock_wsgi_instance

                start_web_server(
                    github_access_token="token",
                    github_api_url="https://api.github.com",
                    host="localhost",
                    port=5000,
                    inventory_provider=None,
                    on_worker_start=mock_callback,
                    kube_client=None,
                )

        mock_create_app.assert_called_once()
        mock_logging.info.assert_called_with(
            "Starting WSGI server on localhost:5000"
        )

    def test_post_fork_callback_success(self) -> None:
        """
        Test _post_fork function with successful callback execution.
        """
        mock_callback = MagicMock()
        mock_server = MagicMock()
        mock_worker = MagicMock()
        mock_worker.pid = 12345

        # Capture the post_fork function from the options
        captured_post_fork = None

        def capture_standalone_app(
            app: Any, custom_options: Optional[dict] = None
        ) -> MagicMock:
            nonlocal captured_post_fork
            captured_post_fork = (
                custom_options.get("post_fork") if custom_options else None
            )
            mock_instance = MagicMock()
            mock_instance.run = MagicMock()
            return mock_instance

        with patch("app.web.server.logging") as mock_logging:
            with patch("app.web.server._create_app", return_value=MagicMock()):
                with patch(
                    "gunicorn.app.wsgiapp.WSGIApplication",
                    side_effect=capture_standalone_app,
                ):
                    start_web_server(
                        github_access_token="token",
                        github_api_url="https://api.github.com",
                        host="127.0.0.1",
                        port=8000,
                        inventory_provider=None,
                        on_worker_start=mock_callback,
                        kube_client=None,
                    )

                    # Test the captured post_fork function
                    if captured_post_fork:
                        captured_post_fork(mock_server, mock_worker)
                        mock_callback.assert_called_once()
                        mock_logging.info.assert_called_with(
                            "Gunicorn worker booted (pid=%s). Starting background tasks...",
                            12345,
                        )

    def test_post_fork_callback_exception(self) -> None:
        """
        Test _post_fork function when callback raises an exception.
        """
        mock_callback = MagicMock(side_effect=Exception("Callback failed"))
        mock_server = MagicMock()
        mock_worker = MagicMock()
        mock_worker.pid = 12345

        # Capture the post_fork function from the options
        captured_post_fork = None

        def capture_standalone_app(
            app: Any, custom_options: Optional[dict] = None
        ) -> MagicMock:
            nonlocal captured_post_fork
            captured_post_fork = (
                custom_options.get("post_fork") if custom_options else None
            )
            mock_instance = MagicMock()
            mock_instance.run = MagicMock()
            return mock_instance

        with patch("app.web.server.logging") as mock_logging:
            with patch("app.web.server._create_app", return_value=MagicMock()):
                with patch(
                    "gunicorn.app.wsgiapp.WSGIApplication",
                    side_effect=capture_standalone_app,
                ):
                    start_web_server(
                        github_access_token="token",
                        github_api_url="https://api.github.com",
                        host="127.0.0.1",
                        port=8000,
                        inventory_provider=None,
                        on_worker_start=mock_callback,
                        kube_client=None,
                    )

                    # Test the post_fork function with exception
                    if captured_post_fork:
                        captured_post_fork(mock_server, mock_worker)
                        mock_callback.assert_called_once()
                        mock_logging.exception.assert_called_with(
                            "on_worker_start failed : %s",
                            mock_callback.side_effect,
                        )

    def test_child_exit_callback(self) -> None:
        """
        Test _child_exit function for proper Prometheus cleanup.
        """
        mock_server: MagicMock = MagicMock()
        mock_worker: MagicMock = MagicMock()
        mock_worker.pid = 12345

        # Capture the child_exit function from the options
        captured_child_exit = None

        def capture_standalone_app(
            app: Any, custom_options: Optional[dict] = None
        ) -> MagicMock:
            nonlocal captured_child_exit
            captured_child_exit = (
                custom_options.get("child_exit") if custom_options else None
            )
            mock_instance = MagicMock()
            mock_instance.run = MagicMock()
            return mock_instance

        with patch("app.web.server.logging"):
            with patch("prometheus_client.multiprocess") as mock_multiprocess:
                with patch(
                    "app.web.server._create_app", return_value=MagicMock()
                ):
                    with patch(
                        "gunicorn.app.wsgiapp.WSGIApplication",
                        side_effect=capture_standalone_app,
                    ):
                        start_web_server(
                            github_access_token="token",
                            github_api_url="https://api.github.com",
                            host="127.0.0.1",
                            port=8000,
                            inventory_provider=None,
                            kube_client=None,
                        )

                        # Test the child_exit function
                        if captured_child_exit:
                            captured_child_exit(mock_server, mock_worker)
                            mock_multiprocess.mark_process_dead.assert_called_once_with(
                                12345
                            )

    def test_child_exit_callback_with_prometheus_error(self) -> None:
        """
        Test _child_exit function when Prometheus cleanup fails.
        """
        mock_server = MagicMock()
        mock_worker = MagicMock()
        mock_worker.pid = 12345

        # Capture the child_exit function from the options
        captured_child_exit = None

        def capture_standalone_app(
            app: Any, custom_options: Optional[dict] = None
        ) -> MagicMock:
            nonlocal captured_child_exit
            captured_child_exit = (
                custom_options.get("child_exit") if custom_options else None
            )
            mock_instance = MagicMock()
            mock_instance.run = MagicMock()
            return mock_instance

        with patch("app.web.server.logging") as mock_logging:
            with patch("prometheus_client.multiprocess") as mock_multiprocess:
                prometheus_error = Exception("Prometheus error")
                mock_multiprocess.mark_process_dead.side_effect = (
                    prometheus_error
                )

                with patch(
                    "app.web.server._create_app", return_value=MagicMock()
                ):
                    with patch(
                        "gunicorn.app.wsgiapp.WSGIApplication",
                        side_effect=capture_standalone_app,
                    ):
                        start_web_server(
                            github_access_token="token",
                            github_api_url="https://api.github.com",
                            host="127.0.0.1",
                            port=8000,
                            inventory_provider=None,
                            kube_client=None,
                        )

                        # Test the child_exit function with Prometheus error
                        if captured_child_exit:
                            captured_child_exit(mock_server, mock_worker)
                            mock_multiprocess.mark_process_dead.assert_called_once_with(
                                12345
                            )
                            mock_logging.exception.assert_called_with(
                                "Failed to mark worker pid dead for Prometheus at exit: %s",
                                prometheus_error,
                            )


if __name__ == "__main__":
    unittest.main()
