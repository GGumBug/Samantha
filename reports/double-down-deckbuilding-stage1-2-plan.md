[← 목록](../README.md)

# Double Down 덱빌딩 1단계 실행 계획: 1-2 도장 찍기

2026-10-20. [덱빌딩 설계 방향](double-down-deckbuilding-design.md) §5 1단계의 셋째 조각 1-2를 실행 단위로 나눈 계획이다.
사용자가 2026-10-20에 1-1 패 더미를 건너뛰고 1-2부터 하라고 지시했다("완료까지 권장 진행"). [1-0 계획](double-down-deckbuilding-stage1-plan.md)의 도메인 위에 세운다.

## 0. 한 장 요약

- 1-0이 만든 도장 도메인(`StampCatalog`·`RunStamps`·태그 축)을 실제 런과 상점, 판 화면에 잇는다. 카드 8개다.
- 사용자 결정: 런 시작 직접 찍기 없음(결정 5, 2026-10-20). 도장은 전부 상점에서 골드로 산다. 상점 가격 재조정은 모든 작업 뒤다.
- 권장으로 정한 것(§1-1): 도장 값 100골드 자리채움, 방문당 제시 2종·구매 1회, 교육 장면은 지정 화면 안의 설명 문구로 줄인다.
- 1-1을 건너뛰어 48칸 격자가 없다. 지정 화면은 그 도장을 찍을 수 있는 패만 보여 준다(홍단 도장이면 띠 7장).

## 1. 권장으로 정한 것

| 항목 | 결정 | 근거 |
|---|---|---|
| 도장 값 | 시트 `stamp_price` 100골드(자리채움) | 1-0 판정에서 값 100이 상점 찍기 런당 1.25회로 밑천 올리기와 다투면서도 사라지지 않는 구간이다. 재조정은 사용자가 뒤로 미뤘다 |
| 제시 | 카탈로그 4종 중 2종을 도장 스트림으로 뽑아 보인다. 방문당 1회 산다(품절). 건너뛸 수 있다 | 설계 문서 §4-2 "도장 2개 중 1개를 골드를 내고 찍거나 건너뛴다" |
| 덮어쓰기 | 칸 3이 찼으면 지정 화면에서 덮을 칸을 고른다. 환불 없음 | 결정 8, 설계 §4-3 행 9 |
| 지정 화면 | 고른 도장을 찍을 수 있는 패만 격자로 보인다. 이미 찍힌 패는 현재 도장을 표시한다 | 1-1이 없어 48칸 격자가 없다. 후보만 보이면 결정에 필요한 정보는 다 있다 |
| 교육 장면 | 별도 장면 없음. 지정 화면의 설명 한 줄("홍단 도장: 띠 한 장을 홍단으로 친다")과 후보 수 문구 | 범위 축소. 설계 §4-3 행 14·15의 문구를 그대로 쓴다 |
| 판 위 표식 | 내 덱 렌즈에서 태그가 바뀐 카드에 작은 글자 표식(홍·청·초·광). 전용 스프라이트가 들어오면 그 자리에 | 아트가 없다. 글자 표식은 폰트가 이미 있다 |
| 뺏김 연출 | 상대가 내 도장 패를 먹어 그 줄의 후보가 닫힐 때만 "뺏김" 외침. 내가 먹으면 표식이 한 번 커졌다 돌아온다 | 설계 §4-3 행 20. 1-0 판정에서 상대가 내 도장 패를 먹은 판이 45~61%라 판마다 띄우면 소음이다 |
| 힌트 칸 | HUD 족보 후보 표를 좌석 덱 렌즈로 만든다 | 1-0 계획 C 메모의 미룸 |

### 1-1. 조사로 확정한 설계 요점 (2026-10-20)

- 상점은 선수전 사이에 뜬다(`MainScene.cs:1120-1157`, 결과창 확인 뒤 `CreateNext` 앞). 판 밖이라 지정 화면의 방향키가 판 입력 게이트로 새지 않는다.
- Presentation은 Domain을 못 본다. 도장 제시·후보·칸은 `ShopSession`이 Application 투영 타입으로 낸다(`CardUpgradeOffer.cs:29` 선례).
  목표 줄은 `ScoreLineKind`(홍단·청단·초단·광)로 옮긴다(`DomainProjection.TryToTagLineKind`).
