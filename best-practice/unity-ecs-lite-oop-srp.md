[← CLAUDE.md로 돌아가기](../CLAUDE.md)

# Unity ECS-Lite와 OOP SRP — Composite Prefab 정공

Unity의 GameObject + Component 패러다임은 **ECS-lite (Entity-Component)** 다. 한 GameObject(entity)가 여러 Component를 갖고, 각 Component는 단일 책임을 진다. 이 구조는 OOP **SRP (Single Responsibility Principle)** 와 자연스럽게 합치 — 단일 클래스에 책임 묶지 말고 **Composite prefab + 별개 컴포넌트 + 별개 인터페이스**가 정공.

## 핵심 원리

| 차원 | OOP SRP | Unity ECS-lite |
|------|---------|----------------|
| 책임 단위 | 클래스 | Component (MonoBehaviour) |
| 조합 단위 | 인터페이스 + DI | GameObject + 여러 Component |
| 합치점 | 한 클래스 = 한 책임 | 한 Component = 한 책임 |

**한 GameObject 안에 여러 Component를 배치**하면 OOP SRP를 자동 강제. 단일 클래스에 인터페이스 여러 개 implement는 책임 묶음.

## 안티패턴 — 단일 클래스에 여러 인터페이스 묶기

```csharp
// 책임 묶음 — 페이드 + 로딩 진행률 + 메시지 표시 모두 한 클래스
public class UILoadingScreen : MonoBehaviour, IFader, ILoadingProgress, IMessageDisplay
{
    public void Fade(float alpha) { /* ... */ }
    public void SetProgress(float p) { /* ... */ }
    public void ShowMessage(string m) { /* ... */ }
}
```

**문제**:
- 변경 이유 3개 (fade 로직 변경, 진행률 표시 변경, 메시지 포맷 변경) — SRP 위반
- 테스트 시 의존성 분리 불가
- 다른 화면에서 fade만 재사용 불가

## 정공 — Composite Prefab + 별개 컴포넌트 + 별개 인터페이스

```csharp
// 한 책임 = 한 컴포넌트
public class UIScreenFader : MonoBehaviour, IFader
{
    public async UniTask FadeAsync(float alpha, CancellationToken ct) { /* ... */ }
}

public class UILoading : MonoBehaviour, ILoadingProgress
{
    public void SetProgress(float p) { /* ... */ }
}

public class UIMessageDisplay : MonoBehaviour, IMessageDisplay
{
    public void ShowMessage(string m) { /* ... */ }
}
```

Prefab 구조:
```
LoadingScreen (GameObject)
├── UIScreenFader   (Component)
├── UILoading       (Component)
└── UIMessageDisplay (Component)
```

**이점**:
- 변경 이유 분리 — fade 로직 변경 시 UIScreenFader만 수정
- 다른 화면에서 UIScreenFader prefab만 가져와 재사용
- `GetComponent<IFader>()` 로 의존성 분리 테스트 가능
- Inspector 편집 단위가 책임 단위와 일치

## 본 세션 사례 — 옵션 X 채택

LoadingScreen prefab 설계 시:

| 후보 | 패턴 | 평가 |
|------|------|------|
| 옵션 A | UILoadingScreen 단일 클래스 (Fade + Progress + Message) | SRP 위반 |
| 옵션 X | UIScreenFader + UILoading 같은 prefab 별개 컴포넌트 | **채택** |

옵션 X가 SRP + ECS-lite 합치 — Inspector에서 책임별 조립, 다른 prefab 재사용 가능.

## 적용 트리거

다음 상황에서 Composite 분리 검토:

- 단일 MonoBehaviour 클래스가 **인터페이스 2개 이상 implement**
- 단일 클래스에 **책임 단어 2개 이상** (예: "Loader + Display", "Fader + Progress")
- 같은 prefab 안 한 컴포넌트의 **일부 기능만 다른 prefab에서 재사용**하고 싶을 때

## 분리 회피 (YAGNI)

다음 케이스는 단일 클래스 유지가 더 단순:

- 인터페이스 1개만 implement
- 책임이 명확히 1개 (단어 1개로 표현 가능)
- 다른 prefab에서 일부 재사용 의도 없음
- 분리 시 호출 사슬만 길어지고 응집도 감소 (헌법 §0 메타 원칙)

## 참고

- [solid-unity-principles.md](solid-unity-principles.md) — SOLID Unity 적용 카탈로그
- [.claude/rules/engineering-constitution.md](../.claude/rules/engineering-constitution.md) — SRP 회색 지대 트레이드오프 정책
