[← 목록](../README.md)

# 폭탄 룰 도입 계획 (Ruleset v0.2 + 구현 카드 13)

## Context

사용자 결정(2026-09-29): "폭탄은 표준 룰로 도입하자". Ruleset v0.1 §1은 폭탄을 제외했고 시스템 디자인 §2(08-05)는
"판 길이·검증 표면 통제"로 미채용을 유지했다. 이번 결정으로 그 사유를 철회한다. 룰셋은 "변경은 별도 변경 기록과
재승인을 거친다"고 못 박았으므로 §1 스펙을 이 계획의 승인으로 갈음하고, 구현 뒤 Notion 변경 기록에 옮긴다.

표준 원문은 룰셋의 근거 문서인 한게임 신맞고 기본규칙이다. "같은 무늬의 패 3장이 있고 바닥에 나머지 한 장이 있을
경우 / 흔들기와 마찬가지로 2배 / 상대방에게서 피 한 장 / 두 장을 미리 낸 셈이기 때문에 나중에 두 장을 뒤집을 수 있다".

사용자 화면 결정(계획 중 확인): 폭탄 입력은 **프롬프트 2버튼**(폭탄 가능한 카드를 클릭하면 [폭탄][치기]),
폭탄패는 **손패 끝 뒷면 카드 2장**(전용 스프라이트가 들어오면 그 자리에, null이면 스킨 뒷면).

## 1. 룰 스펙 (Ruleset v0.2 §4 폭탄)

| # | 항목 | 확정 | 근거 |
|---|---|---|---|
| B1 | 성립 | actor 손패에 같은 달 3장 + 바닥에 그 달 **정확히 1장** | 표준. 48장 불변식상 유일 배치 |
| B2 | 선택형 | 폭탄은 행동이다. 그 달 1장을 그냥 치는 것도 합법 | 표준(한게임 폭탄 버튼) |
| B3 | 획득 | 치기 절반에서 4장 즉시 획득, 뒤집기 절반은 평소대로 | 표준 |
| B4 | 약탈 | 상대 피 1장. 후보 규칙은 쪽·따닥과 동일. 마지막 턴 예외 없음(폭탄은 손 ≥ 3이라 마지막 턴에 구조상 불가) | 표준은 예외를 쪽에만 둔다 |
| B5 | 순서 | **폭탄 → 쪽 → 따닥 → 싹쓸이 → 뻑 해소**. 앞 이벤트의 약탈 카드는 뒤 후보에서 제외 | 폭탄은 치기 절반 사건 |
| B6 | 배수 | 폭탄 좌석이 **승자**일 때 ×2, n회면 ×2ⁿ(최대 3회 = ×8). 박·특수배수 곱에 합류 | 표준 "이겼을 경우 두 배" |
| B7 | 폭탄패 | 폭탄 직후 actor에 폭탄패 2장. 폭탄패를 치면 치기 절반을 건너뛰고 뒤집기만. 사용 시점 자유 | 표준 |
| B8 | 빈손 | "손패가 비면 스톱 확정"의 손패에 폭탄패 포함 | 뒤집기는 이득이 있다 |
| B9 | 폭탄패 턴 | 쪽·따닥 불성립. 싹쓸이·뻑 성립·해소는 평소대로 | 정의 그대로 |
| B10 | 총통·흔들기 | 미채용 유지 | 범위 밖 |
| B11 | AI | 폭탄 가능하면 항상 폭탄(실수 추첨도 생략). 폭탄패는 최고 치기 점수 ≤ 0일 때 | 안 하는 쪽이 늘 손해 |
| B12 | 대칭 | 상대도 같은 규칙 | 좌석 무관 SSOT |
| B13 | 리플레이 | 폭탄·폭탄패는 별도 이벤트. 어휘 판 3 → 4 | 기존 로그와 비호환 |

**불변식 산술.** 좌석당 턴 10, 매 턴 뒤집기 정확히 1장(치기·폭탄·폭탄패 공통) → 더미 20 = 20턴 유지.
좌석 불변식 **손패 + 폭탄패 = 남은 좌석 턴**: 치기 −1, 폭탄 −3+2 = −1, 폭탄패 −1. 토큰 2 = 3−1은 회계 상수다.
b회 폭탄 시 손 10−3b + 토큰 2b, b ≤ 3. `MaxInputsPerTurn = 4` 안(폭탄 턴 = 폭탄 1 + 뒤집기 택1 ≤ 1 + 고/스톱 ≤ 1).
밸런스 행 `bomb_multiplier` = 2.

## 2. 설계 결정 (탐색·검증 완료)

