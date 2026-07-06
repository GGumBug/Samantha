[← README로 돌아가기](../README.md) | [engineering-constitution.md](../.claude/rules/engineering-constitution.md)

# Dead Stub 안티패턴 — 비동기 stub 격하 회피

비어 있는 비동기 메서드(`await UniTask.CompletedTask` / 빈 본문)를 **호출자가 모두 결과 무시**(`.Forget()`, `_ = ...`)하면서 호출하고, 진짜 부수효과는 **다른 경로**에서 처리되고 있다면 — 이 메서드는 채울 게 아니라 **통째로 제거**한다.

## 인시던트 — `Settings.ChangeLocale` stub

2026-05-07 Hwaseo `feature/remove-legacy-localization`. `Settings.cs`에 다음 패턴 잔존:

```csharp
private async UniTask ChangeLocale(LocaleType localeType)
{
    await UniTask.CompletedTask;   // 본문 없음
}
```

호출자 2곳 모두 결과 무시 + 직후 다른 경로에서 진짜 일 처리:

```csharp
Instance.ChangeLocale(value).Forget();
Instance._locale = value;                                  // 실제 상태 변경
LocaleChanged?.Invoke(...);                                // 실제 알림
```

Locale 적용 흐름은 `SettingsLocaleProvider` → `LocalizationDispatcher.OnLocaleChanged` → `FlushAsync`로 이미 동작 중. `ChangeLocale` stub은 **레거시 마이그레이션 잔재** — 채울 책임이 다른 곳으로 이전된 후에도 stub이 살아남음.

**처방**: 메서드 + 호출 2곳 + 미사용 `using Cysharp.Threading.Tasks` 제거. 동작 변화 0건. 헌법 §5(Dead Path 우선 검증) 적용 사례.

## 식별 시그널 (3가지 동시 충족 시 Dead Stub 확정)

1. **본문이 비어 있음**: `await UniTask.CompletedTask` / `return Task.CompletedTask` / `{ }` 단독
2. **호출자 전수가 결과 무시**: `.Forget()`, `_ = call(...)`, await 없음, 반환값 미할당
3. **다른 경로에서 진짜 부수효과 처리 중**: 같은 클래스/모듈/인접 라인에서 실제 상태 변경·이벤트 발행이 별도 진행

세 신호가 모두 켜지면 stub은 **잔재**로 판정. 한두 개만 켜지면 기능 누락 의심으로 채우기 검토.

## 결정 트리

```
호출자가 결과를 사용하는가?
├─ Yes  → 채워라 (진짜 누락된 구현)
└─ No
   └─ 다른 경로에서 진짜 일이 처리되고 있는가?
      ├─ Yes → 통째로 제거 (Dead Stub 확정)
      └─ No  → 기능 누락 의심, 사용자 확인 후 채우기
```

## 왜 채우기가 아니라 제거인가

- **SSOT 위반 회피**: stub을 채우면 진짜 경로(`SettingsLocaleProvider` 등)와 **두 곳에서 같은 일** → SSOT 붕괴
- **YAGNI**: 호출자 전수가 결과 무시하면 그 추상화는 사용처 0 — 인터페이스 비용만 부담
- **거짓 안전감**: stub이 살아 있으면 "여기서 처리되겠지" 잘못된 멘탈 모델을 강화 → 다음 합류자 진단 비용 증가
- **컴파일 통과 ≠ 의미 있음**: 비어 있는 비동기는 타입은 맞지만 **계약은 거짓** (이름이 약속한 일을 안 함)

## 안티패턴: "일단 채우자"

stub 발견 시 본능적으로 본문을 채우려는 충동을 거부한다. **먼저 호출자 grep**으로 결과 사용 여부 + 진짜 경로 존재 여부 확인. 마이그레이션 잔재인 경우 채우면 SSOT가 두 곳으로 분산.

## 자동 검증 grep

```
# 비어 있는 UniTask stub 후보
grep -rEn "async UniTask\w*\s+\w+\([^)]*\)\s*\{\s*await UniTask\.CompletedTask;?\s*\}"

# .Forget()으로만 호출되는 메서드 후보
grep -rEn "\.\w+\([^)]*\)\.Forget\(\)"
```

두 결과의 교집합 = Dead Stub 강력 후보.

## 관련 문서

- [.claude/rules/engineering-constitution.md §5](../.claude/rules/engineering-constitution.md) — 오버엔지니어링 안티패턴 (Dead Path 우선 검증)
- [refactoring-lessons.md](refactoring-lessons.md) — 일반 리팩토링 교훈
- [unitask-async-patterns.md](unitask-async-patterns.md) — UniTask 인시던트 카탈로그
