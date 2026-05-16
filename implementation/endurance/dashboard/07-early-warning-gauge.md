[← README.md로 돌아가기](README.md)

# 07 — Early Warning Gauge (v2 INTENSITY + Stage 배지, ML inference)

> **변경 이력**
> - v2 (2026-05-16): GEMSTONE EWS 재정의에 맞춰 책임 갱신. 사유: 사용자가 GEMSTONE 스크린샷 단언 후 정공 재정의 (옵션 D). 기존 v1 구현 코드는 이 명세 §"v1 코드 처리"에 따라 처리. 본 자산은 자산 11(11-intensity-gauge-stage-badge.md)의 base wrapper 역할로 유지.
> - v1 (이전): placeholder 산식(P/E z-score + 변동성 백분위) 기반 0-100 게이지.

**위임**: Friday | **위치**: `endurance/src/app/dashboard/_components/EarlyWarningGauge.tsx` (자산 11이 본 wrapper 확장) | **의존**: Foundation 07 `gauge-meter` 토큰, Phase 0.5 05 ML inference 어댑터, Phase 0.5 07 GEMSTONE Stage 토큰, Phase 1 02 `DashboardGemstoneBlock.intensity`

## v1 코드 처리

v1 `EarlyWarningGauge.tsx` 게이지 wrapper 보존, **산식 본격화**:

- v1 `calculateEarlyWarning` placeholder 산식 함수 → 폐기. 02-data-api가 Phase 0.5 05 `infer()` 호출로 대체. v1 함수 파일(`early-warning.ts`)은 `@deprecated` 주석 + 호출 0건 확인 후 다음 PR에서 삭제 권장
- v1 `isPlaceholder: true` UI 분기(하단 "ⓘ placeholder algorithm (LPPL coming in Phase 4)" 텍스트) → 제거. v2는 실제 ML 모델 inference 결과 → placeholder 표시 의미 없음
- v1 4구간 band(safe/neutral/caution/danger) → v2 Stage 1-5(Normal/Watch/Caution/Warning/Critical)로 교체. Foundation 07 gauge 4구간 색 매핑 → Phase 0.5 07 GEMSTONE Stage 5구간 색 매핑으로 갱신
- v1 단위 테스트 8건(placeholder 산식 검증) → 폐기. 자산 11이 신규 단위 테스트(ML inference mock + Stage 배지 매핑) 작성
- v1 게이지 컴포넌트 wrapper(SVG·반원형 그리기) → 보존. 자산 11이 본 wrapper를 import해서 INTENSITY 게이지 + Stage 배지 합성

## Purpose

KOSPI200·S&P 500 양 시장의 **0-100 INTENSITY 점수**를 반원형 게이지로 표시. v2는 **ML inference 기반 본격 산식**(Phase 0.5 05 MLP/SVM)으로 v1 placeholder 산식을 교체. 본 자산은 SVG wrapper만 유지하고, 자산 11이 본 wrapper를 import해서 INTENSITY 게이지 + Stage 1-5 배지를 합성.

본 자산이 박는 핵심 분리 (v2):
1. **게이지 wrapper (시각)** — Foundation 07 `gauge-meter` 토큰 재사용. v1 보존.
2. **INTENSITY 점수 산식** — v2에서 Phase 0.5 05 `infer()` 호출로 위임. 02-data-api가 SSOT 진입점.

이 분리가 헌법 §1 OCP(개폐 원칙) 적용 — 산식 교체 시 wrapper 변경 0건.

## 의존성

- **사용하는 자산**:
  - Foundation 07 — `gauge-meter` 토큰 + 컴포넌트 wrapper (`endurance/src/components/gauge/GaugeMeter.tsx`)
  - Phase 0.5 05 — ML inference 어댑터 (직접 호출 안 하고 02 v2 경유)
  - Phase 0.5 07 — GEMSTONE Stage 5구간 색 토큰
  - Phase 1 02 — `DashboardGemstoneBlock.intensity` (v2 시그니처)
- **이걸 사용하는 자산**:
  - 자산 11 — wrapper import해서 INTENSITY + Stage 배지 합성
  - Phase 1 08 (Integration이 자산 11을 grid에 배치, 본 wrapper는 자산 11 내부에서만 사용)

## Public Interface

### v2 게이지 wrapper (자산 11이 import)

```typescript
// src/app/dashboard/_components/EarlyWarningGauge.tsx
// v1 wrapper 보존 — SVG·반원형 그리기 + Foundation 07 gauge-meter 토큰 적용
import type { DashboardGemstoneBlock } from "@/lib/dashboard/data";

interface EarlyWarningGaugeProps {
  blocks: DashboardGemstoneBlock[]; // v2: GemstoneBlock으로 시그니처 갱신
  size?: "sm" | "md" | "lg";
}

export function EarlyWarningGauge(props: EarlyWarningGaugeProps): JSX.Element;
```

