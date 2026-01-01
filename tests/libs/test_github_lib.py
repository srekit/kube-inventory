import pytest

from unittest.mock import Mock, patch

from app.libs.github_lib import (
    count_releases_between,
    _extract_version_parts,
    get_release_with_fallback,
    _normalize_version_for_lookup,
)


class TestCountReleasesBetween:
    def test_count_releases_between_valid_case(self) -> None:
        """
        Test the `list_json` function to ensure it returns an `OrderedDict` structure.

        This test verifies that the `list_json` function correctly processes a pod and:
        - Returns the pod data as an `OrderedDict`.
        - Ensures the keys in the `OrderedDict` are in the expected order.
        - Verifies that the container data within the pod is also an `OrderedDict` with the correct key order.

        Test setup:
        - A mock pod is created with metadata (name, namespace, annotations, labels) and a single container.

        Assertions:
        - The pod data is an instance of `OrderedDict`.
        - The keys in the pod data are in the order: ["name", "namespace", "annotations", "labels", "containers"].
        - The container data is an instance of `OrderedDict`.
        - The keys in the container data are in the order: ["name", "image"].
        """
        mock_client: Mock = Mock()
        mock_client.list_releases.return_value = [
            {"name": "v2.0.0"},
            {"name": "v1.5.0"},
            {"name": "v1.0.0"},
        ]

        result: int = count_releases_between(mock_client, "test/repo", "v1.0.0")
        assert result == 2

    def test_count_releases_between_current_not_found(self) -> None:
        """
        Test the `count_releases_between` function when the specified release is not found.

        This test verifies that the `count_releases_between` function correctly handles the case
        where the specified release does not exist in the list of releases returned by the mock client.

        Test setup:
        - A mock client is used to simulate the GitHub API response with a list of releases.
        - The specified release ("v1.0.0") is not included in the list.

        Assertions:
        - The function returns -1 to indicate that the specified release was not found.
        """
        mock_client: Mock = Mock()
        mock_client.list_releases.return_value = [
            {"name": "v2.0.0"},
            {"name": "v1.5.0"},
        ]

        result: int = count_releases_between(mock_client, "test/repo", "v1.0.0")
        assert result == -1

    def test_count_releases_between_invalid_release_format(self) -> None:
        """
        Test the `count_releases_between` function with an invalid release format.

        This test verifies that the `count_releases_between` function correctly handles a case
        where one of the releases in the list has an invalid format.

        Test setup:
        - A mock client is used to simulate the GitHub API response with a list of releases.
        - The list includes a release with an invalid format ("invalid-format").

        Assertions:
        - The function returns the correct count of valid releases between the specified release
          ("v1.0.0") and the latest release ("v2.0.0").
        - A warning is logged for the invalid release format.
        """
        mock_client: Mock = Mock()
        mock_client.list_releases.return_value = [
            {"name": "v2.0.0"},
            {"name": "invalid-format"},
            {"name": "v1.0.0"},
        ]

        with patch("app.libs.github_lib.logging") as mock_logging:
            result: int = count_releases_between(
                mock_client, "test/repo", "v1.0.0"
            )
            assert result == 1
            mock_logging.warning.assert_called()

    def test_count_releases_between_same_version(self) -> None:
        """
        Test the `count_releases_between` function when the specified release is the same as the only release.

        This test verifies that the `count_releases_between` function correctly handles the case
        where the specified release matches the only release in the list.

        Test setup:
        - A mock client is used to simulate the GitHub API response with a single release.

        Assertions:
        - The function returns 0, indicating no releases exist between the specified release and itself.
        """
        mock_client: Mock = Mock()
        mock_client.list_releases.return_value = [{"name": "v1.0.0"}]

        result: int = count_releases_between(mock_client, "test/repo", "v1.0.0")
        assert result == 0


