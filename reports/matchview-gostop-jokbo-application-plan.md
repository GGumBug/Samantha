[← README로 돌아가기](../README.md)

# MatchView·GoStopView·Item_Jokbo 적용 계획

2026-08-13. [matchview-uiservice-migration-handoff.md](matchview-uiservice-migration-handoff.md)의 후속 — 핸드오프가 정의한 2·3단계를 사용자 저작 프리팹 3종의 실측 결과로 구체화한 실행 계획이다. 대상 저장소는 **Double Down**(`C:\Unity_Projects\Double-Down`, `feature/ui`).

## 0. 목표

세 프리팹을 `IUIService` 단일 경로에 태우고, 옛 `MatchHudView`의 삼중 역할(표시·연출 채널·입력 배선)을 전부 이식한 뒤 **레거시 진입점까지 제거**한다(헌법 §2 — 제거까지가 SSOT 통합).

| 프리팹 | 지금 | 목표 |
|---|---|---|
| `MatchView.prefab` | IUIService로 뜨는 빈 껍데기 (Part B) | 판 데이터 렌더 (패널 6종 + 족보 트래커) |
| `GoStopView.prefab` | 저작 완료, 계약 없음 (스크립트 0·주소 미등록) | 고/스톱 모달 — `HudGoStopPrompt` 대체 (카드 29.7) |
| `Item_Jokbo.prefab` | 저작 완료 (`Text_Count`×4 + `Image_Arrow`×3 풀) | 족보 진행도 항목 — 8라인 트래커의 셀 |

## 1. 현재 상태 (실측 — 재조사 방지)

| 항목 | 상태 | 증거 |
|---|---|---|
| Part A/B (MatchView 경로) | 완료 | 커밋 `223e569`·`fcee59f`·`2d5210f` |
| Part B Play 4항목 | **검증 완료** | 사용자 실행 확인 |
| 족보 데이터 축 (Jarvis) | 완료 | 커밋 `d8e327d` — `CapturedTagTally` + `ScoreLineProgressCatalog` + `DomainProjection` 사상 + 생산자 17지점 |
| Slice 1 — MatchView 패널 데이터 | 완료 | 커밋 `dc89b9c` |
| Slice 3 — GoStopView 계약 | 완료 | 커밋 `7a32acc`(+`203774a` meta) |
| Slice T — 동치·불변식 테스트 | 완료 | 커밋 `84245ba` — **59/59 실행 통과**(신규 10 + 기존 49 회귀 없음) |
| 레이아웃 리빌드 수정 | 완료 | 커밋 `50dd48c` — §6 함정 6번 |
| Slice 2 — 족보 트래커 | 진행 중 | 설계 확정(아래) |
| MatchView 인스펙터 배선 | **미완** | 컴포넌트는 부착됨, 전 필드 `{fileID: 0}` |
| GoStopView 부착·주소 등록 | **미완** | Addressables 엔트리가 `MatchView` 하나뿐 |
| Item_Jokbo.prefab | 풀 구조 재편 완료 | `'Text_Count '` 뒤 공백 잔존 — 이름 조회 전면 금지라 동작 무영향 |

### 데이터 축 요약 (Slice 2·T의 재료)

- **분모(카탈로그 상수)**: `ScoreLineProgressCatalog.All` — 10행을 표시 8종(`ScoreLineKind`)으로 접음. 광만 3단계 `[(3,3점),(4,4점),(5,15점)]`. Collect(열·띠·피)는 `PerExtraScore` 노출.
- **분자(좌석 변동)**: 광·열·띠·피 = `SeatSnapshot.CapturedTally`(기존) / 고도리·홍단·청단·초단 = `SeatSnapshot.CapturedTagTally`(신규, 필수 인자). 둘 다 판정(`HandScoreCalculator`)과 같은 덱 렌즈 축 — 표시와 판정이 갈라질 수 없다.
- **완성 점수 정본**: `ScoreLineEntry.Points`(스텝 스트림) — 비광 감액·초과 가산이 반영된 판정 산출. 진행도는 예고, 점수는 판정.

## 2. Wave 0 — 선행 게이트 (완료)

컴파일·Play·커밋 정리 모두 통과했다. **Editor 없이 검증한 방법이 이후에도 유효하므로 기록해 둔다**:

