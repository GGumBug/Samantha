"""배치 사본(dd-batch)에만 뮤테이션을 넣고 EditMode 전량을 돌린다. 원본 작업 트리는 읽기만 한다.

원본 파일이 미커밋이라 원본에 주입하면 게이트(git diff 비어 있음)를 못 채운다.
사본에 넣으면 원본을 잃을 경로가 구조적으로 없다. 매 회 사본 파일을 원본 바이트로 되돌리고 대조한다.
"""
import io
import subprocess
import sys
import xml.etree.ElementTree as ET

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SRC = "C:/Unity_Projects/Double-Down"
DST = "C:/Unity_Projects/dd-batch"
UNITY = "C:/Program Files/Unity/Hub/Editor/6000.3.19f1/Editor/Unity.exe"
RESULTS = DST + "/results-mutation.xml"
LOG = DST + "/batch-mutation.log"

L = "Assets/Scripts/Presentation/Board/CardChipLabel.cs"
V = "Assets/Scripts/Presentation/Board/ChipLabelView.cs"
R = "Assets/Scripts/Presentation/Board/CardViewRegistry.cs"
CV = "Assets/Scripts/Presentation/Board/CardView.cs"
P = "Assets/Prefabs/UI/ChipLabel.prefab"
T = "Assets/Resources/Cards/CardSpriteTable.asset"
S = "Assets/Scripts/Domain/Randomness/RunSeedCode.cs"
RC = "Assets/Scripts/Boot/RunConfig.cs"
MF = "Assets/Scripts/Boot/MatchSessionFactory.cs"
MI = "Assets/Scripts/Boot/MatchSceneInstaller.cs"
RV = "Assets/Scripts/Presentation/Title/RunSetupView.cs"
TS = "Assets/Scripts/Boot/Scenes/TitleScene.cs"
HP = "Assets/Scripts/Presentation/Hud/JokboHintPlan.cs"
HV = "Assets/Scripts/Presentation/Hud/JokboHintView.cs"
HT = "Assets/Scripts/Presentation/Hud/JokboTracker.cs"
HL = "Assets/Scripts/Presentation/Hud/JokboTrackerLine.cs"
RSV = "Assets/Scripts/Presentation/Hud/RoundSummaryView.cs"
HW = "Assets/Scripts/Presentation/Hud/HudWords.cs"
IJ = "Assets/Prefabs/UI/Item_Jokbo.prefab"
SM = "Assets/Scripts/Application/ScoreLineMembers.cs"

GOV = "Assets/Scripts/Presentation/Hud/GameOverView.cs"
SER = "Assets/Scripts/Presentation/Hud/SummaryExitRule.cs"
GOP = "Assets/Prefabs/UI/GameOverView.prefab"

TV = "Assets/Scripts/Presentation/Title/TitleView.cs"
TSC = "Assets/Scenes/TitleScene.unity"

BSR = "Assets/Scripts/Presentation/Board/BoardSurfaceRect.cs"
FWR = "Assets/Scripts/Presentation/Board/FloorWellRect.cs"
MS = "Assets/Scripts/Boot/Scenes/MainScene.cs"

SR = "Assets/Scripts/Domain/Round/SeonResolver.cs"
RRR = "Assets/Scripts/Domain/Run/RunRulesReducer.cs"
RRL = "Assets/Scripts/Domain/Run/RunRules.cs"
DC = "Assets/Scripts/Domain/Decks/DeckCatalog.cs"
MFL = "Assets/Scripts/Domain/Match/MatchFlow.cs"

TW = "Assets/Scripts/Presentation/Title/TitleWords.cs"
RSP = "Assets/Prefabs/UI/RunSetupView.prefab"
CS = "Assets/Scripts/Presentation/Cards/CardSpriteTable.cs"
BDM = "Assets/Scripts/Boot/BombDebugMode.cs"
MSR = "Assets/Scripts/Simulation/MatchSimRunner.cs"
STL = "Assets/Scripts/Simulation/SimTelemetry.cs"
SAG = "Assets/Scripts/Simulation/SimAggregator.cs"
TBD = "Assets/Scripts/Presentation/Playback/TurnBeatDirector.cs"
SPL = "Assets/Scripts/Presentation/Playback/StepPlayer.cs"
BPV = "Assets/Scripts/Presentation/Hud/BombPromptView.cs"
GSS = "Assets/Scripts/Domain/Scoring/GoStopState.cs"
BV = "Assets/Scripts/Presentation/Board/BoardView.cs"
BTI = "Assets/Scripts/Presentation/Board/BombTokenCardIds.cs"
CVR = "Assets/Scripts/Presentation/Board/CardViewRegistry.cs"
SC = "Assets/Scripts/Presentation/input/SelectionCursor.cs"
MIC = "Assets/Scripts/Presentation/input/MatchInputController.cs"
HRD = "Assets/Scripts/Presentation/input/HandReorderDrag.cs"
HAP = "Assets/Scripts/Domain/Opponents/HeuristicAiPolicy.cs"
BSB = "Assets/Scripts/Application/BoardSnapshotBuilder.cs"
RSM = "Assets/Scripts/Presentation/Hud/RoundSummary.cs"
LST = "Assets/Scripts/Domain/Scoring/LootSettler.cs"
SBL = "Assets/Scripts/Domain/Balance/SettlementBalance.cs"
BBL = "Assets/Scripts/Infrastructure/GameData/BgBalanceLoader.cs"
TE = "Assets/Scripts/Domain/Turn/TurnEngine.cs"
FTM = "Assets/Scripts/Presentation/Board/FloatingTextMotion.cs"
BR = "Assets/Scripts/Domain/Turn/BombRule.cs"
SSR = "Assets/Scripts/Domain/Turn/SpecialSituationRule.cs"
RB = "Assets/Scripts/Domain/Board/RoundBoard.cs"
PBM = "Assets/Scripts/Presentation/Playback/PresentationBoardModel.cs"
PSC = "Assets/Scripts/Application/PresentationStepConverter.cs"
TFE = "Assets/Scripts/Domain/Events/TurnFlowEvents.cs"
DEF = "Assets/Scripts/Domain/Replay/DomainEventFingerprint.cs"
SKT = "Assets/Tests/Presentation/CardSkinTests.cs"
RG = "Assets/Scripts/Presentation/Board/CardViewRegistry.cs"
BLA = "Assets/Resources/Board/BoardLayoutConfig.asset"
BLC = "Assets/Scripts/Presentation/Board/BoardLayoutConfig.cs"

