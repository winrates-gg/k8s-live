# WRGG Kubernetes Live Configuration

This repository is the shared Argo CD desired-state repository for staging and
production. The environment overlays are intentionally separate even though
they use the same ApplicationSet and Helm chart templates.

## Deployment model

This repository contains the desired Kubernetes configuration. It does not
build application artifacts and it does not decide which source revision Argo
should read.

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

Candidate metadata may live under an Argo-excluded CI path in this repository,
but Argo must not use an ignored file as a substitute for an external revision
selector. The current `releases/` files and `main`-tracking wiring are legacy
implementation details to be migrated to this model.

The backend API and worker image repositories should be defined once per
environment and consumed by both runtime and reconcile charts. The selected
backend candidate supplies the immutable API and worker digests.

## Repository layout

```text
apps/base/                  Shared Argo ApplicationSet
apps/overlays/staging/      Staging Argo entry point
apps/overlays/production/   Production Argo entry point
environments/<env>/values/  Environment-specific Helm values
releases/backend/            Legacy backend candidate manifests during migration
releases/frontend/           Legacy frontend records during migration
root/                        Cluster-specific root Applications
```

The desired-state pointer answers which revision an environment requests. Argo
health and Kubernetes state answer what actually rolled out. Rollback is a
revision-pin change, not a rebuild.
