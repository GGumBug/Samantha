[← README.md로 돌아가기](README.md)

# 11 — INTENSITY 게이지 + Stage 1-5 배지 (자산 A)

**위임**: Friday | **위치**: `endurance/src/app/dashboard/_components/IntensityGaugeStageBadge.tsx` (Server Component) | **의존**: 자산 07 (v1 게이지 wrapper 확장), Phase 0.5 05 ML inference 결과 표시, Phase 0.5 07 GEMSTONE Stage 토큰, Phase 1 02 `DashboardGemstoneBlock.intensity`

## Purpose

GEMSTONE EWS의 핵심 시각 — **74점 형식 INTENSITY 게이지** (반원형 0-100 게이지)와 **Stage 1-5 배지** ("비중 확대/축소" 라벨 포함)를 단일 위젯으로 합성. 사용자가 한 눈에 시장 위험 강도(probability → 0-100) + 강도 단계(Normal/Watch/Caution/Warning/Critical) + 행동 권고(확대/축소)를 인식하게 한다.

본 위젯은 데이터 페치 0건. 02-data-api가 Phase 0.5 05 `infer()` 호출 결과를 `intensity` 필드로 합쳐 전달 (헌법 §2 SSOT). 본 위젯은 props로 받은 `intensity.score`·`intensity.stage`·`intensity.weightingHintKey`만 시각화.

## 의존성

- **사용하는 자산**:
  - 자산 07 (`EarlyWarningGauge.tsx` wrapper — v1 게이지 SVG 그리기 로직 보존, ML inference 호출은 02로 위임)
  - Foundation 07 `gauge-meter` 토큰 (반원형 0-100 게이지 wrapper)
  - Phase 0.5 07 GEMSTONE Stage 5구간 색·i18n key 토큰 (`ews.stage.normal|watch|caution|warning|critical`)
  - Phase 1 02 `DashboardGemstoneBlock.intensity`
- **이걸 사용하는 자산**: Phase 1 08 (Integration이 grid 좌상에 배치, 자산 A)

## Public Interface

```typescript
// src/app/dashboard/_components/IntensityGaugeStageBadge.tsx
import type { DashboardGemstoneBlock } from "@/lib/dashboard/data";

interface IntensityGaugeStageBadgeProps {
  blocks: DashboardGemstoneBlock[]; // 1~2개 (market 선택)
  size?: "sm" | "md" | "lg";        // default "md"
}

export function IntensityGaugeStageBadge(
  props: IntensityGaugeStageBadgeProps,
): JSX.Element;
```

표시 형태 (BOTH 시 횡 2매):

```
┌────────────────────────────────────┐
│   KOSPI200 INTENSITY               │
│         ╭─────────╮                │
│       ╱     74      ╲              │
│      ╱_______________╲             │
│   ┌──────────────────────┐         │
│   │ Stage 4 — Warning    │         │
│   │ 비중 축소             │         │
│   └──────────────────────┘         │
└────────────────────────────────────┘
```

data-testid:
- root: `widget-intensity-gauge`
- Stage 배지: `widget-stage-badge`
- (옵션) BOTH 시 시장별: `widget-intensity-gauge-KR`, `widget-intensity-gauge-US`

## Implementation Notes

- **자산 07 wrapper 확장**: v1 `EarlyWarningGauge.tsx` SVG 게이지 그리기 로직 보존. v1 `isPlaceholder` UI 분기는 제거 (v2는 실제 ML inference 결과). 본 자산은 v1 wrapper를 import + Stage 배지를 합성.
- **Stage 배지 색 매핑**: Phase 0.5 07 GEMSTONE Stage 토큰 SSOT — Stage 1(success)·2(ink-muted)·3(warning)·4(amber 커스텀)·5(danger). 본 위젯이 색 결정 0건, 토큰 import만.
- **"비중 확대/축소" 라벨**: `intensity.weightingHintKey` ("ews.weighting.expand" | "ews.weighting.reduce") → 컴포넌트 내부 `t(weightingHintKey)` 호출 (헌법 §2-0-1 — caller가 string 박지 않음). i18n 키 보존.
- **Stage → 행동 매핑**: Stage 1-2 = expand, Stage 3-4-5 = reduce. 본 매핑은 02-data-api가 박음 (Phase 0.5 06 stages.ts SSOT 사용 권장 — 단일 매핑).
- **헌법 §6 escape hatch**: 없음. production 코드.
- **anti-pattern §2-0-1**: `intensity.stageLabelKey` / `intensity.weightingHintKey`는 키 string. 컴포넌트 내부 `useTranslation()` 또는 동등 훅으로 표시 직전 변환.

