# CLAUDE.md

이 파일은 Claude Code(claude.ai/code)가 이 저장소의 코드를 작업할 때 참고하는 지침을 제공합니다.

## 저장소 개요

이 저장소는 Claude Code 설정에 대한 모범 사례 저장소로, 스킬(skills), 서브에이전트(subagents), 훅(hooks), 명령어(commands)의 패턴을 시연합니다. 애플리케이션 코드베이스가 아닌 참조 구현체로 활용됩니다.

## 주요 구성 요소

### 날씨 시스템 (예시 워크플로우)
**명령어 → 에이전트 → 스킬** 아키텍처를 통해 두 가지 서로 다른 스킬 패턴을 시연합니다:
- `/weather-orchestrator` 명령어 (`.claude/commands/weather-orchestrator.md`): 진입점 — 사용자에게 C/F를 묻고, 에이전트를 호출한 후 SVG 스킬을 호출합니다
- `weather-agent` 에이전트 (`.claude/agents/weather-agent.md`): 사전 로드된 `weather-fetcher` 스킬을 사용해 온도를 가져옵니다 (에이전트 스킬 패턴)
- `weather-fetcher` 스킬 (`.claude/skills/weather-fetcher/SKILL.md`): 에이전트에 사전 로드됨 — Open-Meteo에서 온도를 가져오는 지침
- `weather-svg-creator` 스킬 (`.claude/skills/weather-svg-creator/SKILL.md`): 스킬 — SVG 날씨 카드를 생성하고 `orchestration-workflow/weather.svg` 및 `orchestration-workflow/output.md`에 저장합니다

두 가지 스킬 패턴: 에이전트 스킬(`skills:` 필드를 통해 사전 로드) vs 스킬(`Skill` 도구를 통해 호출). 전체 흐름 다이어그램은 `orchestration-workflow/orchestration-workflow.md`를 참고하세요.

### 스킬 정의 구조
`.claude/skills/<name>/SKILL.md`의 스킬은 YAML 프론트매터를 사용합니다:
- `name`: 표시 이름 및 `/슬래시-명령어` (기본값: 디렉토리 이름)
- `description`: 호출 시점 (자동 검색 시 권장)
- `argument-hint`: 자동 완성 힌트 (예: `[issue-number]`)
- `disable-model-invocation`: 자동 호출을 방지하려면 `true`로 설정
- `user-invocable`: `/` 메뉴에서 숨기려면 `false`로 설정 (배경 지식 전용)
- `allowed-tools`: 스킬이 활성화될 때 권한 프롬프트 없이 허용되는 도구
- `model`: 스킬이 활성화될 때 사용할 모델
- `context`: 격리된 서브에이전트 컨텍스트에서 실행하려면 `fork`로 설정
- `agent`: `context: fork`에 대한 서브에이전트 유형 (기본값: `general-purpose`)
- `hooks`: 이 스킬에 범위가 지정된 라이프사이클 훅

### 프레젠테이션 시스템
`.claude/rules/presentation.md` 참고 — 모든 프레젠테이션 작업은 `presentation-curator` 에이전트에 위임됩니다.

### 훅 시스템
`.claude/hooks/`의 크로스 플랫폼 사운드 알림 시스템:
- `scripts/hooks.py`: Claude Code 훅 이벤트의 메인 핸들러
- `config/hooks-config.json`: 공유 팀 설정
- `config/hooks-config.local.json`: 개인 재정의 (git에서 무시됨)
- `sounds/`: 훅 이벤트별로 구성된 오디오 파일 (ElevenLabs TTS로 생성)

`.claude/settings.json`에 설정된 훅 이벤트: PreToolUse, PostToolUse, UserPromptSubmit, Notification, Stop, SubagentStart, SubagentStop, PreCompact, SessionStart, SessionEnd, Setup, PermissionRequest, TeammateIdle, TaskCompleted, ConfigChange.

특별 처리: git 커밋 시 `pretooluse-git-committing` 사운드가 재생됩니다.

## 핵심 패턴

### 서브에이전트 오케스트레이션
서브에이전트는 bash 명령어를 통해 다른 서브에이전트를 **호출할 수 없습니다**. Agent 도구를 사용하세요 (v2.1.63에서 Task에서 이름이 변경됨; `Task(...)`는 여전히 별칭으로 작동):
```
Agent(subagent_type="agent-name", description="...", prompt="...", model="haiku")
```

서브에이전트 정의에서 도구 사용을 명시적으로 지정하세요. bash 명령어로 잘못 해석될 수 있는 "launch"와 같은 모호한 용어는 피하세요.

