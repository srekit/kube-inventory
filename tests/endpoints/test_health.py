
import requests
import unittest

from flask import Flask
from flask.ctx import AppContext
from typing import Any
from unittest.mock import patch, MagicMock

from app.endpoints.health import health_endpoint, _perform_health_checks


class TestHealthEndpoint(unittest.TestCase):
    def setUp(self) -> None:
        """
        Set up test fixtures for the test case.

        This method initializes the Flask application and its application context,
        which is required for testing Flask endpoints. It also sets up default
        values for file paths, GitHub access token, and GitHub API URL used in the tests.
        """
        self.app: Flask = Flask(__name__)
        self.app_context: AppContext = self.app.app_context()
        self.app_context.push()

        self.default_apps_file_path: str = "/path/to/default/apps.yaml"
        self.extra_apps_file_path: str = "/path/to/extra/apps.yaml"
        self.github_access_token: str = "test_token_123"
        self.github_api_url: str = "https://api.github.com"


    def tearDown(self) -> None:
        """
        Tear down test fixtures.

        This method pops the application context created during the `setUp` method,
        ensuring that no resources are left allocated after each test case.
        """
        self.app_context.pop()


    @patch('app.endpoints.health._perform_health_checks')
    @patch('app.endpoints.health.time.time')
    @patch('app.endpoints.health.datetime')
    def test_health_endpoint_healthy_status(self, mock_datetime, mock_time, mock_perform_health_checks) -> None:
        """
        Test health_endpoint when all checks pass and status is healthy.

        This test simulates a scenario where all health checks are successful. It verifies
        that the endpoint returns an HTTP 200 status code, the correct response structure,
        and accurate response time and timestamp.

        Args:
            mock_datetime (MagicMock): Mock for the datetime module to control the timestamp.
            mock_time (MagicMock): Mock for the time module to control response time calculation.
            mock_perform_health_checks (MagicMock): Mock for the _perform_health_checks function
                to simulate a healthy status.
        """
        mock_time.side_effect = [1000.0, 1000.5]  # 0.5 second response time
        mock_datetime.now.return_value.replace.return_value.isoformat.return_value = "2023-01-01T12:00:00"
        mock_perform_health_checks.return_value = {
            'status': 'healthy',
            'checks': {'kubernetes': {'status': 'healthy'}}
        }

        response, status_code = health_endpoint(
            self.default_apps_file_path,
            self.extra_apps_file_path,
            self.github_access_token,
            self.github_api_url
        )

        self.assertEqual(status_code, 200)
        response_data = response.get_json()
        self.assertEqual(response_data['status'], 'healthy')
        self.assertEqual(response_data['response_time_ms'], 500.0)
        self.assertEqual(response_data['timestamp'], "2023-01-01T12:00:00Z")


    @patch('app.endpoints.health._perform_health_checks')
    @patch('app.endpoints.health.time.time')
    @patch('app.endpoints.health.datetime')
    def test_health_endpoint_unhealthy_status(self, mock_datetime, mock_time, mock_perform_health_checks) -> None:
        """
        Test health_endpoint when checks fail and status is unhealthy.

        This test simulates a scenario where the health checks return an unhealthy status.
        It verifies that the endpoint responds with an HTTP 503 status code, the correct
        response structure, and accurate response time and timestamp.

        Args:
            mock_datetime (MagicMock): Mock for the datetime module to control the timestamp.
            mock_time (MagicMock): Mock for the time module to control response time calculation.
            mock_perform_health_checks (MagicMock): Mock for the _perform_health_checks function
                to simulate an unhealthy status.
        """
        mock_time.side_effect = [1000.0, 1000.2]  # 0.2 second response time
        mock_datetime.now.return_value.replace.return_value.isoformat.return_value = "2023-01-01T12:00:00"
        mock_perform_health_checks.return_value = {
            'status': 'unhealthy',
            'checks': {'kubernetes': {'status': 'unhealthy', 'error': 'Connection failed'}}
        }

        response, status_code = health_endpoint(
            self.default_apps_file_path,
            self.extra_apps_file_path,
            self.github_access_token,
            self.github_api_url
        )

        self.assertEqual(status_code, 503)
        response_data = response.get_json()
        self.assertEqual(response_data['status'], 'unhealthy')
        self.assertEqual(response_data['response_time_ms'], 200.0)


    @patch('app.endpoints.health._perform_health_checks')
    def test_health_endpoint_calls_perform_health_checks_with_correct_params(self, mock_perform_health_checks) -> None:
        """
        Test health_endpoint calls _perform_health_checks with correct parameters.

        This test verifies that the `health_endpoint` function correctly calls the
        `_perform_health_checks` function with the expected parameters.

        Args:
            mock_perform_health_checks (MagicMock): Mock for the `_perform_health_checks` function.
        """
        mock_perform_health_checks.return_value = {'status': 'healthy'}

        health_endpoint(
            self.default_apps_file_path,
            self.extra_apps_file_path,
            self.github_access_token,
            self.github_api_url
        )

        mock_perform_health_checks.assert_called_once_with(
            default_apps_file_path=self.default_apps_file_path,
            extra_apps_file_path=self.extra_apps_file_path,
            github_access_token=self.github_access_token,
            github_api_url=self.github_api_url
        )


