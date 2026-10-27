#!/usr/bin/env bash
# Tianzheng DWG Parse skill - one-line installer (macOS / Linux)
# Usage:  curl -fsSL https://raw.githubusercontent.com/hwdemtv/tianzheng-dwg-parse/main/install.sh | bash
set -euo pipefail

OWNER="hwdemtv"
NAME="tianzheng-dwg-parse"
DEST="$HOME/.workbuddy/skills/$NAME"
TMP="$(mktemp -d)"

echo ">> Downloading $NAME ..."
curl -fsSL "https://github.com/$OWNER/$NAME/archive/refs/heads/main.zip" -o "$TMP/$NAME.zip"
unzip -q "$TMP/$NAME.zip" -d "$TMP"

mkdir -p "$DEST/references" "$DEST/scripts"
cp "$TMP/$NAME-main/SKILL.md" "$DEST/"
cp "$TMP/$NAME-main/references/"* "$DEST/references/"
cp "$TMP/$NAME-main/scripts/"* "$DEST/scripts/"

rm -rf "$TMP"
echo ">> Installed to $DEST"
echo ">> Restart WorkBuddy, then say: 用 tianzheng-dwg-parse 技能统计这张天正图纸的设备数量"
