[← README로 돌아가기](../README.md)

# Hwaseo 데미지 표현 기획서

## 0. 개요

| 항목 | 내용 |
|------|------|
| 게임 | 화서 (카드 기반 턴제 전투 RPG) |
| 작성 시점 | 2026-04-30 |
| 범위 | 데미지 표현 5 layer 중 4 layer (A/B/C/D) — E(유형 분류) 제외 |
| 레퍼런스 | Slay the Spire (genre standard) — attack intent + dual-color HP preview |
| 기존 시스템 활용 | `CustomizedValue.GetCalculatedValue` / `DamageResult.FinalValue` / `DescriptionFormatter` / `{value}` placeholder 4-layer L10n 흐름 |

### 배제 항목 (헌법 §5 YAGNI)

- **유형 분류 (Damage Type)** — 일반/관통/도트/반사 출처 구분 표현 X. 게임 디자인이 단일 데미지 풀로 운영.
- **최대 콤보 개념** — 게임 컨셉 부적합 (사용자 명시).

---

## 1. Layer A — 사전 표시 (Preview)

### A-1. 화서 턴 패 사용 시 — 체력바 데미지 미리보기 (Active Card Preview)

**UX 흐름**:
1. 플레이어가 손패에서 카드 선택 (드래그 또는 호버)
2. 타겟 요괴 위에 카드 끌어다 놓기 / 호버
3. 해당 요괴 체력바에 **들어갈 데미지만큼 빨간 슬라이드 영역**으로 미리 표시
4. 카드 사용 결정/취소 시 슬라이드 영역 사라짐

**데이터 흐름**:
- 카드 = `HsSkillInstance.Data.SkillValueData.damage`
- caster = `SkillInstance.Owner` / target = 호버된 요괴 인스턴스
- 평가: `damage.GetCalculatedValue(currentAP, caster, target)` → int
- 표시: 요괴 체력바 컴포넌트 → "예상 데미지 = X" 받아 빨간 영역 그리기

**기존 자산 활용**: `PlayerSkillApplier.cs`의 데미지 계산 로직 미리보기용 readonly 호출 — 실제 적용 X.

### A-2. 도트 데미지 효과 — 체력바 잃을 체력 미리 표시 (Dot Preview)

**UX 흐름**:
1. 요괴/화서 대원에게 화상 N 등 도트 효과 적용 중
2. 차례 시작 또는 효과 트리거 시점 **이전부터** 체력바에 손실 예정 체력 영역 표시
3. 다른 색 (예: 주황) 슬라이드 영역으로 도트 데미지 미리보기

**데이터 흐름**:
- `EffectContainer.GetEffectStack(BurnEffectId, out var stack)`
- 도트 데미지 = stack × 1 (Burn 사양: 매 차례 시작 시 stack의 피해)
- 체력바 컴포넌트 → "예정 도트 데미지 = X" 받아 주황 영역 그리기

**평가 시점**: 효과 적용 직후 + 매 차례 시작 시. effect stack 변화 이벤트 구독.

### A-3. 화서 턴 요괴 호버 — 타겟 + 데미지 UX

**UX 흐름** (Slay the Spire 식):
1. 화서 턴 — 손패에 카드 들고 있는 상태
2. 마우스가 요괴 위로 이동 (카드 드래그 중 OR 카드 미선택 단순 호버 — 미정)
3. 호버된 요괴 강조 (외곽선 / 살짝 떠오르기)
4. 카드 드래그 중이면 **A-1 데미지 미리보기 동시 발동**
5. 카드 미선택 호버는 **요괴 의도(intent) tooltip** + **현재 도트 데미지 누적 표시**만

**미정 사항** — 결정 필요:
- (a) 카드 미선택 호버 시에도 데미지 미리보기 보여줄지? (호버한 요괴를 "다음 패 적용 후보"로 가정)
- (b) Self-target 카드 (회복 등)는 화서 대원 호버 시에도 적용?
- (c) Multi-target 카드 (모든 적 피해)는 호버 없이도 모든 요괴 체력바에 동시 미리보기?

---

## 2. Layer B — 명중 시각 효과 (Floating)

**UX 흐름**:
- 데미지 적용 시점에 피격 위치(요괴 머리 위) **숫자 popup** 떠오르기
- 숫자가 위로 이동하면서 fade-out (~1초)

**기본 사양**:
- 폰트: TMP, 외곽선 검정 / 본체 흰색 (가독성)
- 크기: 일반 데미지 = 36pt, 강타 (예: 모디파이어로 50% 이상 증가) = 48pt + 빨간색

**연출 강화 (Phase 2 예정)** — 우선순위 낮음:
- 풀 댐 (Block 0 으로 모두 관통) → 노란 outline + shake
- 약점 (Weak 적용된 적이 받는 데미지) → 보라색 tint
- 0 데미지 (Block 막음) → "BLOCKED" 텍스트 또는 숫자 회색

**구현 의존**: TMP + DOTween fade/move + sprite outline shader.

---

## 3. Layer C — 결과 요약 (Result Summary)

### C-1. 전투 중 누적 카운터 (실시간)

**표시 위치**: 화서 측 UI 일각 (HP/AP 옆 등)
**표시 항목** (사용자 명시):
- **화서 총 누적 데미지** — 전투 시작부터 현재까지 모든 화서 대원이 가한 데미지 합계

**제외**: 최대 콤보 X / 처치 카운트 X (전투 중 미표시)

