[← 목록](../README.md)

# Double Down 런 시작 덱 패시브 설계

2026-09-23. 런을 시작할 때 고른 덱이 그 런 전체의 규칙을 바꾸는 구조를 확정한다. 구조는 사용자 승인분을 입력으로 받고, 이 문서가 정하는 것은 타입 표면, 접기 순서, 소비 지점, 시험 명부, 구현 분할이다. 코드 변경은 0건이다.

대상 저장소는 Double Down(`/Users/minki/Unity_Projects/Double Down`). 인용한 좌표는 모두 실측이다.

## 1. 한 줄 요약과 계층 둘의 경계

덱은 `DeckEffectRow` 목록이고 리듀서가 그 목록을 `RunRules` 하나로 접는다. 소비자는 `RunRules`의 축만 읽고 덱의 존재를 모른다.

| 계층 | 시점 | 종류 판정 | 입력 | 출력 |
|---|---|---|---|---|
| 설정 | 런 시작 1회 | `RunRulesReducer`(신설) | `MatchBalance` 기준값 + 덱 행 | `RunRules` |
| 사건 | 판 중 다회 | `EffectInterpreter`(기존, 손대지 않는다) | 장착 낱장 + 문맥 | `EffectOutcome` |

경계를 갈라 주는 질문은 **값이 언제 정해지는가** 하나다. 런 시작에 한 번 정해져 런 내내 같은 값이면 설정 계층이고, 판 안의 사건마다 다시 물어야 하면 사건 계층이다.

두 계층은 이미 한 축을 공유한다. `EffectConditionKind.IsSeon`(`Assets/Scripts/Domain/Effects/EffectVocabulary.cs:116`)이 좌석의 선 여부를 읽으므로, 설정 계층이 선을 덮어쓰면 사건 계층이 그 결과를 저절로 읽는다. 두 계층을 잇는 배관은 필요하지 않다.

## 2. 타입 목록

| 타입 | 파일 | 어셈블리 / 네임스페이스 |
|---|---|---|
| `DeckEffectKind` | `Assets/Scripts/Domain/Decks/DeckEffectKind.cs` | `DoubleDown.Domain` / `DoubleDown.Domain.Decks` |
| `DeckEffectRow` | `Assets/Scripts/Domain/Decks/DeckEffectRow.cs` | 같음 |
| `DeckCatalog` | `Assets/Scripts/Domain/Decks/DeckCatalog.cs` | 같음 |
| `FirstSeatPolicy` | `Assets/Scripts/Domain/Run/RunRules.cs` | `DoubleDown.Domain` / `DoubleDown.Domain.Run` |
| `RunRules` | 같은 파일 | 같음 |
| `RunRulesReducer` | `Assets/Scripts/Domain/Run/RunRulesReducer.cs` | 같음 |

`Domain` 어셈블리는 `noEngineReferences: true`라 여섯 타입 모두 Unity 의존 0인 POCO다. `FirstSeatPolicy`를 `RunRules`와 한 파일에 두는 근거는 `RunFlow.cs`가 `RunPhase`를 같은 자리에 두는 선례다. `MatchFlow.cs`는 이미 `using DoubleDown.Domain.Run;`을 들고 있어 소비 측 import는 늘지 않는다.

```csharp
public enum DeckEffectKind : byte
{
    AddStartChip = 1,
    ForcePlayerFirstSeat = 2,
}

public sealed class DeckEffectRow
{
    public DeckEffectRow(ushort deckId, DeckEffectKind kind, int amount);
    public ushort DeckId { get; }
    public DeckEffectKind Kind { get; }
    public int Amount { get; }
}

public static class DeckCatalog
{
    public const ushort BasicDeckId = 1;
    public const ushort ChojjaDeckId = 2;
    public const ushort SeonteonDeckId = 3;

    public static IReadOnlyList<ushort> AllDeckIds { get; }
    public static IReadOnlyList<DeckEffectRow> RowsFor(ushort deckId);
    public static bool Exists(ushort deckId);
    public static void Validate(IReadOnlyList<DeckEffectRow> rows);
}

public enum FirstSeatPolicy : byte
{
    ByPick = 1,
    PlayerFirst = 2,
}

public sealed class RunRules
{
    public RunRules(int startChip, FirstSeatPolicy firstSeat);
    public int StartChip { get; }
    public FirstSeatPolicy FirstSeat { get; }
}

public static class RunRulesReducer
{
    public static RunRules Reduce(MatchBalance baseline, IReadOnlyList<DeckEffectRow> rows);
}
```