| # | 결정 |
|---|---|
| D1 | `TurnActionKind.PlayBomb = 5`(Card = 그 달 손패 중 InstanceId 최소 = 대표 카드, 엔진이 나머지 2장 파생), `PlayBombToken = 6`(Card 없음). 열거 순서 손패 치기 전부 → 폭탄(달 오름차순) → 폭탄패(`legal[0]`·커서 첫 항목 안정). **카드 없는 행동의 `Card`=0이 실재 id 0과 충돌**하므로 `PlayerAction.TargetsCard`에 PlayBomb 포함·PlayBombToken 제외하고 `SelectionCursor.TryMoveTo`·`ApplySlotBadges`·AI `GainedCards`는 이 필터를 먼저 본다 |
| D2 | `DomainEventType.BombPlayed = 21`(Actor·Month·HandCards 3·**HandCardDefinitions 3**(상대 뒷면 공개 echo)·FloorCard·**TokensAfter**), `BombTokenPlayed = 22`(Actor·TokensAfter), `SpecialSituationKind.Bomb = 5`(약탈, 동형 페이로드), `SettlementAppliedEvent.BombMultiplier`(**ulong 거듭제곱값**, bool 아님 — 2ⁿ 재생 검증), 지문 case 3, `VocabularyVersion = 4`. 룰셋 문자열은 그대로 |
| D3 | `RoundBoard`에 좌석별 `BombTokens(seat)`·`BombCount(seat)` 카운터(`_ppeokBoundMonths` 패턴, 좌석 인덱스 배열). 엔진 열거기·정산·화면 배수·스냅샷이 모두 판을 쥐고 있다 |
| D4 | 새 `Domain/Turn/BombRule.cs` 순수 정적 `CollectBombMonths(hand, floor)`. `ISpecialSituationJudge.Judge(RoundBoard, TurnHalfFacts)`로 시그니처를 한 번만 바꾼다(`TurnHalfFacts` = Actor·HandPlay?·BombPlay?·DrawFlip). `TryFormPpeok`·`ReleaseClearedPpeoks`는 치기 사실 null 가드. `IsGoChoiceDegenerate` = 손 0 && 토큰 0 |
| D5 | `SettlementBalance.BombMultiplier`(`bomb_multiplier`, Placeholder 2). `LootSettler.BombMultiplierFor(count, balance)`(checked pow, `DrawCarryMultiplierFor` 선례) 한 곳. `Settle`·`LootMultiplier`에 `int bombMultiplier` 필수 인자. `MatchFlow.SettleRound`·`LootMultiplierOf` 둘 다 이 함수를 부른다(화면 배수는 폭탄 직후 ×2 표시. 멍따·고박은 정산 시점 배수라 1인 것과 구별) |
| D6 | (a) `MatchInputController.HandlePointerClick`은 `TryMoveTo` 직후 즉시 제출하므로, 클릭 카드의 달에 PlayBomb이 합법이면 제출 대신 `BombPromptView`(GoStopView 패턴: 라우터·게이트·커서 Bind, 전면 차단 없음, 버튼 [폭탄][치기])를 연다. (b) `SeatSnapshot.BombTokens` 필수 인자 축 → `CardViewRegistry.PlaceBombToken(zone, 합성 id ≥ 1000, index, count)` 전용 문, 스프라이트 `CardSpriteTable._bombTokenSprite ?? skin.Back`, `HandReorderDrag`는 토큰 제외, 토큰 클릭은 `PlayBombToken` 전용 경로. (c) `BombPlayedStep`(3장 동시 바닥 이동 WhenAll + "BOMB!" 외침 1회), `BombTokenPlayedStep`(폴드: 토큰 = TokensAfter), 정산 `SpecialMomentStep(Bomb)`은 외침 없이 약탈 "+1 PI"만 |
| D7 | AI `ScoreOf`에 PlayBomb 분기(Kind 분기를 `GainedCards`보다 먼저), 폭탄 합법이면 실수 추첨 생략, 폭탄패는 두 패스(최고 치기 점수 선계산) |
| D8 | 카드 13개 순차. C1b까지는 AI가 폭탄을 고르지 않게 두어(점수 0, 동점은 앞 항목) 골든 동결값을 지키고, C3a에서 한 번에 재동결한다 |

## 3. 구현 카드 (순서대로, 카드마다 커밋 1)

담당은 구현/시험 분리. 카드마다 재컴파일 → 라이브 픽스처 → 배치 전량(`ddtest.sh` + `playmode_batch.sh`) →
뮤테이션 ≥ 1 → 커밋. 파일 좌표는 탐색 보고(`Assets/Scripts` 기준)와 같다.