- Unity 재import 뒤 `.csproj`가 갱신되면 `dotnet build`가 유효하다(stale 함정 해제). Application·Presentation·DevSandbox·Presentation.Tests·Integration.Tests·**Boot.Scenes** 6종 통과 — 마지막 하나가 핸드오프의 1순위 의심(asmdef `GameCore.UI` 해석)을 신선한 참조 그래프로 해소했다.
- 정적 생성자의 불변식은 컴파일이 지나간다. 빌드 산출 DLL에 콘솔 하네스를 물려 `ScoreLineProgressCatalog.All`을 실제로 건드려 검증했다.
- NUnit 테스트는 UnityEngine 의존이 없으면 Unity 밖에서 돈다. `[Test]` 메서드를 리플렉션으로 호출하는 러너로 59건을 실행했다(어서션은 실패 시 예외를 던지므로 예외 포착만으로 판정이 성립).

남은 사용자 작업은 **인스펙터 배선**뿐이다(§8).

## 3. 슬라이스 분해

```
Wave 0 (사용자 게이트)
  ├─ Slice 1 — MatchView 패널 데이터   (Ava)  ─┐
  │    └─ Slice 2 — 족보 트래커        (Ava)   ├─ Slice 4 — 모달 이식 (Ava)
  ├─ Slice 3 — GoStopView 계약        (Ava)  ─┘      └─ Slice 5 — 옛 HUD 폐기 (Jarvis+Ava)
  └─ Slice T — 동치·불변식 테스트      (Sonny, 언제든 병렬)
```

Slice 1·3·T는 상호 독립 — 병렬 위임 가능(파일 겹침 없음). Slice 2는 1의 `Render` 창구 위에, 4는 3의 계약 위에 선다.

### Slice 1 — MatchView 패널 데이터 이식 (Ava)

- **창구 두 개**: `Render(BoardSnapshot)`(권위 재동기화) + `UpdateScoreLines(SeatSide, IReadOnlyList<ScoreLineEntry>)`(스텝 완성 라인) — 옛 `MatchHudView`와 같은 모양이어야 Slice 5에서 `MainScene.ApplyScoreLinesFromSteps`의 대상만 갈아 끼운다.
- **패널 6종**: `Panel_SelfSide`/`Panel_OpponentSide`(칩·점수·`CapturedTally` 배지) · `Panel_PlayerChips` · `Panel_GoCountTracker`(`GoCount`) · `Panel_MatchStatus`(`Stage`·`RoundStage`·`ActorSeat`) · `Panel_Round`(`RoundsPlayed + 1`).
- **재시작 리셋 배선**: `StartNewMatchAsync` 경로에서 뷰 상태 초기화 — 생명주기 승격 부채(`PrepareUiAsync` 주석 박제)의 해소. **이 슬라이스의 합격 기준에 포함.**
- 범위 외: `Panel_Act`·`Panel_Multiplier`·`Panel_BonusCardList`·`Panel_RunStatus`(스냅샷에 축 없음 — 빈 채 유지), SerializeField는 쓰는 것만.
- 검증: 진입 렌더 ○ / 재시작 잔재 0 ○ / 언어·연출 무관(표시 전용) / 옛 HUD와 값 동일 프레임 갱신.

### Slice 2 — 족보 트래커 (Ava)

**8라인 고정이 아니라 획득 상황에 대응해 줄이 생긴다** (사용자 확정). 계획 초안의 "8라인 배치"는 폐기 — §5 미결이던 "0/3짜리 여러 줄이 늘 떠 있으면 화면이 죽는다"를 이 규칙이 해결한다.

- **표시 규칙**: 분자 > 0인 종류만, `ScoreLineKind` 오름차순 고정. 순서를 고정해야 줄이 새로 생겨도 기존 줄이 자리를 바꾸지 않는다.
- ⚠️ **소멸 축 필수**: 약탈(`LootSettler`)로 획득패를 뺏기면 분자가 **감소**한다. 증분 추가 방식(한 번 켜면 유지)은 유령 줄을 남긴다 — 매 렌더마다 표시 목록을 통째로 재계산한다.
- **좌석**: 플레이어만(`BoardSnapshot.Player`). 트래커가 좌 컬럼에 하나뿐이고, 상대 진행도는 정보 과다.
- **칸 개수**: `Text_Count` = `1 + Stages.Count`, `Image_Arrow` = `Stages.Count`. 광이 최대(4칸·화살표 3개), 나머지는 2칸·화살표 1개. 남는 칸은 끈다 — 프리팹 저작 풀을 런타임 Instantiate로 늘리지 않는다.
- **흰/그레이**: 분자가 아직 넘지 못한 **첫 단계**가 흰색(전 단계 도달 시 마지막이 흰색), 나머지 그레이. `분자 vs RequiredCount` 파생이라 새 데이터가 필요 없다.
- **점수 두 출처**: 진행 중은 흰색 단계의 `BaseScore`(예고), **완성된 종류는 `ScoreLineEntry.Points`로 덮는다**(판정 산출 — 초과 가산·비광 감액 반영). 이 재료가 Slice 1이 보관만 하던 `_playerScoreLines`이며, 그 부채가 여기서 소비된다.
- ⚠️ **레이아웃 캐시 상호작용**: `50dd48c`의 `_layoutRects`는 첫 `Open()`에 만들어지고 갱신되지 않는다. 줄 풀을 `Open()` 뒤에 만들면 새 줄이 초기 정착에서 빠진다 — 풀 선생성 또는 캐시 무효화가 필요.
- 이름 기반 `transform.Find` **금지**(§6 함정 4). `Item_Jokbo` 내부 참조는 프리팹 자산에 한 번 배선하는 SerializeField 배열로 받아 모든 인스턴스가 물려받게 한다.

