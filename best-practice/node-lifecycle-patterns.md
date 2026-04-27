[← CLAUDE.md로 돌아가기](../CLAUDE.md)

# 노드·세션 생명주기 패턴 — 상태 머신 교훈

Hwaseo 2026-04-17 노드 재입장 시스템 도입(22 커밋, `fd1643e8`~`efdcc479`) 경험에서 도출. 로그라이크·방 기반 게임의 노드(전투/상점/캠프/이벤트)에 중간 종료 후 재입장을 허용하는 **"Deferred Commit State Machine"** 패턴과, 구현 과정에서 반복 발생한 refactoring 함정들을 기록합니다.

## 1. Opt-in 보존 화이트리스트의 취약성

"새 인스턴스 교체" 패턴(refactoring-lessons 섹션 5 확장)에서 보존 대상을 **필드별로 수동 복사**하는 경우, 새 필드 추가 시 리마인더가 없어 **silent data loss 반복**.

**실제 반복 사례** (같은 파일에서 3번 연속 터짐):
1. `RunSeed` 누락 → 매 캡처마다 시드 0 리셋 (결정론 파괴)
2. `PendingShopSnapshot` 누락 → 상점 중간 저장 시 스냅샷 유실
3. `PendingCampSnapshot` + `PendingNodePosition` 누락 → 재클릭 가드 fall-through → 새 전투 시작 버그

**처방 (2단계)**:

1. **구조적**: 보존 로직을 **한 블록에 응집**. 개별 지역 변수로 흩뜨리지 말고 `old` 참조 하나로 통합:
```csharp
PlayerRunStateData old = data.runStateData;
data.runStateData = playerManager.CreateSnapshot(...);
// === non-transient 필드 보존 블록 ===
data.runStateData.RunSeed = old.RunSeed;
data.runStateData.PendingShopSnapshot = old.PendingShopSnapshot;
// ...
```

2. **제도적**: 블록 헤더 주석에 **과거 인시던트를 명시적으로 나열**:
```csharp
// 필드 추가 시 반드시 이 블록에 보존 라인 추가 필수.
// 과거 누락 사례:
// - RunSeed (2026-04-15): 결정론 시드 0 리셋
// - PendingShopSnapshot (2026-04-16): 상점 중간 저장 유실
// - PendingNodePosition (2026-04-17): 재클릭 가드 fall-through
```

**근본 해결(범위 외)**: `CopyFrom(other)` 중앙화 메서드로 opt-out 전환.

## 2. 메서드 오버로드는 부수 효과까지 등가여야 한다

기존 메서드의 **오버로드 추가** 시 핵심 할당만 복제하고 **부수 효과 누락**하면 silent behavioral mismatch.

**사례 — `NodeCleared`**:
- 무인자 `NodeCleared()`: `IsCleared=true` + **`DeactivateSelectableNodes` → `IsSelectable=false`** + `ActivateEdges` + `CommitSelectionChange` + `OnSaveMap`
- 신규 `NodeCleared(Vector2Int)`가 복제한 것: `IsCleared=true` + `OnSaveMap`
- **누락**: `targetNode.IsSelectable = false` 한 줄 → 클리어된 노드 버튼이 계속 클릭 가능

**처방**:
1. 오버로드 추가 시 **원본의 모든 side effect 목록화** 후 diff 작성
2. 호출 맥락에서 다른 경로가 일부 효과를 수행하는지 확인 (중복 제외)
3. "기존 호출을 새 오버로드로 대체해도 상태 동일" 테스트 시나리오 요구

## 2.1 Map SSOT — 클리어 진입점 단일화

§2의 `NodeCleared` 사례를 일반화한 규칙. 노드 비활성화·클리어는 **단일 진입점만** 허용해 부수효과 누락 자체를 구조적으로 차단한다.

- [ ] 노드 클리어 신호는 **`NodeCleared(Vector2Int)` 단일 진입점만** — 무파라미터 / 현재참조 버전이 필요하면 SSOT로 위임만
- [ ] 클리어 SSOT 부수효과 = `IsCleared=true` + 자신 `IsSelectable=false` + **같은 row 형제들 `IsSelectable=false`** + 다음 노드 활성화 + 저장 트리거 — **5종 모두 복제 검증**
- [ ] 부수효과 순서: 자신·형제 잠금 → 다음 노드 활성화 → **저장 트리거는 항상 마지막** (잠금 상태가 디스크 직렬화에 포함되도록)
- [ ] 신규 클리어 트리거(자동 패배·Skip·디버그 명령 등) 추가 시 SSOT 호출만 허용 — 직접 `IsCleared = true` 또는 `IsSelectable = true/false` 세팅 금지
- [ ] 위반 grep: `IsCleared\s*=\s*true` 또는 `IsSelectable\s*=\s*(true|false)` → SSOT 메서드 외부 위치는 모두 위반 후보, 통합 PR 직전 0건 확인 (맵 초기 생성 시점 예외는 주석으로 명시)

