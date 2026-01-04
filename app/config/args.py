import argparse
from argparse import ArgumentParser

from app.common.versions import get_version


def load_args(
    env_github_access_token: str, env_log_level: str
) -> argparse.Namespace:
    """
    Load and parse command-line arguments for the Kubernetes Inventory Tool CLI.

    This function combines multiple argument parsers, each responsible for a specific
    set of arguments, into a single parser. It then parses the command-line arguments
    and returns the resulting namespace.

    Args:
        env_github_access_token (str): The GitHub access token, typically provided as an
            environment variable.
        env_log_level (str): The logging level, typically provided as an environment variable.

    Returns:
        argparse.Namespace: A namespace containing the parsed command-line arguments.

    The function performs the following steps:
    1. Creates individual argument parsers for common, configuration, GitHub, Kubernetes,
       output, and web-related arguments.
    2. Combines these parsers as parents into a single `ArgumentParser` instance.
    3. Parses the command-line arguments using the combined parser.
    4. Returns the parsed arguments as a namespace.
    """
    common_general_parsers: ArgumentParser = general_parsers_common(
        env_log_level=env_log_level
    )
    config_general_parsers: ArgumentParser = general_parsers_config()
    github_general_parsers: ArgumentParser = general_parsers_github(
        env_github_access_token=env_github_access_token
    )
    kubernetes_general_parsers: ArgumentParser = general_parsers_kubernetes()
    output_general_parsers: ArgumentParser = general_parsers_output()
    web_general_parsers: ArgumentParser = general_parsers_web()

    parser = argparse.ArgumentParser(
        description="Kubernetes Inventory Tool CLI",
        parents=[
            common_general_parsers,
            config_general_parsers,
            github_general_parsers,
            kubernetes_general_parsers,
            output_general_parsers,
            web_general_parsers,
        ],
    )

    args = parser.parse_args()
    return args


def general_parsers_common(env_log_level: str) -> ArgumentParser:
    """
    Create an argument parser for common logging-related arguments.

    This function generates an `ArgumentParser` instance that includes a `--log-level`
    argument. The `--log-level` argument allows users to specify the logging level
    for the application, with a default value provided by the `env_log_level` parameter.

    Args:
        env_log_level (str): The default logging level, typically provided as an
            environment variable. If not provided, the argument becomes required.

    Returns:
        ArgumentParser: An `ArgumentParser` instance configured with the `--log-level` argument.
    """
    common_general_parsers: ArgumentParser = argparse.ArgumentParser(
        add_help=False
    )
    common_general_parsers.add_argument(
        "--log-level",
        type=str,
        default=env_log_level,
        required=False if env_log_level else True,
        choices="DEBUG INFO WARNING ERROR CRITICAL".split(),
        help="Logging level (environment variable: LOG_LEVEL, default: INFO)",
    )

    common_general_parsers.add_argument(
        "--version",
        action="version",
        version=f"kube-inventory {get_version()}",
        help="Show application version",
    )

    return common_general_parsers


def general_parsers_config() -> ArgumentParser:
    """
    Create an argument parser for configuration-related arguments.

    This function generates an `ArgumentParser` instance that includes arguments
    for specifying the paths to default and extra application configuration files.

    Returns:
        ArgumentParser: An `ArgumentParser` instance configured with the following arguments:
            --default-apps-file-path: Path to the default apps configuration file.
            --extra-apps-file-path: Path to the extra apps configuration file.
    """
    config_general_parsers: ArgumentParser = argparse.ArgumentParser(
        add_help=False
    )

    config_general_parsers.add_argument(
        "--extra-apps-file-path",
        type=str,
        default="config/extra_apps.yaml",
        required=False,
        help="Extra apps configuration file (default: extra_apps.yaml)",
    )

    return config_general_parsers


