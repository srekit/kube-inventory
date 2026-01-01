import logging
import sys
from typing import Optional, List

from app.clients.kube import KubernetesClient
from app.common import file_operations
from app.workflows import outputs, pods_inventory


def generate(
    extra_apps_file_path: str,
    github_access_token: Optional[str],
    github_api_url: str,
    kube_client: KubernetesClient,
) -> List[pods_inventory.PodsInventoried]:
    """
    Generates a list of `PodsInventoried` objects based on the provided application files
    and GitHub configuration.

    This function uses the `pods_inventory.generate` method to process the default and
    extra application files, along with optional GitHub access credentials and Kubernetes
    configuration, to produce an inventory of pods.

    Args:
        extra_apps_file_path (str): Path to the extra applications file.
        github_access_token (Optional[str]): GitHub access token for authentication (if required).
        github_api_url (str): URL of the GitHub API.
        kube_client (KubernetesClient): Kubernetes client.

    Returns:
        List[pods_inventory.PodsInventoried]: A list of `PodsInventoried` objects representing
        the generated pod inventory.
    """
    pods_inventoried: List[
        pods_inventory.PodsInventoried
    ] = pods_inventory.generate(
        extra_apps_file_path=extra_apps_file_path,
        github_access_token=github_access_token,
        github_api_url=github_api_url,
        kube_client=kube_client,
    )
    return pods_inventoried


def output(
    pods: List[pods_inventory.PodsInventoried],
    output_dir: str,
    output_mode: str,
) -> None:
    """
    Outputs the inventory of pods to a file in the specified format.

    This function generates an output file containing the pod inventory in either
    CSV or JSON format, based on the provided `output_mode`. The file is saved
    in the specified `output_dir`. If an unsupported `output_mode` is provided,
    the function logs an error and exits the program.

    Args:
        pods (List[pods_inventory.PodsInventoried]): A list of `PodsInventoried` objects
            representing the pod inventory.
        output_dir (str): The directory where the output file will be saved.
        output_mode (str): The format of the output file. Supported values are:
            - "csv": Outputs the inventory as a CSV file.
            - "json": Outputs the inventory as a JSON file.

    Raises:
        SystemExit: If an unsupported `output_mode` is provided.
    """
    match output_mode:
        case "csv":
            csv_output: str = outputs.csv(pods)
            file_operations.content_to_file(
                file_path=f"{output_dir}/inventory.csv", content=csv_output
            )
        case "json":
            json_output: list[dict] = outputs.json(pods)
            file_operations.content_to_file(
                file_path=f"{output_dir}/inventory.json", content=json_output
            )
        case _:
            logging.error(f"Unsupported output mode: {output_mode}")
            sys.exit(1)
