[← README로 돌아가기](../README.md)

# 에디터 전용 검증은 런타임 가드가 아니다

`UnityEngine.Pool.ObjectPool<T>`의 `collectionCheck`는 **에디터/개발 빌드 전용**이다. 이중 반환(double release) 검사를 여기에 의존하면 릴리즈 빌드에서 무방비 — 같은 인스턴스가 풀에 두 번 들어가 두 소비자에게 중복 대여되는 데이터 오염이 조용히 발생한다.

## 인시던트 (2026-07-08 GameCore PoolService)

- 이중 반환 방어를 `ObjectPool(collectionCheck: true)`에 의존하는 설계 검토
- `collectionCheck`는 에디터 전용 — 빌드에서는 검사 자체가 수행되지 않음을 확인
- 런타임 가드를 별도 authoritative 상태(`entry.IsPooled`)로 분리 — Release 시 `IsPooled == true`면 거부

## 룰

1. **런타임 안전성이 필요한 검사를 에디터 전용 메커니즘에 위임 금지**. 에디터 전용 검사는 "개발 중 조기 발견" 보조 장치일 뿐, 빌드 방어선이 아니다.
2. **이중 반환 가드는 풀이 소유한 authoritative 상태가 담당** (예: `entry.IsPooled` 플래그). `collectionCheck`는 이 상태의 백업 검증으로만 사용.
3. 설계 검토 시 **"이 가드는 빌드에서도 살아있는가?"** 질문을 명시 검증.

## 에디터 전용 메커니즘 목록 (빌드 방어선 아님)

| 메커니즘 | 빌드 동작 |
|----------|----------|
| `ObjectPool<T>.collectionCheck` | 검사 생략 (에디터/개발 빌드만 수행) |
| `Debug.Assert` | `UNITY_ASSERTIONS` 미정의 시 조건 미평가 |
| `#if UNITY_EDITOR` 블록 | 코드 자체가 제거됨 |
| `[Conditional("UNITY_EDITOR")]` 메서드 | 호출 자체가 제거됨 |
| `OnValidate` | 에디터 전용 콜백 |

## 자가 점검

- [ ] 데이터 무결성/수명 가드가 위 표의 메커니즘에만 의존하고 있지 않은가?
- [ ] 런타임 가드 상태(SSOT)가 별도로 존재하는가?
- [ ] 에디터 전용 검사와 런타임 가드가 동일 조건을 검증한다면, 런타임 가드가 authoritative인가?

## 관련 룰

- [.claude/rules/engineering-constitution.md](../.claude/rules/engineering-constitution.md) — SSOT / 부수효과 가시화
