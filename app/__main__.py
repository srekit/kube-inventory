import logging
import threading

from argparse import Namespace
from typing import List

from app.clients.kube import KubernetesClient
from app.config.bootstrap import load_config
from app.monitoring.metrics import clear_metrics
from app.workflows import pods_inventory, process
from app.web.server import start_web_server
from app.web.workflows import get_inventory_json, run_inventory_loop


def main() -> None:
    """
    Main entry point of the application.

    This function initializes the application by loading the configuration,
    performing prerequisite checks, and executing the appropriate workflow
    based on the specified output mode.

    The function supports the following output modes:
    - "json" or "csv": Generates and outputs inventory data in the specified format.
    - "prometheus": Starts a Prometheus-compatible web server and periodically refreshes inventory data.
    - Unsupported modes result in an error log message.
    """
    args_values: Namespace = load_config()

    kube_client: KubernetesClient = KubernetesClient(
        kube_config_path=args_values.kube_config_path,
        kube_in_cluster=args_values.kube_in_cluster,
    )

    match args_values.output_mode:
        case "json" | "csv":
            logging.debug(
                f"Outputting data in {args_values.output_mode} format"
            )
            pods_inventoried: List[
                pods_inventory.PodsInventoried
            ] = process.generate(
                extra_apps_file_path=args_values.extra_apps_file_path,
                github_access_token=args_values.github_access_token,
                github_api_url=args_values.github_api_url,
                kube_client=kube_client,
            )
            process.output(
                output_mode=args_values.output_mode,
                output_dir=args_values.output_dir,
                pods=pods_inventoried,
            )
        case "prometheus":
            logging.debug(
                f"Outputting data in Prometheus format, refreshing every {args_values.output_refresh_interval_seconds} seconds"
            )

            clear_metrics()

            def _on_worker_start() -> None:
                t = threading.Thread(
                    target=run_inventory_loop,
                    args=(
                        args_values,
                        kube_client,
                    ),
                    daemon=True,
                    name="inventory-loop",
                )
                t.start()

            start_web_server(
                github_access_token=args_values.github_access_token,
                github_api_url=args_values.github_api_url,
                host=args_values.web_host,
                inventory_provider=get_inventory_json,
                kube_client=kube_client,
                on_worker_start=_on_worker_start,
                port=args_values.web_port,
            )
        case _:
            logging.error(f"Unsupported output mode: {args_values.output_mode}")


if __name__ == "__main__":
    main()