### 헌법 §0-1 Step 1 영향 분석

| 변경 대상 | 영향 |
|----------|------|
| 자산 07 v1 게이지 wrapper SVG | 본 위젯이 import. wrapper 변경 시 본 자산 + 후속 GEMSTONE radar 위젯 갱신 |
| Phase 0.5 07 Stage 색 토큰 | 본 위젯이 import. 색 매핑 변경 시 본 자산 시각 회귀 |
| 02 `intensity` 필드 시그니처 | 본 위젯이 props로 직접 읽음. 02 갱신 시 본 자산 갱신 |

### 헌법 §0-1 Step 2 합리화 회피

- "stage 라벨 string을 02가 박아 전달": ❌ caller-driven UI string snapshot (§2-0-1). 키 보존 + 컴포넌트 내부 t() 의무
- "v1 게이지 wrapper 통째 폐기, 신규 작성": ❌ Foundation 07 gauge-meter + v1 wrapper 보존이 SSOT. 신규 작성 = SSOT 위반

## Test Strategy

### 단위
- `intensity.score=74, intensity.stage=4` → 게이지 value=74 + 배지 텍스트 "Stage 4" + 색=amber 커스텀
- `intensity.stage=1` → 배지 색=success, weightingHintKey="ews.weighting.expand" → "비중 확대" 표시
- `blocks=[KR, US]` → 위젯 2매 횡 배치
- `intensity.score=null` (edge) → "데이터 없음" placeholder

### 시각 검증
- `/dev/preview` Section (Phase 0.5 08 GEMSTONE preview)에 본 위젯 5 Stage 모두 렌더 — 시각 회귀 0건
- INTENSITY 게이지 색 분기 (Stage 1-5)가 Phase 0.5 07 토큰과 일치

### 표준 검증 시나리오 (헌법 §0-1 Step 3 — 신기능 + 위젯 빈 데이터)
- 정상: `intensity.score=74, stage=4` → 게이지 + 배지 시각 정상
- 빈 데이터: `blocks=[]` → "데이터 없음"
- null edge: `intensity=null` → 게이지 자리 placeholder + Stage 배지 hidden
- 외부 API 실패: 02 `errors[]`에 박힌 market은 게이지 자리 trigger-badge
- i18n: 마운트 중 언어 토글 시 "Stage 4" → "단계 4" 자동 갱신 (caller-driven string 0건 grep 검증)
- anti-pattern §2-0-1 Pattern A·B grep 본 파일 0건

## Verification

- [ ] `endurance/src/app/dashboard/_components/IntensityGaugeStageBadge.tsx` 존재 + Server Component
- [ ] 자산 07 v1 wrapper import (게이지 SVG 자체 작성 0줄)
- [ ] Phase 0.5 07 Stage 토큰 import (hex 인라인 0건)
- [ ] `tsc --noEmit` 무경고
- [ ] data-testid `widget-intensity-gauge`, `widget-stage-badge` 박힘
- [ ] 단위 테스트 6개 이상 (5 Stage × score 조합 + 빈/null)
- [ ] anti-pattern §2-0-1 grep 0건 (label·title:string 필드 0건, t() 호출은 컴포넌트 내부)
- [ ] `/dev/preview` 시각 회귀 0건

## Open Questions

1. **Stage 배지 위치**: 게이지 하단 vs 우측 — Phase 0.5 08 preview에서 시각 결정. GEMSTONE 스크린샷 따르면 게이지 우측에 큰 카드 + 배지.
2. **"비중 확대/축소" 한글 vs 영어**: i18n key `ews.weighting.expand|reduce` 박혀 후속 변경 비용 0. 초안은 한국어 + 영어 fallback.
3. **74점 디스플레이 폰트 크기**: 사용자 한 눈 인식을 위해 큰 폰트(48-64pt)가 GEMSTONE 스크린샷 패턴. 디자인 토큰의 `typography.display` 사용 권장.