| 카드 | 담당(구현/시험) | 편집 | 깨지는 시험 → 처방 | 신규 시험·뮤테이션 | 게이트 |
|---|---|---|---|---|---|
| **C0a** 도메인 어휘 | Jarvis / Sonny | `Domain/Events/DomainEventContracts.cs`(21·22·Kind 5·v4), `TurnFlowEvents.cs`(BombPlayedEvent·BombTokenPlayedEvent), `RoundFlowEvents.cs`(BombMultiplier), `Replay/DomainEventFingerprint.cs`, `Turn/TurnActions.cs`(5·6·팩토리) | `DomainEventContractsTests` 12-35·88-96·105·217, `DomainEventLogTests` 218·223(19→21), `BetMinPolicyTests` 89(4→6), 시험 내 지문 사본 7곳(TurnEngine 1184·RoundFlow 294·SpecialSituationRule 788·PpeokRule 429·HeuristicAiPolicy 762·OpponentAiWiring 623·MatchGoldenCase 631) | `BombPlayedEvent_RequiresThreeHandCardsAndDefinitions`, `Fingerprint_BombEvents_Distinct` | grep `VocabularyVersion = 4`·`BombPlayed = 21`·`Bomb = 5` |
| **C0b** 응용·화면 어휘 | Jarvis / Sonny | `Application/PresentationVocabulary.cs`(PlayerActionKind 5·6), `DomainProjection.cs`(233·290), `PlayerAction.cs`(TargetsCard), `PresentationStep.cs`(BombPlayedStep·BombTokenPlayedStep, Kind 18·19, SpecialMomentKind 5), `PresentationStepConverter.cs`(case 2·ToSpecialMoment), `Playback/PresentationBoardModel.cs`(폴드 case: 3장 바닥 앞면 이동·토큰 대입) | `PresentationVocabularyMirrorTests` 72-76, `PresentationStepConverterTests` 380, `PresentationBoardModelTests` 700(17→19)·704·1380 | `Converter_BombPlayed_RevealsThreeHandCards`, `Fold_BombTokenPlayed_AssignsTokensAfter` | grep `case PresentationStepKind.BombPlayed` 폴드·감독 |
| **C1a** 규칙·판정 | Sonny / Jarvis | ★`Domain/Turn/BombRule.cs`, `Board/RoundBoard.cs`(카운터), `Turn/TurnBoundaries.cs`(TurnHalfFacts), `Turn/SpecialSituationRule.cs`(폭탄 약탈 맨 앞, actor는 facts에서) | `TurnEngineTests` 스텁 955-962·730·752, `SpecialSituationRuleTests`·`PpeokRuleTests` 직접 호출 | `BombRuleTests`: 3+1 성립, 3+0·2+1·바닥 3(뻑) 불성립, 달 오름차순; `SpecialSituationRule_Bomb_StealsFirst_ThenSsakssuriExcludesIt` | grep `CollectBombMonths(` |
| **C1b** 엔진 | Sonny / Jarvis | `Turn/TurnEngine.cs`(LegalActions·KindMatchesState·Execute·ResolveBomb·ResolveBombToken·null 가드 2·IsGoChoiceDegenerate), `Opponents/HeuristicAiPolicy.cs` 2줄(GainedCards Kind 선행 가드, 폭탄 점수 0) | `TurnEngineTests` 188·403·423·521(손패 == 10−t/2 → 손패+토큰), `RoundFlowTests` 35, `TurnPhaseOrderContractTests` 117·190({HandCardPlayed|BombPlayed|BombTokenPlayed}, PpeokFormed는 HandCardPlayed 뒤만) | `BombEngineTests`(PpeokRuleTests.CreateFixture 시드 순회 + `LayOnFloor`로 4번째 장 바닥 배치): 폭탄 → CardsCaptured 4장·토큰 2·Kind.Bomb 약탈; 폭탄패 턴에 HandCardPlayed 없음·쪽 불성립·싹쓸이 성립; 빈손+토큰이면 고/스톱 제시; 뮤테이션 ① 토큰 미차감 ② TryFormPpeok 가드 제거 | grep `_handPlayFact == null` 2곳 |
| **C2a** 밸런스 행 | Jarvis(+코디네이터 시트) / Sonny | `Domain/Balance/SettlementBalance.cs`, `Infrastructure/GameData/BgBalanceLoader.cs`(179-212), 구글 시트 GameConfig 행 `bomb_multiplier`=2 → 에디터 임포트 → `Assets/Resources/bansheegz_database.bytes` | `BgBalanceLoaderTests` 55-80 표+완전성, `BalanceContractsTests` 74-81·102, `BakJudgeTests` 171, `HandScoreCalculatorTests` 274 | 표 행 1건 | grep `Require(values, "bomb_multiplier")`, 부팅 예외 0 |
| **C2b** 정산 | Jarvis / Sonny | `Scoring/LootSettler.cs`(BombMultiplierFor·Settle·LootMultiplier 7인자), `Match/MatchFlow.cs`(SettleRound 739·LootMultiplierOf 1044·SettlementApplied 783), `DevSandbox/EffectGymMeasure.cs:238` | `LootSettlerTests` 193·315·331·365-377·476·494, `ScoringGoldenCaseTests` 286, `UpgradeScalingGoldenCaseTests` 128, `MatchFlowTests` 385, `MatchGoldenCaseTests` 437(값 불변 확인) | `LootSettler_BombMultiplier_PowersPerCount`(0→1, 2→4), `LootMultiplierOf_ShowsBombRightAfterBomb`; 뮤테이션 거듭제곱 → 곱셈 | grep `BombMultiplierFor(` MatchFlow 2곳 |
| **C2c** 정산창 | Ava / Sonny | `Application/PresentationStep.cs`(RoundSettledStep 715), `PresentationStepConverter.cs` 431, `Hud/RoundSummary.cs` 39·80, `Hud/RoundSummaryView.cs` 420 | `PresentationStepConverterTests` 138 | 요약 항목 1건 | grep `BombMultiplier` in RoundSummary |
| **C3a** AI | Sonny / Jarvis | `Opponents/HeuristicAiPolicy.cs`(PlayBomb 분기·실수 생략·토큰 두 패스) | `HeuristicAiPolicyTests` 126-133 격자, `MatchGoldenCaseTests` 115-199·`OpponentAiWiringTests` 지문 **재동결**(AI가 폭탄을 고르기 시작 — 사유를 시험 헤더에 기록) | `HeuristicAiBombTests`: 폭탄 가능 → 항상 폭탄(레벨 1 포함), 토큰은 최고 치기 ≤ 0일 때만 | — |
| **C3b** 측정 | Jarvis / Sonny | `Simulation/SimMatchRecord.cs`, `MatchSimRunner.cs`(SimObserverSink: 폭탄·폭탄패·Kind.Bomb 약탈; 플레이어 좌석 기회 수 210-224), `SimTelemetry.cs`(추가만, Schema 유지), `SimAggregator.cs`, `Tools/HeadlessSim/Program.cs`(CountingEventSink 101), `Tests/Sweep/RunLadderSweepScratch.cs`(CandidateStats·AccumulateMatch·표 T11) | 직렬화 동결 시험이 있으면 갱신 | 폭탄 횟수 집계 시험; 스윕 1회 실행해 판당 폭탄 빈도·칩 이동 폭 수치 확보 | — |
| **C4a1** 스냅샷 축 | Jarvis / Sonny | `Application/BoardSnapshot.cs`(SeatSnapshot+BombTokens 필수), `BoardSnapshotBuilder.cs`(65·82), `Playback/PresentationBoardModel.cs`(303·309·ToSnapshot), `DevSandbox/AnimationGym.cs`(577·579) | 생산자 5곳 컴파일 강제, `MatchSessionContractTests` 241(무영향 확인) | `Snapshot_BombTokens_FromBoard` | grep `bombTokens:` 5곳 |
| **C4a2** 토큰 뷰·입력 | Ava / Sonny | `Board/BoardView.cs`(175), `Board/CardViewRegistry.cs`(PlaceBombToken·스프라이트), `Cards/CardSpriteTable.cs`(_bombTokenSprite), `input/MatchInputController.cs`(162·316 TargetsCard 필터·토큰 클릭), `input/SelectionCursor.cs`(108), `input/HandReorderDrag.cs`(74) | — | `SelectionCursor_TryMoveTo_IgnoresCardlessActions`(id 0 회귀), `Registry_BombTokens_FaceDownAtHandEnd` | grep `TargetsCard` in TryMoveTo |
| **C4b** 연출·프롬프트 | Ava / Sonny | `Playback/TurnBeatDirector.cs`(BombPlayed WhenAll), `Playback/StepPlayer.cs`(박자 120-162), `Playback/TurnBeatBudget.cs`(폭탄 비트 값), `Board/FloatingTextMotion.cs`(BombPlayedMessage "BOMB!", Bomb 정산은 약탈만), ★`Hud/BombPromptView.cs` + 프리팹(굽기 `run_script`), `Boot/Scenes/MainScene.cs`(430·518·650 배선) | — | `StepPlayer_BombPlayed_UsesBudgetOnly`(시간 리터럴 0), PlayMode `BombPromptView_OpensOnBombableClick_SubmitsPlayBomb`; 재생 프로브: 폭탄 판을 시드로 띄워 캡처(3장 비행·BOMB!·폭탄패 2장 뒷면) | 시간 리터럴 0 |
| **C5** 문서 | 코디네이터 | Notion Ruleset v0.2(§1·§4·변경 기록), 시스템 §2 미채용 목록·점수 문단, 밸런스 "흔들기/폭탄 ×2"→"폭탄 ×2", 핸드오프 §1 룰 표·§3·§5·§7·미결정 표, 메모리 | — | — | 산문 게이트 초록 |

