# Glob: **/*.cs,**/*.unity,**/*.prefab,**/*.asset,**/*.anim,**/*.controller,**/*.shader,**/*.shadergraph,**/*.mat

## 엔지니어링 헌법 (사용자 명시 없이 항상 적용 — 단, 상황 적합성 우선)

Unity 코드 작업 시 **사용자가 매번 요구하지 않아도** 다음 원칙들을 자동 적용합니다. 사용자가 "SOLID 지켜줘", "SSOT 고려해줘", "디자인 패턴 써줘", "유지보수/확장성 챙겨줘" 같은 말을 다시 할 필요가 없도록 박제된 기본값입니다.

> 이 헌법은 Samantha/Jarvis/Sonny/Ava/TARS 모두에게 자동 적용됩니다. **단일 진실 원천은 이 파일 하나** — 다른 곳에 복사 금지(DRY).

### 0. 메타 원칙 — 헌법이 오버엔지니어링이 되지 않도록

이 헌법 자체가 코드보다 비대해지면 안 됩니다. **원칙은 비용 0이 아닙니다.**

- 패턴/추상화 도입은 항상 비용(가독성↓, 신규 진입자 학습 비용↑, 디버깅 stack frame↑)을 동반함
- "원칙을 적용하지 않는 것"이 더 시니어한 결정인 경우가 자주 있음 — 이 판단을 회피하지 말 것
- "원칙대로 했다"가 자체 정당화가 될 수 없음. 항상 **"왜 이 비용을 지불했는가"**가 함께 설명되어야 함
- 시니어 자가 검토는 외부 비판 압력에 비례 — 편집 직전 외부 비판자 시점 6 질문 시뮬레이션 권장 ([best-practice/external-critique-simulation.md](../../best-practice/external-critique-simulation.md))

#### 0-1. Senior Default Mode (모든 변경 작업의 기본 사고 체계)

사용자가 "시니어 판단해줘"라고 매번 말하지 않아도 **모든 코드 변경 작업에 자동 적용**되는 4단계 표준 사고. 누락 시 사고 재발(caller-driven snapshot 사고 패턴 등) 보장.

**Step 1 — 변경 전 영향 분석 (Before 자동)**:
- grep으로 변경 대상 심볼/패턴의 **모든 호출처/의존처** 식별, 영향 범위를 분류 테이블로 명시 (자동 위임/수동 처리/외부 시스템). "SSOT 어느 축에 영향?" 검증 (코드 식별자 / 사용자 노출 / 메타)
- **상태·플래그·접합부 제거 시 grep 방향은 쓰기 지점이 아니라 읽기 지점 전수**. 제거 대상이 원래 목적 외 독자(정렬·순서·가시성 판정 등)를 달고 있는지 **독자별 의미 분류표**(읽는 곳 / 무엇을 판정하려고 읽는가 / 이관 후 대체 채널)를 작성하고, "대체 채널 없음" 행이 0이 될 때까지 이관 미완료로 취급. 제거 대상이 나르던 것이 값이 아니라 **보장(순서·배타·정지)** 이면 컴파일·테스트·정적 grep 어디에도 안 걸리고 시각 회귀로만 드러난다. 상세 [best-practice/implicit-proxy-state-removal.md](../../best-practice/implicit-proxy-state-removal.md). (2026-08-04 카드 연출 채널 이관: 같은 계급 누락 3회, 그중 2회가 사용자 재현에서야 발견)
- **상속 계층 분석 시 `: BaseClass\b` grep + 결과 표 작성 의무**. 사전 조사를 일부 종에 제한 금지 — grep 결과 모두 포함 (2026-04-30 Category 18건 + TooltipTarget 발견)
- **사용자 의도 모호 질문(예: "~는 어떻게 된거지?")은 부분 마이그레이션 누락 노출 신호** — 답변 전 grep 전수 검사 의무
- **자산 마이그레이션 script 작성 시 파일명 정렬 vs 시트 Code Name 정렬의 case sensitivity 일관성 사전 검증 의무** — 상세 [best-practice/asset-migration-sort-consistency.md](../../best-practice/asset-migration-sort-consistency.md)
- **Unity 라이프사이클 메시지(`Awake`/`Start`/`OnEnable`/`OnDestroy`) 신설 시 부모 클래스 grep 의무** — Unity 메시지는 reflection 기반이라 자식 정의 시 부모 호출 누락 위험 (`override` 강제 없음, 컴파일러/IDE 경고 없음). 상세 [best-practice/unity-lifecycle-message-override.md](../../best-practice/unity-lifecycle-message-override.md). (2026-05-12 UIShop Awake 가로채기 회귀 인시던트)

