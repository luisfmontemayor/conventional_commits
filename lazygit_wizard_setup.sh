#!/bin/bash
# Written by Luis Felipe Montemayor, sometime around April of 2026
set -euo pipefail

RED="\e[31m"
CYAN="\e[36m"
RESET="\e[0m"

SCRIPT_DIR=$(dirname $(readlink -f "${BASH_SOURCE[0]}"))
GIT_ROOT="$(git rev-parse --show-superproject-working-tree 2>/dev/null)"
if [ -z "$GIT_ROOT" ]; then
    GIT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
fi
GIT_CONFIG_DIR="${GIT_ROOT}/.git"

if [ -z "$GIT_ROOT" ]; then
    printf "${RED}Error: Not a git repository.$RESET\n"
    exit 1
fi

printf "${CYAN}[CONVENTIONAL_COMMITS] Setting up wizard in $GIT_ROOT...$RESET\n"

# Copy the core scripts and config to .git/ for Lazygit to use
# We copy them so they are available even if the repo is in a weird state
# and to avoid PYTHONPATH issues when running from Lazygit.
cp "${SCRIPT_DIR}/get_staged_scopes.py" "${GIT_CONFIG_DIR}/"
cp "${SCRIPT_DIR}/scopes.py" "${GIT_CONFIG_DIR}/"
cp "${SCRIPT_DIR}/constants.py" "${GIT_CONFIG_DIR}/"

# Copy the main template to .git/lazygit.yml
cp "${SCRIPT_DIR}/lazygit_template.yml" "${GIT_CONFIG_DIR}/lazygit.yml"

printf "${CYAN}[CONVENTIONAL_COMMITS] Wrote lazygit config ${GIT_CONFIG_DIR}/lazygit.yml$RESET\n"
printf "${CYAN}[CONVENTIONAL_COMMITS] Copied logic scripts to ${GIT_CONFIG_DIR}/$RESET\n"