class TestPerformHealthChecks(unittest.TestCase):
    def setUp(self) -> None:
        """
        Set up test fixtures for the test case.

        This method initializes default values for file paths, GitHub access token,
        and GitHub API URL used in the tests.
        """
        self.default_apps_file_path: str = "/path/to/default/apps.yaml"
        self.extra_apps_file_path: str = "/path/to/extra/apps.yaml"
        self.github_access_token: str = "test_token_123"
        self.github_api_url: str = "https://api.github.com"


    @patch('app.endpoints.health.os.path.exists')
    @patch('app.endpoints.health.os.access')
    @patch('app.endpoints.health.requests.get')
    @patch('app.endpoints.health.client.CoreV1Api')
    @patch('app.endpoints.health.config.load_kube_config')
    def test_all_health_checks_pass(
            self,
            mock_load_kube_config,
            mock_core_v1_api,
            mock_requests_get,
            mock_os_access,
            mock_os_exists
    ) -> None:
        """
        Test _perform_health_checks when all checks pass.

        This test simulates a scenario where all health checks are successful. It verifies
        that the function returns a 'healthy' status for all checks, including Kubernetes,
        GitHub API, and configuration files.

        Args:
            mock_load_kube_config (MagicMock): Mock for the Kubernetes configuration loader.
            mock_core_v1_api (MagicMock): Mock for the Kubernetes CoreV1Api client.
            mock_requests_get (MagicMock): Mock for the requests.get function to simulate
                GitHub API responses.
            mock_os_access (MagicMock): Mock for the os.access function to simulate file
                accessibility checks.
            mock_os_exists (MagicMock): Mock for the os.path.exists function to simulate
                file existence checks.
        """
        mock_v1_api: MagicMock = MagicMock()
        mock_core_v1_api.return_value = mock_v1_api

        mock_response: MagicMock = MagicMock()
        mock_response.json.return_value = {'rate': {'remaining': 4000}}
        mock_requests_get.return_value = mock_response

        mock_os_exists.return_value = True
        mock_os_access.return_value = True

        result: dict[str, Any] = _perform_health_checks(
            self.default_apps_file_path,
            self.extra_apps_file_path,
            self.github_access_token,
            self.github_api_url
        )

        self.assertEqual(result['status'], 'healthy')
        self.assertEqual(result['checks']['kubernetes']['status'], 'healthy')
        self.assertEqual(result['checks']['github_api']['status'], 'healthy')
        self.assertEqual(result['checks']['github_api']['rate_limit_remaining'], 4000)
        self.assertEqual(result['checks']['config_files']['status'], 'healthy')


    @patch('app.endpoints.health.os.path.exists')
    @patch('app.endpoints.health.os.access')
    @patch('app.endpoints.health.requests.get')
    @patch('app.endpoints.health.config.load_kube_config')
    @patch('app.endpoints.health.logging.error')
    def test_kubernetes_check_fails(self, mock_logging_error, mock_load_kube_config,
                                    mock_requests_get, mock_os_access, mock_os_exists) -> None:
        """
        Test _perform_health_checks when Kubernetes check fails.

        This test simulates a failure in the Kubernetes health check by raising an
        exception during the Kubernetes configuration loading process. It verifies
        that the function correctly identifies the failure, sets the status to
        'unhealthy', and logs the appropriate error message.

        Args:
            mock_logging_error (MagicMock): Mock for the logging.error function to verify
                error logging.
            mock_load_kube_config (MagicMock): Mock for the Kubernetes configuration loader,
                which raises an exception to simulate a failure.
            mock_requests_get (MagicMock): Mock for the requests.get function to simulate
                GitHub API responses.
            mock_os_access (MagicMock): Mock for the os.access function to simulate file
                accessibility checks.
            mock_os_exists (MagicMock): Mock for the os.path.exists function to simulate
                file existence checks.
        """
        mock_load_kube_config.side_effect = Exception("Kubernetes connection failed")

        mock_response: MagicMock = MagicMock()
        mock_response.json.return_value = {'rate': {'remaining': 4000}}
        mock_requests_get.return_value = mock_response

        mock_os_exists.return_value = True
        mock_os_access.return_value = True

        result = _perform_health_checks(
            self.default_apps_file_path,
            self.extra_apps_file_path,
            self.github_access_token,
            self.github_api_url
        )

        self.assertEqual(result['status'], 'unhealthy')
        self.assertEqual(result['checks']['kubernetes']['status'], 'unhealthy')
        self.assertEqual(result['checks']['kubernetes']['error'], "Kubernetes connection failed")
        mock_logging_error.assert_any_call("Kubernetes health check failed: Kubernetes connection failed")


    @patch('app.endpoints.health.os.path.exists')
    @patch('app.endpoints.health.os.access')
    @patch('app.endpoints.health.requests.get')
    @patch('app.endpoints.health.client.CoreV1Api')
    @patch('app.endpoints.health.config.load_kube_config')
    @patch('app.endpoints.health.logging.error')
    def test_github_api_check_fails(self, mock_logging_error, mock_load_kube_config,
                                    mock_core_v1_api, mock_requests_get, mock_os_access, mock_os_exists) -> None:
        """
        Test _perform_health_checks when GitHub API check fails.

        This test simulates a failure in the GitHub API health check by raising a
        RequestException. It verifies that the function correctly identifies the
        failure, sets the status to 'unhealthy', and logs the appropriate error message.

        Args:
            mock_logging_error (MagicMock): Mock for the logging.error function.
            mock_load_kube_config (MagicMock): Mock for the Kubernetes configuration loader.
            mock_core_v1_api (MagicMock): Mock for the Kubernetes CoreV1Api client.
            mock_requests_get (MagicMock): Mock for the requests.get function.
            mock_os_access (MagicMock): Mock for the os.access function.
            mock_os_exists (MagicMock): Mock for the os.path.exists function.
        """
        mock_v1_api: MagicMock = MagicMock()
        mock_core_v1_api.return_value = mock_v1_api

        mock_requests_get.side_effect = requests.RequestException("GitHub API unreachable")

        mock_os_exists.return_value = True
        mock_os_access.return_value = True

        result = _perform_health_checks(
            self.default_apps_file_path,
            self.extra_apps_file_path,
            self.github_access_token,
            self.github_api_url
        )

        self.assertEqual(result['status'], 'unhealthy')
        self.assertEqual(result['checks']['github_api']['status'], 'unhealthy')
        self.assertEqual(result['checks']['github_api']['error'], "GitHub API unreachable")
        mock_logging_error.assert_any_call("GitHub API health check failed: GitHub API unreachable")


    @patch('app.endpoints.health.os.path.exists')
    @patch('app.endpoints.health.os.access')
    @patch('app.endpoints.health.requests.get')
    @patch('app.endpoints.health.client.CoreV1Api')
    @patch('app.endpoints.health.config.load_kube_config')
    @patch('app.endpoints.health.logging.error')
    def test_config_files_check_fails(self, mock_logging_error, mock_load_kube_config,
                                      mock_core_v1_api, mock_requests_get, mock_os_access, mock_os_exists) -> None:
        """
        Test _perform_health_checks when configuration file checks fail.

        This test simulates a scenario where the configuration files required for the
        application are not accessible. It verifies that the function correctly identifies
        the failure, sets the status to 'unhealthy', and includes an appropriate error
        message in the response.

        Args:
            mock_logging_error (MagicMock): Mock for the logging.error function to verify
                error logging.
            mock_load_kube_config (MagicMock): Mock for the Kubernetes configuration loader.
            mock_core_v1_api (MagicMock): Mock for the Kubernetes CoreV1Api client.
            mock_requests_get (MagicMock): Mock for the requests.get function to simulate
                GitHub API responses.
            mock_os_access (MagicMock): Mock for the os.access function to simulate file
                accessibility checks.
            mock_os_exists (MagicMock): Mock for the os.path.exists function to simulate
                file existence checks.
        """
        mock_v1_api: MagicMock = MagicMock()
        mock_core_v1_api.return_value = mock_v1_api

        mock_response: MagicMock = MagicMock()
        mock_response.json.return_value = {'rate': {'remaining': 4000}}
        mock_requests_get.return_value = mock_response

        mock_os_exists.return_value = False  # File doesn't exist

        result: dict[str, Any] = _perform_health_checks(
            self.default_apps_file_path,
            self.extra_apps_file_path,
            self.github_access_token,
            self.github_api_url
        )

        self.assertEqual(result['status'], 'unhealthy')
        self.assertEqual(result['checks']['config_files']['status'], 'unhealthy')
        self.assertIn("Config file not accessible", result['checks']['config_files']['error'])


    @patch('app.endpoints.health.os.path.exists')
    @patch('app.endpoints.health.os.access')
    @patch('app.endpoints.health.requests.get')
    @patch('app.endpoints.health.client.CoreV1Api')
    @patch('app.endpoints.health.config.load_kube_config')
    def test_github_api_without_token(
            self,
            mock_load_kube_config,
            mock_core_v1_api,
            mock_requests_get,
            mock_os_access,
            mock_os_exists
    ) -> None:
        """
        Test _perform_health_checks when GitHub API is called without a token.

        This test simulates a scenario where the GitHub API health check is performed
        without providing an access token. It verifies that the function correctly
        handles the absence of a token, sets the status to 'healthy', and ensures
        that no authorization headers are included in the API request.

        Args:
            mock_load_kube_config (MagicMock): Mock for the Kubernetes configuration loader.
            mock_core_v1_api (MagicMock): Mock for the Kubernetes CoreV1Api client.
            mock_requests_get (MagicMock): Mock for the requests.get function to simulate
                GitHub API responses.
            mock_os_access (MagicMock): Mock for the os.access function to simulate file
                accessibility checks.
            mock_os_exists (MagicMock): Mock for the os.path.exists function to simulate
                file existence checks.
        """
        mock_v1_api: MagicMock = MagicMock()
        mock_core_v1_api.return_value = mock_v1_api

        mock_response: MagicMock = MagicMock()
        mock_response.json.return_value = {'rate': {'remaining': 60}}
        mock_requests_get.return_value = mock_response

        mock_os_exists.return_value = True
        mock_os_access.return_value = True

        result: dict[str, Any] = _perform_health_checks(
            self.default_apps_file_path,
            self.extra_apps_file_path,
            "",  # Empty token
            self.github_api_url
        )

        self.assertEqual(result['checks']['github_api']['status'], 'healthy')
        args, kwargs = mock_requests_get.call_args
        self.assertEqual(kwargs['headers'], {})


    @patch('app.endpoints.health.os.path.exists')
    @patch('app.endpoints.health.os.access')
    @patch('app.endpoints.health.requests.get')
    @patch('app.endpoints.health.client.CoreV1Api')
    @patch('app.endpoints.health.config.load_kube_config')
    def test_config_files_with_none_paths(self, mock_load_kube_config, mock_core_v1_api,
                                          mock_requests_get, mock_os_access, mock_os_exists) -> None:
        """
        Test _perform_health_checks when configuration file paths are None.

        This test simulates a scenario where the configuration file paths provided to the
        `_perform_health_checks` function are `None`. It verifies that the function handles
        this case gracefully by skipping file existence and accessibility checks, and
        setting the status of the configuration files check to 'healthy'.

        Args:
            mock_load_kube_config (MagicMock): Mock for the Kubernetes configuration loader.
            mock_core_v1_api (MagicMock): Mock for the Kubernetes CoreV1Api client.
            mock_requests_get (MagicMock): Mock for the requests.get function to simulate
                GitHub API responses.
            mock_os_access (MagicMock): Mock for the os.access function to simulate file
                accessibility checks.
            mock_os_exists (MagicMock): Mock for the os.path.exists function to simulate
                file existence checks.
        """
        mock_v1_api: MagicMock = MagicMock()
        mock_core_v1_api.return_value = mock_v1_api

        mock_response: MagicMock = MagicMock()
        mock_response.json.return_value = {'rate': {'remaining': 4000}}
        mock_requests_get.return_value = mock_response

        result: dict[str, Any] = _perform_health_checks(
            "",
            "",
            self.github_access_token,
            self.github_api_url
        )

        self.assertEqual(result['checks']['config_files']['status'], 'healthy')
        mock_os_exists.assert_not_called()
        mock_os_access.assert_not_called()


    @patch('app.endpoints.health.os.path.exists')
    @patch('app.endpoints.health.os.access')
    @patch('app.endpoints.health.requests.get')
    @patch('app.endpoints.health.client.CoreV1Api')
    @patch('app.endpoints.health.config.load_kube_config')
    def test_partial_config_files_accessible(self, mock_load_kube_config, mock_core_v1_api,
                                             mock_requests_get, mock_os_access, mock_os_exists) -> None:
        """
        Test _perform_health_checks when only some configuration files are accessible.

        This test simulates a scenario where one configuration file is accessible while
        the other is not. It verifies that the function correctly identifies the partial
        accessibility, sets the overall status to 'unhealthy', and includes the appropriate
        status for the configuration files check.

        Args:
            mock_load_kube_config (MagicMock): Mock for the Kubernetes configuration loader.
            mock_core_v1_api (MagicMock): Mock for the Kubernetes CoreV1Api client.
            mock_requests_get (MagicMock): Mock for the requests.get function to simulate
                GitHub API responses.
            mock_os_access (MagicMock): Mock for the os.access function to simulate file
                accessibility checks.
            mock_os_exists (MagicMock): Mock for the os.path.exists function to simulate
                file existence checks.
        """
        mock_v1_api: MagicMock = MagicMock()
        mock_core_v1_api.return_value = mock_v1_api

        mock_response: MagicMock = MagicMock()
        mock_response.json.return_value = {'rate': {'remaining': 4000}}
        mock_requests_get.return_value = mock_response

        def side_effect_exists(path):
            return path == self.default_apps_file_path

        def side_effect_access(path):
            return path == self.default_apps_file_path

        mock_os_exists.side_effect = side_effect_exists
        mock_os_access.side_effect = side_effect_access

        result: dict[str, Any] = _perform_health_checks(
            self.default_apps_file_path,
            self.extra_apps_file_path,
            self.github_access_token,
            self.github_api_url
        )

        self.assertEqual(result['status'], 'unhealthy')
        self.assertEqual(result['checks']['config_files']['status'], 'unhealthy')


if __name__ == "__main__":
    unittest.main()