**Step 2 — 합리화 회피 (During 자동)**:
다음 표현이 머릿속에 떠오르면 **즉시 SSOT 위반/책임 회피 신호**로 판정:
- ❌ "이번엔 영향 작음" / "transient라 괜찮음"
- ❌ "Quick fix로 일단" / "나중에 정리"
- ❌ "caller가 항상 직접 호출하니" / "dead path니까"
- ❌ "단순 수정이라 검증 생략"
- ❌ "코드 형태로 디자인 의도 단정" — config 필드 유무/호출 패턴 등은 의도 추론 1회까지, 단정 시 사용자 확인 1차 시도. (2026-05-12 ShopSystemConfig `PriceIncreasePerUse` 존재로 "반복 사용 디자인" 추론 → 실제 1회성 솔드아웃 의도 위배)
- ❌ "이번엔 단순하니 측정 생략" / "코드 분석으로 충분" — 같은 영역 2회 추측 fix 시 **측정 도구 작성 의무**. 정적 안전성/grep/시뮬레이션은 시간축·확률·분포 버그 검증 불가. 상세 [best-practice/measurement-driven-debug.md](../../best-practice/measurement-driven-debug.md). (2026-05-13 본 세션 박제)

위 표현 시도 시 자동 차단 → 옵션 (A) 근본 해결 우선 검토. (C) Quick fix는 사용자 명시 승인 + 후속 task 등록 필수.

**Step 3 — 표준 검증 시나리오 (After 자동)**:
변경 종류별 최소 검증 시나리오. 통과 안 하면 작업 미완료.

| 변경 종류 | 표준 시나리오 |
|-----------|---------------|
| L10n / 다국어 | ① 정상 표시 ② 언어 전환 갱신 ③ **활성 중 토글 자동 갱신** ④ missing key 0 |
| 상태 머신 / 노드 라이프사이클 | ① 정상 진입 ② 재진입 ③ **취소/롤백 시 잔재 0** ④ 양방향 불변식 |
| 비동기 / UniTask | ① 정상 완료 ② **OnDestroy 중 취소** ③ 재진입 atomicity ④ exception 흡수 |
| 리팩토링 / 시그니처 변경 | ① 호출처 grep 0건 ② **부수효과 매트릭스 등가성** ③ revert 안전 |
| 신기능 / API 추가 | ① 정상 호출 ② **null/empty/edge case** ③ 의존성 boundary 격리 |
| 비동기 라이프사이클 / Singleton 부트 race | ① 정상 부트 순서 ② **view OnEnable 시점 매니저 미부트 (lazy-init 가드 함정)** ③ Scene 전환 시 인스턴스 교체 ④ 시간축 안전성 evidence (HasInstance(before) / InstanceID 진단) |

(2026-05-12 btnMap race fix 인시던트: Sonny 1차 "race 안전" 단정이 정적 안전성만 검증, 시간축 미검증. [best-practice/race-fix-meta-patterns.md](../../best-practice/race-fix-meta-patterns.md) §6+§7 박제)

**Step 4 — 사용자 보고 시 시니어 판단 명시 (After 자동)**:
- 합리화 시도가 차단됐는지 명시
- 표준 검증 시나리오 통과 명시
- 트레이드오프 발생 시 헌법 §7 보고 적용
- "활성 중 토글" 같은 핵심 시나리오는 별도 항목으로 가시화

