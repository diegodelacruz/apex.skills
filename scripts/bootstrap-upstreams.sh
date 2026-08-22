#!/bin/bash
# Bootstrap upstream dependencies for apex.skills
# This script clones or updates required upstream repositories

set -e

UPSTREAMS_DIR=".upstreams"
APEX_MCP_REPO="https://github.com/diegodelacruz/apex-mcp.git"

echo "🔧 Bootstrapping apex.skills upstreams..."

# Create upstreams directory if it doesn't exist
if [ ! -d "$UPSTREAMS_DIR" ]; then
	mkdir -p "$UPSTREAMS_DIR"
	echo "✅ Created $UPSTREAMS_DIR/"
fi

# Clone or update apex-mcp
if [ ! -d "$UPSTREAMS_DIR/apex-mcp" ]; then
	echo "📥 Cloning apex-mcp..."
	git clone "$APEX_MCP_REPO" "$UPSTREAMS_DIR/apex-mcp"
	echo "✅ apex-mcp cloned"
else
	echo "♻️  Updating apex-mcp..."
	cd "$UPSTREAMS_DIR/apex-mcp"
	git pull origin main
	cd ../..
	echo "✅ apex-mcp updated"
fi

echo ""
echo "✅ Bootstrap complete. You can now run:"
echo "   pip install -r requirements.txt"
echo ""
