[← README로 돌아가기](../README.md)

# 세대 토큰 패턴 — 일괄 리셋 시 "교체 후 Cancel" (swap-before-cancel)

`ReleaseAll()` / `Clear()` / `ResetAll()` 같은 **일괄 리셋**과 **진행 중 비동기 작업**이 공존하는 시스템의 race 차단 패턴. (2026-07-08 GameCore PoolService DI 리팩토링에서 박제)

## 문제

리셋용 linked CTS를 두고 리셋 시 Cancel하는 표준 구성에서, **Cancel을 먼저 하고 새 CTS로 교체**하면 다음 race 발생:

- `CancellationTokenSource.Cancel()`은 등록된 continuation을 **동기 실행**할 수 있다
- continuation(catch/finally/재시도 로직)이 리셋 대상 컬렉션/상태에 **재진입** → "리셋 중인 옛 상태" 위에서 동작
- 결과: 반쯤 비운 컬렉션에 재등록, 옛 세대 인스턴스가 새 세대 상태에 혼입

```csharp
// 안티패턴 — Cancel 먼저
public void ReleaseAll()
{
    _resetCts.Cancel();          // 동기 continuation이 여기서 재진입 가능
    _resetCts.Dispose();
    _resetCts = new CancellationTokenSource();   // 재진입이 이미 옛 상태를 오염시킨 후
    ClearEntries();
}
```

## 패턴 — 교체를 Cancel보다 먼저

```csharp
private CancellationTokenSource _resetCts = new();
private int _generation;

public void ReleaseAll()
{
    // 1. 세대 증가 + 새 CTS로 교체 (이후 재진입은 새 세대 위에서 동작)
    _generation++;
    var old = _resetCts;
    _resetCts = new CancellationTokenSource();

    // 2. 상태 비우기 (새 세대는 빈 상태에서 시작)
    ClearEntries();

    // 3. 마지막에 Cancel — 동기 continuation이 재진입해도 새 세대·빈 상태
    old.Cancel();
    old.Dispose();
}
```

핵심: **Cancel 시점에 이미 "리셋이 완료된 새 세계"가 준비**되어 있어야 한다. 재진입한 continuation은 새 CTS/빈 컬렉션을 보게 되어 옛 세대 상태를 오염시킬 수 없다.

## 완료 직후 취소 edge — 세대 캡처 비교

비동기 작업이 "완료됐지만 결과를 커밋하기 전"에 리셋이 끼어드는 edge는 토큰만으로 못 막는다 (토큰 체크 통과 직후 리셋 가능). **작업 시작 시 세대를 캡처하고 커밋 직전 비교**:

```csharp
public async UniTask<T> AcquireAsync(CancellationToken callerToken)
{
    int gen = _generation;                     // 시작 시 세대 캡처
    using var linked = CancellationTokenSource.CreateLinkedTokenSource(
        callerToken, _resetCts.Token);
    var instance = await LoadAsync(linked.Token);

    if (gen != _generation)                    // 커밋 직전 세대 비교
    {
        DestroyInstance(instance);             // 옛 세대 결과 폐기
        throw new OperationCanceledException();
    }
    Register(instance);
    return instance;
}
```

## 적용 대상 (일반화)

풀링에 한정되지 않는다 — "일괄 리셋 + 진행 중 비동기" 조합 전부:

- 오브젝트 풀 `ReleaseAll` + 진행 중 `AcquireAsync`
- 씬 전환 시 매니저 상태 리셋 + 진행 중 로드
- 캐시 전체 invalidate + 진행 중 fetch
- 세이브 슬롯 교체 + 진행 중 자동 저장

## 자가 점검

- [ ] 리셋 메서드에서 CTS 교체(+세대 증가)가 Cancel보다 먼저인가?
- [ ] Cancel되는 CTS는 로컬 변수로 분리해 Dispose하는가?
- [ ] 커밋 직전 세대 비교가 있는가 (완료 직후 취소 edge)?
- [ ] 옛 세대 결과물의 폐기 경로(Destroy/dispose)가 있는가?

## 관련 룰

- [.claude/rules/unitask-async.md](../.claude/rules/unitask-async.md) 룰 10 — 요약본
- [unitask-async-patterns.md](unitask-async-patterns.md) — UniTask 인시던트 카탈로그