def general_parsers_github(env_github_access_token: str) -> ArgumentParser:
    """
    Create an argument parser for GitHub-related arguments.

    This function generates an `ArgumentParser` instance that includes arguments
    for specifying the GitHub access token and the GitHub API URL.

    Args:
        env_github_access_token (str): The default GitHub access token, typically provided
            as an environment variable. If not provided, the argument becomes required.

    Returns:
        ArgumentParser: An `ArgumentParser` instance configured with the following arguments:
            --github-access-token: The GitHub access token, required if not provided as an
                environment variable.
            --github-api-url: The GitHub API URL, with a default value of "https://api.github.com".
    """
    github_general_parsers: ArgumentParser = argparse.ArgumentParser(
        add_help=False
    )

    github_general_parsers.add_argument(
        "--github-access-token",
        type=str,
        default=env_github_access_token,
        required=False,
        help="GitHub access token (environment variable: GITHUB_ACCESS_TOKEN)",
    )

    github_general_parsers.add_argument(
        "--github-api-url",
        type=str,
        default="https://api.github.com",
        required=False,
        help="GitHub API URL (default: https://api.github.com)",
    )

    return github_general_parsers


def general_parsers_kubernetes() -> ArgumentParser:
    """
    Create an argument parser for Kubernetes-related arguments.

    This function generates an `ArgumentParser` instance that includes an argument
    for specifying the path to the Kubernetes configuration file.

    Returns:
        ArgumentParser: An `ArgumentParser` instance configured with the following argument:
            --kube-config-path: Path to the Kubernetes configuration file. If not provided,
                the in-cluster configuration will be used by default.
    """
    kubernetes_general_parsers: ArgumentParser = argparse.ArgumentParser(
        add_help=False
    )

    kubernetes_general_parsers.add_argument(
        "--kube-config-path",
        type=str,
        default="~/.kube/config",
        required=False,
        help="Path to the Kubernetes configuration file (default: ~/.kube/config)",
    )

    kubernetes_general_parsers.add_argument(
        "--kube-in-cluster",
        type=str,
        default=False,
        required=False,
        help="Use in-cluster Kubernetes configuration (default: False)",
    )

    return kubernetes_general_parsers


def general_parsers_output() -> ArgumentParser:
    """
    Create an argument parser for output-related arguments.

    This function generates an `ArgumentParser` instance that includes arguments
    for specifying the output directory, output format, and refresh interval for
    the inventory content.

    Returns:
        ArgumentParser: An `ArgumentParser` instance configured with the following arguments:
            --output-dir: Directory to output inventory content, with a default value of "inv_data".
            --output-mode: Format of the output, with options including "json", "yaml", "csv",
                and "prometheus". The default format is "json".
            --output-refresh-interval-seconds: Refresh interval in seconds for the output,
                with a default value of 600 seconds.
    """
    output_general_parsers: ArgumentParser = argparse.ArgumentParser(
        add_help=False
    )

    output_general_parsers.add_argument(
        "--output-dir",
        type=str,
        default="inv_data",
        required=False,
        help="Directory to output inventory content (default: inv_data)",
    )

    output_general_parsers.add_argument(
        "--output-mode",
        type=str,
        default="json",
        required=False,
        choices=["json", "yaml", "csv", "prometheus"],
        help="Output format (default: json)",
    )

    output_general_parsers.add_argument(
        "--output-refresh-interval-seconds",
        type=int,
        default=600,
        required=False,
        help="Refresh interval in seconds for output (default: 600)",
    )

    return output_general_parsers


def general_parsers_web() -> ArgumentParser:
    """
    Create an argument parser for web server-related arguments.

    This function generates an `ArgumentParser` instance that includes arguments
    for specifying the web server host and port.

    Returns:
        ArgumentParser: An `ArgumentParser` instance configured with the following arguments:
            --web-host: The host address for the web server, with a default value of "0.0.0.0".
            --web-port: The port number for the web server, with a default value of 8080.
    """
    web_general_parsers: ArgumentParser = argparse.ArgumentParser(
        add_help=False
    )

    web_general_parsers.add_argument(
        "--web-host",
        type=str,
        default="0.0.0.0",
        required=False,
        help="Web server host (default: 0.0.0.0)",
    )

    web_general_parsers.add_argument(
        "--web-port",
        type=int,
        default=8080,
        required=False,
        help="Web server port (default: 8080)",
    )

    return web_general_parsers
