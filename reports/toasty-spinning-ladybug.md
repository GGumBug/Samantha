# 결정론 런 시드 시스템 리팩토링 (P0)

## Context

**문제**: 게임 도중 종료 후 재접속 시 전투 초기 핸드, 전투 적 구성, 카드 보상 후보, 상점 진열, 맵 인카운터 ID가 모두 달라진다. 로그라이크의 "한 run은 고정된 우연의 연쇄"라는 핵심 계약이 파괴되는 P0 버그.

**근본 원인 (Samantha 진단)**:
1. 게임플레이 분기에서 **`UnityEngine.Random` 전역 상태** 사용 (17개 파일). 프로세스 재시작 시 상태 소멸 → 재추첨.
2. **Run Seed 개념 부재** — `PlayerRunStateData`에 시드 필드 없음. 모든 랜덤이 호출 시각에 종속.
3. **결과 스냅샷 저장 타이밍 결함** — `ShopManager.cs:74`는 `CaptureRunStateFromPlayerManagerNoSave()` 후 `SaveCurrentData()` 호출 누락. 메모리엔 있으나 디스크엔 없음.
4. **초기 덱 셔플 결과 미저장** — `BattleDeckController.Setup()`가 매 진입마다 재셔플.
5. **맵 노드에 확정된 인카운터/적 ID 미저장** — `NodeData`에 선택 결과 기록 필드 없음.

**의도된 결과**: 같은 run 내에서 (세이브 파일만 살아 있다면) 어떤 순간에 종료/재접속해도 모든 랜덤 결과가 동일하게 재현되어야 한다.

**정책 결정** (사용자 승인):
- **B안 전체 리팩토링**: 핫픽스 건너뛰고 `IRunRandom` 인프라 + RunSeed + 스키마 확장을 한 번에.
- **배포 전 게임**: 구 세이브 호환 불필요 → 마이그레이션/폴백 로직 제거하고 구조를 깔끔히.
- **전투 중 세이브 없음** (현 코드 분석 결론): `NodeEntryService`는 진입 시점과 보상 시점에만 저장. 따라서 "전투 진입 시 1회 결정론 셔플·스폰 → 결과 저장 → 재진입 시 복원" 전략으로 충분.

## 결정론 설계 원칙

**2계층 구조**:
1. **Run Seed** (int, 1회 생성 & 영구 저장): `StartNewRun()` 시 생성 → `PlayerRunStateData.RunSeed`.
2. **이벤트 키 기반 서브시드**: `HashCombine(RunSeed, label, ...context)` 로 이벤트마다 독립적인 `System.Random` 생성.

**보조 규칙**:
- 결과 스냅샷 저장 우선, 서브시드는 재현용 백업.
- VFX/DamageText 등 시각 효과용 `UnityEngine.Random`은 **유지**. 게임플레이 분기에만 `IRunRandom` 적용.

## 수정 대상 파일 (담당별)

### Jarvis — 인프라 + DI 배선 + 저장 누락 수정

| # | 파일 | 변경점 |
|---|------|--------|
| J1 | `Assets/Scripts/Runtime/Random/IRunRandom.cs` **(신규)** | 인터페이스: `Next(int)`, `Next(int,int)`, `NextFloat01()`, `Fork(string label)` |
| J2 | `Assets/Scripts/Runtime/Random/DeterministicRunRandom.cs` **(신규)** | `System.Random` 래핑 + `Fork(label)`은 `HashCombine(seed,label)` 기반 결정론적 분기 |
| J3 | `Assets/Scripts/Runtime/Random/RunRngService.cs` **(신규)** | POCO + static 싱글턴. `Initialize(int runSeed)`, `ForSubsystem(label)`, `ForBattle(act,row,label)` |
| J4 | `Assets/Scripts/Data/PlayerRunStateData.cs:16` | `public int RunSeed;` 추가 |
| J5 | `Assets/Scripts/Managers/Data/Services/RunLifecycleService.cs:30-41` | `StartNewRun()`에서 시드 생성 & `RunRngService.Initialize` |
| J6 | `Assets/Scripts/Managers/Data/PlayerDataManager.cs:48-72` | `TryLoad` 성공 시 `RunRngService.Initialize(runStateData.RunSeed)` 호출 |
| J7 | `Assets/Scripts/RoguelikeMap/Generation/RoguelikeMapGenerator.cs:13,21-27,109,149` | 생성자 시그니처 `(settings, IRunRandom rng)`. `settings.useSeed/seed` 분기 제거 |
| J8 | `Assets/Scripts/RoguelikeMap/Controllers/RoguelikeMapManager.cs:103` | `new RoguelikeMapGenerator(settings, RunRngService.Instance.ForSubsystem("map"))` |
| J9 | `Assets/Scripts/RoguelikeMap/Utils/WeightedRandomSelector.cs:49` | `UnityEngine.Random.value` → 주입된 `IRunRandom.NextFloat01()`. 호출처 전수 수정 |
| J10 | `Assets/Scripts/EncounterSystem/EncounterFlow/Model/Services/EncounterRunSelector.cs:12-17,96` | `System.Random` → 주입 `IRunRandom`, seed=0 폴백 제거 |
| J11 | `Assets/Scripts/EncounterSystem/Bootstrap/EncounterManager.cs` | `EncounterRandomSelector` 생성 시 `RunRngService.Instance.ForSubsystem("encounter")` 주입 |
| J12 | `Assets/Scripts/Shop/ShopManager.cs:73-76` | `CaptureRunStateFromPlayerManagerNoSave()` 뒤에 `SaveCurrentData()` 추가 |
| J13 | `Assets/Scripts/Shop/Services/ShopPurchaseService.cs:51`, `ShopCardRemovalService.cs:70`, `ShopBankService.cs:45,65` | 각 `NoSave` 호출 뒤 `SaveCurrentData()` 추가 (save 누락 전수 수정) |