(2026-04-29 RewardButton string snapshot 사고 + 사용자 요청 박제. 메타 원칙으로 모든 변경 작업에 자동 적용)

### 1. SOLID 5원칙 (기본값 — 회색 지대는 트레이드오프 보고)

| 원칙 | 적용 기준 | 회색 지대 신호 |
|------|----------|---------------|
| **S**ingle Responsibility | 하나의 변경 이유만. 200줄 클래스, 50줄 메서드는 분리 검토 | "분리하면 호출 사슬만 길어지고 응집도가 떨어진다" — 그대로 두고 보고 |
| **O**pen/Closed | `if/switch` 타입 분기 3개 이상이면 Strategy/State 검토 | 분기가 2개 이하거나 추가 가능성이 없으면 분기 유지가 더 단순 |
| **L**iskov Substitution | 하위 타입은 상위 계약을 깨지 않음. `is/cast` 후 분기는 LSP 의심 | Unity API(`MonoBehaviour` 계열) 자체가 LSP 깨는 사례 — 어쩔 수 없음 인정 |
| **I**nterface Segregation | 클라이언트가 안 쓰는 메서드를 인터페이스에 두지 않음 | 인터페이스 1개를 2개로 쪼개는 비용 > 이득이면 그대로 |
| **D**ependency Inversion | 구체 클래스 의존 금지. 생성자 주입 우선. Singleton/ServiceLocator는 boundary에서만 | Unity Scene 생명주기상 boundary가 도메인까지 침투하는 건 인정 — 단, 격리 시도는 한다 |

명백한 위반은 자체 거부 후 대안 제시. 회색 지대는 **"왜 이 트레이드오프를 선택했나" 한 줄 보고**로 충분.

### 2. SSOT (Single Source of Truth)

- **상태/규칙/식별자는 단 한 곳에서 정의**. 같은 데이터가 두 곳에 있으면 둘 중 하나는 derive(파생).
- 디스크 저장이 따라오는 변경은 **단일 진입점 메서드**로 통합 (예: `MarkBattleRewardPending`, `NodeCleared`).
- "단일 경로" 통합 시 **시점/관심사**까지 함께 묶이는지 검토 — 시점이 다른 관심사는 분리 (예: `IsCleared` SSOT vs `IsSelectable` row-lock 분리).
- 호출자 grep으로 **모든 진입점이 단일 SSOT를 거치는지** 확인 후 보고.
- 통합 후 **레거시 진입점은 반드시 제거** — 둘 다 살아있으면 SSOT가 아님.

#### 2-0. Caller-Driven UI String Snapshot 안티패턴 → [l10n-ssot.md](l10n-ssot.md) 분리

§2-0 (caller-driven snapshot 식별) · §2-0-1 (데이터 흐름 string snapshot 절대 금지) · §2-0-2 (View-Level ILocaleAware 강제) 전문은 [l10n-ssot.md](l10n-ssot.md)에 **동일 섹션 번호로 분리** (200줄 정책). 적용 강제력 동일 (Glob 자동 주입). 핵심 3원칙:

- caller가 `L10n.T(...)` 결과 string을 UI에 전달 금지 — UI는 **키 보존** + `LocaleApplied` 구독 (Observer)
- 데이터 클래스(`*VisualData`/`*ViewData`/`*Model` 등)는 사용자 노출 텍스트 string 보유 금지 — **키만**
- 사용자 노출 UI 컴포넌트는 `ILocaleAware` 구현 의무 — manager/static-event 우회 금지

자동 검증 grep 패턴(위임 시작·종료 시 의무)·금기 합리화·인시던트 상세는 분리 파일 참조.

#### 2-1. 클래스 불변식 캡슐화 — 양방향 검증 의무

