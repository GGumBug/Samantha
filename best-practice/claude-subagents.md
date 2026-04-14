# 서브에이전트 모범 사례

![Last Updated](https://img.shields.io/badge/Last_Updated-Apr%2013%2C%202026%208%3A02%20PM%20PKT-white?style=flat&labelColor=555) ![Version](https://img.shields.io/badge/Claude_Code-v2.1.101-blue?style=flat&labelColor=555)<br>
[![Implemented](https://img.shields.io/badge/Implemented-2ea44f?style=flat)](../implementation/claude-subagents-implementation.md)

Claude Code 서브에이전트 — 프론트매터 필드와 공식 내장 에이전트 타입.

<table width="100%">
<tr>
<td><a href="../">← Claude Code 모범 사례로 돌아가기</a></td>
<td align="right"><img src="../!/claude-jumping.svg" alt="Claude" width="60" /></td>
</tr>
</table>

---

## 프론트매터 필드 (16개)

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `name` | string | 예 | 소문자와 하이픈을 사용하는 고유 식별자 |
| `description` | string | 예 | 호출 시점. Claude가 자동 호출하도록 `"PROACTIVELY"` 사용 |
| `tools` | string/list | 아니요 | 도구의 쉼표로 구분된 허용 목록 (예: `Read, Write, Edit, Bash`). 생략 시 모든 도구 상속. 생성 가능한 서브에이전트를 제한하는 `Agent(agent_type)` 구문 지원; 이전 `Task(agent_type)` 별칭 여전히 작동 |
| `disallowedTools` | string/list | 아니요 | 거부할 도구, 상속되거나 지정된 목록에서 제거됨 |
| `model` | string | 아니요 | 사용할 모델: `sonnet`, `opus`, `haiku`, 전체 모델 ID (예: `claude-opus-4-6`), 또는 `inherit` (기본값: `inherit`) |
| `permissionMode` | string | 아니요 | 권한 모드: `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, 또는 `plan` |
| `maxTurns` | integer | 아니요 | 서브에이전트가 중지되기 전 최대 에이전트 턴 수 |
| `skills` | list | 아니요 | 시작 시 에이전트 컨텍스트에 사전 로드할 스킬 이름 (전체 내용이 주입됨, 단순히 사용 가능하게만 하는 것이 아님) |
| `mcpServers` | list | 아니요 | 이 서브에이전트를 위한 MCP 서버 — 서버 이름 문자열 또는 인라인 `{name: config}` 객체 |
| `hooks` | object | 아니요 | 이 서브에이전트에 범위가 지정된 라이프사이클 훅. 모든 훅 이벤트 지원; `PreToolUse`, `PostToolUse`, `Stop`이 가장 일반적 |
| `memory` | string | 아니요 | 영구 메모리 범위: `user`, `project`, 또는 `local` |
| `background` | boolean | 아니요 | 항상 백그라운드 작업으로 실행하려면 `true` 설정 (기본값: `false`) |
| `effort` | string | 아니요 | 이 서브에이전트가 활성화될 때 노력 수준 재정의: `low`, `medium`, `high`, `max` (Opus 4.6 전용). 기본값: 세션에서 상속 |
| `isolation` | string | 아니요 | 임시 git 워크트리에서 실행하려면 `"worktree"`로 설정 (변경사항이 없으면 자동 정리) |
| `initialPrompt` | string | 아니요 | 이 에이전트가 메인 세션 에이전트로 실행될 때 (`--agent` 또는 `agent` 설정을 통해) 첫 번째 사용자 턴으로 자동 제출됨. 명령어와 스킬이 처리됨. 사용자 제공 프롬프트 앞에 추가됨 |
| `color` | string | 아니요 | 태스크 목록 및 트랜스크립트에서 서브에이전트의 표시 색상: `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, 또는 `cyan` |

---

## ![Official](../!/tags/official.svg) 공식 에이전트 **(5개)**

| # | 에이전트 | 모델 | 도구 | 설명 |
|---|---------|------|------|------|
| 1 | `general-purpose` | inherit | 전체 | 복잡한 다단계 태스크 — 리서치, 코드 검색, 자율 작업을 위한 기본 에이전트 타입 |
| 2 | `Explore` | haiku | 읽기 전용 (Write, Edit 없음) | 빠른 코드베이스 검색 및 탐색 — 파일 찾기, 코드 검색, 코드베이스 질문 답변에 최적화 |
| 3 | `Plan` | inherit | 읽기 전용 (Write, Edit 없음) | 계획 모드에서의 사전 계획 리서치 — 코드 작성 전에 코드베이스를 탐색하고 구현 방법을 설계 |
| 4 | `statusline-setup` | sonnet | Read, Edit | 사용자의 Claude Code 상태 표시줄 설정을 구성 |
| 5 | `claude-code-guide` | haiku | Glob, Grep, Read, WebFetch, WebSearch | Claude Code 기능, 에이전트 SDK, Claude API에 대한 질문에 답변 |

---

## 출처

- [커스텀 서브에이전트 생성 — Claude Code 공식 문서](https://code.claude.com/docs/en/sub-agents)
- [CLI 참조 — Claude Code 공식 문서](https://code.claude.com/docs/en/cli-reference)
- [Claude Code 변경 이력](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)
