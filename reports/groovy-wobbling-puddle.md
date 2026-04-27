# Samantha 저장소 업데이트 계획 (자산화 → 압축)

## Context

### 동기
이번 Hwaseo 작업 세션에서 SSOT(Single Source of Truth) + Strategy + Template Method 패턴이 노드 시스템에 깊게 적용됐고, 사용자가 이 구조를 마음에 들어 했다. 동시에 Samantha 저장소가 점진적으로 비대해져(현재 93파일 / 18,390줄 / 10.9M) 검색 효율과 가시성이 떨어지기 시작했다. 사용자는 두 가지를 동시에 원한다:

1. **SSOT 패턴을 자산으로 박제** — 미래 위임 시 1줄 인용으로 활용 가능한 체크리스트로
2. **누적된 데이터 압축** — 사례 나열 대신 **방법론적 정리** (When/Then 결정 규칙, 운영 체크리스트)

### 의도된 결과
- 자산화 후: 새 SSOT 작업 위임 시 `refactoring-lessons.md §12.5 6항목 충족` 같이 1줄 참조 가능
- 압축 후: `reports/claude-*.md` 8개(~1,937줄)를 4개(~410줄, **78% 감축**) 결정 규칙 문서로 재구성, 원본은 `reports/archive/` 보존

### 압축 금지 영역 (탐색 중 발견)
`best-practice/claude-*.md` 8개는 **drift-tracking workflow 인프라**와 1:1 결합 (`workflow-claude-*-agent.md` 8개 + `changelog/best-practice/claude-*/` 8개). 압축 시도 시 24개 자산이 동시에 깨지므로 **절대 손대지 않는다**.

---

## Part 1. 자산화 (먼저 실행, 약 25분)

총 +95줄 추가. 모든 항목은 명령형 체크리스트(`- [ ] 동사~`).

### 1A. `best-practice/refactoring-lessons.md` (+18줄)
**위치**: §12 직후 §12.5 신설 — "SSOT 단일 진입점 보존"

체크리스트 6항목:
- 동일 도메인 액션이 N곳에 흩어졌으면 단일 진입점부터 식별
- 오버로드 추가 시 원본 부수효과를 diff로 나열, 새 오버로드 매핑 표
- 호출자 분기가 타이밍 의존이면 SSOT를 명시 파라미터(좌표/ID)로 강제, 무파라미터 폐기
- SSOT 식별 grep 패턴: `\.MethodName\(` (이름만)
- SSOT 통합 후 레거시 진입점 즉시 제거
- 종료 게이트: `grep -rn "OldEntryPoint(" → 0건`

### 1B. `best-practice/node-persistence-matrix.md` (+15줄)
**위치**: §"계약" 직후 §"저장 SSOT" 신설

체크리스트 5항목:
- 노드 진입 저장은 `Mark*NodeEntered` 단일 메서드만 호출, `PlayerData`/`PlayerRunStateData` 직접 set 금지
- 진입 SSOT는 (a) 좌표 정규화 (b) Phase 전이 (c) commit 트리거 3종을 한 곳에서
- 새 노드 타입은 진입 SSOT의 Switch/Strategy 1줄 추가만 허용, 별도 `Mark*Entered` 신설 금지
- 위반 탐지: `git grep "PlayerRunStateData\\." -- '*Manager.cs' '*Service.cs'`에서 Mark 미경유 위반
- 매트릭스 "타이밍" 칸 변경 시 SSOT 메서드 분기 표 동기화 의무

### 1C. `best-practice/node-lifecycle-patterns.md` (+12줄)
**위치**: §2 말미에 §2.1 신설 — "Map SSOT 클리어 진입점"

체크리스트 4항목:
- 노드 클리어 신호는 `NodeCleared(Vector2Int)` 단일 진입점만, 무파라미터 버전은 위임만
- 클리어 SSOT 부수효과 = `IsCleared=true` + `IsSelectable=false` + 다음노드 활성화 + 저장 트리거 — 4종 모두 복제 검증
- 신규 클리어 트리거 추가 시 SSOT 호출만 허용, 직접 `IsCleared` 세팅 금지
- 위반 grep: `IsCleared\s*=\s*true` → SSOT 외부 위치는 모두 위반

