# CI

This directory contains Kubernetes deployment helpers and CI-owned state.

- `release_ledger.py` records and resolves cluster candidates.
- `deployment_pointer.py` reads and updates environment desired-state pins.
- `releases/candidates/` contains cluster candidate records.
- `releases/current/` contains the pointers consumed by Argo.

GitHub workflow orchestration remains under `.github/workflows/` because GitHub
Actions discovers that path automatically.

The environment runtime values own the optional deployment scope. For the
current NA beta, the staging and production overlays contain:

```json
{"releaseStage":"na-beta","platforms":{"na1":"americas"}}
```

Helm conditionally renders the scope into the shared backend ConfigMap and
uses it to constrain runtime workers. Reconciliation jobs consume that same
ConfigMap. Omitting the block means all supported platforms. A scope change is
therefore an ordinary `k8s-live` values change: create and validate a new
cluster candidate, then deploy it through the normal staging and promotion
flow.
