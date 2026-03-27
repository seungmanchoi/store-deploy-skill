#!/usr/bin/env bash

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_FILE="$SKILL_DIR/SKILL.md"
LEGACY_FILE="$SKILL_DIR/skill.md"

# Determine the correct skill file
if [ -f "$SKILL_FILE" ]; then
  SOURCE="$SKILL_FILE"
elif [ -f "$LEGACY_FILE" ]; then
  SOURCE="$LEGACY_FILE"
else
  echo "Error: No SKILL.md or skill.md found in $SKILL_DIR"
  exit 1
fi

# --- Install as Claude Code skill (new pattern) ---
SKILLS_DIR="$HOME/.claude/skills/store-deploy"
SKILLS_TARGET="$SKILLS_DIR/SKILL.md"

echo "=== App Store Publisher Skill Installer ==="
echo ""

# Create skill directory
mkdir -p "$SKILLS_DIR"

# Copy supporting files
if [ -d "$SKILL_DIR/scripts" ]; then
  cp -r "$SKILL_DIR/scripts" "$SKILLS_DIR/"
  echo "[+] Copied scripts/ to $SKILLS_DIR/scripts/"
fi

# Create symlink for SKILL.md
if [ -L "$SKILLS_TARGET" ] || [ -f "$SKILLS_TARGET" ]; then
  rm "$SKILLS_TARGET"
fi
ln -s "$SOURCE" "$SKILLS_TARGET"
echo "[+] Skill symlink: $SKILLS_TARGET -> $SOURCE"

# --- Also install as legacy command (backward compatibility) ---
COMMANDS_DIR="$HOME/.claude/commands"
COMMANDS_TARGET="$COMMANDS_DIR/store-deploy.md"
mkdir -p "$COMMANDS_DIR"

if [ -L "$COMMANDS_TARGET" ] || [ -f "$COMMANDS_TARGET" ]; then
  rm "$COMMANDS_TARGET"
fi
ln -s "$SOURCE" "$COMMANDS_TARGET"
echo "[+] Command symlink: $COMMANDS_TARGET -> $SOURCE"

# --- Check & install prerequisites ---
echo ""
echo "=== Checking prerequisites ==="

MISSING=()

# agent-browser
if command -v agent-browser &>/dev/null; then
  echo "[✓] agent-browser $(agent-browser --version 2>/dev/null || echo 'installed')"
else
  MISSING+=("agent-browser")
  echo "[✗] agent-browser — run: brew install agent-browser && agent-browser install"
fi

# eas-cli
if command -v eas &>/dev/null; then
  echo "[✓] eas-cli $(eas --version 2>/dev/null)"
else
  MISSING+=("eas-cli")
  echo "[✗] eas-cli — run: npm install -g eas-cli"
fi

# fastlane
if command -v fastlane &>/dev/null; then
  echo "[✓] fastlane $(fastlane --version 2>/dev/null | head -1)"
else
  MISSING+=("fastlane")
  echo "[✗] fastlane — run: brew install fastlane"
fi

# Python3 + Pillow
if python3 -c "from PIL import Image; print('OK')" &>/dev/null; then
  echo "[✓] Python3 + Pillow"
else
  MISSING+=("pillow")
  echo "[✗] Python3 Pillow — run: pip3 install Pillow"
fi

# xcrun simctl (macOS only)
if command -v xcrun &>/dev/null; then
  echo "[✓] Xcode CLI tools (xcrun simctl)"
else
  echo "[!] Xcode CLI tools not found — iOS simulator screenshots unavailable"
fi

echo ""

if [ ${#MISSING[@]} -gt 0 ]; then
  echo "=== Install missing tools? (y/n) ==="
  read -r REPLY
  if [[ "$REPLY" =~ ^[Yy]$ ]]; then
    for tool in "${MISSING[@]}"; do
      case $tool in
        agent-browser)
          echo "Installing agent-browser..."
          brew install agent-browser && agent-browser install
          ;;
        eas-cli)
          echo "Installing eas-cli..."
          npm install -g eas-cli
          ;;
        fastlane)
          echo "Installing fastlane..."
          brew install fastlane
          ;;
        pillow)
          echo "Installing Pillow..."
          pip3 install Pillow
          ;;
      esac
    done
    echo ""
    echo "[✓] All tools installed."
  else
    echo "Skipped. Install them manually before using the skill."
  fi
fi

echo ""
echo "=== Installation complete ==="
echo ""
echo "  Skill:   $SKILLS_TARGET"
echo "  Command: $COMMANDS_TARGET"
echo "  Source:  $SOURCE"
echo ""
echo "Usage: In Claude Code, type /store-deploy to activate."
echo ""
