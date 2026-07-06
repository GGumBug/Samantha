[← README로 돌아가기](../README.md)

# Sentinel `0` vs `-1` 안티패턴 — ID-인덱스 충돌 카탈로그

`int default=0` 언어 기본값과 "ID=0은 미설정/없음" 라는 sentinel 의미가 **시스템에 분산 박힌 변환** (`== 0 ? -1 : v`) 으로 충돌하면, ID=0 이 합법인 자산이 자연 발생하는 환경에서 간헐 결정론 사고가 발생한다. 사용자 표현 "**계속 반복**"의 본질은 이 3중 충돌이다.

## 3중 충돌 구조

```
[Layer A 언어 기본값]   [Layer B Sentinel 변환]      [Layer C 자산 ID 할당]
int existingId = 0;  →  existingId == 0 ? -1 : v  →  IODatabase List 인덱스 0
"미설정"                 "0 = 없음 신호"               "0 = 정상 자산 ID"
```

세 의미가 한 변수 (`int existingId`) 에 겹쳐 있어 caller 의 의도(미설정/sentinel/실제 ID)를 시그널만 봐서는 분간 불가. 한 layer 만 fix 시 다른 layer 가 sentinel 의미를 보존해 버그 재발.

## 4중 충돌 (영속화 layer)

데이터 SoT 마이그 후 **영속화 (Restore*RunData)** + **caller hardcode (Test* 자동 호출)** 양립 시 무한 자원 race. Layer A/B/C 외에 Layer D = 영속화 layer 가 추가로 sentinel/hardcode 의미를 보존.

**본 사이클 사례 (2026-05-11 Stage 2 Potion fix)**:
- `GameScene.cs:140` 의 `TestAddPotion()` hardcode 자동 호출 (씬 진입 시)
- `TestBattle.cs:90` 의 `TestAddPotion()` hardcode 자동 호출 (테스트 진입 시)
- `RunLifecycleService.cs:141` 의 `RestorePotionRunData(data)` 영속화 흐름
- 결과: 사용자 슬롯 비우면 → 다음 전투 진입 시 hardcode 가 자동 보충 → 영속화 layer 가 보충된 상태 저장 → 무한 자원 race

**해결**: hardcode 호출 완전 폐기 (헌법 §5 YAGNI — "테스트용 자동 호출" 정당화 회피) + 영속화 단일 SSOT 흐름 유지. 4 layer 중 한 곳이라도 자동 보충 잔재가 있으면 영속화 race.

**룰**: 자산 ID/자원 마이그 종료 게이트에 다음 grep 추가:

```bash
# Test* 자동 호출 잔재 (caller hardcode + 영속화 양립 race)
grep -rnE "(TestAdd|TestGive)\w*\s*\(" Assets/Scripts | grep -v "// removed"
```

## 양산 메커니즘

`IODatabase` 류 Add/Reorder 시스템이 **List 인덱스 0 부터 자동 ID 할당** 하면 **ID=0 자산이 자연 발생**. caller 가 sentinel `0` 을 "없음"으로 해석하는 한 ID=0 자산은 영구 race 후보.

```csharp
// 안티패턴 — 시스템 차원 ID-인덱스 충돌
public void Add<T>(List<T> list, T item) where T : IdentifiedObject
{
    item.ID = list.Count;   // 0, 1, 2, ... — ID=0 자산 자동 발생
    list.Add(item);
}
```

## 본 사이클 사례 (2026-05-08 BattleRng 결정론 인시던트)

**증상**: 동일 시나리오·동일 시드 5-10회 재현 시 1회 RNG 결정론 깨짐. Run C → Run D 변환 시점 한정.

**원인 흐름**:
- `EnemySpawnData_Node1_00.asset` ID=0 자산 자연 발생 (IODatabase 인덱스 0)
- `MapDataMapper.RoundtripExisting()` 가 `existingId == 0 ? -1 : existingId` 변환 → 정상 ID=0 자산을 sentinel 로 오해석 → `MapSaveLoad` 가 미설정으로 가드 → re-roll
- `GameScene.selectedCharacters` 가 `List<int> { 0, 1, 2 }` literal 사용 → `GetDataByID(0)` 이 합법 자산 반환했지만 caller 가 "미설정 시 첫 캐릭터 fallback" 로직과 충돌 → Run C/D 분기에서 다른 자산 선택 → 시드 동일에도 다른 RNG 라벨 소비

**해결 옵션**:

### 옵션 B — Sentinel `-1` 통일 (Layer B 정정)

- `MapDataMapper.RoundtripExisting()`: `existingId == 0 ? -1 : v` 변환 제거 → ID 그대로 round-trip
- `MapSaveLoad`: 미설정 가드를 `existingId != -1` 로 정정 (0 ≠ 미설정)
- `EnemySpawnManager`: `existingId != -1` 로 동일 정정
- caller 영향: `int default=0` 인 곳은 명시 `-1` 초기화로 변경

