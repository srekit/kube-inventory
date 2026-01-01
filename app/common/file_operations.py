import json
import logging
import pathlib

from pathlib import Path
from typing import Union


def content_to_file(file_path: str, content: Union[str, list, dict]) -> None:
    """Write content to a file, creating parent directories if needed.
    Args:
        file_path: Path to the file where content will be written
        content: Content to write - can be string, list, or dict
    """
    path: pathlib.Path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w") as file:
        if isinstance(content, str):
            file.write(content)
        else:
            json.dump(content, file, indent=2)
        logging.info(f"Content written to {file_path}")
