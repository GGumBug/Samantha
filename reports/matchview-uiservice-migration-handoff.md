[← README로 돌아가기](../README.md)

# MatchView → IUIService 마이그레이션 핸드오프

2026-08-13. 다른 데스크톱에서 이어서 작업하기 위한 인수인계 문서. 대상 저장소는 **Double Down**(`feature/ui` 브랜치)이며, 이 문서가 가리키는 커밋 3개가 푸시되어 있어야 한다.

## 0. 목표 (사용자 확정 결정)

MainScene의 UI를 사용자가 저작한 `MatchView.prefab`으로 교체하고, **게임의 모든 UI를 UIManager가 관리**하게 한다. 결정 사항:

| 결정 | 내용 |
|------|------|
| UIManager 실체 | **새 클래스를 만들지 않는다.** GameCore의 `IUIService`/`UIService`가 UIManager다 (신설 시 관리자 2개 = SSOT 위반) |
| 로드 경로 | **Addressables** — 주소 컨벤션은 `typeof(T).Name` (IUIService 계약) |
| 배선 범위 | **단계적** — 1단계 경로(완료) → 2단계 패널 데이터 이식 → 3단계 고/스톱 모달 이식 후 MatchHudView 폐기 |

## 1. 완료된 커밋 (Double Down, feature/ui)

| 커밋 | 내용 |
|------|------|
| `223e569` | MatchView.prefab 좌 컬럼 재구성 + Panel_JokboTracker CSF 버그 수정 (LayoutGroup 없는 단독 CSF는 자식을 못 잰다 — VLG 추가 + Deco 라인 IgnoreLayout) |
| `fcee59f` | **Part A — 기반 구축.** `MatchView.cs`(IUIView 구현, 표시/숨김만) + `UIAddressableRegistrar.cs`(메뉴 `Double Down > Register UI Addressables`) + Addressables 최초 구성(주소 `MatchView` 등록 완료) + 프리팹에 컴포넌트 부착. **기존 동작 무변경** |
| `2d5210f` | **Part B — 스위치 넘기기.** MainScene에 `[Inject] IUIService` + 로드 스텝 4단계("UI 준비" 10, 판 준비 50→40, 합 100) + `OnUnloadingAsync`에서 `Close<MatchView>()` + prefab sortingOrder 0→200 |

Samantha 저장소(이 repo)에는 미커밋 `reports/balatro-animation-improvement-plan.md`가 별도로 남아 있다 — 이번 작업과 무관, 카드 29 juice 개선 계획.

## 2. ⚠️ 즉시 해야 할 일 — Part B는 Unity 미검증 상태로 커밋됐다

외부 Roslyn 컴파일(exit 0)만 통과했고 **Unity 쪽 검증이 남아 있다**. stale `.csproj` 탓에 `GameCore.UI.dll`을 수동 주입한 검사라 asmdef 해석은 별개 축이다.

체크리스트 (새 데스크톱에서 pull 후):

1. Unity 열고 컴파일 확인 — 에러 시 1순위 의심: `DoubleDown.Boot.Scenes.asmdef`의 `"GameCore.UI"` 참조 해석
2. Play 진입 후 콘솔에 `[MainScene] IUIService가 주입되지 않아…` **없어야** 함 (Reflex 주입 성공)
3. 로딩 커튼 걷힌 뒤 MatchView가 **이미 떠 있어야** 함 (커튼 뒤 생성 — "UI 준비" 스텝)
4. 옛 HUD 기능 무회귀: 고/스톱 모달·거부 피드백·키 힌트 동작 (Part B는 옛 HUD를 건드리지 않았다)
5. 재시작(스톱→정산→재시작) 시 MatchView가 사라지거나 중복 생성되지 않는지

## 3. 핵심 아키텍처 사실 (재조사 방지용 실측 결과)

### 두 UI의 실체

| | `MatchHudView` (옛, 동작 중) | `MatchView` (신규, 사용자 저작) |
|---|---|---|
| 스크립트 | MatchHudView + HudSelfPanel/HudOpponentPanel/HudRejectionFeedback | `MatchView.cs` (IUIView, 표시/숨김만) |
| 생성 경로 | `MatchRuntime.ResolveHudView` → `Object.Instantiate` (씬 할당 `MainScene._hudPrefab`) | `IUIService.OpenAsync<MatchView>` (주소 `MatchView`) |
| 역할 | 표시 + **연출 채널(IStepMotion, CompositeStepMotion의 두 번째 채널)** + **입력 배선(Bind(router, gate, cursor))** | 아직 표시뿐 — 패널 데이터 없음 |
| sortingOrder | 100 (코드 지정) | 200 (프리팹 정본 — 코드로 덮지 않는다) |

**MatchHudView를 지금 걷어내면 안 되는 이유**: 화면이 아니라 연출·입력의 삼중 역할이다. 고/스톱 배너·키 힌트가 함께 사라진다. 3단계에서 이식 후 폐기.

### 생명주기 승격 (가장 중요한 설계 축)

