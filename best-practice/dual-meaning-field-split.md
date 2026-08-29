[← README로 돌아가기](../README.md)

# 의미 겸직 필드 — 두 질문에 답하는 필드는 갈라지는 날 조용히 틀린다

한 필드가 **판정 사실**("지금 이런 상태다")과 **후속 계획**("그래서 이렇게 할 것이다")을 동시에 뜻하면, 둘이 늘 같이 움직이는 동안에는 아무 문제가 없다. 규칙이 바뀌어 **둘이 갈라지는 날** 코드는 틀린 쪽을 고르고, 필드는 여전히 하나이므로 **컴파일러가 침묵한다**. Double Down 턴 엔진 재구성(2026-08-29) 실측 — `IsChoicePending` 이 "바닥에 같은 달이 2장이다"(사실)와 "그래서 선택을 물을 것이다"(계획)를 겸직했고, 룰 변경으로 "2장이지만 묻지 않는" 경우가 생기자 오판했다.

## 1. 식별 — 이름이 두 질문에 답하는가

필드 이름을 두 질문에 각각 넣어 본다. **둘 다 자연스러운 답이 되면 겸직**이다.

1. *사실 질문* — "지금 무엇이 참인가?"
2. *계획 질문* — "그래서 무엇을 할 것인가?"

`IsChoicePending` 은 둘 다 답이 된다("짝이 2장이다" / "선택 UI 를 띄운다"). 상습 형태:

| 형태 | 겹치기 쉬운 두 의미 |
|---|---|
| `Is*Pending` / `Is*Required` | 조건 성립 ↔ 후속 절차 예약 |
| `Should*` / `Needs*` | 판정 결과 ↔ 행동 지시 |
| `Has*` 를 연출 분기 키로 사용 | 보유 사실 ↔ 표시 여부 |
| `*Enabled` | 기능 활성 ↔ 화면 노출 |

## 2. 왜 조용한가 — 겸직은 타입을 바꾸지 않는다

축을 **더하거나 빼면** 도구가 말해 준다. 더하면 컴파일러가 생산 지점을 지목하고([second-producer-axis-drift.md](second-producer-axis-drift.md)), 빼면 읽기 지점이 컴파일 에러나 grep 으로 드러난다([implicit-proxy-state-removal.md](implicit-proxy-state-removal.md)).

겸직은 **아무것도 더하지도 빼지도 않는다**. `bool` 하나가 그대로 `bool` 하나다. 달라지는 것은 사람 머릿속의 의미뿐이라 컴파일·테스트·grep 어디에도 신호가 없고, 갈라진 뒤 **행동으로만** 드러난다.

## 3. 처방 — 두 번째 의미를 별도 축으로 선언

겸직을 발견하면 **의미를 나누어 각각 이름을 준다**. 저장소 선례: `CardsCapturedStep.SettlesTurnLoot` — "카드를 획득했다"(사실)와 별개로 "이 스텝이 턴 전리품을 확정한다"(계획)를 독립 축으로 선언해, 획득이 일어나도 정산하지 않는 경우를 표현할 수 있다.

- **사실 축은 계산으로 유지** — 입력에서 유도되는 값이므로 SSOT 는 계산 쪽에 둔다
- **계획 축은 결정 결과로 명시** — 사실에서 자동 유도하지 말고 결정 지점에서 채운다
- 나눈 직후 **한쪽만 참인 케이스를 테스트로 동결** — 그 케이스가 없으면 다음 사람이 "둘은 같다"며 다시 합친다
- 필드를 나눌 수 없으면(직렬화 호환 등) 읽는 쪽마다 **어느 의미로 읽는지 드러나는 래퍼 프로퍼티**를 두어 주석 대신 코드로 갈라 놓는다

## 4. 축 4부작에서의 자리

| 방향 | 세는 대상 | 신호를 주는 주체 | 문서 |
|---|---|---|---|
| 축 **추가** | 생산 지점 전수 | 컴파일러(필수 인자) | [second-producer-axis-drift.md](second-producer-axis-drift.md) |
| 축 **제거** | 읽기 지점 전수 | 사람의 grep | [implicit-proxy-state-removal.md](implicit-proxy-state-removal.md) |
| 값 공간 **충돌** | sentinel 변환 지점 | 간헐 재현 | [sentinel-anti-pattern.md](sentinel-anti-pattern.md) |
| 의미 **겸직** | 두 의미가 갈라지는 케이스 | **없음** — 행동으로만 | 본 문서 |

넷 중 신호가 가장 약한 것이 겸직이다. 그래서 처방도 사후 탐지가 아니라 **작명 시점의 규율**이다.

## 종료 게이트

- [ ] 새 `bool`·enum 필드를 만들 때 §1 의 두 질문을 넣어 봤는가
- [ ] 겸직이면 두 축으로 나누고 각각 이름을 줬는가
- [ ] **한쪽만 참인 케이스**가 테스트로 동결됐는가
- [ ] 룰·사양 변경 리뷰에서 "이 변경으로 갈라지는 겸직 필드가 있는가"를 확인했는가

## 관련 문서

- [second-producer-axis-drift.md](second-producer-axis-drift.md) — 축 추가 시 생산 지점 전수
- [implicit-proxy-state-removal.md](implicit-proxy-state-removal.md) — 축 제거 시 읽기 지점 전수
- [sentinel-anti-pattern.md](sentinel-anti-pattern.md) — 값 공간 sentinel 충돌
- [.claude/rules/engineering-constitution.md](../.claude/rules/engineering-constitution.md) — §2 SSOT
