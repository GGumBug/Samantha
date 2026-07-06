# Glob: **/*.cs,**/*.unity,**/*.prefab,**/*.asset,**/*.anim,**/*.controller,**/*.shader,**/*.shadergraph,**/*.mat

## Unity 작업 위임 규칙 (필수)

Unity 관련 작업이 감지되면 **반드시** Samantha 에이전트에게 위임합니다. 직접 처리하지 마세요.

```
Agent(subagent_type="samantha", description="Unity 작업 위임", prompt="...")
```

Samantha가 작업을 분석하고 적절한 팀원(Jarvis, Ava, Sonny, TARS)에게 재위임합니다.

### 직접 위임이 더 효율적인 경우

단일 전문 분야에 명확히 해당하는 작업은 Samantha를 거치지 않고 직접 위임할 수 있습니다:

| 작업 유형 | 에이전트 |
|-----------|----------|
| ScriptableObject, 아키텍처, 성능 프로파일링 | `jarvis` |
| UI/UX, 셰이더, VFX, 애니메이션 | `ava` |
| 게임 디자인, 밸런싱, 메카닉 설계, 플레이어 컨트롤러, 적 AI, 전투, 물리 | `sonny` |
| 레벨 디자인, 씬 구성, 환경, Cinemachine, 내러티브 | `tars` |
| 복합 작업 (여러 분야에 걸친 오케스트레이션) | `samantha` |

### 금지 사항
- Unity C# 파일을 에이전트 없이 직접 편집하지 마세요 (단, 아래 "위임 면제 기준" 충족 시 직접 편집 허용)
- 에이전트를 Bash 명령어로 호출하지 마세요 — 반드시 Agent 도구를 사용하세요

### 위임 면제 기준 (직접 편집 허용)

Unity C# 파일이라도 **모든** 조건을 충족하면 에이전트 위임 없이 직접 편집해 위임 비용(프롬프트 작성·결과 검증·토큰)을 절약합니다. 룰의 의도는 "전문 영역 보호"이지 "trivial 변경의 의식화"가 아닙니다.

**모든 조건 충족 시 직접 편집 허용**:
- 단일 파일 변경
- 1~3줄 추가/삭제 (공백·주석 제외)
- 로직 분기·시그니처·public API 변경 없음 (예: 진단 로그 추가/제거, 명백한 오타 수정, dead `using` 제거)
- 이미 존재하는 메서드/필드의 단순 호출 추가가 아닌, 기존 코드의 좁은 수정만

**직접 편집 후에도 의무**:
- 메인 응답에 헌법 자가 검증 단락 한 줄 (위반 없으면 생략 가능, `engineering-constitution.md §7` 보고 정책 따름)
- `git diff --stat` + 변경 파일 grep 검증을 직접 실행해 결과 보고
- 면제 기준 중 하나라도 의심되면 위임으로 복귀

**여전히 위임 필수**:
- 다파일 변경, 4줄 이상, 시그니처/public API 변경
- 새 메서드/클래스/인터페이스 신설
- SSOT 통합·리팩토링·아키텍처 변경
- `.meta`/`.asset`/`.prefab` 등 Unity 직렬화 파일 수정

(2026-04-27 row-lock 작업 회고: Sonny 위임 6번 중 진단 로그 추가/제거 2번은 이 면제 기준에 해당. 위임 비용 약 30% 절감 가능 추산)

### 위임 종료 시 워킹트리 전체 인지 의무 (필수)

위임이 끝나고 사용자에게 보고하기 전에 **반드시 `git status --short` 전체를 확인**하고, 위임 작업과 무관한 변경(디버깅 흔적, 자동 갱신된 `.asset`, 의도 외 수정)이 있으면 보고에 **별도 강조**한다.

**의무 보고 형식**:

```
## 작업 범위 외 변경 발견 (사용자 결정 필요)
- {파일 경로}: {변경 요약 1줄}
- ...
```

**처리 옵션 항상 함께 제시**:
- (A) 커밋에서 제외 (의도된 디버깅이라면) — 작업 파일만 명시 add
- (B) 되돌리기 (`git checkout -- {파일}`)
- (C) 별도 커밋 (의도된 변경이라면)

**왜 의무인가**: 광범위 add(`git add .` / `git add -A`) 시 의도 외 변경이 함께 끌려들어가 게임 밸런스 깨짐, 임시 디버그 값 commit, 비밀 노출 등 심각한 결과 가능. 시니어 검토의 본질은 "내가 의도한 것 외에 무엇이 따라오는가"를 점검하는 것.