- `UIService`는 뷰를 **DontDestroyOnLoad `UIRoot`** 아래 만들고 `Close`해도 파괴하지 않는다 (get-or-create 레지스트리).
- 반면 `MatchRuntime.Dispose()`는 판 루트 통째 Destroy가 "재시작 잔재 0의 유일한 기구"다.
- **MatchView는 이제 그 기구 밖이다** — 판을 갈아엎어도 살아남는다. 버그가 아니라 의도: UI는 판 수명이 아니라 씬 수명.
- 따라서 **2단계에서 판 데이터가 붙는 순간, 재시작 경로(`StartNewMatchAsync`)에서 뷰 상태 리셋을 함께 배선해야 한다** (잔재 0 = 파괴가 아니라 상태 초기화). 이 부채는 `MainScene.PrepareUiAsync` 주석에도 박제돼 있다.

### 함정 3종 (이미 밟았거나 코드에 박제된 것)

1. **EventSystem 순서 제약**: "UI 준비"가 "판 준비"보다 먼저 돌면 `UIService.EnsureEventSystem`이 **DDOL** EventSystem을 만들어 씬 포인터 기구가 씬을 넘는다. 현 순서(판 준비 먼저)는 `MatchInputRig`가 만든 씬 자식 EventSystem을 서비스가 재사용. 스텝 재정렬 금지 — `PrepareUiAsync` 주석 참조.
2. **`ReleaseAll` 금지**: 전 뷰 파기라 그 전환이 띄운 로딩 커튼까지 죽인다. 씬 이탈은 `Close<T>()` 숨김만.
3. **stale .csproj**: asmdef 수정 후 Unity 재import 전까지 `.csproj`는 옛 참조다. 외부 컴파일 검사가 CS0234로 실패하면 코드가 아니라 이걸 의심하라.

## 4. 다음 단계 (미착수)

### 2단계 — 패널 데이터 이식

`MatchView`에 `Render(BoardSnapshot)`을 만들고 패널별로 채운다. 프리팹 패널 인벤토리(실측): `Panel_JokboTracker`(+ 내부 `Panel_List` = VLG+CSF 정상 동작), `Panel_GoScale`, `Panel_GoCountTracker`, `Panel_BonusCardList`, `Panel_Multiplier`, `Panel_Breakdown`, `Panel_MatchStatus`, `Panel_SelfSide`/`Panel_OpponentSide`, `Panel_Act`, `Panel_Round`, `Panel_PlayerChips`, `Panel_RunStatus`.

- 값은 전부 `BoardSnapshot` 경유 (UI 자체 계산 금지 — SSOT)
- 옛 HUD의 대응 구현을 참고: `HudSelfPanel`/`HudOpponentPanel`(칩·점수), `MatchHudView.Render`
- SerializeField는 **쓰는 것만** 추가 (Part A에서 미리 안 판 이유와 동일)
- **재시작 리셋 배선** — 위 생명주기 승격 부채 해소를 이 단계 합격 기준에 포함할 것

### 3단계 — 연출·입력 이식 + 옛 HUD 폐기

- `IStepMotion` 구현(또는 별도 채널 분리)으로 고/스톱 배너·이벤트 오버레이 이식
- `Bind(router, gate, cursor)` 상당의 입력 배선 (제출 경로는 `MatchInputRouter.Submit` 단일 초크포인트 유지)
- 완료 후 `MatchRuntime.ResolveHudView`·`_hudPrefab`·`MatchHudView` 계열 제거 — **레거시 진입점 제거까지가 SSOT 통합** (헌법 §2)

### 병행 가능 (Slice A 크리티컬 패스)

Notion 「Slice A 개발 보드」 기준 29.6(시작 플로우)·29.7(고/스톱 모달 정착)·29.8(종료 화면)이 대기 중. 29.7/29.8의 표현 작업은 3단계와 겹치므로 **MatchView 이식과 통합 설계**하는 편이 이중 작업을 막는다.

## 5. 관련 파일 맵

| 경로 | 역할 |
|------|------|
| `Assets/Scripts/Presentation/Hud/MatchView.cs` | 신규 IUIView 뷰 (Part A) |
| `Assets/Scripts/Editor/Hud/UIAddressableRegistrar.cs` | 주소 등록 메뉴 (Part A) |
| `Assets/Scripts/Boot/Scenes/MainScene.cs` | 로드 스텝·PrepareUiAsync·OnUnloadingAsync (Part B) |
| `Assets/Scripts/Boot/Scenes/MatchRuntime.cs` | 판 조립·ResolveHudView(옛 경로, 3단계 제거 대상) |
| `Assets/Scripts/Presentation/Hud/MatchHudView.cs` | 옛 HUD (연출+입력 겸, 3단계 폐기 대상) |
| `Assets/Scripts/Boot/ProjectInstaller.cs` | Reflex 합성 루트 (`IUIService → UIService` 등록) |
| `Packages/com.ggumbug.gamecore/Runtime/UI/` | IUIService/UIService/IUIView 계약 (수정 금지 — 공유 패키지) |
| `Assets/Prefabs/UI/MatchView.prefab` | 사용자 저작 비주얼 (Editor에서만 수정 권장) |
