[← CLAUDE.md로 돌아가기](../CLAUDE.md)

# SOLID·하드코딩 방지·디자인 패턴 — Unity 적용 카탈로그

Sonny/Jarvis가 **구현 전 자체 점검** 시 참조하는 단일 진실 소스. Unity 특유 제약(MonoBehaviour, Inspector, 씬 로드)을 반영한 실전 적용법.

## SOLID 5원칙 — Unity 예시

### S (Single Responsibility)
하나의 클래스/메서드는 한 가지 책임만. **변경의 이유가 하나**.

- ❌ `PlayerController`가 입력·이동·애니메이션·사운드 모두 담당
- ✅ `PlayerInput` → `PlayerMovement` → `PlayerAnimator` → `PlayerSFX` 분리
- **Hwaseo 사례 (2026-04-17)**: `CampActionExecutor`가 행동 수행 + 저장 두 책임을 가지던 것을 `SaveCurrentData()` 제거로 "행동만" 담당하도록 축소 → 저장은 `NodeEntryService` 단일 책임

### O (Open/Closed)
확장에는 열리고 수정에는 닫혀야. **새 타입 추가 시 기존 코드 수정 금지**.

- ❌ `switch (weaponType)` 로 분기 → 무기 추가마다 switch 수정
- ✅ `IWeapon` 인터페이스 + ScriptableObject 기반 `WeaponData`
- **Hwaseo 사례**: 새 노드 타입 추가 시 `NodeEntryService`에 페어(`MarkXxxNodeEntered` + `CommitPendingXxxIfLeaving`) 추가만으로 확장. 도메인 서비스/GameScene 수정 불필요
- **Hwaseo Strategy Pattern 사례 (2026-04-24)**: `NodeEntryService`의 `Mark*NodeEntered` 5개 메서드가 각자 `CommitPending*IfLeaving` static 5개를 일일이 호출하는 O(N²) 결합 구조였음. `INodeSessionCommitter` 인터페이스 + 도메인별 5개 구현체(`BattleRewardSessionCommitter`, `ShopSessionCommitter`, `CampSessionCommitter`, `EncounterSessionCommitter`, `TreasureSessionCommitter`)를 `IReadOnlyList<INodeSessionCommitter>` 로 주입, 통합 `MarkNodeEntered(phase)` 가 순회하도록 리팩토링 → 347줄 → 184줄 (47% 축소), 새 노드 추가 시 수정 위치 10곳 → 6곳. OCP의 Unity 실전 구현.

### L (Liskov Substitution)
서브타입은 기반 타입을 대체할 수 있어야. **계약 위반 금지**.

- ❌ `Rectangle` → `Square` 상속하면서 `SetWidth`가 `Height`까지 바꿈
- ✅ 불변 속성으로 설계하거나 별도 타입 분리
- Unity 특화: `MonoBehaviour` 상속 시 `Awake/OnEnable` 계약 위반 주의

### I (Interface Segregation)
클라이언트는 사용하지 않는 메서드에 의존하지 않아야. **큰 인터페이스보다 작은 전용 인터페이스**.

- ❌ `IEntity { Move, Attack, Talk, Trade, OpenInventory, Save }` — 적은 Trade/Save 불필요
- ✅ `IMovable`, `IAttackable`, `IDialogueTarget` 분리
- **Hwaseo 사례**: `MarkEncounterCleared(saveImmediately: bool)` — 호출자가 저장 여부를 선택. 자동/수동 경로 분리

### D (Dependency Inversion)
고수준 모듈은 저수준 모듈에 의존하지 않음. **둘 다 추상화에 의존**.

- ❌ `Enemy` 가 `FileSaveSystem` 직접 참조 → 저장 방식 변경 시 Enemy 수정
- ✅ `IEnemyPersistence` 인터페이스 주입
- **Hwaseo 사례**: `UpdatePendingBattleReward`의 의미를 "in-memory only"로 재정의해 호출부(BattleManager)가 저장 정책을 모르게 은닉 → DIP 달성

## 하드코딩 방지 규칙

### 1. 매직 넘버/문자열
- ❌ `if (level > 3)`, `if (tag == "Enemy")`
- ✅ `if (level > MaxBeginnerLevel)` const 또는 ScriptableObject 수치
- ✅ `if (tag == Tags.Enemy)` const 클래스 또는 `LayerMask`/`CompareTag`

