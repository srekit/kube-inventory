import json
import logging

from dataclasses import dataclass
from datetime import datetime

from kubernetes.client.models.v1_pod_list import V1PodList
from typing import List, Optional

from app.clients.github import GithubClient
from app.clients.kube import KubernetesClient
from app.common import file_check
from app.common.config_files import load_app_configs
from app.common.file_check import get_bundled_config_path
from app.libs import github_lib, kube_lib


@dataclass
class PodsInventoried:
    container_name: str
    current_release_date: str
    current_release_name: str
    current_release_timestamp: int
    latest_release_date: str
    latest_release_name: str
    latest_release_timestamp: int
    name: str
    namespace: str
    repo: str
    silenced: bool
    versions_to_latest_release: int


@dataclass
class VersionsInfo:
    current_release_date: str
    current_release_name: str
    current_release_timestamp: int
    latest_release_date: str
    latest_release_name: str
    latest_release_timestamp: int
    versions_to_latest_release: int


def generate(
    extra_apps_file_path: str,
    github_access_token: Optional[str],
    github_api_url: str,
    kube_client: KubernetesClient,
) -> List[PodsInventoried]:
    github_client: GithubClient = GithubClient(
        github_access_token=github_access_token, github_api_url=github_api_url
    )

    file_check.load_file(file_path=get_bundled_config_path("default_apps.yaml"))
    file_check.load_file(file_path=extra_apps_file_path)

    kube_pods: V1PodList = kube_client.list_pods()
    logging.info(f"Found {len(kube_pods.items)} pods in the cluster")

    pods: list[dict] = kube_lib.list_json(kube_pods)
    logging.debug(f"Pods data: {json.dumps(pods, indent=2)}")

    app_configs: dict = load_app_configs(
        default_apps_file_path="default_apps.yaml",
        extra_apps_file_path=extra_apps_file_path,
    )

    pods_inventoried: List[PodsInventoried] = []
    pods_inventoried_count: int = 0
    for pod in pods:
        pod_annotations: dict = pod["annotations"]
        pod_labels: dict = pod["labels"]
        for app_name, app_config in app_configs.get("apps", {}).items():
            label_key: str = app_config.get("label_key")
            label_value: str = app_config.get("label_value")

            if label_key in pod_labels and pod_labels[label_key] == label_value:
                silenced: bool = False
                if pod_annotations and isinstance(pod_annotations, dict):
                    silenced = (
                        pod_annotations.get("kube-inventory/silenced") == "true"
                    )

                    if pod_annotations.get("kube-inventory/exclude") == "true":
                        logging.info(
                            f"Pod {pod['name']} in namespace {pod['namespace']} is marked as excluded from inventory"
                        )
                        continue

                container_name: str = app_config.get("container_name", app_name)
                container_found: bool = any(
                    container_name == container["name"]
                    for container in pod["containers"]
                )

                if container_found:
                    logging.debug(
                        f"Container name {container_name} found in pod {pod['name']}"
                    )
                    container: dict = next(
                        (
                            c
                            for c in pod["containers"]
                            if container_name == c["name"]
                        ),
                        {},
                    )

                    container_image_tag: str
                    if app_config.get("prefix"):
                        container_image_tag = f"{app_config.get('prefix')}{container['image'].split(':')[1]}"
                    else:
                        container_image_tag = container["image"].split(":")[1]
                        if "@" in container_image_tag:
                            container_image_tag = container_image_tag.split(
                                "@"
                            )[0]

                    versions_info_output: VersionsInfo | None = _versions_info(
                        current_release_name=container_image_tag,
                        github_client=github_client,
                        prefix=app_config.get("prefix"),
                        repo=app_config.get("repo"),
                    )

                    if versions_info_output:
                        pod_inventoried: PodsInventoried = _inventory_pod(
                            container_name=container_name,
                            pod_name=pod["name"],
                            pod_namespace=pod["namespace"],
                            repo=app_config.get("repo"),
                            silenced=silenced,
                            versions_config=versions_info_output,
                        )
                        pods_inventoried.append(pod_inventoried)
                        pods_inventoried_count += 1
                        logging.info(
                            f"Pod {pod['name']} in namespace {pod['namespace']} inventoried for app {app_name}"
                        )
                    else:
                        logging.warning(
                            f"Skipping pod {pod['name']} due to missing versions info"
                        )
                else:
                    logging.error(
                        f"Container name {app_config.get('container_name')} not found in any container of pod {pod['name']}"
                    )
                    break

    logging.info(f"Total of {pods_inventoried_count} pods inventoried")
    return pods_inventoried


def _inventory_pod(
    container_name: str,
    pod_name: str,
    pod_namespace: str,
    repo: str,
    silenced: bool,
    versions_config: VersionsInfo,
) -> PodsInventoried:
    pod_inventoried: PodsInventoried = PodsInventoried(
        container_name=container_name,
        current_release_date=versions_config.current_release_date,
        current_release_name=versions_config.current_release_name,
        current_release_timestamp=versions_config.current_release_timestamp,
        latest_release_date=versions_config.latest_release_date,
        latest_release_name=versions_config.latest_release_name,
        latest_release_timestamp=versions_config.latest_release_timestamp,
        name=pod_name,
        namespace=pod_namespace,
        repo=repo,
        silenced=silenced,
        versions_to_latest_release=versions_config.versions_to_latest_release,
    )
    logging.debug(f"Pod inventoried: {pod_inventoried}")

    return pod_inventoried


def _versions_info(
    current_release_name: str,
    github_client: GithubClient,
    prefix: Optional[str],
    repo: str,
) -> Optional[VersionsInfo]:
    current_release: dict = github_lib.get_release_with_fallback(
        github_client=github_client,
        prefix=prefix,
        repo_name=repo,
        tag_name=current_release_name,
    )

    if current_release:
        current_release_date: str = current_release.get("published_at", "")
        current_release_timestamp: int = int(
            datetime.fromisoformat(
                current_release.get("published_at", "").replace("Z", "+00:00")
            ).timestamp()
        )
        latest_release: dict = github_client.get_latest_release(repo_name=repo)
        latest_release_name: str = latest_release.get("tag_name", "")
        latest_release_date: str = latest_release.get("published_at", "")
        latest_release_timestamp: int = int(
            datetime.fromisoformat(
                latest_release.get("published_at", "").replace("Z", "+00:00")
            ).timestamp()
        )

        current_release_name_str: str = current_release.get("name", "")
        if not current_release_name_str:
            logging.warning(
                f"Current release has no name for {current_release_name}"
            )
            return None

        versions_to_latest_release: int = github_lib.count_releases_between(
            github_client=github_client,
            repo_name=repo,
            current_release_name=current_release_name_str,
        )

        pod_versions_info: VersionsInfo = VersionsInfo(
            current_release_date=current_release_date,
            current_release_name=current_release_name_str,
            current_release_timestamp=current_release_timestamp,
            latest_release_date=latest_release_date,
            latest_release_name=latest_release_name,
            latest_release_timestamp=latest_release_timestamp,
            versions_to_latest_release=versions_to_latest_release,
        )

        return pod_versions_info
    else:
        logging.warning(f"No versions info for {current_release_name}")
        return None
