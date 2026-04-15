[← CLAUDE.md로 돌아가기](../CLAUDE.md)

# 대규모 리팩토링 교훈 — 실전 체크리스트

Hwaseo 프로젝트의 결정론 런 시드 시스템 도입(38개 파일, 2026-04-15) 경험에서 도출한 교훈입니다. "전역 상태 제거", "결정론 보장", "대규모 인터페이스 도입" 유형의 리팩토링에 적용합니다.

## 1. 플랜 단계 — 전수 검색이 먼저

**절대 원칙**: 심볼·패턴을 "제거/대체"하는 리팩토링은 **플랜 작성 이전에** 전수 grep을 돌리고, 결과를 **분류 테이블**로 정리해야 합니다.

```
Grep("UnityEngine\.Random|Random\.Range", output_mode="content")
→ 각 호출을 [게임플레이 분기 / VFX / 시드 생성용 / 의도적 유지] 4개 카테고리로 분류
→ 플랜 파일에 테이블로 고정
```

**왜?** 플랜 작성 시 눈에 띄는 파일만 적으면 꼭 몇 개가 누락됩니다. Hwaseo 케이스에서는 `EnemyBrain`, `TargetResolver`, `BattleUnitRegistry`, `PlayerManager.PickWeighted`, `ShopPricingService`, `ShopBankService` 7개가 1차 플랜에서 누락되어 추가 배치로 마무리해야 했습니다.

## 2. 설계 단계 — "이중 안전망" 구조

결정론/재현성이 요구되는 시스템은 **두 겹의 보장**을 설계하세요:

1. **1차**: 결과 스냅샷을 디스크에 저장
2. **2차**: `Hash(seed, label, context)` 기반 서브시드로 결과 재생성

"스냅샷 삭제 후에도 동일 결과"를 테스트하지 않으면 1차만 동작하는 설계인지 2차까지 동작하는지 구분 못 합니다.

## 3. 해시 결정성 함정

- `string.GetHashCode()` — .NET 런타임/프로세스마다 다른 값
- `HashCode.Combine(...)` — 같은 이유로 비결정적
- **반드시 FNV-1a 또는 SHA-256 수동 구현을 사용**

## 4. 캐시 vs 재현성 — 상충 설계 주의

"서비스에서 RNG 인스턴스를 캐시하면 빠르지만, 같은 label로 재호출 시 **진행된 상태**가 반환되어 '스냅샷 삭제 후 재현' 시나리오가 깨집니다". 재현성 우선 서비스는 **매 호출마다 새 인스턴스 반환**이 원칙, 캐시는 명시적으로 금지하세요.

## 5. "새 객체 교체" 패턴의 필드 누락

`data.snapshot = factory.CreateSnapshot(...)` 류 코드는 **기존 필드 복사 누락**을 유발합니다. Hwaseo에서 `CreateRunStateSnapshot`이 `RunSeed`를 포함하지 않아 매 Capture마다 RunSeed가 0으로 리셋되는 버그가 있었습니다.

**처방**:
- 새 인스턴스 교체 직전에 **보존할 필드를 로컬 변수로 꺼내두고** 교체 직후 재대입
- 또는 `previousState`를 팩토리 인자로 받아 필드별 명시 복사

## 6. 방어 분기는 반드시 로깅

"`RunSeed==0`이면 새 시드 생성" 류의 안전망 분기는 **`Debug.LogWarning`을 반드시 동반**해야 합니다. 정상 플로우에서 트리거되면 결정론을 파괴합니다. 로그가 없으면 증상만 보이고 원인을 찾을 수 없습니다.

## 7. 두 버그가 서로를 가리는 경우

"매번 값이 바뀜" 증상은 종종 **중첩된 버그**입니다. 한 버그를 수정해도 다른 버그가 증상을 유지시키면 수정 효과가 안 보입니다.

**처방**: 단일 변화 포인트마다 `Debug.Log` 추가 → 값의 변화 단계를 눈으로 추적 → 어느 단계에서 값이 달라지는지 특정 → 역추적으로 원인 발견.

