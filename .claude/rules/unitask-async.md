# Glob: **/*.cs

## UniTask 비동기 헌법 (사용자 명시 없이 항상 적용)

Unity 프로젝트의 모든 비동기 코드는 **UniTask 기반**으로 작성한다. `Task`/`async void`/`Coroutine` 혼용은 GC, 캡처, 취소 누락, 라이프사이클 누수의 주범. 다음 10개 룰은 **타협 불가 기본값** — 매번 프롬프트에서 상기시키지 않아도 모든 Unity 에이전트에 박제된다.

상세 인시던트 분석과 Before/After 코드는 [best-practice/unitask-async-patterns.md](../../best-practice/unitask-async-patterns.md) 참조. 코루틴→UniTask 마이그레이션 비대칭(작성자 깜빡 패턴)은 [best-practice/paradigm-transition-asymmetry.md](../../best-practice/paradigm-transition-asymmetry.md).

### 룰 1 — `async void` 절대 금지 (단, Unity 이벤트 메서드 예외)

`async void`는 예외를 삼키고 호출자가 `await` 불가능하다. 진단도 안 되고 취소도 안 된다.

- **금지**: 일반 메서드, 이벤트 핸들러, 콜백 함수
- **예외 허용 (좁게)**: `OnEnable`, `OnDisable`, `Awake`, `Start` 등 Unity 라이프사이클 메서드만 — 단 본문은 `try/catch (OperationCanceledException)` 필수
- **대체**: 일반 비동기는 `UniTask` / `UniTaskVoid` 반환. fire-and-forget은 `.Forget()` 명시

### 룰 2 — CancellationTokenSource 라이프사이클 의무

CTS는 생성자/Awake에서 만들고 OnDestroy에서 **반드시 Cancel + Dispose + null 대입**. 누수 시 다음 씬에서 이전 토큰의 작업이 살아남아 race 발생.

```csharp
private CancellationTokenSource _cts;

private void Awake()    { _cts = new CancellationTokenSource(); }
private void OnDestroy()
{
    _cts?.Cancel();
    _cts?.Dispose();
    _cts = null;
}
```

### 룰 3 — Frame-Budget Batching 의무 (대량 루프)

UI 50개 이상, DB row 100개 이상 같은 대량 루프를 한 프레임에 처리하면 hitch 발생. **N개마다 `await UniTask.Yield(PlayerLoopTiming.Update, token)`**.

```csharp
const int FRAME_BUDGET_PER_BATCH = 32;
for (int i = 0; i < items.Count; i++)
{
    if (token.IsCancellationRequested) return;
    Process(items[i]);
    if ((i + 1) % FRAME_BUDGET_PER_BATCH == 0)
        await UniTask.Yield(PlayerLoopTiming.Update, token);
}
```

배치 크기는 측정 기반 — 16/32/64 중 hitch 없는 최대값 선택.

### 룰 4 — `.Forget()` 가드 의무

fire-and-forget을 명시할 때 `.Forget()`은 단순 호출이 아니라 **예외 처리 보증** 역할. `try/catch`가 없는 `UniTaskVoid`는 예외가 사일런트하게 사라진다.

```csharp
// 안티패턴
SomeOperationAsync().Forget();   // 예외 발생 시 무음

// 권장
private async UniTaskVoid SomeOperationAsync()
{
    try { /* ... */ }
    catch (OperationCanceledException) { /* 정상 */ }
    catch (Exception e) { Debug.LogException(e); }
}
SomeOperationAsync().Forget();
```

### 룰 5 — `OperationCanceledException`은 정상 종료로 분류

CTS Cancel 시 `OperationCanceledException`이 throw된다. 이는 **에러가 아니라 정상 흐름**:

```csharp
try { await SomethingAsync(token); }
catch (OperationCanceledException) { /* 정상 종료 — 무시 */ }
catch (Exception e) { Debug.LogException(e); }   // 진짜 에러만 로깅
```

`OperationCanceledException`을 일반 `Exception`으로 같이 잡아 LogException 하면 OnDestroy 시점에 매번 에러 로그 폭주.

### 룰 6 — 재진입 atomicity 가드

Locale 변경, Save/Load, Network refresh 등 **빠른 토글로 재진입이 가능한 작업**은 `_isApplying` 플래그로 가드:

```csharp
private bool _isApplying;

private async UniTaskVoid FlushAsync(CancellationToken token)
{
    if (_isApplying) return;       // 또는 이전 작업 cancel 후 재시작
    _isApplying = true;
    try { /* ... */ }
    finally { _isApplying = false; }
}
```

가드 없이 재진입하면 컬렉션 수정 중 enumeration 변경 예외, 부분 적용, race 발생.

### 룰 7 — 트윈은 **LitMotion**, `MotionHandle` 보관 + 취소 의무

이 프로젝트의 트윈 라이브러리는 **LitMotion**이다(`com.annulusgames.lit-motion`). **DOTween은 설치돼 있지 않다** — `DG.Tweening` 사용·설치 금지(트윈 라이브러리 이중화).

모션을 띄우고 버리면 파괴된 대상에 `Bind` 콜백이 잔존한다. 다음 3가지가 세트다:

