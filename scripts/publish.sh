#!/usr/bin/env bash
# Publish one profile from this monorepo to its dedicated distribution repo.
#
# Usage:
#   ./scripts/publish.sh <role> [version]     # bump + split + tag + push
#   ./scripts/publish.sh <role> --check       # show what would be published
#
# Prerequisites:
#   - The target repo exists on GitHub (see REMOTES below), e.g.:
#       gh repo create lovelybowen/orchestrator-agent --private
#   - You have push rights (SSH key or credential helper).
#
# How it works:
#   git subtree split extracts profiles/<role>'s history into branch dist/<role>
#   (stable SHAs: repeated splits append, they don't rewrite). The split branch
#   is pushed to the target repo's main — normally a fast-forward; a divergence
#   (rewritten monorepo history) requires explicit confirmation.
set -euo pipefail

ROLE="${1:?用法: publish.sh <role> [version|--check]}"
ARG2="${2:-}"

declare -A REMOTES=(
  [backend-engineer]="https://github.com/lovelybowen/backend-engineer-agent.git"
  [debugger]="https://github.com/lovelybowen/debugger-agent.git"
  [frontend-engineer]="https://github.com/lovelybowen/frontend-engineer-agent.git"
  [orchestrator]="https://github.com/lovelybowen/orchestrator-agent.git"
  [product-manager]="https://github.com/lovelybowen/product-manager-agent.git"
  [qa-engineer]="https://github.com/lovelybowen/qa-engineer-agent.git"
  [researcher]="https://github.com/lovelybowen/researcher-agent.git"
  [reviewer]="https://github.com/lovelybowen/reviewer-agent.git"
  [technical-architect]="https://github.com/lovelybowen/technical-architect-agent.git"
)
REMOTE="${REMOTES[$ROLE]:?"没有角色 '$ROLE' 的仓库映射（检查 REMOTES）"}"
PREFIX="profiles/$ROLE"
BRANCH="dist/$ROLE"

cd "$(git rev-parse --show-toplevel)"

# ---- 0. 前置检查 -----------------------------------------------------------
[[ -f "$PREFIX/distribution.yaml" ]] || { echo "❌ 缺 $PREFIX/distribution.yaml"; exit 1; }
[[ -z "$(git status --porcelain)" ]] || { echo "❌ 工作区不干净，先 commit："; git status --short; exit 1; }

echo "── 发布检查：validate_profiles.py"
# python3 is the norm on macOS/Linux; on Windows git-bash `python3` exits 9009.
run_python() {
  if command -v python3 >/dev/null 2>&1 && python3 -c "import sys" >/dev/null 2>&1; then
    python3 "$@"
  else
    python "$@"
  fi
}
run_python scripts/validate_profiles.py

CURRENT_VERSION=$(grep -E '^version:' "$PREFIX/distribution.yaml" | head -1 | sed 's/version:[[:space:]]*//; s/["'\'']//g' | tr -d '\r')
echo "── $ROLE 当前版本: $CURRENT_VERSION"

# ---- 检查模式 ---------------------------------------------------------------
if [[ "$ARG2" == "--check" ]]; then
  echo "── [check] 将发布 $PREFIX → $REMOTE (main)"
  git log --oneline -5 -- "$PREFIX" | sed 's/^/   /'
  exit 0
fi

# ---- 1. 版本号 bump ---------------------------------------------------------
if [[ -n "$ARG2" && "$ARG2" != "$CURRENT_VERSION" ]]; then
  echo "── bump version → $ARG2"
  run_python - "$PREFIX/distribution.yaml" "$ARG2" <<'PY'
import re, sys
p, v = sys.argv[1], sys.argv[2]
s = open(p, encoding="utf-8").read()
s2 = re.sub(r"(?m)^version:[^\n]*", f"version: {v}", s, count=1)
open(p, "w", encoding="utf-8", newline="").write(s2)
PY
  git add "$PREFIX/distribution.yaml"
  git commit -m "$ROLE: bump version to $ARG2"
  CURRENT_VERSION="$ARG2"
fi
TAG="v$CURRENT_VERSION"

# ---- 2. subtree split（增量：同前缀重复 split 追加而不重写）------------------
echo "── git subtree split --prefix=$PREFIX"
SHA=$(git subtree split --prefix="$PREFIX" | tail -1)
[[ -n "$SHA" ]] || { echo "❌ split 未产出 commit"; exit 1; }
git branch -f "$BRANCH" "$SHA"
git tag -f "$TAG" "$BRANCH"

# ---- 3. push ---------------------------------------------------------------
echo "── push → $REMOTE"
REMOTE_MAIN=$(git ls-remote "$REMOTE" refs/heads/main | awk '{print $1}')
if [[ -z "$REMOTE_MAIN" ]]; then
  git push "$REMOTE" "$BRANCH:refs/heads/main"          # 首推：新建 main
elif git merge-base --is-ancestor "$REMOTE_MAIN" "$BRANCH" 2>/dev/null; then
  git push "$REMOTE" "$BRANCH:refs/heads/main"          # fast-forward
else
  echo "⚠️  远端 main 与本次 split 历史分叉（monorepo 历史被重写，或远端被手改）。"
  echo "    远端: $REMOTE_MAIN"
  echo "    本地: $(git rev-parse "$BRANCH")"
  read -r -p "强制覆盖远端 main? 输入 yes 确认: " ans
  [[ "$ans" == "yes" ]] || { echo "已取消。"; exit 1; }
  git push --force "$REMOTE" "$BRANCH:refs/heads/main"
fi
git push -f "$REMOTE" "refs/tags/$TAG"

echo ""
echo "✓ $ROLE@$CURRENT_VERSION 已发布 → $REMOTE (main, tag $TAG)"
echo "  安装: hermes profile install github.com/lovelybowen/$ROLE-agent --alias"