### Sonny — 게임플레이 분기 결정론화

| # | 파일 | 변경점 |
|---|------|--------|
| S1 | `Assets/Scripts/Runtime/BattleRoom/BattleSystem/BattleDeckController.cs:4,151-158,429,447-452` | `Shuffle(List, IRunRandom)`로 시그니처 변경. `InsertToPile` `Random.Range` 제거. 생성자 주입 |
| S2 | `Assets/Scripts/Runtime/BattleRoom/BattleSystem/BattleManager.cs:655,797-815` | `GoldReward` & `FillCardRewards` → `RunRngService.Instance.ForBattle(act,row,"reward")` |
| S3 | `Assets/Scripts/Runtime/BattleRoom/BattleSystem/Enemy/EnemySpawnManager.cs:5,83,121` | `Random.Range` → `ForBattle(act,floor,"enemy").Next(...)` |
| S4 | `Assets/Scripts/Runtime/BattleRoom/BattleSystem/Enemy/EnemySpawnManager.cs:12,56-93` | **쿨다운 지속화**: `_stateByAct`를 `PlayerRunStateData.EnemySpawnRuntimeState`로 저장/복원. `CaptureState/RestoreState` API 추가 |
| S5 | `Assets/Scripts/RoguelikeMap/Models/MapDto.cs:99-106` | `NodeData`에 `public int selectedEnemySpawnDataId = -1;` 추가 |
| S6 | `Assets/Scripts/Runtime/BattleRoom/BattleSystem/Enemy/EnemySpawnManager.cs` | 첫 진입 시 뽑은 `EnemySpawnData.ID`를 `MapData.nodes[row].row[idx].selectedEnemySpawnDataId`에 기록. 재진입 시 해당 ID로 바로 스폰 |
| S7 | `Assets/Scripts/Scenes/GameScene.cs:218` | S6 시그니처 변경에 맞춰 호출부 수정 |
| S8 | `Assets/Scripts/Shop/Services/ShopSlotGenerationService.cs` (L40, 74, 99, 115, 127) | 모든 `UnityEngine.Random.Range/value` → 생성자 주입 `IRunRandom`. `ShopManager.InitializeServices`에서 `ForSubsystem("shop")` 주입 |
| S9 | `Assets/Scripts/EncounterSystem/EncounterFlow/Model/Services/EncounterRandomSelector.cs:52` | `Random.Range` → 주입 `IRunRandom` |
| S10 | `Assets/Scripts/EncounterSystem/EncounterFlow/Model/Services/EncounterActionExecutor.cs:583,719` | `UnityEngine.Random.Range` → `ForSubsystem("encounter_action")` |
| S11 | `Assets/Scripts/Relic/UI/RelicRewardFlowService.cs:314` | `Random.Range(0, totalWeight)` → `ForSubsystem("relic_reward")` |
| S12 | `Assets/Scripts/Runtime/EventRoom/UIChoiceEvent.cs:41` | 사용 중이면 `IRunRandom` 교체, 미사용이면 제거 |
| S13 | `Assets/Scripts/Runtime/BattleRoom/Effect/DefinedEffects.cs` | 내부 랜덤 사용처 전수 grep. 게임플레이 분기면 교체, VFX만이면 유지 |

