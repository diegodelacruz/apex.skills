#!/bin/bash
# Pre-commit hook for capturing audit trail
# Automatically records git changes to .bitacora.json

set -e

BITACORA_DIR="control-proyecto"
BITACORA_FILE="$BITACORA_DIR/.bitacora.json"

# Create control-proyecto if it doesn't exist
mkdir -p "$BITACORA_DIR"

# Initialize .bitacora.json if it doesn't exist
if [ ! -f "$BITACORA_FILE" ]; then
  echo "{}" > "$BITACORA_FILE"
fi

# Get current timestamp in ISO 8601 format
TIMESTAMP=$(date -u +'%Y-%m-%dT%H:%M:%SZ')

# Get git info
BRANCH=$(git rev-parse --abbrev-ref HEAD)
AUTHOR=$(git config user.name)
EMAIL=$(git config user.email)

# Get staged files
STAGED_FILES=$(git diff --cached --name-only | tr '\n' ',' | sed 's/,$//g')
STAGED_COUNT=$(git diff --cached --name-only | wc -l)

# Get commit message if available (this runs before commit is created)
COMMIT_MSG="$(git diff --cached --diff-filter=M --name-only | head -1 || echo 'staged changes')"

# Create entry JSON (using Python for better JSON handling)
python3 << PYTHON_EOF
import json
import os
from datetime import datetime, timezone

bitacora_file = "$BITACORA_FILE"

# Read existing bitacora
with open(bitacora_file, 'r') as f:
    try:
        bitacora = json.load(f)
    except:
        bitacora = {}

# Create entry
timestamp = "$TIMESTAMP"
entry = {
    "type": "git_staged_changes",
    "branch": "$BRANCH",
    "author": "$AUTHOR",
    "email": "$EMAIL",
    "files_count": $STAGED_COUNT,
    "files_changed": "$STAGED_FILES".split(',') if "$STAGED_FILES" else [],
    "status": "staged"
}

# Add to bitacora
if timestamp not in bitacora:
    bitacora[timestamp] = []
if not isinstance(bitacora[timestamp], list):
    bitacora[timestamp] = [bitacora[timestamp]]

bitacora[timestamp].append(entry)

# Write updated bitacora
with open(bitacora_file, 'w') as f:
    json.dump(bitacora, f, indent=2)

print(f"✓ Audit logged: {$STAGED_COUNT} files staged at {timestamp}")
PYTHON_EOF

exit 0