- 새 뷰는 `UIAddressableRegistrar.cs:32-38, 63-70`에 경로 상수와 `RegisterView<T>` 한 줄이 있어야 뜬다. 프리팹은 기존 프리팹을 `CopyAsset`으로 복사해 굽는다(`AgentScripts/BakeBombPromptView.cs` 선례, `run_script`).
- UI 카드 얼굴은 `CardSpriteTable.TryGetFront(definitionId, out sprite)` → `Image.sprite`(`ShopChipOfferCard.cs:133` 선례, 168×252). 판의 `CardView`는 월드 전용이라 쓰지 않는다.
- 키보드는 EventSystem 선택 + Enter다. Esc 처리 선례가 0건이라 닫기는 버튼과 가림막 클릭으로 한다(`BombPromptView.cs:102-104`).
- 족보 후보 표 `ScoreLineMembers.Of(kind)`는 원형에서 굽는다. 좌석 렌즈판은 `Of(kind, deck)` 꼴로 Application이 만들어 `JokboTracker.cs:270-289`에 넘긴다.
- 시험: `Presentation.Tests`는 EditMode(`[UnityTest]` 0건), PlayMode는 `Integration.Tests`다. 뷰 생명주기 시험 선례는 `ShopViewLifecycleTests.cs:113-129`.
- 시트: `GameConfig` 34행 `stamp_price`=100, DB `_id` RxfTOYmJMkGZxFaOMQpRqA(2026-10-20, 시트와 DB 대조 완료).

### 1-2. 상점 도장 SKU의 모양 (S3~S5 공통 계약)

| 층 | 표면 |
|---|---|
| 공장(S3) | `RunStamps _stamps`가 각서·작업패·보너스와 같은 런 수명. `CreateNext`의 덱은 `new PlayerDeck(_stamps.ApplyTo(_cardUpgrades.Snapshot()), handUpgrades)`. 도장 제시 스트림 표지 `shop-stamp` |
| 세션(S4) | `IReadOnlyList<StampOffer> StampOffers`(제시 2종, 세션 생성 시 1회 추첨), `bool IsStampSoldOut`, `bool CanBuyStamp`, `IReadOnlyList<StampTarget> StampTargetsOf(string stampId)`, `IReadOnlyList<StampSlotView> StampSlots`, `void BuyStamp(string stampId, ushort definitionId, int overwriteSlot)` |
| 투영 타입 | `StampOffer(StableId, ScoreLineKind TargetLine)`, `StampTarget(DefinitionId, ScoreLineKind? CurrentLine, string HeldStampId)`, `StampSlotView(Index, DefinitionId, StampId)` |
| 화면(S5) | 상점 칸 "도장 찍기"에 제시 2종 버튼. 누르면 `StampPlacementView`: 설명 한 줄, 후보 격자(얼굴 + 현재 줄 글자), 칸 3(찼을 때만 덮을 칸 선택), 확인·취소. 확인에서만 `BuyStamp` |

## 2. 카드

순차다. 카드마다 구현자와 시험 작성자를 나눈다. 좌표는 2026-10-20 기준이다.

