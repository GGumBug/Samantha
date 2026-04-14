---
name: samantha-best-practices
description: Samantha 프로젝트의 핵심 정책과 모범 사례를 담은 마스터 스킬. 팀 에이전트 생성 시 모든 에이전트에 사전 로드되어 프로젝트 표준을 자동 적용합니다.
user-invocable: false
---

# Samantha 프로젝트 베스트 프랙티스

이 스킬은 Samantha 프로젝트(`d:/AIProjects/Samantha`)에 정의된 모든 핵심 정책을 담고 있습니다.
이 스킬을 로드한 모든 에이전트는 아래 규칙들을 **반드시** 준수해야 합니다.

---

## 1. 서브에이전트 오케스트레이션 — 절대 원칙

### ✅ 올바른 에이전트 호출 방법

에이전트는 **반드시** `Agent` 도구를 사용하여 다른 에이전트를 호출합니다:

```
Agent(
  subagent_type="에이전트-이름",
  description="작업 요약",
  prompt="상세 지시",
  model="haiku|sonnet|opus"
)
```

### ❌ 절대 금지 사항

- **bash 명령어로 에이전트 호출 금지**: claude, subprocess 등으로 에이전트 실행 불가
- **"launch", "run", "execute" 같은 모호한 동사 사용 금지** — bash 명령으로 잘못 해석될 수 있음
- **병렬 실행 시 의존성 있는 작업 동시 실행 금지** — 데이터 계약 위반

---

## 2. YAML 프론트매터 표준

### 에이전트 `.claude/agents/[name].md`

```yaml
---
name: [에이전트-식별자]           # kebab-case
description: [언제 PROACTIVELY 사용하는지 설명]
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
color: [색상]                    # 역할별 색상 가이드 참조
maxTurns: 15                     # 10~20 범위
permissionMode: acceptEdits
memory: project
skills:
  - samantha-best-practices      # 항상 포함 (필수)
  - [전문-스킬-이름]              # 추가 전문 스킬
hooks:                           # 팀장 에이전트에만 Stop 훅 추가
  Stop:
    - hooks:
        - type: command
          command: python3 ${CLAUDE_PROJECT_DIR}/.claude/hooks/scripts/hooks.py
          timeout: 5000
          async: true
---
```

### 역할별 색상 가이드

| 역할 | 색상 |
|------|------|
| 팀장 / 오케스트레이터 | `magenta` |
| 기획 / 디자인 | `cyan` |
| 프로그래밍 / 백엔드 | `blue` |
| UI / 프론트엔드 | `yellow` |
| 시스템 / 인프라 | `white` |
| QA / 검증 | `green` |
| 데이터 / 분석 | `red` |

### 모델 선택 가이드

| 에이전트 유형 | 권장 모델 |
|-------------|---------|
| 팀장 (복잡한 판단) | `sonnet` |
| 전문가 (일반 구현) | `sonnet` |
| 반복적/단순 작업 | `haiku` |
| 고도 추론 필요 | `opus` |

### 커맨드 `.claude/commands/[name].md`

```yaml
---
name: [커맨드-이름]
description: [목적]
argument-hint: "[예: '구현 요청 내용']"
model: sonnet
---
```

### 스킬 `.claude/skills/[name]/SKILL.md`

```yaml
---
name: [스킬-이름]
description: [언제 필요한지]
user-invocable: false            # 팀 전용 스킬은 항상 false
---
```

---

## 3. 훅(Hook) 정책

### Stop 훅 — 팀장 에이전트 전용

```yaml
hooks:
  Stop:
    - hooks:
        - type: command
          command: python3 ${CLAUDE_PROJECT_DIR}/.claude/hooks/scripts/hooks.py
          timeout: 5000
          async: true
```

**규칙**:
- Stop 훅은 **팀장(오케스트레이터) 에이전트에만** 추가합니다
- 팀원 에이전트에 중복 추가 금지 (중복 실행 방지)
- `${CLAUDE_PROJECT_DIR}` 변수는 Claude Code가 자동으로 프로젝트 루트로 대체

