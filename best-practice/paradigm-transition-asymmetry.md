[← CLAUDE.md로 돌아가기](../CLAUDE.md)

# 패러다임 전환 비대칭 — 새 패턴이 안전성을 강제하지 못할 때

옛 패턴 → 새 패턴 마이그레이션은 종종 **비대칭 비용**을 발생시킨다. 옛 패턴이 자동으로 보장하던 안전성을 새 패턴이 호출자에게 떠넘기면, 작성자가 깜빡할 때 silent bug가 누적된다.

## 1. 코루틴 yield return vs UniTask 명시 yield

**옛 패턴 (코루틴)**:
```csharp
IEnumerator ProcessLoop(List<Item> items)
{
    foreach (var item in items)
    {
        Process(item);
        yield return null;   // frame 분배 자동 — 한 줄
    }
}
```

**새 패턴 (UniTask)**:
```csharp
async UniTask ProcessLoop(List<Item> items, CancellationToken token)
{
    for (int i = 0; i < items.Count; i++)
    {
        Process(items[i]);
        if ((i + 1) % 32 == 0)
            await UniTask.Yield(PlayerLoopTiming.Update, token);  // 명시 — 깜빡 가능
    }
}
```

**비대칭**: 코루틴은 yield return이 frame budget 자동 분배. UniTask는 작성자가 batching을 의식해야 함 — 깜빡 시 hitch 누적.

**처방**: UniTask 마이그레이션 시 **frame-budget batching 자동 검증 grep** 의무 (`.claude/rules/unitask-async.md` §3 룰).

## 2. 시그니처가 안전성 강제 — Token Closure vs 명시 파라미터

**안티패턴 — `Func<UniTask>` (token 클로저 의존)**:
```csharp
public void Register(Func<UniTask> handler)  // token 시그니처에 없음
{
    _handlers.Add(handler);
}

// 호출자가 token 클로저 깜빡 가능
loader.Register(() => DoSomethingAsync());  // token 누락 — silent
```

**정공 — `Func<CancellationToken, UniTask>` (시그니처 강제)**:
```csharp
public void Register(Func<CancellationToken, UniTask> handler)  // token 시그니처 강제
{
    _handlers.Add(handler);
}

// 호출자가 token 안 받으면 컴파일 에러
loader.Register(token => DoSomethingAsync(token));  // 강제
```

**처방**: callback/handler 시그니처에 token을 **포지셔널 파라미터로** 박제. 시그니처가 안전성을 강제하면 작성자 깜빡 차단.

## 3. AsyncOperation .ToUniTask 라이브러리 패턴 인지

**안티패턴 — boilerplate 60줄**:
```csharp
var op = SceneManager.LoadSceneAsync("X");
while (!op.isDone)
{
    OnProgress(op.progress);
    yield return null;
}
// 추가 콜백, error handling, token check 수동 boilerplate
```

**정공 — `.ToUniTask` 1줄**:
```csharp
var op = SceneManager.LoadSceneAsync("X");
await op.ToUniTask(progress: Progress.Create<float>(OnProgress), cancellationToken: token);
```

**비대칭**: AsyncOperation은 `isDone` 폴링 패턴이 익숙해 boilerplate가 누적. UniTask `.ToUniTask` 인지 시 1줄로 압축 + token 전파 보장.

**처방**: `Resources.LoadAsync`, `SceneManager.LoadSceneAsync`, `Addressables.LoadAsync*`, `WebRequest` 사용 시 `.ToUniTask(cancellationToken: token)` 패턴 우선 검토.

## 본 세션 사례

| 회고 # | 패턴 |
|--------|------|
| 4 | §1 코루틴→UniTask 비대칭 (frame-budget yield 깜빡) |
| 5 | §2 `Func<UniTask>` → `Func<CT, UniTask>` 시그니처 강제 |
| 6 | §3 AsyncOperation 60줄 boilerplate → `.ToUniTask` 1줄 |

## 마이그레이션 체크리스트

- [ ] 옛 패턴이 자동 보장한 안전성 식별 (frame 분배, 자동 cancel, error 처리 등)
- [ ] 새 패턴이 동일 안전성을 자동 보장하는지 검증
- [ ] 자동 보장 안 되면 **시그니처/타입 강제**로 컴파일 타임 안전성 박제
- [ ] 라이브러리 helper(`.ToUniTask` 등) 활용으로 boilerplate 압축

## 참고

- [.claude/rules/unitask-async.md](../.claude/rules/unitask-async.md) — UniTask 10개 룰 (§3 frame-budget batching 직접 연계)
- [unitask-async-patterns.md](unitask-async-patterns.md) — UniTask 인시던트 카탈로그
- [overload-semantic-equivalence.md](overload-semantic-equivalence.md) — 오버로드 의미론 등가성
