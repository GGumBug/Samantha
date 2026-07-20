[← README로 돌아가기](../README.md)

# BGDatabase enum 바인딩 — 필드 타입 3종·시트 어휘 계약·다형 컬럼 한계

BGDatabase 시트 컬럼을 C# enum 에 바인딩할 때 확정된 세 가지 교훈. Slice A 밸런스 스키마 임포트(2026-07-19~20, 개발 보드 카드 13.5~18)에서 실측·검증했다.

## 1. enum 필드 타입은 underlying type 별 3종

BGDatabase 의 enum 필드는 하나가 아니다 — C# enum 의 underlying type 에 따라 별도 필드 타입을 선택해야 한다.

| C# enum 선언 | BGDatabase 필드 타입 | 비고 |
|---|---|---|
| `enum Foo` (기본 = int) | `enum` | 기본 피커에 노출 |
| `enum Foo : short` | `enumShort` | |
| `enum Foo : byte` | `enumByte` | **기본 `enum` 필드 타입 피커에 안 보임** — 함정 |

함정: 메모리 절약 목적으로 `: byte` enum 을 선언하면 BG Editor 의 기본 `enum` 피커에서 해당 타입이 검색되지 않아 "바인딩 불가"로 오판하기 쉽다. `enumByte` 필드 타입을 선택해야 노출된다.

## 2. 시트 어휘 = enum 멤버 이름 계약 (변환 계층 0개)

BGDatabase 임포트의 enum 파싱은 `Enum.IsDefined` **정확 일치** — 대소문자·언더스코어가 다르면 파싱 실패.

- 계약: **시트 셀 어휘는 enum 멤버 이름 그대로(PascalCase) 기입**
- 효과: 임포터/로더에 매핑 테이블·string 변환 계층 0개 — 시트가 곧 SSOT
- 실사례: 소문자 snake_case 로 기입돼 있던 137셀을 PascalCase 로 일괄 변환해 임포트 통과 (2026-07-19)

계약 위반 신호: 임포트 코드에 `ToLower()` / `Replace("_", "")` / 별도 매핑 Dictionary 가 등장하면 시트 어휘 계약이 깨진 것 — 변환 계층을 늘리지 말고 시트 셀을 enum 이름으로 정규화한다.

## 3. 다형 컬럼은 enum 필드 바인딩 불가 — 로드 시점 typed 파싱

판별자 + 다형 값 컬럼 구조(예: Hand 시트의 `condition_type` 판별자 + `condition_value` 가 Category 값 또는 Tag 값)는 **단일 enum 필드로 바인딩할 수 없다** — 셀의 타입이 행마다 달라지기 때문.

해법 — string 유지 + 로드 시점 typed 파싱 fail-fast:

```csharp
// condition_type 판별자에 따라 정적 팩토리로 typed 파싱
// 잘못된 어휘는 fixture 구성 시점에 예외 — 런타임까지 전파 금지
HandCondition.ForCategory(categoryCell);   // CardCategory 정확 파싱
HandCondition.ForTag(tagCell);             // CardTag 정확 파싱
```

- 시트 컬럼은 string 으로 유지하되, **fixture/로드 구성 시점**에 판별자 기반 정적 팩토리로 typed 파싱
- 잘못된 어휘는 로드 시점 fail-fast — 게임플레이 중 발견되는 지연 실패 금지

기각한 대안 (YAGNI — 헌법 §5): 타입별 컬럼 분리 정규화(`condition_category` + `condition_tag`)는 ① `CardCategory` 에 None=0 부재로 "빈 값" 표현 불가 ② 행마다 절반이 빈 컬럼이 되는 시트 가독성 비용으로 기각.

## 임포트 위임 체크리스트

- [ ] `: byte` / `: short` enum 은 `enumByte` / `enumShort` 필드 타입 선택
- [ ] 시트 셀 어휘가 enum 멤버 이름과 정확 일치하는지(대소문자·언더스코어) 사전 sweep
- [ ] 임포트/로드 코드에 어휘 변환 계층(`ToLower` 등)이 생기면 시트 정규화로 회귀
- [ ] 판별자 + 다형 값 컬럼은 enum 바인딩 대신 로드 시점 정적 팩토리 typed 파싱 + fail-fast

## 관련 문서

- [bgdatabase-asset-reference.md](bgdatabase-asset-reference.md) — BGDatabase asset 참조 trade-off
- [sheet-batch-readback.md](sheet-batch-readback.md) — 시트 batch update 후 read-back 검증
- [.claude/rules/engineering-constitution.md](../.claude/rules/engineering-constitution.md) — §2 SSOT / §5 YAGNI