병렬 가능: C3a ∥ C3b ∥ C4a1(파일 겹침 0). 나머지는 순차(허브 파일 `TurnEngine`·`MatchFlow`·`PresentationStep` 직렬화).

## 4. 검증

- 카드마다: `unity command recompile` → `recompile_status` completed → `runtests.py editor <픽스처>` → `ddtest.sh`(EditMode 전량) + `playmode_batch.sh` → `mutate_copy.py <이름>`(사본, 한 건씩, cmp 원복) → 커밋.
- 골든 동결값이 움직이는 카드는 C3a 하나여야 한다. 다른 카드에서 움직이면 계약 누수다.
- 종단: C4b 뒤 재생 프로브로 폭탄 판을 띄워 일곱 항을 캡처한다. 시드는 순회로 찾아 `PendingRunConfig`에 싣는다.
  ① 프롬프트 등장 ② 3장 동시 비행 + 4장 획득 ③ "BOMB!" 1회 ④ 손패 끝 뒷면 2장.
  ⑤ 폭탄패 클릭 시 뒤집기만 ⑥ 상단 배수 ×2 ⑦ 정산창 폭탄 항목. 상대 폭탄은 같은 경로가 자동으로 재생되는지 시드 하나로 확인.
- C3b 스윕 수치(판당 폭탄 기회·발생률·×2가 칩 이동에 주는 폭)를 핸드오프에 기록해 밸런스 재검 근거로 남긴다.

## 5. 위험과 완화

| 위험 | 완화 |
|---|---|
| 시트 행 부재 = 부팅 예외(`Require`) | C2a를 시트 행 + 임포트 + 코드 **한 커밋**. 임포트는 코디네이터가 에디터에서, 안 되면 사용자 |
| 골든·결정론 동결값 이동 | C1b까지 AI 폭탄 비선택, C3a에서 한 번에 재동결하고 사유 기록 |
| id 0 충돌(카드 없는 행동) | `TargetsCard` 필터 3곳 + 회귀 시험 |
| 상대 폭탄 3장 정체 누수(폴드 종류 미상) | `HandCardDefinitions` echo + 변환 시험 |
| Judge 시그니처 파급 | `TurnHalfFacts`로 한 번만 바꾼다 |
| 위임 절단(카드당 파일 5·계층 3 상한) | 13카드 분할이 그 상한. 초과 징후면 카드 안에서 다시 가른다 |