### Slice 3 — GoStopView 계약 (Ava — Part A 미러)

- `GoStopView.cs`(IUIView — `MatchView.cs`가 템플릿: OnCreated 숨김 기준선·CQS·CloseAsync 취소 의미론 동일) + 프리팹 부착 + Addressables 주소 `GoStopView` 등록(`Double Down > Register UI Addressables` 메뉴 확장).
- **기존 동작 무변경** — 옛 `HudGoStopPrompt`는 그대로 돈다. 위험 최소 슬라이스.

### Slice 4 — 고/스톱 모달 이식 (Ava, 카드 29.7 통합)

- `HudGoStopPrompt`의 계약 승계: 표시 여부는 `IInputGate` **파생**(잠금 기구 신설 금지) · 제출은 `MatchInputRouter.Submit` 단일 초크포인트 · 숫자키와 같은 문.
- **판 수명 재배선**: 뷰는 씬 수명(DDOL), router·gate·cursor는 판 수명 — 판 교체마다 재주입하고 폐기 시 해제. MatchView 재시작 리셋과 같은 계약.
- 점수·판돈 표시(`_standing`·`_stake` 상당)는 프리팹에 텍스트 슬롯이 없음 — 저작 추가 필요 여부를 위임 전 사용자와 확정.
- 완료 후 `HudGoStopPrompt` 폐기(§5 미결 2 결정 포함).

### Slice 5 — 옛 HUD 폐기 (Jarvis 아키텍처 + Ava 연출)

- 연출 채널(`IStepMotion`, `CompositeStepMotion` 두 번째 채널)·이벤트 오버레이 이식 → `Bind(router, gate, cursor)` 상당 입력 배선 이식 → `MatchRuntime.ResolveHudView`·`MainScene._hudPrefab`·`MatchHudView` 계열 제거.
- **암묵 프록시 제거 주의**: 제거 대상이 값이 아니라 보장(연출 순서·입력 게이팅)을 나르는지 읽기 지점 전수 grep — [implicit-proxy-state-removal](../best-practice/implicit-proxy-state-removal.md).
- 카드 29.8(종료 화면)과 표현 작업이 겹침 — 통합 설계로 이중 작업 방지(핸드오프 §4).

### Slice T — 테스트 (Sonny — 구현자 분리 원칙)

- EditMode: ① `CapturedTagTally`·`CapturedTally` vs `HandScoreCalculator` 환산 매칭 수 동치(덱 렌즈 포함 픽스처) ② `ScoreLineProgressCatalog` 불변식 스모크(정적 생성이 던지지 않음 + 8종·광 3단계 형태 동결).
- Unity API grep 선행으로 모드 판정 확인 — [unity-test-mode-selection](../best-practice/unity-test-mode-selection.md).

## 4. 박제할 설계 결정

0. **연출 시점은 변환기가 선언하고 재생기는 읽기만 한다** (2026-08-13, 같은 계급 버그 4회 후 확정).

   같은 시점 버그가 네 번 반복됐다 — 배치 끝에만 갱신 / 재생 중 승계값 / 택1로 쪼개진 부분 갱신 / 배치를 턴으로 착각. 원인은 전부 같다: **재생기가 저수준 스텝 스트림을 훑어 "지금이 그 순간인가"를 역산**했고, 요구가 늘 때마다 술어를 손으로 깎다 범위를 잘못 잡았다.

   이벤트 소싱에서 이름 붙은 안티패턴이다 — 하류가 내부 이벤트에서 의미를 역산하면 상류가 바뀔 때마다 깨진다. `PresentationStepConverter`는 변환 시점에 **배치 전체를 손에 들고 있어 미래를 안다**. 추론이 필요 없는 자리다.

   **정식 절차**: 새 시점 요구("~할 때 갱신돼야 해")가 오면 → ① 그 순간을 뜻하는 표식을 기존 스텝의 축으로 추가(새 스텝 종류 신설은 접점이 5~6파일로 늘어나므로 최후수단) ② **필수 생성자 인자**로 두어 생산자 명부를 컴파일러가 세게 한다 ③ 변환기 마무리 패스가 선언 ④ 소비자는 읽기만. 재생기에 `if (다음 스텝이 …)` 같은 전방·후방 탐색이 생기면 그 자체가 신호다.

   선례: `CardsCapturedStep.SettlesTurnLoot`(커밋 `67b1fc4`) — 역산 로직 -50줄, `StepPlayer`는 순수 읽기.

   라이브러리(ZeroMessenger·MessagePipe·R3)는 **이 원칙 다음 순위**다. 구독자가 늘어 배선이 번거로워지면 그때 도입한다 — 지금 문제는 전달 수단이 아니라 의미 선언의 부재였다.


