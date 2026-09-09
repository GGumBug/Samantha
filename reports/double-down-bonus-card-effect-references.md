[← README로 돌아가기](../README.md)

# 보너스 카드 구현 참고 — Balatro 조커 · Slay the Spire 파워/렐릭의 효과 구현법

2026-09-09 조사. 대상은 Double Down 「보너스 피 설계」(Balatro 조커 자리)의 **구현 계획**이고, 비교 기준은 이미 완성된 도메인 효과 엔진(`EffectVocabulary`·`EffectInterpreter`·`EffectChargeLedger`, 카드 45·48)이다. 결론부터: **도메인은 두 원작과 견주어 v1 범위에서 부족한 축이 없고, 비어 있는 것은 표현 계층(발화 연출·슬롯 UI)이다.** 원작들이 그 자리를 어떻게 푸는지가 이 문서의 요지다.

## 1. Balatro — 컨텍스트 하나로 묶은 단일 함수

Steamodded 공식 문서([Calculate Functions](https://docs.smods.dev/API%20Documentation/Calculate-Functions), [SMODS.Joker](https://docs.smods.dev/Game%20Objects/SMODS.Center/SMODS.Joker/)) 기준.

**선언 = 데이터 필드 + 코드 한 함수.** 조커는 `SMODS.Joker{ key, rarity, cost, blueprint_compat, config = {extra = ...}, calculate = function(self, card, context) ... end }` 로 선언된다. 희귀도·가격·복사 가능 여부는 **데이터**, 효과는 **코드**(Lua 클로저)다. 낱장의 가변 상태(스케일링 카운터)는 `card.ability.extra` 에 산다.

**훅 = 컨텍스트 플래그.** 훅마다 메서드를 두지 않고 `calculate` 하나가 모든 순간에 불리며, `context.joker_main`·`context.individual`·`context.end_of_round` 같은 플래그로 "지금이 어느 순간인가"를 가른다. 컨텍스트가 40개를 넘는다. 문서가 못 박는 함정 — **"calculate 는 손 한 번에 여러 번 불리므로 모든 효과는 컨텍스트 가드 안에 있어야 한다."**

**평가 순서 (스코어링).** `before` → `initial_scoring_step` → **낸 카드 좌→우**(`main_scoring` → `individual` → `repetition`, 리트리거는 이 블록을 반복) → **조커 좌→우**(`pre_joker` → `joker_main` → `other_joker` → `post_joker`) → `final_scoring_step` → `destroy_card` → `after`. 칩·배수는 **만나는 순서대로 누산**되므로 조커의 좌우 배치가 곧 전략이다(×배수 조커를 오른쪽에).

**연산 = 반환 테이블.** `{ chips = 50 }`, `{ mult = 4 }`, `{ xmult = 1.5 }`, `{ dollars = 3 }`, `{ repetitions = 1 }`, `{ saved = true }`, `{ remove = true }`. 연출도 같은 테이블로 제어한다 — `message`·`colour`·`sound`·`message_card`(팝업을 띄울 카드)·`no_juice`(흔들림 끄기). **효과의 결과와 그 연출이 한 반환값에 실린다.**

**연출 문법** ([Blake Crosley, Balatro: Juicy Feedback](https://blakecrosley.com/guides/design/balatro)): 발화는 좌→우 **순차**로, 발화한 조커가 **튀고**(juice), 그 자리에 기여분이 **팝업**되며, 러닝 토탈이 갱신된다. 색이 곧 라벨 — 파랑 = 칩, 빨강 = 배수, "라벨 없이 색이 라벨이다". 강도는 크기에 비례 — 흔들림 0.2/0.3/0.5s, 5장이면 음 높이 C·D·E·F·G 상승. 원칙: **"feedback should be proportional to significance."**

**데이터로 표현되는가.** [Joker Forge](https://github.com/Jaydchw/joker-forge)(웹 조커 빌더)가 바닐라 조커 대부분을 **Trigger › Condition › Effect** 3항으로 표현한다 — 트리거 22종 · 조건 28종(AND/OR 그룹) · 효과 43종, 가변 상태는 "Modify Internal Variable" 효과. 원작은 낱장당 코드지만, **그 위에 데이터 층을 얹는 것이 가능하고 실제로 쓰인다**는 실증이다.

## 2. Slay the Spire — 훅 메서드 + 액션 큐

[BaseMod Hooks](https://github.com/daviscook477/BaseMod/wiki/Hooks), [BasicMod Powers](https://github.com/Alchyr/BasicMod/wiki/Powers-(Buffs)), [MiniSTS](https://github.com/iambb5445/MiniSTS), [모딩 튜토리얼](https://linuxtut.com/en/f61d9f3553e2d045aa2e/) 기준.

**훅 = 가상 메서드.** 파워(`AbstractPower`)와 렐릭(`AbstractRelic`)이 순간마다 다른 메서드를 오버라이드한다 — `atStartOfTurn`·`onUseCard`·`onAttack`·`wasHPLost`·`onVictory`, 렐릭은 `onEquip`·`atBattleStart`·`onPlayCard`. Balatro 가 플래그로 가르는 것을 StS 는 **메서드 이름**으로 가른다. 전역 이벤트는 BaseMod 구독(`PostDraw`·`OnCardUse`·`PostBattle`…)으로 한 번 더 열린다.

**수정치는 파이프라인.** 데미지는 `atDamageGive → atDamageReceive → atDamageFinalGive → atDamageFinalReceive` 네 단계를 지난다 — **"어느 단계에 개입하는가"**로 효과를 분류한다. 스택은 `ApplyPowerAction(stackAmount)` — 같은 파워가 이미 있으면 `amount` 를 더한다.

**효과는 상태를 직접 바꾸지 않는다 — 액션을 큐에 넣는다.** 카드의 `use(p, m)` 는 `AbstractDungeon.actionManager.addToBottom(new DamageAction(...))` 처럼 **액션을 쌓을 뿐**이고, `GameActionManager` 가 하나씩 `update()` 하며 `isDone` 이 될 때까지 기다린다. `addToTop` 은 "연출을 먼저, 피해를 나중에" 같은 순서 조작에 쓴다. 이 큐가 곧 **연출 타임라인이자 결정론의 근거**다 — 한 액션이 끝나야 다음이 시작하므로 애니메이션과 판정이 같은 줄에 선다.

**MiniSTS 의 정리.** 액션(`play(by, game_state, battle_state, [target])`) · 상태 효과(이벤트 구독형, `stack`·`end_turn`·`done`) · 값 객체(`ConstValue`·`UpgradableOnce`·`LinearUpgradable`) 셋으로 바닐라를 축약한다 — 상태 효과가 **메서드 오버라이드가 아니라 이벤트 구독**으로도 같은 일을 한다는 대조 사례.

## 3. 세 설계를 한 표에

| 축 | Balatro | Slay the Spire | **Double Down (현재)** |
|---|---|---|---|
| 훅 모델 | 단일 `calculate` + 컨텍스트 플래그 40+ | 훅 메서드 / 구독 | `EffectPhase` 5 (`RoundStarted`·`CardsCaptured`·`HandCompleted`·`Settlement`·`RoundEnded`) |
| 조건 | 코드(`if`) — JF 는 28 조건 + AND/OR | 코드 | `EffectConditionKind` 10, 행당 1개 |
| 연산 | 반환 테이블 키(`chips`·`mult`·`xmult`·…) | 액션 클래스 | `EffectOperationKind` 6 |
| 순서 | 슬롯 좌→우, 만나는 순서로 누산 | 파워 목록 순 / 큐 순 | **슬롯 순서 = 결과 순서** (`SlotOrder_DeterminesOutcomeOrder`) |
| 낱장 상태 | `card.ability.extra` (스케일링) | `power.amount` (스택) | `EffectChargeLedger` (충전 횟수만) |
| 결과 적용 | 즉시 누산(`hand_chips`/`mult`) | 액션 큐가 순차 적용 | `EffectTriggeredEvent` → sink → 정산 수식(`LensChipSum`·`ActualTransfer`) |
| 연출 | 반환키(`message`·`colour`·`no_juice`) + 이벤트 매니저 | 액션 큐 자체가 타임라인 | **없음** — `EffectTriggered` 스텝을 의도적으로 안 냄 |
| 정의 | 낱장당 코드 + 데이터 필드 | 낱장당 클래스 | **데이터 행**(`EffectDefinition`, fixture) |
| 어휘 확장 | 코드가 흡수 | 코드가 흡수 | **어휘 게이트** — 표현 불가면 낱장 재설계(카드 45 계약 1) |

**판정.** 도메인 축은 셋 중 가장 좁지만 v0 낱장 30종 중 21종을 6연산이 이미 담고(카드 45 감사), 누락 9종은 "축을 늘리지 말고 재설계"로 처리하기로 확정돼 있다. 두 원작이 예외 낱장을 코드로 흡수하는 자리를 우리는 재설계로 흡수한다 — **20~30종 범위에서는 문제 없고, 100종+ 에서 재검토**할 결정이다.

## 4. 가져올 것 (구체 — 계획에 반영)

1. **발화 연출은 Balatro 반환키의 우리식 = 이벤트에 실어 스텝으로 낸다.** `EffectTriggeredEvent` 는 이미 발행된다. `PresentationStepConverter` 의 `EffectTriggered` 케이스가 지금 "의도적으로 스텝을 안 낸다"고 못 박아 뒀으니 그 결정을 **열어** `EffectFiredStep`(좌석·낱장 id·연산·양·대상 카드 id)을 낸다. 표현은 원작 문법 그대로 — 슬롯 카드 **튀기**(`UICardReaction` 재사용) + **발화 소스 위치에 플로팅 텍스트**(`FloatingTextSpawner` 재사용, "+3칩") + **색 = 축**(칩/이전액 감액을 다른 색으로) + **크기 비례**(`ScaleForCountValue` 와 같은 축).
2. **순차성은 이미 공짜다.** Balatro 는 좌→우로 시간을 두고 보여주는데, 우리 스텝 폴드가 순차 재생이라 슬롯 순서대로 스텝을 내면 그대로 된다. 여러 발화가 한 phase 에 겹칠 때 **한 스텝에 묶지 말고 낱장마다 스텝 하나** — 원작이 "each Joker triggers in order" 로 가독성을 얻는 자리.
3. **슬롯 순서 = 발화 순서 = 표시 순서**는 이미 계약이다. Balatro 는 드래그 재정렬이 핵심 전략이라 **UI 재정렬 허용 여부**를 결정해야 한다(허용하면 `RunBonusCards` 에 순서 변경 문이 필요).
4. **"컨텍스트 가드" 함정은 구조로 이미 막혀 있다.** phase 가 인자라 잘못된 순간에 불릴 수 없다(`PhaseMismatch_DoesNotFire`). 유지.
5. **스케일링 상태 축은 v1 범위 밖으로 명시한다.** v0 30종에 누적 카운터형(Green Joker 류)이 없다. 필요해지면 `card.ability.extra` 격의 **낱장 인스턴스 상태**를 `EffectChargeLedger` 옆에 두되, 지금 만들지 않는다(YAGNI).
6. **조건 결합(AND/OR)은 지금 필요 없다.** 30종 전부 조건 1개다(`IsSeon`·`Category`·`TurnIndexRange`…). Joker Forge 의 그룹 구조는 필요해질 때의 좌표로만 남긴다.
7. **정산 phase 의 적용 순서를 StS 파이프라인처럼 고정한다.** `ScaleTransfer`(감액) → `CapTransfer`(상한) → 클램프. 곱을 먼저, 상한을 나중에 — 순서가 바뀌면 북어(상한)와 소금(감액)의 합성 결과가 갈린다. **시험으로 못 박을 항목.**
8. **중복 장착 결정.** StS 는 스택(`amount` 합산), Balatro 는 같은 조커 여러 장이 독립 발화. 우리 `RunBonusCards` 가 같은 낱장 두 장을 허용할지, 허용하면 독립 발화인지 정한다(권장: **v1 금지** — 추첨 풀에서 장착 중인 것 제외).
9. **연출 강도는 크기에 비례.** 발화 텍스트·흔들림을 양에 비례시킨다(원칙 인용). `FloatingTextConfig` 에 이미 그 축(`ScaleForCountValue`)이 있다.

## 5. 우리에게 없는 것 (원작이 가진 것) — 의도적 보류

- **리트리거(`repetitions`)·복사(Blueprint/Brainstorm)** — 원작 조커 복잡도의 핵심이지만 GDD 30종에 없다. 어휘에 넣지 않는다.
- **효과 안 RNG** — 원작은 `pseudorandom` 시드 라벨. 우리는 카드 45 계약 ⑧(라벨 스트림 경유)로 자리만 있고 낱장이 없다. `RandomChance` 조건이 필요한 낱장이 생기면 그때.
- **보드 변이(재떨이 — 바닥→더미)** — `CardInstance` 허용 전이에 없어 재설계 대상(카드 45 위험 1순위).

## 관련 문서

- [double-down-ingame-handoff.md](double-down-ingame-handoff.md) — §3 작업패 계보(같은 4계층 문법을 그대로 미러링한다)
- Notion 「보너스 피 설계 (상시 패시브)」 · 「강화 시스템 아키텍처 계약」(카드 45) · 「효과 해석기 + 보너스 피 3장」(카드 48)
- [../best-practice/second-producer-axis-drift.md](../best-practice/second-producer-axis-drift.md) — `EffectFiredStep` 같은 새 스텝은 생산자 전수·필수 인자
