#!/usr/bin/env python3
"""Read and update the environment current pointers used by Argo."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
SHA = re.compile(r"^[0-9a-f]{40}$")
ARTIFACT_KEYS = {
    "cluster": "clusterCandidateId",
}


def _validate(value: str, label: str, pattern: re.Pattern[str] = SAFE_ID) -> str:
    if not pattern.fullmatch(value):
        raise ValueError(f"{label} contains unsupported characters: {value}")
    return value


def pointer_path(root: Path, environment: str) -> Path:
    return root / "releases" / "current" / f"{_validate(environment, 'environment')}.yaml"


def _set_value(lines: list[str], key: str, value: str) -> list[str]:
    pattern = re.compile(rf"^{re.escape(key)}:\s*.*$")
    replacement = f"{key}: {value}"
    for index, line in enumerate(lines):
        if pattern.fullmatch(line):
            lines[index] = replacement
            return lines
    lines.append(replacement)
    return lines


def update_pointer(
    *,
    root: Path,
    environment: str,
    artifact: str,
    candidate_id: str,
    k8s_live_revision: str,
    chart_revision: str,
) -> Path:
    artifact_key = ARTIFACT_KEYS.get(artifact)
    if artifact_key is None:
        raise ValueError(f"unsupported artifact: {artifact}")
    _validate(candidate_id, "candidate_id")
    _validate(k8s_live_revision, "k8s_live_revision", SHA)
    _validate(chart_revision, "chart_revision", SHA)

    path = pointer_path(root, environment)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    _set_value(lines, "environment", environment)
    _set_value(lines, "k8sLiveRevision", k8s_live_revision)
    _set_value(lines, artifact_key, candidate_id)
    _set_value(lines, "chartRevision", chart_revision)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def get_value(*, root: Path, environment: str, key: str) -> str:
    path = pointer_path(root, environment)
    if not path.exists():
        raise ValueError(f"deployment pointer does not exist: {path}")
    pattern = re.compile(rf"^{re.escape(key)}:\s*(\S+)\s*$")
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.fullmatch(line)
        if match:
            return match.group(1)
    raise ValueError(f"deployment pointer {path} has no {key} value")


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    update = subparsers.add_parser("update")
    update.add_argument("--environment", required=True)
    update.add_argument("--artifact", choices=sorted(ARTIFACT_KEYS), required=True)
    update.add_argument("--candidate-id", required=True)
    update.add_argument("--k8s-live-revision", required=True)
    update.add_argument("--chart-revision", required=True)

    get = subparsers.add_parser("get")
    get.add_argument("--environment", required=True)
    get.add_argument("--key", required=True)

    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.command == "update":
        print(update_pointer(
            root=root,
            environment=args.environment,
            artifact=args.artifact,
            candidate_id=args.candidate_id,
            k8s_live_revision=args.k8s_live_revision,
            chart_revision=args.chart_revision,
        ))
    else:
        print(get_value(root=root, environment=args.environment, key=args.key))


if __name__ == "__main__":
    main()