**데이터 흐름**:
- `BattleManager.Context.DamageHistory` 등 누적 큰틀 신설 또는 기존 History 확장
- 데미지 적용 이벤트 (`OnDamageDealt`) 구독해 카운터 증가

### C-2. 런 종료 시 정리 (Run End Summary)

**표시 시점**: 한 런 마무리 (보스 클리어 또는 사망)
**표시 항목**:
- **총 누적 데미지** (전 전투 합계)
- **처치 요괴 카운트** (전 전투 합계)
- 추가 후보 (사용자 결정 필요): 받은 데미지 합계 / 사용한 카드 수 / 최대 단일 데미지 등

**데이터 흐름**: `RunStateData` 등에 누적 통계 필드 추가 → 런 종료 화면에서 read.

---

## 4. Layer D — 메카닉 표현 (Modifier Visualization)

### D-1. 도트 데미지 효과 — 체력바 미리 표시

→ **Layer A-2와 동일** (단일 표현 단일 책임).

### D-2. 데미지 증감 효과 — 호버 시 체력바 미리보기

**UX 흐름**:
1. 요괴/화서가 데미지 증감 효과 보유 (예: Power +3, Weak 25% 감소)
2. 화서가 카드 호버 / 드래그 (Layer A-1 트리거)
3. 체력바 미리보기에 **모디파이어 적용된 최종 데미지** 반영
4. **다른 색 슬라이드 영역**으로 가감 영역 시각화 (예: base 데미지 = 빨강, modifier 가산 = 진한 빨강 / Block 차감 = 회색)

**시각 사양**:
- base damage 영역 → 기본 빨간색
- Power 등으로 가산된 영역 → **약간 더 진한 빨강** (가산분 시각 분리)
- Block 차감 영역 → 회색 (실제로 깎이지 않을 영역)
- Weak 등으로 감산된 영역 → 빨간색 영역이 짧아져서 시각적으로 표현 (별도 색 X)

**데이터 흐름**:
- `damage.GetCalculatedValue(currentAP, caster, target)` 결과 = 최종 데미지
- 분해 정보 = base + modifier (Power 등) - Block 등 → 미리보기 분할 표시
- 분해 메서드 신설 필요: `DamageResult.FromPreview(caster, target, skill)` (분해 결과 반환)

---

## 5. 우선순위 / Phase 분리

| Phase | Layer | 우선순위 | 비고 |
|-------|-------|---------|------|
| **Phase 1** | A-1 (active card preview) + B (floating) | 최우선 | 핵심 게임 피드백, MVP 필수 |
| **Phase 2** | A-2 / D-1 (도트 미리보기) | 높음 | 화상 / 가시 등 메카닉 명시성 |
| **Phase 3** | A-3 (요괴 호버 UX) + D-2 (모디파이어 시각화) | 중간 | 정보 밀도 향상 |
| **Phase 4** | C-1 (전투 중 누적 카운터) | 중간 | 사이드 정보 |
| **Phase 5** | C-2 (런 종료 정리) | 낮음 | 런 종료 화면 신설 시 함께 |

---

## 6. 헌법 정합 + 기존 시스템 활용

### §0-1 Step 1 (영향 분석)
- `CustomizedValue.GetCalculatedValue` — 모든 layer가 의존, signature 변경 X
- `DescriptionFormatter` — `{damage}` placeholder 흐름 보존, A-1 미리보기는 추가 신설
- `DamageResult` — 분해 정보 추가 (D-2 위해 modifier breakdown 노출)

### §1 SOLID
- HP bar 컴포넌트 = 단일 책임 (현재값 + 도트 미리보기 + 모디파이어 미리보기 = SRP 위반 가능 → 분리 검토)
- modifier breakdown 인터페이스 = ISP (preview용 readonly vs apply용 mutable 분리)

### §2-0 Caller-Driven Snapshot 박멸
- 데미지 popup (Layer B)은 숫자(int) 보존, 텍스트 박제 X — 현재 `DescriptionFormatter` 흐름 정합
- 미리보기 (Layer A) 모두 lazy resolve — caster/target/skill ref 보존, 평가는 표시 직전

### §5 YAGNI
- E (유형 분류) 배제 정합
- 최대 콤보 배제 정합
- 모디파이어 색 구분은 base + 가산 + 차감 3종만 (4종 이상은 게임 디자인 명확화 후 추가)

---

## 7. Open Questions (사용자 결정 필요)

1. **Layer A-3 미정 사항** — 카드 미선택 호버 시 미리보기 발동 여부 / Self-target / Multi-target 처리
2. **Layer B Phase 2 연출 강화** — 강타/약점/풀댐 시각 차이 도입 시점
3. **Layer C-2 런 종료 표시 항목** — 받은 데미지 합계 / 사용 카드 수 / 최대 단일 데미지 포함 여부
4. **Layer D-2 modifier 색상 팔레트** — base/가산/차감 3종으로 충분한지, Weak 별도 색 필요한지
5. **HP bar 컴포넌트 분리 vs 통합** — 현재값 / 도트 / 모디파이어 미리보기 단일 컴포넌트 vs 3분할

---

## 관련 문서

- [best-practice/multilayer-locale-snapshot.md](../best-practice/multilayer-locale-snapshot.md) — `{value}` placeholder lazy resolve 패턴 (Layer A 데미지 표현 동일 적용)
- [.claude/rules/engineering-constitution.md](../.claude/rules/engineering-constitution.md) — §0/§1/§2-0/§5 정합 기준