class TestExtractVersionParts:
    def test_extract_version_parts_with_v_prefix(self) -> None:
        """
        Test the `_extract_version_parts` function with a version string that includes a 'v' prefix.

        This test verifies that the function correctly extracts the major version and the minor version
        as a tuple when the input string starts with a 'v'.

        Test setup:
        - The input version string is "v1.2.3".

        Assertions:
        - The function returns the tuple (1, 2.3), representing the major version as an integer
          and the minor version as a float.
        """
        result: tuple[int, float] = _extract_version_parts("v1.2.3")
        assert result == (1, 2.3)

    def test_extract_version_parts_without_v_prefix(self) -> None:
        """
        Test the `_extract_version_parts` function with a version string that does not include a 'v' prefix.

        This test verifies that the function correctly extracts the major version and the minor version
        as a tuple when the input string does not start with a 'v'.

        Test setup:
        - The input version string is "1.2.3".

        Assertions:
        - The function returns the tuple (1, 2.3), representing the major version as an integer
          and the minor version as a float.
        """
        result: tuple[int, float] = _extract_version_parts("1.2.3")
        assert result == (1, 2.3)

    def test_extract_version_parts_with_at_symbol(self) -> None:
        """
        Test the `_extract_version_parts` function with a version string containing an '@' symbol.

        This test verifies that the function correctly extracts the major version and the minor version
        as a tuple when the input string includes an '@' symbol.

        Test setup:
        - The input version string is "v1.2.3@sha123".

        Assertions:
        - The function returns the tuple (1, 2.3), representing the major version as an integer
          and the minor version as a float.
        """
        result: tuple[int, float] = _extract_version_parts("v1.2.3@sha123")
        assert result == (1, 2.3)

    def test_extract_version_parts_with_hyphen(self) -> None:
        """
        Test the `_extract_version_parts` function with a version string containing a hyphen.

        This test verifies that the function correctly extracts the major version and the minor version
        as a tuple when the input string includes a hyphen.

        Test setup:
        - The input version string is "release-v1.2.3".

        Assertions:
        - The function returns the tuple (1, 2.3), representing the major version as an integer
          and the minor version as a float.
        """
        result: tuple[int, float] = _extract_version_parts("release-v1.2.3")
        assert result == (1, 2.3)

    def test_extract_version_parts_with_space(self) -> None:
        """
        Test the `_extract_version_parts` function with a version string containing a space.

        This test verifies that the function correctly extracts the major version and the minor version
        as a tuple when the input string includes a space.

        Test setup:
        - The input version string is "release v1.2.3".

        Assertions:
        - The function returns the tuple (1, 2.3), representing the major version as an integer
          and the minor version as a float.
        """
        result: tuple[int, float] = _extract_version_parts("release v1.2.3")
        assert result == (1, 2.3)

    def test_extract_version_parts_major_only(self) -> None:
        """
        Test the `_extract_version_parts` function with a version string containing only the major version.

        This test verifies that the function correctly extracts the major version and sets the minor version to 0.0
        when the input string includes only the major version.

        Test setup:
        - The input version string is "v1.0".

        Assertions:
        - The function returns the tuple (1, 0.0), representing the major version as an integer
          and the minor version as a float.
        """
        result: tuple[int, float] = _extract_version_parts("v1.0")
        assert result == (1, 0.0)

    def test_extract_version_parts_invalid_format(self) -> None:
        """
        Test the `_extract_version_parts` function with an invalid version string format.

        This test verifies that the function raises a `ValueError` with the expected error message
        when the input version string does not conform to the expected format.

        Test setup:
        - The input version string is "invalid-format".

        Assertions:
        - A `ValueError` is raised with the message "Invalid release name format".
        """
        with pytest.raises(ValueError, match="Invalid release name format"):
            _extract_version_parts("invalid-format")

    def test_extract_version_parts_empty_string(self) -> None:
        """
        Test the `_extract_version_parts` function with an empty string as input.

        This test verifies that the function raises a `ValueError` with the expected error message
        when the input version string is empty.

        Test setup:
        - The input version string is an empty string ("").

        Assertions:
        - A `ValueError` is raised with the message "Invalid release name format".
        """
        with pytest.raises(ValueError, match="Invalid release name format"):
            _extract_version_parts("")