### 서브에이전트 정의 구조
`.claude/agents/*.md`의 서브에이전트는 YAML 프론트매터를 사용합니다:
- `name`: 서브에이전트 식별자
- `description`: 호출 시점 (자동 호출을 위해 "PROACTIVELY" 사용)
- `tools`: 도구의 쉼표로 구분된 허용 목록 (생략 시 모든 도구 상속). `Agent(agent_type)` 구문 지원
- `disallowedTools`: 거부할 도구, 상속되거나 지정된 목록에서 제거됨
- `model`: 모델 별칭: `haiku`, `sonnet`, `opus`, 또는 `inherit` (기본값: `inherit`)
- `permissionMode`: 권한 모드 (예: `"acceptEdits"`, `"plan"`, `"bypassPermissions"`)
- `maxTurns`: 서브에이전트가 중지되기 전 최대 에이전트 턴 수
- `skills`: 에이전트 컨텍스트에 사전 로드할 스킬 이름 목록
- `mcpServers`: 이 서브에이전트를 위한 MCP 서버 (서버 이름 또는 인라인 설정)
- `hooks`: 이 서브에이전트에 범위가 지정된 라이프사이클 훅 (모든 훅 이벤트 지원; `PreToolUse`, `PostToolUse`, `Stop`이 가장 일반적)
- `memory`: 영구 메모리 범위 — `user`, `project`, 또는 `local` (`reports/claude-agent-memory.md` 참고)
- `background`: 항상 백그라운드 작업으로 실행하려면 `true`로 설정
- `effort`: 노력 수준 재정의: `low`, `medium`, `high`, `max` (기본값: 세션에서 상속)
- `isolation`: 임시 git 워크트리에서 실행하려면 `"worktree"`로 설정
- `color`: 시각적 구분을 위한 CLI 출력 색상

### 설정 계층 구조
1. **관리됨** (`managed-settings.json` / MDM plist / 레지스트리): 조직이 강제 적용, 재정의 불가
2. 명령행 인수: 단일 세션 재정의
3. `.claude/settings.local.json`: 개인 프로젝트 설정 (git에서 무시됨)
4. `.claude/settings.json`: 팀 공유 설정
5. `~/.claude/settings.json`: 전역 개인 기본값
6. `hooks-config.local.json`이 `hooks-config.json`을 재정의

### 훅 비활성화
`.claude/settings.local.json`에 `"disableAllHooks": true`를 설정하거나, `hooks-config.json`에서 개별 훅을 비활성화하세요.

## 모범 사례 질문에 대한 답변

사용자가 Claude Code 모범 사례 질문을 할 경우, 훈련 지식이나 외부 소스에 의존하기 전에 **항상 이 저장소를 먼저 검색하세요** (`best-practice/`, `reports/`, `tips/`, `implementation/`, `README.md`). 이 저장소가 권위 있는 출처입니다 — 여기서 답을 찾지 못한 경우에만 외부 문서나 웹 검색으로 돌아가세요.

## 하네스 엔지니어링

이 저장소는 하네스 엔지니어링 3축(컨텍스트 엔지니어링, 환경 설계, 평가 주도 개선)을 구현합니다. 상세 매핑은 `best-practice/harness-engineering.md`를 참고하세요.

### 평가 주도 검증
- 코드 작성 후 반드시 테스트 실행 또는 브라우저 확인으로 검증합니다
- 작성자와 검증자를 분리합니다 — 서브에이전트(`isolation: "worktree"`)로 독립 리뷰
- 자기 평가 금지: "잘 되었다"고 선언하지 않고 실행 결과로 증명합니다
- 상세 규칙은 `.claude/rules/evaluation.md` 참고

## 엔지니어링 헌법 (자동 적용)

`.claude/rules/engineering-constitution.md`는 SOLID·SSOT·시니어 4단계 사고·합리화 차단·오버엔지니어링 회피 등 **사용자가 매번 요구하지 않아도 자동 적용되는 박제 룰**입니다. 모든 웹 팀 에이전트(Joi/Friday/HAL/GERTY)에게 자동 적용됩니다. 트레이드오프 발생 시에만 보고하고, 위반/회색 지대가 없으면 별도 단락 생략.

## 회고 시스템 (Self-Evolution)

세션에서 축적된 교훈이 휘발되지 않도록 3중 구조로 박제:
- `/reflect` 명령어 (수동 트리거)
- `reflection-curator` 에이전트 (실제 분석·적용)
- Stop 훅의 `reflection-reminder.py` (자동 탐지·제안)

상세는 `best-practice/reflection-protocol.md` 참고. 세션 중 회귀 발생 또는 사용자 시니어 검토자 개입이 있었으면 종료 직전 `/reflect` 사용 권장.

## 워크플로우 모범 사례

이 저장소 작업 경험을 바탕으로:

- 안정적인 준수를 위해 CLAUDE.md를 파일당 200줄 이하로 유지하세요
- 독립 실행형 에이전트 대신 워크플로우에 명령어를 사용하세요
- 범용 에이전트보다는 스킬이 있는 기능별 서브에이전트를 생성하세요 (점진적 공개)