(2026-04-27 옵션 5b/2 작업 시 Monster_101~110 .asset 10개의 maxHP=1 디버깅 흔적이 working tree에 있었던 사례 — 사용자가 직접 발견 전까지 격리 안 됨)

### 병렬 위임 원칙 (필수)

- 독립적인 Unity 작업이 2개 이상이면 **단일 메시지에 여러 Agent 호출**로 병렬 실행합니다 (예: 아키텍처 리팩토링 + UI 색상 수정 → Jarvis + Ava 병렬)
- **Samantha 우회**: 서브에이전트는 내부에서 Agent/Task 도구를 쓸 수 없으므로, 병렬 위임이 명확한 복합 작업이라면 Samantha를 거치지 말고 상위 세션에서 Jarvis/Ava/Sonny/TARS를 직접 병렬 호출합니다. Samantha는 작업 분석이 모호하거나 순차적 오케스트레이션이 필요할 때만 사용합니다. (2026-04-15 Shop 노드 통합에서 Jarvis+Ava+Sonny 병렬 3호출로 약 2.3배 속도 향상 검증)
- **단일 에이전트 5개 항목 한계**: 한 에이전트 호출에 독립 항목을 5개 초과 몰아주면 `maxTurns: 25` 제한에 걸려 보고가 잘리고 일부 항목이 누락됩니다. 5개 초과면 ① 병렬로 분할 또는 ② 순차 호출(1차 → 검증 → 2차).

### 시각 버그 위임 우선순위 (Ava)

UI 미표시·반투명·색상 이상 등 Unity 시각 버그는 **코드/asset 수정 전에 Inspector 확인을 우선**합니다. Ava 위임 프롬프트에 반드시 명시: "Button.Disabled Color, SerializeField 할당, CanvasGroup.alpha를 코드 수정 전에 먼저 의심하고, 같은 가설 2회 실패 시 사용자에게 Inspector 확인을 요청하라".

**prefab 시각 회귀 시 git diff 우선 의무**: 사용자가 "어제까지 멀쩡했는데 이상해짐" 같이 회귀를 보고하면 Ava 위임 프롬프트 1순위는 **`git diff <prefab>` + `git log --oneline <prefab>`** 으로 변경 이력 확인. 코드/asset 수정 시도보다 먼저. 직접 의심한 컴포넌트 외 어떤 필드가 함께 바뀌었는지 diff 가 가장 빠른 답을 준다 (특히 prefab variant 의 modifications 블록).

### 리팩토링 위임 체크리스트

심볼 제거·시그니처 변경·인라인 추출 위임 시 프롬프트에 명시:

- [ ] 제거 대상 심볼을 `\.MethodName\(` 같이 **메서드 이름만 grep**하고 괄호 안은 육안 검토 (파라미터 값 기준 grep은 누락 유발)
- [ ] 사용처를 목록화한 후 **모든 수정을 한 번에** 위임 (분산하면 컴파일 에러)
- [ ] 인라인→유틸 추출이라면 **추출 전 책임 목록화 + 추출 후 책임 매핑**을 프롬프트에 명시하고 "기능 동등성 보존" 명시적 요구
- [ ] 기대 시나리오 1-2개 명시 (예: "minFloor=6 LocationType은 actLevel=3에서 추첨되지 않아야 함")
- [ ] **오버로드 추가** 시 원본의 부수 효과를 diff로 나열하고 "새 오버로드가 모든 부수 효과를 복제하는지" 명시 요구 (2026-04-17 `NodeCleared(Vector2Int)` 에서 `IsSelectable=false` 한 줄 누락으로 visible bug 발생)
- [ ] **"현재" 암묵 참조 API 이동** 시(예: `_currentNode`, `_activeSession`): 이동 후 호출 시점의 포인터 타이밍을 명시하고, 필요 시 명시 파라미터(좌표/ID) 기반 오버로드 요구
- [ ] **SSOT 통합 위임** 시 프롬프트에 5요소 모두 포함: ① 단일 진입점 메서드명 ② 모든 호출자 grep 결과 ③ 부수효과 매트릭스 ④ 통합 후 레거시 진입점 제거 의무 ⑤ 종료 게이트 grep 패턴 (`refactoring-lessons.md §12.5` 6항목 참조)
- [ ] **패턴 미러링 보고 시 코드 형태 grep 비교 + 인용 의무**: "다른 노드 N곳 참고/미러링" 보고 시 실제 grep 결과로 현재 편집 코드와 참고 코드의 정확한 형태(가드 유무, 호출 순서, lazy-init 여부 등)를 인용해야 함. "패턴을 따랐다" 자체 정당화 회피 (헌법 §0 메타 원칙). (2026-04-27 Treasure 부트 보장 인시던트: `if (HasInstance)` 가드가 다른 노드 11곳 패턴(가드 없이 `Instance` 직접 호출)과 코드 형태가 달라 lazy-init을 막아 race 유지)
- [ ] **패턴 미러링 — 코드 형태 grep + "적용 영역 일치" 분리 검증 의무**: grep 으로 코드 형태 일치만으로는 부족. 각 미러링 사례의 **"패턴 적용 영역"이 현재 작업과 일치하는지** 명시 검증 — ① 시간축 적용 영역(부트 의존 / 상태 의존 / 라이프사이클 단계) ② 호출 시점 의존성(lazy-init 트리거 필요 여부 / Singleton 부트 race 가능성). 영역이 다른 미러링은 **무효 정당화** — 코드 형태만 같아도 함정 가능. (2026-05-12 btnMap race fix: `HasInstance` 가드 다른 viewer 6곳 미러링 보고했으나 6곳 모두 상태 의존 컨텍스트, UIGame.OnEnable 만 부트 의존 → 영역 mismatch 로 race 발생. 상세 [best-practice/race-fix-meta-patterns.md](../../best-practice/race-fix-meta-patterns.md) §7)
- [ ] **신규 시그니처 사용 시 Unity C# 버전 호환 확인** (record struct/required member/file-scoped types 등은 LangVersion override 필요). 상세 [best-practice/unity-csharp-version-check.md](../../best-practice/unity-csharp-version-check.md)

