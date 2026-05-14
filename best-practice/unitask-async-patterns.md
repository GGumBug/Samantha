[← README로 돌아가기](../README.md)

# UniTask 비동기 패턴 — 인시던트 기반 권위 가이드

Unity 프로젝트의 비동기 코드에서 **반복적으로 발생한 누수·race·취소 누락 인시던트**를 박제. 룰 단축본은 [.claude/rules/unitask-async.md](../.claude/rules/unitask-async.md), 본 문서는 인시던트와 Before/After.

이 문서는 권위 가이드다. 단정형 어조 항목은 **타협하지 말 것** — Hwaseo 프로젝트의 실제 사고 비용으로 도출됐다.

## 1. `async void` 무가드 누수 — UILoading.cs

### 인시던트 (`Assets/Scripts/UI/UILoading.cs:22, 49`)

```csharp
private async void OnEnable() { await LoadingStartAnimation(); }   // token 없음

private async void LoadingEndAction()
{
    await canvasGroup.DOFade(0, fadeDuration);
    await SceneManager.UnloadSceneAsync(...);   // 예외 시 호출자 전파 불가
}
```

`OnDisable`에서 `DOTween.Kill`만 함 — Kill 후에도 await 콜백 race 가능.

### 처방

```csharp
private CancellationTokenSource _cts;

private void Awake() { _cts = new CancellationTokenSource(); }

private void OnEnable() { LoadingStartAsync(_cts.Token).Forget(); }

private async UniTaskVoid LoadingStartAsync(CancellationToken token)
{
    try { await canvasGroup.DOFade(1, fadeDuration).ToUniTask(cancellationToken: token); }
    catch (OperationCanceledException) { /* 정상 */ }
    catch (Exception e) { Debug.LogException(e); }
}

private void OnDestroy()
{
    _cts?.Cancel(); _cts?.Dispose(); _cts = null;
    DOTween.Kill(canvasGroup);
}
```

**핵심**: `async void` → `UniTaskVoid + .Forget() + token + try/catch` 4종 세트.

## 2. 컨펌 다이얼로그의 폐기된 await — UIRewards.cs

### 인시던트 (`Assets/Scripts/Runtime/UIRewards.cs:54`)

```csharp
public async void Close()   // async void → 호출자(onClick) await 불가
{
    var simplePopup = await UIManager.Instance.GetUIAsync<UIPopup>();
    simplePopup.SetMessage(...);   // 사용자가 빠르게 X 누르면 destroyed object
}
```

### 처방

```csharp
public void Close()   // 동기 본문, 비동기는 분리
{
    if (setReward == 0) { EndReward(); return; }
    ShowConfirmAsync(_cts.Token).Forget();
}

private async UniTaskVoid ShowConfirmAsync(CancellationToken token)
{
    try
    {
        var popup = await UIManager.Instance.GetUIAsync<UIPopup>()
            .AttachExternalCancellation(token);
        if (popup == null || token.IsCancellationRequested) return;
        popup.SetMessage(L10n.T(BattleKeys.REWARD_CONFIRM_CLOSE));
    }
    catch (OperationCanceledException) { /* 정상 */ }
}
```

**핵심**: 사용자 입력 콜백은 동기 본문, 비동기는 `UniTaskVoid + token` 분리.

## 3. 대량 루프 + 재진입 — LocalizationDispatcher.cs (모범 참고)

### CTS 라이프사이클 (`LocalizationDispatcher.cs:44-77`)

```csharp
private CancellationTokenSource _flushCts;

private void Awake()     { _flushCts = new CancellationTokenSource(); }
private void OnDestroy() { _flushCts?.Cancel(); _flushCts?.Dispose(); _flushCts = null; }
```

### 재진입 가드 + frame-budget (`LocalizationDispatcher.cs:254-317`)

