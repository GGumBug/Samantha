[← README로 돌아가기](../README.md)

# 다중 Layer 상태 동기화 패턴 (데이터 + Transient + 시각)

`multilayer-locale-snapshot.md` 와 동등한 패턴 — **상태가 데이터 / transient flag / Animator·Spine state 3 layer 에 분산**되어 있을 때, 한 layer 만 fix 하면 다른 layer 잔재로 시각/논리 불일치 발생. SSOT 진입점 메서드 우회 금지.

## 데이터 흐름 3-Layer 책임 분리

```
[Layer 1 SoT 데이터]      [Layer 2 Transient Flag]    [Layer 3 시각 State]
PlayerManager.hpDatas  →  HsUnit.IsDying           →  Spine AnimationState
(영구 저장 데이터)         UnitAnimController          (track 0 의 마지막 keyframe)
                          .IsDeadAnimPlaying          (Animator parameter)
                          (transient 라이프사이클)     (시각 잔재)
```

**원칙**: 각 layer 는 **자기 책임만** 보유. 상태 변환은 **단일 SSOT 진입점 메서드** (`HsUnit.Revive()`) 가 3 layer 모두 동기화 — caller 가 layer 1 만 직접 수정 시 layer 2/3 잔재.

## Layer별 책임 매트릭스

| Layer | 보유 데이터 | 금지 |
|-------|-----------|------|
| 1 SoT 데이터 | `PlayerManager.hpDatas[unitId].HP` (영구 저장) | layer 2/3 직접 알기 |
| 2 Transient Flag | `HsUnit.IsDying`, `UnitAnimController.IsDeadAnimPlaying` (라이프사이클) | 영구 저장 / 외부 caller 직접 set |
| 3 시각 State | Spine `AnimationState` track / Animator parameter | 게임 로직 (HP 등) 보유 |

## 본 사이클 사례 — 부활 시 시각 잔재 (2026-05-08 부활 hook 사고)

**증상**: 부활 시 HP 데이터는 정상 갱신 (`PlayerManager.hpDatas` HP=1) 됐지만 **쓰러진 포즈 잔존** — Spine `Death` 애니메이션 마지막 keyframe (track 0) 이 그대로 표시.

**원인**:
- 부활 hook 이 **Layer 1 만 갱신** (`PlayerManager.hpDatas[unitId].HP = 1`)
- Layer 2 미동기화: `HsUnit.IsDying = true` 잔존, `UnitAnimController.IsDeadAnimPlaying = true` 잔존
- Layer 3 미동기화: Spine `AnimationState` track 0 의 Death 마지막 keyframe 그대로 표시

**해결 — SSOT 진입점 호출**:

`HsUnit.Revive()` 가 **이미 존재**하며 3 layer 모두 동기화:
```csharp
public void Revive(int hp)
{
    PlayerManager.Instance.SetHP(unitId, hp);   // Layer 1
    IsDying = false;                            // Layer 2-a
    _animController.IsDeadAnimPlaying = false;  // Layer 2-b
    _animController.ReturnToIdle();             // Layer 3 (Spine track 0 Idle 재생)
    OnRevived?.Invoke(this);                    // 이벤트 발사
}
```

부활 hook 이 **`HsUnit.Revive(hp)` 호출** 로 변경 → 3 layer 동시 갱신.

## SSOT 진입점 우회 금지

```csharp
// ❌ Layer 1 만 직접 수정 — Layer 2/3 잔재
PlayerManager.Instance.SetHP(unitId, 1);   // 데이터만 갱신, 포즈 잔존

// ❌ Layer 1 + Layer 2 만 — Layer 3 (Spine state) 잔재
PlayerManager.Instance.SetHP(unitId, 1);
unit.IsDying = false;
// Spine track 0 의 Death 마지막 keyframe 그대로

// ✓ SSOT 진입점 호출 — 3 layer 동시 동기화
unit.Revive(1);
```

## 2-Layer 변형 — Live in-memory ↔ Raw Disk-Serialized SoT 분기

3-layer 데이터/transient/시각 패턴 외에 **2-layer 변형**도 동일 안티패턴. **같은 도메인 필드가 live in-memory class + persistence DTO 양쪽에 존재**하면 setter 가 한쪽만 갱신할 때 SoT 분기 발생.

**구조**:
```
[Layer 1 Live in-memory]              [Layer 2 Raw disk-serialized]
MapNode.SelectedEnemySpawnDataId  ↔   NodeData.selectedEnemySpawnDataId
(_mapLayout 노드 객체)                  (MapData 디스크 serialize 대상)
```

