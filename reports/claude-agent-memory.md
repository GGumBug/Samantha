# Claude Code: 에이전트 메모리 프론트매터

서브에이전트를 위한 영구 메모리 — 에이전트가 세션 간에 학습하고, 기억하고, 지식을 구축할 수 있게 합니다.

<table width="100%">
<tr>
<td><a href="../">← Claude Code 모범 사례로 돌아가기</a></td>
<td align="right"><img src="../!/claude-jumping.svg" alt="Claude" width="60" /></td>
</tr>
</table>

---

## 개요

**Claude Code v2.1.33** (2026년 2월)에 도입된 `memory` 프론트매터 필드는 각 서브에이전트에 자체적인 영구 마크다운 기반 지식 저장소를 제공합니다. 이 이전에는 모든 에이전트 호출이 처음부터 시작되었습니다.

```yaml
---
name: code-reviewer
description: 품질과 모범 사례에 대해 코드를 검토합니다
tools: Read, Write, Edit, Bash
model: sonnet
memory: user
---

당신은 코드 리뷰어입니다. 코드를 검토할 때
발견한 패턴, 관례, 반복되는 문제를 에이전트 메모리에 업데이트하세요.
```

---

## 메모리 범위

| 범위 | 저장 위치 | 버전 관리 | 공유 | 최적 사용 |
|------|----------|----------|------|---------|
| `user` | `~/.claude/agent-memory/<agent-name>/` | 아니요 | 아니요 | 크로스 프로젝트 지식 (권장 기본값) |
| `project` | `.claude/agent-memory/<agent-name>/` | 예 | 예 | 팀이 공유해야 하는 프로젝트별 지식 |
| `local` | `.claude/agent-memory-local/<agent-name>/` | 아니요 (git-ignored) | 아니요 | 개인적인 프로젝트별 지식 |

이 범위들은 설정 계층 구조(`~/.claude/settings.json` → `.claude/settings.json` → `.claude/settings.local.json`)를 반영합니다.

---

## 작동 방식

1. **시작 시**: `MEMORY.md`의 처음 200줄이 에이전트의 시스템 프롬프트에 주입됩니다
2. **도구 접근**: `Read`, `Write`, `Edit`이 자동 활성화되어 에이전트가 메모리를 관리할 수 있습니다
3. **실행 중**: 에이전트는 자유롭게 메모리 디렉토리를 읽고 씁니다
4. **큐레이션**: `MEMORY.md`가 200줄을 초과하면 에이전트는 세부 사항을 주제별 파일로 이동합니다

```
~/.claude/agent-memory/code-reviewer/     # user 범위 예시
├── MEMORY.md                              # 기본 파일 (처음 200줄 로드)
├── react-patterns.md                      # 주제별 파일
└── security-checklist.md                  # 주제별 파일
```

---

## 에이전트 메모리 vs 다른 메모리 시스템

| 시스템 | 작성자 | 읽는 자 | 범위 |
|--------|-------|---------|------|
| **CLAUDE.md** | 직접 작성 | 메인 Claude + 모든 에이전트 | 프로젝트 |
| **자동 메모리** | 메인 Claude (자동) | 메인 Claude 전용 | 프로젝트별 사용자별 |
| **`/memory` 명령어** | 편집기를 통해 직접 | 메인 Claude 전용 | 프로젝트별 사용자별 |
| **에이전트 메모리** | 에이전트 자체 | 해당 특정 에이전트만 | 설정 가능 (user/project/local) |

이 시스템들은 **보완적** — 에이전트는 CLAUDE.md(프로젝트 컨텍스트)와 자체 메모리(에이전트별 지식)를 모두 읽습니다.

---

## 실제 예시

```yaml
---
name: api-developer
description: 팀 관례에 따라 API 엔드포인트를 구현합니다
tools: Read, Write, Edit, Bash
model: sonnet
memory: project
skills:
  - api-conventions
  - error-handling-patterns
---

API 엔드포인트를 구현합니다. 사전 로드된 스킬의 관례를 따르세요.
작업하면서 아키텍처 결정과 패턴을 메모리에 저장하세요.
```

이것은 **스킬**(시작 시 정적 지식)과 **메모리**(시간이 지남에 따라 구축되는 동적 지식)를 결합합니다.

---

## 팁

- **메모리 사용을 프롬프트에 명시하세요** — 명시적 지침 포함: `"시작하기 전에 메모리를 검토하세요. 완료 후 배운 것으로 메모리를 업데이트하세요."`
- 에이전트를 호출할 때 **메모리 확인을 요청하세요**: `"이 PR을 검토하고, 이전에 본 패턴에 대한 메모리를 확인하세요."`
- **올바른 범위를 선택하세요** — 크로스 프로젝트는 `user`, 팀 공유는 `project`, 개인적인 것은 `local`

---

## 출처

- [커스텀 서브에이전트 생성 — Claude Code 공식 문서](https://code.claude.com/docs/en/sub-agents)
- [Claude 메모리 관리 — Claude Code 공식 문서](https://code.claude.com/docs/en/memory)
- [Claude Code v2.1.33 릴리즈 노트](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)