---

## 4. Git 커밋 규칙

### 파일별 개별 커밋 원칙

변경 사항을 커밋할 때 **파일 하나당 커밋 하나**를 생성합니다:

```bash
# ✅ 올바른 방법
git add README.md
git commit -m "docs: README에 팀 구조 설명 추가"

git add .claude/agents/leader.md
git commit -m "feat: 팀장 에이전트 초기 설정"
```

```bash
# ❌ 금지
git add .
git commit -m "여러 파일 변경"
```

**이유**: git 기록이 명확해지고 개별 변경 사항을 검토/되돌리기/체리픽하기 쉬워집니다.

---

## 5. 워크플로우 모범 사례

### 에이전트 설계 원칙

- **독립 에이전트보다 커맨드 우선**: 워크플로우 진입점은 Command로 정의
- **범용 에이전트보다 전문 스킬 에이전트**: 점진적 공개 원칙 적용
- **에이전트 1명 = 명확한 도메인 1개**: 역할 겸임 금지
- **팀장은 코드를 직접 작성하지 않음**: 위임과 통합만 담당

### 세션 위생 및 토큰 최적화 (Token Saving)

대화가 길어질수록 발생할 수 있는 토큰 낭비(메시지 30개 시 토큰 98.5%가 이전 대화 재독해에 소모)를 막기 위해 다음 5가지 루틴을 엄수합니다:

1. **안 쓰는 MCP 서버 종료**: `/context` 명령을 실행해 토큰을 많이 잡아먹는 안 쓰는 도구(MCP 서버 등)를 확인하고 정리하세요. (MCP 서버 하나가 메시지당 최대 18K 토큰을 소진할 수 있습니다)
2. **CLAUDE.md 다이어트**: 파일 크기가 200줄을 넘지 않게 유지합니다. 세부 매뉴얼은 별도 `best-practice/` 파일로 분리하고 CLAUDE.md에는 목차와 링크만 남기세요.
3. **주제 변경 시 즉각 `/clear`**: 대화가 비대해지면 비용 증가 및 품질 저하가 오므로, 주제/태스크 전환 시 지체 없이 세션을 초기화합니다.
4. **골든타임 `/compact` 수동 실행**: 95% 자동 압축을 기다리지 마세요. 가장 효과적인 타이밍인 **컨텍스트 60% 시점**에서 수동으로 스코프를 유지하며 `/compact`를 실행합니다.
5. **자리 비움 전 컨텍스트 정리**: 캐시 만료(5분) 후에는 전체 대화를 다시 처리하기 위해 낭비가 발생합니다. 자리를 비우기 전에는 미리 `/compact` 하거나 `/clear` 하여 세션을 가볍게 비워두세요.

- 서브태스크는 컨텍스트 50% 이하에서 완료 가능하도록 분리
- 복잡한 작업은 **계획 모드**로 시작
- 다단계 작업에는 **사람이 승인하는 작업 목록 워크플로우** 사용

---

## 6. 문서 표준 (markdown-docs.md 기반)

- **파일은 하나의 주제에 집중**하고 간결하게 유지
- 절대 GitHub URL이 아닌 **상대 링크** 사용: `../best-practice/claude-memory.md`
- best-practice · reports 문서 상단에 **뒤로 가기 링크** 포함
- 새 개념/보고서 추가 시 **`README.md` 표 업데이트** 필수

### 폴더 배치 규칙

| 문서 유형 | 폴더 |
|---------|------|
| 모범 사례 | `best-practice/` |
| 구현 문서 | `implementation/` |
| 보고서 | `reports/` |
| 팁 | `tips/` |
| 변경 이력 | `changelog/<category>/` |

---

## 7. 디버깅 팁

