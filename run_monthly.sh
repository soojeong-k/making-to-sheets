#!/bin/bash
# 매월 1~7일 중 최초 실행 시 전월 랭킹 스냅샷 생성
# launchd가 매월 1~7일 09:00에 호출하며, 이미 실행된 달은 건너뜀

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$PROJECT_DIR/logs"
MARKER="$HOME/.making-to-sheets-last-run"
CURRENT_MONTH=$(date +%Y-%m)
DAY=$(date +%-d)

mkdir -p "$LOG_DIR"
LOGFILE="$LOG_DIR/$(date +%Y%m).log"

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $1" >> "$LOGFILE"; }

log "[check] day=$DAY month=$CURRENT_MONTH"

# 이미 이번 달 실행 완료된 경우 건너뜀
if [ -f "$MARKER" ] && [ "$(cat "$MARKER")" = "$CURRENT_MONTH" ]; then
    log "[skip] 이번 달($CURRENT_MONTH) 이미 실행 완료"
    exit 0
fi

# 1~7일 범위를 벗어난 경우 건너뜀 (안전장치)
if [ "$DAY" -gt 7 ]; then
    log "[skip] 실행 대상 기간(1~7일)이 지났습니다"
    exit 0
fi

log "[start] 실행 시작"

cd "$PROJECT_DIR"

# .env 로드
set -a
# shellcheck disable=SC1091
source "$PROJECT_DIR/.env"
set +a

# 실행
/usr/bin/python3 "$PROJECT_DIR/main.py" >> "$LOGFILE" 2>&1
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "$CURRENT_MONTH" > "$MARKER"
    log "[done] 성공적으로 완료"
else
    log "[error] 실패 (exit=$EXIT_CODE) — 내일 재시도 예정"
fi