## 6. 문서 (C5 상세)

- Ruleset v0.1 → **v0.2**: §1 제외 목록에서 폭탄 삭제·포함에 추가, §4 폭탄 항(§1 표).
  변경 기록에는 "2026-09-29 v0.2 폭탄 채용(사용자 승인)"을 적는다.
- 시스템 디자인 §2: 미채용 목록에서 폭탄 제거, 점수 문단 "흔들기·총통 ×2" → "폭탄 ×2".
- 밸런스 데이터: "흔들기/폭탄 각 ×2 × 박" → "폭탄 ×2ⁿ × 박". 핸드오프 §1 룰 표 행 추가, 미결정 표 "폭탄·자뻑" → "자뻑(뻑 계열, 보류)".

## 7. 진행 상태

| 카드 | 상태 | 커밋 | 검증 |
|---|---|---|---|
| C0a 도메인 어휘(+응용 미러 enum) | 완료 (2026-09-30) | Double Down `6bb75f5` | EditMode 1489 → 1491, PlayMode 129, 뮤테이션 CA 2/2 사망 |
| C0b 스텝 어휘·변환·폴드 | 완료 (2026-09-30) | Double Down `8b99f66` | EditMode 1491 → 1496, PlayMode 129, 뮤테이션 CB 2/2 사망 |
| C1a 규칙·판정 | 완료 (2026-09-30) | Double Down `805dedd` | 라이브 5픽스처 90건, EditMode 1496 → 1520, PlayMode 129, 뮤테이션 CC 5/5 사망 |
| C1b 엔진 | 완료 (2026-09-30) | Double Down `5531ec1` | 라이브 10픽스처 145건, EditMode 1520 → 1532, PlayMode 129, 뮤테이션 CE 5/5 사망 |
| C2a 밸런스 행 | 완료 (2026-09-30) | Double Down `c369960` | 라이브 4픽스처 97건, EditMode 1532 → 1534, PlayMode 129, 뮤테이션 CF 2/3 사망(CF1 생존, 아래) |
| C2b 정산 | 완료 (2026-09-30) | Double Down `5263a47` | 라이브 5픽스처 63건, EditMode 1534 → 1540, PlayMode 129, 뮤테이션 CG 9/9 사망 |
| C2c 정산창 | 완료 (2026-09-30) | Double Down `f6644c5` | 라이브 5픽스처 121건, EditMode 1540 → 1545, PlayMode 129, 뮤테이션 CH 4/4 사망 |
| C3a AI | 완료 (2026-09-30) | Double Down `1fd7d2f` | EditMode 1545 → 1556(C4a1과 합본 검증), PlayMode 129, 뮤테이션 CI 3/3 사망, 골든 케이스 2 재동결·공개 누수 시드 2 → 5 |
| C4a1 스냅샷 축 | 완료 (2026-09-30) | Double Down `05ce785` | 같은 합본 검증, 뮤테이션 CJ 6/6 사망 |
| C4a2 토큰 뷰·입력 | 완료 (2026-09-30) | Double Down `ad43ade` | 라이브 Presentation 496, EditMode 1556 → 1568, PlayMode 129 → 132, 뮤테이션 CK 5/5·CL 5/5 사망, 재생 캡처 확인 |
| (끼어든 작업) 약탈 곱 오버플로 가드 | 완료 (2026-09-30) | Double Down `58232c5` | EditMode 1568 → 1575, PlayMode 132, 뮤테이션 CM 5/5 사망, 골든 동결값 변경 0 |
| C4b 연출·프롬프트 | 완료 (2026-09-30) | Double Down `0b4478c`(연출) · `6eddaa3`(프롬프트) | EditMode 1575 → 1598, PlayMode 132 → 134, 뮤테이션 CN 3/3·CP 3/3·CQ 5/5 사망, 종단 프로브 7항 통과(아래) |
| C3b 측정 | 완료 (2026-09-30) | Double Down `26f291d`(레코드·집계) · `2f2e700`(도구·스윕) · `f12164d`(주석) | EditMode 1598 → 1602, PlayMode 134, 뮤테이션 CR 9/9 사망, 헤드리스 5000시드 대조, 사다리 스윕 T11 |
| C5 문서 | 완료 (2026-09-30) | Samantha 핸드오프 · Notion 3쪽 | 산문 게이트 초록 |

- **C3b 메모**: 계획의 "플레이어 좌석 기회 수"는 넣지 않았다. 휴리스틱 정책은 폭탄이 합법이면 항상 치므로 기회 수와 발생 수가 같다.
  레코드 축은 `SimBombTally`(좌석별 폭탄·폭탄패)와 `SimRoundTransfer.BombMultiplier`, 집계는 `SimBombSummary`와 `RoundSum`이다.
  JSONL은 키를 더하기만 해서 `schemaVersion` 1을 유지한다. 폭탄패 "2"는 도구가 `DomainEventContract.BombTokenGrant`를 읽는다.
  시험 작성자가 명세의 구멍 둘을 메웠다. 첫 선 픽에서 끊긴 실패 레코드는 전부 0이라 집계 제외를 검증하지 못했고(둘째 판에서
  던지는 결함 정책을 더했다), 시드 1~400에는 나가리가 없어 판 수 합과 정산 수가 같은 값이었다(범위를 600으로 넓혔다).
