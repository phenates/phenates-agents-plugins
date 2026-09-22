#!/usr/bin/env bash
#
# validate.sh — Validate every plugin of this repository against the supported targets.
#
# This repository is a plugin store, not a plugin itself: a plugin is any directory
# containing a plugin.json outside .claude-plugin/, and each one is validated
# independently. Details are printed only when a check fails.
#
# Targets:
#   1. Agent Plugins 1.0.0  — doctor + builder, once per plugin directory
#   2. Claude Code          — marketplace manifest at the repository root
#   3. Skills               — frontmatter and marketplace declaration, via check_skills.py
#
# Usage: bash scripts/validate.sh

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXIT_CODE=0

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "═══════════════════════════════════════════════════"
echo "   Validating phenates-agents-plugins"
echo "═══════════════════════════════════════════════════"
echo ""

# Discover plugin directories: every plugin.json that is not a Claude Code manifest.
# Read line by line so repository paths containing spaces survive.
PLUGIN_DIRS=()
while IFS= read -r PLUGIN_DIR; do
  [ -n "$PLUGIN_DIR" ] && PLUGIN_DIRS+=("$PLUGIN_DIR")
done < <(find "$REPO_ROOT" \
  \( -name .git -o -name node_modules \) -prune -o \
  -name plugin.json -not -path "*/.claude-plugin/*" -print0 \
  | xargs -0 -r -n1 dirname | sort -u)

if [ ${#PLUGIN_DIRS[@]} -eq 0 ]; then
  echo -e "${RED}✗ No plugin found: no plugin.json outside .claude-plugin/${NC}"
  exit 1
fi

echo -e "${YELLOW}Plugins found: ${#PLUGIN_DIRS[@]}${NC}"
echo ""

for PLUGIN_DIR in "${PLUGIN_DIRS[@]}"; do
  PLUGIN_NAME="${PLUGIN_DIR#$REPO_ROOT/}"

  # Validation 1a : Agent Plugins doctor check
  echo -e "${YELLOW}→ ${PLUGIN_NAME} — Agent Plugins 1.0.0 (doctor)...${NC}"
  if OUTPUT=$(npx @hiai-gg/agent-plugins-doctor check "$PLUGIN_DIR" 2>&1); then
    echo -e "${GREEN}  ✓ Doctor check passed${NC}"
  else
    echo "$OUTPUT"
    echo -e "${RED}  ✗ Doctor check failed${NC}"
    EXIT_CODE=1
  fi

  # Validation 1b : Agent Plugins builder inspect
  echo -e "${YELLOW}→ ${PLUGIN_NAME} — Agent Plugins 1.0.0 (builder)...${NC}"
  if OUTPUT=$(npx @hiai-gg/agent-plugins-builder inspect "$PLUGIN_DIR" 2>&1); then
    echo -e "${GREEN}  ✓ Builder inspection passed${NC}"
  else
    echo "$OUTPUT"
    echo -e "${RED}  ✗ Builder inspection failed${NC}"
    EXIT_CODE=1
  fi

  echo ""
done

# Validation 2 : skill frontmatter and marketplace consistency
# Warnings are printed even on success: they point at skills the picker will not offer.
echo -e "${YELLOW}→ Skills — frontmatter and marketplace consistency...${NC}"
PYTHON="$(command -v python3 || command -v python || true)"
if [ -z "$PYTHON" ]; then
  echo -e "${RED}  ✗ python not found: cannot run scripts/check_skills.py${NC}"
  EXIT_CODE=1
elif OUTPUT=$("$PYTHON" "$REPO_ROOT/scripts/check_skills.py" "$REPO_ROOT" 2>&1); then
  echo "$OUTPUT"
  echo -e "${GREEN}  ✓ Skills check passed${NC}"
else
  echo "$OUTPUT"
  echo -e "${RED}  ✗ Skills check failed${NC}"
  EXIT_CODE=1
fi

echo ""

# Validation 3 : Claude Code marketplace via claude CLI
echo -e "${YELLOW}→ Marketplace — Claude Code...${NC}"
if OUTPUT=$(claude plugin validate --strict "$REPO_ROOT" 2>&1); then
  echo -e "${GREEN}  ✓ Claude Code validation passed${NC}"
else
  echo "$OUTPUT"
  echo -e "${RED}  ✗ Claude Code validation failed${NC}"
  EXIT_CODE=1
fi

echo ""
echo "═══════════════════════════════════════════════════"
if [ $EXIT_CODE -eq 0 ]; then
  echo -e "${GREEN}✓ ALL VALIDATIONS PASSED${NC}"
else
  echo -e "${RED}✗ VALIDATION FAILED${NC}"
fi
echo "═══════════════════════════════════════════════════"
echo ""

exit $EXIT_CODE
