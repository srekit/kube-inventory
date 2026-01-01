import os
import logging
from importlib.resources.abc import Traversable

import yaml
from importlib.resources import files
from pathlib import Path


def file_exists(file_path: str) -> bool:
    """Check if a file exists at the given path.
    Args:
        file_path (str): The path to the file to check.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    logging.debug(f"File {file_path} exists")
    if os.path.exists(file_path):
        return True
    else:
        logging.warning(f"File {file_path} does not exists")
        return False


def check_is_yaml(file_path: str) -> bool:
    """Check if a file exists and is in valid YAML format.
    Args:
        file_path (str): The path to the file to check.

    Returns:
        bool: True if the file exists and is valid YAML, False otherwise.
    """
    file_check: bool = file_exists(file_path=file_path)
    if file_check:
        try:
            with open(file=file_path, mode="r") as file:
                yaml.safe_load(file)
            logging.debug(f"File {file_path} is in yaml format")
            return True
        except yaml.YAMLError as e:
            logging.warning(f"File {file_path} is not in yaml format: {e}")
            return False
    else:
        return False


def get_bundled_config_path(filename: str) -> str:
    """Get the path to a bundled config file.

    Args:
        filename (str): Name of the config file (e.g., 'default_apps.yaml')

    Returns:
        str: Path to the config file as a string
    """
    try:
        config_file: Traversable = files("app.config.data").joinpath(filename)
        return str(config_file)
    except (ModuleNotFoundError, TypeError, AttributeError):
        return str(Path(__file__).parent.parent / "config" / "data" / filename)


def load_file(file_path: str) -> dict:
    """Load a YAML file and return its contents as a dictionary.
    Args:
        file_path (str): The path to the YAML file to load.

    Returns:
        dict: The contents of the YAML file as a dictionary, or empty dict if file cannot be loaded.
    """
    is_yaml: bool = check_is_yaml(file_path=file_path)
    if is_yaml:
        with open(file=file_path, mode="r") as file:
            apps: dict = yaml.safe_load(file)
        logging.debug(f"File {file_path} loaded successfully")
        return apps
    else:
        logging.warning(f"File {file_path} could not be loaded")
        return {}
