[← README로 돌아가기](../README.md)

# 손으로 든 명부는 조용히 낡는다 — 완전성 장치의 목록은 검사 대상에서 파생한다

완전성·커버리지를 주장하는 장치(감사 테스트·허용 목록 검증자·매핑 표)가 **검사 대상 목록을 리터럴로 들고 있으면**, 대상이 늘어난 날 그 장치는 낡는다. 감사라면 **조용히 거짓 통과**하고, 허용 목록이라면 **정당한 새 항목을 거짓 차단**한다. Double Down 상점 각서 세션(2026-09-01)에서 감사가 막으려던 실수를 감사 자신이 못 보는 것을 실측.

## 1. 실측 — 같은 병 3자리

### 1-1. 감사 테스트의 하드코딩 명부 (조용한 거짓 통과)

`BgBalanceLoaderTests.Expectations_CoverEveryDeclaredBalanceProperty` 는 "모든 밸런스 속성이 동결됐는가"를 검사하는데, 볼 대상을 손으로 들고 있었다:

```csharp
private static readonly (string Group, Type Type)[] BalanceGroups =
{ ("Match", typeof(MatchBalance)), ("GoStop", ...), ("Settlement", ...) };
```

`BalanceSet` 에 `Shop` 축을 추가하며 이 배열을 잊자 **감사가 조용히 통과**했다. 누락이 "감사 통과"로 보여 신호가 0 — 감사가 막으려던 실수를 감사가 못 본다. 같은 파일의 `Load_DoesNotHandBackTheCodeSidePlaceholder` 도 같은 병이었다.

### 1-2. 허용 목록 if 사슬 (시끄러운 거짓 차단)

`StableSeedDeriver.ValidateStreamKey` 가 허용 키를 `if` 사슬로 나열 — `RandomStreamKey.Opponent` 추가 시 PlayMode 8건이 "Unknown replay stream key" 로 죽었다. `switch` 와 달리 `if` 사슬에는 완전성 검사가 없어 **컴파일러가 침묵한다** (2026-08-31 실측, [reports/double-down-ingame-handoff.md](../reports/double-down-ingame-handoff.md)).

### 1-3. 주석의 명부 (빨간불 장치 없음)

주석이 시트 키 목록을 손으로 들고 있던 세 번째 자리는 어떤 장치도 없어 이미 stale 상태로 발견됐다. 명부의 세 형태 — 코드 배열·if 사슬·주석 — 중 주석이 가장 조용하다.

## 2. 방향에 따라 실패 소음이 갈린다

| 명부의 역할 | 낡으면 | 소음 | 위험도 |
|---|---|---|---|
| **감사 대상 목록** (이만큼 검사한다) | 새 대상을 안 본다 | **0 — 초록 통과** | 최고 — 신호가 없다 |
| **허용 목록** (이것만 통과시킨다) | 정당한 새 항목 차단 | 시끄러움 — 즉시 빨간불 | 낮음 — 그날 고친다 |
| **주석 목록** (설명) | 그냥 거짓말 | 0 | 다음 독자를 오도 |

시끄러운 쪽은 낡은 날 잡히지만, 감사 목록의 부족은 **감사 통과가 곧 증상**이라 사람이 의심하지 않는 한 영원히 간다.

## 3. 처방 — 명부를 검사 대상 자신에서 파생

| 명부 형태 | 파생 수단 |
|---|---|
| 타입/프로퍼티 목록 | 대상 타입의 **공개 프로퍼티 리플렉션** (`typeof(BalanceSet).GetProperties()`) |
| enum 값 목록 | `Enum.GetValues` 전수 순회 |
| 분기 완전성 | `if` 사슬 대신 `switch` + default throw (컴파일러/analyzer 완전성) |
| 주석 목록 | 삭제하고 파생 코드를 가리키게 — 주석은 파생이 불가능한 명부 |

파생으로 바꾸는 순간 축을 더하면 **감사가 그 축을 요구**한다 — 누락이 초록이 아니라 빨강이 된다.

## 4. 파생 전환은 뮤테이션으로 검증

파생 코드 자체가 틀릴 수 있으므로, 전환 직후 **기대 행 하나를 제거해 빨간불이 켜지는지** 확인한다 — 켜지지 않으면 파생이 아직 명부를 다 세지 못하는 것. 뮤테이션 원복은 [.claude/rules/evaluation.md](../.claude/rules/evaluation.md) 뮤테이션 검증 절차 게이트 준수 — 미커밋 작업 위에서 `git checkout` 원복 금지.

## 종료 게이트

- [ ] 완전성을 주장하는 테스트·검증자에 **리터럴 배열/if 사슬 명부**가 있는가 — 있으면 1순위 의심
- [ ] 명부를 검사 대상 자신에서 파생했는가 (리플렉션 / `Enum.GetValues` / `switch` 완전성)
- [ ] 파생 전환을 뮤테이션으로 검증했는가 (기대 행 제거 → 빨간불)
- [ ] 열거·타입에 축을 더할 때 그 **타입명을 grep 해 나열 지점 전수** 확인했는가 — 검증자·매핑 표·직렬화 변환기가 상습 지점

## 관련 문서

- [second-producer-axis-drift.md](second-producer-axis-drift.md) — 축 추가 시 생산 지점 전수 (본 문서는 그 "검사 지점" 판)
- [stale-artifact-false-signal.md](stale-artifact-false-signal.md) — 판정자가 거짓말하는 조건을 함께 확인
- [golden-case-gate.md](golden-case-gate.md) — 커버리지 감사 표 선행
- [.claude/rules/evaluation.md](../.claude/rules/evaluation.md) — 뮤테이션 검증 절차 게이트