Hwaseo에서는 3개 버그 중첩:
1. `SetCurrentNodeSelectedEnemySpawnDataId` 디스크 저장 누락
2. `CreateRunStateSnapshot`의 RunSeed 복사 누락
3. `TryLoad` 최초 생성 경로의 `InitializeRunRngFromLoadedData` 미호출

각각을 고친 후에야 결정론이 완성됐습니다.

## 8. Setter 주입 vs 생성자 주입

싱글턴·풀 객체에서 **생성 시점에 DI 파라미터가 아직 확정되지 않은 경우**(예: act/row가 맵 로드 전에는 없음)는 **Setter 주입 + Fallback label**이 더 안전합니다.

```csharp
public void SetRng(IRunRandom rng) { _rng = rng; }
private IRunRandom GetRng() => _rng ??= RunRngService.Instance.ForSubsystem("deck_fallback");
```

Fallback label을 따로 두면 "주입이 실제로 호출되는지"를 운영 중에 감지할 수 있습니다.

## 9. 에이전트 위임 — 배치 크기 5개 한계

단일 에이전트에 10+ 항목을 한 번에 주면 **중단**됩니다(컨텍스트/턴 제한). Hwaseo의 첫 Sonny 위임(S1~S13 13개)이 S12 분석 중 종료된 경험이 있습니다.

**처방**: 13개 항목을 4개 배치(2/5/4/2)로 분할 후 병렬 투입. 각 배치의 수정 파일이 disjoint면 race 없이 병렬 안전.

## 10. 백그라운드 에이전트 "completed" 신뢰하지 말 것

`status=completed`는 프로세스 종료만 의미합니다. 최종 보고가 "중간 작업 메시지"로 잘려 돌아오면 실제로 작업을 다 안 했을 가능성이 높습니다.

**처방**: 에이전트 종료 직후 **수정 대상 파일을 직접 grep**으로 교차 검증. 예: `UnityEngine\.Random` 잔재 검색, 신규 필드 존재 확인.

## 11. 경계 충돌 — 누가 호출부를 고치나?

두 에이전트가 같은 인터페이스를 건드릴 때 "생성자 변경" vs "호출부 수정" 책임이 누구에게도 명시되지 않으면 떨어집니다. Hwaseo의 `EncounterRandomSelector` 생성자가 변경됐지만 `EncounterManager`의 호출부 수정이 누락되어 컴파일 에러 발생.

**처방**: 플랜에 "A는 정의, B는 배선"을 문자 그대로 적고, 각 에이전트 프롬프트에 상대 에이전트가 건드리는 파일을 **금지 목록**으로 명시.

## 12. 메서드 시그니처 변경 시 — "메서드 이름만 grep"

파라미터 제거·추가 시 **파라미터 값 기준 grep은 반드시 누락을 만든다**. 정규식은 "내가 상상한 패턴만" 찾기 때문:

- `,\s*false\s*\)` 검색 → 단일 인자 `Foo(false)` 누락
- `(false)` 검색 → `Foo(true)` 호출 누락
- 두 번째 인자 검색 → 명명 인자 `Foo(saveImmediately: false)` 누락
- 한 줄 형태 검색 → 줄바꿈 인자 `Foo(\n    false)` 누락

**2026-04-15 PlayerDataManager 리팩토링에서 같은 종류 실수가 2차례 연속 발생** (1차: 6곳 누락, 2차 수정 후: `MarkBattleTutorialCompleted(true)` 누락).

**유일하게 안전한 패턴 — 메서드 이름 자체만 grep**:
```
\.MarkBattleTutorialCompleted\(
```
결과를 **육안으로 검토**하여 괄호 안 인자 수가 새 시그니처와 맞는지 확인. 파라미터 값(true/false/변수)은 **전혀 검색하지 말 것**.

복수 메서드는 파이프로 1회 grep: `\.Foo\(|\.Bar\(|\.Baz\(`

Unity `[SerializeField]` 필드 이름 변경 시 저장값이 유실되므로 `[FormerlySerializedAs("oldName")]` 부착은 별도 필수 절차.

## 13. 추출(Extract) 리팩토링의 책임 매핑

