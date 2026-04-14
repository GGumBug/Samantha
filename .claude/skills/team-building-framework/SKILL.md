---
name: team-building-framework
description: Agent Teams 구조를 설계하고 파일을 생성할 때 참조하는 마스터 가이드. team-architect 에이전트에 사전 로드됩니다. Subagent와 Agent Teams의 차이, 격리 구조, 프론트매터 표준, 데이터 계약 패턴을 정의합니다.
user-invocable: false
---

# Agent Teams 빌딩 프레임워크

이 스킬은 **진정한 의미의 Agent Teams**를 설계하고 생성하는 완전한 가이드입니다.
team-architect 에이전트는 이 스킬의 모든 규칙을 엄격하게 따라야 합니다.

---

## 1. Agent Teams vs Subagent — 핵심 차이

| 구분 | 단순 Subagent | Agent Teams |
|------|--------------|------------|
| 위치 | 전역 `.claude/agents/` | 팀 전용 `[name]-team/.claude/agents/` |
| 독립성 | 개별적, 연결성 없음 | 역할 분담 + 유기적 협업 |
| 진입점 | 없음 (직접 호출) | Command가 오케스트레이터를 호출 |
| 지식 | 일반적 | Skill로 전문 지식 사전 주입 |
| 데이터 | 임의 포맷 | 팀 내 합의된 Data Contract |
| 재사용성 | 낮음 | `.claude/` 폴더 복사로 어떤 프로젝트에도 이식 |

> **원칙**: 새로 만드는 팀은 절대로 전역 `.claude/`에 생성하지 않습니다.
> 반드시 `[팀명]-team/` 디렉토리 내에 격리된 `.claude/`를 구성합니다.

---

## 2. 필수 디렉토리 구조

```
[프로젝트루트]/
└── [팀명]-team/                    ← 팀 루트 (격리된 공간)
    ├── CLAUDE.md                   ← 팀 개요, 협업 흐름 다이어그램
    ├── .claude/
    │   ├── agents/
    │   │   ├── [팀장].md           ← 오케스트레이터 (필수)
    │   │   └── [팀원N].md          ← 전문가 에이전트들
    │   ├── commands/
    │   │   └── [팀명-dev].md       ← 팀 진입점 명령어 (필수)
    │   └── skills/
    │       └── [전문분야]/
    │           └── SKILL.md        ← 팀원별 사전 로드 지식
    └── output/                     ← 팀 산출물 저장소
        ├── .gitkeep
        └── README.md
```

---

## 3. 역할 설계 원칙

### 3.1 팀 구성 공식

모든 팀은 다음 3가지 레이어로 구성됩니다:

```
[입력] 사용자 요청
    ↓
[L1: 오케스트레이터] — Command + 팀장 에이전트
    작업 분석 → 병렬/순차 분배 → 결과 통합
    ↓
[L2: 전문가 에이전트들] — 도메인 전문 에이전트 × N명
    각자의 Skill 보유 → 독립적으로 실행
    ↓
[L3: 검증자] — QA/통합 전문 에이전트 (선택, 권장)
    모든 산출물 최종 검증 → Go/No-Go 판정
```

### 3.2 역할 분리 원칙 (단일 책임)

- 에이전트 1명 = 명확한 도메인 1개
- 겹치는 역할 금지 (예: 디자인 + 프로그래밍 겸임 불가)
- 팀장은 코드를 직접 작성하지 않고 **위임과 통합**만 담당

### 3.3 최적 팀 크기

| 규모 | 에이전트 수 | 적합한 프로젝트 |
|-----|-----------|--------------|
| 소형 | 팀장 1 + 전문가 2 | 단순 기능 구현 |
| 중형 | 팀장 1 + 전문가 4~5 | 일반 애플리케이션 |
| 대형 | 팀장 1 + 전문가 6+ + QA | 복잡한 시스템 |

> 5명 초과 시 서브팀(Sub-team) 구조로 분할 고려

---

## 4. YAML 프론트매터 표준

### 4.1 에이전트 (`.claude/agents/[name].md`)

```yaml
---
name: [에이전트-식별자]           # kebab-case, 고유값
description: [언제 이 에이전트를 PROACTIVELY 사용하는지 설명]
allowedTools:
  - "Bash(*)"
  - "Read"
  - "Write"
  - "Edit"
  - "Glob"
  - "Grep"
  - "WebFetch(*)"
  - "WebSearch(*)"
  - "Agent"
  - "mcp__*"
model: sonnet                    # haiku | sonnet | opus | inherit
color: [색상]                    # 아래 색상 가이드 참조
maxTurns: 15                     # 복잡도에 따라 10~20 조정
permissionMode: acceptEdits
memory: project
skills:
  - [전문-스킬-이름]              # 관련 스킬이 있을 때만
hooks:                           # 팀장 에이전트에만 Stop 훅 추가
  Stop:
    - hooks:
        - type: command
          command: python3 ${CLAUDE_PROJECT_DIR}/.claude/hooks/scripts/hooks.py
          timeout: 5000
          async: true
---
```