- **측정값(2026-09-30)**: 헤드리스 5000시드(자리채움 밸런스, 상대 칩 720). 폭탄은 라운드당 0.27회(양 좌석 합)·매치당 0.48회,
  폭탄패 사용률 70.9%, 폭탄 배수가 걸린 정산 14.6%, 그 정산의 평균 약탈은 클램프 전 2391(전체 1325)·클램프 후 899(전체 723).
  배수 2 대 1: 1라운드 종료 49.5% 대 43.1%, 라운드 상한 패배 10.8% 대 14.5%, 라운드당 약탈 클램프 전 1325 대 1139·클램프 후 723 대 691.
  사다리 스윕(시트값, 후보 10개 × 2000런): 라운드당 0.29회, 폭탄패 사용률 70~71%, 폭탄 배수 정산 16.0~16.4%,
  그 정산의 평균 이전량 948~980(전체 713~741). 대조군(강화 0) 1막 클리어율 11.3%(2026-09-07 기준선 9.2%. 그 사이 다른 변경도 있다).
  대조군 실행은 같은 궤적에서 배수만 뺀 것이 아니다. AI 판단과 칩 이전량이 함께 갈려 폭탄 수도 달라진다(4808장 대 5122장).
- **C3b에서 밟은 것**: 산문 게이트를 `| tail`로 잘라 읽으며 같은 줄에서 커밋해 빨간불(줄표 2줄)인 채 `2f2e700`이 나갔다.
  `f12164d`로 고쳤다. 게이트는 파일로 받아 `if`로 가른다.

- **C4b 메모**: 커밋을 둘로 갈랐다. 연출(`TurnBeatDirector`·`StepPlayer` 박자)은 프롬프트 없이도 서고, 프롬프트는 뷰·프리팹·주소 엔트리·
  씬 배선이 한 몸이다. 계획과 달라진 것 셋. ① `TurnBeatBudget`에 폭탄 전용 값을 더하지 않았다(획득으로 가는 손패 치기와 같은 박자를
  기존 값으로 조립한다). ② `FloatingTextMotion`은 고치지 않았다(폭탄 약탈의 특수 순간이 이미 "BOMB!"을 띄운다). ③ 프리팹은 새로 그리지
  않고 `GoStopView.prefab`을 밑그림으로 굽는다(`AgentScripts/BakeBombPromptView.cs`, 두 번째 실행 바꾼 것 0건). 그래서 이후 `GoStopView`
  디자인 변경을 따라가지 않는다. 남긴 것: Esc로 닫는 길 없음(선례 없음, 가림막 클릭으로 닫는다), 도착 뜸 없음, 폭탄패 퇴장 연출 없음,
  `MainScene` 배선은 자동 시험이 없고 프로브로만 확인했다.
- **종단 프로브(계획 §4, 2026-09-30)**: 시드 코드 `00000380`, 대본 `5:0 6:0 1:2 1:3 1:4 1:5 1:7 4:0`(종류:카드 id). 부트 씬에서 재생해
  타이틀의 시작 문(`TitleScene.OnRunStartRequested`)으로 시드를 넣었다. ① 3월 손패 클릭 → 프롬프트 ② [폭탄] → 3장이 함께 떠나 바닥 3월
  위에 쌓임, 그 턴 획득 5장(4장 + 약탈 1) ③ "BOMB! +1 PI" 1회 ④ 손패 7 + 뒷면 2 ⑤ 폭탄패 클릭 → 프롬프트 없이 더미만 뒤집힘(손패 7 유지,
  폭탄패 1) ⑥ 고/스톱 제시 시점 상단 배수 28 = 7점 × 피박 2 × 폭탄 2(점수가 0인 동안은 0으로 보인다) ⑦ 정산창 박 줄 `피박 · 폭탄 x2`.
  같은 판 3턴째에 상대도 폭탄을 냈다. 3장이 앞면으로 뒤집히며 함께 날고 "FOE BOMB! +1 PI"가 뜬다(같은 경로 자동 재생 확인).
  시드 탐색은 편집 모드 eval에서 프로덕션 공장(`MatchSessionFactory`)으로 했다. 코드 1..400 중 첫 입력에 폭탄이 합법인 판이 20개다.
  도구는 스크래치패드의 `probe_e2e_seed.cs`·`e2e_bomb.py`(세션 한정).
- **프로브에서 본 것(범위 밖)**: 특수 순간 글자가 흔들릴 때 판 오른쪽 세로 패널 밑으로 들어가 끝 글자가 잘리는 프레임이 있다
  (`FOE BOMB! +1 PI`가 가장 길다). 폭탄 이전부터 있던 외침 배치의 성질이다.

- **C2b 메모**: 흐름 수준 시험(`MatchFlowTests` 2건)을 C3a로 미루지 않고 이 카드에 넣었다. 기존 흐름 시험은 전부 폭탄 0회라
  `SettleRound`·`LootMultiplierOf` 배선 뮤테이션(CG2·CG3·CG4)이 새 2건 없이는 전부 살아남는다. 표본은 시드 1..400 첫 판을
  "폭탄이 합법이면 폭탄" 구동으로 모으고, 표시 배수는 스톱 직전 값으로 정산 `BaseSteal`과 대조한다(기대값 재계산 없음).