## 3. 타이밍 의존성 제거 — "현재" 암묵 참조 대신 명시 ID/좌표

"현재 선택된 X" 류 API(`_currentNode`, `_activeSession`)는 **포인터 갱신 타이밍에 코드 흐름이 결합**되어 버그 온상.

**사례 — `ClearMap()` 타이밍**:
- 원 설계: `FinalizeRewardFlow` 내부 호출 → `_currentNode` = 방금 클리어한 전투 노드 → 정상
- 변경: `NodeEntryService.CommitPendingBattleRewardIfLeaving`로 이동 → `MarkBattleNodeEntered` 선두 → 이미 `MoveNextNode`가 `_currentNode`를 **새 노드**로 업데이트한 뒤 → **새 노드가 지워짐**

**처방**:
1. 커밋 훅에 전달할 대상은 **명시 ID/좌표**로 (`PendingNodePosition` 스냅샷 + `ClearNodeAt(pos)` API)
2. "현재" 참조 API와 "대상 명시" API를 **쌍으로** 제공 + 의미론 동등성 보장 (섹션 2)
3. 새 커밋 훅 추가 시 포인터 타이밍 타임라인을 그려봄

## 4. "Deferred Commit State Machine" 패턴

### 패턴 구조

```
[노드 진입] → MarkNodeEntered (Pending* 플래그)
   ↓
[세션 실행] (구매/전투/휴식/선택)
   ↓
[완료 상태] (IsEnded 또는 BattleRewardPending)
   ↓────┐
   │    │ Exit 버튼 또는 자동 맵 복귀
   │    │   (allowCurrentReentry=true → IsNodeEntryPending 유지)
   │    ▼
   │  [맵에서 재클릭] → 완료 상태 UI 재표시 (상태 유지)
   │    │
   └────┘
   ↓
[다른 노드 Mark*NodeEntered] ← 유일한 커밋 경계
   ├─ CommitPending*IfLeaving → ClearPending* + ClearNodeAt(pendingPos)
   └─ _saveCurrentData (지연 커밋 확정)
```

### 필수 인프라

1. **Navigation Service** (노드별): `ResumeMapAsync(bool allowCurrentReentry)` — reentry=true면 `ClearNodeEntryPending` 생략 + `ReopenCurrentNodeIfAvailable` 호출
2. **Pending Snapshot** (노드별 + 공통 `PendingNodePosition`)
3. **NodeResumePhase enum**: `ShopEntered`, `BattleEntered`, `BattleRewardPending`, `EncounterEntered`, `CampEntered`, `TreasureEntered`
4. **Commit Hook**: `CommitPending*IfLeaving(PlayerData)` — 각 `Mark*NodeEntered` 선두에서 호출
5. **재클릭 가드**: `phase && pending && pendingPos == nodeInfo` 4조건 AND로 기존 세션 복원 경로 분기

### Strategy Pattern 확장 — N² 결합 제거

Commit Hook을 **노드별 static 메서드**로 두면 `Mark*NodeEntered` N개 × `CommitPending*IfLeaving` N개 = **O(N²) 결합** 발생. 새 노드 추가 시 N개 Mark 메서드 모두를 수정해야 함 (OCP 위반).

**처방 — `INodeSessionCommitter` 인터페이스로 추출**:

```csharp
public interface INodeSessionCommitter
{
    NodeResumePhase Phase { get; }
    bool CommitIfLeaving(PlayerData data, NodeResumePhase enteringPhase);
}
```

도메인별 구현체 (`BattleRewardSessionCommitter`, `ShopSessionCommitter`, `CampSessionCommitter`, `EncounterSessionCommitter`, `TreasureSessionCommitter` 등)를 `IReadOnlyList<INodeSessionCommitter>`로 주입, 통합 `MarkNodeEntered(phase)` 가 순회하도록 리팩토링.

**효과** (2026-04-24 Hwaseo Treasure 노드 추가):
- `NodeEntryService`: 347줄 → 184줄 (47% 축소)
- 새 노드 추가 시 수정 위치: 10곳 → 6곳 (신규 Committer 클래스 + 등록만)
- `Mark*` 메서드 간 Commit 호출 중복 제거

**추가 시 체크리스트**:
- [ ] `NodeResumePhase` enum 값 추가
- [ ] `I*SessionCommitter` 구현체 신설 (기존 도메인 매니저의 `ExitXxxSession` 또는 `ClearPendingXxx`를 호출)
- [ ] `NodeEntryService` 등록 리스트에 추가
- [ ] "자기 자신이 enter 중이면 스킵" 가드 확인 (`if (enteringPhase == Phase) return false`)