표면에 대한 결정 넷.

- **열거 값은 1부터 시작한다.** `EffectConditionKind.None = 0`과 달리 덱 행에는 "효과 없음" 멤버가 없다. 0을 비워 두면 `default(DeckEffectKind)`가 어휘 밖 값이라 초기화 누락이 리듀서의 `default`에서 즉시 터진다. `FirstSeatPolicy`도 같은 이유로 1부터다.
- **`DeckCatalog`는 `EffectCatalog`와 같은 형태다.** 하드코딩 fixture가 시트 행의 동결 사본이고 BGDatabase read-path는 뒤로 이연한다. **v1에 Infrastructure 계층(시트 탭, BGDB 로더)은 없다.** id는 1부터 append-only이고 0은 예약이며 지운 덱의 id는 재사용하지 않는다.
- **`Validate`가 public인 근거는 `EffectCatalog.Validate`와 같다.** 불변식을 검사하는 곳이 하나여야 하고, 나중에 붙는 시트 어댑터도 같은 문을 지나야 한다. 종류별 파라미터 계약(`AddStartChip`은 `Amount != 0`, `ForcePlayerFirstSeat`은 `Amount == 0`)을 그 안에 둔다.
- **`RunRules`는 `sealed class`다.** `readonly struct`로 두면 `default(RunRules)`가 `StartChip = 0`이라 생성자 가드를 우회하는 sentinel이 생긴다. 생성자는 `BalanceGuard.RequirePositive`로 개시 자본 1 이상을 강제한다(같은 어셈블리의 `internal` 가드다).

이름에 대한 주의 한 줄. 이 저장소에서 "덱"은 이미 48장 화투 덱(`PlayerDeck`, `DeckEntry`, `CanonicalDeckSize`)을 뜻한다. 새 여섯 타입은 런 시작 덱이라 뜻이 다르고, 폴더와 네임스페이스(`Domain.Decks`)가 그 구분을 나른다.

## 3. 접기 알고리즘

축마다 **순서에 닿지 않는 연산만** 쓴다. 가산은 교환·결합 법칙을 타고 덮어쓰기는 멱등이라, 행 순서를 뒤섞어도 누산 결과가 같다. 기준값에 얹는 순서는 행이 아니라 루프 뒤의 마지막 줄이 정한다. 그다음 불변 객체 하나로 봉한다.

```csharp
public static RunRules Reduce(MatchBalance baseline, IReadOnlyList<DeckEffectRow> rows)
{
    int startChipDelta = 0;
    FirstSeatPolicy firstSeat = FirstSeatPolicy.ByPick;
    for (int index = 0; index < rows.Count; index++)
    {
        DeckEffectRow row = rows[index];
        switch (row.Kind)
        {
            case DeckEffectKind.AddStartChip: startChipDelta += row.Amount; break;
            case DeckEffectKind.ForcePlayerFirstSeat: firstSeat = FirstSeatPolicy.PlayerFirst; break;
            default: throw new NotSupportedException(
                $"Deck row {row.DeckId}: kind '{row.Kind}' is in the vocabulary but no fold exists yet"
                + " - add it here together with its parameter contract in DeckCatalog.Validate.");
        }
    }

    return new RunRules(baseline.PlayerStartChip + startChipDelta, firstSeat);
}
```

`default`의 어조는 `EffectInterpreter.FireCount`(`Assets/Scripts/Domain/Effects/EffectInterpreter.cs:171`)를 그대로 따른다. 0이나 기준값을 조용히 돌려주면 행을 넣은 사람이 배선 실수와 미구현을 구분할 수 없다.

v1은 종류가 둘뿐이라 order 정수 축을 넣지 않는다. Add와 Mul이 같은 칸을 겨누는 날 §5의 순열 시험이 먼저 빨간불이 되고, 그때 order를 넣는다.

## 4. 소비 지점 변경