1. **`MotionHandle`을 필드로 보관** — 재실행·정리 시 취소하려면 핸들이 있어야 한다
2. **재실행 전·`OnDestroy`에서 `TryCancel()`**
3. **`destroyCancellationToken`과 호출자 token을 링크** — 수동 CTS 신설보다 우선(룰 2·9)

```csharp
private MotionHandle _handle;

private void OnDestroy() => _handle.TryCancel();   // 파괴 대상에 Bind 콜백 잔존 방지

private async UniTask FadeToAsync(float target, CancellationToken token)
{
    _handle.TryCancel();                            // 이전 모션 먼저 정리 — 두 모션이 같은 값을 다투지 않게
    using var linked = CancellationTokenSource.CreateLinkedTokenSource(destroyCancellationToken, token);

    _handle = LMotion.Create(_canvasGroup.alpha, target, _duration)
        // Bind는 static 람다 + 상태 인자 — 클로저 할당 회피(매 모션마다 GC 발생 방지)
        .Bind(_canvasGroup, static (alpha, group) => group.alpha = alpha);

    await _handle.ToUniTask(linked.Token);
}
```

실사용 선례: `Packages/com.ggumbug.gamecore/Runtime/UI/UIScreenFader.cs`.

### 룰 8 — `PlayerLoopTiming` 명시

`UniTask.Yield()`/`UniTask.DelayFrame()`은 timing 인자를 항상 명시:

- 기본 안전: `PlayerLoopTiming.Update`
- 물리 동기화 필요: `PlayerLoopTiming.FixedUpdate`
- 카메라 직후 처리: `PlayerLoopTiming.PostLateUpdate`

생략 시 기본값(`PlayerLoopTiming.Update`)이 쓰이지만 **명시함으로써 의도를 코드에 박제**한다 (Why 주석 대체).

### 룰 9 — `CancellationToken` 전파 의무

비동기 메서드 시그니처는 **`CancellationToken token` 파라미터를 받아 하위 호출에 전파**한다. 토큰을 무시하고 작업하는 메서드는 OnDestroy 후에도 살아남는다.

```csharp
// 안티패턴
public async UniTask LoadAsync()
{
    await Resources.LoadAsync<Sprite>(path);   // token 없음
}

// 권장
public async UniTask LoadAsync(CancellationToken token)
{
    await Resources.LoadAsync<Sprite>(path).ToUniTask(cancellationToken: token);
}
```

호출 사슬의 **최상단까지 token이 흘러야** 안전. 중간에 끊기면 그 지점부터 누수.

### 룰 10 — 일괄 리셋은 "교체 후 Cancel" (세대 토큰)

`ReleaseAll`/`Clear` 같은 **일괄 리셋 + 진행 중 비동기 작업** 조합에서, 리셋용 CTS는 **새 CTS로 교체(+세대 증가)를 Cancel보다 먼저** 수행한다. `Cancel()`의 동기 continuation이 재진입해도 새 세대·빈 상태 위에서 동작해 옛 상태를 오염시킬 수 없다. 완료 직후 취소 edge는 **작업 시작 시 세대 캡처 → 커밋 직전 비교**로 방어.

```csharp
_generation++;
var old = _resetCts;
_resetCts = new CancellationTokenSource();   // 1. 교체 먼저
ClearEntries();                              // 2. 상태 비우기
old.Cancel(); old.Dispose();                 // 3. Cancel은 마지막
```

상세 Before/After와 세대 비교 코드: [best-practice/generation-token-reset.md](../../best-practice/generation-token-reset.md). (2026-07-08 GameCore PoolService ReleaseAll race)

## 자가 검증 체크리스트

코드 작성/수정 후 보고 직전:

- [ ] `async void`가 Unity 이벤트 메서드(OnEnable 등) 외 어디에도 없는가?
- [ ] CTS는 Awake에서 생성, OnDestroy에서 Cancel+Dispose+null 처리되는가?
- [ ] 50+ 항목 루프에 frame-budget yield가 있는가?
- [ ] `.Forget()` 호출 대상 메서드 본문에 try/catch가 있는가?
- [ ] `OperationCanceledException`이 일반 Exception과 분리 처리되는가?
- [ ] 재진입 가능 작업에 `_isApplying` 가드가 있는가?
- [ ] LitMotion 모션의 `MotionHandle`을 보관하고 `OnDestroy`·재실행 전에 `TryCancel()` 하는가? (`DG.Tweening` 사용 0건인가?)
- [ ] `UniTask.Yield`/`DelayFrame`에 PlayerLoopTiming이 명시되어 있는가?
- [ ] 비동기 메서드 시그니처가 CancellationToken을 받는가?
- [ ] 일괄 리셋 메서드에서 CTS 교체(+세대 증가)가 Cancel보다 먼저인가?

## 관련 문서

- [best-practice/unitask-async-patterns.md](../../best-practice/unitask-async-patterns.md) — 인시던트 + Before/After 상세
- [best-practice/generation-token-reset.md](../../best-practice/generation-token-reset.md) — 세대 토큰 패턴 상세
- [.claude/rules/engineering-constitution.md](engineering-constitution.md) — SOLID/SSOT 원칙
- [.claude/rules/evaluation.md](evaluation.md) — 평가 주도 검증