### 옵션 D — 시스템 차원 invariant (Layer C 정정 — 권장)

ID-인덱스 결합 자체를 분리:
- `IODatabase.Add/ReorderDatas()`: **1-based ID 할당** (`item.ID = list.Count + 1`)
- `IODatabase.GetDataByID(int id)`: `List.Find(x => x.ID == id)` (인덱싱 X)
- `IdentifiedObject.OnValidate()`: `ID > 0` assert
- `OnEnable()`: ID=0 자산 발견 시 즉시 throw → 시스템 차원 invariant

자산 ID 마이그레이션:
- 기존 ID=0 자산을 max+1 시프트 (gap 보존, caller hardcode 영향 0건 보장)
- 시트 Code Name 정렬 case sensitivity 일관성 검증 ([asset-migration-sort-consistency.md](asset-migration-sort-consistency.md))

## 사고 차단 게이트 (위임 시작 + 종료 grep)

```bash
# Pattern A — sentinel 변환 잔재
grep -rE "==\s*0\s*\?\s*-1\s*:" Assets/Scripts
grep -rE "!=\s*0" Assets/Scripts | grep -iE "(existingId|enemyId|cardId|relicId)"

# Pattern B — int default=0 + sentinel 의미 혼재
grep -rE "int\s+\w*[Ii]d\s*=\s*0\s*;" Assets/Scripts | grep -v "// sentinel"

# Pattern C — caller hardcode literal (시그니처 grep 만으론 누락)
grep -rE "(AddPotion|AddCard|AddAlly|AddRelic)\s*\(\s*\d+\s*\)" Assets/Scripts
grep -rE "List<int>\s*\{[^}]*\b0\b[^}]*\}" Assets/Scripts
```

세 패턴 모두 0건 아니면 sentinel 안티패턴 잔재.

## Pattern D — 동거 심볼 cascade (class 단위 grep 한계)

ScriptableObject/POCO **폐기 마이그**에서 class 단위 grep 만 sweep 하면, 같은 `.cs` 파일에 동거하는 enum / nested class / static field 가 다른 파일에서 참조되는 경우 cascade 누락 → 컴파일 에러.

**본 사이클 사례 (2026-05-11 Stage 2 Potion 마이그)**:
- `HsPotionData.cs` 폐기 대상 식별 → class 본문만 grep
- 같은 파일에 동거하던 `HsPotionType` enum 누락
- 결과: `PotionTableSet.cs:18` (`List<HsPotionType>` 필드) + `BGCodeGenerate.cs:3456` (auto-gen 참조) 컴파일 에러 cascade
- 메인 1차 dangling 4 위치 → Samantha 6 위치 보강 → 실제 컴파일 시 8 위치 cascade

**권장 grep 패턴** (위임 시작 + 종료 의무):

```bash
# Pattern D-1 — 폐기 대상 class 파일의 동거 심볼 식별
grep -nE "class\s+\w+Data\s*\{" Assets/Scripts/<폐기파일.cs>
grep -nE "public\s+(enum|class|struct|static)\s+\w+" Assets/Scripts/<폐기파일.cs>

# Pattern D-2 — 식별된 동거 심볼 caller cascade
grep -rnE "(HsPotionType|PotionType)\b" Assets/Scripts
```

**룰**: ScriptableObject/POCO 폐기 위임 시 **class 명 + 동거 enum/nested class/static field 모두 grep 의무**. 한 심볼이라도 누락하면 cascade 잔재.

## 시니어 회고

- "한 곳만 fix" 함정: sentinel 의미가 시스템에 분산 박혀 있어 caller hardcode + IODatabase 자동 할당 + 변환 layer 셋 모두 일관 처리해야 진짜 sweep
- "합법 ID=0 자산 발생 가능" 가정 자체를 시스템 차원에서 차단 (옵션 D) 이 옵션 B (변환 정정) 보다 ROI 우수 — 새 자산 추가 시 동일 사고 재발 방지
- **Gate grep 통과 ≠ 사고 차단**: 시그니처 grep 은 caller literal `{ 0, 1, 2 }` 까지 cover 못 함 — 실행 결과 (Editor 재현) 가 진실 ([evaluation.md](../.claude/rules/evaluation.md))

## 관련 문서

- [.claude/rules/engineering-constitution.md](../.claude/rules/engineering-constitution.md) — 헌법 §2 SSOT 단일 진입점 원칙
- [multilayer-locale-snapshot.md](multilayer-locale-snapshot.md) — Layer-by-layer 일관성 강제 (동일 패턴)
- [asset-migration-sort-consistency.md](asset-migration-sort-consistency.md) — 자산 ID 마이그레이션 case sensitivity
- [determinism-hooks.md](determinism-hooks.md) — RNG 결정론 라벨 SSOT