| 좌표 | before | after |
|---|---|---|
| `Boot/MatchSceneInstaller.cs:57` | `var run = new RunFlow(balances.Match.PlayerStartChip, catalog.FinalAct);` | 위에 `RunRules rules = RunRulesReducer.Reduce(balances.Match, DeckCatalog.RowsFor(PendingRunConfig.Value.DeckId));`를 더하고 `new RunFlow(rules.StartChip, catalog.FinalAct)`로 바꾼다 |
| `Boot/MatchSceneInstaller.cs:65` | `run, PendingRunConfig.Value.Seed);` | `run, rules, PendingRunConfig.Value.Seed);` |
| `Boot/MatchSessionFactory.cs:145,162` | 생성자 2문 | `RunRules rules`를 `run` 다음에 필수 인자로 더하고 `_rules` 필드에 담는다 |
| `Boot/MatchSessionFactory.cs:444` | `_run = new RunFlow(_balances.Match.PlayerStartChip, _opponentCatalog.FinalAct);` | `_run = new RunFlow(_rules.StartChip, _opponentCatalog.FinalAct);` |
| `Boot/MatchSessionFactory.cs:281` 근처 | 동결 블록(칩·각서·작업패·장착) | 아래에 `FirstSeatPolicy firstSeat = _rules.FirstSeat;`를 더해 `CreateFlow` 인자로 넘긴다 |
| `Boot/MatchSessionFactory.cs:503` | `CreateFlow(... int runChips, ...)` | `FirstSeatPolicy firstSeatPolicy`를 더해 `CreateWithOpponentProfile`로 전달한다 |
| `Domain/Match/MatchFlow.cs:171,300,358` | 입구 3문 | `settlementBalance` 다음에 `FirstSeatPolicy firstSeatPolicy` 필수 인자를 더하고 `_firstSeatPolicy`에 담는다 |
| `Domain/Match/MatchFlow.cs:492` | `SeonResolver.Resolve(playerPickIndex, seonStream, _eventSink);` | `SeonResolver.Resolve(playerPickIndex, seonStream, _eventSink, _firstSeatPolicy);` |
| `Domain/Round/SeonResolver.cs:43` | `Resolve(byte, IRandomStream, IEventSink)` | 네 번째 필수 인자 `FirstSeatPolicy firstSeatPolicy` |
| `Domain/Round/SeonResolver.cs:72` | `Seat firstSeat = playerCard.Month > opponentCard.Month ? Seat.Player : Seat.Opponent;` | 아래 블록 |
| `Boot/RunConfig.cs:17` | `RunConfig(string seedCode)` | `RunConfig(string seedCode, ushort deckId)` + `public ushort DeckId { get; }`. 생성 시점에 `DeckCatalog.Exists`로 거른다 |
| `Boot/RunConfig.cs:37` | `new RunConfig(DefaultSeedCode)` | `new RunConfig(DefaultSeedCode, DeckCatalog.BasicDeckId)` |
| `Boot/Scenes/TitleScene.cs:148` | `PendingRunConfig.Set(new RunConfig(code));` | `new RunConfig(code, DeckCatalog.BasicDeckId)`. 사람이 고른 값으로 바뀌는 자리는 Presentation 카드다 |
| `Simulation/MatchSimRunner.cs` | `CreateWithOpponentProfile(...)` 1건 | 정책 인자를 명시한다 |

`SeonResolver.cs:72`의 after는 닫힌 열거 분기로 쓴다.

```csharp
switch (firstSeatPolicy)
{
    case FirstSeatPolicy.ByPick:
        firstSeat = playerCard.Month > opponentCard.Month ? Seat.Player : Seat.Opponent;
        break;
    case FirstSeatPolicy.PlayerFirst:
        firstSeat = Seat.Player;
        break;
    default:
        throw new NotSupportedException($"First seat policy '{firstSeatPolicy}' has no resolution yet.");
}
```

**`MatchFlow`에 `RunRules`를 통째로 넘기지 않는 근거.** `CreateFlow`는 이미 런의 칩으로 판 스코프 `MatchBalance`를 합성한다(`MatchSessionFactory.cs:539`). `MatchFlow`가 `RunRules`를 함께 들면 `_matchBalance.PlayerStartChip`(이 판의 개시 칩)과 `_runRules.StartChip`(런의 개시 자본)이 한 클래스에 나란히 놓이고, 뒤에 읽는 사람이 둘을 맞바꿔도 컴파일과 시험이 통과한다. 그래서 수치 축은 지금처럼 합성 `MatchBalance`를 타고 들어가고, `MatchBalance`에 `With` 류 변환은 더하지 않으며, 판이 직접 쓰는 정책 축만 얼린 값으로 건넨다. 런 스코프 소지품을 판 조립 시점에 동결해 넘기는 그 공장의 규율과 같은 형태다. `RunRules`를 생성자 인자 하나로 받는 소비자는 런을 쥔 `MatchSessionFactory`다.

