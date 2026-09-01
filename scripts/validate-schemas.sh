#!/usr/bin/env bash
set -euo pipefail

# Audit Field Kit — Validate Schemas
# Usage: ./scripts/validate-schemas.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_DIR"

errors=0

echo "=== Validating Audit Field Kit Schemas ==="
echo ""

# 1. Validate benchmark YAML files
echo "[1/4] Benchmark YAML files..."
for yaml_file in skills/core/benchmark-loader/benchmarks/**/*.yaml; do
    if [ ! -f "$yaml_file" ]; then
        continue
    fi
    # Skip mapping files (cross-benchmark references, not benchmarks)
    if echo "$yaml_file" | grep -q '/mappings/'; then
        continue
    fi
    if python3 -c "
import yaml, sys
try:
    with open('$yaml_file') as f:
        data = yaml.safe_load(f)
    if 'benchmark' not in data:
        print(f'ERROR: Missing benchmark field in $yaml_file')
        sys.exit(1)
    if 'controls' not in data:
        print(f'ERROR: Missing controls field in $yaml_file')
        sys.exit(1)
    for c in data['controls']:
        if 'id' not in c or 'title' not in c:
            print(f'ERROR: Control missing id/title in $yaml_file')
            sys.exit(1)
except yaml.YAMLError as e:
    print(f'ERROR: Invalid YAML in $yaml_file: {e}')
    sys.exit(1)
except Exception as e:
    print(f'ERROR: $yaml_file: {e}')
    sys.exit(1)
" 2>&1; then
        echo "  ✓ $(basename $yaml_file)"
    else
        echo "  ✗ $(basename $yaml_file)"
        errors=$((errors + 1))
    fi
done

# 2. Validate connector Python files
echo "[2/4] Connector Python files..."
for py_file in $(find skills -path '*/connectors/*.py'); do
    if python3 -c "
import sys
try:
    with open('$py_file') as f:
        source = f.read()
    compile(source, '$py_file', 'exec')
except SyntaxError as e:
    print(f'Syntax error in $py_file: {e}')
    sys.exit(1)
" 2>&1; then
        echo "  ✓ $(basename $py_file)"
    else
        echo "  ✗ $(basename $py_file)"
        errors=$((errors + 1))
    fi
done

# 3. Validate SKILL.md frontmatter
echo "[3/4] SKILL.md frontmatter..."
for skill_file in $(find skills -name 'SKILL.md'); do
    if python3 -c "
import yaml, sys
with open('$skill_file') as f:
    content = f.read()
if content.startswith('---'):
    parts = content.split('---', 2)
    if len(parts) >= 2:
        try:
            fm = yaml.safe_load(parts[1])
            if not fm or 'name' not in fm:
                print(f'ERROR: Missing name in $skill_file')
                sys.exit(1)
        except yaml.YAMLError as e:
            print(f'ERROR: Invalid YAML frontmatter in $skill_file: {e}')
            sys.exit(1)
" 2>&1; then
        echo "  ✓ $(echo $skill_file | sed 's|skills/||')"
    else
        echo "  ✗ $(echo $skill_file | sed 's|skills/||')"
        errors=$((errors + 1))
    fi
done

# 4. Validate Python library files
echo "[4/4] Python library files..."
for py_file in $(find lib -name '*.py'); do
    if python3 -c "
import sys
try:
    with open('$py_file') as f:
        source = f.read()
    compile(source, '$py_file', 'exec')
except SyntaxError as e:
    print(f'Syntax error in $py_file: {e}')
    sys.exit(1)
" 2>&1; then
        echo "  ✓ $(basename $py_file)"
    else
        echo "  ✗ $(basename $py_file)"
        errors=$((errors + 1))
    fi
done

echo ""
if [ $errors -eq 0 ]; then
    echo "=== All validations passed ==="
else
    echo "=== $errors validation error(s) found ==="
    exit 1
fi