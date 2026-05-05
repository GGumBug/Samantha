#!/usr/bin/env python3
"""Reflection Reminder Hook
=============================
Stop 이벤트에서 세션에 반영 가치 있는 변경이 있는지 감지하고,
Claude를 통해 사용자에게 `/reflect` 명령어 사용을 제안합니다.

감지 방식: 파일 mtime 기반 (git 의존 X)
  - `.claude/agents/`, `.claude/rules/`, `.claude/skills/`, `.claude/commands/`,
    `.claude/hooks/scripts/`, `best-practice/` 하위 파일의 최근 mtime 조사

출력:
  - 최근 수정 감지 시 stdout에 알림 → Claude가 사용자에게 전달
  - 감지 못하면 무소음
"""

import sys
import time
import os
from pathlib import Path

# 최근성 임계값 (초) — 세션 길이 대략치
RECENT_THRESHOLD_SECONDS = 30 * 60  # 30분

# 감지 대상 (project root 기준 상대 경로)
TARGET_DIRS = [
    ".claude/agents",
    ".claude/rules",
    ".claude/skills",
    ".claude/commands",
    ".claude/hooks/scripts",
    "best-practice",
]

# 중복 알림 억제 (쿨다운)
COOLDOWN_SECONDS = 10 * 60  # 10분
MARKER_FILE = ".claude/hooks/.reflection-reminder-last"


def project_root() -> Path:
    """스크립트 위치 기준 프로젝트 루트 추정.

    이 파일: Samantha/.claude/hooks/scripts/reflection-reminder.py
    루트까지 .parent 4번: scripts → hooks → .claude → Samantha
    """
    return Path(__file__).resolve().parent.parent.parent.parent


def has_recent_changes(base: Path, threshold: float) -> bool:
    """디렉토리 재귀 순회하며 threshold 이내 수정된 파일 존재 여부"""
    now = time.time()
    try:
        for path in base.rglob("*"):
            if path.is_file() and (now - path.stat().st_mtime) < threshold:
                return True
    except (OSError, PermissionError):
        pass
    return False


def in_cooldown(marker: Path) -> bool:
    """직전 알림 이후 COOLDOWN_SECONDS 이내면 True"""
    try:
        if not marker.exists():
            return False
        return (time.time() - marker.stat().st_mtime) < COOLDOWN_SECONDS
    except OSError:
        return False


def touch_marker(marker: Path) -> None:
    """알림 발송 기록 갱신"""
    try:
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.touch(exist_ok=True)
        os.utime(marker, None)
    except OSError:
        pass


def main() -> int:
    root = project_root()
    marker = root / MARKER_FILE

    if in_cooldown(marker):
        return 0  # 최근에 이미 알렸음

    hits = []
    for rel in TARGET_DIRS:
        target = root / rel
        if target.exists() and has_recent_changes(target, RECENT_THRESHOLD_SECONDS):
            hits.append(rel)

    if not hits:
        return 0

    # Claude가 surface할 메시지
    print(
        "💡 Samantha 웹 프로젝트 최근 변경 감지: "
        f"{', '.join(hits)}\n"
        "   `/reflect` 명령어로 이번 세션 인사이트를 체계적으로 반영할 수 있습니다 "
        "(CLAUDE.md 200줄 정책 자동 준수)."
    )
    touch_marker(marker)
    return 0


if __name__ == "__main__":
    sys.exit(main())