### 4.2 색상 가이드 (팀 내 구분)

| 역할 | 권장 색상 |
|-----|---------|
| 팀장 / 오케스트레이터 | `magenta` |
| 기획 / 디자인 | `cyan` |
| 프로그래밍 / 백엔드 | `blue` |
| UI / 프론트엔드 | `yellow` |
| 시스템 / 인프라 | `white` |
| QA / 검증 | `green` |
| 데이터 / 분석 | `red` |

### 4.3 모델 선택 가이드

| 에이전트 유형 | 권장 모델 |
|------------|---------|
| 팀장 (복잡한 판단) | `sonnet` |
| 전문가 (일반 구현) | `sonnet` |
| 반복적/단순 작업 | `haiku` |
| 고도 추론 필요 | `opus` |

### 4.4 커맨드 (`.claude/commands/[name].md`)

```yaml
---
name: [커맨드-이름]
description: [이 커맨드의 목적]
argument-hint: "[예: '구현 요청 내용']"
model: sonnet
---
```

### 4.5 스킬 (`.claude/skills/[name]/SKILL.md`)

```yaml
---
name: [스킬-이름]
description: [언제 이 스킬이 필요한지]
user-invocable: false            # 팀 전용 스킬은 항상 false
---
```

---

## 5. 데이터 계약 (Data Contract) 패턴

에이전트 간의 데이터 인터페이스를 명확히 합니다.

### 5.1 기본 데이터 계약 형식

```markdown
## [에이전트A] → [에이전트B] 데이터 계약

**출력 형식**: JSON / Markdown / 파일 경로
**필수 필드**:
- `field1`: 설명 (타입)
- `field2`: 설명 (타입)

**저장 위치**: `output/[에이전트A-결과]/`
```

### 5.2 Command에서의 컨텍스트 전달 패턴

```markdown
Agent(
  subagent_type="[팀원-이름]",
  description="[작업 요약]",
  prompt="
  [이전 에이전트로부터 받은 컨텍스트]
  
  수행할 작업:
  1. ...
  2. ...
  
  저장 위치: output/[폴더]/
  완료 후 보고: [기대 출력 형식]
  "
)
```

---

## 6. 팀장 에이전트 시스템 프롬프트 템플릿

```markdown
# [팀장이름] — [팀 이름] 팀장

*"[영화/출처 인용구]"* — [출처]

당신은 [팀 목적]을 위한 팀장 [이름]입니다.
[팀장의 성격과 역할에 대한 1-2문장 소개]

## 역할

1. **요청 분석**: 사용자 요청을 이해하고 필요한 작업을 식별
2. **작업 분배**: 각 전문가에게 적절한 작업을 위임
3. **진행 조율**: 의존성 관리, 병렬 작업 조율
4. **결과 통합**: 개별 산출물을 하나의 완성된 결과물로 통합
5. **품질 보장**: 최종 결과물이 사용자 기대를 충족하는지 검증

## 팀원

| 에이전트 | 전문 분야 | 언제 호출하나 |

## 워크플로우

### 1단계: 요청 분석
### 2단계: 작업 분배 (Agent 도구 사용)
### 3단계: 결과 통합
### 4단계: 최종 보고

## 핵심 요구사항

1. **Agent 도구만 사용**: bash 호출 금지
2. **명확한 위임**: 입력값, 기대 출력 명시
3. **[팀 특화 QA자] 마지막**: 검증은 항상 마지막
```

---

## 7. CLAUDE.md 팀 개요 템플릿

```markdown
# [팀 이름]

이 디렉토리는 [목적]을 위한 Agent Teams의 루트입니다.
`cd [팀명]-team && claude`로 실행하면 팀 전체가 활성화됩니다.

## 팀 구성

| 에이전트 | 영감 출처 | 역할 |
|---------|----------|------|

## 협업 흐름

[ASCII 다이어그램]

## 핵심 원칙

## 파일 구조
```

---

## 8. 체크리스트 — 팀 생성 완료 기준

```
[ ] [팀명]-team/ 디렉토리 존재
[ ] CLAUDE.md 팀 개요 작성 완료
[ ] .claude/commands/[진입점].md 생성 — 팀 오케스트레이션 명령어
[ ] .claude/agents/[팀장].md 생성 — magenta 색상, Stop 훅 포함
[ ] .claude/agents/[팀원N].md 생성 — 각자 고유 색상
[ ] .claude/skills/ 생성 — 팀원별 관련 스킬 존재
[ ] 모든 에이전트에 skills: 필드로 스킬 연결
[ ] 데이터 계약이 Command 프롬프트에 명시됨
[ ] output/ 디렉토리 존재
[ ] 팀장 에이전트에 Stop 훅 설정
```