### 1D. `.claude/rules/unity-delegation.md` (+10줄)
**위치 1**: §"리팩토링 위임 체크리스트" 말미에 1불릿
- SSOT 통합 위임 시 프롬프트 5요소(단일 진입점 메서드명 / 호출자 grep 결과 / 부수효과 매트릭스 / 레거시 제거 의무 / 종료 게이트 grep)

**위치 2**: §"중앙 허브 병렬 직렬화" 말미에 1불릿
- SSOT 통합 작업은 무조건 단일 에이전트 직렬, 병렬 위임 금지

### 1E. 신규 `best-practice/determinism-hooks.md` (≈60줄)
**근거**: 결정론 보존 지점이 `refactoring-lessons.md §3`(해시 결정성)과 `node-lifecycle-patterns.md`(재진입)에 산재. 단일 정리 없음.

**구조**:
1. 결정론 불변식 표 (시드 / Phase / IsReentrant / Save 시점) — 5행
2. Hook 지점 체크리스트 (저장 / 로드 / Re-entry / Skip / Auto-clear) — 5항목
3. 재진입 가드 패턴 (Phase 정의 + IsReentrant 조합표) — 3행
4. 안티패턴 3개 (시드 재할당 / Phase skip / 미커밋 상태 재진입)
5. 새 결정론 hook 추가 체크리스트 — 5항목

**Template Method 결정론 박제 사례**: `NodeReentryHandlerBase.EstablishDeterminismContextAsync`를 §2 Hook 지점 체크리스트의 정식 사례로 인용 (1줄 + 파일 링크).

---

## Part 2. 압축 (자산화 후 실행, 약 50분)

### 2A. 그룹화 (사실 기반)

| 그룹 | reports 파일 | 줄수 | 외부 참조 |
|---|---|---|---|
| **A. SDK/시스템 프롬프트** | claude-agent-sdk-vs-cli-system-prompts.md, claude-agent-command-skill.md | 550 | 0 |
| **B. 메모리/설정** | claude-agent-memory.md, claude-global-vs-project-settings.md | 356 | CLAUDE.md:69, presentation-curator.md:101 |
| **C. 운영 한계/도구** | claude-usage-and-rate-limits.md, claude-advanced-tool-use.md, claude-skills-for-larger-mono-repos.md | 686 | 0 |
| **D. 브라우저** | claude-in-chrome-v-chrome-devtools-mcp.md | 345 | workflow-concepts:53, changelog/concepts:238 |

### 2B. 통합 결과물 (4개 신규 파일, 총 ~410줄)

각 파일 동일 헤딩 트리:
1. **결정 규칙 표** (When / Then 두 컬럼)
2. **운영 체크리스트** (사용 전 / 중 / 후)
3. **트레이드오프 매트릭스** (옵션 × 비용/이득)
4. **참조** (원본 외부 docs URL)

```
reports/claude-agent-architecture.md     (~120줄, 그룹 A)
reports/claude-memory-and-settings.md    (~100줄, 그룹 B)
reports/claude-operational-limits.md     (~140줄, 그룹 C)
reports/claude-browser-decision.md       (~50줄, 그룹 D)
```

case study성 인용은 모두 1줄 요약 + 외부 URL로 치환.

### 2C. 원본 처리 (사용자 결정)
- `reports/archive/` 디렉토리 신설
- 8개 원본 파일 `git mv` 로 archive/ 이동 (히스토리 보존)
- 새 4개 파일이 결정 규칙 + 운영 체크리스트 담당, 사례 전체가 필요할 때만 archive/ 조회

