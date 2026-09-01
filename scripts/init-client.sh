#!/usr/bin/env bash
set -euo pipefail

# Audit Field Kit — Initialize Client Directory
# Usage: ./scripts/init-client.sh <client-name>

CLIENT_NAME="${1:?Usage: $0 <client-name>}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_DIR"

CLIENT_DIR="clients/$CLIENT_NAME"

if [ -d "$CLIENT_DIR" ]; then
    echo "Warning: Client '$CLIENT_NAME' already exists"
    read -p "Overwrite? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create client directory
mkdir -p "$CLIENT_DIR"

# Copy templates
cp clients/_template/client-config.yaml "$CLIENT_DIR/"
cp clients/_template/scoping.yaml "$CLIENT_DIR/"
cp clients/_template/benchmarks.yaml "$CLIENT_DIR/"
cp clients/_template/credentials.yaml "$CLIENT_DIR/"

# Replace placeholders
DATE=$(date +%Y%m%d)
SEQ=$(printf "%03d" $((RANDOM % 1000)))
AUDITOR="${AUDITOR:-$(whoami)}"

if [[ "$(uname)" == "Darwin" ]]; then
    sed -i '' "s/{{CLIENT_NAME}}/$CLIENT_NAME/g" "$CLIENT_DIR/client-config.yaml"
    sed -i '' "s/{{DATE}}/$DATE/g" "$CLIENT_DIR/client-config.yaml"
    sed -i '' "s/{{SEQ}}/$SEQ/g" "$CLIENT_DIR/client-config.yaml"
    sed -i '' "s/{{AUDITOR_NAME}}/$AUDITOR/g" "$CLIENT_DIR/client-config.yaml"
    sed -i '' "s/{{DATE}}/$DATE/g" "$CLIENT_DIR/client-config.yaml"
else
    sed -i "s/{{CLIENT_NAME}}/$CLIENT_NAME/g" "$CLIENT_DIR/client-config.yaml"
    sed -i "s/{{DATE}}/$DATE/g" "$CLIENT_DIR/client-config.yaml"
    sed -i "s/{{SEQ}}/$SEQ/g" "$CLIENT_DIR/client-config.yaml"
    sed -i "s/{{AUDITOR_NAME}}/$AUDITOR/g" "$CLIENT_DIR/client-config.yaml"
    sed -i "s/{{DATE}}/$DATE/g" "$CLIENT_DIR/client-config.yaml"
fi

echo "Client '$CLIENT_NAME' initialized."
echo ""
echo "Next steps:"
echo "  1. Edit $CLIENT_DIR/scoping.yaml      — define audit targets"
echo "  2. Edit $CLIENT_DIR/benchmarks.yaml    — select benchmarks"
echo "  3. Edit $CLIENT_DIR/credentials.yaml   — add credentials"
echo "  4. Run: ./scripts/run-audit.sh $CLIENT_NAME"