- **빈손 확정 판**: 손패·폭탄패가 비면 제시 없이 스톱이 확정돼 `AwaitingGoStop`을 거치지 않는다. 표시 배수를 읽을 시점이 없어
  표본의 `ReadoutBeforeStop`은 `int?`다. 첫 실행에서 전제 단언이 이 판(시드 2)을 잡았다.
- **독립 리뷰 뒤 보강**: 흐름 시험이 밑수 3 밸런스를 주입한다(`Placeholder` 고정 뮤테이션 CG6·CG9 사망). 표본 보장 단언은
  승자 > 패자, 패자 ≥ 1, 승자 좌석별 비대칭 넷이다(좌석 고정 CG7·상대 좌석 CG8 사망).
- **C2c 메모**: 박 줄(`Text_Bak`, 칸 950)에 `폭탄 x{n}`을 끝 낱말로 잇는다. 폰트(`NeoDunggeunmoPro-Regular SDF`, 정적)가
  `폭`·`탄`을 직접 갖고, 최악 조합 다섯 낱말이 594라 넘치지 않는다(에디터 측정). 플레이 캡처는 입력 경로가 생기는 C4b 프로브 ⑦에서 한다.
  나가리 이월 배수는 박 줄에 아직 없다(기존 공백, 범위 밖).
- **C3a 메모**: 재동결로 움직인 것은 2건뿐이다(골든 케이스 2, 공개 누수 시드). 시드 3은 유지했다. 새 1라운드는 상대 4월 폭탄 →
  Σ칩 42 × 기본 7 × 피박 2 × 폭탄 2 = 1176이고 2라운드 전개는 같다. 폭탄 배수가 빠져도 최종 결과(PlayerAllIn, 0/1920)는 같아서
  배수를 잡는 단언은 중간값 셋(2R 시작 칩 24/1896, 1R 약탈 1176, 2R 이전 24)이다. 폭탄 결정에서 난수를 한 번 뽑는 뮤테이션(CI2)도
  이 골든이 잡는다. 시드 구동 매치에 폭탄패를 내는 판은 아직 없다(CI3은 단위 시험 하나만 죽였다).
- **C4a1 메모**: 판 경계 초기화 코드는 없다. 폴드가 판마다 분배 스냅샷에서 새로 시작하고 `RoundStartedStep`은 폴드에서 예외다.
  구현자와 시험 작성자가 각각 코디네이터 명세("RoundStarted에서 0 대입")를 바로잡았다.
- **C4a2·C4b가 밟을 함정(독립 리뷰)**: ① 스톱으로 닫힌 배치에서 `StepPlayer.cs:352-357`은 권위 렌더를 건너뛰어 판 표면에 폴드 값이
  남는데 `MainScene.cs:985-988`은 같은 배치 끝에 `_matchView.Render(authority)`를 부른다. 폭탄패를 판 표면과 HUD 중 어디에 두느냐로
  스톱 직후 값이 갈린다(권위는 판이 없어 0). ② 커서가 합법 목록 전량을 든다(`MatchInputController.cs:82`). `PlayBomb`은 대표 카드 id가
  손패 치기와 같아 배지가 두 번 붙고 방향키 + 확인으로 지금도 제출된다. `PlayBombToken`은 id 0이라 실재 카드 0번에 걸린다.
  ③ `TurnBeatDirector.cs:178-213`·`StepPlayer.cs:119-160`에 폭탄 스텝 분기가 없어 상대 폭탄은 3장이 모션 없이 바닥에 놓인다.
  ②는 C1b부터, ③은 C3a부터 플레이에서 보이는 중간 상태다. C4a2·C4b가 닫는다.
- **C4a2 메모**: 계획의 전용 문(`PlaceBombToken`)을 만들지 않았다. `BoardView.Render`가 손패 목록 끝에 뒷면 카드
  (`CardSnapshot.FaceDown(BombTokenCardIds.Of(seat, i))`, 합성 id 1000번대)를 이어 붙이면 `PlaceZone`이 목록 길이를 부채 배치의
  분모로 써서 간격·회수·입력 대상 부착이 손패 경로 그대로 된다. 커서에는 `PlayBomb`을 뺀 목록이 들어간다(`CursorActionsOf`).
  그래서 **C4b 전까지 플레이어는 폭탄을 낼 길이 없다.** C4b가 받을 것: 컨트롤러가 걸러낸 `PlayBomb`을 보관하지 않으므로
  프롬프트가 "이 손패의 달에 폭탄이 합법인가"를 알려면 `Refresh`에서 걸러낸 목록을 필드로 들어야 한다. 폭탄패를 쓰면 누른 장이
  아니라 끝 장의 뷰가 회수된다(id가 순번 기반, 퇴장 연출 없음). 회수 계약은 `Object.Destroy` 때문에 PlayMode 시험이다
  (`Assets/Tests/Integration/BombTokenViewRecycleTests.cs`). 전용 스프라이트 칸은 `CardSpriteTable._bombTokenSprite`(비어 있음).