자산 11(`IntensityGaugeStageBadge.tsx`)이 본 wrapper를 import해서 Stage 배지 합성. **v1 점수 산식 함수(`calculateEarlyWarning`) export 폐기** — 02가 Phase 0.5 05 `infer()` 직접 호출.

표시 형태: 자산 11 명세 참조 (74점 형식 + Stage 1-5 배지).

## Implementation Notes

- **v1 wrapper SVG 보존**: 반원형 게이지 그리기 로직(SVG arc·label·color 분기)은 v1 그대로. Phase 0.5 07 GEMSTONE Stage 5구간 색 매핑으로 v1 band 4구간 색 매핑 교체.
- **v1 `calculateEarlyWarning` 산식 함수 폐기**: 02-data-api가 Phase 0.5 05 `infer()` 호출로 INTENSITY score 계산 → `intensity.score` 박음. v1 함수 파일(`early-warning.ts`)은 `@deprecated` + 다음 PR에서 삭제.
- **v1 `isPlaceholder` UI 분기 제거**: v2는 실제 ML inference 결과 → "placeholder algorithm" 텍스트 제거. Stage 배지가 결과의 강도·신뢰도를 표현.
- **자산 11과의 분리 책임**:
  - 본 자산(07 v2) = SVG wrapper만 (Foundation 07 gauge-meter 토큰 적용)
  - 자산 11 = wrapper import + Stage 배지 합성 + 02 `intensity` 필드 props 분배

### 헌법 §0-1 Step 1 영향 분석

| 변경 대상 | 영향 |
|----------|------|
| Foundation 07 `GaugeMeter` props | 본 wrapper가 의존. 변경 시 자산 11 + 11 호출처 갱신 |
| Phase 0.5 05 `infer()` 결과 → 02 → `intensity.score` | v1 산식 폐기 + ML inference로 교체. 02 v2 명세 SSOT |
| 자산 11 합성 책임 | 본 wrapper만 단독 사용 안 함 — 자산 11 통합 진입점 |

### 헌법 §0-1 Step 2 합리화 회피

- "v1 wrapper 통째 폐기 + 자산 11에 신규 SVG 작성": ❌ SSOT 위반. v1 wrapper 보존 + 자산 11이 import
- "v1 `calculateEarlyWarning` 함수 보존 (Phase 4 대비)": ❌ Phase 0.5 05 `infer()`가 SSOT. 잔재 보존 = 헌법 §2 위반

## Test Strategy

본 wrapper 단독 단위 테스트는 v1과 동일 — SVG 렌더링 + 색 매핑. **점수 산식 단위 테스트는 폐기** (자산 11 + Phase 0.5 05 inference parity 테스트로 흡수).

### 표준 검증 시나리오 (헌법 §0-1 Step 3 — 위젯 빈/null)
- 빈 데이터: blocks 빈 → "데이터 없음" placeholder
- null edge: `intensity.score=null` → 게이지 미렌더
- 외부 API 실패: 02 `errors[]` 박은 market은 게이지 자리 trigger-badge

## Verification

- [ ] `endurance/src/app/dashboard/_components/EarlyWarningGauge.tsx` 존재 + v2 시그니처(`DashboardGemstoneBlock`)
- [ ] Foundation 07 `GaugeMeter` wrapper만 사용 (자체 SVG 작성 0줄)
- [ ] `tsc --noEmit` 무경고
- [ ] v1 `early-warning.ts` 함수 `@deprecated` 또는 삭제 결정
- [ ] grep `calculateEarlyWarning\|EarlyWarningInput\|EarlyWarningResult\|isPlaceholder` 본 파일 v2 잔재 0건
- [ ] grep `DashboardMacroBlock` 본 파일 0건 (v2는 `DashboardGemstoneBlock`)
- [ ] grep으로 본 파일 내 `fetch(`, `yahoo-finance` 0건
- [ ] 자산 11이 본 wrapper import 검증 (자산 11 verification과 동기)

## Open Questions

1. **v1 `early-warning.ts` 파일 처리**: 즉시 삭제 vs `@deprecated` 후 다음 PR 삭제. 후자 권장 (안전).
2. **자산 11과 본 wrapper 단일 컴포넌트 통합 가능성**: 분리가 SRP에 부합하나 호출 사슬 길어짐. 자산 11 머지 후 시니어 판단 — 통합 또는 분리 유지.
3. **band 4구간 → Stage 5구간 매핑 회귀**: v1 4구간 사용처(있다면) v2 5구간으로 마이그레이션 시 색 분기 회귀 위험. grep으로 v1 band 잔재 0건 확인 의무.
4. **Phase 4 LPPL 모델 추가 가능성**: 현 v2는 MLP/SVM 단일 모델 출력 `intensity.score`. Phase 4에서 LPPL이 추가 모델로 합류 시 02-data-api가 multi-model 합성(가중평균 또는 max) — 본 wrapper 변경 0건 (OCP 검증).