상세:
- [best-practice/refactoring-lessons.md](../../best-practice/refactoring-lessons.md) — 일반 리팩토링 교훈
- [best-practice/node-lifecycle-patterns.md](../../best-practice/node-lifecycle-patterns.md) — 상태 머신·노드 생명주기 패턴

### 위임 prompt 범위 보존 의무 (필수)

위임 prompt 는 **사용자가 명시한 작업 범위만** 포함한다. 에이전트가 "겸사겸사 다른 부분도 정리할까?" / "관련 파일도 함께 수정?" 같이 **범위 외 작업을 자가 확장**하면 다음 사고 발생:

- 의도 외 변경이 working tree 에 누적 (헌법 §unity-delegation 워킹트리 인지 의무로도 사후 발견 비용 큼)
- 사용자 검증 부담 폭발 — "내가 부탁한 것 외에 무엇이 바뀌었나" 추적
- 위임 비용/turn 낭비 — 한 번에 너무 많이 하다 `maxTurns=25` 절단

**필수 prompt 골격**:

```
[작업 범위]
- {파일/심볼/시나리오 명시}

[범위 외 작업 금지]
- 같은 파일 안의 다른 수정 / 리팩토링 / 정리 금지
- 발견한 별도 이슈는 보고만 하고 수정 금지 (사용자 결정 후 별도 위임)

[허용된 부수 작업]
- {필요 시: import 정리 / 컴파일 에러 fix 한정}
```

**자가 확장 의심 신호** (위임 결과 점검 시):
- 보고에 "겸사겸사" / "함께" / "관련해서" 같이 작업 확장 표현
- `git diff --stat` 에 prompt 명시 외 파일 등장
- 줄수가 예상보다 1.5배 이상

발견 시 `git restore` 로 범위 외 변경 즉시 롤백 검토 + 사용자 보고.

(2026-05-13 본 세션 회고: 시각 회귀 prompt 에 명시 안 한 컴포넌트 정리가 함께 진행되어 사용자가 별도 검증해야 한 사례)

### 중앙 허브 파일 병렬 작업 직렬화 (필수)

여러 노드 타입/도메인이 **공통 허브 파일**(예: `NodeEntryService`, `PlayerData`, `PlayerRunStateData`, `RoguelikeMapController`)에 훅/필드/API를 추가해야 하는 경우 **반드시 순차 실행**. 병렬 위임하면 같은 파일에 분산 편집이 몰려 merge conflict 또는 중복 구현 발생.

**식별 방법**: 여러 에이전트의 수정 파일 목록에 **같은 파일이 나타나면** 직렬화 후보. 특히 `*Service.cs`, `*Data.cs`, 공통 Enum 정의 파일.

**예외**: Shop/Battle/Camp/Encounter 같이 **도메인이 분리된 파일**(예: `ShopManager`, `BattleManager`)은 안전하게 병렬 가능.

**추가 절대 규칙**: SSOT 단일 진입점 통합 작업(`Mark*NodeEntered`, `NodeCleared`, 저장 SSOT 등)은 **무조건 단일 에이전트 직렬 실행**. 병렬 위임 시 SSOT 자체가 분산 편집으로 깨진다. 도메인이 분리돼 보여도 통합 대상이면 직렬화.