1. **생명주기 승격 계약**: `UIService` 뷰는 씬 수명(DDOL·get-or-create), 판 수명 의존물(router·gate·cursor·판 데이터)은 **판 교체마다 재주입 + 리셋**. "잔재 0 = 파괴"(옛 HUD)에서 "잔재 0 = 상태 초기화"(신규 뷰)로 기구가 바뀐다. MatchView·GoStopView 공통.
2. **점수 채널 분리**: 진행도(분자·분모 파생)는 예고, 완성 점수(`ScoreLineEntry.Points`)는 판정 정본. UI가 초과 가산·비광 감액을 자체 계산하지 않는다.
3. **정렬 층은 프리팹 정본**: 옛 HUD 100(코드) < MatchView 200 < GoStopView 300. `UIRoot`가 Canvas 없는 빈 오브젝트라 각 뷰 Canvas는 루트 Canvas — `overrideSorting` 불필요. 코드로 sortingOrder를 덮지 않는다(Part B 결정 승계).

## 5. 결정 현황

**확정된 것**:

| 결정 | 내용 |
|---|---|
| 트래커 줄 생성 | 획득 상황 대응 — 분자 > 0인 종류만, `ScoreLineKind` 오름차순 고정 |
| 트래커 좌석 | 플레이어만 |
| `Group_Point` 점수 | 흰색(도달 중) 단계 추종, 완성분은 `ScoreLineEntry.Points`로 정정 |
| 라벨 언어 | **한글** — `NeoDunggeunmoPro-Regular SDF`가 한글 글리프 보유("고도리" 저작 확인). 옛 "영문 강제(두부 방지)" 제약 해제 |

**남은 미결** (Slice 4 전에 필요):

| # | 결정 | 기본안 |
|---|---|---|
| 1 | 모달 시각 상수 정본 — `HudModal`(코드) vs 프리팹 저작 | **프리팹 정본 전환**. 29.8 종료 화면(두 번째 모달)이 오기 전에 확정해야 갈라짐이 시작되지 않는다 |
| 2 | GoStopView 점수·판돈 텍스트 | 옛 모달의 `_standing`·`_stake` 자리가 프리팹에 없다. 저작 추가하거나, **답이 없으면 `Text_GoStopDesc` 한 줄로 합친다** |

## 6. 함정 (핸드오프 승계 + 신규)

