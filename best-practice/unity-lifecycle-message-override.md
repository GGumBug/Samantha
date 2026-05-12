[← README로 돌아가기](../README.md)

# Unity 라이프사이클 메시지 가로채기 함정

Unity의 `Awake`/`Start`/`OnEnable`/`OnDisable`/`OnDestroy` 등은 **C# 가상 함수가 아니라 reflection 기반 메시지**다. 부모와 자식이 같은 이름의 메시지 메서드를 정의하면 **자식 정의가 부모 호출을 가로채고**, 부모 본문은 `base.Awake()`를 명시적으로 호출하지 않는 한 영원히 실행되지 않는다.

`UIBase`처럼 베이스 클래스가 `Awake`에서 리스너 등록·바인딩·초기화를 수행하는 패턴에서 가장 위험. 자식이 `private void Awake()`를 신설하는 순간 부모의 모든 초기화가 사라진다.

## 인시던트 (2026-05-12 UIShop CardRemoval)

`UIBase.cs`는 `protected async void Awake()`에서 `AddListener()`를 호출해 `btnExit`/`btnDebugAddGold` 등 공통 버튼 리스너를 등록한다. UIShop 카드 제거 기능 작업 중 `UIShop`에 `private void Awake()`가 신설되어 **부모 `Awake`가 호출되지 않게 됨** → 모든 디버그 버튼이 무동작 상태로 회귀. 컴파일은 통과, 런타임 NRE도 없음 — 사용자가 Editor에서 직접 버튼을 눌러보고서야 발견.

### 왜 grep으로 잡히지 않았나

- 자식의 `private void Awake()`만 보면 SOLID 위반이 없음 (메서드 이름 충돌 경고도 없음)
- `Awake`는 C# 메서드가 아니라 Unity 메시지 — `override` 키워드가 강제되지 않음
- IDE의 "Override Method" 마법사도 동작하지 않음 (`Awake`는 virtual이 아니라서)

## 처방 — Init() Template Method 패턴

`UIBase`는 이미 자식 확장 지점으로 `protected virtual void Init()`를 제공한다. 자식은 **`Awake`를 정의하지 말고** `Init`을 override한다.

### Before (가로채기 발생)

```csharp
public class UIShop : UIBase
{
    private void Awake()                    // 부모 Awake 가로챔
    {
        _cardRemovalSlots = new List<UIShopSlot>();
        BindCardRemovalUI();
    }
}
```

`UIBase.Awake`의 `AddListener()` 호출이 실행되지 않아 `btnExit`/`btnDebugAddGold` 리스너 미등록.

### After (Template Method)

```csharp
public class UIShop : UIBase
{
    protected override void Init()          // UIBase.Awake → Init() 호출 체인 보존
    {
        base.Init();                        // 부모 초기화 명시
        _cardRemovalSlots = new List<UIShopSlot>();
        BindCardRemovalUI();
    }
}
```

## 검증된 미러링 — UIBase 자식 10곳 패턴

UIBase 자식 중 `Awake`를 신설한 경우는 0건. 모두 `Init` 또는 부모가 제공하는 다른 진입점을 override:

- `AudioManager`, `BattleManager`, `PlayerManager`, `PotionGameRoot`
- `SceneLoadManager`, `RelicSystemRoot`, `UIToolTip`, `UITooltipList`
- `UIRelicReward`, `UIEncounterPanelView`

UIShop만 1곳 예외였음 → 이 인시던트로 통일.

## 자동 검증 grep

**의무 패턴** (Unity 라이프사이클 메시지를 자식이 신설했는지 + 부모 호출 누락 여부):

```
grep -rnE "private void (Awake|Start|OnEnable|OnDisable|OnDestroy)\(\)" Assets/Scripts
```

검출된 각 파일에 대해:
1. 클래스가 `MonoBehaviour` 직속이면 OK (부모 호출 불필요)
2. 클래스가 **다른 클래스 상속**이면 `: SomeBase` 부모를 grep으로 추적 → 부모가 같은 이름의 메시지 메서드를 가지는지 확인
3. 부모가 가지고 있으면 **자식에서 즉시 `base.XXX()` 호출 추가** 또는 부모의 `protected virtual` 진입점으로 이동

## Senior Default Mode 추가 게이트

헌법 [§0-1 Step 1](../.claude/rules/engineering-constitution.md)의 변경 전 영향 분석에 박제:

> Unity 라이프사이클 메시지(`Awake`/`Start`/`OnEnable`/`OnDestroy`) **신설** 시 부모 클래스 grep 의무. Unity 메시지는 reflection 기반이라 자식 정의 시 부모 호출이 누락된다. `override` 강제가 없으므로 컴파일러도 IDE도 경고하지 않음.

## 관련 문서

- [.claude/rules/engineering-constitution.md](../.claude/rules/engineering-constitution.md) — Senior Default Mode §0-1
- [.claude/rules/unity-delegation.md](../.claude/rules/unity-delegation.md) — Unity 위임 규칙
- [refactoring-lessons.md](refactoring-lessons.md) — §12.5 SSOT 단일 진입점 보존
- [overload-semantic-equivalence.md](overload-semantic-equivalence.md) — 오버로드/override 의미론 등가성