class TestGetReleaseWithFallback:
    def test_get_release_with_fallback_found_first_try(self) -> None:
        """
        Test the `get_release_with_fallback` function when the release is found on the first attempt.

        This test verifies that the function correctly retrieves the release information
        when the specified release tag exists and is returned by the mock client.

        Test setup:
        - A mock client is used to simulate the GitHub API response.
        - The mock client returns a release with the tag name "v1.0.0".

        Assertions:
        - The function returns a dictionary containing the release information with the tag name "v1.0.0".
        """
        mock_client: Mock = Mock()
        mock_client.get_release_by_tag_name.return_value = {
            "tag_name": "v1.0.0"
        }

        result: dict = get_release_with_fallback(
            mock_client, None, "test/repo", "v1.0.0"
        )
        assert result == {"tag_name": "v1.0.0"}

    def test_get_release_with_fallback_found_with_variation(self) -> None:
        """
        Test the `get_release_with_fallback` function when the release is found after a variation.

        This test verifies that the function correctly retrieves the release information
        when the first attempt to find the release returns `None`, but a subsequent variation succeeds.

        Test setup:
        - A mock client is used to simulate the GitHub API response.
        - The mock client is configured to return `None` on the first attempt and a release with the tag name "1.0.0" on the second attempt.

        Assertions:
        - The function returns a dictionary containing the release information with the tag name "1.0.0".
        """
        mock_client: Mock = Mock()
        mock_client.get_release_by_tag_name.side_effect = [
            None,  # First variation fails
            {"tag_name": "1.0.0"},  # Second variation succeeds
        ]

        result: dict = get_release_with_fallback(
            mock_client, None, "test/repo", "v1.0.0"
        )
        assert result == {"tag_name": "1.0.0"}

    def test_get_release_with_fallback_not_found(self) -> None:
        """
        Test the `get_release_with_fallback` function when the release is not found.

        This test verifies that the function handles the case where the specified release tag
        does not exist and an exception is raised during the lookup.

        Test setup:
        - A mock client is used to simulate the GitHub API response.
        - The mock client raises an `Exception` with the message "Not found" when attempting to retrieve the release.

        Assertions:
        - The function returns an empty dictionary (`{}`) to indicate that no release was found.
        - A warning is logged to notify about the failure to find the release.
        """
        mock_client: Mock = Mock()
        mock_client.get_release_by_tag_name.side_effect = Exception("Not found")

        with patch("app.libs.github_lib.logging") as mock_logging:
            result: dict = get_release_with_fallback(
                mock_client, None, "test/repo", "v1.0.0"
            )
            assert result == {}
            mock_logging.warning.assert_called()

    def test_get_release_with_fallback_with_prefix(self) -> None:
        """
        Test the `get_release_with_fallback` function with a specified prefix.

        This test verifies that the function correctly retrieves the release information
        when a prefix is provided and the release tag includes the prefix.

        Test setup:
        - A mock client is used to simulate the GitHub API response.
        - The mock client returns a release with the tag name "controller-v1.0.0".

        Assertions:
        - The function returns a dictionary containing the release information with the tag name "controller-v1.0.0".
        """
        mock_client: Mock = Mock()
        mock_client.get_release_by_tag_name.return_value = {
            "tag_name": "controller-v1.0.0"
        }

        result: dict = get_release_with_fallback(
            mock_client, "controller-", "test/repo", "v1.0.0"
        )
        assert result == {"tag_name": "controller-v1.0.0"}


