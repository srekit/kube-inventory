import logging
from typing import Any, Optional

from app.clients import github


def count_releases_between(
    github_client: github.GithubClient,
    repo_name: str,
    current_release_name: str,
) -> int:
    """
    Count the number of releases between the current release and the latest release.

    This function retrieves the list of releases for a given repository and filters
    them based on their version numbers. It calculates the number of releases between
    the specified current release and the latest release in the repository.

    Args:
        github_client (github.GithubClient): The GitHub client used to interact with the repository.
        repo_name (str): The name of the repository to fetch releases from.
        current_release_name (str): The name of the current release to compare against.

    Returns:
        int: The number of releases between the current release and the latest release.
             Returns -1 if the current release is not found in the repository.

    Raises:
        ValueError: If a release name has an invalid format and cannot be parsed.

    Notes:
        - Releases with invalid version formats are skipped with a warning.
        - The function assumes that release names follow a semantic versioning pattern.
    """
    current_major_version, current_minor_version = _extract_version_parts(
        current_release_name
    )
    releases: list[Any] | None = github_client.list_releases(repo_name)

    if not releases:
        logging.warning(f"No releases found for repository {repo_name}.")
        return -1

    filtered_releases: list[dict] = []
    for release in releases:
        try:
            major_version, minor_version = _extract_version_parts(
                release["name"]
            )
            if major_version > current_major_version or (
                major_version == current_major_version
                and minor_version >= current_minor_version
            ):
                filtered_releases.append(release)
        except ValueError:
            logging.warning(
                f"Skipping release with invalid format: {release['name']}"
            )

    release_names: list[str] = [
        release["name"] for release in filtered_releases
    ]

    if current_release_name not in release_names:
        logging.warning(
            f"Current release {current_release_name} not found in the repository {repo_name}."
        )
        return -1

    latest_release_name: str = release_names[0]
    current_index: int = release_names.index(current_release_name)
    latest_index: int = release_names.index(latest_release_name)

    return abs(latest_index - current_index)


def _extract_version_parts(release_name: str) -> tuple[int, float]:
    """
    Extract the major and minor version parts from a release name.

    This function parses a release name to extract the major and minor version
    numbers. It supports various formats, including those prefixed with "v" or
    containing delimiters such as spaces or hyphens. If the release name does not
    conform to a valid version format, a ValueError is raised.

    Args:
        release_name (dict): The release name to parse.

    Returns:
        tuple[int, float]: A tuple containing the major version as an integer and
        the minor version as a float.

    Raises:
        ValueError: If the release name format is invalid.
    """

    def parse(name: str) -> tuple[int, float]:
        """
        Parse the release name to extract version parts.

        This helper function splits the release name into parts using delimiters
        and identifies the version components. It handles cases where the version
        is prefixed with "v" or contains multiple delimiters.

        Args:
            name (str): The release name to parse.

        Returns:
            tuple[int, float]: The major and minor version numbers.

        Raises:
            ValueError: If the release name format is invalid.
        """
        if "@" in name:
            name = name.split("@")[0]

        parts: list = []
        for delimiter in [" ", "-"]:
            for part in name.split(delimiter):
                parts.append(part)

        for part in parts:
            if part.startswith("v") and len(part) > 1:
                numeric_version = part[1:]
                if _is_valid_version(numeric_version):
                    major_version = int(numeric_version.split(".")[0])
                    minor_parts = numeric_version.split(".")[1:3]
                    minor_version = (
                        float(".".join(minor_parts)) if minor_parts else 0.0
                    )
                    return major_version, minor_version

            elif _is_valid_version(part):
                major_version = int(part.split(".")[0])
                minor_parts = part.split(".")[1:3]
                minor_version = (
                    float(".".join(minor_parts)) if minor_parts else 0.0
                )
                return major_version, minor_version

        raise ValueError(f"Invalid release name format: {name}")

    def _is_valid_version(version_str: str) -> bool:
        """
        Check if a version string is valid.

        This helper function validates a version string by ensuring it contains
        at least two numeric components separated by dots.

        Args:
            version_str (str): The version string to validate.

        Returns:
            bool: True if the version string is valid, False otherwise.
        """
        if not version_str:
            return False
        parts = version_str.split(".")
        return len(parts) >= 2 and all(part.isdigit() for part in parts)

    try:
        return parse(str(release_name))
    except ValueError:
        raise ValueError(f"Invalid release name format: {release_name}")


def get_release_with_fallback(
    github_client: github.GithubClient,
    prefix: Optional[str],
    repo_name: str,
    tag_name: str,
) -> dict:
    """
    Retrieve a release from a GitHub repository, trying multiple version formats as fallbacks.

    This function attempts to find a release in the specified repository by trying
    different variations of the provided tag name. If a release is found using any
    of the variations, it is returned. If no release is found, an empty dictionary
    is returned, and a warning is logged.

    Args:
        github_client (github.GithubClient): The GitHub client used to interact with the repository.
        prefix (Optional[str]): An optional prefix to prepend or match against the tag name.
        repo_name (str): The name of the repository to search for the release.
        tag_name (str): The tag name of the release to look up.

    Returns:
        dict: The release data if found, otherwise an empty dictionary.

    Notes:
        - The function generates multiple variations of the tag name using the `_normalize_version_for_lookup` helper.
        - If a release is found using any variation, it is returned immediately.
        - Logs debug messages for each attempted version format and a warning if no release is found.
    """
    version_variations: list[str] = _normalize_version_for_lookup(
        prefix=prefix, version=tag_name
    )

    for version in version_variations:
        try:
            release: dict = github_client.get_release_by_tag_name(
                repo_name=repo_name, tag_name=version
            )
            if release:
                logging.debug(
                    f"Found release for {repo_name} using version format: {version}"
                )
                return release
        except Exception as e:
            logging.debug(f"Version {version} not found for {repo_name}: {e}")
            continue

    logging.warning(
        f"No release found for {repo_name} with any version format of: {', '.join(version_variations)}"
    )
    return {}


def _normalize_version_for_lookup(
    prefix: Optional[str], version: str
) -> list[str]:
    """
    Generate a list of version variations for lookup purposes.

    This function creates multiple variations of a given version string to account
    for different possible formats. It handles prefixes, version prefixes (e.g., "v"),
    and delimiters such as '@' and '-'. The variations are deduplicated before being returned.

    Args:
        prefix (Optional[str]): An optional prefix to prepend or match against the version.
        version (str): The version string to normalize.

    Returns:
        list[str]: A list of deduplicated version variations.
    """
    if "@" in version:
        version = version.split("@", 1)[0]

    variations: list[str] = [version]

    if prefix and version.startswith(prefix):
        base_version = version[len(prefix) :]
        variations.append(base_version)

        if not base_version.startswith("v"):
            variations.append(f"v{base_version}")
            variations.append(f"{prefix}v{base_version}")

    if not version.startswith("v"):
        variations.append(f"v{version}")

    if version.startswith("v"):
        variations.append(version[1:])

    if prefix:
        if version.startswith("v"):
            # For controller-v1.13.0, also try controller-1.13.0 and v1.13.0
            clean_version = version[1:]  # Remove 'v'
            variations.append(f"{prefix}{clean_version}")
            variations.append(version)  # Keep original v1.13.0
        else:
            variations.append(f"{prefix}v{version}")

    if "-" in version:
        base_version = version.rsplit("-", 1)[0]
        variations.append(base_version)
        if not base_version.startswith("v"):
            variations.append(f"v{base_version}")

    return list(dict.fromkeys(variations))
