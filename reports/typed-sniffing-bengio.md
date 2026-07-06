# 상점 "패" 전용 프리팹 구조 도입 플랜

## Context

현재 상점 시스템은 `UIShopSlot.prefab` 한 벌을 모든 판매 아이템(소비 아이템, 유물, 패, 특수)에 공용으로 사용한다. 슬롯은 "아이콘 + 이름 + 가격 + 구매 버튼" 수준이라, "패"(= `HsSkillData`)가 원래 가진 **레어도**, **어느 유닛의 스킬인지**, **카드다운 외형** 같은 가치가 UI에서 드러나지 않는다.

사용자는 상점에서 패를 띄울 때 "패 모양의 UI 프리팹" 안에 이미지·이름·설명 등이 들어가는 구조를 원한다. 즉 상점 공통 껍데기(가격/버튼/SoldOut dim)는 유지하되, 콘텐츠 영역만 카드 전용 비주얼로 교체한다.

**의도한 결과**: Card 타입 슬롯이 카드다운 외형(아이콘, 이름, 설명, 레어도 테두리, OwnerUnitId 배지)으로 표시되고, 다른 아이템 타입(Relic/CardRemoval/Special)의 표시와 상점 공통 UX는 전혀 영향받지 않는다.

## 설계 결론

- **프리팹 전략**: 컴포지션. `UIShopSlot.prefab`의 콘텐츠 영역에 `objContentHolder`(빈 컨테이너)를 두고, Card 타입일 때 그 자식으로 신규 `UIShopCardView.prefab`을 Instantiate/교체한다. 다른 타입은 기존 `imgItemIcon + txtName`을 그대로 사용한다.
- **신규 프리팹**: `Assets/Prefabs/UI/Shop/UIShopCardView.prefab` (카드 전용 비주얼).
  - 포함 요소: `imgCardArt`, `txtCardName`, `txtCardDesc`, `imgRarityFrame`(레어도 색), `imgOwnerUnitBadge` + `txtOwnerUnit`(초상/약칭).
- **재사용**: 슬롯 공통 요소(`txtPrice`, `btnBuy`, `objSoldOutDim`, `UIShopSlotSelectionRelay`, 툴팁)와 PoolManager 풀링은 그대로.
- **HoldingSkillButton.prefab은 참조하지 않음** — 독립 프리팹 신규 제작(사용자 확인됨).

## 수정 대상 파일 (모두 [/Users/minki/Unity_Projects/Hwaseo/Assets/](/Users/minki/Unity_Projects/Hwaseo/Assets/) 하위)

### 코드
1. [Scripts/Shop/Data/ShopSlotVisualData.cs](Assets/Scripts/Shop/Data/ShopSlotVisualData.cs)
   - 필드 추가: `HsSkillRarity Rarity`, `int OwnerUnitId` (Card 외 타입은 각각 `HsSkillRarity.Common` / `-1` 기본값).
   - 생성자 확장. `readonly struct` 유지.

2. [Scripts/Shop/Services/ShopSlotDisplayResolver.cs](Assets/Scripts/Shop/Services/ShopSlotDisplayResolver.cs)
   - 시그니처 확장: `Resolve(... out HsSkillRarity rarity, out int ownerUnitId)`.
   - `ResolveCard`: `HsGameDB.SkillDB.GetDataByID(cardId) as HsSkillData` 에서 `rarity` 추출, `slot.OwnerUnitId` 그대로 전파.
   - 다른 분기(Relic/CardRemoval/Special)는 기본값 출력.

3. [Scripts/Shop/ShopController.cs](Assets/Scripts/Shop/ShopController.cs) — `BuildVisualData()` 에서 확장 필드 전달. (라인 62~86 범위 1곳만 수정.)

4. [Scripts/Shop/UI/UIShopSlot.cs](Assets/Scripts/Shop/UI/UIShopSlot.cs)
   - 직렬화 필드 추가: `RectTransform rectContentHolder`, `GameObject objCardViewPrefab`, `UIShopCardView cardView`(Pool 재사용을 위해 슬롯에 사전 캐시하는 방식 또는 `Setup` 시 한 번 Instantiate).
   - `Setup(ShopSlotVisualData data, ...)` 내부에서 `data.ItemType == Card` 이면:
     - 기본 `imgItemIcon`/`txtName` 숨김 (또는 `objDefaultContent.SetActive(false)`).
     - `cardView.Bind(data.DisplayName, data.Description, data.Icon, data.Rarity, data.OwnerUnitId)` 호출.
   - 비카드 타입일 때는 `cardView` 숨기고 기존 경로 유지.
   - `ResetState()`에서 cardView hide 포함.

