import tomllib
from pathlib import Path
from typing import Any


def get_version() -> str:
    """
    Read the version from pyproject.toml.

    Returns:
        str: The version string from pyproject.toml.
    """
    pyproject_path: Path = (
        Path(__file__).parent.parent.parent / "pyproject.toml"
    )
    with open(pyproject_path, "rb") as f:
        pyproject_data: dict[str, Any] = tomllib.load(f)
    version: str = pyproject_data["tool"]["poetry"]["version"]
    return version
