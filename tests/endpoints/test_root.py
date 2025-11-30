import json
import unittest

from flask import Flask, Response
from unittest.mock import MagicMock

from flask.ctx import AppContext

from app.endpoints.root import root_endpoint


class TestRootEndpoint(unittest.TestCase):
    def setUp(self) -> None:
        """
        Set up the test environment.

        This method initializes a Flask application instance and pushes its application
        context to make it available during the test execution. It is executed before
        each test method in the test case.
        """
        self.app: Flask = Flask(__name__)
        self.app_context: AppContext = self.app.app_context()
        self.app_context.push()

    def tearDown(self) -> None:
        """
        Tear down the test environment.

        This method pops the Flask application context that was pushed during the
        `setUp` method. It is executed after each test method in the test case to
        clean up the test environment.
        """
        self.app_context.pop()

    def test_root_endpoint_with_callable_provider(self) -> None:
        """
        Test root_endpoint with a callable inventory provider.

        This test verifies that when INVENTORY_PROVIDER is set to a callable function,
        the endpoint correctly invokes the provider and returns its data as JSON.

        The test sets up a mock inventory provider that returns a predefined list of
        inventory items. It then configures the Flask application to use this mock
        provider, calls the root_endpoint function, and asserts that the response
        contains the expected data, status code, and content type.

        Finally, it ensures that the mock provider was called exactly once.
        """
        mock_inventory_data: list[dict[str, int | str]] = [
            {"id": 1, "name": "item1"},
            {"id": 2, "name": "item2"},
        ]
        mock_provider: MagicMock = MagicMock(return_value=mock_inventory_data)

        self.app.config["INVENTORY_PROVIDER"] = mock_provider

        response: Response = root_endpoint()

        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")

        response_data: str = json.loads(response.get_data(as_text=True))
        self.assertEqual(response_data, mock_inventory_data)

        mock_provider.assert_called_once()

    def test_root_endpoint_with_non_callable_provider(self) -> None:
        """
        Test root_endpoint with a non-callable inventory provider.

        This test verifies that when INVENTORY_PROVIDER is set to a non-callable value,
        the endpoint returns an empty JSON array.
        """
        self.app.config["INVENTORY_PROVIDER"] = "not_callable"

        response: Response = root_endpoint()

        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")

        response_data: str = json.loads(response.get_data(as_text=True))
        self.assertEqual(response_data, [])

    def test_root_endpoint_with_no_provider(self) -> None:
        """
        Test root_endpoint when INVENTORY_PROVIDER is not configured.

        This test verifies that when INVENTORY_PROVIDER is not set in the configuration,
        the endpoint returns an empty JSON array.
        """
        self.app.config.pop("INVENTORY_PROVIDER", None)

        response: Response = root_endpoint()

        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")

        response_data: str = json.loads(response.get_data(as_text=True))
        self.assertEqual(response_data, [])

    def test_root_endpoint_with_none_provider(self) -> None:
        """
        Test root_endpoint when INVENTORY_PROVIDER is explicitly set to None.

        This test verifies that when INVENTORY_PROVIDER is set to None,
        the endpoint returns an empty JSON array.
        """
        self.app.config["INVENTORY_PROVIDER"] = None

        response: Response = root_endpoint()

        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")

        response_data: str = json.loads(response.get_data(as_text=True))
        self.assertEqual(response_data, [])


if __name__ == "__main__":
    unittest.main()
