#!/usr/bin/env python3
"""Write an auditable deployment receipt for a k8s-live candidate."""

from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path


SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def _safe_id(value: str, label: str) -> str:
    if not SAFE_ID.fullmatch(value):
        raise ValueError(f"{label} contains unsupported characters: {value}")
    return value


def write_receipt(
    *,
    root: Path,
    environment: str,
    artifact: str,
    candidate_id: str,
    source_revision: str,
    status: str,
    artifact_status: str,
    run_url: str,
) -> Path:
    environment = _safe_id(environment, "environment")
    artifact = _safe_id(artifact, "artifact")
    candidate_id = _safe_id(candidate_id, "candidate_id")

    receipt_path = root / "releases" / "deployments" / environment / artifact / f"{candidate_id}.yaml"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    deployed = "true" if status == "deployed" else "false"
    deployed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    receipt_path.write_text(
        "\n".join(
            (
                "deployment:",
                f"  candidate_id: {candidate_id}",
                f"  artifact: {artifact}",
                f"  environment: {environment}",
                f"  source_revision: {source_revision}",
                f"  artifact_status: {artifact_status}",
                f"  status: {status}",
                f"  deployed: {deployed}",
                f"  recorded_at: {deployed_at}",
                f"  workflow_run: {run_url}" if run_url else "  workflow_run: null",
                "",
            )
        ),
        encoding="utf-8",
    )
    return receipt_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--environment", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--candidate-id", required=True)
    parser.add_argument("--source-revision", required=True)
    parser.add_argument("--status", choices=("deployed", "failed", "not_deployed"), required=True)
    parser.add_argument("--artifact-status", choices=("published", "failed", "not_published"), required=True)
    parser.add_argument("--run-url", default="")
    args = parser.parse_args()

    path = write_receipt(
        root=Path(__file__).resolve().parents[1],
        environment=args.environment,
        artifact=args.artifact,
        candidate_id=args.candidate_id,
        source_revision=args.source_revision,
        status=args.status,
        artifact_status=args.artifact_status,
        run_url=args.run_url,
    )
    print(path)


if __name__ == "__main__":
    main()
