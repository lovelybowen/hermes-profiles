#!/usr/bin/env bash
# Install all 8 role profiles from their dedicated distribution repos.
#
# Usage:
#   ./install-all.sh              # install all roles
#   ./install-all.sh --update     # update all roles in place
#
# Requires: git, hermes CLI. Each role needs DEEPSEEK_API_KEY in its .env
# (see ~/.hermes/profiles/<role>/.env.EXAMPLE after install).
set -euo pipefail

ORG="${ORG:-lovelybowen}"
ROLES=(
  backend-engineer
  debugger
  frontend-engineer
  orchestrator
  qa-engineer
  researcher
  reviewer
  technical-architect
)

MODE="install"
[[ "${1:-}" == "--update" ]] && MODE="update"

for role in "${ROLES[@]}"; do
  echo "── $MODE: $role"
  if [[ "$MODE" == "install" ]]; then
    hermes profile install "github.com/$ORG/$role-agent" --alias -y \
      || { echo "❌ $role 安装失败"; exit 1; }
  else
    hermes profile update "$role" -y || { echo "❌ $role 更新失败"; exit 1; }
  fi
done

echo ""
echo "✓ 全部 ${#ROLES[@]} 个角色 $MODE 完成。"
echo "  下一步: cp ~/.hermes/profiles/<role>/.env.EXAMPLE ~/.hermes/profiles/<role>/.env 并填入 DEEPSEEK_API_KEY"