인라인 코드를 유틸/메서드 호출로 **추출**할 때 **컴파일 성공은 동작 동등성을 보장하지 않는다**. 컴파일러는 로직 동등성을 검증하지 못하므로, 인라인이 갖고 있던 **모든 책임**이 추출된 곳에 옮겨졌는지 수동 검증 필수.

**2026-04-15 RoguelikeMap 회귀 사례**: `RoguelikeMapGenerator.GetRandomLocationByWeight`의 인라인 구현을 `LocationWeightUtil.GetRandomLocation` 호출로 교체했으나, 인라인이 수행하던 `minFloor/maxFloor` 필터링 책임이 유틸로 **이동하지 않고 사라짐**. Generator의 `validWeights` 사전 필터는 "0개 체크"로만 쓰이는 상태로 방치되어 **3층에 Elite가 등장**하는 회귀 버그가 플레이 테스트에서야 발견됨.

### 추출 전 책임 목록화

인라인 코드의 다음 책임을 목록화:
- 입력 변환
- 필터링 / 검증
- 추첨 / 계산
- 폴백 처리
- 부수 효과 (로깅 등)

### 추출 후 책임 매핑

각 책임이 추출 후 어디로 이동했는지 확인:
- 유틸 내부로 이동?
- 호출자 측에 남음?
- **사라지지 않았는가?** ← 회귀 버그의 원흉

### 위험 신호 패턴

- "이전 코드가 받던 파라미터를 새 코드가 안 받는다" → 그 파라미터의 효과가 사라졌을 가능성
- "이전 호출자가 사전 필터를 했는데 새 유틸이 같은 필터를 갖지 않는다" → 책임 누락
- "리팩토링 직후 코드가 더 단순해 보인다" → 단순화가 아니라 **기능 누락**일 가능성

### 추출 위임 프롬프트 체크리스트

에이전트 위임 시 명시:
- [ ] 추출 전 인라인 코드의 모든 책임 목록화
- [ ] 추출 후 각 책임이 어디로 이동하는지 명시
- [ ] "기능 동등성 보존" 명시적 요구
- [ ] 의도된 동작 시나리오 1-2개 (예: "minFloor=6인 LocationType은 actLevel=3에서 추첨되지 않아야 함")

## 14. Unity 시각 버그 — Inspector 우선 진단

UI 미표시·반투명·색상 이상 등 시각 버그는 **코드/asset 수정 전에 Inspector를 먼저 의심**한다. 2026-04-15 Hwaseo에서 두 건의 사례 모두 코드·anim을 여러 번 잘못 추적한 후 Inspector에서 해결됨.

### 진단 우선순위 (위→아래)

1. **Inspector 컴포넌트 설정값** — Button(Color Tint/Disabled Color), Image(Color/Material), CanvasGroup(alpha/interactable), Outline(effectColor)
2. **SerializeField 할당 상태** — 비어 있는 필드
3. Animator Controller / .anim 키프레임
4. Material/Shader 설정
5. 코드의 색상/알파 조작

대부분 **상위 1-2개**에서 해결됨.

### 대표 함정: Button Disabled Color

- `interactable = false` 시 Button은 **Disabled Color**로 자동 전환
- 기본 Disabled Color = `(0.78, 0.78, 0.78, 0.5)` — **알파 0.5 반투명이 디폴트**
- "버튼 비활성화 시 반투명" 증상 = 거의 100% 이 설정

### 행동 원칙

- 같은 가설(예: "알파 조작")을 2회 이상 추적했는데 진전 없으면 **중단하고 사용자에게 Inspector 확인 요청**
- **Fail Loud**: 코드 폴백(없으면 기본값 생성)은 런타임 동적 생성이 필요한 경우만. 고정 프리팹에는 Inspector 정정이 정석 — 폴백은 버그를 숨길 뿐
- `.anim` 파일을 함부로 빈 클립으로 만들지 말 것(원인이 Inspector면 부수 피해)

## 15. 세션 종료 전 반드시 grep 전수 검증

Phase 마지막에 한 번 더:
```
Grep("[제거 대상 패턴]", path="Assets/Scripts")
```
잔재가 남아있으면 한 번에 처리. 컴파일이 통과했다고 결정론이 작동한다는 보장 없음. **타입 검증과 동작 검증은 별개**.
