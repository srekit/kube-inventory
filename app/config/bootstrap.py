import argparse

from app.config import args, os_envs, log_settings


def load_config() -> argparse.Namespace:
    """
    Load the application configuration.

    This function retrieves environment variables, loads command-line arguments,
    and sets up logging based on the provided log level.

    The function performs the following steps:
    1. Loads environment variables using `os_envs.load_envs`.
    2. Loads command-line arguments using `args.load_args`, passing the GitHub access token
       and log level from the loaded environment variables.
    3. Configures logging using the log level from the loaded arguments.

    Returns:
        argparse.Namespace: The parsed arguments containing the application configuration.
    """
    app_envs: dict = os_envs.load_envs()
    args_values: argparse.Namespace = args.load_args(
        env_github_access_token=app_envs["GITHUB"]["access_token"],
        env_log_level=app_envs["LOG"]["log_level"],
    )

    log_settings.setup_logging(log_level_str=args_values.log_level)

    return args_values
