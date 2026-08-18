#!/bin/zsh
set -euo pipefail

PROJECT_DIR="/Users/seven/Desktop/Codex/技能库/github热门项目"
PROMPT_FILE="$PROJECT_DIR/automation/daily_update_prompt.md"
LOG_DIR="$PROJECT_DIR/logs"
LOCK_DIR="/tmp/github-hot-projects-daily.lock"
DATE_STAMP="$(/bin/date +%F)"
LOG_FILE="$LOG_DIR/daily-update-$DATE_STAMP.log"
LAST_MESSAGE_FILE="$LOG_DIR/daily-update-$DATE_STAMP.final.txt"

/bin/mkdir -p "$LOG_DIR"

if ! /bin/mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "Another daily update is already running." >> "$LOG_FILE"
  exit 0
fi

cleanup() {
  /bin/rmdir "$LOCK_DIR" 2>/dev/null || true
}
trap cleanup EXIT

{
  echo "=== GitHub Hot Projects daily update: $(/bin/date '+%Y-%m-%d %H:%M:%S %Z') ==="
  echo "Project: $PROJECT_DIR"
  cd "$PROJECT_DIR"

  /usr/bin/env -i \
    HOME="/Users/seven" \
    PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin" \
    TERM="dumb" \
    /opt/homebrew/bin/codex exec \
    --cd "$PROJECT_DIR" \
    --model gpt-5 \
    --ask-for-approval never \
    --sandbox danger-full-access \
    --search \
    --output-last-message "$LAST_MESSAGE_FILE" \
    < "$PROMPT_FILE"

  echo "=== Done: $(/bin/date '+%Y-%m-%d %H:%M:%S %Z') ==="
} >> "$LOG_FILE" 2>&1
