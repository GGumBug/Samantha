[← README로 돌아가기](../README.md)

# MatchView UI 마이그레이션 핸드오프

2026-08-18 갱신. 다른 PC에서 이어가기 위한 인수인계. 대상 저장소는 **Double Down**(`feature/ui`), 이 문서가 가리키는 커밋이 푸시되어 있어야 한다.

> 2026-08-13 초판(Part A/B — `IUIService` 경로 신설)은 완료되어 §5 이력으로 접었다. 지금 살아 있는 작업은 §3 이후다.

## 1. 확정 결정 (재논의 금지)

| 결정 | 내용 |
|------|------|
| UIManager 실체 | GameCore의 `IUIService`/`UIService`가 UIManager다. **새 관리자 클래스 신설 금지**(SSOT 위반) |
| UI 로드 경로 | Addressables, 주소 = `typeof(T).Name` |
| 화면 스펙 SSOT | Notion 「인게임 화면 구성 (확정)」 — **유추 금지, 원문을 먼저 연다**(헌법 §0-1) |
| 좌 컬럼(나) | 족보 게이지 → 칩×배수 → 보너스 슬롯 → 내 판돈 바 |
| 우 패널(상대) | 문양·이름·등급 → 남은 판돈 바 → 라운드·최소 판돈 → 고 선언 → 족보 게이지(위협 순) |

## 2. ⚠️ 새 PC에서 첫 3분

1. **양쪽 저장소 pull** — Double Down `feature/ui`, Samantha `master`
2. **Unity 열고 컴파일 확인** — 에러 0건이어야 한다
3. **Inspector 배선 1건 (미완)**:
   ```
   Assets/Prefabs/UI/MatchView.prefab → 루트 MatchView → Match View 컴포넌트
     Opponent Panel > Score  ←  Panel_RunStatus>Panel_GoScale>Panel_OpponentSide>Panel_Score>Text_ScoreThreshold
   ```
   지금 실행하면 상대 점수 칸이 저작 문구 `"0 | 9"`로 고정돼 보인다 — 그럴듯해서 버그로 안 보이는 종류다. 실행 시 `ReportMissingWiringOnce`가 콘솔에 좌석까지 붙여 찍는다.
4. **재생 검증** — 두 좌석 점수 칸이 `"현재 | 필요"`로 갱신되는가. 이게 `ffb57e1`의 미검증분이다.
5. **고/스톱 모달 확인** — 조건 성립 시 창이 뜨는가. 주소는 `0fdf991`에서 등록했으니 안 뜨면 프리팹 배선(`_goButton`·`_stopButton`)을 의심한다.

## 3. 지금 하던 일 — MatchView 기능 연동

프리팹 TMP를 기획 확정본과 대조해 배선하는 작업. **다음 차례는 `Panel_Breakdown`(칩 × 배수)** — 사용자가 "복잡하니 마지막에" 이월한 항목이다.

### 배선 상태

| 프리팹 오브젝트 | 기획 항목 | 상태 |
|---|---|---|
| `Panel_JokboTracker` | 족보 게이지 | ✅ `_jokboTracker` |
| `Panel_PlayerChips>Text_Chips` | 좌 ④ 내 판돈 | ✅ `_selfPanel._chips` |
| `Panel_OpponentStatus>Panel_Chips>Text_ChipAmount` | 우 ② 상대 판돈(체력바) | ✅ `_opponentPanel._chips` |
| `Panel_GoCountTracker>Text_GoCount` | 우 ④ 고 선언 | ✅ `_goCountText` |
| `Panel_Round>Text_Round` | 우 ③ 라운드 | ✅ `_roundText` |
| `Panel_SelfSide>Text_ScoreThreshold` | 내 점수\|필요 | ✅ `_selfPanel._score` |
| `Panel_OpponentSide>Text_ScoreThreshold` | 상대 점수\|필요 | ⚠️ **Inspector 배선 미완** (§2-3) |
| `Panel_Breakdown>Text_ChipValue`·`Text_MultiplierValue` | 좌 ② 칩×배수 | ❌ **다음 작업** |
| `Panel_MatchStatus` | 매치 상태 한 줄 | ❌ 프리팹에 쓸 TMP 자식이 없음 |

### 코드 배선이 필요 없는 것 (사용자 확정)

- `Image_Ref` — 시안 참조 이미지. 디자인 완료 후 사용자가 직접 제거
- `Panel_BonusCardList` — 보너스 카드 개발 시점으로 이월(현재 자식 0개)
- `Text_Rank` — 우선 "피쉬" 등급 고정. 프리팹 문구가 정본
- `Text_Act` — 우선 "1막" 고정. 프리팹 문구가 정본
- `Text_OpponentName` — 별명 기획 대기(타짜 원작 "작두"류). placeholder 유지
- 정적 라벨 7종(`Text_SeatLabel`×2 · `Text_GoCountTitle` · `Text_Chip` · `Text_MultiplierTitle` · `Text_PlayerChipsTitle` · `Text_ActLabel` · `Text_RoundLabel`) — 프리팹 문구가 정본

