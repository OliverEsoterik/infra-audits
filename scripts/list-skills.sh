#!/usr/bin/env bash
set -euo pipefail

# Audit Field Kit — List Available Skills
# Usage: ./scripts/list-skills.sh [client-id]
# If client-id is provided, shows only skills relevant to that client's scope.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_DIR"

echo "Available Audit Skills:"
echo "======================="
echo ""

for skill_file in skills/*/*/SKILL.md; do
    if [ ! -f "$skill_file" ]; then
        continue
    fi

    # Extract frontmatter fields
    NAME=""
    DOMAIN=""
    DESCRIPTION=""
    BENCHMARKS=""
    CONNECTORS=""

    while IFS= read -r line; do
        if [[ "$line" =~ ^name:\ (.*) ]]; then
            NAME="${BASH_REMATCH[1]}"
        elif [[ "$line" =~ ^domain:\ (.*) ]]; then
            DOMAIN="${BASH_REMATCH[1]}"
        elif [[ "$line" =~ ^description:\ (.*) ]]; then
            DESCRIPTION="${BASH_REMATCH[1]}"
        elif [[ "$line" =~ ^benchmarks: ]]; then
            BENCHMARKS="(see SKILL.md)"
        elif [[ "$line" =~ ^\ \ -\ (.*) ]]; then
            if [ -z "$BENCHMARKS" ]; then
                BENCHMARKS="${BASH_REMATCH[1]}"
            fi
        fi
    done < <(head -30 "$skill_file" | grep -E '^(name:|description:|domain:|benchmarks:|connectors:|  - )')

    SKILL_DIR=$(dirname "$skill_file" | sed 's|skills/||')
    echo "  [$DOMAIN] $NAME"
    echo "    Path:    skills/$SKILL_DIR"
    echo "    Desc:    $DESCRIPTION"
    echo "    Conn:    $(ls -1 "$(dirname "$skill_file")/connectors/" 2>/dev/null | wc -l) connector(s)"
    echo "    Bench:   $BENCHMARKS"
    echo ""
done

echo "---"
echo "Total domains: $(find skills -mindepth 1 -maxdepth 1 -type d | wc -l)"
echo "Total skills:  $(find skills -name 'SKILL.md' | wc -l)"
echo "Total connectors: $(find skills -path '*/connectors/*' \( -name '*.py' -o -name '*.sh' \) | wc -l)"
echo "Total benchmarks: $(find skills/core/benchmark-loader/benchmarks -name '*.yaml' | wc -l)"