setter나 메서드가 **클래스 불변식을 자동으로 유지**하도록 만들 때(예: `IsSelectable=false → outgoing edges Inactive` 자동 동기화), **반대 방향도 항상 참인지 명시적으로 검증**한다:

- "한쪽 방향이 자동화되어 있으면 반대 방향도 자동화하면 자연스럽다"는 잘못된 직관
- 한쪽만 항상 참이면 **한쪽만 자동화** — 반대 방향은 호출자 컨텍스트(현재 선택된 노드인가? 등)가 필요해 모델이 알 수 없는 정보에 의존
- 양방향 자동화는 호출자 컨텍스트 누락 시 **두 단계 앞 부작용**(예: 다음 노드의 outgoing이 미리 노란색)을 만들기 쉬움
- 결정 시 다음 두 명제를 명시 검증: ① "X=true → Y" 는 항상 참인가? ② "X=false → ¬Y" 는 항상 참인가? 둘 다 참이 아니면 한쪽만 자동화

(2026-04-27 옵션 5 → 5b 회귀 사례: `MapNode.IsSelectable=true → outgoing Available` 양방향 자동화가 두 단계 앞 노란색 잔재 유발)

SSOT는 SOLID보다 양보 폭이 좁습니다. "두 곳에 같은 상태"는 거의 항상 버그.

### 3. 디자인 패턴 우선순위 (3회 반복 또는 확장 요구 명확 시에만)

| 상황 | 권장 패턴 |
|------|----------|
| 행동의 런타임 교체 | Strategy |
| 상태 전이 + 행동 변화 | State |
| 객체 생성 분기 | Factory / Abstract Factory |
| 1:N 알림 | Observer / Event |
| 작업의 큐잉/Undo | Command |
| 알고리즘 골격 + 가변 단계 | Template Method |
| 외부 시스템 격리 | Adapter / Facade |

**금기**: GoF 패턴 자체를 위한 패턴 적용 금지. **3회 반복** 또는 **확장 요구가 명확**할 때만 도입. 1·2회 반복은 인라인 유지가 더 단순.

### 4. 유지보수성 / 확장성 체크리스트

- [ ] **명명**: 의도가 드러나는 이름. `Manager`, `Helper`, `Util` 같은 책임 모호한 접미사 지양
- [ ] **부수효과 가시화**: 시그니처에서 부수효과(저장, 이벤트 발행, 전역 상태 변경)가 예측 가능한지
- [ ] **테스트 가능성**: 의존성 주입으로 단위 테스트 가능한 형태인지. `Time.deltaTime`/`UnityEngine.Random`은 추상화
- [ ] **결정론**: RNG/시간/씬 로딩은 `RunRngService.ForSubsystem(label)` 같은 라벨 기반 SSOT 경유
- [ ] **삭제 용이성**: 기능 제거 시 영향 파일이 5개 이하로 국소화되는지
- [ ] **MonoBehaviour 비대화 방지**: `MonoBehaviour`는 Unity 라이프사이클 어댑터, 도메인 로직은 POCO 분리
- [ ] **POCO 단위 테스트 검토**: `MonoBehaviour` 의존성 없는 POCO(예: `MapNode.IsSelectable` setter, `ResolveFromNodeOutgoingEdgesAfterSelection` 같은 순수 메서드)는 NUnit 단위 테스트 작성 검토. 강제는 아니지만, 클래스 불변식이나 상태 전이를 다루는 코드는 테스트가 회귀 방지 비용 대비 가치가 큼. 테스트 작성을 생략하기로 결정한 경우 보고에 한 줄 사유 명시.

### 5. 오버엔지니어링 안티패턴 (적극 회피)

원칙을 적용한다는 명분으로 다음을 만들면 헌법 위반:

