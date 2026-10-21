# WRGG Kubernetes Live Configuration

This repository is the shared Argo CD desired-state repository for staging and
production. The environment overlays are intentionally separate even though
they use the same base ApplicationSet manifests and Helm chart templates.

## Deployment model

This repository contains the desired Kubernetes configuration. It does not
build application artifacts and it does not own backend or frontend artifact
records. It owns cluster tags that resolve the selected app artifacts into one
immutable Kubernetes desired-state revision.

The target model is:

```text
backend/chart tags
  -> cluster tag
  -> environment deployment file
  -> Argo reconciliation
```

The generated environment Applications select an immutable Helm tag and
an immutable `k8s-live` cluster tag. The small root Application tracks
`main` only to load the desired-state ApplicationSet; the selected runtime
configuration and chart are still release-pinned.

The environment desired-state files live in this repository. CI moves the
staging state first and moves the production state after validation. Argo remains
auto-synced in normal operation.

Environment deployment state is maintained in this repository:

```text
deployments/staging.yaml
deployments/production.yaml
```

The cluster workflow runs from `main`, verifies the selected backend and Helm
tags, writes the environment deployment file, and publishes a
`cluster-v1.34.8`-shaped tag. Rollback runs through the same workflow with an
explicit `rollback_tag` input. The workflow may also create an optional
GitHub Release page. Frontend publication is separate: its workflow writes
the selected bundle directly to the environment's S3 release and `current/`
paths. The deployment file therefore selects only the immutable cluster,
backend, and chart tags. Rollback selects an existing cluster tag and
copies its environment state forward.

## Application order

Bootstrap is a separate Argo ApplicationSet and remains responsible for
cluster-level services. The application ApplicationSet renders one Argo
Application with two Helm sources so resource sync waves are shared across
initialization and runtime:

```text
bootstrap ApplicationSet
  -> namespaces, ingress, Argo support

application ApplicationSet
  -> database migration       wave 10
  -> database seed             wave 20
  -> partitions and row data   wave 30
  -> initial asset refreshes   waves 40-50
  -> Redis                     wave 60
  -> runtime workers           wave 70
  -> API                       wave 80
  -> recurring reconciliation  wave 90
```

The application ApplicationSet uses two Helm sources: `init` for the finite
blocking Jobs and `runtime` for the API, workers, Redis, and recurring
CronJobs. Reconciliation is a runtime workload, not a separate deployment
layer.

The initialization chart is one-time setup, not a separate runtime service.
If an initialization Job fails, fix or publish the relevant code and let
Argo replace that Job before the later waves are considered healthy.

Normal backend or chart changes do not require replacing the control plane:
publish the new artifacts, create the next cluster desired state, and let
Argo reconcile the existing cluster. Control-plane replacement is the
recovery path for a broken or misconfigured cluster host. Once the replacement
host is ready, the root Applications and this ApplicationSet recreate the
desired application state from Git.

The environment runtime values own the optional deployment scope. For the
current NA beta they contain
`{"releaseStage":"na-beta","platforms":{"na1":"americas"}}`.
Helm conditionally renders that scope into the shared backend ConfigMap and
uses it to constrain runtime workers; reconciliation jobs consume the same
ConfigMap. Omitting the block renders all supported platforms. Expanding the
launch scope is therefore a normal values change followed by cluster-tag
validation and the normal staging/promotion flow.

The deployment file is the requested state. Argo health and Kubernetes state
answer what actually rolled out; Git history preserves previous pointers for
rollback.

Before the first cluster deployment exists, the environment state file is
absent and the ApplicationSet intentionally creates no runtime Applications.

The backend API and worker image repositories should be defined once per
environment and consumed by the runtime chart. The selected
backend tag supplies the immutable API and worker image tags.

## Repository layout

```text
apps/base/                  Shared Argo ApplicationSets
apps/overlays/staging/      Staging Argo entry point
apps/overlays/production/   Production Argo entry point
environments/<env>/values/  Environment-specific Helm values
deployments/                 Environment release selections
root/                        Cluster-specific root Applications
```

The desired-state file answers which revision an environment requests. Argo
health and Kubernetes state answer what actually rolled out. Rollback is an
explicit revision-pin change, not a rebuild.