**`StartNewRun`은 같은 덱으로 다시 선다.** `_rules`를 다시 읽으므로 끝난 런의 덱이 새 런에 이어진다. 런 종료 화면이 서면 덱 재선택은 그 화면 뒤로 간다.

**`RunSetupView` 시그니처 권고.** `Assets/Scripts/Presentation/Title/RunSetupView.cs:37`을 `public event Action<string, ushort> StartRequested;`로 바꾸고 `RaiseStart()`가 (입력 글자, 고른 덱 id)를 싣는다. Presentation asmdef는 `DoubleDown.Domain`을 참조하지 않아 도메인 타입을 실을 수 없고, 화면은 고른 것만 말하고 다듬는 일은 듣는 쪽(`TitleScene`)이 한다는 기존 계약이 그대로 유지된다. 축이 셋째로 늘면 그때 묶음 struct로 감싼다. **v1은 시그니처만 정하고 배선은 하지 않는다.**

## 5. 시험 명세

| # | 픽스처 / 파일 | 모드 | 무는 것 | 빨간불 뮤테이션 한 줄 |
|---|---|---|---|---|
| 1 | `RunRulesReducerTests` · `Assets/Tests/Domain/` | EditMode | `Enum.GetValues(typeof(DeckEffectKind))` 전수. 모든 종류가 접히고, 모든 종류를 쓰는 덱이 카탈로그에 하나 이상 있다 | 리듀서의 `case DeckEffectKind.ForcePlayerFirstSeat:` 줄을 지운다 |
| 2 | 같음 | EditMode | 순서 무관. 시험이 만든 3행 목록의 모든 순열을 접어 `RunRules`의 **모든 public 속성**을 리플렉션으로 비교한다 | `startChipDelta += row.Amount;`를 `startChipDelta = row.Amount;`로 바꾼다 |
| 3 | 같음 | EditMode | 초짜 종단값 동결. `Reduce(MatchBalance.Placeholder, RowsFor(ChojjaDeckId)).StartChip`이 손계산값과 같다 | `baseline.PlayerStartChip + startChipDelta`를 `baseline.PlayerStartChip`으로 바꾼다 |
| 4 | 같음 | EditMode | 기본 덱 회귀. 0행을 접으면 `StartChip == MatchBalance.Placeholder.PlayerStartChip`이고 `FirstSeat == ByPick`이다 | 기본 덱 행 목록에 `AddStartChip` 행 하나를 더한다 |
| 5 | `SeonResolverTests` · `Assets/Tests/Domain/` | EditMode | 선턴 고정이 달 비교를 우회한다. `ByPick`이면 `Opponent`가 나오는 같은 입력에서 `PlayerFirst`가 `Player`를 낸다. draw는 여전히 정확히 1회이고 6필드가 모두 채워진다 | `case FirstSeatPolicy.PlayerFirst:`의 `firstSeat = Seat.Player;`를 `ByPick` 식으로 바꾼다 |
| 6 | `DeckPassiveWiringTests` · `Assets/Tests/Integration/` | PlayMode | 초짜 이득은 런 개시 1회다. 1판째 개시 칩은 기준값 + 행 값이고 2판째는 직전 판이 남긴 칩이다. 선턴 고정 덱으로 돌린 판은 매 라운드 `FirstSeat == Player`다 | `CreateFlow`의 `runChips`를 `_rules.StartChip`으로 바꾼다(판마다 재적용) |
| 7 | `RunConfigTests` · `Assets/Tests/Integration/` | PlayMode | 없는 덱 id는 생성 시점에 끊긴다. `RunConfig.Default.DeckId == BasicDeckId`가 동결이다 | `RunConfig` 생성자의 `DeckCatalog.Exists` 가드를 지운다 |

