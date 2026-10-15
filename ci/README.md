# CI

This directory contains Kubernetes deployment helpers and CI-owned state.

- `release_ledger.py` records and resolves cluster candidates.
- `deployment_pointer.py` reads and updates environment desired-state pins.
- `releases/candidates/` contains cluster candidate records.
- `releases/current/` contains the pointers consumed by Argo.

GitHub workflow orchestration remains under `.github/workflows/` because that
is the path GitHub Actions discovers automatically.
