#!/usr/bin/env bash
set -euo pipefail

# Audit Field Kit — Install Dependencies
# Usage: ./scripts/install-deps.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_DIR"

echo "=== Installing Audit Field Kit Dependencies ==="
echo ""

# Python virtual environment
if [ ! -d "venv" ]; then
    echo "[1/3] Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "[2/3] Installing Python dependencies..."
pip install --upgrade pip
pip install -r lib/requirements.txt

echo "[3/3] Checking external CLI tools..."
check_tool() {
    if command -v "$1" &> /dev/null; then
        echo "  ✓ $1 ($($1 --version 2>&1 | head -1))"
    else
        echo "  ✗ $1 — NOT FOUND (optional for some skills)"
    fi
}

check_tool az
check_tool kubectl
check_tool aws
check_tool gcloud
check_tool terraform
check_tool ansible
check_tool op     # 1Password CLI

echo ""
echo "=== Done ==="
echo "To activate: source venv/bin/activate"