- **약탈 곱 오버플로(끼어든 작업, 사용자 요청)**: 측정 결과 보수적 최악은 Σ칩 219 × 약탈 배수 21,430,272 = 46.9억(2^31의 2.19배)이다.
  배수 단독은 int의 1%다. 족보 강화 레벨에 코드상 상한이 없어 여유는 성장형이다. 처방의 규칙은 "칩이 낀 금액은 `long`, 배수만의 곱은
  `checked int`"다(`BaseLoot`·`PreMultiplierLoot`는 long, `LootMultiplier`·`CombinedMultiplier`·`GoMultiplier`는 checked int). 처음에는
  `BaseLoot`만 넓혔다가, 프로덕션이 읽지 않는 진단값 `PreMultiplierLoot`의 checked가 계산 가능한 정산을 예외로 만드는 것을 보고 고쳤다.
  2^32를 넘으면 음수가 아니라 틀린 양수로 접힌다(bet_min 증상도 없다). 화면 배수 칸은 넓히지 않았다(생산 지점 25곳).
  남긴 것: `BakJudge.cs:41`과 Σ칩 합산은 unchecked, AI가 고 + 1의 고배수를 미리 계산해 예외가 난다면 정산보다 먼저 난다.
- **환경 사고(2026-09-30 16:05)**: `%TEMP%` 나이 기준 정리가 배치 사본의 `Library/PackageCache`에서 수정 시각이 오래된 파일(에디터 내장
  패키지, 2026-06-24)과 스크래치패드의 오래된 스크립트(`runtests.py`·`playmode_batch.sh`)를 지웠다. 증상은 배치 컴파일 오류 7545건(전부
  패키지·시험 어셈블리, 우리 코드 0건). `ddtest.sh --full-sync`(1분 42초)로 복구하고 `playmode_batch.sh`를 다시 썼다. 사본이 임시 폴더
  아래에 있는 한 재발한다. 사본 위치 이전은 사용자 결정 대기.
- **기술 부채(리뷰 발견, 별도 작업 칩)**: 약탈 공식의 곱(`BaseLoot`·`CombinedMultiplier`·정적 `LootMultiplier`)이 unchecked `int`다.
  2^31을 넘으면 음수가 되어 bet_min만 이전된다. 폭탄이 상한을 최대 3비트 당긴다. 현재 밸런스에서 닿는지 미측정.
- 낡은 주석 1건 남음: `RoundFlowEvents.cs:199` 수식 본문에 폭탄 항이 없고 `:205`에 덧붙인 문장만 있다(C5 문서 정리 때 같이 본다).

- 미러 enum 5파일은 계획의 C0b에서 C0a로 옮겼다. 도메인 enum만 넣으면 미러 시험 2건이 빨강이라 한 커밋이어야 했다
  (뻑 선례 `713e841`도 같았다).
- 시험 내 지문 사본 7곳은 C0a가 아니라 **C1b**에서 고친다. 발행자가 없는 동안은 그 분기에 닿지 않는다.
- 2026-09-30 현재 에디터가 닫혀 있어 안쪽 겹(라이브)은 건너뛰고 배치로만 검증한다. C2a(시트 임포트)와 C4(굽기·재생
  프로브)는 에디터가 필요하다.
- **C1b 메모(시험 작성자 발견)**: `SpecialSituationRuleTests.cs:680` `AssertStealContract`가 같은 턴의 감지를 Kind 숫자
  오름차순으로 단언한다. 폭탄은 값 5인데 순서는 맨 앞이라 엔진이 폭탄 + 싹쓸이를 발행하면 깨진다. C1b에서 "판정자 순서"
  기준으로 고친다.
- **등가 뮤테이션 주의**: 한 달이 4장이라 손패 3장이면 바닥은 최대 1장이다. `바닥 == 1`을 `>= 1`로 바꾸는 뮤테이션은
  실제 판에서 죽지 않는다. 시험은 분배판 밖 다섯 번째 장을 만들어 고정했다(`CollectBombMonths_ThreeInHandAndTwoOnFloor_IsEmpty`).
- **신규 `.cs`의 `.meta`**: 에디터가 닫혀 있어 배치 사본의 Unity가 만든 `.meta`를 회수해 짝을 맞춘다. 다음 동기화
  (`robocopy /MIR`)가 사본의 `.meta`를 지우기 전에 회수해야 GUID가 고정된다.
- **기술 부채(CF1 생존)**: `BgBalanceLoader`가 `bomb_multiplier` 자리에 `pi_bak_multiplier`를 읽어도 시험이 초록이다. 시트값이 둘 다
  2라 값 동등 비교로는 슬롯 오배선이 안 보인다. 값 2인 키 7개(pi_bak·gwang_bak·go_bak·meongtta·draw_carry·go_multiplier_base·
  go_min_lines)에 같은 맹점이 이미 있다. 처방은 행 딕셔너리를 주입하는 seam(`FromRows`)과 키마다 값이 전부 다른 고정구다.
  프로덕션 seam이 필요해 별도 카드로 뺀다.
- C2a의 시트 행은 BGDatabase 에디터 API(`BGRepoSaver.SaveAndMarkAsSaved`)로 DB에 먼저 넣고 구글 시트 28행에 같은 `_id`
  (`Jjz8aTgKjUWjjD9WIVuUCg`)로 적었다. 다음 시트 임포트가 둘을 같은 행으로 본다.