1. **EventSystem**: 씬 저작 추가로 순서 함정이 이중 안전이 됐지만, **그 오브젝트를 지우면 함정이 되살아난다**. 스텝 재정렬 금지는 유지 (`PrepareUiAsync` 주석). 씬 저작 `m_ActionsAsset`은 런타임에 `MatchInputRig`의 정적 자산으로 덮인다 — Inspector의 참조가 실동작이 아니다.
2. **`ReleaseAll` 금지**: 전 뷰 파기 = 로딩 커튼까지 죽는다. 씬 이탈은 `Close<T>()`.
3. **stale `.csproj`**: 외부 컴파일 CS0234는 코드가 아니라 재import 미완을 의심.
4. **프리팹 이름 뒤 공백** (2건 재발): `'Panel_Breakdown  '`·`'Text_Count '` — Inspector에서 안 보인다. 이름 기반 Find 전면 금지, SerializeField 배선만.
5. **풀 저작물 존중**: `Text_Count`·`Image_Arrow`는 저작 풀 — 런타임 Instantiate로 늘리지 말고 SetActive로 접는다.
6. **`SetActive(false)`가 레이아웃 큐를 버린다** (신규 — 커밋 `50dd48c`): 생성 프레임에 꺼지면 그 프레임에 큐잉된 리빌드가 실행되지 못한 채 소비된다(`LayoutRebuilder`가 `StripDisabledBehavioursFromList`로 비활성 부품을 걸러내고 큐는 비워진다). `IUIService` 마이그레이션이 만든 비용이며 `OnCreated` 훅을 가진 모든 뷰에 해당한다.
7. **루트 1회 `ForceRebuildLayoutImmediate`는 no-op일 수 있다** (신규): 그 재귀는 받은 rect 자신이 레이아웃 부품을 들고 있을 때만 내려간다 — uGUI 원문 주석 "If there are no controllers on this rect we can skip this entire sub-tree". 루트가 Canvas 컨테이너(`Canvas`·`CanvasScaler`·`GraphicRaycaster`)면 한 줄도 실행되지 않는다. **부품 보유 rect를 깊은 것부터 직접 짚어야 한다.**
8. **신규 `.cs`는 `.csproj`에 없어 조용히 컴파일에서 빠진다** (신규): Unity 재import 전까지 `<Compile Include>` 명시 목록에 없으므로 `dotnet build`가 **그 파일을 컴파일하지 않은 채 0 오류로 통과**한다(무의미한 green). 검증 전 Compile 항목 존재를 grep으로 확인하거나 직접 넣어라 — `*.csproj`는 gitignore 대상이라 커밋에 안 들어간다.
9. **에이전트 보고 절단 ≠ 작업 미완** (신규, 4/4 재현): 종료 메시지가 "Now …" 같은 진행 서술로 끝나도 편집은 완료된 경우가 지배적이었다. 재위임 전 `git status` + 처방 grep으로 상태 ⓐ/ⓑ/ⓒ를 판별하라 — 이번 세션 4건 모두 ⓐ(편집 완료·보고만 절단)였다.

## 7. 파일 맵 (핸드오프 §5에 추가분)

| 경로 | 역할 |
|---|---|
| `Assets/Scripts/Application/ScoreLineProgressCatalog.cs` | 족보 표시 카탈로그 (신규) |
| `Assets/Scripts/Application/BoardSnapshot.cs` | `CapturedTagTally` + `SeatSnapshot` 필수 인자 승격 |
| `Assets/Scripts/Application/DomainProjection.cs` | 태그·조건 → `ScoreLineKind` 사상 |
| `Assets/Tests/Application/ScoreLineProgressAxisTests.cs` | 카탈로그 동결 + 판정 동치 (신규) |
| `Assets/Scripts/Presentation/Hud/MatchView.cs` | 판 화면 — 창구 둘·재시작 리셋·레이아웃 정착 |
| `Assets/Scripts/Presentation/Hud/GoStopView.cs` | 고/스톱 모달 IUIView 계약 (신규) |
| `Assets/Scripts/Editor/Hud/UIAddressableRegistrar.cs` | 주소 등록 — `MatchView`·`GoStopView` |
| `Assets/Prefabs/UI/GoStopView.prefab` | 고/스톱 모달 비주얼 (사용자 저작) |
| `Assets/Prefabs/UI/Item_Jokbo.prefab` | 족보 진행도 셀 (사용자 저작) |
| `Assets/Scripts/Presentation/Hud/HudGoStopPrompt.cs` | 옛 모달 (Slice 4 폐기 대상) |
| `Assets/Scripts/Presentation/Hud/MatchHudView.cs` | 옛 HUD (Slice 5 폐기 대상) |

## 8. 남은 사용자 작업 (Editor)

| 필드 / 작업 | 대상 |
|---|---|
| `_selfPanel._chips` | `Panel_PlayerChips>Panel_Chips>Text_Chips` |
| `_opponentPanel._chips` | `Panel_OpponentStatus>Panel_Chips>Text_ChipAmount` |
| `_selfPanel._score` / `_opponentPanel._score` | `Panel_GoScale>Panel_SelfSide\|Panel_OpponentSide>Panel_Score>Text_ScoreThreshold` |
| `_goCountText` | `Panel_GoCountTracker>Panel_GoCount>Text_GoCount` |
| `_roundText` | `Panel_MatchStatus>Panel_Round>Panel_RoundCount>Text_Round` |
| `_capturedTally` · `_matchStatusText` | **대상 칸이 프리팹에 없다** — 저작하거나 비워 둔다(비우면 그 줄만 안 그린다) |
| `GoStopView` 컴포넌트 | `GoStopView.prefab` **루트**에 부착(자식 `Panel_GoStop` 아님) |
| 주소 등록 | 메뉴 `Double Down > Register UI Addressables` → 엔트리 `MatchView`·`GoStopView` 2개 확인 |