### `.meta` GUID 수동 지정 리스크 (Ava/Jarvis)

에이전트가 Animator `.controller` 또는 `.cs.meta` 파일을 **직접 생성**하면서 GUID를 수동으로 지정하면, Unity 첫 import 시 **재발급**될 수 있음. 결과: prefab의 Script/Asset 참조가 `Missing (Mono Script)` 상태로 깨짐.

**처방**:

- Ava/Jarvis 위임 시 `.meta` 파일 직접 생성이 포함되면 프롬프트 보고 항목에 **"사용자 Unity Editor에서 Missing 참조 확인 필수"** 를 명시하도록 지시
- 가능하면 `.meta` 생성은 Unity Editor의 자동 생성에 맡기고, 에이전트는 `.cs`/`.asset` 본문만 작성

### Unity 자동 prefab mutation 함정 (공유 asset 추가 시)

새 폰트/머터리얼/스프라이트/Shader 등 **공유 asset 을 Assets/ 에 추가**하면 Unity 가 import 시점에 기존 prefab 의 reference GUID 를 자동 교체하는 사고가 발생할 수 있다. 결과: 작업 범위 외 prefab 들이 `Modified` 상태로 working tree 에 등장.

**증상**:
- `git status` 에 위임 작업과 무관한 `.prefab` 다수 등장
- prefab modifications 블록에 `m_FontAsset` / `m_Material` / `m_Sprite` 등 GUID 만 변경된 entry
- Inspector 에서 "보이는 폰트는 같은데 GUID 가 다른 asset 가리킴"

**처방** (헌법 §unity-delegation "워킹트리 인지 의무" 와 cross-link):

- 공유 asset (`*.ttf` / `*.asset` TMP_FontAsset / `*.mat` / `*.png` 등) 추가가 포함된 위임 종료 직후 **`git status` 전체 점검 의무**
- 의도한 prefab (예: UIMapView, UITutorialGuidePanel) 외 prefab mutation 발견 시 사용자 보고 + (A) 의도 적용 / (B) `git restore` 옵션 제시
- 사전 예방: 공유 asset 추가 위임 prompt 에 "**asset import 후 `git status` 로 의도 외 prefab mutation 확인 + 사용자 보고**" 의무 명시

(2026-05-14 RIDIBatang 폰트 추가 인시던트: `1e51495b` 커밋에서 UIMapView 의 TMP_Text fontAsset GUID 가 자동 교체되어 의도된 폰트 마이그레이션과 함께 의도 외 prefab modification 도 발생. 사용자가 직접 발견 전까지 격리 안 됨)

### 서브에이전트 Read 권한 사전 점검

`.claude/settings.json`의 `permissions.allow`에 `Read(*)` 또는 Unity 작업 영역 경로가 누락된 경우, 서브에이전트가 Samantha 디렉토리 밖 파일(예: `../Assets/`)을 **Read 불가**. Interactive 승인이 필요하므로 백그라운드 에이전트는 즉시 실패.

**증상**: Jarvis/Sonny가 "해당 파일을 읽을 수 없습니다" 로 조기 종료.

**처방**:

- Unity 프로젝트 작업 시 `.claude/settings.json`의 `permissions.allow`에 `"Read(*)"` 포함 여부 **사전 점검**
- 2026-04-24 Jarvis Stage 2a 차단 인시던트로 확인된 실제 실패 모드 — permission 수정 후 재위임으로 복구

### Sonny `maxTurns=25` 절단 감지 (중요)

Sonny가 복잡한 다파일 작업에서 `maxTurns=25` 제한으로 중단되는 경우가 잦음. **절단 시점의 90%는 "검증 쿼리" 단계**(편집 완료 **후**) — 사용자가 "이미 편집이 끝난 상태"를 놓치기 쉬움.

**처방**:

1. **재위임 전 반드시 `git diff --stat`으로 실제 수정 상태 확인** — 파일이 이미 수정되어 있으면 재수정 금지
2. 절단 보고가 "확인합니다 / 검토합니다" 같은 탐색 메시지로 끝나면 **편집은 끝났을 가능성 80%+**
3. 재위임이 필요한 경우 프롬프트에 "**편집만 하고 검증/분석은 생략**, 보고는 3줄 이내" 명시
4. 보고서 포맷을 사전에 좁혀 고정 (섹션 수, 줄 수 상한)

**예방**:

- 파일 5개 이상 수정 예상 시 **Part A/B 분할**로 각 15 turn 이내로 설계
- 한 에이전트에 "감사(read-only)" + "구현(edit)"을 동시에 시키지 말 것 — 분리 호출