세 가지를 명시한다. ① 순열 시험은 카탈로그 덱이 아니라 **시험이 만든 3행 목록**을 쓴다. v1 덱은 행이 하나뿐이라 카탈로그로는 판별력이 0이다. ② 속성 비교를 리플렉션으로 파생하는 근거는 손으로 적은 명부가 축이 늘어난 날 조용히 거짓 통과하기 때문이다([hand-listed-roster-decay.md](../best-practice/hand-listed-roster-decay.md)). ③ `Assets/Tests/Domain`은 `includePlatforms: ["Editor"]`라 EditMode이고, `Assets/Tests/Integration`은 Boot를 참조해 PlayMode로 돈다.

## 6. 계층별 구현 분할

| 레인 | 어셈블리 | 신규 | 수정 | 호출 지점 |
|---|---|---|---|---|
| ① 도메인 | `DoubleDown.Domain` | 5파일 | `SeonResolver.cs`, `MatchFlow.cs` | 입구 3문 + `:492` + `:72` |
| ② 배선 | `Boot`, `Boot.Scenes`, `Simulation` | 0 | `RunConfig.cs`, `MatchSceneInstaller.cs`, `MatchSessionFactory.cs`, `TitleScene.cs`, `MatchSimRunner.cs` | 운영 7건 |
| ③ 시험 쓸기 | 시험 4묶음 | 0 | 22파일 | 43건(값만 더한다) |
| ④ 신규 시험 | `Domain.Tests`, `Integration.Tests` | 2파일 | `SeonResolverTests`, `RunConfigTests` | 시험 7건 |

기계적 쓸기 43건의 내역은 `new MatchFlow(` 7건, `CreateWithRuleJudges(` 4건, `CreateWithOpponentProfile(` 10건, `new MatchSessionFactory(` 11건, `SeonResolver.Resolve(` 10건, `RunConfig` 생성 8건이다(운영 7건 포함).

**판정: 계층당 한 에이전트로 가른다.** 관통 어셈블리가 6개(`Domain`, `Boot`, `Boot.Scenes`, `Simulation`, 시험 4묶음)이고 수정 파일이 30개를 넘어 한 에이전트의 25턴에 들어가지 않는다. 레인 간 시그니처는 코디네이터가 이 문서의 §2·§4 원문을 양쪽 프롬프트에 박아 확정하고, 배치 시험도 코디네이터가 돌린다. 레인 ④는 [evaluation.md](../.claude/rules/evaluation.md)의 작성자·구현자 분리에 따라 ①·②와 다른 에이전트에 맡긴다.

선턴 고정 정책을 `MatchFlow` 입구에 **필수** 인자로 넣는 값이 21건이다. 선택 인자로 두면 `MatchSimRunner`가 조용히 `ByPick`으로 계측해 덱 밸런스 수치가 어긋난다. 이 값은 첫 정책 축의 일회성 비용이고, 두 번째 정책 축이 오는 날 묶음 타입으로 바꿔 같은 쓸기를 반복하지 않는다.

## 7. 열린 결정

| 결정 | 권고안 | 근거 한 줄 |
|---|---|---|
| `RunConfig.Default`의 덱 | 중립 기본 덱(행 0개, `BasicDeckId`) | 빈 행 목록을 접은 값이 시트 기준값과 한 비트도 다르지 않아 §5 #4 회귀 시험의 주체가 되고, 널 가능한 덱 축이 생기지 않는다 |
| 선 뽑기 의식 | 유지하고 `firstSeat`만 덮는다 | 6필드가 모두 채워진 채 이벤트 형태와 "정확히 1 draw" 동결이 유지되고, 정책이 닿는 자리가 `:72` 하나로 끝난다. 발행을 건너뛰면 라운드 로그 형태가 덱마다 갈린다 |
| 초짜가 가산인가 배율인가 | 가산(`AddStartChip`) | 가산은 행이 몇 개든 순서 무관이 형태로 성립한다. 배율은 절단 규칙과 bp 단위를 v1에 미리 확정해야 하고 `DeckChipMultiplierBp`와 혼동 축이 생긴다. 금액은 데이터라 시트 튜닝에 맡긴다 |
| 덱 효과와 슬롯 상한 | 별도 목록으로 이어 붙인다(5칸을 먹지 않는다) | 5칸은 상점에서 사는 자원이라 덱이 한 칸을 먹으면 숨은 세금이 된다. 슬롯을 먹으면 추첨 풀 제외 규칙이 덱을 알아야 해 덱이 상점 계층으로 새어 나간다 |

