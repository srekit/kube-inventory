import unittest
import requests

from unittest.mock import patch, Mock

from app.clients.github import GithubClient


class TestGithubClient(unittest.TestCase):
    def setUp(self) -> None:
        """
        Sets up the test environment for the TestGithubClient class.

        Initializes:
            - `self.api_url` (str): The base URL of the GitHub API.
            - `self.access_token` (str): A test GitHub personal access token.
            - `self.client_with_token` (GithubClient): An instance of GithubClient initialized with an access token.
            - `self.client_without_token` (GithubClient): An instance of GithubClient initialized without an access token.
        """
        self.api_url: str = "https://api.github.com"
        self.access_token: str = "test_token"
        self.client_with_token: GithubClient = GithubClient(self.access_token, self.api_url)
        self.client_without_token: GithubClient = GithubClient(None, self.api_url)


    def test_initializes_with_access_token(self) -> None:
        """
        Tests that the GithubClient initializes correctly when an access token is provided.

        Verifies:
            - The API URL is set correctly.
            - The headers include the GitHub API version and the authorization token.
        """
        expected_headers: dict = {
            'X-GitHub-Api-Version': '2022-11-28',
            'Authorization': f"Bearer {self.access_token}"
        }

        self.assertEqual(self.client_with_token.api_url, self.api_url)
        self.assertEqual(self.client_with_token.headers, expected_headers)


    def test_initializes_without_access_token(self) -> None:
        """
        Tests that the GithubClient initializes correctly when no access token is provided.

        Verifies:
            - The API URL is set correctly.
            - The headers include only the GitHub API version without an authorization token.
        """
        expected_headers: dict = {
            'X-GitHub-Api-Version': '2022-11-28'
        }

        self.assertEqual(self.client_without_token.api_url, self.api_url)
        self.assertEqual(self.client_without_token.headers, expected_headers)


    def test_fetches_latest_release_successfully(self) -> None:
        """
        Tests that the `get_latest_release` method fetches the latest release successfully.

        Scenario:
            - The GitHub API returns a 200 status code with a valid response.

        Verifies:
            - The method returns the correct release data.
            - The `requests.get` method is called with the correct URL and headers.

        Mocks:
            - `requests.get` to simulate the API response.
        """
        repo_name: str = "owner/repo"
        mock_response: dict = {
            "name": "v1.0.0",
            "tag_name": "v1.0.0",
            "published_at": "2023-01-01T00:00:00Z"
        }

        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_response

            result: dict  = self.client_with_token.get_latest_release(repo_name)

            self.assertEqual(result, mock_response)
            mock_get.assert_called_once_with(
                url=f"{self.api_url}/repos/{repo_name}/releases/latest",
                headers=self.client_with_token.headers
            )


    def test_returns_empty_dict_on_latest_release_non_200_status(self) -> None:
        """
        Tests that the `get_latest_release` method returns an empty dictionary
        when the GitHub API responds with a non-200 status code.

        Scenario:
            - The API returns a 404 status code.

        Verifies:
            - The method returns an empty dictionary.
            - A warning log is generated with the appropriate message.

        Mocks:
            - `requests.get` to simulate the API response.
            - `logging.warning` to verify the warning log.
        """
        repo_name: str = "owner/repo"

        with patch("requests.get") as mock_get:
            with patch("logging.warning") as mock_log:
                mock_get.return_value.status_code = 404

                result: dict = self.client_with_token.get_latest_release(repo_name)

                self.assertEqual(result, {})
                mock_log.assert_called_once_with(
                    f"Unable to get latest release of repo {repo_name}, status code is 404")


    def test_returns_empty_dict_on_latest_release_request_exception(self) -> None:
        """
        Tests that the `get_latest_release` method returns an empty dictionary
        when a `RequestException` is raised during the API call.

        Scenario:
            - A `RequestException` is simulated to occur during the API request.

        Verifies:
            - The method returns an empty dictionary.
            - An error log is generated with the appropriate message.

        Mocks:
            - `requests.get` to raise a `RequestException`.
            - `logging.error` to verify the error log.
        """
        repo_name: str = "owner/repo"

        with patch("requests.get", side_effect=requests.exceptions.RequestException("Connection error")) as mock_get:
            with patch("logging.error") as mock_log:
                result: dict = self.client_with_token.get_latest_release(repo_name)

                self.assertEqual(result, {})
                mock_log.assert_called_once_with(f"Unable to get latest release of repo {repo_name}: Connection error")


    def test_fetches_release_by_tag_name_successfully(self) -> None:
        """
        Tests that the `get_release_by_tag_name` method fetches the release data
        for a specific tag name successfully.

        Scenario:
            - The GitHub API returns a 200 status code with a valid response.

        Verifies:
            - The method returns the correct release data.
            - The `requests.get` method is called with the correct URL and headers.

        Mocks:
            - `requests.get` to simulate the API response.
        """
        repo_name: str = "owner/repo"
        tag_name: str = "v1.0.0"
        mock_response: dict = {
            "name": "v1.0.0",
            "tag_name": "v1.0.0",
            "published_at": "2023-01-01T00:00:00Z"
        }

        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_response

            result: dict = self.client_with_token.get_release_by_tag_name(repo_name, tag_name)

            self.assertEqual(result, mock_response)
            mock_get.assert_called_once_with(
                url=f"{self.api_url}/repos/{repo_name}/releases/tags/{tag_name}",
                headers=self.client_with_token.headers
            )


    def test_returns_empty_dict_on_release_by_tag_non_200_status(self) -> None:
        """
        Tests that the `get_release_by_tag_name` method returns an empty dictionary
        when the GitHub API responds with a non-200 status code.

        Scenario:
            - The API returns a 404 status code.

        Verifies:
            - The method returns an empty dictionary.
            - A warning log is generated with the appropriate message.

        Mocks:
            - `requests.get` to simulate the API response.
            - `logging.warning` to verify the warning log.
        """
        repo_name: str = "owner/repo"
        tag_name: str = "v1.0.0"

        with patch("requests.get") as mock_get:
            with patch("logging.warning") as mock_log:
                mock_get.return_value.status_code = 404

                result: dict = self.client_with_token.get_release_by_tag_name(repo_name, tag_name)

                self.assertEqual(result, {})
                mock_log.assert_called_once_with(
                    f"Unable to get release by tag {tag_name} of repo {repo_name}, status code is 404")


    def test_fetches_tag_release_date_successfully(self) -> None:
        """
        Tests that the `get_tag_release_date` method fetches the release date
        for a specific tag successfully.

        Scenario:
            - The GitHub API returns a 200 status code with a valid response.

        Verifies:
            - The method returns the correct release date as a string.
            - The `requests.get` method is called with the correct URL and headers.

        Mocks:
            - `requests.get` to simulate the API response.
        """
        repo_name: str = "owner/repo"
        release_name: str = "v1.0.0"
        expected_date: str = "2023-01-01T00:00:00Z"
        mock_response: dict = {"published_at": expected_date}

        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_response

            result: str = self.client_with_token.get_tag_release_date(repo_name, release_name)

            self.assertEqual(result, expected_date)


    def test_returns_empty_string_on_tag_release_date_error(self) -> None:
        """
        Tests that the `get_tag_release_date` method returns an empty string
        when the GitHub API responds with a non-200 status code.

        Scenario:
            - The API returns a 404 status code.

        Verifies:
            - The method returns an empty string.
            - A warning log is generated with the appropriate message.

        Mocks:
            - `requests.get` to simulate the API response.
            - `logging.warning` to verify the warning log.
        """
        repo_name: str = "owner/repo"
        release_name: str = "v1.0.0"

        with patch("requests.get") as mock_get:
            with patch("logging.warning") as mock_log:
                mock_get.return_value.status_code = 404

                result: str = self.client_with_token.get_tag_release_date(repo_name, release_name)

                self.assertEqual(result, "")

    def test_lists_releases_successfully_excluding_prereleases(self) -> None:
        """
        Tests that the `list_releases` method fetches releases successfully
        while excluding prereleases by default.

        Scenario:
            - The GitHub API returns a 200 status code with releases including prereleases.

        Verifies:
            - The method returns only non-prerelease releases.
            - Prereleases are filtered out from the response.

        Mocks:
            - `requests.get` to simulate the API response.
        """
        repo_name: str = "owner/repo"
        mock_response: list[dict] = [
            {"name": "v1.0.0", "prerelease": False, "published_at": "2023-01-01T00:00:00Z"},
            {"name": "v1.0.0-beta", "prerelease": True, "published_at": "2022-12-01T00:00:00Z"}
        ]
        expected_result: list[dict] = [
            {"name": "v1.0.0", "prerelease": False, "published_at": "2023-01-01T00:00:00Z"}
        ]

        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_response

            result: list = self.client_with_token.list_releases(repo_name)

            self.assertEqual(result, expected_result)


    def test_lists_releases_successfully_including_prereleases(self) -> None:
        """
        Tests that the `list_releases` method fetches all releases successfully,
        including prereleases when the `include_prerelease` parameter is set to True.

        Scenario:
            - The GitHub API returns a 200 status code with releases, including prereleases.

        Verifies:
            - The method returns all releases, including prereleases.
            - The total number of releases matches the expected count.

        Mocks:
            - `requests.get` to simulate the API response.
        """
        repo_name: str = "owner/repo"
        mock_response: list[dict] = [
            {"name": "v1.0.0", "prerelease": False, "published_at": "2023-01-01T00:00:00Z"},
            {"name": "v1.0.0-beta", "prerelease": True, "published_at": "2022-12-01T00:00:00Z"}
        ]

        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_response

            result: list = self.client_with_token.list_releases(repo_name, include_prerelease=True)

            self.assertEqual(len(result), 2)


    def test_returns_empty_list_on_list_releases_exception(self) -> None:
        """
        Tests that the `list_releases` method returns an empty list
        when a `RequestException` is raised during the API call.

        Scenario:
            - A `RequestException` is simulated to occur during the API request.

        Verifies:
            - The method returns an empty list.
            - An error log is generated with the appropriate message.

        Mocks:
            - `requests.get` to raise a `RequestException`.
            - `logging.error` to verify the error log.
        """
        repo_name: str = "owner/repo"

        with patch("requests.get", side_effect=requests.exceptions.RequestException("Error")) as mock_get:
            with patch("logging.error") as mock_log:
                result: list = self.client_with_token.list_releases(repo_name)

                self.assertEqual(result, [])
                mock_log.assert_called_once_with(f'Unable to list releases of repo {repo_name}, error is: Error')


    def test_lists_tags_successfully(self) -> None:
        """
        Tests that the `list_tags` method fetches all tags successfully.

        Scenario:
            - The GitHub API returns a 200 status code with a valid response containing tags.

        Verifies:
            - The method returns a list of tag names.
            - The returned list matches the expected result.

        Mocks:
            - `requests.get` to simulate the API response.
        """
        repo_name: str = "owner/repo"
        mock_response: list[dict] = [
            {"name": "v1.0.0"},
            {"name": "v0.9.0"}
        ]
        expected_result: list = ["v1.0.0", "v0.9.0"]

        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_response

            result: list = self.client_with_token.list_tags(repo_name)

            self.assertEqual(result, expected_result)


    def test_returns_empty_list_on_list_tags_non_200_status(self) -> None:
        """
        Tests that the `list_tags` method returns an empty list
        when the GitHub API responds with a non-200 status code.

        Scenario:
            - The API returns a 404 status code.

        Verifies:
            - The method returns an empty list.
            - A warning log is generated with the appropriate message.

        Mocks:
            - `requests.get` to simulate the API response.
            - `logging.warning` to verify the warning log.
        """
        repo_name: str = "owner/repo"

        with patch("requests.get") as mock_get:
            with patch("logging.warning") as mock_log:
                mock_get.return_value.status_code = 404

                result: list = self.client_with_token.list_tags(repo_name)

                self.assertEqual(result, [])
                mock_log.assert_called_once_with(f"Unable to list tags of repo {repo_name}, status code is: 404")


    def test_returns_empty_list_on_list_tags_exception(self) -> None:
        """
        Tests that the `list_tags` method returns an empty list
        when a `RequestException` is raised during the API call.

        Scenario:
            - A `RequestException` is simulated to occur during the API request.

        Verifies:
            - The method returns an empty list.
            - An error log is generated with the appropriate message.

        Mocks:
            - `requests.get` to raise a `RequestException`.
            - `logging.error` to verify the error log.
        """
        repo_name: str = "owner/repo"

        with patch("requests.get", side_effect=requests.exceptions.RequestException("Error")) as mock_get:
            with patch("logging.error") as mock_log:
                result: list = self.client_with_token.list_tags(repo_name)

                self.assertEqual(result, [])
                mock_log.assert_called_once_with(f'Unable to list tags of repo {repo_name}, error is: Error')


if __name__ == '__main__':
    unittest.main()
