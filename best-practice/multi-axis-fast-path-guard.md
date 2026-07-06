[← README로 돌아가기](../README.md) | [engineering-constitution.md](../.claude/rules/engineering-constitution.md)

# Multi-Axis Fast-Path Guard — 시간축 다른 invariant 합성 가드 패턴

UI 트랜지션·상태 머신·라이프사이클 작업에서 "fast path" (작업 생략 / 단순화 분기) 가드를 작성할 때, **시간축이 다른 boolean invariant 들을 단일 AND 가드로 합치는** 패턴. 한 축만 검증하면 race / 시각 회귀 발생.

## 문제 정의

같은 방향 transition 이 연속 호출되면 시각적 시그널이 없어 UX 가 어색해진다. 예: 튜토리얼 가이드 패널이 왼쪽에서 들어오는 step 2개 연속 → 사용자는 "패널이 다시 들어왔는지 / 내용만 바뀐 건지" 구분 불가.

순진한 해결책:

```csharp
// ❌ 단일 축 가드 — race 발생
public async UniTask ShowFromAsync(SlideDirection from, CancellationToken token)
{
    if (_slideFrom == from)   // 같은 방향이면 fast path
    {
        UpdateContent();
        return;
    }
    await PlayFullTransition(from, token);
}
```

문제: panel 이 **현재 보이는지** (`gameObject.activeSelf`), **Hide tween 이 진행 중인지** (`_isHideInProgress`) 모르고 같은 방향이라는 이유만으로 content 만 갱신 → 안 보이는 panel 에 content 만 바뀌고 사용자는 아무 시그널도 못 봄.

## 권장 패턴 — 3-tuple AND 가드

```csharp
public async UniTask ShowFromAsync(SlideDirection from, CancellationToken token)
{
    bool isSameSide        = (_slideFrom == from);
    bool isActive          = gameObject.activeSelf;
    bool isHideInProgress  = _isHideInProgress;

    if (isSameSide && isActive && !isHideInProgress)
    {
        // Fast path — 보이는 상태 + 같은 방향 + 안정 상태
        UpdateContent();
        return;
    }

    await PlayFullTransition(from, token);
}
```

## 각 boolean 의 시간축 invariant 분류

| boolean | 시간축 | 변화 trigger | 단일 사용 시 race 시나리오 |
|---------|--------|--------------|---------------------------|
| `isSameSide` | 도메인 상태 (SSOT) | `SetSlideFrom` 호출 | 안 보이는 panel 에 content 만 바뀜 |
| `isActive` | Unity 라이프사이클 | `SetActive` / OpenUIAsync | Hide 중인데 fast path 발동 → tween 무시 |
| `!isHideInProgress` | UniTask 비동기 작업 | HideAsync 시작/완료 | 첫 Show 인데 isActive=false → 시각 효과 0 |

**핵심**: 세 invariant 가 각자 다른 시간 축 (런타임 상태 / GameObject 라이프 / 비동기 작업) 에서 변화. 단일 축 가드로는 부족, AND 결합 필수.

## Multi-axis 가드의 정석

> 시간축이 다른 invariant 를 단일 가드로 합치면 안 되는 게 아니라, **반드시 모든 축을 명시적으로 합쳐야 한다**.

각 축을 누락하면 race. 코드 리뷰 시 fast path 발견하면 **"이 가드가 검증하는 시간축이 몇 개인가?"** 를 명시 질문.

## Caller-Callee 협업 — Enabler 책임 분리

Fast path 가드는 callee 만으로 부족. **Caller 가 invariant 를 깨뜨리면 가드가 무효화**.

### 사례 — TutorialFlowController.HideStep

```csharp
// ❌ Caller 가 매번 Hide 호출 → callee fast path enabler 가 작동 못 함
async UniTaskVoid OnActionButton()
{
    await HideStep(token);          // 다음 step 도 같은 방향인데 매번 Hide
    await ShowStep(nextStep, token);
}
```

```csharp
// ✓ Caller 가 advance type 분기 → fast path enabler
async UniTaskVoid OnActionButton()
{
    if (_currentStep.AdvanceType == AdvanceType.Next && nextStep.SlideFrom == _currentStep.SlideFrom)
    {
        // 같은 방향 다음 step → Hide 생략, ShowFromAsync 내부 fast path 활용
        await ShowStep(nextStep, token);
    }
    else
    {
        await HideStep(token);
        await ShowStep(nextStep, token);
    }
}
```

**룰**: Fast path 가드는 callee 가 가지지만, **enabler 책임은 caller 에게도 있음**. 시각 회귀 진단 시 callee 가드 검증만으로 부족, **caller flow 도 grep 의무**.

## 진단 체크리스트

시각 회귀 / 트랜지션 어색 발생 시:

- [ ] Callee fast path 가드의 시간축 개수 확인 (단일 축이면 race 후보)
- [ ] 각 invariant 의 변화 trigger 식별 (런타임 / Unity / 비동기)
- [ ] Caller flow grep — fast path enabler 호출 패턴이 invariant 깨뜨리는지
- [ ] AdvanceType / NavigationType 같은 caller hint 가 있는가? 있다면 분기로 enabler 분리

## 사용자 시니어 통찰 박제

> "AdvanceType 이 Next 면 그냥 Hide 하지 않고 내용만 바꾸면 됨. 가드는 callee 가 가지지만 enabler 는 caller 가 가져야 fast path 가 실제로 발동돼."

— 본 세션 사용자 회고, 2026-05-14. callee 가드 작성 후 enabler 누락으로 fast path 가 실제 코드 경로에 도달 못 한 사례 → caller-callee 협업 룰 박제.

## 본 세션 박제 근거

- `23e0f88e` UITutorialGuidePanel — UIPanelSlider 위임 + same-side fast path (3-tuple AND 가드)
- `646ff83b` TutorialFlowController — onActionButton 람다 HideStep 조건 정정 (AdvanceType.Next 시 fast path enabler)

## 관련 문서

- [ui-transition-prefab-convention.md](ui-transition-prefab-convention.md) — prefab=Start 컨벤션
- [ui-visibility-two-layer-srp.md](ui-visibility-two-layer-srp.md) — 2-layer SSOT 분리
- [race-fix-meta-patterns.md](race-fix-meta-patterns.md) — Unity race 메타 패턴 (시간축 분리 미러링)
- [unitask-async-patterns.md](unitask-async-patterns.md) — `_isHideInProgress` 같은 재진입 atomicity 플래그
- [.claude/rules/engineering-constitution.md §2-1 클래스 불변식 캡슐화](../.claude/rules/engineering-constitution.md)
