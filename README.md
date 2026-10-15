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
backend/frontend candidates
  -> cluster candidate
  -> k8s-live configuration commit
  -> staging revision pin
  -> production revision pin
  -> Argo reconciliation
```

The generated environment Applications do not track `main`. Each environment
is independently pinned to an immutable `k8s-live` commit so shared
ApplicationSet logic, base manifests, Helm wiring, and values can be tested in
staging while production remains stable. The small root Application may track
`main` to load the pointer-aware ApplicationSet itself.

The environment pointers live in this repository. CI moves the staging
pointer first and moves the production pointer after validation. Argo remains
auto-synced in normal operation.

Candidate manifests and environment pointers are maintained in this
repository:

```text
ci/releases/candidates/cluster-v0.0.N.yaml
ci/releases/current/staging.yaml
ci/releases/current/production.yaml
```

The backend and frontend repositories own their own candidate records and
artifact promotion. The cluster workflow verifies those records, writes a
cluster candidate containing their IDs and resolved image values, captures its
commit SHA, and then commits the environment pointer. The pointer's
`k8sLiveRevision` is immutable, so Argo does not follow moving `main` content
for the selected environment.

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
ci/                          CI helpers and CI-owned state
ci/releases/candidates/      CI-generated cluster candidates
ci/releases/current/         Environment pointers consumed by Argo
root/                        Cluster-specific root Applications
```

The desired-state pointer answers which revision an environment requests. Argo
health and Kubernetes state answer what actually rolled out. Rollback is a
revision-pin change, not a rebuild.
