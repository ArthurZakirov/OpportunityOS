#!/usr/bin/env python3
"""Materialize private context from a private repo into a local config folder."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from pathlib import Path


def backup_if_needed(path: Path) -> None:
    if not path.exists():
        return
    backup = path.with_suffix(path.suffix + ".bak")
    counter = 1
    while backup.exists():
        backup = path.with_suffix(path.suffix + f".bak{counter}")
        counter += 1
    shutil.copy2(path, backup)


def decrypt_with_sops(source: Path, target: Path) -> bool:
    if not (source.name.endswith(".sops.yaml") or source.name.endswith(".sops.yml") or source.name.endswith(".sops.json")):
        return False
    if shutil.which("sops") is None:
        raise RuntimeError(f"{source} appears encrypted, but sops is not installed")
    name = source.name.replace(".sops", "")
    output = target.parent / name
    output.parent.mkdir(parents=True, exist_ok=True)
    backup_if_needed(output)
    with output.open("wb") as handle:
        subprocess.run(["sops", "--decrypt", str(source)], check=True, stdout=handle)
    return True


def copy_tree(source_root: Path, target_root: Path) -> None:
    ignored_dirs = {".git", ".github", ".idea", ".vscode", "__pycache__"}
    for source in source_root.rglob("*"):
        relative = source.relative_to(source_root)
        if any(part in ignored_dirs for part in relative.parts):
            continue
        target = target_root / relative
        if source.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        if decrypt_with_sops(source, target):
            continue
        if ".sops." in source.name:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        backup_if_needed(target)
        shutil.copy2(source, target)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=os.environ.get("AGENTDESK_PRIVATE_REPO", str(Path.home() / ".local/share/AgentDesk/private-repo")))
    parser.add_argument("--target", default=os.environ.get("AGENTDESK_PRIVATE_HOME", str(Path.home() / ".config/AgentDesk/private")))
    args = parser.parse_args()

    source = Path(args.source).expanduser()
    target = Path(args.target).expanduser()
    if not source.exists():
        raise SystemExit(f"Private source does not exist: {source}")
    target.mkdir(parents=True, exist_ok=True)
    copy_tree(source, target)
    print(f"Materialized private context to {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
