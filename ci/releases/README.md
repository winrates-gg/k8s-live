# Cluster Release Records

This directory is the CI-owned release state for the Kubernetes desired-state
domain. GitOps is the delivery mechanism; `cluster-v0.0.N` is the candidate
identity for a resolved cluster configuration.

- `candidates/cluster-v0.0.N.yaml` maps a merged `k8s-live` source revision to
  the selected backend/frontend/chart candidates and the resolved chart SHA
  used by Argo.
- `current/<environment>.yaml` records the environment's selected cluster
  candidate and immutable `k8sLiveRevision`.

Every merge to `main` creates a `not_validated` cluster candidate. Automatic
overlay validation marks it `validated` or `failed`. Staging selects that
candidate plus built application candidates and a validated Helm candidate.
Production promotion reads the chart revision from the tested
staging pointer; no deployment depends on a moving chart branch.

Backend and frontend candidate records remain authoritative in their own
repositories. A cluster candidate contains the resolved Helm values needed by
Argo, so Argo does not need to read application repositories at render time.