```csharp
private bool _isApplying;

private void OnLocaleChanged(LocaleType _)
{
    if (_isApplying) { Debug.LogWarning("re-entry suppressed."); return; }
    FlushAsync(_flushCts.Token).Forget();
}

private async UniTaskVoid FlushAsync(CancellationToken token)
{
    _isApplying = true;
    try
    {
        int processed = 0;
        for (int i = _bindings.Count - 1; i >= 0; i--)
        {
            if (token.IsCancellationRequested) return;
            _bindings[i]?.Apply();
            if (++processed % FRAME_BUDGET_PER_BATCH == 0)
                await UniTask.Yield(PlayerLoopTiming.Update, token);
        }
        // ILocalizedView, ILocaleAware 동일 패턴
    }
    catch (OperationCanceledException) { /* 정상 */ }
    catch (Exception e) { Debug.LogException(e); }
    finally { _isApplying = false; }
}
```

### 학습 포인트

- 재진입 가드: 빠른 Locale 토글 차단. 없으면 enumeration 중 컬렉션 수정 예외
- Frame-budget: `processed % N == 0`마다 yield → hitch 방지
- 취소 체크 이중화: 루프 진입 + yield 토큰 전달
- try/catch/finally: `OperationCanceledException` 분리, finally `_isApplying = false`

## 4. PlayerLoopTiming 선택 가이드

| 상황 | timing | 이유 |
|------|--------|------|
| 일반 UI batch | `Update` | 안전 기본값 |
| Rigidbody 동기 | `FixedUpdate` | 물리 스텝 정합 |
| 카메라 후처리 | `PostLateUpdate` | LateUpdate 다음 |

생략 시 기본 `Update`이지만 **명시로 의도 박제** — 미래 개발자 추적 비용 절감.

## 5. Cancel-Cleanup Bypass + 강제 토글

`try/catch (OperationCanceledException)` 흡수 시 try 본문의 cleanup 코드 (`SetActive(false)` / 콜백 발화) 가 우회되는 함정. 강제 토글 (`if (activeSelf) SetActive(false); SetActive(true);`) 로 4 진입 상태 멱등 보장.

상세: [cancel-cleanup-bypass.md](cancel-cleanup-bypass.md).

## 6. 안티패턴 카탈로그

| # | 안티패턴 | 처방 |
|---|----------|------|
| A | `await UniTask.Delay(1000)` (token 없음) | `cancellationToken: token` 전달 |
| B | OnDestroy에서 `_cts?.Cancel()`만 | Cancel + Dispose + null 3단계 |
| C | `catch (Exception)`으로 `OperationCanceledException` 일괄 로깅 | 분리 catch — OperationCanceled는 무시 |
| D | `.Forget()` 본문에 try/catch 없음 | 예외 사일런트 → try/catch 필수 |
| E | `Forget()` 후 동일 메서드 즉시 `await` | 동시 실행 race — 양자택일 |

## 체크리스트 (작업 종료 직전 self-audit)

- [ ] `async void`가 Unity 라이프사이클 메서드 외 어디에도 없는가?
- [ ] CTS Awake/OnDestroy 라이프사이클 완비됐는가?
- [ ] 50+ 루프에 frame-budget yield가 있는가?
- [ ] DOTween 사용 시 `ToUniTask` token 전달됐는가?
- [ ] `OperationCanceledException` 분리 catch됐는가?
- [ ] `CancellationToken`이 비동기 시그니처 전체에 흐르는가?
- [ ] 재진입 가능 작업에 `_isApplying` 또는 token 재발급 패턴이 있는가?

## 관련 문서

- [.claude/rules/unitask-async.md](../.claude/rules/unitask-async.md) — 9개 룰 단축본
- [.claude/rules/engineering-constitution.md](../.claude/rules/engineering-constitution.md) — SOLID/SSOT
- [refactoring-lessons.md](refactoring-lessons.md) §6 — 방어 분기 로깅
- [evidence-based-debugging.md](evidence-based-debugging.md) — 비동기 race 진단
- [multi-axis-fast-path-guard.md](multi-axis-fast-path-guard.md) — `_isHideInProgress` 같은 재진입 플래그를 fast path 가드에 합성
