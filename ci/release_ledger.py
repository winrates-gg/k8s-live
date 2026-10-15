#!/usr/bin/env python3
"""Maintain the k8s-live candidate ledger without external dependencies."""

from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "ci" / "releases" / "candidates"
VERSION_RE = re.compile(r"^cluster-v\d+\.\d+\.(\d+)$")


def scalar(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    text = str(value)
    return text if re.fullmatch(r"[A-Za-z0-9_./:@+-]+", text) else json.dumps(text)


def lines(value: object, indent: int = 0) -> list[str]:
    prefix = " " * indent
    if isinstance(value, dict):
        output = []
        for key, child in value.items():
            if isinstance(child, dict):
                output.append(f"{prefix}{key}:")
                output.extend(lines(child, indent + 2))
            else:
                output.append(f"{prefix}{key}: {scalar(child)}")
        return output
    return [f"{prefix}{scalar(value)}"]


def source_sha(path: Path) -> str | None:
    match = re.search(r"^\s+sha: ([0-9a-f]{40})$", path.read_text(encoding="utf-8"), re.MULTILINE)
    return match.group(1) if match else None


def record(args: argparse.Namespace) -> None:
    if not re.fullmatch(r"[0-9a-f]{40}", args.source_sha):
        raise SystemExit("source_sha must be a full 40-character lowercase SHA")
    CANDIDATES.mkdir(parents=True, exist_ok=True)
    existing = sorted(CANDIDATES.glob("cluster-v*.yaml"))
    for path in existing:
        if source_sha(path) == args.source_sha:
            print(path.stem)
            return
    numbers = [int(match.group(1)) for path in existing if (match := VERSION_RE.fullmatch(path.stem))]
    candidate_id = f"cluster-v0.0.{max(numbers, default=0) + 1}"
    document = {"candidate": {"id": candidate_id, "domain": "cluster", "status": "not_validated", "source": {"repository": "winrates-gg/k8s-live", "sha": args.source_sha}, "created_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")}}
    (CANDIDATES / f"{candidate_id}.yaml").write_text("\n".join(lines(document)) + "\n", encoding="utf-8")
    print(candidate_id)


def update(args: argparse.Namespace) -> None:
    path = CANDIDATES / f"{args.candidate_id}.yaml"
    if not path.is_file():
        raise SystemExit(f"unknown candidate: {args.candidate_id}")
    text = path.read_text(encoding="utf-8")
    text, count = re.subn(r"(?m)^  status: .*?$", f"  status: {args.status}", text, count=1)
    if count != 1:
        raise SystemExit(f"candidate has no status: {args.candidate_id}")
    if args.metadata:
        metadata = json.loads(Path(args.metadata).read_text(encoding="utf-8"))
        text = text.rstrip() + "\n" + "\n".join(lines(metadata, 2)) + "\n"
    path.write_text(text, encoding="utf-8")


def resolve(args: argparse.Namespace) -> None:
    path = CANDIDATES / f"{args.candidate_id}.yaml"
    if not path.is_file():
        raise SystemExit(f"unknown candidate: {args.candidate_id}")
    sha = source_sha(path)
    if not sha:
        raise SystemExit(f"candidate has no source SHA: {args.candidate_id}")
    print(sha)


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    record_parser = subparsers.add_parser("record")
    record_parser.add_argument("--source-sha", required=True)
    update_parser = subparsers.add_parser("update")
    update_parser.add_argument("--candidate-id", required=True)
    update_parser.add_argument("--status", required=True)
    update_parser.add_argument("--metadata")
    resolve_parser = subparsers.add_parser("resolve")
    resolve_parser.add_argument("--candidate-id", required=True)
    args = parser.parse_args()
    if args.command == "record":
        record(args)
    elif args.command == "update":
        update(args)
    else:
        resolve(args)


if __name__ == "__main__":
    main()