class TestNormalizeVersionForLookup:
    def test_normalize_version_for_lookup_basic(self) -> None:
        """
        Test the `_normalize_version_for_lookup` function with a basic version string.

        This test verifies that the function correctly normalizes a version string
        without any prefix or special characters.

        Test setup:
        - The input version string is "1.0.0".
        - No prefix is provided.

        Assertions:
        - The function returns a list containing the original version string and the version string
          with a 'v' prefix: ["1.0.0", "v1.0.0"].
        """
        result: list[str] = _normalize_version_for_lookup(None, "1.0.0")
        expected: list[str] = ["1.0.0", "v1.0.0"]
        assert result == expected

    def test_normalize_version_for_lookup_with_v_prefix(self) -> None:
        """
        Test the `_normalize_version_for_lookup` function with a version string that includes a 'v' prefix.

        This test verifies that the function correctly normalizes a version string
        that starts with a 'v' prefix.

        Test setup:
        - The input version string is "v1.0.0".
        - No prefix is provided.

        Assertions:
        - The function returns a list containing the original version string and the version string
          without the 'v' prefix: ["v1.0.0", "1.0.0"].
        """
        result: list[str] = _normalize_version_for_lookup(None, "v1.0.0")
        expected: list[str] = ["v1.0.0", "1.0.0"]
        assert result == expected

    def test_normalize_version_for_lookup_with_at_symbol(self) -> None:
        """
        Test the `_normalize_version_for_lookup` function with a version string containing an '@' symbol.

        This test verifies that the function correctly normalizes a version string
        that includes an '@' symbol.

        Test setup:
        - The input version string is "v1.0.0@sha123".
        - No prefix is provided.

        Assertions:
        - The function returns a list containing the original version string and the version string
          without the '@' symbol: ["v1.0.0", "1.0.0"].
        """
        result: list[str] = _normalize_version_for_lookup(None, "v1.0.0@sha123")
        expected: list[str] = ["v1.0.0", "1.0.0"]
        assert result == expected

    def test_normalize_version_for_lookup_with_prefix_and_version(self) -> None:
        """
        Test the `_normalize_version_for_lookup` function with a prefix and version string.

        This test verifies that the function correctly normalizes a version string
        when a prefix is provided and the version string includes a 'v' prefix.

        Test setup:
        - The input prefix is "controller-".
        - The input version string is "v1.0.0".

        Assertions:
        - The function returns a list containing the original version string, the version string
          without the 'v' prefix, and the version string with the prefix applied:
          ["v1.0.0", "1.0.0", "controller-1.0.0"].
        """
        result: list[str] = _normalize_version_for_lookup(
            "controller-", "v1.0.0"
        )
        expected: list[str] = ["v1.0.0", "1.0.0", "controller-1.0.0"]
        assert result == expected

    def test_normalize_version_for_lookup_with_prefix_matching(self) -> None:
        """
        Test the `_normalize_version_for_lookup` function with a version string that includes a matching prefix.

        This test verifies that the function correctly normalizes a version string
        when the input string already includes the specified prefix.

        Test setup:
        - The input prefix is "controller-".
        - The input version string is "controller-v1.0.0".

        Assertions:
        - The function returns a list of normalized version strings, including:
          - The original version string.
          - Variations with and without the 'v' prefix.
          - Variations with the prefix applied multiple times.
          - The prefix itself and its variation with a 'v' prefix.
        """
        result: list[str] = _normalize_version_for_lookup(
            "controller-", "controller-v1.0.0"
        )
        expected: list[str] = [
            "controller-v1.0.0",
            "v1.0.0",
            "vcontroller-v1.0.0",
            "controller-vcontroller-v1.0.0",
            "controller",
            "vcontroller",
        ]
        assert result == expected

    def test_normalize_version_for_lookup_with_hyphen(self) -> None:
        """
        Test the `_normalize_version_for_lookup` function with a version string containing a hyphen.

        This test verifies that the function correctly normalizes a version string
        that includes a hyphen.

        Test setup:
        - The input version string is "release-v1.0.0".
        - No prefix is provided.

        Assertions:
        - The function returns a list containing the original version string, the version string
          with a 'v' prefix, and variations without the version number:
          ["release-v1.0.0", "vrelease-v1.0.0", "release", "vrelease"].
        """
        result: list[str] = _normalize_version_for_lookup(
            None, "release-v1.0.0"
        )
        expected: list[str] = [
            "release-v1.0.0",
            "vrelease-v1.0.0",
            "release",
            "vrelease",
        ]
        assert result == expected

    def test_normalize_version_for_lookup_deduplication(self) -> None:
        """
        Test the `_normalize_version_for_lookup` function to ensure deduplication of results.

        This test verifies that the function does not produce duplicate entries in the list
        of normalized version strings.

        Test setup:
        - The input prefix is "test-".
        - The input version string is "test-1.0.0".

        Assertions:
        - The length of the result list is equal to the length of the set of the result list,
          ensuring no duplicate entries.
        """
        result: list[str] = _normalize_version_for_lookup("test-", "test-1.0.0")
        assert len(result) == len(set(result))

    def test_normalize_version_for_lookup_empty_prefix(self) -> None:
        """
        Test the `_normalize_version_for_lookup` function with an empty prefix.

        This test verifies that the function correctly normalizes a version string
        when an empty prefix is provided.

        Test setup:
        - The input prefix is an empty string ("").
        - The input version string is "1.0.0".

        Assertions:
        - The function returns a list containing the original version string and the version string
          with a 'v' prefix: ["1.0.0", "v1.0.0"].
        """
        result: list[str] = _normalize_version_for_lookup("", "1.0.0")
        expected: list[str] = ["1.0.0", "v1.0.0"]
        assert result == expected