MUTATIONS = [
    ("C1", L, "private const float TabHeightFactor = 0.24f;", "private const float TabHeightFactor = 0.30f;", "높이비"),
    ("C2", L, "private const float TopGapFactor = 0.04f;", "private const float TopGapFactor = 0f;", "간격"),
    ("C3", L, "rect.pivot = new Vector2(0.5f, 0f);", "rect.pivot = new Vector2(0.5f, 0.5f);", "피벗"),
    ("C4", L, "rect.localPosition = new Vector3(center.x, center.y + size.y * (0.5f + TopGapFactor), 0f);",
     "rect.localPosition = new Vector3(0f, size.y * (0.5f + TopGapFactor), 0f);", "카드 중심 무시"),
    ("C5", L, "float scale = size.y * TabHeightFactor / authored;", "float scale = 3.4f * TabHeightFactor / authored;", "카드 크기 상수화"),
    ("C6", L, "if (Value != chips || isFirstShow)", "if (isFirstShow)", "재질의 캐시"),
    ("C7", L, "            if (_tab != null)\n            {\n                _tab.ApplySorting(sortingLayerId, sortingOrder);",
     "            if (false)\n            {\n                _tab.ApplySorting(sortingLayerId, sortingOrder);", "뜬 뒤 정렬 미전달"),
    ("C8", L, "_tab.ApplySorting(_sortingLayerId, _sortingOrder);", "_tab.ApplySorting(_sortingLayerId, 0);", "생성 시 정렬 미전달"),
    ("C9", L, "            if (_tab != null)\n            {\n                DestroySafely(_tab.gameObject);",
     "            if (false)\n            {\n                DestroySafely(_tab.gameObject);", "프리팹 교체 시 옛 인스턴스 방치"),
    ("C10", L, "                DestroySafely(instance);", "                instance.SetActive(false);", "뷰 없는 인스턴스 방치"),
    ("C11", L, "            if (_tab != null)\n            {\n                _tab.gameObject.SetActive(false);",
     "            if (false)\n            {\n                _tab.gameObject.SetActive(false);", "숨기기 죽음"),
    ("C12", V, "LayoutRebuilder.ForceRebuildLayoutImmediate((RectTransform)transform);", "transform.GetType();", "루트 재측정 죽음"),
    ("C13", V, "LayoutRebuilder.ForceRebuildLayoutImmediate(panel);", "panel.GetType();", "판 재측정 죽음"),
    ("C14", L,
     "                _isShown = true;\n                tab.gameObject.SetActive(true);\n            }\n\n            if (Value != chips || isFirstShow)\n            {\n                Value = chips;\n                tab.SetValue(chips);\n            }",
     "                _isShown = true;\n            }\n\n            if (Value != chips || isFirstShow)\n            {\n                Value = chips;\n                tab.SetValue(chips);\n            }\n\n            if (isFirstShow)\n            {\n                tab.gameObject.SetActive(true);\n            }",
     "켜기 전에 값 넣기"),
    ("C15", R, "view.SetChipLabelPrefab(_sprites.ChipLabelPrefab);", "view.SetChipLabelPrefab(null);", "레지스트리가 프리팹을 안 민다"),
    ("C16", CV, "_chipLabel.SetPrefab(prefab);", "_chipLabel.SetPrefab(null);", "뷰가 프리팹을 안 넘긴다"),
    ("B1", V, "for (int v = chips; v >= 4; v >>= 1)", "for (int v = chips; v >= 8; v >>= 1)", "구간 경계 밀림"),
    ("B2", V, "color = _bandColors[Mathf.Min(BandIndexOf(chips), _bandColors.Length - 1)];",
     "color = _bandColors[BandIndexOf(chips) % _bandColors.Length];", "위를 닫고 순환"),
    ("B3", V, "                _value.color = color;", "                color.GetHashCode();", "글자색 안 칠함"),
    ("B4", V, "if (_bandColors == null || _bandColors.Length == 0)", "if (_bandColors == null)", "빈 목록 가드 죽음"),
    ("S1", S, "return character >= '0' && character <= '9';", "return char.IsDigit(character);", "다른 문자 체계 숫자 허용"),
    ("S2", S, "if (code == null || code.Length != Digits)", "if (code == null || code.Length > Digits)", "길이 검사 느슨"),
    ("S3", S, "return new string(ZeroDigit, Digits - count) + new string(digits, 0, count);",
     "return new string(digits, 0, count);", "앞 0 채우기 죽음"),
    ("S4", S, "            return new RootSeed(value);", "            return new RootSeed(value * 2654435761UL);", "코드를 해시로 접음"),
    ("S5", S, "digits[index] = (char)(ZeroDigit + random.Next(0, 10));",
     "digits[index] = (char)(ZeroDigit + new System.Random().Next(0, 10));", "난수원 무시"),
    ("S6", S, "for (int index = 0; index < Digits; index++)",
     "for (int index = 0; index < 0; index++)", "무작위 자릿수 루프 죽음"),
    ("S7", S, "public const int Digits = 8;", "public const int Digits = 7;", "자릿수 변경"),
    ('R1', RC, 'private const string DefaultSeedCode = "20260721";', 'private const string DefaultSeedCode = "11111111";', '기본 시드 변경', "PlayMode"),
    ('R2', RC, 'Seed = RunSeedCode.ToRootSeed(seedCode);', 'Seed = new RootSeed(0UL);', '코드와 무관한 시드', "PlayMode"),
    ('R3', RC, 'if (!RunSeedCode.IsValid(seedCode))', 'if (false)', '생성자 검사 죽음', "PlayMode"),
    ('R4', RC, '_value = config ?? throw new ArgumentNullException(nameof(config));', '_value = config;', '널 거부 죽음', "PlayMode"),
    ('R5', RC, '            _value = RunConfig.Default;', '            _value = _value;', '되돌리기 죽음', "PlayMode"),
    ('R6', RC, 'public static RunConfig Value => _value;', 'public static RunConfig Value => RunConfig.Default;', '언제나 기본값', "PlayMode"),
    ('R7', MF, ': this(randomFactory, opponentCatalog, balances, run, RunConfig.Default.Seed)', ': this(randomFactory, opponentCatalog, balances, run, new RootSeed(7UL))', '기본 경로 시드 변경', "PlayMode"),
    ('R8', MI, 'PendingRunConfig.Value.Seed);', 'RunConfig.Default.Seed);', '설치자가 전달자를 무시', "PlayMode"),
    ('V1', RV, 'private void RaiseStart() => StartRequested?.Invoke(_seedInput != null ? _seedInput.text : string.Empty);', 'private void RaiseStart() => StartRequested?.Invoke("11111111");', '시작이 화면 글자 대신 상수를 올림', "PlayMode"),
    ('V4', RV, 'public void Open() => gameObject.SetActive(true);', 'public void Open() { }', '여는 문이 죽음', "PlayMode"),
    ('V5', RV, 'private void RaiseRandomize() => RandomizeRequested?.Invoke();', 'private void RaiseRandomize() => Cancelled?.Invoke();', '무작위가 취소 신호를 냄', "PlayMode"),
    ('V2', TS, 'string code = RunSeedCode.Normalize(text) ?? RunSeedCode.Random(_codeRandom);', 'string code = RunSeedCode.Random(_codeRandom);', '입력한 코드를 버림', "PlayMode"),
    ('V3', TS, 'PendingRunConfig.Set(new RunConfig(code));', 'PendingRunConfig.Reset();', '고른 코드를 전달하지 않음', "PlayMode"),
    ('H1', HP, 'state = JokboHintCardState.Owned;', 'state = JokboHintCardState.Open;', '내 카드를 열린 것으로'),
    ('H2', HP, 'state = JokboHintCardState.TakenByOpponent;', 'state = JokboHintCardState.Open;', '상대 카드를 열린 것으로'),
    ('H3', HP, 'output.Clear();', 'output.GetType();', '출력을 비우지 않음'),
    ('H4', HV, 'cell.color = ResolveColor(card.State);', 'cell.color = OwnedColor;', '상태를 무시하고 한 색으로'),
    ('H10', HP, 'if (Contains(mine, member))', 'if (Contains(mine, member) && !Contains(theirs, member))', '판정 순서 뒤집기'),
    ('H11', HV, 'JokboHintCardState.Open => NotOwnedColor,', 'JokboHintCardState.Open => OwnedColor,', '열린 칸이 내 색이 됨'),
    ('W1', RSV, 'return _slideRestingPosition - new Vector2(0f, SlideTravel());', 'return _slideRestingPosition + new Vector2(0f, SlideTravel());', '위에서 내려오게 뒤짐'),
    ('W2', RSV, '            MoveSlideToStart();', '            _ = 0;', '시작 지점으로 안 밀어 둔다'),
    ('W3', RSV, 'return Mathf.Max(travel, panelHeight);', 'return travel;', '바닥 물러섬 죽음'),
    ('W4', RSV, '            SnapSlideToResting();', '            _ = 0;', '닫을 때 자리를 안 되돌림'),
    ('U1', RSV, 'MatchView.SetText(_verdict, VerdictText(summary, exit));', '_ = exit;', '승패 낱말을 안 적음'),
    ('U2', RSV, '_panelBorder.color = BorderColorOf(summary, playerWon);', '_ = playerWon;', '테도리 색이 안 바뀜'),
    ('U3', RSV, '_bakContainer.SetActive(bak != null);', '_bakContainer.SetActive(true);', '박 칸을 항상 켜 둔다'),
    ('U4', RSV, 'if (!summary.IsMatchOver)', 'if (false)', '매치 종료를 안 봄'),
    ('U5', RSV, 'MatchView.SetText(_confirmLabel, HudWords.ConfirmWord(exit) + KeyHintSuffix);', '_ = exit;', '버튼 문구를 안 적음'),
    ('U6', HW, 'return winner == SeatSide.Player ? "승리" : "패배";', 'return "승리";', '진 판도 승리로 적음'),
    ('H18', HT, 'ApplyPanelVisibility(assigned);', '_ = assigned;', '줄이 생겨도 판을 안 켬'),
    ('H19', HT, 'ApplyPanelVisibility(0);', '_ = 0;', '줄이 없어도 판을 안 접음'),
    ('H20', HT, 'gameObject.SetActive(visibleLines > 0);', 'gameObject.SetActive(true);', '판이 영영 켜져 있음'),
    ('H17', HV, 'JokboHintCardState.TakenByOpponent => NotOwnedColor,', 'JokboHintCardState.TakenByOpponent => OwnedColor,', '상대 칸만 다른 어둡기'),
    ('H12', IJ, 'm_Name: Panel_JokboElements\n  m_TagString: Untagged\n  m_Icon: {fileID: 0}\n  m_NavMeshLayer: 0\n  m_StaticEditorFlags: 0\n  m_IsActive: 0', 'm_Name: Panel_JokboElements\n  m_TagString: Untagged\n  m_Icon: {fileID: 0}\n  m_NavMeshLayer: 0\n  m_StaticEditorFlags: 0\n  m_IsActive: 1', '구성 패 칸이 늘 켜져 있음'),
    ('H13', IJ, 'm_RaycastTarget: 0', 'm_RaycastTarget: 1', '카드 템플릿이 커서를 받음'),
    ('H5', HV, '            gameObject.SetActive(false);', '            gameObject.SetActive(true);', '숨기기가 안 꺼짐'),
    ('H6', HT, 'line.ShowElements(_hintCards);', 'line.GetType();', '호버해도 안 띄움'),
    ('H14', HT, 'if (_openLine != line)', 'if (false)', '이탈이 남의 줄까지 닫음'),
    ('H15', HT, 'if (_openLine != null && _openLine != line)', 'if (false)', '옛 줄을 안 닫음'),
    ('H16', HL, '_elements.Hide();', '_elements.GetType();', '줄이 제 칸을 안 접음'),
    ('H7', HL, 'PointerEntered?.Invoke(this);', 'PointerExited?.Invoke(this);', '진입이 이탈 신호를 냄'),
    ('H8', SM, 'return card.Category == CardCategory.Gwang;', 'return card.Category == CardCategory.Yeol;', '광 매핑 오류'),
    ('H9', SM, 'members.Sort(CompareByMonthThenId);', 'members.Reverse();', '정렬 죽음'),
    ("P1", T, "_chipLabelPrefab: {fileID: 5997321827286041994, guid: a1ccd56b6e14f324f99a0396e0d32290, type: 3}",
     "_chipLabelPrefab: {fileID: 0}", "테이블 칸 비움"),
    ("P2", P, "    m_Right: 15", "    m_Right: 5", "판 오른쪽 여백"),
    ("P3", P, "_value: {fileID: 6588402832821177800}", "_value: {fileID: 0}", "숫자 칸 비움"),
    ("P4", P, "_canvas: {fileID: 9051207746195418065}", "_canvas: {fileID: 0}", "캔버스 칸 비움"),
    ("P5", P, "m_RenderMode: 2", "m_RenderMode: 0", "월드 캔버스 아님"),
    ("G1", HW, 'return "칩을 모두 잃었다";', 'return "라운드 안에 꺾지 못했다";', "사유 낱말 하나로 못침"),
    ("G2", HW, "string ordinal = (slotIndex + 1).ToString(CultureInfo.InvariantCulture);",
     "string ordinal = slotIndex.ToString(CultureInfo.InvariantCulture);", "도달 상대 번호 0기준 노출"),
    ("G3", GOV, "private static readonly Color BorderColor = new Color(0.78f, 0.22f, 0.19f, 1f);",
     "private static readonly Color BorderColor = new Color(0.29f, 0.33f, 0.41f, 1f);", "패배 테도리가 라운드 색"),
    ("G4", GOV, "_chosen?.TrySetResult(GameOverChoice.Retry);", "_chosen?.TrySetResult(GameOverChoice.Title);", "재도전 눌렀는데 하이틀로"),
    ("G5", GOV, 'private const string EmptyValue = "-";', 'private const string EmptyValue = "";', "벼 칸 자리표 없음"),
    ("G6", GOV, "            if (_retryButton == null)\n            {\n                return GameOverChoice.Retry;\n            }",
     "            if (_retryButton == null && false)\n            {\n                return GameOverChoice.Retry;\n            }", "배선 붕굴 때 런 교착"),
    ("G7", SER, ": SummaryExit.RunLost;", ": SummaryExit.RunCleared;", "지사가 런 클리어로 들어올"),
    ("G8", GOV, "return _slideRestingPosition - new Vector2(0f, SlideTravel());",
     "return _slideRestingPosition + new Vector2(0f, SlideTravel());", "밑에서가 아니라 위에서 내려오는 밀림"),
    ("G9", GOV, "            SnapSlideToResting();\n            gameObject.SetActive(false);",
     "            gameObject.SetActive(false);", "닫으면 밀린 자리 그대로 남음"),
    ("G10", GOP, "  m_SortingOrder: 300", "  m_SortingOrder: 100", "매치 HUD 아래로 가라지는 창"),
    ("G11", GOP, "_retryButton: {fileID: 8044308209818131764}", "_retryButton: {fileID: 0}", "재도전 칸 배선 끊김"),
    ("T1", TV, "            if (_version != null)", "            if (_version != null \u0026\u0026 false)",
     "\ubc84\uc804 \uce78\uc5d0 \uac12\uc744 \uc548 \ucc44\uc6c0", "PlayMode"),
    ("T2", TV, "            if (_version == null)", "            if (_version == null \u0026\u0026 false)",
     "\ube48 \ubc84\uc804 \uce78\uc744 \uac10\uc0ac\uac00 \ub118\uae40", "PlayMode"),
    ("T3", TSC, "  _version: {fileID: 622132497}", "  _version: {fileID: 0}",
     "\uc528\uc758 \ubc84\uc804 \uce78 \ubc30\uc120 \ub04a\uae40", "PlayMode"),
    ("D1", BSR, '            float topY = config.PlayAreaTopY + config.OffsetFor(BoardZone.OpponentHand).y;', '            float topY = config.PlayAreaTopY;', "위쪽 구역 보정을 빠뜨림"),
    ("D2", BSR, "                window.LeftX - padding,", "                window.LeftX,",
     "\uc67c\ucabd \uc5ec\ubc31 0"),
    ("D3", BSR, '                topY * scale + padding);', '                topY * scale + padding * scale);', "여백에 배율이 곱해짐"),
    ("D4", FWR, "for (int slotIndex = 0; slotIndex < FloorRailModel.MaxSlots; slotIndex++)",
     "for (int slotIndex = 0; slotIndex < 1; slotIndex++)", "\ub808\uc77c \uccab \uce78\ub9cc \ub364"),
    ("D5", FWR, "for (int fanCount = 1; fanCount <= MaxFanCards; fanCount++)",
     "for (int fanCount = 1; fanCount <= 1; fanCount++)", "\ubb34\ub9ac \uc313\uae30 \ubb34\uc2dc"),
    ("D6", MS, "            _boardBackdrop?.Apply(playWindow, boardScale);",
     "            // MUTATION _boardBackdrop?.Apply(playWindow, boardScale);", "\ubc30\uacbd\uc744 \uc544\uc608 \uc548 \ucf1c\uc90c"),
    ("D7", BSR, '            float bottomY = config.PlayAreaBottomY + config.OffsetFor(BoardZone.PlayerHand).y;', '            float bottomY = config.PlayAreaBottomY;', "아래쪽 구역 보정을 빠뜨림"),
    ('K1', MF, '            _run = new RunFlow(_rules.StartChip, _opponentCatalog.FinalAct);', '            _run = new RunFlow(_balances.Match.PlayerStartChip, _opponentCatalog.FinalAct);', '새 런이 덱을 잊고 시트 값으로 섬', "PlayMode"),
    ('K2', MF, '            int runChips = _run.Chips;', '            int runChips = _rules.StartChip;', '덱 이득을 판마다 다시 붙임', "PlayMode"),
    ('K3', RC, '            if (!DeckCatalog.Exists(deckId))', '            if (deckId == 0)', '카탈로그 대신 0만 거름', "PlayMode"),
    ('K4', RC, '        public static RunConfig Default { get; } = new RunConfig(DefaultSeedCode, DeckCatalog.BasicDeckId);', '        public static RunConfig Default { get; } = new RunConfig(DefaultSeedCode, DeckCatalog.ChojjaDeckId);', '기본 설정의 덱이 초짜', "PlayMode"),
    ('K5', TS, '            PendingRunConfig.Set(new RunConfig(code, DeckCatalog.BasicDeckId));', '            PendingRunConfig.Set(new RunConfig(code, DeckCatalog.ChojjaDeckId));', '타이틀이 초짜를 건넴', "PlayMode"),
    ('K6', MI, '                balances.Match, DeckCatalog.RowsFor(PendingRunConfig.Value.DeckId));', '                balances.Match, DeckCatalog.RowsFor(DeckCatalog.BasicDeckId));', '인스톨러가 고른 덱을 무시함', "PlayMode"),
    ('K7', MI, '            var run = new RunFlow(rules.StartChip, catalog.FinalAct);', '            var run = new RunFlow(balances.Match.PlayerStartChip, catalog.FinalAct);', '인스톨러가 규칙을 무시하고 시트 값으로 런을 세움', "PlayMode"),
    ('F1', SR, '                    firstSeat = Seat.Player;', '                    firstSeat = playerCard.Month > opponentCard.Month ? Seat.Player : Seat.Opponent;', '정책이 달 비교를 덮지 않음', 'EditMode'),
    ('F2', RRR, '                        firstSeat = FirstSeatPolicy.PlayerFirst;', '                        firstSeat = FirstSeatPolicy.ByPick;', '리듀서가 선턴 행을 무시함', 'EditMode'),
    ('F3', RRR, '            FirstSeatPolicy firstSeat = FirstSeatPolicy.ByPick;', '            FirstSeatPolicy firstSeat = FirstSeatPolicy.PlayerFirst;', '행 없는 덱도 선턴', 'EditMode'),
    ('F4', MFL, '            SeonResolvedEvent seon = SeonResolver.Resolve(playerPickIndex, seonStream, _eventSink, _firstSeatPolicy);', '            SeonResolvedEvent seon = SeonResolver.Resolve(playerPickIndex, seonStream, _eventSink, FirstSeatPolicy.ByPick);', '판이 정책을 잊음', 'PlayMode'),
    ('F5', MF, '            FirstSeatPolicy firstSeat = _rules.FirstSeat;', '            FirstSeatPolicy firstSeat = FirstSeatPolicy.ByPick;', '공장이 정책을 잊음', 'PlayMode'),
    ('F6', DC, '                    if (row.Amount != 0)', '                    if (row.Amount < 0)', '카탈로그가 양수 실수를 못 거름', 'EditMode'),
    ('F7', RRL, '            if (!Enum.IsDefined(typeof(FirstSeatPolicy), firstSeat))', '            if (firstSeat == (FirstSeatPolicy)255)', '정책 가드가 0을 통과시킴', 'EditMode'),
    ('L1', RV, '            _selectedIndex = 0;\n            RefreshDeckLabels();', '            _selectedIndex = 0;\n            _selectedIndex = 0;', '명부를 담고도 글자를 새로 그리지 않음', 'PlayMode'),
    ('L2', RV, '            StartRequested?.Invoke(_seedInput != null ? _seedInput.text : string.Empty, SelectedDeckId);', '            StartRequested?.Invoke(_seedInput != null ? _seedInput.text : string.Empty, default(ushort));', '시작 신호가 고른 덱 대신 0을 올림', 'PlayMode'),
    ('L3', RV, '            _selectedIndex = index;', '            _selectedIndex = _selectedIndex;', 'SetSelectedDeck이 선택을 바꾸지 않음', 'PlayMode'),
    ('L4', TS, '            PendingRunConfig.Set(new RunConfig(code, deckId));', '            PendingRunConfig.Set(new RunConfig(code, DeckCatalog.BasicDeckId));', '타이틀이 고른 덱을 버리고 기본 덱을 넣음', 'PlayMode'),
    ('L5', TW, '                    return "초짜";', '                    return "선턴";', '초짜 이름표가 선턴', 'EditMode'),
    ('L6', TW, '                case 3:   // DeckCatalog.SeonteonDeckId\n                    return "선턴";', '                case 30:   // DeckCatalog.SeonteonDeckId\n                    return "선턴";', '선턴 이름표가 표에서 빠짐', 'EditMode'),
    ('L7', RSP, '  _deckNextButton: {fileID: 7204858234944133546}', '  _deckNextButton: {fileID: 0}', '프리팹의 다음 화살표 칸이 빔', 'PlayMode'),
    ('L8', TS, '                _runSetup.SetDecks(DeckCatalog.AllDeckIds);', '                _runSetup.SetDecks(System.Array.Empty<ushort>());', '타이틀이 빈 덱 명부를 세움', 'PlayMode'),
    ('L9', RV, '            _selectedIndex = (_selectedIndex + direction + _deckIds.Count) % _deckIds.Count;', '            _selectedIndex = (_selectedIndex + 1 + _deckIds.Count) % _deckIds.Count;', '앞 화살표도 뒤로 넘김', 'PlayMode'),
    ('M1', RV, '                    _deckBackImage.sprite = back;', '                    _deckBackImage.sprite = _deckBackImage.sprite;', 'RefreshDeckDisplay가 뒷면을 바꾸지 않음', 'PlayMode'),
    ('M2', RV, '            return _deckBacks[0].Sprite;', '            return null;', 'BackFor가 표에 없는 id에 null을 돌려줌', 'PlayMode'),
    ('M3', RV, '            return _deckBacks[0].Sprite;', '            return _deckBacks[_deckBacks.Length - 1].Sprite;', 'BackFor가 표에 없는 id에 마지막 칸을 돌려줌', 'PlayMode'),
    ('M4', RV, '                if (_deckBacks[index].DeckId == deckId)', '                if (_deckBacks[index].DeckId == _deckBacks[0].DeckId)', 'BackFor가 id를 무시하고 늘 첫 칸을 돌려줌', 'PlayMode'),
    ('M5', RSP, '  _deckBackImage: {fileID: 8777084365386880808}', '  _deckBackImage: {fileID: 0}', '프리팹의 뒷면 그림 칸이 빔', 'PlayMode'),
    ('M6', RSP, '    _sprite: {fileID: -6875485830153749483, guid: 60e377e4a7d48364e8dd07f5047793b3, type: 3}', '    _sprite: {fileID: -1896382917343656912, guid: 38b5e07e75dbe644aa868363d9dc2537, type: 3}', '굽기가 물주 칸에 단골 그림을 둠', 'PlayMode'),
    ('M7', RSP, '  - _deckId: 1\n    _sprite: {fileID: 6484080048281605771, guid: abfe3e47d1bf06c40a3a1960eefaa1fb, type: 3}', '  - _deckId: 1\n    _sprite: {fileID: -6875485830153749483, guid: 60e377e4a7d48364e8dd07f5047793b3, type: 3}', '굽기가 표의 첫 칸에 물주 그림을 둠', 'PlayMode'),
    ('X1', BLA, '  _cardHeight: 0.98', '  _cardHeight: 1', '자산 카드 높이가 1(102px)', 'EditMode'),
    ('X2', BLA, '  _floorCardScale: 1', '  _floorCardScale: 0.8', '자산 바닥 배율이 0.8', 'EditMode'),
    ('X3', BLA, '  _playAreaHalfWidth: 5.5', '  _playAreaHalfWidth: 6.11', '자산 밴드 반폭이 창보다 넓음', 'EditMode'),
    ('X4', BLC, '        private float _cardAspect = 70f / 98f;', '        private float _cardAspect = 226f / 340f;', 'C# 종횡비 초기값이 데모 아트', 'EditMode'),
    ('N1', CV, '            }\n\n            ApplyFrontSkin();\n        }', '            }\n\n            _skinTiltApplied = false;\n        }', '표시 대입 지점이 스킨을 갱신하지 않음', 'PlayMode'),
    ('N2', CV, '            float scale = _displaySprite.bounds.size.y / skinHeight;', '            float scale = 1f;', '스킨 배율이 1로 고정', 'PlayMode'),
    ('N3', RG, '                card.IsFaceDown ? null : _sprites.FrontBackgroundSprite,\n                card.IsFaceDown ? null : _sprites.FrontBorderSprite);', '                _sprites.FrontBackgroundSprite,\n                _sprites.FrontBorderSprite);', '레지스트리가 뒷면 카드에도 스킨을 넘김', 'PlayMode'),
    ('N4', CV, '                _frontBackgroundRenderer.sortingOrder = order;', '                _frontBackgroundRenderer.sortingOrder = order + 1;', '배경 정렬이 그림보다 하나 위', 'PlayMode'),
    ('DS1', CS, '                if (skins[i].DeckId != deckId)', '                if (skins[i].DeckId != deckId || deckId >= 0)', 'SkinFor가 덱 id를 무시하고 기본만 돌려줌', 'EditMode'),
    ('DS2', CS, '                    entry.Background != null ? entry.Background : fallback.Background,\n                    entry.Border != null ? entry.Border : fallback.Border,\n                    entry.Back != null ? entry.Back : fallback.Back);', '                    entry.Background,\n                    entry.Border,\n                    entry.Back);', '빈 칸의 필드별 대체가 사라짐', 'EditMode'),
    ('DS3', T, '    _border: {fileID: 2547513636019849481, guid: b295108311aa0e64f80c00e6e75e5533, type: 3}', '    _border: {fileID: 3327315892823159581, guid: 0a36e287bf0265145a5e33a854b62a0f, type: 3}', '굽기가 물주 칸에 단골 테두리를 둠', 'EditMode'),
    ('FC1', T, '  - _definitionId: 101\n    _sprite: {fileID: 21300000, guid: da7963b47a75eb94689aac63d7249af5, type: 3}\n  - _definitionId: 102\n    _sprite: {fileID: 21300000, guid: e573322b265166142a04218ce5e5adea, type: 3}\n', '  - _definitionId: 101\n    _sprite: {fileID: 21300000, guid: e573322b265166142a04218ce5e5adea, type: 3}\n  - _definitionId: 102\n    _sprite: {fileID: 21300000, guid: da7963b47a75eb94689aac63d7249af5, type: 3}\n', '자산에서 101·102 앞면이 맞바뀜', 'EditMode'),
    ('FC2', T, '    _sprite: {fileID: 21300000, guid: da7963b47a75eb94689aac63d7249af5, type: 3}', '    _sprite: {fileID: -631506818516679975, guid: 1ce4d65b6ced9e049b853d9fe817e9b1, type: 3}', '101 앞면이 데모 아틀라스로 되돌아감', 'EditMode'),
    ('IN1', CV, '            float scale = sprite.pixelsPerUnit / _displaySprite.pixelsPerUnit;', '            float scale = _displaySprite.bounds.size.y / skinHeight;', '스킨 배율이 옛 높이 맞춤으로 돌아가 배경이 테두리 높이로 늘어남', 'PlayMode'),
    ('IN2', SKT, '        private const int BackgroundInsetPixels = 2;', '        private const int BackgroundInsetPixels = 0;', '배경 인셋 기대가 0이 되어 66×94 배경을 70×98로 요구', 'EditMode'),
    ('CA1', TFE, '                if (cards[index - 1].Value >= cards[index].Value)', '                if (cards[index - 1].Value > cards[index].Value + 1000u)', '폭탄 손패 오름차순 가드가 죽어 내림차순 이벤트가 통과', 'EditMode'),
    ('CA2', DEF, '                        + $"|{e.FloorCard.Value}|{e.TokensAfter}";', '                        + $"|{e.FloorCard.Value}";', '폭탄 지문이 폭탄패 수를 빼먹음', 'EditMode'),
    ('CB1', PBM, '                        MoveToFloorFaceUp(card.CardId, card.CardDefinitionId, card.CardKind);', '                        MoveToFloorFaceUp(card.CardId, card.CardDefinitionId, default(CardKind));', '폭탄 폴드가 종류 echo를 버려 상대 폭탄 3장이 종류 미상으로 선다', 'EditMode'),
    ('CB2', PSC, '                            revealed[cardId] = definitionId;\n', '', '변환기가 폭탄 3장을 공개 맵에 적지 않는다', 'EditMode'),
    ('CC1', BR, '                if (handCounts[month] == DomainEventContract.BombHandCardCount', '                if (handCounts[month] >= 2', '손패 2장으로도 폭탄이 성립', 'EditMode'),
    ('CC2', BR, '                    && floorCounts[month] == BombFloorCardCount)', '                    && floorCounts[month] >= 0)', '바닥에 그 달이 없어도 폭탄이 성립(흔들기 배치)', 'EditMode'),
    ('CC3', SSR, '            if (facts.BombPlay != null)', '            if (facts.BombPlay != null && facts.HandPlay != null)', '폭탄 약탈 감지가 죽음', 'EditMode'),
    ('CC4', RB, '            byte tokens = checked((byte)(_bombTokens[index] + DomainEventContract.BombTokenGrant));', '            byte tokens = checked((byte)(_bombTokens[index] + 1));', '폭탄 1회에 폭탄패를 1장만 줌', 'EditMode'),
    ('CC5', SSR, '                detections.Add(DetectWithSteal(SpecialSituationKind.Bomb, actor, board, claimedSteals));', '                detections.Add(DetectWithSteal(SpecialSituationKind.Bomb, actor, board, new List<CardInstanceId>()));', '폭탄이 고른 약탈 카드를 뒤 이벤트 후보에서 빼지 않음', 'EditMode'),
    ('CE1', TE, '            _board.RecordBomb(_actor);\n', '            _board.RecordBomb(_actor);\n            _board.RecordBomb(_actor);\n', '폭탄 1회가 두 번 기록돼 폭탄패 4장·횟수 2', 'EditMode'),
    ('CE2', TE, 'BombRule.HandCardsOf(hand, bombMonths[index])[0];', 'BombRule.HandCardsOf(hand, bombMonths[index])[1];', '폭탄 행동의 대표 카드가 id 최소가 아님', 'EditMode'),
    ('CE3', TE, '            _board.SpendBombToken(_actor);\n', '', '폭탄패를 쳐도 폭탄패가 줄지 않음', 'EditMode'),
    ('CE4', TE, 'Count == 0 && _board.BombTokens(_actor) == 0;', 'Count == 0;', '폭탄패가 남았는데 빈손으로 보고 묻지 않고 스톱', 'EditMode'),
    ('CE5', FTM, '                case SpecialMomentKind.Bomb:\n                    return "BOMB!";\n', '', '폭탄 외침 단어가 없어 정산 순간 예외', 'EditMode'),
    ('CF1', BBL, '            int bombMultiplier = Require(values, "bomb_multiplier");', '            int bombMultiplier = Require(values, "pi_bak_multiplier");', '로더가 폭탄 배수 자리에 피박 배수 행을 읽음(둘 다 시트값 2)', 'EditMode'),
    ('CF2', SBL, '            BombMultiplier = BalanceGuard.RequirePositive(bombMultiplier, nameof(bombMultiplier));', '            BombMultiplier = bombMultiplier;', '폭탄 배수 양수 가드가 죽음', 'EditMode'),
    ('CF3', SBL, '            bombMultiplier: 2);', '            bombMultiplier: 3);', '시험 고정구의 폭탄 배수가 시트와 어긋남', 'EditMode'),
    ('CG1', LST, '                multiplier = checked(multiplier * balance.BombMultiplier);', '                multiplier = checked(balance.BombMultiplier * (step + 1));', '폭탄 배수가 거듭제곱이 아니라 밑수 × 횟수(1회·2회는 같고 3회부터 갈린다)', 'EditMode'),
    ('CG2', MFL, '                new BombCount(_currentBoard.BombCount(winner)),', '                new BombCount(0),', '정산이 승자의 폭탄 횟수를 넘기지 않음', 'EditMode'),
    ('CG3', MFL, '                new BombCount(_currentBoard.BombCount(winner)),', '                new BombCount(_currentBoard.BombCount(Other(winner))),', '정산이 패자의 폭탄 횟수를 넘김', 'EditMode'),
    ('CG4', MFL, '                    new BombCount(_currentBoard.BombCount(seat)), _settlementBalance));', '                    new BombCount(0), _settlementBalance));', '판 중 표시 배수가 폭탄 항을 빼먹음', 'EditMode'),
    ('CG5', LST, '            int bombMultiplier = BombMultiplierFor(bombCount, settlementBalance);', '            int bombMultiplier = 1;', 'Settle이 폭탄 횟수를 무시함', 'EditMode'),
    ('CG6', MFL, '                    new BombCount(_currentBoard.BombCount(seat)), _settlementBalance));', '                    new BombCount(_currentBoard.BombCount(seat)), SettlementBalance.Placeholder));', '표시 배수가 주입 밸런스 대신 Placeholder 밑수를 읽음', 'EditMode'),
    ('CG7', MFL, '                new BombCount(_currentBoard.BombCount(winner)),', '                new BombCount(_currentBoard.BombCount(Seat.Player)),', '정산이 승자 대신 플레이어 좌석의 폭탄 횟수를 넘김', 'EditMode'),
    ('CG8', MFL, '                    new BombCount(_currentBoard.BombCount(seat)), _settlementBalance));', '                    new BombCount(_currentBoard.BombCount(other)), _settlementBalance));', '표시 배수가 상대 좌석의 폭탄 횟수를 읽음', 'EditMode'),
    ('CG9', MFL, '                _goStopBalance,\n                _settlementBalance);', '                _goStopBalance,\n                SettlementBalance.Placeholder);', '정산이 주입 밸런스 대신 Placeholder 밑수를 읽음', 'EditMode'),
    ('CH1', PSC, '                            settlement.BombMultiplier,', '                            1UL,', '변환기가 폭탄 배수 대신 1을 고정으로 넘김', 'EditMode'),
    ('CH2', RSM, '                BombMultiplier = settled.BombMultiplier;', '                BombMultiplier = 1UL;', '요약이 정산 스텝의 폭탄 배수를 옮기지 않음', 'EditMode'),
    ('CH3', HW, '            line = AppendBak(line, bombMultiplier > 1UL, bomb);', '            line = AppendBak(line, bombMultiplier > 2UL, bomb);', '폭탄 1회(배수 2)가 박 줄에서 빠짐', 'EditMode'),
    ('CH4', RSV, '                    summary.BombMultiplier)', '                    1UL)', '뷰가 박 줄에 폭탄 배수를 넘기지 않음', 'EditMode'),
    ('CI1', HAP, '                if (legalActions[index].Kind == TurnActionKind.PlayBomb)\n                {\n                    return legalActions[index];', '                if (index < 0)\n                {\n                    return legalActions[index];', 'AI가 폭탄을 먼저 반환하지 않음', 'EditMode'),
    ('CI2', HAP, '                if (legalActions[index].Kind == TurnActionKind.PlayBomb)\n                {\n                    return legalActions[index];', '                if (legalActions[index].Kind == TurnActionKind.PlayBomb)\n                {\n                    aiStream.NextInt(0, 2);\n                    return legalActions[index];', 'AI가 폭탄 결정에서 난수를 한 번 뽑음', 'EditMode'),
    ('CI3', HAP, '            if (bestScore <= 0)', '            if (bestScore < 0)', '폭탄패 조건이 0 이하가 아니라 0 미만', 'EditMode'),
    ('CJ1', BSB, '                bombTokens: board != null ? board.BombTokens(Seat.Player) : 0,', '                bombTokens: 0,', '빌더가 플레이어 폭탄패를 싣지 않음', 'EditMode'),
    ('CJ2', PBM, '                    SetBombTokens(token.Seat, token.TokensAfter);', '                    _ = token;', '폴드가 폭탄패 스텝을 무시함', 'EditMode'),
    ('CJ3', PBM, '                bombTokens: _playerBombTokens,', '                bombTokens: _opponentBombTokens,', '보드 모델이 플레이어 자리에 상대 폭탄패를 냄', 'EditMode'),
    ('CJ4', PBM, '                    SetBombTokens(bomb.Seat, bomb.TokensAfter);', '                    _ = bomb;', '폴드가 폭탄 스텝의 폭탄패 지급을 무시함', 'EditMode'),
    ('CJ5', PBM, '            _opponentBombTokens = origin.Opponent.BombTokens;', '            _opponentBombTokens = 0;', '보드 모델이 원본의 상대 폭탄패를 승계하지 않음', 'EditMode'),
    ('CJ6', BSB, '                bombTokens: board != null ? board.BombTokens(Seat.Opponent) : 0,', '                bombTokens: 0,', '빌더가 상대 폭탄패를 싣지 않음', 'EditMode'),
    ('CK1', BV, '                buffer.Add(CardSnapshot.FaceDown(BombTokenCardIds.Of(seat, index)));', '                buffer.Insert(0, CardSnapshot.FaceDown(BombTokenCardIds.Of(seat, index)));', '폭탄패가 손패 앞에 붙음', 'EditMode'),
    ('CK2', BV, '                    snapshot.Opponent.BombTokens, _opponentHandWithTokens));', '                    snapshot.Player.BombTokens, _opponentHandWithTokens));', '상대 손패에 플레이어 폭탄패 수를 씀', 'EditMode'),
    ('CK3', BTI, '        internal const uint PlayerFirst = 1000u;', '        internal const uint PlayerFirst = 0u;', '폭탄패 id가 실재 카드 id와 겹침', 'EditMode'),
    ('CK5', CVR, '                if (BombTokenCardIds.IsToken(card.InstanceId) && _sprites.BombTokenSprite != null)', '                if (_sprites.BombTokenSprite != null)', '전용 스프라이트가 모든 뒷면 카드에 쓰임', 'EditMode'),
    ('CL1', SC, '                if (action.TargetsCard && action.CardInstanceId == cardInstanceId)', '                if (action.CardInstanceId == cardInstanceId)', '커서가 카드 없는 행동을 id 0으로 잡음', 'EditMode'),
    ('CL2', MIC, '                if (legal[index].Kind != PlayerActionKind.PlayBomb)', '                if (legal[index].Kind != PlayerActionKind.PlayBombToken)', '커서 목록이 폭탄 대신 폭탄패를 뺌', 'EditMode'),
    ('CL3', SC, '                if (_actions[index].Kind == kind)', '                if (index == 0)', '종류 이동이 항상 첫 항목으로 감', 'EditMode'),
    ('CL4', MIC, '            if (BombTokenCardIds.IsPlayerToken(cardInstanceId))\n            {\n                if (!_cursor.TryMoveToKind(PlayerActionKind.PlayBombToken))', '            if (BombTokenCardIds.IsToken(cardInstanceId))\n            {\n                if (!_cursor.TryMoveToKind(PlayerActionKind.PlayBombToken))', '상대 폭탄패 클릭도 폭탄패 치기를 제출함', 'EditMode'),
    ('CL5', HRD, '            if (BombTokenCardIds.IsToken(view.InstanceId))', '            if (view == null)', '폭탄패 뷰가 재정렬 끌기에 잡힘', 'EditMode'),
    ('CK4', CVR, '                if (!_visited.Contains(entry.Key))', '                if (!_visited.Contains(entry.Key) && entry.Key < 1000u)', '레지스트리가 폭탄패 뷰를 회수하지 않음', 'PlayMode'),
    ('CM1', LST, '            BaseLoot = checked((long)chipSum * LootMultiplier);', '            BaseLoot = chipSum * LootMultiplier;', '기본 약탈을 int로 곱한 뒤 long에 담음', 'EditMode'),
    ('CM2', LST, '            TransferAmount = (int)Math.Min((long)loserChipsBefore, floored);', '            TransferAmount = Math.Min(loserChipsBefore, unchecked((int)floored));', '이전액을 int로 먼저 자른 뒤 상한을 검', 'EditMode'),
    ('CM3', LST, '            return checked(\n                adjustedScore * bakMultiplier', '            return unchecked(\n                adjustedScore * bakMultiplier', '약탈 배수 곱의 넘침 검사를 지움', 'EditMode'),
    ('CM4', GSS, '                multiplier = checked(multiplier * balance.GoMultiplierBase);', '                multiplier = unchecked(multiplier * balance.GoMultiplierBase);', '고배수 거듭제곱의 넘침 검사를 지움', 'EditMode'),
    ('CM5', LST, '            PreMultiplierLoot = checked((long)chipSum * adjustedScore);', '            PreMultiplierLoot = chipSum * adjustedScore;', '칩 × 점수를 int로 곱한 뒤 long에 담음', 'EditMode'),
    ('CN1', SPL, '                case BombPlayedStep:\n                    return _budget.SeatDefaultSecondsFor(step.Seat)\n                        + _budget.MatchHoldSecondsFor(step.Seat);', '                case BombPlayedStep:\n                    return _budget.SeatDefaultSecondsFor(step.Seat);', '폭탄 박자에서 획득 쉼이 빠짐', 'EditMode'),
    ('CN2', TBD, '                        moves.Add(cardView.MoveWithProfileAsync(', '                        await (cardView.MoveWithProfileAsync(', '감독이 폭탄 3장을 차례로 보냄', 'PlayMode'),
    ('CN3', TBD, '                case BombPlayedStep bomb:\n                    return PlayBombAsync(bomb, token);', '                case BombPlayedStep bomb:\n                    return UniTask.CompletedTask;', '감독이 폭탄 스텝을 연출하지 않음', 'PlayMode'),
    ('CP1', MIC, '                if (MonthOf(hand, bombs[index].CardInstanceId) == month)', '                if (bombs[index].CardInstanceId == cardInstanceId)', '폭탄을 달이 아니라 대표 카드 id로 찾음', 'EditMode'),
    ('CP2', MIC, '                && current.Kind == PlayerActionKind.PlayHandCard\n                && _gate.IsOpen', '                && current.Kind == PlayerActionKind.PlayHandCard', '가로채기가 닫힌 게이트에서도 물음', 'EditMode'),
    ('CP3', MIC, '            if (_drag != null && _drag.ConsumeClickSuppression())\n            {\n                return;\n            }\n\n            if (IsPromptOpen)', '            if (_drag != null && _drag.ConsumeClickSuppression())\n            {\n                return;\n            }\n\n            if (false)', '프롬프트가 떠 있어도 클릭을 받음', 'EditMode'),
    ('CQ1', BPV, '            Submit(_bombAction);', '            Submit(_playAction);', '폭탄 버튼이 치기를 제출함', 'EditMode'),
    ('CQ2', BPV, '            if (_router != null && _hasActions)', '            if (_router != null)', 'Ask 없이 열린 창의 버튼이 기본값 행동을 제출함', 'EditMode'),
    ('CQ3', BPV, '            if (!isMyHandPlay || _gate == null || !_gate.IsOpen)', '            if (!isMyHandPlay || _gate == null)', '프롬프트가 닫힌 게이트를 보지 않음', 'EditMode'),
    ('CQ4', BPV, '                status.RoundStage == RoundStage.AwaitingHandPlay && status.ActorSeat == SeatSide.Player;', '                status.RoundStage == RoundStage.AwaitingHandPlay;', '프롬프트가 행위자 좌석을 보지 않음', 'EditMode'),
    ('CQ5', BPV, '            _hasActions = false;', '            _hasActions = _hasActions;', '닫을 때 받아 둔 행동을 버리지 않음', 'EditMode'),
    ('CR1', MSR, '                        if (bomb.Actor == Seat.Player)', '                        if (bomb.Actor != Seat.Player)', '폭탄을 반대 좌석에 셈', 'EditMode'),
    ('CR2', MSR, '                        if (token.Actor == Seat.Player)', '                        if (token.Actor != Seat.Player)', '폭탄패를 반대 좌석에 셈', 'EditMode'),
    ('CR3', MSR, '                            settlement.BombMultiplier));', '                            1UL));', '정산 배수를 1로 고정해 기록', 'EditMode'),
    ('CR4', MSR, '                            _playerBombTokens++;', '                            _playerBombs++;', '플레이어석 폭탄패를 폭탄으로 셈', 'EditMode'),
    ('CR5', STL, 'AppendSigned(builder, "playerBombTokenCount", record.Bombs.PlayerTokens);', 'AppendSigned(builder, "playerBombTokenCount", record.Bombs.OpponentTokens);', 'JSONL 키에 다른 좌석 값을 실음', 'EditMode'),
    ('CR6', SAG, '                        if (transfers[index].BombMultiplier > 1UL)', '                        if (transfers[index].BombMultiplier >= 1UL)', '배수 1 정산도 폭탄 정산으로 셈', 'EditMode'),
    ('CR7', MSR, 'observer.OpponentGoCount, observer.Bombs,\n                    exception);', 'observer.OpponentGoCount, default(SimBombTally),\n                    exception);', '실패 레코드가 폭탄 계수를 버림', 'EditMode'),
    ('CR8', SAG, '                    faultCount++;\n                    continue;', '                    faultCount++;', '실패 레코드를 집계에 섞음', 'EditMode'),
    ('CR9', SAG, '                roundSum += record.RoundsPlayed;', '                roundSum += record.RoundTransfers.Count;', '판 수 합에 정산 수를 넣음', 'EditMode'),
    ('CS1', BDM, '                if (!round.IsAccepted || round.Seon.FirstSeat != SeatSide.Player)', '                if (!round.IsAccepted || round.Seon.FirstSeat == SeatSide.Player)', '상대가 선인 궤적에서 잼', 'PlayMode'),
    ('CS2', BDM, '                return ContainsBomb(session.LegalActions());', '                return true;', '폭탄 여부를 보지 않고 첫 코드를 냄', 'PlayMode'),
    # ── 벽 W0: 4판 이후 bet_min ──
    ('W0', 'Assets/Scripts/Domain/Scoring/LootSettler.cs', '                    if (roundNumber < 1)\n', '                    if (roundNumber < 1 || roundNumber > 3)\n', '4판 이후 bet_min을 다시 던지게 함', 'EditMode'),
    # ── 벽 W1a: 밑천 내기 밸런스 키 ──
    ('W1a1', 'Assets/Scripts/Infrastructure/GameData/BgBalanceLoader.cs', 'stakeRuleEnabled: stakeRule == 1,', 'stakeRuleEnabled: stakeRule == 0,', '스위치를 거꾸로 읽음', 'EditMode'),
    ('W1a2', 'Assets/Scripts/Infrastructure/GameData/BgBalanceLoader.cs', 'if (stakeRule != 0 && stakeRule != 1)', 'if (stakeRule < 0 && stakeRule > 1)', '0/1 가드를 없앰', 'EditMode'),
    ('W1a3', 'Assets/Scripts/Domain/Balance/MatchBalance.cs', 'StakeCapBp = BalanceGuard.RequirePositive(stakeCapBp, nameof(stakeCapBp));', 'StakeCapBp = stakeCapBp;', '한도 배수 하한 가드를 없앰', 'EditMode'),
    ('W1a4', 'Assets/Scripts/Infrastructure/GameData/BgBalanceLoader.cs', 'int stakeCapBp = Require(values, "stake_cap_bp");', 'int stakeCapBp = Require(values, "draw_carry_multiplier");', '한도 배수가 다른 키를 읽음', 'EditMode'),
    # ── 벽 W1b: 밑천 내기 정산과 종료 ──
    ('W1b1', 'Assets/Scripts/Domain/Scoring/LootSettler.cs', 'int stakeCap = Math.Min(winnerCap, loserRemainingStake);', 'int stakeCap = loserRemainingStake;', '이긴 쪽 한도를 없앰', 'EditMode'),
    ('W1b2', 'Assets/Scripts/Domain/Match/MatchFlow.cs', 'StakeOf(loser) - StakeLostOf(loser));', 'ChipsOf(loser));', '남은 밑천을 진 쪽 칩으로 바꿈', 'EditMode'),
    ('W1b3', 'Assets/Scripts/Domain/Match/MatchFlow.cs', 'return lost >= StakeOf(loser) ? ChipsOf(loser) : transferAmount;', 'return transferAmount;', '밑천이 바닥나도 전부 이전하지 않음', 'EditMode'),
    ('W1b4', 'Assets/Scripts/Domain/Match/MatchFlow.cs', '            if (!_matchBalance.StakeRuleEnabled)\n            {\n                return StakeLimit.None;', '            if (!_matchBalance.StakeRuleEnabled && _matchBalance.StakeCapBp < 0)\n            {\n                return StakeLimit.None;', '한도가 스위치를 무시함', 'EditMode'),
    ('W1b5', 'Assets/Scripts/Domain/Match/MatchFlow.cs', '            if (!_matchBalance.StakeRuleEnabled)\n            {\n                return transferAmount;', '            if (!_matchBalance.StakeRuleEnabled && _matchBalance.StakeCapBp < 0)\n            {\n                return transferAmount;', '누계가 스위치를 무시함', 'EditMode'),
    ('W1b6', 'Assets/Scripts/Domain/Match/MatchFlow.cs', '            int transferAmount = FireSettlementEffects(winner, loser, bak, settlement.TransferAmount);\n            transferAmount = ChargeStakeLoss(loser, transferAmount);\n', '            int transferAmount = FireSettlementEffects(winner, loser, bak, ChargeStakeLoss(loser, settlement.TransferAmount));\n', '효과 앞의 이전액으로 누계를 올림', 'EditMode'),
    ('W1b7', 'Assets/Scripts/Domain/Match/MatchFlow.cs', 'int lost = checked(StakeLostOf(loser) + transferAmount);', 'int lost = checked(StakeOf(loser) - ChipsOf(loser) + transferAmount);', '이긴 판이 누계를 줄임(순손실)', 'EditMode'),
    ('W1b8', 'Assets/Scripts/Domain/Match/MatchFlow.cs', '(long)StakeOf(winner) * _matchBalance.StakeCapBp', '(long)StakeOf(loser) * _matchBalance.StakeCapBp', '이긴 쪽 한도를 진 쪽 밑천으로 셈', 'EditMode'),
    ('W1b9', 'Assets/Scripts/Domain/Scoring/LootSettler.cs', 'CappedByStake = floored > stakeCap;', 'CappedByStake = floored >= stakeCap;', '한도 경계 판정을 비틂', 'EditMode'),
    # ── 벽 W1d: 밑천 내기 런의 개평꾼 매대 제외 ──
    ('W1d1', 'Assets/Scripts/Domain/Run/BonusPackDraw.cs', 'if (stakeRuleEnabled && candidate.Id == EffectCatalog.GaepyeongkkunId)', 'if (stakeRuleEnabled && candidate.Id == ushort.MaxValue)', '제외 대상을 엉뚱한 id로 바꿈', 'EditMode'),
    ('W1d2', 'Assets/Scripts/Domain/Run/BonusPackDraw.cs', 'if (stakeRuleEnabled && candidate.Id == EffectCatalog.GaepyeongkkunId)', 'if (!stakeRuleEnabled && candidate.Id == EffectCatalog.GaepyeongkkunId)', '스위치를 거꾸로 읽음', 'EditMode'),
    ('W1d3', 'Assets/Scripts/Application/ShopSession.cs', 'BonusPackDraw.Draw(_bonusCards, _run.StakeRuleEnabled, _bonusDrawStream)', 'BonusPackDraw.Draw(_bonusCards, false, _bonusDrawStream)', '상점이 런의 스위치를 무시함', 'EditMode'),
    ('W1d4', 'Assets/Scripts/Boot/MatchSessionFactory.cs', '_opponentCatalog.FinalAct, _balances.Match.StakeRuleEnabled)', '_opponentCatalog.FinalAct, false)', '재시작 런이 스위치를 잃음', 'EditMode'),
    ('W1d4p', 'Assets/Scripts/Boot/MatchSessionFactory.cs', '_opponentCatalog.FinalAct, _balances.Match.StakeRuleEnabled)', '_opponentCatalog.FinalAct, false)', '재시작 런이 스위치를 잃음', 'PlayMode'),
    ('W1d5', 'Assets/Scripts/Domain/Run/RunFlow.cs', 'StakeRuleEnabled = stakeRuleEnabled;', 'StakeRuleEnabled = false;', '런이 스위치를 버림', 'EditMode'),
    ('W1d6', 'Assets/Scripts/Boot/MatchSceneInstaller.cs', 'catalog.FinalAct, balances.Match.StakeRuleEnabled)', 'catalog.FinalAct, false)', '씬 설치자가 스위치를 잃음', 'PlayMode'),
    # ── 벽 W1e: 최대 밑천과 골드 분리 ──
    ('W1e1', 'Assets/Scripts/Domain/Run/RunFlow.cs', 'gold = checked(Gold + gained);', 'gold = Gold;', '이겨도 골드가 들어오지 않음', 'EditMode'),
    ('W1e2', 'Assets/Scripts/Domain/Run/RunFlow.cs', 'public int Purse => StakeRuleEnabled ? Gold : Chips;', 'public int Purse => Chips;', '상점 돈이 칩을 봄', 'EditMode'),
    ('W1e3', 'Assets/Scripts/Domain/Run/RunFlow.cs', 'Gold -= amount;', 'Chips -= amount;', '골드 대신 칩을 씀', 'EditMode'),
    ('W1e4', 'Assets/Scripts/Domain/Run/RunFlow.cs', '? Gold - amount >= 0', '? Gold - amount >= 1', '골드 하한을 1로 비틂', 'EditMode'),
    ('W1e5', 'Assets/Scripts/Domain/Run/RunFlow.cs', 'Gold = stakeRuleEnabled ? startingGold : 0;', 'Gold = startingGold;', '꺼진 런도 시작 골드를 쥠', 'EditMode'),
    ('W1e6', 'Assets/Scripts/Domain/Run/RunFlow.cs', 'if (gained < 0)', 'if (gained < -1000000000)', '보존 위반 가드를 없앰', 'EditMode'),
    ('W1e7', 'Assets/Scripts/Infrastructure/GameData/BgBalanceLoader.cs', 'Require(values, "player_start_gold")', 'Require(values, "stake_rule")', '시작 골드가 다른 키를 읽음', 'EditMode'),
    ('W1e8', 'Assets/Scripts/Application/ShopSession.cs', '_run.CanSpend(PackPrice)', '_run.Chips > PackPrice', '각서 구매 판정이 칩을 봄', 'EditMode'),
    ('W1e9', 'Assets/Scripts/Domain/Balance/ShopBalance.cs', 'BalanceGuard.RequireNonNegative(startGold, nameof(startGold))', 'startGold', '시작 골드 음수 가드를 없앰', 'EditMode'),
    # ── 벽 2단계 C1: 밑천 장부와 정산 기록 ──
    ('C1a', 'Assets/Scripts/Domain/Match/MatchFlow.cs', 'int forfeitedWinnings = transferAmount - transferBeforeStakeCharge;', 'int forfeitedWinnings = 0;', '넘어간 딴 돈을 0으로', 'EditMode'),
    ('C1b', 'Assets/Scripts/Domain/Match/MatchFlow.cs', 'int forfeitedWinnings = transferAmount - transferBeforeStakeCharge;', 'int forfeitedWinnings = transferAmount;', '넘어간 딴 돈을 이전액 전체로', 'EditMode'),
    ('C1c', 'Assets/Scripts/Domain/Match/MatchFlow.cs', 'int stakeCut = settlement.TransferBeforeStakeCap - settlement.TransferAmount;', 'int stakeCut = 0;', '잘린 양을 0으로', 'EditMode'),
    ('C1d', 'Assets/Scripts/Domain/Match/MatchFlow.cs', '_playerStakeLost : _opponentStakeLost', '_playerStake : _opponentStake', '누계 대신 밑천을 돌려줌', 'EditMode'),
    ('C1e', 'Assets/Scripts/Domain/Replay/DomainEventFingerprint.cs', '|{e.StakeCut}|{e.ForfeitedWinnings}', '|{e.StakeCut}|', '지문이 넘어간 딴 돈을 뺌', 'EditMode'),
    ('C1f', 'Assets/Scripts/Domain/Match/MatchFlow.cs', 'if (ChipsOf(loser) - transferAmount == 0)', 'if (ChipsOf(loser) - transferAmount == int.MinValue)', '디버그 종료 누계 채우기를 없앰', 'EditMode'),
    ('C1g', 'Assets/Scripts/Domain/Scoring/LootSettler.cs', 'TransferBeforeStakeCap = (int)Math.Min((long)loserChipsBefore, floored);', 'TransferBeforeStakeCap = (int)Math.Min((long)int.MaxValue, floored);', '한도 전 이전액이 진 쪽 칩을 무시', 'EditMode'),
    ('C1h', 'Assets/Scripts/Domain/Events/RoundFlowEvents.cs', 'if (forfeitedWinnings > actualTransfer)', 'if (forfeitedWinnings > actualTransfer + (ulong.MaxValue / 2))', '넘어간 딴 돈 가드를 없앰', 'EditMode'),
    # ── 벽 2단계 C2: 정산 스텝과 요약 ──
    ('C2a', 'Assets/Scripts/Application/PresentationStepConverter.cs', '                            settlement.StakeCut,\n                            settlement.ForfeitedWinnings));', '                            settlement.ForfeitedWinnings,\n                            settlement.StakeCut));', '변환기가 두 칸을 맞바꿈', 'EditMode'),
    ('C2b', 'Assets/Scripts/Presentation/Hud/RoundSummary.cs', 'StakeCut = settled.StakeCut;', 'StakeCut = 0;', '요약이 잘린 양을 복사하지 않음', 'EditMode'),
    ('C2c', 'Assets/Scripts/Presentation/Hud/RoundSummary.cs', 'ForfeitedWinnings = settled.ForfeitedWinnings;', 'ForfeitedWinnings = 0;', '요약이 넘어간 딴 돈을 복사하지 않음', 'EditMode'),
    ('C2d', 'Assets/Scripts/Application/PresentationStep.cs', 'StakeCut = stakeCut;', 'StakeCut = forfeitedWinnings;', '스텝이 잘린 양 칸에 엉뚱한 값을 담음', 'EditMode'),
    ('C2e', 'Assets/Scripts/Application/PresentationStep.cs', 'if (forfeitedWinnings > actualTransfer)', 'if (forfeitedWinnings > actualTransfer + (ulong.MaxValue / 2))', '스텝 가드를 없앰', 'EditMode'),
    # ── 벽 2단계 C3: 좌석 밑천 축 ──
    ('C3a', 'Assets/Scripts/Application/BoardSnapshotBuilder.cs', 'StakeOf(flow, Seat.Player),', 'StakeOf(flow, Seat.Opponent),', '빌더가 좌석을 맞바꿈', 'EditMode'),
    ('C3b', 'Assets/Scripts/Presentation/Playback/PresentationBoardModel.cs', '_origin.Player.Chips, _origin.Player.Stake,', '_origin.Player.Chips, default(SeatStake),', '폴드가 밑천을 버림', 'EditMode'),
    ('C3c', 'Assets/Scripts/Application/BoardSnapshot.cs', 'Chips - Stake.Remaining', 'Chips - Stake.Stake', '딴 돈을 밑천 기준으로 셈', 'EditMode'),
    ('C3d', 'Assets/Scripts/Application/BoardSnapshotBuilder.cs', 'return flow.StakeRuleEnabled\n', 'return true\n', '빌더가 스위치를 무시함', 'EditMode'),
    ('C3e', 'Assets/Scripts/Application/BoardSnapshot.cs', 'if (stake.IsActive && chips < stake.Remaining)', 'if (stake.IsActive && chips < stake.Remaining - 1000000)', '스냅숏 항등식 가드를 없앰', 'EditMode'),
    ('C3f', 'Assets/Scripts/Application/SeatStake.cs', 'if (lost < 0 || lost > stake)', 'if (lost < 0)', '누계 상한 가드를 없앰', 'EditMode'),
    # ── 벽 2단계 C4: 골드 경로 ──
    ('C4a', 'Assets/Scripts/Boot/MatchSessionFactory.cs', 'new GoldLine(_run.Gold, _run.Gold - goldBefore)', 'new GoldLine(_run.Gold, _run.Gold)', '늘어난 골드 대신 잔액을 담음', 'PlayMode'),
    ('C4c', 'Assets/Scripts/Presentation/Hud/ShopView.cs', '_chipsChanged?.Invoke(session.RunChips);', '_chipsChanged?.Invoke(session.Purse);', '상점이 계기판에 골드를 보고', 'EditMode'),
    ('C4d', 'Assets/Scripts/Boot/MatchSessionFactory.cs', '_run.StakeRuleEnabled ? new GoldLine(_run.Gold, 0) : default', 'new GoldLine(_run.Gold, 0)', '꺼진 런도 골드 줄을 보임', 'PlayMode'),
    ('C4e', 'Assets/Scripts/Application/ShopSession.cs', 'public int RunChips => _run.Chips;', 'public int RunChips => _run.Purse;', '런 칩 대신 상점 돈', 'EditMode'),
    ('C4f', 'Assets/Scripts/Application/GoldLine.cs', 'IsShown = true;', 'IsShown = false;', '골드 줄이 늘 숨음', 'EditMode'),
    ('C4g', 'Assets/Scripts/Application/GoldLine.cs', 'if (gained < 0 || gained > balance)', 'if (gained < 0)', '늘어난 골드 상한 가드를 없앰', 'EditMode'),
    # ── 벽 2단계 C5: 스위치 단일 출처 ──
    ('C5a', 'Assets/Scripts/Boot/MatchSessionFactory.cs', 'rules.StartChip, opponentCatalog.FinalAct, balances.Match.StakeRuleEnabled, balances.Shop.StartGold', 'rules.StartChip, opponentCatalog.FinalAct, false, balances.Shop.StartGold', '새 런 생성이 스위치를 거짓으로 고정', 'PlayMode'),
    ('C5b', 'Assets/Scripts/Boot/MatchSessionFactory.cs', 'rules.StartChip, opponentCatalog.FinalAct, balances.Match.StakeRuleEnabled, balances.Shop.StartGold', 'rules.StartChip, opponentCatalog.FinalAct, true, balances.Shop.StartGold', '새 런 생성이 스위치를 참으로 고정', 'PlayMode'),
    ('C5c', 'Assets/Scripts/Boot/MatchSessionFactory.cs', 'bool stakeRuleEnabled = _run.StakeRuleEnabled;', 'bool stakeRuleEnabled = _balances.Match.StakeRuleEnabled;', '매치가 시트 스위치를 읽음', 'PlayMode'),
    ('C5d', 'Assets/Scripts/Boot/MatchSessionFactory.cs', '_opponentCatalog.FinalAct, _stakeRuleEnabled, _balances.Shop.StartGold', '_opponentCatalog.FinalAct, _balances.Match.StakeRuleEnabled, _balances.Shop.StartGold', '재시작 런이 시트 스위치를 읽음', 'PlayMode'),
    ('C5e', 'Assets/Scripts/Boot/MatchSessionFactory.cs', 'bool stakeRuleEnabled = _run.StakeRuleEnabled;', 'bool stakeRuleEnabled = !_run.StakeRuleEnabled;', '매치가 스위치를 거꾸로 읽음', 'PlayMode'),
    # ── 벽 2단계 C6: 계기판 밑천 막대 ──
    ('C6a', 'Assets/Scripts/Presentation/Hud/MatchView.cs', 'SetRatio(stake > 0 ? remaining / (float)stake : 0f)', 'SetRatio(stake > 0 ? (stake - remaining) / (float)stake : 0f)', '막대가 잃은 비율을 그림', 'EditMode'),
    ('C6b', 'Assets/Scripts/Presentation/Hud/MatchView.cs', 'HudWords.FormatStakeRemaining(remaining, stake)', 'HudWords.FormatStakeRemaining(stake, remaining)', '분자·분모 맞바꿈', 'EditMode'),
    ('C6c', 'Assets/Scripts/Presentation/Hud/MatchView.cs', 'if (seat.Stake.IsActive)', 'if (seat.Stake.IsActive || seat.Chips >= 0)', '꺼진 런에도 막대를 켬', 'EditMode'),
    ('C6d', 'Assets/Scripts/Presentation/Hud/MatchView.cs', '_stakeRule\n                    ? HudWords.FormatRoundOrdinal(displayRound)', '!_stakeRule\n                    ? HudWords.FormatRoundOrdinal(displayRound)', '라운드 칸 표기를 뒤집음', 'EditMode'),
    ('C6e', 'Assets/Scripts/Presentation/Hud/MatchView.cs', '_selfPanel.RenderChips(chips, _stakeRule);', '_selfPanel.RenderChips(chips, false);', '상점 미리보기가 규칙을 무시', 'EditMode'),
    ('C6f', 'Assets/Scripts/Presentation/Hud/MatchView.cs', 'RenderStake(seat.Stake.Remaining, seat.Stake.Stake, seat.Winnings);', 'RenderStake(seat.Stake.Remaining, seat.Stake.Stake, seat.Chips);', '딴 돈 자리에 칩 전체', 'EditMode'),
    # ── 벽 2단계 C7: 상점 골드 칸 ──
    ('C7a', 'Assets/Scripts/Presentation/Hud/ShopView.cs', 'bool shown = session != null && session.StakeRuleEnabled;', 'bool shown = session != null;', '꺼진 런에도 골드 칸', 'EditMode'),
    ('C7b', 'Assets/Scripts/Presentation/Hud/ShopView.cs', 'HudWords.FormatGold(session.Purse)', 'HudWords.FormatGold(session.RunChips)', '골드 칸에 런 칩', 'EditMode'),
    ('C7c', 'Assets/Scripts/Presentation/Hud/ShopView.cs', '            RenderBonusShelf();\n            RenderGold(session);\n', '            RenderBonusShelf();\n', '골드 칸을 그리지 않음', 'EditMode'),
    ('C7d', 'Assets/Scripts/Presentation/Hud/HudWords.cs', 'return gold.ToString("N0", CultureInfo.InvariantCulture);', 'return gold.ToString(CultureInfo.InvariantCulture);', '천 단위 구분 빠짐', 'EditMode'),
    ('C7e', 'Assets/Scripts/Presentation/Hud/ShopView.cs', '_goldPanel.SetActive(shown);', 'if (shown) _goldPanel.SetActive(true);', '끄는 쪽을 잊음', 'EditMode'),
    # ── 벽 2단계 C8: 정산 창 ──
    ('C8a', 'Assets/Scripts/Presentation/Hud/RoundSummaryView.cs', 'MatchView.SetText(_myChips, StakeBalanceText(stakes.Player));', 'MatchView.SetText(_myChips, StakeBalanceText(stakes.Opponent));', '잔액 칸 좌석 맞바꿈', 'EditMode'),
    ('C8b', 'Assets/Scripts/Presentation/Hud/RoundSummaryView.cs', '_winningsRow.SetActive(stakes.IsActive);', '_winningsRow.SetActive(true);', '꺼진 런에도 딴 돈 줄', 'EditMode'),
    ('C8c', 'Assets/Scripts/Presentation/Hud/RoundSummaryView.cs', 'HudWords.FormatStakeCutNote(playerWon, summary.StakeCut)', 'HudWords.FormatStakeCutNote(!playerWon, summary.StakeCut)', '한도 줄 시점 뒤집힘', 'EditMode'),
    ('C8d', 'Assets/Scripts/Presentation/Hud/RoundSummaryView.cs', 'return forfeit == null ? cut : cut + "\\n" + forfeit;', 'return cut;', '소진 줄을 잃음', 'EditMode'),
    ('C8e', 'Assets/Scripts/Presentation/Hud/RoundSummaryView.cs', '_goldPanel.SetActive(stakes.Gold.IsShown);', '_goldPanel.SetActive(stakes.IsActive);', '골드 줄을 매치 중간에도 켬', 'EditMode'),
    ('C8f', 'Assets/Scripts/Presentation/Hud/HudWords.cs', '? text + " (+" + gained.ToString("N0", CultureInfo.InvariantCulture) + ")"', '? text', '들어온 골드 빠짐', 'EditMode'),
    ('C8g', 'Assets/Scripts/Presentation/Hud/RoundSummaryStakes.cs', 'if (player.Stake.IsActive != opponent.Stake.IsActive)', 'if (false)', '좌석 규칙 가드 제거', 'EditMode'),
    ('C8h', 'Assets/Scripts/Presentation/Hud/RoundSummaryView.cs', '_stakeLift = StakeRowsLift();', '_stakeLift = 0f;', '패널을 들어 올리지 않음', 'EditMode'),
    ('C8i', 'Assets/Scripts/Presentation/Hud/RoundSummaryView.cs', 'rect.height + spacing : 0f;', 'rect.height : 0f;', '간격을 빼먹음', 'EditMode'),
    ('C8j', 'Assets/Scripts/Presentation/Hud/RoundSummaryView.cs', '+ RestingTarget().y;', '+ _slideRestingPosition.y;', '시작 지점이 올린 자리를 모름', 'EditMode'),
    ('C8k', 'Assets/Scripts/Presentation/Hud/RoundSummaryView.cs', 'return row != null && row.activeSelf ?', 'return row != null ?', '꺼진 줄도 셈', 'EditMode'),
    # ── 벽 2단계 C7b: 골드 아이콘 돈주머니 ──
    ('C7f', 'Assets/Scripts/Presentation/Hud/ShopView.cs', 'return session != null && session.StakeRuleEnabled ? _goldPriceSprite : _chipPriceSprite;', 'return session != null ? _goldPriceSprite : _chipPriceSprite;', '꺼진 런에도 돈주머니', 'EditMode'),
    ('C7g', 'Assets/Scripts/Presentation/Hud/ShopView.cs', '            RenderGold(session);\n            RenderPriceIcons(session);\n', '            RenderGold(session);\n', '팩 값 아이콘을 바꾸지 않음', 'EditMode'),
    ('C7h', 'Assets/Scripts/Presentation/Hud/ShopView.cs', 'card.SetPriceIcon(PriceSpriteFor(session));', 'card.SetPriceIcon(_chipPriceSprite);', '보너스 카드 아이콘은 늘 칩', 'EditMode'),
    ('C7i', 'Assets/Scripts/Presentation/Hud/ShopView.cs', '                _chipPackPriceIcon.sprite = sprite;', '                _chipPackPriceIcon.sprite = _chipPriceSprite;', '작업패 팩 아이콘만 칩', 'EditMode'),
    ('C7j', 'Assets/Scripts/Presentation/Hud/ShopBonusOfferCard.cs', 'if (_priceIcon != null && icon != null)', 'if (_priceIcon != null)', '빈 그림으로 덮음', 'EditMode'),
    # ── 벽 2단계 C9: 패배 화면 ──
    ('C9a', 'Assets/Scripts/Presentation/Hud/GameOverView.cs', 'if (summary.Stake <= 0 || summary.Cause != GameOverCause.AllIn)', 'if (summary.Stake <= 0)', '라운드 상한 패배에도 밑천 줄', 'EditMode'),
    ('C9b', 'Assets/Scripts/Presentation/Hud/GameOverView.cs', 'if (summary.Stake <= 0 || summary.Cause != GameOverCause.AllIn)', 'if (summary.Cause != GameOverCause.AllIn)', '꺼진 런에도 밑천 줄', 'EditMode'),
    ('C9c', 'Assets/Scripts/Presentation/Hud/GameOverView.cs', 'return summary.ForfeitedWinnings > 0', 'return summary.ForfeitedWinnings >= 0', '넘어간 딴 돈 0도 적음', 'EditMode'),
    ('C9d', 'Assets/Scripts/Presentation/Hud/HudWords.cs', 'return "밑천 " + stake.ToString("N0", CultureInfo.InvariantCulture) + " 모두 잃음";', 'return "밑천 " + stake.ToString(CultureInfo.InvariantCulture) + " 모두 잃음";', '밑천 줄 천 단위 구분 빠짐', 'EditMode'),
    ('C9e', 'Assets/Scripts/Presentation/Hud/GameOverSummary.cs', 'ForfeitedWinnings = forfeitedWinnings;', 'ForfeitedWinnings = 0;', '요약이 넘어간 딴 돈을 버림', 'EditMode'),
    # ── 벽 2단계 C10: 스위치 켜기 ──
    ('C10a', 'Assets/Scripts/Infrastructure/GameData/BgBalanceLoader.cs', 'stakeRuleEnabled: stakeRule == 1,', 'stakeRuleEnabled: stakeRule == 0,', '스위치를 거꾸로 읽음', 'EditMode'),
    ('C10b', 'Assets/Scripts/Infrastructure/GameData/BgBalanceLoader.cs', 'stakeRuleEnabled: stakeRule == 1,', 'stakeRuleEnabled: stakeRule == 0,', '스위치를 거꾸로 읽음(출하 시트 시험)', 'PlayMode'),
    ('C10c', 'Assets/Scripts/Infrastructure/GameData/BgBalanceLoader.cs', 'int roundLimit = Require(values, "round_limit");', 'int roundLimit = Require(values, "bet_min_round_3");', '판 상한을 다른 키에서 읽음', 'EditMode'),
    # ── 밑천 올리기 D1: 상점 밸런스 축 ──
    ('D1a', 'Assets/Scripts/Infrastructure/GameData/BgBalanceLoader.cs', 'stakeUpgradePrice: stakeUpgradePrice,', 'stakeUpgradePrice: stakeUpgradeAmount,', '값 슬롯에 양 슬롯을 꽂음', 'EditMode'),
    ('D1b', 'Assets/Scripts/Infrastructure/GameData/BgBalanceLoader.cs', 'int stakeUpgradeAmount = Require(values, "stake_upgrade_amount");', 'int stakeUpgradeAmount = Require(values, "stake_upgrade_price");', '양을 값 키에서 읽음', 'EditMode'),
    ('D1c', 'Assets/Scripts/Domain/Balance/ShopBalance.cs', 'StakeUpgradePrice = BalanceGuard.RequirePositive(', 'StakeUpgradePrice = BalanceGuard.RequireNonNegative(', '값 0을 허용', 'EditMode'),
    ('D1d', 'Assets/Scripts/Domain/Balance/ShopBalance.cs', 'StakeUpgradeAmount = BalanceGuard.RequirePositive(', 'StakeUpgradeAmount = BalanceGuard.RequireNonNegative(', '양 0을 허용', 'EditMode'),
    ('D1e', 'Assets/Scripts/Domain/Balance/ShopBalance.cs', 'stakeUpgradePrice: 400, stakeUpgradeAmount: 300);', 'stakeUpgradePrice: 401, stakeUpgradeAmount: 300);', 'Placeholder 값이 시트와 갈라짐', 'EditMode'),
    # ── 밑천 올리기 D2: 상점 SKU ──
    ('D2a', 'Assets/Scripts/Boot/MatchSessionFactory.cs', 'stakeUpgradePrice: _balances.Shop.StakeUpgradePrice,', 'stakeUpgradePrice: _balances.Shop.StakeUpgradeAmount,', '공장이 값 자리에 양을 꽂음', 'PlayMode'),
    ('D2b', 'Assets/Scripts/Application/ShopSession.cs', 'if (!_run.StakeRuleEnabled)', 'if (false)', '꺼진 런 구매를 지출 전에 막지 않음', 'EditMode'),
    ('D2c', 'Assets/Scripts/Application/ShopSession.cs', '            _run.StakeRuleEnabled\n            && !IsStakeUpgradeSoldOut', '            true\n            && !IsStakeUpgradeSoldOut', '꺼진 런에도 CanBuy 참', 'EditMode'),
    ('D2d', 'Assets/Scripts/Application/ShopSession.cs', '_stakeUpgradeSoldOut = true;', '_stakeUpgradeSoldOut = false;', '품절이 서지 않음', 'EditMode'),
    ('D2e', 'Assets/Scripts/Application/ShopSession.cs', '_ = checked(_run.Chips + StakeUpgradeAmount);', '_ = unchecked(_run.Chips + StakeUpgradeAmount);', '넘침 사전 판정 없음', 'EditMode'),
    ('D2f', 'Assets/Scripts/Application/ShopSession.cs', '_run.RaiseStake(StakeUpgradeAmount);', '_run.RaiseStake(StakeUpgradePrice);', '양 대신 값만큼 올림', 'EditMode'),
    ('D2g', 'Assets/Scripts/Application/ShopSession.cs', 'if (!_run.TrySpend(StakeUpgradePrice))', 'if (!_run.TrySpend(StakeUpgradeAmount))', '값 대신 양만큼 냄', 'EditMode'),
    ('D2h', 'Assets/Scripts/Application/ShopSession.cs', 'if (stakeUpgradePrice < 1)', 'if (stakeUpgradePrice < 0)', '값 0 허용', 'EditMode'),
    ('D2i', 'Assets/Scripts/Application/ShopSession.cs', '&& _run.CanSpend(StakeUpgradePrice);', '&& true;', 'CanBuy가 잔액을 묻지 않음', 'EditMode'),
    # ── 물주 덱 750 ──
    ('MJ1', 'Assets/Scripts/Domain/Decks/DeckCatalog.cs', 'DeckEffectKind.AddStartChip, 750),', 'DeckEffectKind.AddStartChip, 600),', '물주를 옛 값 600으로 되돌림', 'EditMode'),
    # ── 밑천 올리기 E: 상점 칸·계기판 상승 ──
    ('E1a', 'Assets/Scripts/Presentation/Hud/ShopView.cs', 'session != null && session.StakeRuleEnabled && !session.IsStakeUpgradeSoldOut);', 'session != null && !session.IsStakeUpgradeSoldOut);', '꺼진 런에도 밑천 칸을 세움', 'EditMode'),
    ('E1b', 'Assets/Scripts/Presentation/Hud/ShopView.cs', '_buyStakeButton.interactable = session != null && session.CanBuyStakeUpgrade;', '_buyStakeButton.interactable = session != null;', '잔액과 무관하게 눌 수 있음', 'EditMode'),
    ('E1c', 'Assets/Scripts/Presentation/Hud/ShopView.cs', '            session.BuyStakeUpgrade();', '            ;', '눌러도 사지 않음', 'EditMode'),
    ('E1d', 'Assets/Scripts/Presentation/Hud/ShopView.cs', '_stakePriceIcon.sprite = sprite;', '_stakePriceIcon.sprite = null;', '밑천 값 아이콘을 비움', 'EditMode'),
    ('E1e', 'Assets/Prefabs/UI/ShopView.prefab', '_buyStakeButton: {fileID: 1453755991161651877}', '_buyStakeButton: {fileID: 0}', '프리팹 밑천 버튼 배선 끊김', 'EditMode'),
    ('E2a', 'Assets/Scripts/Presentation/Hud/MatchView.cs', '            CancelStakeRise();\n            if (seat.Stake.IsActive)', '            if (seat.Stake.IsActive)', '스냅샷이 상승을 끊지 않음', 'PlayMode'),
    ('E2b', 'Assets/Scripts/Presentation/Hud/MatchView.cs', '_selfPanel.CancelStakeRise();', ';', '화면이 꺼져도 상승을 끊지 않음', 'PlayMode'),
    ('E2c', 'Assets/Scripts/Presentation/Hud/MatchView.cs', 'chips > previousStake &&', 'chips >= previousStake &&', '같은 값에도 상승', 'PlayMode'),
    ('E2d', 'Assets/Scripts/Presentation/Hud/MatchView.cs', 'PlayStakeRise(previousStake, chips, riseDuration);', ';', '상승을 부르지 않음', 'PlayMode'),
    ('E2e', 'Assets/Scripts/Presentation/Hud/MatchView.cs', 'private const float StakeRisePeakScale = 1.06f;', 'private const float StakeRisePeakScale = 1f;', '부풀기 없음', 'PlayMode'),
    ('E2f', 'Assets/Scripts/Presentation/Hud/MatchView.cs', 'private const float StakeRisePeakScale = 1.06f;', 'private const float StakeRisePeakScale = 1.2f;', '부푼 글자가 칸 밖으로', 'PlayMode'),
    ('DA1', 'Assets/Scripts/Domain/Opponents/HeuristicAiPolicy.cs', 'return -DiscardCost(action, context, outcome, depthBp);', 'return 0;', '버림 비용 항 꺼짐', 'EditMode'),
    ('DA2', 'Assets/Scripts/Domain/Opponents/HeuristicAiPolicy.cs', 'divisor *= PairHeldCostDivisor;', 'divisor *= 1;', '짝 절반 없음', 'EditMode'),
    ('DA3', 'Assets/Scripts/Domain/Opponents/HeuristicAiPolicy.cs', 'int unseenSameMonth = context.UnseenCountOfMonth(discarded.Month);', 'int unseenSameMonth = ActiveCardSet.CardsPerMonth;', '미확인 장수 무시', 'EditMode'),
    ('DA4', 'Assets/Scripts/Domain/Opponents/HeuristicAiPolicy.cs', '+ ScoreDelta(context.OpponentCaptured, discardedOnly, context.OpponentDeck) * PointValueInChips;', '+ 0;', '상대 족보 증가분 무시', 'EditMode'),
    ('DA5', 'Assets/Scripts/Domain/Opponents/HeuristicAiPolicy.cs', 'if (context.OwnHandCountOfMonth(discarded.Month) > 1)', 'if (context.OwnHandCountOfMonth(discarded.Month) > 0)', '짝 판정이 늘 참', 'EditMode'),
    ('DB1', 'Assets/Scripts/Simulation/MatchSimRunner.cs', '_opponentDeck,', 'PlayerDeck.Empty,', '상대 덱이 흐름에 안 닿음', 'EditMode'),
    ('DB2', 'Assets/Scripts/Simulation/MatchSimRunner.cs', '_playerEffectSlots,', 'Array.Empty<EffectDefinition>(),', '플레이어 장착이 흐름에 안 닿음', 'EditMode'),
    ('DB3', 'Assets/Scripts/Simulation/MatchSimRunner.cs', '_opponentEffectSlots,', 'Array.Empty<EffectDefinition>(),', '상대 장착이 흐름에 안 닿음', 'EditMode'),
    ('DB4', 'Assets/Scripts/Simulation/MatchSimRunner.cs', '_playerEffectSlots,\n                _opponentEffectSlots,', '_opponentEffectSlots,\n                _playerEffectSlots,', '두 좌석 장착이 뒤바뀜', 'EditMode'),
    ('DB5', 'Assets/Scripts/Simulation/MatchSimRunner.cs', '_opponentDeck = opponentDeck ?? throw new ArgumentNullException(nameof(opponentDeck));', '_opponentDeck = opponentDeck;', '상대 덱 null 가드 없음', 'EditMode'),
    ('DC1', 'Assets/Scripts/Domain/Run/CardUpgrade.cs', 'tag = upgrade.TagOverride.Value;', 'tag = definition.Tag;', '태그 덮어쓰기를 접지 않음', 'EditMode'),
    ('DC2', 'Assets/Scripts/Domain/Run/CardUpgrade.cs', 'definition.Category, tag, countValue,', 'definition.Category, definition.Tag, countValue,', '해석이 원형 태그를 반환', 'EditMode'),
    ('DC3', 'Assets/Scripts/Domain/Run/CardUpgrade.cs', 'if (tagOverride.HasValue && !Enum.IsDefined(typeof(CardTag), tagOverride.Value))', 'if (false)', '정의 밖 태그 가드 없음', 'EditMode'),
    ('DC4', 'Assets/Scripts/Domain/Run/CardUpgrade.cs', 'if (upgrade.TagOverride.HasValue)', 'if (upgrade.TagOverride.HasValue && tag == definition.Tag)', '첫 덮어쓰기만 반영', 'EditMode'),
    ('DC5', 'Assets/Scripts/Domain/Match/MatchFlow.cs', 'HandScoreCalculator.Calculate(winnerCaptured, DeckOf(winner), _settlementBalance);', 'HandScoreCalculator.Calculate(winnerCaptured, DeckOf(loser), _settlementBalance);', '정산 채점이 패자 렌즈', 'EditMode'),
    ('DD1', 'Assets/Scripts/Domain/Opponents/HeuristicAiPolicy.cs', 'score += VariantSetProgress(gained, context, depthBp);', 'score += 0;', '세트 진행 항 꺼짐', 'EditMode'),
    ('DD2', 'Assets/Scripts/Domain/Opponents/HeuristicAiPolicy.cs', 'if (before + gainedCount >= line.RequiredCount)', 'if (false)', '완성 순간도 진행으로 셈', 'EditMode'),
    ('DD3', 'Assets/Scripts/Domain/Opponents/HeuristicAiPolicy.cs', 'OwnVariantHands = seat == Seat.Player ? playerVariantHands : opponentVariantHands;', 'OwnVariantHands = playerVariantHands;', '좌석 무시하고 플레이어 줄', 'EditMode'),
    ('DD4', 'Assets/Scripts/Domain/Opponents/HeuristicAiPolicy.cs', 'if (definition.Tag != tag && deck.Resolve(definition).Tag == tag)', 'if (deck.Resolve(definition).Tag == tag)', '원형 그대로도 변종 줄로 셈', 'EditMode'),
    ('DD5', 'Assets/Scripts/Domain/Opponents/HeuristicAiPolicy.cs', 'long ownWeightBp = BpOne + context.Profile.CautionBp;', 'long ownWeightBp = BpOne;', '신중함 가중 무시', 'EditMode'),
    ('DF1', 'Assets/Scripts/Domain/Run/StampCatalog.cs', 'if (definition.Category != EligibleCategory)', 'if (false)', 'CanStamp 범주 검사 없음(등가 예상)', 'EditMode'),
    ('DF2', 'Assets/Scripts/Domain/Run/StampCatalog.cs', 'new[] { CardTag.Cheongdan, CardTag.Chodan, CardTag.BiTti }),', 'new[] { CardTag.Cheongdan, CardTag.Chodan }),', '홍단 도장 원천에서 비띠 빠짐', 'EditMode'),
    ('DF3', 'Assets/Scripts/Domain/Run/StampCatalog.cs', 'return new CardUpgrade(null, 0, TargetTag);', 'return new CardUpgrade(null, 0, null);', '도장 강화가 태그를 안 바꿈', 'EditMode'),
    ('DF4', 'Assets/Scripts/Domain/Run/StampCatalog.cs', 'if (IsDanTag(targetTag) && eligibleCategory != CardCategory.Tti)', 'if (false)', '단 도장 범주 가드 없음', 'EditMode'),
    ('DE1', 'Assets/Scripts/Domain/Run/RunStamps.cs', 'if (IsFull)', 'if (false)', '칸 상한 없음', 'EditMode'),
    ('DE2', 'Assets/Scripts/Domain/Run/RunStamps.cs', 'if (existing >= 0)\n            {\n                _slots[existing] = new StampSlot(card, stamp);', 'if (false)\n            {\n                _slots[existing] = new StampSlot(card, stamp);', '같은 패 교체 대신 새 칸', 'EditMode'),
    ('DE3', 'Assets/Scripts/Domain/Run/RunStamps.cs', 'return entries;', 'return new List<DeckEntry>(entries);', '도장 0에서 새 목록', 'EditMode'),
    ('DE4', 'Assets/Scripts/Domain/Run/RunStamps.cs', 'result.Add(WithStampLast(entry, _slots[slot].Stamp));', 'result.Add(new DeckEntry(entry.DefinitionId, new[] { _slots[slot].Stamp.ToUpgrade() }));', '도장 칸이 금박 단을 버림', 'EditMode'),
    ('DE5', 'Assets/Scripts/Domain/Run/RunStamps.cs', 'if (existing >= 0 && existing != slotIndex)', 'if (false)', '덮어쓰기 다른 칸 가드 없음', 'EditMode'),
    ('DE6', 'Assets/Scripts/Domain/Run/RunStamps.cs', 'if (!stamp.CanStamp(definition))', 'if (false)', '적용 대상 검사 없음', 'EditMode'),
    ('DE7', 'Assets/Scripts/Domain/Run/RunStamps.cs', 'if (!merged[slot])', 'if (false)', '덱에 없는 도장 패를 버림', 'EditMode'),
    ('DE8', 'Assets/Scripts/Domain/Run/RunStamps.cs', 'CardCatalog.Get(card);\n            return FindSlot(card);', 'return FindSlot(card);', 'IndexOf가 미실재 id를 조용히 넘김', 'EditMode'),
    ('DG1', 'Assets/Scripts/Simulation/MatchSimRunner.cs', 'bool byPlayer = captured.Actor == Seat.Player;', 'bool byPlayer = captured.Actor != Seat.Player;', '행동자 좌석 뒤집힘', 'EditMode'),
    ('DG2', 'Assets/Scripts/Simulation/MatchSimRunner.cs', 'if (_playerStampCards.Count == 0 || alreadyCounted)', 'if (_playerStampCards.Count == 0)', '판마다 한 번 제한 없음', 'EditMode'),
    ('DG3', 'Assets/Scripts/Simulation/MatchSimRunner.cs', 'if (entries[index].Score >= _stopThreshold)', 'if (entries[index].Score > _stopThreshold)', '문턱 같음을 빼먹음', 'EditMode'),
    ('DG4', 'Assets/Scripts/Simulation/MatchSimRunner.cs', 'if (entries[index].Score >= _stopThreshold)', 'if (score.TotalScore >= _stopThreshold)', '항목 대신 총점', 'EditMode'),
    ('DG5', 'Assets/Scripts/Simulation/MatchSimRunner.cs', '_playerStampCapturedThisRound = false;', ';', '라운드 시작 초기화 없음', 'EditMode'),
    ('DG6', 'Assets/Scripts/Simulation/MatchSimRunner.cs', 'if (deck.Resolve(definition).Tag != definition.Tag)', 'if (true)', '도장 패 집합이 전부', 'EditMode'),
    ('DG7', 'Assets/Scripts/Simulation/SimTelemetry.cs', 'AppendSigned(builder, "roundsWithOpponentStampCapture", record.RoundsWithOpponentStampCapture);', ';', '직렬화 키 누락', 'EditMode'),
    ('SA1', 'Assets/Scripts/Domain/Run/StampCatalog.cs', 'new[] { CardTag.Hongdan, CardTag.Chodan, CardTag.BiTti }),', 'new[] { CardTag.Hongdan, CardTag.BiTti }),', '청단 도장 원천에서 초단 빠짐', 'EditMode'),
    ('SA2', 'Assets/Scripts/Domain/Run/StampCatalog.cs', '"stamp_chodan", CardTag.Chodan, CardCategory.Tti,', '"stamp_chodan", CardTag.Cheongdan, CardCategory.Tti,', '초단 도장 목표가 청단', 'EditMode'),
    ('SA3', 'Assets/Scripts/Domain/Run/StampCatalog.cs', '                new StampDefinition(\n                    "stamp_chodan", CardTag.Chodan, CardCategory.Tti,\n                    new[] { CardTag.Hongdan, CardTag.Cheongdan, CardTag.BiTti }),\n', '', '초단 도장 행 없음', 'EditMode'),
    ('SA4', 'Assets/Scripts/Infrastructure/GameData/BgBalanceLoader.cs', 'int stampPrice = Require(values, "stamp_price");', 'int stampPrice = values.TryGetValue("stamp_price", out int sp) ? sp : 100;', 'stamp_price 누락을 조용히 넘김', 'EditMode'),
    ('SA5', 'Assets/Scripts/Domain/Balance/ShopBalance.cs', 'StampPrice = BalanceGuard.RequirePositive(stampPrice, nameof(stampPrice));', 'StampPrice = BalanceGuard.RequireNonNegative(stampPrice, nameof(stampPrice));', '도장 값 0 허용', 'EditMode'),
    ('SB1', 'Assets/Scripts/Boot/MatchSessionFactory.cs', 'cardUpgrades = _stamps.ApplyTo(cardUpgrades);', ';', '도장이 덱 렌즈에 안 실림', 'PlayMode'),
    ('SB2', 'Assets/Scripts/Boot/MatchSessionFactory.cs', '_stakeRuleEnabled, _balances.Shop.StartGold);\n            _upgrades = new RunUpgrades();\n            _cardUpgrades = new RunCardUpgrades();\n            _bonusCards = new RunBonusCards();\n            _stamps = new RunStamps();', '_stakeRuleEnabled, _balances.Shop.StartGold);\n            _upgrades = new RunUpgrades();\n            _cardUpgrades = new RunCardUpgrades();\n            _bonusCards = new RunBonusCards();', '새 런이 옛 도장을 이음', 'PlayMode'),
    ('SB3', 'Assets/Scripts/Boot/MatchSessionFactory.cs', '_stamps.Stamp(new CardDefinitionId(definitionId), StampCatalog.Get(stampStableId));', 'try { _stamps.Stamp(new CardDefinitionId(definitionId), StampCatalog.Get(stampStableId)); } catch (System.ArgumentException) { }', 'DebugStamp가 거부를 삼킴', 'PlayMode'),
    ('SC1', 'Assets/Scripts/Application/ShopSession.cs', 'if (second >= first)\n            {\n                second++;\n            }', 'if (false)\n            {\n                second++;\n            }', '둘째 제시 보정 없음(같은 도장 둘)', 'EditMode'),
    ('SC2', 'Assets/Scripts/Application/ShopSession.cs', 'offers.Add(catalog[low]);\n            offers.Add(catalog[high]);', 'offers.Add(catalog[first]);\n            offers.Add(catalog[second]);', '제시 정렬 없음', 'EditMode'),
    ('SC3', 'Assets/Scripts/Application/ShopSession.cs', '            _stampSoldOut = true;', '            ;', '도장 품절 표시 없음', 'EditMode'),
    ('SC4', 'Assets/Scripts/Application/ShopSession.cs', '&& !IsStampSoldOut\n            && _run.Phase == RunPhase.AwaitingMatch', '&& !IsStampSoldOut', '도장 SKU 국면 조건 없음', 'EditMode'),
    ('SC5', 'Assets/Scripts/Application/ShopSession.cs', 'if (IsSameStamp(_stamps.Slots[held].Stamp, stamp))', 'if (false)', '같은 도장 재구매 허용', 'EditMode'),
    ('SC6', 'Assets/Scripts/Application/ShopSession.cs', 'return overwriteSlot >= 0 && overwriteSlot < RunStamps.SlotCount;', 'return overwriteSlot >= 0;', '덮을 칸 상한 검사 없음', 'EditMode'),
    ('SC7', 'Assets/Scripts/Application/ShopSession.cs', 'if (!CanPlaceStamp(stampStableId, definitionId, overwriteSlot))', 'if (false)', 'BuyStamp가 배치 규칙을 건너뜀', 'EditMode'),
    ('SC8', 'Assets/Scripts/Application/ShopSession.cs', '                    heldStamp.StableId);', '                    null);', 'HeldStampId가 늘 null', 'EditMode'),
    ('SD1', 'Assets/Scripts/Presentation/Hud/ShopStampPanel.cs', '                && _chosenCard.HasValue\n                && session.CanPlaceStamp(\n                    session.StampOffers[_offerIndex].StableId, _chosenCard.Value, _chosenSlot);', '                && _chosenCard.HasValue;', '확인 버튼이 CanPlaceStamp를 안 묻는다', 'EditMode'),
    ('SD2', 'Assets/Scripts/Presentation/Hud/ShopStampPanel.cs', '            Close();\n            buy(stampId, card, slot);', '            buy(stampId, card, slot);\n            Close();', '확인이 닫기보다 사기를 먼저 한다', 'EditMode'),
    ('SD3', 'Assets/Scripts/Presentation/Hud/ShopStampPanel.cs', 'card.SetChoosable(!string.Equals(target.HeldStampId, offer.StableId, StringComparison.Ordinal));', 'card.SetChoosable(true);', '같은 도장을 든 패도 고를 수 있다', 'EditMode'),
    ('SD4', 'Assets/Scripts/Presentation/Hud/ShopView.cs', '            session.BuyStamp(stampStableId, definitionId, overwriteSlot);\n\n            RenderShelf();\n            SettleLayout();\n            HudModal.TakeSelectionIfLost(_leaveButton != null ? _leaveButton.gameObject : null);', '            session.BuyStamp(stampStableId, definitionId, overwriteSlot);\n\n            RenderShelf();\n            SettleLayout();', '도장 구매 뒤 잃은 선택을 안 옮긴다', 'EditMode'),
    ('SD5', 'Assets/Scripts/Presentation/Hud/ShopView.cs', '            HideChipOpening();\n            CloseStampPanel();\n            RenderShelf();', '            HideChipOpening();\n            RenderShelf();', '재방문이 도장 패널을 안 닫는다', 'EditMode'),
    ('SD6', 'Assets/Scripts/Presentation/Hud/ShopView.cs', 'bool stampPanelOpen = _stampPanel != null && _stampPanel.IsOpen;', 'bool stampPanelOpen = false;', '도장 패널이 열려도 매대를 안 잠근다', 'EditMode'),
    ('SD7', 'Assets/Scripts/Presentation/Hud/ShopView.cs', '            // 잠금을 먼저 푼다. 잠긴 버튼에 선택을 주면 uGUI가 그 선택을 지운다.\n            RenderShelf();\n', '            // 잠금을 먼저 푼다. 잠긴 버튼에 선택을 주면 uGUI가 그 선택을 지운다.\n', '그만이 잠금을 안 풀고 선택을 준다', 'EditMode'),
    ('SE1', 'Assets/Scripts/Application/MatchSession.cs', '                CountTiers(entry.Upgrades),', '                entry.Upgrades.Count,', '도장을 금박 단으로 센다', 'PlayMode'),
    ('SE2', 'Assets/Scripts/Application/MatchSession.cs', '                : StampLineProjection.TargetLineOf(resolvedTag);', '                : (ScoreLineKind?)null;', '프로브의 도장 줄이 늘 null', 'PlayMode'),
    ('SE3', 'Assets/Scripts/Application/ScoreLineMembers.cs', 'if (CountsToward(card, deck.Resolve(card).Tag, kind))', 'if (CountsToward(card, card.Tag, kind))', '후보 표가 렌즈를 무시한다', 'EditMode'),
    ('SE4', 'Assets/Scripts/Application/PresentationVocabulary.cs', '                && IsWeightAltered == other.IsWeightAltered\n                && StampLine == other.StampLine;', '                && IsWeightAltered == other.IsWeightAltered;', '같음 비교가 도장 줄을 무시한다', 'EditMode'),
    ('SF1', 'Assets/Scripts/Presentation/Board/CardView.cs', '                else\n                {\n                    _stampBadge.Hide();\n                }', '                else\n                {\n                }', '도장이 빠져도 배지가 남는다', 'EditMode'),
    ('SF2', 'Assets/Scripts/Presentation/Hud/JokboTracker.cs', '                _lineMembers != null && _lineMembers.TryGetValue(line.Kind, out IReadOnlyList<ushort> lensMembers)', '                false && _lineMembers.TryGetValue(line.Kind, out IReadOnlyList<ushort> lensMembers)', '힌트가 렌즈 표를 안 쓴다', 'EditMode'),
    ('SF3', 'Assets/Scripts/Presentation/Hud/JokboTracker.cs', '            _lineMembers = null;', '            // MUTATION', '판 사이에 렌즈 표가 남는다', 'EditMode'),
    ('SF4', 'Assets/Scripts/Presentation/Board/CardStampBadge.cs', 'bounds.max.x - bounds.size.x * RightInsetFactor,', 'bounds.min.x + bounds.size.x * RightInsetFactor,', '배지가 왼쪽 위로 간다', 'EditMode'),
    ('SF5', 'Assets/Scripts/Presentation/Board/CardStampBadge.cs', '_labelRenderer.sortingOrder = sortingOrder + SortingOrderOffset;', '_labelRenderer.sortingOrder = sortingOrder;', '배지가 카드와 같은 정렬 순서', 'EditMode'),
    ('SF6', 'Assets/Scripts/Presentation/Board/CardViewRegistry.cs', 'if (zone == BoardZone.OpponentCaptured && values.HasStamp)', 'if (false && values.HasStamp)', '상대 획득패에도 내 도장 배지', 'EditMode'),
    ('SF7', 'Assets/Scripts/Presentation/Board/CardView.cs', 'if (!IsFlipCovered && _upgradeValues.HasStamp)', 'if (_upgradeValues.HasStamp)', '뒤집기 가림 중에도 배지', 'EditMode'),
    ('SF8', 'Assets/Scripts/Presentation/Board/CardStampBadge.cs', '            _label = holder.AddComponent<TextMeshPro>();\n            if (_font != null)\n            {\n                _label.font = _font;\n            }', '            _label = holder.AddComponent<TextMeshPro>();', '새 배지 라벨이 폰트를 안 받는다', 'EditMode'),
    ('SF9', 'Assets/Scripts/Presentation/Board/CardStampBadge.cs', '            if (_label != null && font != null)\n            {\n                _label.font = font;\n            }', '            if (false)\n            {\n                _label.font = font;\n            }', '이미 선 배지가 폰트 교체를 안 받는다', 'EditMode'),
]


