#!/usr/bin/env bash
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

# Validation 1a : Agent Plugins doctor check
echo -e "${YELLOW}→ Checking Agent Plugins 1.0.0 (doctor)...${NC}"
if npx @hiai-gg/agent-plugins-doctor check "$REPO_ROOT" 2>/dev/null; then
  echo -e "${GREEN}✓ Doctor check passed${NC}"
else
  echo -e "${RED}✗ Doctor check failed${NC}"
  EXIT_CODE=1
fi

echo ""

# Validation 1b : Agent Plugins builder inspect
echo -e "${YELLOW}→ Inspecting Agent Plugins 1.0.0 (builder)...${NC}"
if npx @hiai-gg/agent-plugins-builder inspect "$REPO_ROOT" 2>/dev/null; then
  echo -e "${GREEN}✓ Builder inspection passed${NC}"
else
  echo -e "${RED}✗ Builder inspection failed${NC}"
  EXIT_CODE=1
fi

echo ""

# Validation 2 : Claude Code native via claude CLI
echo -e "${YELLOW}→ Checking Claude Code plugin...${NC}"
if claude plugin validate --strict "$REPO_ROOT" 2>/dev/null; then
  echo -e "${GREEN}✓ Claude Code validation passed${NC}"
else
  echo -e "${RED}✗ Claude Code validation failed${NC}"
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