- **사용처 1곳뿐인 인터페이스/추상 클래스** — 모킹 의도가 명확하지 않으면 구체 클래스로 충분
- **확장 가능성 추측에 기반한 패턴 도입** — "나중에 늘어날 수도 있으니 Strategy 미리 깔자" 금지. 늘어날 때 도입.
- **5줄 메서드를 3개로 쪼개기 / DI 컨테이너 도입 위한 DI 컨테이너** — SRP 위반 신호 없으면 인라인. Unity 수동 주입으로 충분.
- **이벤트 남발** — 호출 사슬이 명확한 1:1 호출은 직접 호출이 디버깅에 유리
- **호출자가 .Forget()으로 결과 무시하는 비동기 stub** — 채우기보다 제거 검토. 상세 [best-practice/dead-stub-pattern.md](../../best-practice/dead-stub-pattern.md).
- **헌법 검증 단락을 형식적으로 채우기** — 위반/트레이드오프 없으면 단락 자체를 생략

YAGNI(You Aren't Gonna Need It)가 SOLID보다 우선하는 경우가 자주 있음.

**Dead Path 우선 검증 의무**: 마이그레이션 대상 발견 시 **사용처 grep으로 dead path 가능성 우선 검증** — 제거 옵션을 마이그레이션보다 먼저 검토. (2026-04-30 Camp success message 체인 dead path 사례 — 옵션 A -60 LoC 채택. 본 세션 §5 YAGNI 적용 4건 누적: UICardRemovalPanel 삭제 / Camp dead path / Dialogue.Title / Category 시트 통합)

### 6. Escape Hatch (헌법 완화 허용 상황)

다음 컨텍스트에서는 헌법을 완화합니다 — 단, 보고에 **"이건 X이므로 헌법 완화 적용"** 명시:

- **프로토타입/PoC/스파이크**: 동작 검증이 목적, 폐기 예정 코드. SOLID 강제 = 비용 낭비
- **긴급 hotfix**: 운영 중단 복구 우선, 리팩토링은 후속 PR
- **외부 API 미러링**: Unity/3rd-party API 형태를 그대로 따라야 하는 어댑터 코드
- **데이터 클래스/POCO**: getter/setter만 있는 DTO는 SOLID 평가 대상 아님
- **에디터 전용 스크립트**: 런타임 영향 없음, 빠른 작성 우선

### 7. 보고 정책 (양식주의 회피)

- **위반/트레이드오프가 없으면 별도 헌법 단락 생략**. 평소 보고는 평소대로 간결하게.
- **위반/회색 지대 발생 시에만** 다음 한 줄 추가:
  ```
  ## 트레이드오프
  [어느 원칙을 / 어떻게 양보했는가 / 왜]
  ```
- **명백한 SOLID/SSOT 위반은 보고하지 말고 자체 수정** 후 결과만 보고
- 보고에 패턴/원칙 이름을 나열하는 것보다 **"이 코드가 6개월 뒤 누가 봐도 변경 가능한가"**를 자가 점검

### 8. 장기 회고 메커니즘 (세션 휘발 방지)

세션 안에서 발견한 **회귀/실수 패턴**(예: 양방향 불변식 잘못 정의, 워킹트리 격리 실패)이 다음 세션에 전달되지 않으면 같은 실수가 반복됩니다. 휘발 방지를 위해:

- 한 세션에서 **회귀가 1회 이상 발생**했거나 **사용자가 시니어 검토자 역할로 잡아낸 약점**이 있으면, 세션 종료 직전 `/reflect` 스킬을 호출 권장
- `/reflect`는 `reflection-curator` 에이전트를 호출해 인사이트를 `.claude/` 또는 `best-practice/`에 박제할지 사용자에게 확인 후 적용
- 박제 대상 우선순위: ① 옵션 회귀 케이스(예: 옵션 5 → 5b) ② 헌법으로 잡지 못한 실패 패턴 ③ 위임 비용/가치 ROI 데이터
- 회고가 박제되지 않은 채 세션이 끝나면, "사용자가 다음 번에 같은 지적을 또 해야 함" — 이건 헌법 §0 메타 원칙 위반(사용자에게 부담 떠넘김)
