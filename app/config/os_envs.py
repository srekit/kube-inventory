import os


def load_envs() -> dict:
    """
    Load environment variables and return them as a dictionary.

    This function retrieves environment variables for the application, including
    GitHub access tokens and logging configuration. Default values are used if
    the environment variables are not set.

    Returns:
        dict: A dictionary containing the environment variables grouped by category.
        - "GITHUB": Contains the GitHub access token.
            - "access_token": The GitHub access token (default: an empty string).
        - "LOG": Contains the logging configuration.
            - "log_level": The logging level (default: "INFO").
    """
    return {
        "GITHUB": {
            "access_token": os.getenv("GITHUB_ACCESS_TOKEN", ""),
        },
        "LOG": {
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
        },
    }
