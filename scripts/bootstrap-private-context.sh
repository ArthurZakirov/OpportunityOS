#!/usr/bin/env bash
set -euo pipefail

PRIVATE_HOME="${SELF_SOURCE_HOME:-$HOME/.config/self-source}"
PRIVATE_REPO="${SELF_SOURCE_REPO:-$HOME/.local/share/self-source/repo}"
PRIVATE_REMOTE="${SELF_SOURCE_REMOTE:-}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  cat <<'EOF'
Usage: bootstrap-private-context.sh [private-remote-url]

Bootstraps private, remote-backed OpportunityOS/AgentDesk context onto this
machine, materializes files under SELF_SOURCE_HOME, and validates them.

Environment:
  SELF_SOURCE_REMOTE
  SELF_SOURCE_HOME
  SELF_SOURCE_REPO
  SOPS_AGE_KEY_FILE / SOPS_AGE_KEY / SOPS_* as supported by sops
EOF
  exit 0
fi

if [[ -n "${1:-}" ]]; then
  PRIVATE_REMOTE="$1"
fi

mkdir -p "$(dirname "$PRIVATE_REPO")" "$PRIVATE_HOME"

required_files=(
  "$PRIVATE_HOME/job-applications/application-profile.yaml"
  "$PRIVATE_HOME/job-applications/document-manifest.yaml"
  "$PRIVATE_HOME/job-applications/field-answer-policy.yaml"
)

missing=false
for file in "${required_files[@]}"; do
  if [[ ! -f "$file" ]]; then
    missing=true
  fi
done

if [[ "$missing" == "true" ]]; then
  if [[ -z "$PRIVATE_REMOTE" && ! -d "$PRIVATE_REPO/.git" ]]; then
    cat >&2 <<EOF
Private context is missing and no remote source is configured.

Set SELF_SOURCE_REMOTE or pass a private repo URL:
  SELF_SOURCE_REMOTE=git@github.com:OWNER/private-context.git scripts/bootstrap-private-context.sh
EOF
    exit 2
  fi

  if [[ -d "$PRIVATE_REPO/.git" ]]; then
    git -C "$PRIVATE_REPO" pull --ff-only
  else
    git clone "$PRIVATE_REMOTE" "$PRIVATE_REPO"
  fi

  python3 "$SCRIPT_DIR/materialize-private-context.py" \
    --source "$PRIVATE_REPO" \
    --target "$PRIVATE_HOME"
fi

python3 "$SCRIPT_DIR/validate-private-context.py" \
  --private-home "$PRIVATE_HOME"
