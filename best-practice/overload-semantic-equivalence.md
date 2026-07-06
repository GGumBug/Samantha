[← README로 돌아가기](../README.md)

# 오버로드 의미론 등가성 — Overload Semantic Equivalence

기존 메서드에 **새 오버로드를 추가**할 때, 시그니처만 다른 게 아니라 **모든 부수효과(side effect)도 동일하게 복제**해야 한다. 컴파일이 통과해도 동작이 등가가 아니면 SSOT 위반.

## 인시던트 — `NodeCleared(Vector2Int)` IsSelectable 누락

2026-04-17 Hwaseo. 기존 `NodeCleared()`(무파라미터)는 `_currentNode`를 암묵 참조하면서 다음 부수효과 모두 수행:

```
1. node.IsCleared = true
2. node.IsSelectable = false        ← 핵심: 클리어된 노드는 재선택 불가
3. NodeClearedEvent 발행
4. outgoing edges Available 전이
5. PlayerData.SaveAsync()
```

리팩토링 중 명시 좌표 기반 오버로드 `NodeCleared(Vector2Int pos)`를 추가하면서 **2번(IsSelectable=false) 한 줄을 누락**. 결과: 클리어된 노드가 시각적으로 노란색을 유지(선택 가능 상태) → 사용자가 클리어된 노드를 다시 클릭하면 진입 시도 → 디스크 상태와 메모리 상태 불일치.

**컴파일은 통과**(타입 안전), **테스트는 부분 통과**(IsCleared 검증만 있었음), **시각 회귀는 플레이 테스트에서야 발견**.

## 핵심 원리

### "오버로드는 동의어"라는 묵시적 계약

호출자는 `NodeCleared()`와 `NodeCleared(pos)`가 **같은 일을 한다**고 기대한다. 시그니처가 다른 이유는 "어떤 노드인지 알려주는 방식"의 차이일 뿐, **수행할 작업의 차이가 아니다**.

이 계약이 깨지면:
- 호출자가 "어느 오버로드를 쓰느냐"에 따라 결과가 달라짐 → SSOT 붕괴
- 미래 개발자가 "왜 이 오버로드만 IsSelectable을 안 건드리지?" 추적에 시간 낭비
- 한쪽 오버로드만 호출되는 경로에서 부분 적용 버그 발생

### "핵심 한 줄만 복제"의 함정

리팩토링 시 "이 오버로드의 본질은 X 할당"이라고 단순화하면 부수효과가 시야에서 사라진다. **본질은 부수효과까지 포함한 전체 트랜잭션**임을 잊지 말 것.

## 검증 절차

### 1. 원본 부수효과를 diff로 나열

```csharp
// 원본 NodeCleared() 부수효과 (5개):
// 1. node.IsCleared = true
// 2. node.IsSelectable = false
// 3. NodeClearedEvent 발행
// 4. outgoing edges Available 전이
// 5. PlayerData.SaveAsync()
```

코멘트 또는 PR 설명에 명시. 머릿속에서만 추적 금지.

### 2. 신규 오버로드와 복제 매핑 표

| 부수효과 | 원본 `NodeCleared()` | 신규 `NodeCleared(pos)` | 일치 |
|----------|----------------------|--------------------------|------|
| IsCleared = true | O | O | OK |
| IsSelectable = false | O | **X** | **NG** ← 누락 발견 |
| Event 발행 | O | O | OK |
| outgoing 전이 | O | O | OK |
| SaveAsync | O | O | OK |

표로 정리하면 **누락이 즉시 시각적으로 드러남**. 리뷰어 검증도 쉬움.

### 3. 호출자 grep — 메서드 이름만

```
\.NodeCleared\(
```

파라미터 패턴(`\(\)` 같은 것) 검색 금지 — 호출자가 어느 오버로드를 쓰든 누락된 부수효과의 영향을 받는다. 이름만 grep하고 결과를 육안으로 분류.

### 4. 통합 우선 — 오버로드 자체 회피

가능하면 **오버로드 추가 대신 SSOT 단일 진입점으로 통합**:

```csharp
// 권장
public void NodeCleared(Vector2Int pos)
{
    var node = ResolveNode(pos);
    // ... 모든 부수효과 단일 본문에서 처리
}

// 비권장 — 오버로드 두 개 유지 시 복제 의무 영구화
public void NodeCleared() => NodeCleared(_currentNode.Position);
public void NodeCleared(Vector2Int pos) { /* ... */ }
```

위처럼 무파라미터 버전이 명시 버전을 호출하도록 wrapping하면 부수효과 복제 의무가 사라진다 (단일 본문). 단, 호출 타이밍이 다를 경우(`_currentNode` 갱신 직후 vs 이후)는 wrapping이 위험 — `unity-delegation.md`의 "현재 암묵 참조 API 이동" 체크리스트 참조.

## 위임 프롬프트 의무 항목

오버로드 추가 작업을 에이전트에 위임할 때 프롬프트에 반드시 포함:

- [ ] 원본 메서드의 부수효과를 diff/주석으로 나열
- [ ] 신규 오버로드가 모든 부수효과를 복제하는지 매핑 표 작성
- [ ] "핵심 할당 한 줄만 복제"는 거의 항상 버그라는 경고
- [ ] 가능하면 오버로드 추가 대신 단일 본문 + wrapper로 통합
- [ ] 호출자 grep을 **이름만** (`\.MethodName\(`)

## 안티패턴

### 1. 시그니처 비교만으로 등가 판정

```
"public void Foo() vs public void Foo(int x) — 파라미터 하나만 추가했으니 본질 동일"
```

→ 본문의 부수효과 비교 없는 자기 정당화. 이름이 같다고 등가가 아니다.

### 2. 테스트 통과 = 등가 판정

부수효과 중 테스트로 검증 안 되는 것(시각 상태, 디스크 저장, 외부 이벤트 구독자)은 누락되어도 테스트 Green. **테스트 Green ≠ 동작 등가**.

### 3. "나중에 통합" 미루기

오버로드를 두 개 유지하고 "나중에 SSOT로 통합" 미루면 복제 의무가 영구화되어 **모든 부수효과 추가 시마다 두 곳을 동시 수정**해야 한다. 한쪽만 빠지면 즉시 인시던트.

## 관련 문서

- [refactoring-lessons.md](refactoring-lessons.md) §12.5 — SSOT 단일 진입점 보존
- [node-lifecycle-patterns.md](node-lifecycle-patterns.md) — 노드 생명주기 부수효과 매트릭스
- [.claude/rules/unity-delegation.md](../.claude/rules/unity-delegation.md) — 리팩토링 위임 체크리스트