## 4. 다음 작업의 선행 조사 결과

`Panel_Breakdown`(칩 × 배수)에 착수하기 전에 알아야 할 것:

- **배수는 스냅샷에 없다.** 도메인에는 `GoStopState.GoMultiplier(balance)`·`OpponentProfile.DeckChipMultiplierBp`가 있고, 정산식은 `Σ칩 × 점 × 배수`(카드 49 완료).
- **축을 더하면 생산 지점 전수 갱신이 강제된다.** `SeatSnapshot` 생산 지점은 **13곳** — `BoardSnapshotBuilder` 2(실값) / `PresentationBoardModel` 2(**재생 모델 — 보존 전달, 재계산 금지**) / `AnimationGym` 2 / 테스트 7. 새 축은 **필수 인자**로 넣어 컴파일러가 명부를 만들게 한다(`= default` 금지 — 재생 모델이 조용히 0을 흘린다).
- **선례가 바로 앞 커밋에 있다.** `2ebaf84`가 "다음 고까지 필요 점수" 축을 같은 절차로 올렸다 — 도메인 파생 함수(SSOT) → `MatchFlow` 통과 노출 → 스냅샷 필수 인자 → 13곳 갱신 → `GoStopTests` 합류. **그 커밋을 그대로 따라 하면 된다.**

## 5. 커밋 이력 (Double Down, feature/ui)

| 커밋 | 내용 |
|---|---|
| `223e569` | MatchView.prefab 좌 컬럼 재구성 + JokboTracker CSF 버그 수정 |
| `fcee59f` | Part A — `MatchView : IUIView` + Addressables 주소 등록 도구 |
| `2d5210f` | Part B — MainScene이 `IUIService` 경유로 MatchView를 세운다 |
| `3d2410d` | 슬롯 배지·라운드 요약을 MatchView로 이관 |
| `5d155f2` | 배너 사건 채널 → `EventBannerMotion`(얇은 `IStepMotion` 어댑터) |
| `b418d04` | 거부 피드백·고스톱 키 힌트 이관 |
| `2ca0540` | **옛 `MatchHudView` 계열 제거** — UI 생성이 `IUIService` 하나로 수렴(−8,572줄) |
| `2ebaf84` | "다음 고까지 필요 점수" 도메인 파생 + 스냅샷 축 |
| `ffb57e1` | 좌석 점수 칸 두 값 렌더 + `_capturedTally` dead 필드 제거 |
| `0fdf991` | `GoStopView` Addressables 주소 등록 — 옛 프롬프트 제거 후 끊겨 있던 모달 경로 복구 |

## 6. 도달한 구조

```
IUIService (= UIManager)
 ├─ MatchView    계기판 — Render · UpdateScoreLines · ResetForNewMatch
 │   ├─ EventBannerMotion    사건 채널 (IStepMotion) — 선언 배너
 │   ├─ HudRoundSummary      라운드 요약
 │   └─ HudRejectionFeedback 거부 흔들기
 └─ GoStopView   고/스톱 모달 + 키 힌트
```

## 7. 함정 (이미 밟은 것 — 반복 금지)

- **생명주기 승격**: `MatchView`는 `DontDestroyOnLoad`라 **판보다 오래 산다**. `MatchRuntime.Dispose`(판 파괴)가 이 뷰를 치우지 않으므로 재시작 잔재 0은 **파괴가 아니라 `ResetForNewMatch`**로 얻는다. 판 수명 객체(라우터·커서)를 구독할 때는 씬 수명 쪽에서 걸고 판을 캡처하지 말 것.
- **`ReleaseAll` 금지**: 전 뷰 파기라 그 전환이 띄운 로딩 커튼까지 죽인다. 씬 이탈은 `Close<T>()`.
- **EventSystem 순서**: `MainScene.unity`에 저작물로 배치해 해결됨. 로드 스텝을 재정렬하지 말 것(`PrepareUiAsync` 주석 참조).
- **stale `.csproj`**: asmdef 수정 후 Unity 재import 전까지 `.csproj`는 옛 참조다. 외부 컴파일 검사가 CS0234로 실패하면 코드가 아니라 이걸 의심하라.
- **컴파일 검증의 결정적 증거**: `Library/ScriptAssemblies/*.dll` mtime이 편집 소스보다 최신인지 대조. Editor.log의 `error CS`는 옛 컴파일 잔상일 수 있다.
- **`Text_ScoreThreshold` 저작 문구**가 `"0 | 9"`라 미배선이어도 그럴듯해 보인다 — 배선 검사는 콘솔 경고로 한다.

## 8. 유실 기록

`reports/balatro-animation-improvement-plan.md`(카드 29 juice 개선 계획, 2026-07-29)가 커밋되지 않은 채 사라졌다. git에 없어 복구 불가. 내용 요지: 발라트로의 매력은 이동이 아니라 **반응 채널**(juice 펄스·아이들 워블·포커스 반응·점수 롤링·화면 흔들림)에서 나오고, 현 구현은 이동 채널만 있다. 재작성이 필요하면 카드 29 재개 시점에 다시 분석할 것.
