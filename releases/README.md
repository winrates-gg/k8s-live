# Cluster Release Records

This directory is the CI-owned release state for the Kubernetes desired-state
domain. GitOps is the delivery mechanism; `cluster-vX.Y.Z` is the candidate
identity for a resolved cluster configuration.

- `candidates/cluster-vX.Y.Z.yaml` records the selected backend/frontend
  candidates and the chart revision used by Argo.
- `current/<environment>.yaml` records the environment's selected cluster
  candidate and immutable `k8sLiveRevision`.

Every staging deployment explicitly supplies the full Helm chart repository
SHA to `deploy-cluster.yaml`. Production promotion reads the chart revision
from the tested staging pointer; no deployment depends on an inherited
pointer or a moving chart branch.

Backend and frontend candidate records remain authoritative in their own
repositories. A cluster candidate contains the resolved Helm values needed by
Argo, so Argo does not need to read application repositories at render time.