### 2. 씬/프리팹 경로
- ❌ `Resources.Load("Prefabs/Enemies/Goblin")`
- ✅ `AssetReference` (Addressables) 또는 Inspector `[SerializeField] GameObject _prefab`

### 3. 밸런스 수치
- ❌ 코드에 `damage = 10 * level`
- ✅ `WeaponDataSO.DamageCurve.Evaluate(level)` — 디자이너가 에디터에서 조정 가능

### 4. 데이터 정의
- 게임 콘텐츠(적, 아이템, 스킬, 퀘스트) = 반드시 **ScriptableObject**
- 코드 상수는 규칙/제약 표현에만 사용 (`MaxInventorySlots`, `GravityScale`)

### 5. "나중에 설정으로 빼지 뭐" 금지
3개 이상의 `if` 분기나 enum 케이스가 등장하면 **즉시 SO/config로 추출**. 나중에 빼려면 이미 여러 호출처가 생겨 리팩토링 비용이 커짐.

## 게임에 자주 쓰는 디자인 패턴

### Observer (이벤트)
게임 내 여러 시스템이 특정 사건에 반응해야 할 때. C# `event` 또는 UnityEvent.
- 예: `OnPlayerDied`, `OnEnemyDefeated`, `OnItemPickedUp`

### State Machine
캐릭터/UI/게임 상태 관리. 전이 규칙 명시화.
- FSM: 단순 (Idle/Run/Jump)
- HFSM: 계층적 (Combat → SubStates)
- **Deferred Commit State Machine**: 트랜잭션 경계 분리. 상세: [node-lifecycle-patterns.md](node-lifecycle-patterns.md)

### Command
실행/취소 가능한 동작. Undo 시스템, AI 계획, 입력 리바인딩.
- 예: `MoveCommand`, `AttackCommand` 객체화

### Object Pool
자주 생성/파괴되는 오브젝트 (총알, 파티클).
- Unity 2021+: `UnityEngine.Pool.ObjectPool<T>`

### Service Locator / DI
글로벌 서비스(오디오, 저장, 이벤트 버스) 접근.
- Unity 특화: `Singleton<T>` MonoBehaviour, VContainer, Zenject

### Strategy
런타임에 알고리즘 교체. AI 행동, 공격 패턴, 난이도 조정.

### Flyweight
대량 오브젝트의 공통 데이터 공유. `ScriptableObject`가 Unity의 기본 Flyweight.

### Dirty Flag
비싼 계산(Navigation, 조명)의 재계산 회피.

### Claimed vs Applied (이번 세션 추가)
다단계 보상/트랜잭션 시스템에서 **선택(Claimed)**과 **적용(Applied)** 플래그 분리.
- 단일 플래그로는 "부분 수령 → 재입장 → 나머지 수령" 시나리오에서 재지급/누락 중 하나가 반드시 터짐. 상세: [node-lifecycle-patterns.md](node-lifecycle-patterns.md) 섹션 4

## 구현 전 자체 점검 체크리스트

에이전트(Sonny/Jarvis)가 코드 편집 **이전**에 실행:

1. **SRP**: 메서드/클래스가 **한 가지** 책임만 가지는가? 변경 이유가 하나인가?
2. **하드코딩 검출**: 매직 넘버/문자열/경로를 ScriptableObject/enum/const로 추출했는가?
3. **패턴 매칭**: 상태 관리/이벤트/보상/확장 지점이 위 카탈로그의 어떤 패턴에 해당하는가?
4. **OCP**: 새 타입 추가 시 기존 코드를 수정해야 하는가? → 인터페이스/Strategy로 분리
5. **테스트 가능성**: 순수 C# 로직이 MonoBehaviour 의존성에서 분리됐는가?

점검에서 미비점 발견 시 **먼저 사용자에게 구조 개선안을 제안**하고 승인받은 뒤 구현 진입.

## 안티패턴 경고

