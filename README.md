# WRGG Kubernetes Live Configuration

This repository is the shared Argo CD desired-state repository for staging and
production. The environment overlays are intentionally separate even though
they use the same ApplicationSet and Helm chart templates.

## Release model

- `releases/` contains immutable release candidates. A candidate records the
  application release tag and the image tags that were published for it.
- `apps/overlays/<environment>/kustomization.yaml` contains the deployed
  release pointer for that environment, including the pinned Helm chart
  revision.
- `environments/<environment>/values/` contains only environment-specific
  configuration such as hosts, namespaces, database names, and ECR repository
  names.

Promoting a release changes only the target environment overlay pointer. It
does not copy staging values into production and it does not make Argo watch
the other environment's path.

Release tags and image tags must be treated as immutable after publication.
Rollback is a pointer change back to the previously committed candidate.

## Repository layout

```text
apps/base/                  Shared Argo ApplicationSet
apps/overlays/staging/      Staging generator and release pointer
apps/overlays/production/   Production generator and release pointer
environments/<env>/values/  Environment-specific Helm values
releases/backend/            Backend release candidates
releases/frontend/           Frontend release records
root/                        Cluster-specific root Applications
```
