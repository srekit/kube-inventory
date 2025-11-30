from flask import Flask
from typing import Callable, Optional, Any

import logging

from app.endpoints.health import health_endpoint
from app.endpoints.metrics import metrics_endpoint
from app.endpoints.root import root_endpoint


def _create_app(
        default_apps_file_path: Optional[str] = None,
        extra_apps_file_path: Optional[str] = None,
        github_access_token: Optional[str] = None,
        github_api_url: Optional[str] = None,
        inventory_provider: Optional[list[dict]] = None
) -> Flask:
    """
    Create and configure a Flask application instance.

    This function initializes a Flask app, sets its configuration, and registers
    URL routes for the root, metrics, and health endpoints.

    Args:
        default_apps_file_path (Optional[str]): Path to the default applications file.
        extra_apps_file_path (Optional[str]): Path to the extra applications file.
        github_access_token (Optional[str]): GitHub access token for API authentication.
        github_api_url (Optional[str]): URL of the GitHub API.
        inventory_provider (Optional[list[dict]]): Inventory provider configuration.

    Returns:
        Flask: The configured Flask application instance.
    """
    app: Flask = Flask(__name__)
    app.config['INVENTORY_PROVIDER'] = inventory_provider
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.config['JSON_SORT_KEYS'] = False
    app.config['JSONIFY_MIMETYPE'] = 'application/json'
    app.json.compact = False
    app.add_url_rule('/', 'root', root_endpoint, methods=['GET'])
    app.add_url_rule('/metrics','metrics', metrics_endpoint, methods=['GET'])

    app.add_url_rule(
        '/health',
        'health',
        lambda: health_endpoint(
            default_apps_file_path=default_apps_file_path,
            extra_apps_file_path=extra_apps_file_path,
            github_access_token=github_access_token,
            github_api_url=github_api_url
        ),
        methods=['GET']
    )

    return app


application: Flask = _create_app()
def start_web_server(
        default_apps_file_path: str,
        extra_apps_file_path: str,
        github_access_token: str,
        github_api_url: str,
        host: str,
        port: int,
        inventory_provider,
        on_worker_start: Optional[Callable[[], None]] = None,
) -> None:
    """
    Start the web server using Gunicorn.

    This function initializes the Flask application and starts a Gunicorn WSGI server
    to serve the application. It supports custom configurations for the server and
    allows for background tasks to be executed when workers start.

    Args:
        default_apps_file_path (str): Path to the default applications file.
        extra_apps_file_path (str): Path to the extra applications file.
        github_access_token (str): GitHub access token for API authentication.
        github_api_url (str): URL of the GitHub API.
        host (str): Host address to bind the server.
        port (int): Port number to bind the server.
        inventory_provider: Configuration for the inventory provider.
        on_worker_start (Optional[Callable[[], None]]): Callback function to execute
            when a Gunicorn worker starts.

    Raises:
        ImportError: If Gunicorn is not installed.
    """
    global application
    application = _create_app(
        default_apps_file_path=default_apps_file_path,
        extra_apps_file_path=extra_apps_file_path,
        github_access_token=github_access_token,
        github_api_url=github_api_url,
        inventory_provider=inventory_provider
    )
    try:
        from gunicorn.app.wsgiapp import WSGIApplication
        class StandaloneApplication(WSGIApplication):
            def __init__(self, app, custom_options=None):
                self.options = custom_options or {}
                self.application = app
                super().__init__()


            def load_config(self) -> None:
                for key, value in self.options.items():
                    if key in self.cfg.settings and value is not None:
                        self.cfg.set(key.lower(), value)


            def load(self) -> None:
                return self.application


        def _post_fork(server, worker) -> None:
            logging.info("Gunicorn worker booted (pid=%s). Starting background tasks...", worker.pid)
            if on_worker_start:
                try:
                    on_worker_start()
                except Exception as error:
                    logging.exception("on_worker_start failed : %s", error)


        def _child_exit(server, worker) -> None:
            try:
                from prometheus_client import multiprocess
                multiprocess.mark_process_dead(worker.pid)
            except Exception as error:
                logging.exception("Failed to mark worker pid dead for Prometheus at exit: %s", error)
            logging.info("Gunicorn worker booted (pid=%s). Starting background tasks...", worker.pid)
            if on_worker_start:
                try:
                    on_worker_start()
                except Exception as error:
                    logging.exception("on_worker_start failed: %s", error)

        options: dict[str, Any] = {
            'bind': f'{host}:{port}',
            'workers': 1,
            'worker_class': 'sync',
            'timeout': 120,
            'keepalive': 5,
            'max_requests': 1000,
            'max_requests_jitter': 100,
            "post_fork": _post_fork,
            "child_exit": _child_exit,
        }

        logging.info(f"Starting WSGI server on {host}:{port}")
        StandaloneApplication(app=application, custom_options=options).run()

    except ImportError as e:
        logging.error("Gunicorn is required but not installed. Install with: pip install gunicorn")
        raise e