- **God Object**: 한 클래스가 모든 것을 관리 (예: `GameManager`에 100개 필드)
- **Magic Singleton**: 전역 상태 남발 — 테스트 불가능
- **MonoBehaviour Everywhere**: 순수 로직까지 MonoBehaviour에 넣어 유닛 테스트 불가
- **Inspector Spaghetti**: 수많은 SerializeField로 Inspector 관계망이 복잡해 추적 불가
- **"일단 작동하게"**: 하드코딩 후 리팩토링 약속 — 거의 이행 안 됨
- **도메인 컴포넌트 중복 구현 (Copy over Reuse)**: 신규 UI/기능이 기존과 유사한 책임을 가질 때 전용 컴포넌트를 새로 작성하는 유혹. **2026-04-24 Hwaseo 사례**: Treasure 보상 패널에 유물 아이콘 + 호버 툴팁 + 착용자 표시 요구 → `UITreasureRelicSlot` 신설 유혹. 실제 해법은 기존 `UIRelicIconSlot.Bind(RelicDefinition)` 재사용으로 아이콘/툴팁/착용자 전부 자동 처리. `UITreasure.cs`에서 `ApplyRelicIcon/ApplyRelicName/ApplyRelicFallback` 3개 메서드 + 2개 필드가 `_relicIconSlot` 1개 필드로 축소됨. **규칙**: "X 로직 참고" 지시 수신 시 **도메인 전문 컴포넌트가 이미 존재하는지 먼저 grep** (`UI*IconSlot`, `*Presenter`, `*Binder` 류).
- **Polymorphic Field Sentinel 오해**: 하나의 필드가 타입/의미를 이중으로 가질 때(예: 숫자 "0" = 빈 값 sentinel vs 문자열 = 실제 ID), 코드가 sentinel 해석을 빠뜨리면 silent misinterpretation 발생. **2026-04-17 Hwaseo 사례**: `EncounterAction.Value2=0`을 literal ID `"0"`으로 오해 → `ReserveRelicAsync("0")` null 반환 → 유물 미지급. **해결**: sentinel 상수 명명 + 전용 헬퍼.
  ```csharp
  private const string EmptyIdSentinel = "0";
  private static bool IsFixedIdSentinel(string id)
      => string.IsNullOrWhiteSpace(id) || id == EmptyIdSentinel;
  ```
  규칙: polymorphic field를 해석하는 코드는 **sentinel 판정을 전용 메서드로 분리** (SRP 확보, 향후 sentinel 추가 용이).
- **Speculative Observer Pattern (투기적 이벤트 도입)**: 1:1 호출 사슬을 "나중에 구독자 늘어날 수도 있으니" 미리 `event Action`/`UnityEvent`로 추상화하는 유혹. **2026-05-13 Hwaseo 사례**: UIMapView 시각 회귀 진단 중 단일 호출자→단일 수신자 흐름에 이벤트를 끼워넣으려 한 시도가 외부 비판 시뮬레이션에서 차단됨. 추상화 시 stack frame 증가 + 호출 시점 추적 비용 폭증 + Inspector listener 누락 시 silent fail. **규칙**: 헌법 §3 적용 — **3회 반복** 또는 **확장 요구가 코드에 명시**될 때만 도입. 1·2회 호출 사슬은 직접 호출이 디버깅·합류자 학습 비용 모두 우위. "확장 가능성 추측"은 안티패턴 신호어 (헌법 §5 "확장 가능성 추측에 기반한 패턴 도입" 금지 조항).
- **Root-Only GetComponent 사각지대**: 자식 GameObject 의 컴포넌트를 `GetComponent<T>()` 단일 호출로 찾으려 시도. Unity API 는 **호출된 GameObject 의 컴포넌트만** 반환 — 자식/부모 미탐색. **2026-05-13 Hwaseo 사례**: UIMapView 자식 노드 prefab 의 시각 컴포넌트 진단 시 root 에서 `GetComponent` 만 호출 → null → "컴포넌트 없음" 오판단 → 불필요한 prefab 수정 시도. **규칙**: ① 자식 탐색은 `GetComponentInChildren<T>(includeInactive: true)` 명시 ② 부모 탐색은 `GetComponentInParent<T>()` ③ **API 선택 자체를 진단 단계에 박제** — null 결과 = "컴포넌트 없음"이 아닌 "탐색 범위 mismatch" 가능성을 먼저 의심. Inspector hierarchy 트리와 코드 API 가 일치하는지 사전 검증 의무.

## 참고 문헌

- **Game Programming Patterns** (Robert Nystrom) — 게임 특화 패턴 카탈로그
- **Clean Architecture** (Robert C. Martin) — 의존성 규칙, 경계 설계
- **Refactoring** (Martin Fowler) — 코드 냄새 식별 및 안전 리팩토링
- **Unity 공식 Best Practices** — ScriptableObject, Addressables 사용법
