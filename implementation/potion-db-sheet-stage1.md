# Potion DB 시트 — Stage 1 설계

![Last Updated](https://img.shields.io/badge/Last_Updated-May_08%2C_2026-white?style=flat&labelColor=555)

## 컨텍스트

포션 시스템을 BGDatabase + Google Sheets 시트 SoT 로 마이그레이션. HsEffect 다형성 보존 (HybridFK 패턴).

**Stage 분리** (사용자 결정):
- Stage 1 (본 PR): 시트만 작성 (entity + row export)
- Stage 2 (다음 PR): SO 폐기 + POCO + Factory + 호출자 마이그 + 영속화
- 별도 청소: PotionView 이중 진입점 + UnitAnimController.ResetState

**메인 안 채택**:
- 시트 SoT (HsPotionData SO 폐기)
- BGDatabase + GoogleSheets (Relic 패턴 4번째 미러링 — Relic/Encounter/Shop 검증)
- HybridFK (HsEffectData SO 유지, codeName 으로 참조)
- string PK (`POT_HwaSang_001`)
- 베타 단계 — backward compat 미고려

**A-E 권장안 채택**:
- A: `BGFieldString` + codeName (Effect 참조)
- B: `DB_PotionCondition` Stage 1 미도입 (YAGNI)
- C: 메타 컬럼 (Rarity/Tags/Memo) Relic 미러링 추가
- D: DescKey PotionMaster 통합 (description string snapshot 박멸 — 헌법 §2-0-1)
- E: 신규 `LocalizedText_Potion` 시트 (잡탕 `system.*` 시트에서 분리)

## DB_PotionMaster (14 컬럼)

> 시트 헤더는 `f_` 접두사 없이 — BG generator 가 자동으로 `f_*` 추가.
> PotionId 는 발음(`HwaSang`) 대신 의미 영문화(`Burn`, `Block`) — 효과 codeName 일관.

| 컬럼 | Type | 의미 |
|------|------|------|
| name | EntityName | BG PK (`potion_001`) |
| PotionId | String | runtime ID (`POT_Burn_001` — 효과명 기반) |
| CodeName | String | 자산 codeName (`Potion_01`) |
| NameKey | String | L10n key |
| DescKey | String | L10n key — string snapshot 박멸 |
| PotionType | Enum\<HsPotionType\> | Battle / Always |
| TargetSelectionType | Enum | Self/Select/All/RandomMultiHit/RandomDistributedHit |
| TargetUnitType | Enum\<HsUserType\> | Hwaseo / Enemy / Both |
| TargetLifeState | Enum | Alive / Dead |
| TargetCount | Int | 대상 수 |
| potionsprite | UnitySprite | Addressables Sprite |
| RarityType | String | Common/Rare/... |
| Tags | String | CSV |
| Memo | String | 디자이너 메모 |

## DB_PotionEffectEntry (11 컬럼, FK = PotionId)

> 시트 헤더는 `f_` 접두사 없이 — BG generator 자동 추가.

| 컬럼 | Type | 의미 |
|------|------|------|
| name | EntityName | BG PK |
| EffectEntryId | String | runtime ID |
| PotionId | String | FK → DB_PotionMaster.PotionId |
| Order | Int | 적용 순서 |
| **EffectAssetCodeName** | **String** | **HsEffectData codeName (HybridFK)** — Burn/Block 등 |
| EffectTargetType | Enum | EffectSpec.effectTargetType |
| Value1 | Int | CustomizedValue.value |
| Value2 | Int | 예약 |
| HasConditionality | Bool | Stage 1 = false |
| ConditionGroupId | String | 미래 join 용 |
| Memo | String | 메모 |

`DB_PotionCondition` 은 Stage 1 미도입 (YAGNI). 실제 사용 시 `DB_RelicCondition` (`BGCodeGenerate.cs:1039-1228`) 미러링.

## Potion_01/02 Row Sample

### DB_PotionMaster

| name | PotionId | CodeName | NameKey | DescKey | PotionType | TargetSelection | TargetUnit | TargetLifeState | TargetCount | RarityType | Tags |
|------|----------|----------|---------|---------|------------|-----------------|------------|-----------------|-------------|------------|------|
| potion_001 | POT_Burn_001 | Potion_01 | potion.0001 | potion.0002 | Battle | Select | Enemy | Alive | 0 | Common | Burn,Battle |
| potion_002 | POT_Block_001 | Potion_02 | potion.0003 | potion.0004 | Battle | Select | Hwaseo | Alive | 0 | Common | Block,Battle |

Sprite GUID (BG drag-and-drop):
- Potion_01: `5063888dcba8f8a4fbbed22485f2aa82`
- Potion_02: `2e864ef1a6397d84fb20bb760e30ac6f`

### DB_PotionEffectEntry

| name | EffectEntryId | PotionId | Order | EffectAssetCodeName | Value1 | Memo |
|------|----------------|----------|-------|----------------------|--------|------|
| potion_001_e1 | POT_Burn_001_E1 | POT_Burn_001 | 0 | Burn | 5 | 화상 5 부여 |
| potion_002_e1 | POT_Block_001_E1 | POT_Block_001 | 0 | Block | 5 | 방어도 5 부여 |

원본 자산: `Assets/Resources/HsPotionData/HSPOTIONDATA_Potion_0[12].asset`.

**5 enum 검증 완료** (`HsSkillData.cs` / `HsPotionData.cs` / `HsEffectData.cs` grep):
- `HsPotionType` = Battle, Always
- `TargetSelectionType` = Self, Select, All, RandomMultiHit, RandomDistributedHit
- `HsUserType` = **Hwaseo(=0), Enemy(=1)**, Both ← 박제 문서 가정 확정
- `TargetLifeState` = Alive, Dead, Any
- `EffectTargetType` = **Selected(=0)**, Caster, AllHwaseo, AllEnemy, All ← 시트 EffectTargetType="Selected"

## L10n 키 컨벤션

`potion.{2N-1}=name, potion.{2N}=desc` (Relic 미러링).

| 자산 | 신규 NameKey | 신규 DescKey | 옛 키 |
|------|-------------|-------------|-------|
| Potion_01 | `potion.0001` | `potion.0002` | `system.0560`, `system.0561` |
| Potion_02 | `potion.0003` | `potion.0004` | `system.0562`, `system.0563` |

신규 `LocalizedText_Potion` 시트 생성. `PotionKeys.cs` const 갱신은 Stage 2.

## Relic 미러링 기준

- Entity 정의: `Assets/Scripts/BGDatabase/BGCodeGenerate.cs:657-1509`
- POCO row data: `Assets/Scripts/Relic/Data/RelicTableSet.cs`
- Factory: `Assets/Scripts/Relic/Data/Source/RelicTableSetFactory.cs:15-29`

## 다음 세션 진행 흐름

1. **Claude Code 재시작** (uv 0.11.11 설치 완료, `mcp-google-sheets` 활성화 시점)
2. 새 세션에서 `/clear` 후 첫 명령 (예시):
   - "feature/potion-db-sheet 브랜치, implementation/potion-db-sheet-stage1.md 참조하여 Google Sheets 에 entity + row 입력 진행"
3. `claude mcp list` — `google-sheets ✓` 확인
4. 첫 호출 시 OAuth 인증 (브라우저 redirect)
5. 시트 URL: `https://docs.google.com/spreadsheets/d/1wfS0LZ4mLI15zTq-0O-3lOizEbJi29uN6KKu_0p6Knc/edit`
6. Claude 가 시트 read → 현재 상태 → entity + row 입력 → BGDatabase sync

## Stage 2 Input 명세

### POCO row data (신규: `Assets/Scripts/Runtime/BattleRoom/Potion/Data/PotionTableSet.cs`)

```csharp
public sealed class PotionTableSet
{
    public List<PotionMasterRowData> Potions = new();
    public List<PotionEffectEntryRowData> Effects = new();
}
public sealed class PotionMasterRowData
{
    public string PotionId, CodeName, NameKey, DescKey, RarityType, Tags, Memo;
    public HsPotionType PotionType;
    public TargetSelectionType TargetSelectionType;
    public HsUserType TargetUnitType;
    public TargetLifeState TargetLifeState;
    public int TargetCount;
    public Sprite IconSprite;
}
public sealed class PotionEffectEntryRowData
{
    public string EffectEntryId, PotionId, EffectAssetCodeName, ConditionGroupId, Memo;
    public int Order, Value1, Value2;
    public EffectTargetType EffectTargetType;
    public bool HasConditionality;
}
```

### Factory + Resolver

- `PotionTableSetFactory.CreateAsync(token, 128)` — `RelicTableSetFactory` 미러
- `HsEffectDataResolver.Resolve(codeName)` — `Resources.LoadAll<HsEffectData>` dictionary
- UniTask 헌법 §3 (frame budget) + §5 (OperationCanceledException) + §9 (token 전파)

### 호출자 마이그 (1건)

- `Assets/Scripts/Runtime/PlayerManager.cs:50` — `HsGameDB.PotionDB.GetDataByID(id)` → `_potionRepository.GetByPotionId(potionId)`

### 영속화 추가

- `PlayerData.ownedPotionIds: List<string>`
- `PlayerRunStateData.potionSlotCount: int`

### 폐기 대상 (Stage 2 종료 게이트)

- `HSPOTIONDATA_Potion_01.asset` / `HSPOTIONDATA_Potion_02.asset` 삭제
- `HsPotionDataDatabase.asset` 삭제
- `HsPotionData.cs` 삭제
- `PotionKeys.cs` const 갱신 (`system.*` → `potion.*`)

## 헌법 자가 검증

- §2 SSOT: 시트 = 1차 SoT. Stage 2 종료 시 SO 폐기로 통합
- §2-0-1: description string snapshot → DescKey + lazy resolve (Stage 2)
- §1 SRP: 시트 = 데이터, HsEffectData SO = 다형 동작 (HybridFK 격리)
- §3 패턴: Relic + Encounter + Shop = 3회 검증 → 4번째 도입 정당
- §5 YAGNI: `DB_PotionCondition` 미도입

## 관련 파일

- `Assets/Scripts/BGDatabase/BGCodeGenerate.cs` — Relic entity 미러 기준
- `Assets/Scripts/Relic/Data/RelicTableSet.cs` — POCO 미러
- `Assets/Scripts/Relic/Data/Source/RelicTableSetFactory.cs` — Factory 미러
- `Assets/Scripts/Runtime/BattleRoom/Data/HsPotionData.cs` — 폐기 대상
- `Assets/Resources/HsPotionData/HSPOTIONDATA_Potion_0[12].asset` — 마이그 출처
- `Assets/Scripts/Localization/L10n/PotionKeys.cs` — Stage 2 const 갱신 대상