### 💡 세션 위생 및 토큰 최적화 (Token Saving 5계명)
대화가 길어질수록 발생할 수 있는 토큰 낭비(메시지 30개 시 98.5%가 이전 대화 재독해 소모)를 막기 위해 다음을 엄수합니다:
1. **안 쓰는 MCP 서버 종료**: `/context`를 통해 활성화된 MCP 서버와 도구를 확인하고, 안 쓰는 도구는 즉각 정리하세요 (MCP당 최대 18K 토큰 소모).
2. **CLAUDE.md 다이어트**: 파일은 무조건 **200줄 이하**로 유지합니다. 자세한 매뉴얼은 `best-practice/` 내의 개별 문서로 분리하고 CLAUDE.md에는 목차/링크만 남기세요.
3. **주제 변경 시 즉각 `/clear`**: 새로운 스크립트나 태스크로 넘어갈 때는, 비대해진 세션으로 인한 비용 낭비 및 품질 저하를 막기 위해 즉시 세션을 초기화하세요.
4. **골든타임 `/compact` 수동 실행**: 95% 자동 압축을 기다리지 마세요. 컨텍스트가 **60% (또는 ~50%)** 찼을 때 선제적으로 압축해야 품질 저하가 없습니다.
5. **자리 비움 전 컨텍스트 정리**: 캐시 만료(5분) 시 전체 텍스트가 다시 처리되는 것을 막기 위해, 5분 이상 쉬거나 자리를 비우기 전에는 미리 `/compact` 하거나 `/clear` 하세요.

- 복잡한 작업은 계획 모드로 시작하세요
- 다단계 작업에는 사람이 승인하는 작업 목록 워크플로우를 사용하세요
- 서브태스크는 컨텍스트 50% 이하에서 완료할 수 있을 만큼 작게 분리하세요

### 디버깅 팁

- 진단을 위해 `/doctor`를 사용하세요
- 더 나은 로그 가시성을 위해 장시간 실행되는 터미널 명령어를 백그라운드 작업으로 실행하세요
- Claude가 콘솔 로그를 검사할 수 있도록 브라우저 자동화 MCP (Claude in Chrome, Playwright, Chrome DevTools)를 사용하세요
- 시각적 문제를 보고할 때 스크린샷을 제공하세요

## Git 커밋 규칙

변경 사항을 커밋할 때 **파일별로 개별 커밋을 생성하세요**. 여러 파일 변경 사항을 하나의 커밋으로 묶지 마세요. 각 파일은 해당 파일 변경 사항에 특화된 설명 메시지와 함께 자체 커밋을 가져야 합니다.

예를 들어, `README.md`, `best-practice/claude-subagents.md`, 스킬 파일이 모두 변경된 경우:
- 커밋 1: `git add README.md` → README 관련 메시지로 커밋
- 커밋 2: `git add best-practice/claude-subagents.md` → 서브에이전트 문서 관련 메시지로 커밋
- 커밋 3: `git add .claude/skills/weather-fetcher/SKILL.md` → 스킬 관련 메시지로 커밋

이렇게 하면 git 기록이 더 깔끔해지고 개별 변경 사항을 검토, 되돌리기, 체리픽하기 쉬워집니다.

## 웹 풀스택 개발 팀

웹 프로젝트(Next.js/React/TS) 관련 작업은 **반드시** 전문 에이전트에게 위임합니다. 위임 규칙: `.claude/rules/web-delegation.md`

| 에이전트 | 영화 | 역할 | 모델 |
|----------|------|------|------|
| **Samantha** | Her | 프로듀서 — 소통, 위임, 진행 관리, 품질 감독 (코딩 안 함) | opus |
| **Joi** | Blade Runner 2049 | 프론트엔드 아키텍트 — 디자인 시스템, shadcn/ui, Tailwind, 접근성, 테마, i18n | sonnet |
| **Friday** | Iron Man | 앱 엔지니어 — Next.js App Router, 라우팅, 상태, zod 폼, TanStack Table | sonnet |
| **HAL** | 2001: A Space Odyssey | 백엔드 엔지니어 — API 라우트, SQLite, 파일·PDF 파이프라인, 외부 데이터 통합 | sonnet |
| **GERTY** | Moon | AI 엔지니어 — Gemini/OpenAI 추상화, 프롬프트 엔지니어링, 응답 파싱, AI 기능 설계 | sonnet |

복합 작업은 Samantha에게(오케스트레이션만), 단일 전문 분야는 해당 에이전트에게 직접 위임합니다.

## 문서

문서 표준은 `.claude/rules/markdown-docs.md`를 참고하세요. 주요 문서:
- `best-practice/claude-subagents.md`: 서브에이전트 프론트매터, 훅, 저장소 에이전트
- `best-practice/claude-commands.md`: 슬래시 명령어 패턴 및 내장 명령어 참고
- `best-practice/harness-engineering.md`: 하네스 엔지니어링 3축 프레임워크
- `best-practice/refactoring-lessons.md`: 대규모 리팩토링 교훈 (전수 grep, SSOT, 추출 책임 매핑)
- `best-practice/evidence-based-debugging.md`: 증거 기반 디버깅 4단계 프로토콜
- `best-practice/reflection-protocol.md`: 세션 인사이트 반영 프로토콜
- `orchestration-workflow/orchestration-workflow.md`: 날씨 시스템 흐름 다이어그램
