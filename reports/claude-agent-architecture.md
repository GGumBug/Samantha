[← README로 돌아가기](../README.md)

# Claude Agent 아키텍처 결정 규칙

SDK / CLI 시스템 프롬프트와 Agent / Command / Skill 선택은 자주 마주치는 분기점이다. 사례 전체는 [reports/archive/](archive/)에 보존, 본 문서는 **결정 규칙 + 체크리스트 + 매트릭스**만 다룬다.

## 1. 결정 규칙

| When (상황) | Then (결정) |
|---|---|
| SDK 와 CLI 가 동일 시스템 프롬프트로 동작해야 함 | `systemPrompt: { type: "preset", preset: "claude_code", append: "..." }` |
| 프로덕션에서 출력 재현성이 필요 | 비트 동등 재현 불가 — 구조화된 출력 + JSON 스키마 검증 + 캐싱으로 완화 |
| CLAUDE.md 자동 로드를 SDK 측에서도 원함 | `settingSources: ["project"]` 명시 (기본 비활성) |
| 간단·반복 절차 (`/time`, 빠른 변환 등) | **Skill** 우선 (인라인, 자동 호출 가능) |
| 다단계 자율 작업 + 컨텍스트 격리 + 지속 메모리 필요 | **Agent** (`.claude/agents/<name>.md`) |
| 사용자 주도 워크플로 또는 다중 에이전트 조율 | **Command** (`.claude/commands/<name>.md`) |
| Claude 가 의도에 따라 자동 호출할 재사용 절차 | **Skill** + `description` 명시 (자동 발견 활성) |
| 컨텍스트는 격리하지 않고 현재 세션과 통합 | Skill / Command (`context: fork` 로 선택적 격리) |

## 2. 운영 체크리스트

### 사용 전
- [ ] SDK ↔ CLI 일관성 필요 여부 결정 (재현성 불가능을 팀에 공지)
- [ ] preset 사용 vs 시스템 프롬프트 직접 작성 결정
- [ ] CLAUDE.md 자동 로드가 SDK 환경에서도 필요하면 `settingSources` 설정
- [ ] Agent / Command / Skill 선택 — 자동 호출(O/X) × 컨텍스트 격리(O/X) 2축으로 결정

### 사용 중
- [ ] Agent 자동 호출 활성화 시 `description` 의 명시도 점검 (모호하면 미호출)
- [ ] Command 워크플로의 단계별 실행 흐름 점검
- [ ] Skill 인라인 실행 시 컨텍스트 오버헤드가 의도대로 낮은지 확인
- [ ] 동일 트리거에 Skill/Agent/Command 가 매칭되면 우선순위(Skill > Agent > Command) 따름

### 사용 후
- [ ] 출력 변동성 로깅 (모델 버전 / 인프라 변동 / 시각 추론 변동)
- [ ] 프로덕션 파이프라인은 JSON 스키마 검증 통과 후에만 채택
- [ ] Agent 의 `memory:` 설정이 세션 간 유지되는지 확인

## 3. 트레이드오프 매트릭스

### SDK vs CLI 시스템 프롬프트

| 항목 | CLI (기본) | SDK (최소값) | SDK (preset) |
|---|---|---|---|
| 시스템 프롬프트 | 모듈식 (~269+ base) | 최소 | 모듈식 (CLI 일치) |
| 내장 도구 | 18+ | 제한 | 18+ |
| CLAUDE.md 자동 로드 | O | X | X (config 필요) |
| 코딩 가이드라인 | O | X | O |
| 비트 동등 재현 | X | X | X |
| 장점 | 풍부한 자동 컨텍스트 | 컨텍스트 여유 | 통제된 일관성 |
| 단점 | 출력 변동 | 기능 손실 | 설정 부담 |

### Agent vs Command vs Skill

| 기능 | Agent | Command | Skill |
|---|---|---|---|
| 위치 | `.claude/agents/<name>.md` | `.claude/commands/<name>.md` | `.claude/skills/<name>/SKILL.md` |
| 컨텍스트 | 분리(독립) | 인라인 | 인라인 (선택적 fork) |
| Claude 자동 호출 | O (description) | X | O (description) |
| `/` 메뉴 표시 | X | O | O |
| 독립 컨텍스트 윈도우 | O | X | X (`context: fork` 시 O) |
| 지속 메모리 | O | X | X |
| 권장 용도 | 다단계 자율 작업 | 사용자 주도 조율 | 경량 자동 호출 |

## 4. 참조

- [Modifying System Prompts — Agent SDK](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/sdk#modifying-system-prompts)
- [Claude Code Skills](https://code.claude.com/docs/en/skills)
- [Claude Code Sub-agents](https://code.claude.com/docs/en/sub-agents)
- [원본 사례 — reports/archive/claude-agent-sdk-vs-cli-system-prompts.md](archive/claude-agent-sdk-vs-cli-system-prompts.md)
- [원본 사례 — reports/archive/claude-agent-command-skill.md](archive/claude-agent-command-skill.md)
