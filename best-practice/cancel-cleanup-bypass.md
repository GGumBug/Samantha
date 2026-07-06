[← README로 돌아가기](../README.md) | [engineering-constitution.md](../.claude/rules/engineering-constitution.md)

# Cancel-Cleanup Bypass — try/catch OperationCanceled 의 cleanup 우회

`try/catch (OperationCanceledException)` 으로 cancel 을 정상 종료로 흡수할 때, **try 블록의 await 이후 cleanup 코드가 도달 안 함**. cancel 경로에서도 cleanup 보장하는 패턴.

## 인시던트 — UIPanelSlider HideAsync cancel 시 SetActive(false) 누락

```csharp
// ❌ Cancel 시 cleanup 우회
public async UniTask HideAsync(CancellationToken token)
{
    _isHideInProgress = true;
    try
    {
        await _rect.DOAnchorPos(_startPos, _duration).ToUniTask(cancellationToken: token);
        gameObject.SetActive(false);    // cancel 시 도달 못 함
        _onHideCompleted?.Invoke();     // cancel 시 발화 안 됨
    }
    catch (OperationCanceledException) { /* 정상 — 그러나 cleanup 누락 */ }
    finally { _isHideInProgress = false; }
}
```

증상: cancel 경로에서 `SetActive(false)` + `OnHideCompleted` 발화가 누락 → 다음 Show 호출 시 panel 이 이미 active 라는 잘못된 멘탈 상태 + 다음 step 알림 누락. 두 번째 Show 가 같은 방향이면 fast path 가드가 발동하여 시각 시그널 0.

## 처방 — finally 블록으로 멱등 cleanup 강제

```csharp
public async UniTask HideAsync(CancellationToken token)
{
    _isHideInProgress = true;
    try
    {
        await _rect.DOAnchorPos(_startPos, _duration).ToUniTask(cancellationToken: token);
    }
    catch (OperationCanceledException) { /* 정상 */ }
    finally
    {
        _isHideInProgress = false;
        // 정상/cancel 양쪽 모두 cleanup 보장
        if (gameObject != null) gameObject.SetActive(false);
        _onHideCompleted?.Invoke();
    }
}
```

**룰**: `OperationCanceledException` 흡수 시 try 블록 후속 cleanup 코드를 **finally 로 이동** 또는 **별도 멱등 메서드로 분리**. cancel 경로에서도 도달 보장.

## 강제 토글 패턴 — 4 진입 상태 멱등성

cleanup 누락 buffer 가 발생하더라도 caller 측에서 방어할 수 있는 패턴.

```csharp
// 사전 생성 panel 의 Show 시 4가지 상태 멱등 대응
public async UniTask ShowAsync(CancellationToken token)
{
    if (gameObject.activeSelf) gameObject.SetActive(false);  // 강제 토글 — OnEnable 재발화
    gameObject.SetActive(true);
    await _rect.DOAnchorPos(_targetPos, _duration).ToUniTask(cancellationToken: token);
}
```

4 진입 상태 멱등 보장:

| 진입 상태 | activeSelf | _isHideInProgress | 강제 토글 효과 |
|-----------|-----------|-------------------|----------------|
| 사전 생성 직후 | false | false | 그대로 true 로 활성화, 정상 tween |
| 정상 Hide 직후 | false | false | 그대로 true 로 활성화, 정상 tween |
| Cancel Hide 직후 | true (cleanup 누락) | false | true → false → true 강제 토글 → OnEnable 재발화 → 깨끗한 시작 |
| Hide 없이 연속 Show | true | false | true → false → true 강제 토글 → 시각 시그널 유지 |

defense in depth — cleanup 누락이 있어도 강제 토글이 보호.

## 진단 체크리스트

비동기 작업의 cancel 경로 발견 시:

- [ ] `try` 블록에 `await` 이후 cleanup 코드 (`SetActive` / 콜백 / 상태 변경) 가 있는가?
- [ ] `catch (OperationCanceledException)` 으로 흡수하는 경로에서 cleanup 이 우회되는가?
- [ ] Cleanup 이 멱등인가? (이미 false 인데 false 호출해도 안전한가?)
- [ ] Caller 측에 강제 토글 같은 defense-in-depth 가 있는가?

## 본 세션 박제 근거

- `23e0f88e` UITutorialGuidePanel — UIPanelSlider 위임 + Y축 플립 + Left/Right 대칭 슬라이드 + same-side fast path (cancel cleanup 보장 + 강제 토글 도입)

## 관련 문서

- [unitask-async-patterns.md](unitask-async-patterns.md) — UniTask 인시던트 카탈로그
- [multi-axis-fast-path-guard.md](multi-axis-fast-path-guard.md) — `_isHideInProgress` fast path 가드
- [.claude/rules/unitask-async.md](../.claude/rules/unitask-async.md) — 9 룰 단축본
