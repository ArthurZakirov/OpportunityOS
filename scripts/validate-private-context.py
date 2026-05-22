#!/usr/bin/env python3
"""Validate materialized private job-application context without printing secrets."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text()


def env_path(name: str, default: Path) -> Path:
    return Path(os.environ.get(name, str(default))).expanduser()


def has_top_level_key(text: str, key: str) -> bool:
    return re.search(rf"^{re.escape(key)}\s*:", text, re.MULTILINE) is not None


def current_paths_from_manifest(text: str) -> list[str]:
    values: list[str] = []
    for match in re.finditer(r"^\s*currentPath\s*:\s*(.+?)\s*$", text, re.MULTILINE):
        raw = match.group(1).strip().strip('"').strip("'")
        if raw:
            values.append(raw)
    return values


def validate_jsonl(path: Path, errors: list[str]) -> None:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
        return
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{path}:{index}: invalid JSONL record: {exc}")
            continue
        if not isinstance(record, dict):
            errors.append(f"{path}:{index}: JSONL record must be an object")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--private-home", default=os.environ.get("AGENTDESK_PRIVATE_HOME", str(Path.home() / ".config/AgentDesk/private")))
    args = parser.parse_args()

    private_home = Path(args.private_home).expanduser()
    job_home = private_home / "job-applications"
    profile = env_path("AGENTDESK_PROFILE_PATH", job_home / "application-profile.yaml")
    manifest = env_path("AGENTDESK_DOCUMENT_MANIFEST_PATH", job_home / "document-manifest.yaml")
    field_policy = env_path("AGENTDESK_FIELD_POLICY_PATH", job_home / "field-answer-policy.yaml")
    log_path = env_path("AGENTDESK_APPLICATION_LOG_PATH", job_home / "application-log.jsonl")

    errors: list[str] = []
    statuses: list[tuple[str, Path, bool]] = [
        ("profile", profile, profile.exists()),
        ("document_manifest", manifest, manifest.exists()),
        ("field_policy", field_policy, field_policy.exists()),
        ("application_log", log_path, log_path.exists()),
    ]

    for label, path, exists in statuses[:3]:
        if not exists:
            errors.append(f"Missing {label}: {path}")

    if profile.exists():
        text = read_text(profile)
        for key in ["version", "identity", "contact"]:
            if not has_top_level_key(text, key):
                errors.append(f"{profile}: missing top-level key `{key}`")

    document_summary: list[dict[str, str | bool]] = []
    if manifest.exists():
        text = read_text(manifest)
        for key in ["version", "documents"]:
            if not has_top_level_key(text, key):
                errors.append(f"{manifest}: missing top-level key `{key}`")
        for raw_path in current_paths_from_manifest(text):
            expanded = Path(os.path.expandvars(raw_path)).expanduser()
            document_summary.append({"path": str(expanded), "exists": expanded.exists()})
            if not expanded.exists():
                errors.append(f"Referenced document is missing: {expanded}")

    if field_policy.exists():
        text = read_text(field_policy)
        for key in ["version", "submission", "fieldPolicies"]:
            if not has_top_level_key(text, key):
                errors.append(f"{field_policy}: missing top-level key `{key}`")

    validate_jsonl(log_path, errors)

    report = {
        "privateHome": str(private_home),
        "profile": {"path": str(profile), "exists": profile.exists()},
        "documentManifest": {"path": str(manifest), "exists": manifest.exists()},
        "fieldPolicy": {"path": str(field_policy), "exists": field_policy.exists()},
        "applicationLog": {"path": str(log_path), "exists": log_path.exists()},
        "documents": document_summary,
        "validationErrors": errors,
        "ready": not errors,
        "nextManualAction": None if not errors else "Create, sync, decrypt, or repair the missing private files/documents.",
    }
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