| 카드 | 담당(구현/시험) | 무엇을 | 좌표 | 통과 기준 |
|---|---|---|---|---|
| S0 재측정 | Sonny / 코디네이터 | 스윕에서 런 시작 찍기를 빼고 1-0 판정을 다시 잰다. 배치 사본을 `%TEMP%` 밖으로 옮긴다 | `Tests/Sweep/RunLadderSweepScratch.cs:1911-1919` | 기본 사다리 스윕 비트 동일. 판정 표를 1-0 계획 §2-1에 덮어쓴다 |
| S1 카탈로그 | Jarvis / Sonny | 청단 도장·초단 도장 행 | `Domain/Run/StampCatalog.cs:180-190` | 단 도장 셋 모두 대상 7곳. 파생 명부 시험 통과 |
| S2 밸런스 행 | Jarvis(+코디네이터 시트·DB) / Sonny | `stamp_price` 시트 행, `ShopBalance.StampPrice`, 로더 | `Domain/Balance/ShopBalance.cs:20-57`, `Infrastructure/GameData/BgBalanceLoader.cs:177-195`, 시트 `GameConfig` | 부팅 예외 0. 값이 다른 고정구로 슬롯 오배선 검출 |
| S3 런 배선 | Jarvis / Sonny | 공장이 `RunStamps`를 들고 덱을 `stamps.ApplyTo(cardUpgrades.Snapshot())`로 짠다. 도장 스트림 표지 | `Boot/MatchSessionFactory.cs:123-191, 330-339, 416-443, 602` | 도장 0에서 덱 조립 비트 동일. 도장이 다음 판 렌즈에 선다 |
| S4 상점 세션 | Jarvis / Sonny | 도장 SKU: 제시 2종, `CanBuyStamp`, 후보 조회, `BuyStamp(stamp, card, overwriteSlot)`, 방문당 1회 | `Application/ShopSession.cs:627-667`(밑천 SKU 선례) | 지출·보관소·품절이 한 호출에서 원자적. 못 찍는 패는 지출 전에 거부 |
| S5 상점 화면 | Ava / Sonny | 상점의 도장 칸과 지정 화면(도장 고르기 → 패 고르기 → 덮을 칸 → 확인). 프리팹 굽기, 키보드 탐색 | `Presentation/Hud/ShopView.cs:156-166, 966-994, 1389-1398`(밑천 칸 선례), `Editor/Hud/ShopViewPrefabBaker.cs` | PlayMode 생명주기 시험. 재생 프로브로 찍기·덮어쓰기·건너뛰기 캡처 |
| S6 판 표식·힌트 | Jarvis(응용)+Ava(뷰) / Sonny | `CardSnapshot`에 도장 축, `CardView` 표식, 족보 후보 표의 좌석 렌즈화 | `Application/BoardSnapshotBuilder.cs:215-232`, `Application/ScoreLineMembers.cs:40-100`, `Presentation/Hud/JokboTracker.cs:285` | 도장 0에서 스냅샷·힌트 비트 동일. 도장 패에 표식, 힌트 후보 4장 |
| S7 연출 | Ava / Sonny | 내 획득 시 표식 펄스, 상대 획득으로 후보가 닫힐 때 "뺏김" 외침 | `Application/PresentationStepConverter.cs`, `Presentation/Board/FloatingTextMotion.cs`, `Playback/StepPlayer.cs` | 닫히지 않는 뺏김은 외침 0. 시간 리터럴 0 |
| S8 문서 | 코디네이터 | Notion Ruleset 도장 절, GDD, 핸드오프, 메모리 | | 산문 게이트 초록 |

카드마다 1-0과 같은 절차다. 재컴파일, 픽스처, 배치 전량(EditMode·PlayMode), 뮤테이션 1건 이상, 커밋 1.
S5·S7은 재생 프로브(시드 고정, 부트 씬 재생)로 화면을 캡처해 합격 기준을 확인한다.

## 3. 되돌릴 지점

- S5까지 가서 지정 화면이 서지 않으면 S4까지 커밋해 두고 화면만 뒤로 뺀다. 도장 SKU는 세션 시험으로만 산다.
- 도장 0일 때 모든 카드가 비트 동일이라 기능을 끄는 스위치는 따로 두지 않는다. 시트 `stamp_price`를 끄면 상점이 도장을 내놓지 않는다(S2에서 `enabled` 0 → 부팅 예외가 아니라 SKU 숨김으로 할지는 S2에서 정한다).

## 4. 실행 상태

| 카드 | 상태 | 커밋 | 검증 |
|---|---|---|---|
| S0 재측정 | 진행 | | |
| S1 카탈로그 | 대기 | | |
| S2 밸런스 행 | 대기 | | |
| S3 런 배선 | 대기 | | |
| S4 상점 세션 | 대기 | | |
| S5 상점 화면 | 대기 | | |
| S6 판 표식·힌트 | 대기 | | |
| S7 연출 | 대기 | | |
| S8 문서 | 대기 | | |