기본 덱 권고에 딸린 단서 하나. v1 종단 배선은 기본 덱이라 초짜와 선턴 고정의 유일한 소비자가 시험이다. 호출자 없는 표면을 오래 두지 않으려면 덱 선택 Presentation 카드가 곧 따라와야 하고, 그 카드가 채우는 자리는 `TitleScene.cs:148` 한 곳이다.

슬롯 권고에 딸린 단서 둘. 이어 붙일 자리는 `MatchSessionFactory.cs:281`이고 덱 행이 앞에 선다. 슬롯 순서가 곧 발화 순서라 앞뒤가 정수 배율의 절단 지점을 바꾼다. `RunBonusCardsTests`의 `EffectCatalog.All.Count == RunBonusCards.MaxSlots` 역방향 가드는 별도 목록에서는 건드려지지 않는다.

## 8. 구조가 못 받는 것

행 하나로 되는 효과의 조건은 셋이다. ① 값이 런 시작에 정해진다 ② 그 값이 이미 있는 소비 지점 한 줄을 지난다 ③ 소비자가 닫힌 열거 분기로 읽는다. 판별 질문 하나로 줄이면 **"이 효과가 바꾸는 값이 이미 어딘가에 변수로 있는가"**다.

없으면 엔진 작업이고 갈래가 셋이다.

- **`EffectPhase` 5개 밖의 시점.** 분배 전, 선 결정 중, 상점 안 같은 시점은 발화 지점 자체가 엔진에 없다. 시점을 새로 뚫는 일은 행이 아니라 카드다.
- **엔진에 능력이 없는 것.** 되돌리기, 낸 카드 회수, 턴 재실행이 여기다. 이벤트 로그가 append-only이고 판 상태에 역연산이 없어, 행을 아무리 늘려도 표현할 대상이 없다.
- **자료 구조를 바꾸는 것.** 덱 장수 변경(48장 canonical 계약), 카드 마스킹 축(`CardSnapshot.FaceDown`), 좌석 수가 여기다. `EffectCatalog` 헤더가 백열등을 뺀 근거와 같은 계급이고, 생산 지점 전수 갱신이 따라온다.

**패시브 사건 효과의 이음매(v1 미구현).** 판 중에 패시브로 작용하는 효과의 길은 `DeckEffectKind.EquipEffect(effectId)` 행에서 `RunRules.PassiveEffectIds`를 거쳐 `MatchSessionFactory.cs:281`의 슬롯 목록에 합류하는 것이고, `EffectInterpreter`는 한 줄도 바뀌지 않는다. v1은 이 종류를 만들지 않는다. 소비자 없는 종류는 `EffectCatalog` 헤더가 거부하는 빈 훅이다. 열린 질문은 §7 마지막 줄의 슬롯 상한 하나다.

## 구조 충돌 0건, 발견 3건

구조를 바꿔야 하는 충돌은 없다. 아래 셋은 보고만 한다.

1. **이름 겹침.** `Domain.Decks`의 `DeckEffectRow`·`DeckCatalog`가 48장 덱 어휘(`PlayerDeck`, `DeckEntry`, `CanonicalDeckSize`, `DeckChipMultiplierBp`)와 같은 낱말을 쓴다. 구조 충돌이 아니라 읽는 사람의 비용이다.
2. **재현 좌표가 넓어진다.** 덱이 결과를 바꾸므로 같은 판을 되살리는 좌표가 시드 코드 하나에서 (시드 코드, 덱 id) 쌍이 된다. `MainScene.cs:1042`는 시드 코드만 표시하고 리플레이 계약에 덱 축이 없다.
3. **`MatchFlow` 생성자가 20 인자다.** 정책 축을 더하면 21이 된다. 이 문서는 그 자리를 재설계하지 않고, 두 번째 정책 축이 올 때 묶음 타입으로 가는 지점만 §6에 적어 둔다.

**인터페이스로 넘어가는 시점.** switch를 명부로 남기고 case 본문이 클래스에 위임하는 형태로 바뀌는 조건은 셋이다. ① case가 자기 상태를 갖는다 ② 한 case가 10줄을 넘는다 ③ `Domain` 어셈블리 밖에서 종류를 정의해야 한다. 그때도 switch는 "다 있는가"를 묻는 대상으로 남는다. 추가이고 재작성이 아니다.
