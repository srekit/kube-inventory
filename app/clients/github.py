from typing import Optional, Any

import requests
import logging
import collections


class GithubClient:
    def __init__(
        self, github_access_token: Optional[str], github_api_url: str
    ) -> None:
        """
        Initializes the GithubClient instance.

        Args:
            github_access_token (Optional[str]): A GitHub personal access token for authentication.
                                                 If None, requests will be made without authentication.
            github_api_url (str): The base URL of the GitHub API (e.g., "https://api.github.com").
        """
        self.api_url = github_api_url

        if github_access_token:
            self.headers = {
                "X-GitHub-Api-Version": "2022-11-28",
                "Authorization": f"Bearer {github_access_token}",
            }
        else:
            self.headers = {"X-GitHub-Api-Version": "2022-11-28"}

    def get_latest_release(self, repo_name: str) -> dict[Any, Any]:
        """
        Fetches the latest release of a given GitHub repository.

        Args:
            repo_name (str): The name of the repository in the format 'owner/repo'.

        Returns:
            dict: A dictionary containing the latest release data if the request is successful.
                  Returns an empty dictionary if the request fails or the release is not found.

        Logs:
            - A warning if the request is unsuccessful (non-200 status code).
            - An error if a request exception occurs.

        API Reference:
            https://docs.github.com/en/rest/releases/releases?apiVersion=2022-11-28#get-the-latest-release
        """
        url = f"{self.api_url}/repos/{repo_name}/releases/latest"

        try:
            response = requests.get(url=url, headers=self.headers)
            if response.status_code == 200:
                response_data: dict[Any, Any] = response.json()
                return response_data
            else:
                logging.warning(
                    f"Unable to get latest release of repo {repo_name}, status code is {response.status_code}"
                )
                return {}
        except requests.exceptions.RequestException as e:
            logging.error(
                f"Unable to get latest release of repo {repo_name}: {e}"
            )
            return {}

    def get_release_by_tag_name(self, repo_name: str, tag_name: str) -> dict:
        """
        Fetches a release from a GitHub repository by its tag name.

        Args:
            repo_name (str): The name of the repository in the format 'owner/repo'.
            tag_name (str): The tag name of the release to fetch.

        Returns:
            dict: A dictionary containing the release data if the request is successful.
                  Returns an empty dictionary if the request fails or the release is not found.

        Logs:
            - A warning if the request is unsuccessful (non-200 status code).
            - An error if a request exception occurs.

        API Reference:
            https://docs.github.com/en/rest/releases/releases?apiVersion=2022-11-28#get-a-release-by-tag-name
        """
        url: str = f"{self.api_url}/repos/{repo_name}/releases/tags/{tag_name}"

        try:
            response: requests.Response = requests.get(
                url=url, headers=self.headers
            )
            if response.status_code == 200:
                response_data: dict[Any, Any] = response.json()
                return response_data
            else:
                logging.warning(
                    f"Unable to get release by tag {tag_name} of repo {repo_name}, status code is {response.status_code}"
                )
                return {}
        except requests.exceptions.RequestException as e:
            logging.error(
                f"Unable to get release by tag {tag_name} of repo {repo_name}: {e}"
            )
            return {}

    def get_tag_release_date(self, repo_name: str, release_name: str) -> str:
        """
        Fetches the release date of a specific tag from a GitHub repository.

        Args:
            repo_name (str): The name of the repository in the format 'owner/repo'.
            release_name (str): The name of the release tag to fetch the release date for.

        Returns:
            str: The release date as a string in ISO 8601 format if the request is successful.
                 Returns an empty string if the request fails or the release is not found.

        Logs:
            - A warning if the request is unsuccessful (non-200 status code).
            - An error if a request exception occurs.

        API Reference:
            https://docs.github.com/en/rest/releases/releases?apiVersion=2022-11-28#get-a-release-by-tag-name
        """
        url: str = (
            f"{self.api_url}/repos/{repo_name}/releases/tags/{release_name}"
        )

        try:
            response: requests.Response = requests.get(
                url=url, headers=self.headers
            )
            if response.status_code == 200:
                response_data: dict[Any, Any] = response.json()
                release_date: str = response_data["published_at"]
                return release_date
            else:
                logging.warning(
                    f"Unable to get published date of release {release_name} of repo {repo_name}, status code is: {response.status_code}"
                )
                return ""
        except requests.exceptions.RequestException as e:
            logging.error(
                f"Unable to list tags of repo {repo_name}, error is: {e}"
            )
            return ""

    def list_releases(
        self, repo_name: str, include_prerelease: bool = False
    ) -> list[Any] | None:
        """
        Fetches a list of releases from a GitHub repository.

        Args:
            repo_name (str): The name of the repository in the format 'owner/repo'.
            include_prerelease (bool, optional): Whether to include prerelease versions in the results.
                                                 Defaults to False.

        Returns:
            list[Any] | None: A list of releases, where each release is represented as an OrderedDict
                              containing 'name', 'prerelease', and 'published_at'. Returns an empty list
                              if the request fails or no releases are found.

        Logs:
            - Debug logs for each release found or skipped.
            - An error log if a request exception occurs.

        API Reference:
            https://docs.github.com/en/rest/releases/releases?apiVersion=2022-11-28#list-releases
        """
        url: str = f"{self.api_url}/repos/{repo_name}/releases"

        try:
            response: requests.Response = requests.get(
                url=url, headers=self.headers
            )
            if response.status_code == 200:
                response_data: dict = response.json()
                releases_dict: list[dict] = []
                for release in response_data:
                    if not include_prerelease and release["prerelease"]:
                        logging.debug(
                            f"Skipping prerelease {release['name']} in repo {repo_name}"
                        )
                        continue

                    r: collections.OrderedDict[
                        Any, Any
                    ] = collections.OrderedDict()
                    r["name"] = release["name"]
                    r["prerelease"] = release["prerelease"]
                    r["published_at"] = release["published_at"]
                    releases_dict.append(r)
                    logging.debug(
                        f"Found release {release['name']} in repo {repo_name}, prerelease: {release['prerelease']}, published at: {release['published_at']}"
                    )
                return releases_dict
            else:
                logging.warning(
                    f"Unable to list releases of repo {repo_name}, status code is: {response.status_code}"
                )
                return []
        except requests.exceptions.RequestException as e:
            logging.error(
                f"Unable to list releases of repo {repo_name}, error is: {e}"
            )
            return []

    def list_tags(self, repo_name: str) -> list:
        """
        Fetches a list of tags from a GitHub repository.

        Args:
            repo_name (str): The name of the repository in the format 'owner/repo'.

        Returns:
            list: A list of tag names as strings if the request is successful.
                  Returns an empty list if the request fails or no tags are found.

        Logs:
            - A warning if the request is unsuccessful (non-200 status code).
            - An error if a request exception occurs.

        API Reference:
            https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#list-repository-tags
        """
        url: str = f"{self.api_url}/repos/{repo_name}/tags"

        try:
            response: requests.Response = requests.get(
                url=url, headers=self.headers
            )
            if response.status_code == 200:
                response_data: dict = response.json()
                tags_dict: list[dict] = []
                for tag in response_data:
                    tags_dict.append(tag["name"])
                return tags_dict
            else:
                logging.warning(
                    f"Unable to list tags of repo {repo_name}, status code is: {response.status_code}"
                )
                return []
        except requests.exceptions.RequestException as e:
            logging.error(
                f"Unable to list tags of repo {repo_name}, error is: {e}"
            )
            return []
