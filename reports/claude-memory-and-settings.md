[← README로 돌아가기](../README.md)

# Claude Memory & Settings 결정 규칙

에이전트 메모리(user / project / local)와 설정 우선순위는 충돌 시 디버깅이 어려운 영역이다. 사례 전체는 [reports/archive/](archive/)에 보존, 본 문서는 **결정 규칙 + 체크리스트 + 매트릭스**만 다룬다.

## 1. 결정 규칙

| When (상황) | Then (결정) |
|---|---|
| 에이전트가 세션 간 지식을 보존해야 함 | 메모리 범위 — 크로스 프로젝트 = `user`, 팀 공유 = `project`, 개인 노트 = `local` |
| 설정 충돌 발생 | 우선순위: managed → CLI 플래그 → `.claude/settings.local.json` → `.claude/settings.json` → `~/.claude/settings.local.json` → `~/.claude/settings.json` |
| 토큰 / OAuth / 자격증명 저장 | **반드시 전역**(`~/.claude.json` 또는 시스템 키체인) — 프로젝트 파일에 절대 금지 |
| MEMORY.md 200줄 초과 | 주제별 파일로 분리 — 상단 200줄만 시스템 프롬프트에 주입됨 |
| 팀과 구성을 공유 | `.claude/rules/`, `.claude/agents/`, `.claude/settings.json` (버전 관리됨) |
| 개인 키바인딩 / MCP / 캐시 설정 | 전역 `~/.claude/`만 (프로젝트 레벨 미지원) |
| 다중 세션 간 작업 연계 | `~/.claude/tasks/` + `CLAUDE_CODE_TASK_LIST_ID` 환경변수 |
| 프로젝트별 에이전트 메모리 필요 | `.claude/agent-memory/<agent-name>/` 또는 전역 동등 경로 |
| `deny` 규칙이 의도대로 안 걸릴 때 | managed 또는 상위 우선순위 파일에서 `allow` 가 덮었는지 확인 (`deny` 는 허용으로 오버라이드 불가하므로 **둘 다 있을 경우 deny 가 항상 승리**) |

## 2. 운영 체크리스트

### 메모리 구성 전
- [ ] 에이전트가 학습할 패턴이 크로스 프로젝트인지 / 팀 공유인지 / 개인용인지 결정
- [ ] 메모리 범위(`user` / `project` / `local`) 프론트매터에 명시
- [ ] 에이전트 프롬프트에 "메모리를 먼저 검토하고 작업 후 업데이트" 명시

### 설정 검증 중
- [ ] `.claude/settings.json` 과 `~/.claude/settings.json` 의 중복 키 확인
- [ ] 자격증명이 프로젝트 파일에 누적되지 않았는지 grep
- [ ] hooks / permissions 충돌 시 우선순위 표대로 동작하는지 점검

### 세션 종료 후
- [ ] MEMORY.md 가 200줄 초과하면 분리
- [ ] 에이전트가 학습한 패턴이 메모리에 저장됐는지 확인
- [ ] 다중 세션 협업이면 `CLAUDE_CODE_TASK_LIST_ID` 로 태스크 공유 상태 확인

## 3. 트레이드오프 매트릭스

### 메모리 범위 선택

| 범위 | 저장 위치 | 공유 범위 | 버전 관리 | 추천 |
|---|---|---|---|---|
| `user` | `~/.claude/agent-memory/` | 모든 프로젝트 | X | 크로스 프로젝트 지식 (기본) |
| `project` | `.claude/agent-memory/` | 팀 (커밋됨) | O | 팀 표준 필요 시 |
| `local` | `.claude/agent-memory-local/` | 개인 전용 | X (gitignore) | 민감 / 프로젝트별 노트 |

### 설정 우선순위

| 우선순위 | 저장소 | 범위 | 버전 관리 | 용도 |
|---|---|---|---|---|
| 1 (최고) | managed | 조직 강제 | N/A | MDM / 정책 |
| 2 | CLI 플래그 | 세션 | N/A | 일시 오버라이드 |
| 3 | `.claude/settings.local.json` | 프로젝트 | X (gitignore) | 개인 프로젝트 설정 |
| 4 | `.claude/settings.json` | 프로젝트 | O | 팀 공유 |
| 5 | `~/.claude/settings.local.json` | 전역 | N/A | 개인 전역 오버라이드 |
| 6 (최저) | `~/.claude/settings.json` | 전역 | N/A | 기본 전역 |

**규칙**: `deny` 는 모든 우선순위에서 허용으로 오버라이드 불가.

## 4. 참조

- [Claude Code Sub-agents](https://code.claude.com/docs/en/sub-agents) — 메모리 필드 사양
- [Claude Code Memory](https://code.claude.com/docs/en/memory) — MEMORY.md 프론트매터, 자동 큐레이션
- [Claude Code Settings](https://code.claude.com/docs/en/settings) — 우선순위 계층
- [Agent Teams](https://code.claude.com/docs/en/agent-teams) — 다중 세션 협업 (Feb 2026)
- [원본 사례 — reports/archive/claude-agent-memory.md](archive/claude-agent-memory.md)
- [원본 사례 — reports/archive/claude-global-vs-project-settings.md](archive/claude-global-vs-project-settings.md)