setter 가 layer 2 (raw + 디스크) 만 갱신하고 layer 1 (live) 을 누락하면, 직후 `SaveMap → PopulateNodeDataRows(live → raw)` 가 layout 전체를 박제할 때 raw 가 live 의 stale 값 (예: -1) 으로 덮어쓰여짐 → 디스크에 stale 값 영구 박제.

### 본 사이클 사례 — 재진입 InvalidOperationException (2026-05-11)

**증상**: 전투 노드 재진입 시 `InvalidOperationException("노드에 매치하는 데이터 없음")` — cached path 미발동.

**원인**:
- `RoguelikeMapManager.SetCurrentNodeSelectedEnemySpawnDataId` setter 가 **layer 2 (raw `NodeData` + 디스크 SaveMap) 만 갱신**, layer 1 (`MapNode.SelectedEnemySpawnDataId` live) 누락
- 직후 `SaveMap → PopulateNodeDataRows(live → raw)` 호출 시 raw 가 live 의 stale `-1` 로 덮어쓰여짐 → 디스크 `selectedEnemySpawnDataId = -1` 영구 박제
- 재접속 후 `EnemySpawnManager.SelectData` 의 cached path (`existingId != -1`) 미발동 → 신규 추첨 시도 → 매치 실패

**해결** (commit `b085eeda`): setter 가 layer 1 (live) + layer 2 (raw) **양쪽 모두 갱신** — single source of truth 분기 해소.

### 사고 차단 grep — 단일 갱신 setter 의심

```bash
# 같은 도메인 필드가 live class + persistence DTO 양쪽에 존재하는지 식별
grep -rE "(class|struct)\s+\w+(Node|Data|Layout|State).*\{" -A 50 Assets/Scripts \
  | grep -E "public\s+\w+\s+SelectedEnemySpawnDataId"

# setter 가 양쪽 모두 갱신하는지 확인
grep -rE "Set\w+SelectedEnemySpawnDataId|Set\w+SelectedId" Assets/Scripts -A 15
```

**룰**: 같은 도메인 필드가 live class + persistence DTO 양쪽에 존재하면 setter 가 양쪽 모두 갱신하는지 확인 의무. **단일 갱신 setter** 가 있으면 SoT 분기 의심.

## 사고 차단 게이트 (위임 시작 + 종료 grep)

```bash
# Pattern A — Layer 1 직접 set 후 SSOT 미경유
grep -rE "PlayerManager\.Instance\.(SetHP|hpDatas\[)" Assets/Scripts \
  | grep -v "HsUnit.cs"   # HsUnit.Revive 외부의 직접 set 의심

# Pattern B — Transient flag 외부 set
grep -rE "\.IsDying\s*=" Assets/Scripts | grep -v "HsUnit.cs"
grep -rE "\.IsDeadAnimPlaying\s*=" Assets/Scripts | grep -v "UnitAnimController.cs"

# Pattern C — Animator/Spine state 직접 조작 (SSOT 우회)
grep -rE "AnimationState\.SetAnimation\s*\(\s*0" Assets/Scripts | grep -v "UnitAnimController.cs"
```

세 패턴 모두 SSOT 진입점 외부에서 0건이어야 함.

## 시니어 회고

- **"한 layer 만 fix" 함정**: 부활 hook 작성자가 "데이터만 갱신하면 시각은 다음 frame 자동 reset" 이라고 잘못 추정 → Animator/Spine state 가 자동 reset 안 함 (라이프사이클 분리)
- **SSOT 진입점이 이미 존재** — 작성자가 grep 으로 확인 안 하고 직접 layer 1 만 set. `HsUnit.Revive()` 가 표준 진입점이므로 무조건 호출
- 헌법 §2 SSOT 단일 진입점 원칙 직접 적용 — 시점/관심사 (데이터 / transient / 시각) 다른 3 layer 가 한 메서드로 묶여 있음 → 우회 금지

## 관련 문서

- [.claude/rules/engineering-constitution.md](../.claude/rules/engineering-constitution.md) — 헌법 §2 SSOT 단일 진입점, §2-1 클래스 불변식 캡슐화
- [multilayer-locale-snapshot.md](multilayer-locale-snapshot.md) — L10n 4-layer (동등 패턴, 데이터 흐름 횡단 일관성)
- [node-lifecycle-patterns.md](node-lifecycle-patterns.md) — 상태 머신·노드 생명주기 패턴
- [sentinel-anti-pattern.md](sentinel-anti-pattern.md) — Layer-by-layer 일관성 강제 (동등 안티패턴)
