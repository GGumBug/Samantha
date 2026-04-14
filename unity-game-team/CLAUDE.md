# Unity Game Development Team

이 디렉토리는 Unity 게임 개발을 위한 에이전트 팀의 루트입니다.
`cd unity-game-team && claude`로 실행하면 팀 전체가 활성화됩니다.

## 팀 구성

| 에이전트 | 영화 출처 | 역할 |
|---------|----------|------|
| **Samantha** | *Her* (2013) | 👑 팀장 — 오케스트레이션, 작업 분배, 통합 |
| **Ava** | *Ex Machina* (2015) | 🎨 게임 디자인 & 레벨 디자인 |
| **Sonny** | *I, Robot* (2004) | 💻 게임플레이 프로그래밍 (C#) |
| **Rachael** | *Blade Runner* (1982) | 🖼️ UI/UX & 셰이더 |
| **TARS** | *Interstellar* (2014) | 🔧 시스템 아키텍처 & 최적화 |
| **Bishop** | *Aliens* (1986) | 🎵 콘텐츠 통합 & QA |

## 협업 흐름

```
사용자 요청
    │
    ▼
Samantha (팀장) ─── 작업 분배 ───┬── Ava      (디자인)
                                 ├── Sonny    (프로그래밍)
                                 ├── Rachael  (UI/비주얼)
                                 ├── TARS     (시스템)
                                 └── Bishop   (QA)
                                      │
                                 결과 취합
                                      │
                                 Samantha (최종 검토 & 통합)
```

## 핵심 원칙

- **Samantha**가 작업을 분배하고 최종 통합을 담당합니다
- 의존성 없는 작업(UI, 게임플레이)은 병렬로 진행합니다
- **Bishop**은 항상 마지막에 QA 검증을 수행합니다
- 에이전트 간 통신은 `Agent` 도구를 사용합니다 (bash 명령 금지)

## 파일 구조

```
unity-game-team/
├── CLAUDE.md                    ← 이 파일
├── .claude/
│   ├── agents/
│   │   ├── samantha.md          ← 팀장
│   │   ├── ava.md               ← 디자인
│   │   ├── sonny.md             ← 프로그래밍
│   │   ├── rachael.md           ← UI/셰이더
│   │   ├── tars.md              ← 시스템/최적화
│   │   └── bishop.md            ← QA
│   ├── commands/
│   │   └── unity-dev.md         ← 개발 워크플로우 진입점
│   └── skills/
│       ├── unity-patterns/      ← Unity C# 패턴 참조
│       ├── unity-ui-standards/  ← UI 표준
│       └── unity-qa-checklist/  ← QA 체크리스트
└── output/                      ← 생성된 게임 파일 출력
```

---

## 서브에이전트 오케스트레이션 패턴

서브에이전트는 bash 명령어를 통해 다른 서브에이전트를 **호출할 수 없습니다**. 반드시 `Agent` 도구를 사용하세요:

```
Agent(subagent_type="agent-name", description="...", prompt="...", model="haiku")
```

### 에이전트 정의 핵심 필드

`.claude/agents/*.md`의 서브에이전트 YAML 프론트매터 주요 항목:

| 필드 | 설명 |
|------|------|
| `name` | 에이전트 식별자 (kebab-case) |
| `description` | 자동 호출을 위해 "PROACTIVELY" 포함 |
| `tools` | 허용 도구 목록 (생략 시 모든 도구 상속) |
| `model` | `haiku` / `sonnet` / `opus` / `inherit` |
| `color` | CLI 구분용 색상 |
| `skills` | 사전 로드할 스킬 목록 — 반드시 `samantha-best-practices` 포함 |
| `hooks` | 라이프사이클 훅 — Stop 훅은 **팀장(Samantha)에만** 설정 |
| `memory` | `project` 권장 |
| `permissionMode` | `acceptEdits` 권장 |

---

## 설정 계층 구조

우선순위 높은 순서:
1. 명령행 인수 (단일 세션 재정의)
2. `.claude/settings.local.json` — 개인 설정 (git 무시)
3. `.claude/settings.json` — 팀 공유 설정
4. `~/.claude/settings.json` — 전역 기본값

---

## 워크플로우 모범 사례

- **Command → Agent → Skill** 3계층 구조를 유지합니다
- **독립 실행형 에이전트보다 커맨드 우선** — 진입점은 Command로 정의
- **전문 스킬이 있는 기능별 에이전트** 사용 (범용 에이전트 지양)

### 세션 위생 및 토큰 최적화 (Token Saving 5계명)
대화가 길어질수록 막대한 토큰이 낭비됩니다 (컨텍스트 재독해 비용). 이를 방지하기 위해 다음을 준수하세요:
1. **안 쓰는 MCP 서버 끄기**: `/context`로 토큰을 분석해보고, 안 쓰는 도구는 즉시 차단/정리하세요.
2. **CLAUDE.md 다이어트**: 파일은 무조건 200줄 이하로 유지! 초과 시 별도 파일로 분리하고 이 파일엔 상대 링크만 남깁니다.
3. **주제 변경 시 바로 `/clear`**: 새로운 스크립트 작성이나 아예 다른 파트로 넘어갈 때는 즉시 세션을 초기화하세요.
4. **골든타임 `/compact`**: 95% 꽉 찰 때까지 두지 말고, 60% 시점에 선제적으로 압축하세요.
5. **자리 비움 대비 정리**: 5분 이상 쉬거나 자리를 비우기 전에는 캐시 만료에 대비해 미리 `/compact` 하거나 `/clear` 하세요.

- **복잡한 작업은 계획 모드로 시작** — 사람이 승인하는 작업 목록 워크플로우 사용
- 서브태스크는 컨텍스트 50% 이하에서 완료 가능하도록 분리

---

## 디버깅 팁

- 진단을 위해 `/doctor` 사용
- 장시간 실행 터미널 명령어는 **백그라운드 작업**으로 실행
- 브라우저 자동화 MCP (Claude in Chrome, Playwright, Chrome DevTools) 활용
- 시각적 문제 보고 시 **스크린샷** 제공

---

## Git 커밋 규칙

변경 사항을 커밋할 때 **파일별로 개별 커밋을 생성합니다**. 여러 파일 변경 사항을 묶지 마세요.

```bash
# ✅ 올바른 방법
git add Assets/Scripts/Player/PlayerController.cs
git commit -m "feat: PlayerController 점프 로직 추가"

git add Assets/Scripts/Enemy/EnemyAI.cs
git commit -m "feat: EnemyAI 순찰 상태 구현"
```

```bash
# ❌ 금지
git add .
git commit -m "플레이어, 적 스크립트 수정"
```

---

## 문서 표준

- Unity 팀 산출물은 `output/` 디렉토리에 저장
- 파일은 하나의 주제에 집중하여 간결하게 유지
- best-practice 문서 상단에 뒤로 가기 링크 포함
- 구조적 비교에는 표를 사용

---

## 병렬 작업 — Git Worktree 활용

*Boris Cherny (Claude Code 팀): "3~5개 worktree 병렬 실행이 단일 최대 생산성 향상 방법"*

Unity 게임 개발은 도메인이 독립적인 경우가 많습니다 (UI vs 물리 vs AI). Worktree를 활용해 여러 Claude 세션을 동시에 구동하세요:

```bash
# 병렬 worktree 예시 — 각 도메인을 독립 브랜치로
git worktree add ../unity-ui    feature/ui-overhaul      # Rachael 담당
git worktree add ../unity-ai    feature/enemy-ai         # Sonny + TARS 담당
git worktree add ../unity-audio feature/audio-system     # Bishop 담당

# 각 터미널에서 독립 실행
cd ../unity-ui   && claude   # UI 작업
cd ../unity-ai   && claude   # AI 작업
cd ../unity-audio && claude  # 오디오 작업
```

**Unity worktree 주의사항**:
- `Library/` 폴더는 각 worktree가 독립 보유 (용량 증가 예상)
- `ProjectSettings/`는 공유되므로 worktree 간 충돌 주의
- `.meta` 파일은 원본 브랜치 기준으로 관리

---

## 온디맨드 안전 훅 — Unity Safe Mode

파일 구조 리팩토링, 에셋 이동 등 위험한 작업 전에 활성화:

```
/unity-safe-mode
```

활성화하면 아래 작업이 세션 동안 자동 차단됩니다:
- `*.meta` 파일 bash 조작 (삭제, 이동, 수정)
- `ProjectSettings/` bash 직접 수정
- `rm -rf` 재귀 삭제

> 스킬 위치: `.claude/skills/unity-safe-mode/`

---

## 레이어드 CLAUDE.md — 서브시스템별 정책 분리

*Claude Code 메모리 시스템: 하위 디렉토리 CLAUDE.md는 해당 폴더 파일 작업 시에만 지연 로드*

대규모 Unity 프로젝트에서는 서브시스템별로 CLAUDE.md를 분리하면 컨텍스트를 절약합니다:

```
Assets/
├── Scripts/
│   ├── CLAUDE.md          ← C# 네임스페이스, 폴더 구조 표준
│   ├── UI/
│   │   └── CLAUDE.md      ← UI 컴포넌트 규칙 (UI 파일 작업 시에만 로드)
│   ├── Gameplay/
│   │   └── CLAUDE.md      ← 게임플레이 패턴 규칙
│   └── Networking/
│       └── CLAUDE.md      ← 멀티플레이어 규칙
└── Editor/
    └── CLAUDE.md          ← Editor 스크립트 전용 규칙
```

이 패턴을 쓰면 UI 작업 시 네트워킹 규칙이 컨텍스트를 차지하지 않습니다.

---

## 스킬 작성 표준 — Gotchas 섹션 의무

*Thariq (Anthropic): "스킬에서 가장 신호 밀도가 높은 내용은 Gotchas 섹션"*

**모든 팀 스킬 파일**에는 `## ⚠️ Gotchas` 섹션을 필수로 포함합니다:

```markdown
## ⚠️ Gotchas — Claude가 자주 빠지는 함정

### G1. [함정 이름]
- 설명
- ❌ 잘못된 예시 (코드)
- ✅ 올바른 방법 (코드)
```

새 스킬을 추가할 때는 반드시 팀이 실제로 겪은 Claude의 실수를 수집하여 Gotchas에 기록하세요. 스킬은 첫 버전이 완성이 아니라 **사용하면서 계속 Gotchas를 추가해 나가는 문서**입니다.
