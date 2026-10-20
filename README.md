# WRGG Kubernetes Live Configuration

This repository is the shared Argo CD desired-state repository for staging and
production. The environment overlays are intentionally separate even though
they use the same ApplicationSet and Helm chart templates.

## Deployment model

This repository contains the desired Kubernetes configuration. It does not
build application artifacts and it does not own backend or frontend candidate
records. It owns cluster candidates that resolve the selected app candidates
into one immutable Kubernetes desired-state revision.

The target model is:

```text
backend/chart releases
  -> cluster GitHub Release and tag
  -> environment deployment file
  -> Argo reconciliation
```

The generated environment Applications select an immutable Helm release and
an immutable `k8s-live` cluster release. The small root Application tracks
`main` only to load the pointer-aware ApplicationSet; the selected runtime
configuration and chart are still release-pinned.

The environment pointers live in this repository. CI moves the staging
pointer first and moves the production pointer after validation. Argo remains
auto-synced in normal operation.

Environment deployment state is maintained in this repository:

```text
deployments/staging.yaml
deployments/production.yaml
```

The cluster workflow verifies the selected backend and Helm GitHub Releases,
writes the environment deployment file, and publishes a `cluster-v0.0.N`
GitHub Release and tag. Frontend publication is separate: its workflow writes
the selected bundle directly to the environment's S3 release and `current/`
paths. The deployment file therefore selects only the immutable cluster,
backend, and chart releases. Rollback selects an existing cluster release and
copies its environment state forward.

The environment runtime values own the optional deployment scope. For the
current NA beta they contain
`{"releaseStage":"na-beta","platforms":{"na1":"americas"}}`.
Helm conditionally renders that scope into the shared backend ConfigMap and
uses it to constrain runtime workers; reconciliation jobs consume the same
ConfigMap. Omitting the block renders all supported platforms. Expanding the
launch scope is therefore a normal values change followed by cluster candidate
validation and the normal staging/promotion flow.

The current pointer is the requested state. Argo health and Kubernetes state
answer what actually rolled out; Git history preserves previous pointers for
rollback.

Before the first cluster candidate exists, the environment pointer file is
absent and the ApplicationSet intentionally creates no runtime Applications.

The backend API and worker image repositories should be defined once per
environment and consumed by both runtime and reconcile charts. The selected
backend candidate supplies the immutable API and worker digests.

## Repository layout

```text
apps/base/                  Shared Argo ApplicationSet
apps/overlays/staging/      Staging Argo entry point
apps/overlays/production/   Production Argo entry point
environments/<env>/values/  Environment-specific Helm values
deployments/                 Environment release selections
root/                        Cluster-specific root Applications
```

The desired-state pointer answers which revision an environment requests. Argo
health and Kubernetes state answer what actually rolled out. Rollback is a
revision-pin change, not a rebuild.