5. **신규** `Scripts/Shop/UI/UIShopCardView.cs`
   - `MonoBehaviour`. `Bind(name, desc, icon, rarity, ownerUnitId)` 하나만 노출.
   - 직렬화 필드: `imgCardArt`, `txtCardName`, `txtCardDesc`, `imgRarityFrame`, `imgOwnerUnitBadge`, `txtOwnerUnit`, `Color rarityCommon/Rare/Unique`.
   - OwnerUnit 표시: `HsGameDB` 또는 유닛 DB에서 `ownerUnitId` → `Icon / DisplayName` 조회 (기존 상점에서 유닛 DB 조회 패턴이 없으면 이 탐색은 구현 단계에서 Sonny가 빠르게 확인).

### 프리팹 / 씬
6. **신규** `Assets/Prefabs/UI/Shop/UIShopCardView.prefab` (Ava)
   - 계층: 루트 + imgRarityFrame(테두리 Image) + imgCardArt(아트) + txtCardName + txtCardDesc + OwnerBadge 하위(badge + name).
   - 루트에 `UIShopCardView` 컴포넌트 부착 & 필드 바인딩.

7. 기존 [Assets/Prefabs/UI/Shop/UIShopSlot.prefab](Assets/Prefabs/UI/Shop/UIShopSlot.prefab) 수정 (Ava)
   - `objDefaultContent`(현재의 imgItemIcon+txtName 묶음) 래퍼 GameObject 신설.
   - `rectContentHolder`(빈 RectTransform) 신설 → 런타임 Instantiate 부모.
   - `UIShopSlot` 컴포넌트에 추가된 직렬화 필드 할당 (`objCardViewPrefab`에 6번 프리팹 드래그, `rectContentHolder`/`objDefaultContent` 연결).

## 재사용 대상 (새로 만들지 말 것)

- `ShopSlotVisualData` (구조는 그대로, 필드만 추가) — 새 VO 만들지 않음.
- `ShopSlotDisplayResolver` — Card 전용 Resolver 분리 안 함. 한 메서드 내 분기 유지가 기존 패턴.
- `PoolManager` Pop/Push — 슬롯 루트는 그대로 풀링, 자식 `UIShopCardView`는 슬롯 prefab에 이미 포함되도록 만들어 동적 Instantiate/Destroy를 피한다(풀 재사용 시 비용 0).
- `UIToolTip` 툴팁 — 기존 `_tooltipTitle/_tooltipDescription` 경로 재사용.

## Unity 팀 위임 전략 (CLAUDE.md 규칙 준수)

`.claude/rules/unity-delegation.md`에 따라 복수 분야가 섞인 작업은 상위 세션에서 병렬 호출한다. 단 **UIShopSlot.cs는 Ava의 프리팹 수정과 Jarvis의 VO 확장 양쪽이 건드리므로 직렬화가 필요**(중앙 허브 파일 규칙).

- Step 1 (병렬 가능):
  - **Jarvis**: (1)(2)(3) 코드 변경 — VO 확장 + Resolver/Controller 전파만.
  - **Ava**: (6) `UIShopCardView.prefab` + (5) `UIShopCardView.cs` 신규 작성 — UIShopSlot.cs 건드리지 않음.
- Step 2 (순차):
  - **Ava**: (4) `UIShopSlot.cs` 수정 + (7) `UIShopSlot.prefab` 수정 — Step 1 결과 VO 필드 존재를 전제로 한 번에.

이 순서로 하면 `UIShopSlot.cs` 멀티 에디트가 한 에이전트에 모이고, 같은 파일을 병렬로 건드릴 위험이 없다.

## 검증 (Evaluation-Driven)

1. **컴파일**: Unity Editor에서 에러 없이 도메인 리로드 성공.
2. **상점 진입 E2E**:
   - Map 상 Shop 노드 진입 → 슬롯 리스트 확인.
   - Card 타입 슬롯: 카드 아트/이름/설명/레어도 테두리 색/오너 유닛 배지 노출.
   - Relic/CardRemoval/Special 슬롯: 기존 아이콘/이름/가격 그대로 (회귀 없음).
3. **상호작용 회귀**:
   - 골드 부족 시 가격 텍스트 빨강.
   - 구매 성공 시 `objSoldOutDim` 활성화, btnBuy 비활성화.
   - 호버/키보드 선택 시 툴팁(이름+설명) 정상.
   - Exit 후 재진입 시 스냅샷 복원 정상.
4. **위임 결과 검증**:
   - `git diff --stat`으로 (4) `UIShopSlot.cs`에 병렬 충돌 없음 확인.
   - Ava 보고에 "프리팹 수정 후 Inspector에서 필드 할당 확인" 항목 포함 요구 (unity-delegation.md 시각 버그 규칙).

## 아웃 오브 스코프

- 카드 레어도별 **파티클/이펙트**(이번 플랜은 정적 비주얼만). 후속 이터레이션.
- CardRemoval/Special 슬롯 전용 프리팹화 (요청 범위 밖).
- `PlayerShopSlotData`/스냅샷 스키마 변경 (필요 없음 — `OwnerUnitId`는 이미 존재).
