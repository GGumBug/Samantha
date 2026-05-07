# Glob: **/*.cs

## UniTask 비동기 헌법 (사용자 명시 없이 항상 적용)

Unity 프로젝트의 모든 비동기 코드는 **UniTask 기반**으로 작성한다. `Task`/`async void`/`Coroutine` 혼용은 GC, 캡처, 취소 누락, 라이프사이클 누수의 주범. 다음 9개 룰은 **타협 불가 기본값** — 매번 프롬프트에서 상기시키지 않아도 모든 Unity 에이전트에 박제된다.

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

### 룰 7 — `DOTween.ToUniTask`는 token 전달 필수

DOTween Tween을 await할 때 cancellation token 미전달 시 OnDestroy 후에도 콜백이 살아남는다.

```csharp
// 안티패턴
await canvasGroup.DOFade(1, 1f).ToUniTask();

// 권장
await canvasGroup.DOFade(1, 1f).ToUniTask(cancellationToken: _cts.Token);
```

또는 `OnDisable`/`OnDestroy`에서 `DOTween.Kill(target)` 명시.

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

## 자가 검증 체크리스트

코드 작성/수정 후 보고 직전:

- [ ] `async void`가 Unity 이벤트 메서드(OnEnable 등) 외 어디에도 없는가?
- [ ] CTS는 Awake에서 생성, OnDestroy에서 Cancel+Dispose+null 처리되는가?
- [ ] 50+ 항목 루프에 frame-budget yield가 있는가?
- [ ] `.Forget()` 호출 대상 메서드 본문에 try/catch가 있는가?
- [ ] `OperationCanceledException`이 일반 Exception과 분리 처리되는가?
- [ ] 재진입 가능 작업에 `_isApplying` 가드가 있는가?
- [ ] `DOTween.ToUniTask` 호출에 token이 전달되는가?
- [ ] `UniTask.Yield`/`DelayFrame`에 PlayerLoopTiming이 명시되어 있는가?
- [ ] 비동기 메서드 시그니처가 CancellationToken을 받는가?

## 관련 문서

- [best-practice/unitask-async-patterns.md](../../best-practice/unitask-async-patterns.md) — 인시던트 + Before/After 상세
- [.claude/rules/engineering-constitution.md](engineering-constitution.md) — SOLID/SSOT 원칙
- [.claude/rules/evaluation.md](evaluation.md) — 평가 주도 검증