### 2D. 링크 갱신 (필수, 총 4곳)
| 위치 | 기존 링크 | 신규 링크 |
|---|---|---|
| `CLAUDE.md:69` | reports/claude-agent-memory.md | reports/claude-memory-and-settings.md |
| `.claude/agents/presentation-curator.md:101` | claude-global-vs-project-settings.md | claude-memory-and-settings.md |
| `.claude/agents/workflows/best-practice/workflow-concepts-agent.md:53` | claude-in-chrome-v-chrome-devtools-mcp.md | claude-browser-decision.md |
| `changelog/best-practice/concepts/changelog.md:238` | claude-in-chrome-v-chrome-devtools-mcp.md | claude-browser-decision.md |

### 2E. README CONCEPTS 표 갱신
- 그룹 D `claude-in-chrome-v-chrome-devtools-mcp.md` BP 뱃지 → 새 경로
- 압축으로 행이 줄어드는 만큼 표 정리

---

## Critical Files

**자산화 (Part 1)**:
- best-practice/refactoring-lessons.md
- best-practice/node-persistence-matrix.md
- best-practice/node-lifecycle-patterns.md
- .claude/rules/unity-delegation.md
- best-practice/determinism-hooks.md (신규)

**압축 (Part 2)**:
- reports/claude-agent-architecture.md (신규)
- reports/claude-memory-and-settings.md (신규)
- reports/claude-operational-limits.md (신규)
- reports/claude-browser-decision.md (신규)
- reports/archive/ (신규 디렉토리, 8개 파일 git mv)
- CLAUDE.md, presentation-curator.md, workflow-concepts-agent.md, changelog 4곳 링크 갱신
- README.md CONCEPTS 표

**재사용 자산 (수정 없음, 인용만)**:
- best-practice/solid-unity-principles.md
- best-practice/evidence-based-debugging.md

---

## 검증 (각 Part 종료 후)

### Part 1 검증
- [ ] 새 체크리스트 5곳 모두 명령형 문장(`- [ ] 동사~`)으로 시작
- [ ] Sonny/Jarvis 위임 프롬프트에 1줄 인용 가능 형태(헤딩 + 번호 안정)
- [ ] determinism-hooks.md 60줄 이하
- [ ] 4개 보강 파일 어느 것도 200줄 초과하지 않음

### Part 2 검증
- [ ] `git mv` 로 8개 원본이 archive/ 이동, git log 추적성 확보
- [ ] 4곳 외부 참조 링크 모두 갱신 (`grep -rn "claude-agent-memory\|claude-global-vs-project-settings\|claude-in-chrome-v-chrome-devtools-mcp"` 결과 archive/ 외 0건)
- [ ] README CONCEPTS 표 BP/RP 행이 새 4파일과 일치
- [ ] 4개 신규 파일 각각 4섹션(결정 규칙/체크리스트/매트릭스/참조) 모두 존재
- [ ] 압축 전후 "When/Then" 항목 수 비교 — 30% 이상 손실 없음

### 종합 검증
- [ ] `wc -l reports/claude-*.md best-practice/*.md` 결과: archive 제외 시 줄수 약 -1,500줄
- [ ] best-practice/claude-*.md 8개 변경 0건 (인프라 보존)
- [ ] git status에 의도하지 않은 변경 없음

---

## 작업량 견적

- Part 1: 약 25분 (체크리스트 작성, 사례는 본 plan에 추출 완료)
- Part 2: 약 50분 (8파일 정독 + 4파일 작성 + 4곳 링크 + archive 이동)
- 총 약 75분, **자산화 → 검증 → 압축 → 검증** 순서

## 위험·완화

| 위험 | 완화 |
|---|---|
| 압축 중 결정 규칙 누락 | 검증 단계에서 "When/Then" 항목 수 30% 임계 비교 |
| 외부 링크 깨짐 | 4곳 링크 갱신 체크리스트 + grep 검증 |
| best-practice/claude-* 실수 압축 | plan 명시 + 작업자에게 24자산 결합 경고 |
| determinism-hooks.md 비대화 | 60줄 상한 검증 |
