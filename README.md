# Kube Inventory

This idea was raised to cover the common needs to identify if the applications running in the cluster are outdated. It is common
as a first assessment in a Kubernetes cluster, to detect which third-party applications were installed, but it is a challenge to quickly
determine if it requires an upgrade action.

The Kube Inventory contains a list of default applications that could be identified by key labels in the pods, and then look for the 
releases information in the Github official repositories, determining the version details.

You could run the application locally, and then have an output like:



# Requirements

Install [Poetry](https://python-poetry.org/docs/)

# Local execution

```
$ poetry run python kube_inventory
$ poetry run python -m unittest discover tests/
```

Validate workflow 8
