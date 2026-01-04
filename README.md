# Kube Inventory

A tool to inventory and track software versions running in Kubernetes clusters, helping identify outdated applications that may need upgrades.


## Overview

Kube Inventory scans your Kubernetes cluster to identify running applications and compares their versions against the latest releases available in their GitHub repositories. This helps you quickly assess which applications need updates.


## Features

- **Multiple Output Formats**: Export inventory data as `json`, `csv` or expose via **Prometheus metrics**
- **GitHub Integration**: Automatically fetches latest release information from GitHub repositories
- **Kubernetes Native**: Works with standard `kubeconfig` or `in-cluster` configuration
- **Custom Application Support**: Extend the default application list with custom definitions
- **Prometheus Integration**: Expose metrics for monitoring and alerting
- **Web Interface**: Built-in web server for Prometheus mode


## Utilization

The tool can be run from the command line with various options to customize its behavior or 
by Kubernetes, and then generating Prometheus metrics for monitoring purposes.


### CLI Mode

![CLI Mode](docs/gifs/cli_mode.gif)

You can run Kube Inventory from the command line to generate inventory reports in your desired format. Use the `--output-mode` flag to specify the format (`json` or `csv`).

The installation can be easily done via pip:

```bash
pip install kube-inventory
```

Example command to run Kube Inventory in CLI mode:

```bash
kube-inventory
```

The reports will be saved in the default output directory specified by the argument `--output-dir`, which defaults to the current directory.

In this sample output, you can see the generation of the report in the `csv` format:

![CSV Output](docs/gifs/csv_format.gif)


### Prometheus Mode

You can also run Kube Inventory in Prometheus mode, where it exposes the inventory data as metrics via a built-in web server.
This allows you to integrate with Prometheus for monitoring and alerting.

You can specify the output mode as `prometheus` using the `--output-mode` flag, and them application will start a web server to expose the metrics in Prometheus format.

![Prometheus Mode](docs/gifs/prometheus_mode.gif)

In case you want to install Kube Inventory in a Kubernetes cluster, you can use the provided Helm chart available in 
the [srekit/helm-charts/kube-inventory](https://github.com/srekit/helm-charts/tree/main/charts/kube-inventory),

![Helm Chart Installation](docs/gifs/helm_install.gif)

You could also have the possibility to visualize the metrics using Grafana dashboards, besides trigger alerts using Prometheus rules.

![dashboard_overall_and_coverage](docs/images/dashboard_overall_and_coverage.png)

![dashboard_details](docs/images/dashboard_details.png)



## Command-Line Options

| Argument                            | Options                             | Description                                | Default                  |
|-------------------------------------|-------------------------------------|--------------------------------------------|--------------------------|
| --extra-apps-file-path              | Path to YAML file                   | Path to custom applications YAML file      | None                     |
| --github-access-token               | String                              | GitHub access token for API requests       | None                     |
| --github-api-url                    | URL                                 | Base URL for GitHub API                    | `https://api.github.com` |
| --kube-config-path                  | Path to kubeconfig file             | Path to the kubeconfig file to use         | `~/.kube/config`         |
| --kube-in-cluster                   | Boolean                             | Use in-cluster Kubernetes config           | `False`                  |
| --log-level                         | `debug`, `info`, `warning`, `error` | Logging level for the application          | `info`                   |
| --output-dir                        | Path to output directory            | Directory to save output files             | Current directory        |
| --output-mode                       | json, csv, prometheus               | Output format for the inventory data       | `json`                   |
| --output-refresh-interval-seconds   | Integer (seconds)                   | Refresh interval for Prometheus mode       | `300`                    |
| --version                           |                                     | Show application version and exit          |                          |
| --web-host                          | Hostname or IP                      | Host for the web server in Prometheus mode | `0.0.0.0`                |
| --web-port                          | Integer (port number)               | Port for the web server in Prometheus mode | `8080`                   |


## Environment Variables

The following environment variables can be used as alternatives to command-line arguments:

| Environment Variable                  | Description                                  |
|---------------------------------------|----------------------------------------------|
| `GITHUB_ACCESS_TOKEN`                 | GitHub access token for API requests         |
| `LOG_LEVEL`                           | Logging level for the application            |