### 건드리지 않음
- VFX / DamageText / 사운드 재생의 `UnityEngine.Random` — 시각 효과 전용.
- `MapGenerationSettings.useSeed`/`seed` SerializeField — Inspector asset 회귀 방지 차원에서 deprecated 주석 처리, 필드는 유지.
- `GameScene.StartBossBattle` — 이미 act 기반 결정성 확보됨.

## 재사용 기존 유틸

- `PlayerDataManager.SaveCurrentData()` — 디스크 flush 엔트리포인트 ([Assets/Scripts/Managers/Data/PlayerDataManager.cs](../../Assets/Scripts/Managers/Data/PlayerDataManager.cs)).
- `PlayerManager.CaptureRunStateFromPlayerManagerNoSave()` — 스냅샷 캡처 로직 (그대로 재사용, 단 호출처에서 Save 추가).
- `NodeEntryService.MarkBattleNodeEntered/MarkBattleRewardPending` — 저장 트리거 (수정 불필요, 호출 타이밍만 확인).
- `PlayerBattleRewardSnapshotData`, `PlayerShopSlotData`, `PendingShopSnapshot` — 기존 스냅샷 데이터 구조 그대로 사용.
- `HashCombine`은 표준 구현 (C# `HashCode.Combine` 또는 FNV-1a) 사용.

## 검증 절차 (Unity Editor 수동 테스트)

### 시나리오 1 — 상점 재현 (스냅샷 경로)
1. 에디터 Play → 새 런 → 첫 상점 노드 진입 → 슬롯 구성 스크린샷.
2. 구매 없이 뒤로가기 → 맵 → 상점 재진입. **기대**: 동일 슬롯.
3. 카드 1개 구매 → 맵 → 상점 재진입. **기대**: 남은 슬롯 동일 + 구매된 것만 `IsPurchased=true`.
4. 에디터 Stop → Play → 같은 런 로드 → 상점 재진입. **기대**: 동일 슬롯.

### 시나리오 2 — 스냅샷 삭제 후 서브시드 재현
1. 새 런 → 상점 진입 → 슬롯 스크린샷.
2. `Saves/Player/playerData.es3`에서 `PendingShopSnapshot`만 null로 편집.
3. 상점 재진입 → `GenerateNewShopAsync`가 재호출되지만 동일 `RunSeed` + `Fork("shop")` → 동일 시드.
4. **기대**: 1번과 동일 슬롯. 실패 시 `Fork` 해시 비결정성.

### 시나리오 3 — 맵 결정론
1. 새 런 직전 `Debug.Log($"[RunSeed]={RunSeed}")`로 시드 기록.
2. 맵 진입 → 레이아웃 스크린샷.
3. `Saves/` 전체 삭제 → 에디터 재시작 → 새 런 → `[ContextMenu]` 디버그로 `RunSeed`를 1번 값으로 주입 (Jarvis가 추가).
4. 맵 진입. **기대**: 동일 레이아웃.

### 시나리오 4 — 전투 재진입
1. 새 런 → 맵의 첫 전투 노드 진입 → 적 구성, 초기 핸드 스크린샷.
2. 에디터 Stop (전투 중) → Play → 같은 런 로드.
3. 재진입. **기대**: 동일 적, 동일 초기 핸드 (셔플 결과 재현).

### 시나리오 5 — 회귀 sanity check
새 런 → 전투 1회 완료 → 보상 수령 → 맵 복귀 → 다음 노드 선택까지 끊김 없는지 확인.

## 리스크 / TODO

- **`DefinedEffects.cs` 범위**: 전수 grep 결과에 따라 S13 확장 가능.
- **`EncounterManager._encounterRandomSelector` 생성 라인**: J11 진행 시 정확한 라인 특정 필요.
- **`NodeData` 스키마 변경**: 구 세이브 깨짐 — 사용자 승인 완료.
- **`RunRngService` 싱글턴 수명주기**: POCO + static, `PlayerDataManager.TryLoad` & `RunLifecycleService.StartNewRun`에서 초기화. Play 종료 시 static 리셋은 Unity의 `[RuntimeInitializeOnLoadMethod]` 처리.
- **Jarvis J11 vs Sonny S9·S10 경계**: DI 배선은 Jarvis, 실제 Random 호출부 교체는 Sonny. 경계 파일(`EncounterManager`)은 Jarvis 단독.

## 실행 순서 (승인 후)

1. Jarvis J1~J6 선행 (인프라 + 데이터 스키마) — 다른 모든 작업의 선결 조건.
2. Jarvis J7~J13 + Sonny S1~S13 병렬 투입.
3. Unity 에디터 컴파일 성공 확인.
4. 위 검증 시나리오 1~5 수동 테스트.
5. 결과 리포트.
