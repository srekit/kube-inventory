import logging
import os
import shutil

PROMETHEUS_MULTIPROC_DIR = os.environ.get(
    "PROMETHEUS_MULTIPROC_DIR", "/tmp/prometheus_multiproc"
)
os.environ.setdefault("PROMETHEUS_MULTIPROC_DIR", PROMETHEUS_MULTIPROC_DIR)
from prometheus_client import CollectorRegistry  # noqa: E402
from prometheus_client.multiprocess import MultiProcessCollector  # noqa: E402


def get_registry() -> CollectorRegistry:
    """
    Create and return a Prometheus `CollectorRegistry` instance.

    This function initializes a new `CollectorRegistry` and attaches a
    `MultiProcessCollector` to it, enabling the collection of metrics
    in a multi-process environment.

    Returns:
        CollectorRegistry: The initialized Prometheus collector registry.
    """
    registry: CollectorRegistry = CollectorRegistry()
    MultiProcessCollector(registry)
    return registry


def init_storage(clean: bool = False) -> None:
    """
    Initialize the storage directory for Prometheus metrics.

    This function ensures that the directory specified by `PROMETHEUS_MULTIPROC_DIR`
    exists. If the `clean` parameter is set to True and the directory already exists,
    it will be deleted and recreated.

    Args:
        clean (bool): If True, the existing directory will be cleaned before initialization.
    """
    if clean and os.path.isdir(PROMETHEUS_MULTIPROC_DIR):
        logging.debug(
            "Cleaning PROMETHEUS_MULTIPROC_DIR: %s", PROMETHEUS_MULTIPROC_DIR
        )
        shutil.rmtree(PROMETHEUS_MULTIPROC_DIR, ignore_errors=True)
    os.makedirs(PROMETHEUS_MULTIPROC_DIR, exist_ok=True)