- 진단을 위해 `/doctor` 사용
- 장시간 실행 터미널 명령어는 **백그라운드 작업**으로 실행
- 브라우저 자동화 MCP (Claude in Chrome, Playwright 등) 활용
- 시각적 문제 보고 시 **스크린샷** 제공
- 결과물 보고 시 항상 실제 파일 경로와 내용을 명시

---

```

---

## 9. 병렬 작업 — Git Worktree 전략

*Boris Cherny (Claude Code 팀): "단일 최대 생산성 향상 방법"*

독립적인 도메인 작업은 git worktree를 활용해 여러 Claude 세션을 병렬 실행합니다:

```bash
git worktree add ../feature-a feature/domain-a   # 에이전트 A 담당
git worktree add ../feature-b feature/domain-b   # 에이전트 B 담당

cd ../feature-a && claude   # 병렬 세션 1
cd ../feature-b && claude   # 병렬 세션 2
```

**팀 생성 시 CLAUDE.md에 도메인별 worktree 예시를 반드시 포함하세요.**

---

## 10. 온디맨드 안전 훅 패턴

*Thariq (Anthropic): "On-Demand Hooks — 위험한 작업에만 선택적 훅 적용"*

모든 팀에 위험 작업 차단용 온디맨드 훅 스킬을 제공합니다:

```yaml
# 스킬 내 hooks 필드로 세션 단위 훅 등록 예시
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: python3 -c "..."   # 위험 패턴 감지 + 차단
          timeout: 3000
```

**규칙**:
- 도메인별 파괴적 작업 차단 훅은 `user-invocable: true` 스킬로 제공
- 항상 실행되는 훅이 아닌 **필요할 때만 활성화**
- 스킬 이름 컨벤션: `[팀명]-safe-mode`

---

## 11. 레이어드 CLAUDE.md — 서브시스템별 분리

*Claude Code 메모리 시스템: 하위 디렉토리 CLAUDE.md는 지연 로드(Lazy Loading)*

대규모 프로젝트에서는 서브시스템별로 CLAUDE.md를 분리해 컨텍스트를 최적화합니다:

```
[프로젝트 루트]/
├── CLAUDE.md                ← 공통 정책 (항상 로드)
└── [서브시스템]/
    └── CLAUDE.md            ← 해당 폴더 파일 작업 시에만 로드
```

**이점**: 관련 없는 규칙이 컨텍스트를 차지하지 않아 토큰 효율 최적화

---

## 12. 스킬 Gotchas 섹션 의무화

*Thariq (Anthropic): "스킬에서 가장 신호 밀도가 높은 내용은 Gotchas 섹션"*

**모든 팀 스킬**에는 `## ⚠️ Gotchas` 섹션을 **반드시** 포함합니다:

```markdown
## ⚠️ Gotchas — Claude가 자주 빠지는 함정 (반드시 숙지)

> 코드 작성 전에 반드시 확인하세요.

### G1. [함정 이름]
❌ 잘못된 방법 + 이유
✅ 올바른 방법
```

Gotchas는 스킬 첫 버전에 포함하고, **실제 Claude 실수 발생 시마다 업데이트**합니다.

---

## 13. 핵심 체크리스트 (작업 완료 전 확인)

```
[ ] Agent 도구로만 에이전트 호출 (bash 호출 없음)
[ ] 에이전트 YAML에 samantha-best-practices 스킬 포함
[ ] 팀장 에이전트에만 Stop 훅 설정 (중복 없음)
[ ] Git 커밋: 파일별 개별 커밋
[ ] 문서: 단일 주제 집중, 상대 링크 사용
[ ] 컨텍스트 50% 도달 시 /compact 실행
[ ] 팀 CLAUDE.md에 Git Worktree 병렬 작업 가이드 포함
[ ] 온디맨드 안전 훅 스킬 ([팀명]-safe-mode) 생성
[ ] 모든 스킬에 ⚠️ Gotchas 섹션 포함
[ ] 대규모 프로젝트 시 레이어드 CLAUDE.md 구조 안내
```
