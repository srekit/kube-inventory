import logging
import sys
import yaml

from typing import Optional


def load_app_configs(
        default_apps_file_path: str,
        extra_apps_file_path: Optional[str] = None
) -> dict:
    """Load application configurations from YAML files.
    Loads a default apps configuration file and optionally merges it with
    an extra apps configuration file.

    Args:
        default_apps_file_path: Path to the default apps configuration YAML file.
        extra_apps_file_path: Optional path to an extra apps configuration YAML file
            that will be merged with the default configuration.

    Returns:
        A dictionary containing the merged application configuration.

    Raises:
        SystemExit: If the default apps configuration file is not found.
    """
    try:
        with open(default_apps_file_path, 'r') as f:
            logging.debug(f"Loading default apps configuration from {default_apps_file_path}")
            config: dict = yaml.safe_load(f)
    except FileNotFoundError:
        logging.error(f"Default apps configuration file not found: {default_apps_file_path}")
        sys.exit(1)

    if extra_apps_file_path:
        try:
            with open(extra_apps_file_path, 'r') as f:
                logging.debug(f"Loading extra apps configuration from {extra_apps_file_path}")
                extra_config: dict = yaml.safe_load(f)

                if extra_config and 'apps' in extra_config:
                    logging.debug("Merging extra apps configuration into default apps configuration")
                    config['apps'].update(extra_config['apps'])
        except FileNotFoundError:
            logging.warning(f"Extra apps configuration file not found: {extra_apps_file_path}")

    return config
