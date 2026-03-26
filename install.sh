#!/usr/bin/env bash

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_FILE="$SKILL_DIR/skill.md"
COMMANDS_DIR="$HOME/.claude/commands"
TARGET="$COMMANDS_DIR/store-deploy.md"

echo "Installing store-deploy skill..."

# Create ~/.claude/commands/ if it doesn't exist
if [ ! -d "$COMMANDS_DIR" ]; then
  mkdir -p "$COMMANDS_DIR"
  echo "Created $COMMANDS_DIR"
fi

# Remove existing symlink or file if present
if [ -L "$TARGET" ]; then
  rm "$TARGET"
  echo "Removed existing symlink at $TARGET"
elif [ -f "$TARGET" ]; then
  rm "$TARGET"
  echo "Removed existing file at $TARGET"
fi

# Create symlink
ln -s "$SKILL_FILE" "$TARGET"

echo ""
echo "store-deploy skill installed successfully."
echo ""
echo "  Symlink: $TARGET"
echo "  Source:  $SKILL_FILE"
echo ""
echo "Usage: In Claude Code, type /store-deploy to activate the skill."
