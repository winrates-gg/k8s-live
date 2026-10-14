# WRGG Kubernetes Live Configuration

This repository is the shared Argo CD desired-state repository for staging and
production. The environment overlays are intentionally separate even though
they use the same ApplicationSet and Helm chart templates.

## Deployment model

This repository contains the desired Kubernetes configuration. It does not
build application artifacts. It also contains the candidate records and
environment pointers that tell Argo which immutable configuration revision to
read.

The target model is:

```text
backend candidate
  -> k8s-live configuration commit
  -> staging revision pin
  -> production revision pin
  -> Argo reconciliation
```

Staging and production must not both track `main`. Each environment should be
independently pinned to an immutable `k8s-live` commit so shared ApplicationSet
logic, base manifests, Helm wiring, and values can be tested in staging while
production remains stable.

The revision pins belong in the Argo/bootstrap control layer outside the
`k8s-live` revision they select. CI moves the staging pin first and moves the
production pin after validation. Argo remains auto-synced in normal operation.

Candidate manifests and environment pointers are maintained in this
repository:

```text
releases/candidates/backend/<candidate>.yaml
releases/candidates/frontend/<candidate>.yaml
releases/deployed/staging.yaml
releases/deployed/production.yaml
```

CI commits the candidate first, captures that commit SHA, and then commits the
environment pointer. The pointer's `k8sLiveRevision` is immutable, so Argo
does not follow moving `main` content for the selected environment.

Deployment receipts are recorded separately under
`releases/deployments/<environment>/<artifact>/`. They include the candidate
ID, source revision, artifact status, deployment status, and a `deployed: true`
or `false` value. Kubernetes pointer updates use `status: requested` until a
health-aware process confirms Argo has rolled out successfully. Receipts are
environment-specific so staging and production history cannot be confused.

The backend API and worker image repositories should be defined once per
environment and consumed by both runtime and reconcile charts. The selected
backend candidate supplies the immutable API and worker digests.

## Repository layout

```text
apps/base/                  Shared Argo ApplicationSet
apps/overlays/staging/      Staging Argo entry point
apps/overlays/production/   Production Argo entry point
environments/<env>/values/  Environment-specific Helm values
releases/candidates/         CI-generated backend and frontend candidates
releases/deployed/           Environment pointers consumed by Argo
releases/deployments/        Environment-specific deployment receipts
root/                        Cluster-specific root Applications
```

The desired-state pointer answers which revision an environment requests. Argo
health and Kubernetes state answer what actually rolled out. Rollback is a
revision-pin change, not a rebuild.