def read(path):
    with open(path, "rb") as f:
        return f.read()


def write(path, data):
    with open(path, "wb") as f:
        f.write(data)


def run_one(name, rel, old, new, why, platform="EditMode"):
    src_bytes = read(f"{SRC}/{rel}")
    dst_path = f"{DST}/{rel}"
    if read(dst_path) != src_bytes:
        print(f"{name}: 사본이 원본과 다르다. 먼저 동기화하라")
        return None

    text = src_bytes.decode("utf-8")
    crlf = "\r\n" in text
    probe = old.replace("\n", "\r\n") if crlf else old
    repl = new.replace("\n", "\r\n") if crlf else new
    if text.count(probe) != 1:
        print(f"{name}: 원문이 {text.count(probe)}회. 정확히 1회여야 한다")
        return None

    write(dst_path, text.replace(probe, repl).encode("utf-8"))
    try:
        try:
            import os
            os.remove(RESULTS)
        except FileNotFoundError:
            pass
        subprocess.run([UNITY, "-batchmode", "-nographics", "-projectPath", DST, "-runTests",
                        "-testPlatform", platform, "-testResults", RESULTS, "-logFile", LOG],
                       capture_output=True, timeout=900)
        try:
            root = ET.parse(RESULTS).getroot()
        except Exception:
            print(f"{name} ({why}): 결과 없음. 컴파일 실패를 의심한다")
            return None
        failed = [tc.get("fullname").replace("DoubleDown.Presentation.Tests.", "").replace("DoubleDown.Integration.Tests.", "").replace("DoubleDown.Integration.Tests.", "")
                  for tc in root.iter("test-case") if tc.get("result") == "Failed"]
        print(f"{name} ({why}, {platform}): 총 {root.get('total')} / 실패 {root.get('failed')}")
        for f in failed:
            print(f"    - {f}")
        return failed
    finally:
        write(dst_path, src_bytes)
        assert read(dst_path) == src_bytes, f"{name}: 사본 원복 실패"


def main():
    wanted = set(sys.argv[1:])
    for m in MUTATIONS:
        if wanted and m[0] not in wanted:
            continue
        run_one(*m)
        sys.stdout.flush()


if __name__ == "__main__":
    main()
