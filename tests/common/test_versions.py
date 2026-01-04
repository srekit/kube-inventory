import unittest
from pathlib import Path
from unittest.mock import mock_open, patch
from app.common.versions import get_version


class TestGetVersion(unittest.TestCase):
    def test_get_version_returns_correct_version(self) -> None:
        """Test that get_version returns the version from pyproject.toml."""
        mock_toml_content = b"""
[tool.poetry]
name = "kube-inventory"
version = "1.0.0"
description = "Test description"
"""

        with patch("builtins.open", mock_open(read_data=mock_toml_content)):
            with patch(
                "pathlib.Path.__truediv__", return_value=Path("pyproject.toml")
            ):
                version = get_version()
                self.assertEqual(version, "1.0.0")

    def test_get_version_with_different_version(self) -> None:
        """Test get_version with a different version number."""
        mock_toml_content = b"""
[tool.poetry]
version = "2.5.3"
"""

        with patch("builtins.open", mock_open(read_data=mock_toml_content)):
            with patch(
                "pathlib.Path.__truediv__", return_value=Path("pyproject.toml")
            ):
                version = get_version()
                self.assertEqual(version, "2.5.3")

    def test_get_version_file_not_found(self) -> None:
        """Test that get_version raises FileNotFoundError when file doesn't exist."""
        with patch("builtins.open", side_effect=FileNotFoundError):
            with self.assertRaises(FileNotFoundError):
                get_version()


if __name__ == "__main__":
    unittest.main()