### Claimed vs Applied 분리 (보상 시스템)

선택/지급 타이밍이 다른 보상은 **두 플래그로 분리** 필수:
- `IsXxxClaimed` = UI 선택 (가시성 필터 전용)
- `IsXxxApplied` = 인벤토리 추가 (중복 지급 가드 전용)

단일 플래그로는 "부분 수령 → 재입장 → 나머지 수령"에서 재지급/누락 중 하나가 반드시 터짐.

### 노드 타입 추가 체크리스트

- [ ] Navigation Service 신설 (Shop/Battle/Camp/Encounter 중 유사한 것 복제)
- [ ] Pending Snapshot 데이터 구조 (필요 시)
- [ ] NodeResumePhase enum 값 추가
- [ ] `CommitPending*IfLeaving` 훅 + 4곳 `Mark*NodeEntered` 호출
- [ ] 재클릭 가드 (`GameScene.Start*` 선두)
- [ ] Capture 화이트리스트에 새 Pending 필드 추가 (섹션 1)

**참조 구현**: Hwaseo `feature/shop` 브랜치 `fd1643e8`~`efdcc479` (22 커밋).

## 5. Deferred Commit vs Bookmark 분리

"mid-session 재접속 복원"과 "applied effects 롤백" 요구는 **서로 다른 concern** — 함께 설계 가능.

### 두 개념 구분

| 개념 | 대상 | 저장 타이밍 | 예시 |
|------|------|---------|------|
| **Applied Effects** | 플레이어 인벤토리/상태 변경 | **다음 노드 진입 시** (Deferred Commit) | 골드 차감, 유물 추가, HP 변화 |
| **Session Bookmark** | "어느 세션을 진행 중이었는가" 식별자 | **세션 시작 시 1회** | encounter_07 선택됨, Shop 슬롯 구성 |

### 양립 설계

- Bookmark는 **applied effects 변경 전**에 저장 → 저장해도 "롤백 불가" 문제 없음
- Applied effects는 pending 리스트로 누적 → 다음 노드 진입 시 commit hook이 일괄 적용
- 중간 종료 → 재접속 시: bookmark로 **같은 세션 복원**, pending effects는 **롤백**

### Hwaseo 사례 (2026-04-17)

`EncounterManager.StartRandomEncounter` 신규 Encounter 선택 직후:
```csharp
_encounterState = new EncounterState(def.Id, def.FirstStepId);  // 시작 상태
PersistEncounterState();                                          // in-memory
PlayerDataManager.Instance.SaveCurrentData();                     // ← bookmark 디스크 flush
```

이 시점엔 유물/골드/HP 변경 0 → bookmark만 영속화. 이후 choice 효과는 `_pendingRelicRewards` 등에 쌓이고 다음 노드 진입 시 `ApplyPendingRewardsAsync`로 적용.

## 6. 세션 격리 3가지 아키텍처 대안

Encounter/Shop/Camp가 각기 다른 전략으로 "세션 간 상태 누수"를 방지 — 같은 문제에 대한 3가지 해법.

| 전략 | 대표 | 메커니즘 | 장점 | 단점 |
|------|-----|--------|------|------|
| **Singleton + Instance state** | `EncounterManager` | Manager 필드(`_encounterState`) 보유 + 명시적 `Reset()` / `BeginFreshXxxSession()` 호출 | 메모리 할당 최소 | Reset 누락 시 silent 누수 |
| **Instance-per-session** | `ShopController` | 매 세션마다 `new ShopController(...)` 생성 | 자동 격리, 코드 단순 | GC 부담 (가벼움) |
| **Explicit reset-on-init** | `CampRoomController` | Controller 재사용하되 `Initialize()`가 `_context = new(...)` 로 전체 재할당 | 중간 전략 — 인스턴스 유지 + 상태 초기화 | Initialize 누락 시 누수 |

### 선택 기준

- **재사용 비용이 높음 (무거운 의존성)** → Explicit reset-on-init
- **의존성이 가볍고 생성 저렴** → Instance-per-session (가장 안전)
- **Singleton 이점이 필요하고 상태 많음** → Singleton + 명시 Reset (가장 주의 필요)

### 안티패턴: Singleton + 암묵 상태 리셋
Singleton 매니저가 인스턴스 필드를 보유하면서 Reset을 생성자 호출로 암묵 대체 → 새 필드 추가 시 리셋 포인트 놓침 → 누수. **반드시 명시적 `Reset()` 또는 `BeginFreshSession()` 메서드로 경계 선언**.

**참조 사례**: Hwaseo 2026-04-17 Encounter A→B 연속 진입 누수 — `_encounterState.IsEnded=true`가 B로 전파되어 "떠난다만 있는 final step" 렌더링. `BeginFreshEncounterSession()` 신설로 해결.
