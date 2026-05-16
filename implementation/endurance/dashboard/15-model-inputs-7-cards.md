[← README.md로 돌아가기](README.md)

# 15 — MODEL INPUTS 7 변수 카드 (자산 E)

**위임**: Joi | **위치**: `endurance/src/app/dashboard/_components/ModelInputsCards.tsx` (Server Component) + `endurance/src/app/dashboard/_components/ModelInputCard.tsx` (단일 카드) | **의존**: Foundation 07 `metric-card` 토큰, Foundation 08 Sparkline wrapper, Phase 0.5 07 GEMSTONE 7 토큰 SSOT, Phase 1 02 `DashboardGemstoneBlock.modelInputs[]`

## Purpose

GEMSTONE 7 변수(Garnet · Emerald · Moonstone · Sapphire · Topaz · Ruby · Amber)를 **7 sparkline 카드 grid**로 표시. 각 카드:
- 보석명 + 변수 풀네임 라벨 (i18n key 경유)
- 현재 값 + z-score
- 90포인트 sparkline (시계열)
- NEUTRAL / REVERSION 라벨 (z-score 분포 기반)

본 자산이 **자산 06(Term Spread Chart) v1을 흡수** (Sapphire 인스턴스로 통합). 7 카드 grid + Phase 0.5 07 GEMSTONE 토큰 SSOT 경유 — 임의값 사용 금지.

## 의존성

- **사용하는 자산**:
  - Foundation 07 `metric-card` 토큰 (라벨 + 값 + sparkline 슬롯)
  - Foundation 08 `Sparkline` wrapper
  - Phase 0.5 07 `GEMSTONE_TOKENS` 상수 (7 보석 메타데이터 SSOT)
  - Phase 1 02 `DashboardGemstoneBlock.modelInputs[]`
- **이걸 사용하는 자산**: Phase 1 08 (Integration — grid 우중에 배치, 자산 E)
- **흡수 대상**: 자산 06 v1 (Sapphire 카드 인스턴스로 통합)

## Public Interface

```typescript
// src/app/dashboard/_components/ModelInputsCards.tsx
import type { DashboardGemstoneBlock } from "@/lib/dashboard/data";

interface ModelInputsCardsProps {
  blocks: DashboardGemstoneBlock[]; // 1~2개
}

export function ModelInputsCards(props: ModelInputsCardsProps): JSX.Element;

// src/app/dashboard/_components/ModelInputCard.tsx
import type { GemstoneId } from "@/components/gemstone/types";

interface ModelInputCardProps {
  gemstoneId: GemstoneId;
  currentValue: number;
  zScore: number;
  sparkline: Array<{ date: string; value: number }>;
  regimeKey: "modelInput.regime.neutral" | "modelInput.regime.reversion";
}

export function ModelInputCard(props: ModelInputCardProps): JSX.Element;
```

표시 형태 (7 카드 grid — desktop 4+3 또는 4×2-1):

```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ Garnet      │ Emerald     │ Moonstone   │ Sapphire    │
│ KOSPI Skew  │ Vol/Cap     │ Pairwise ρ  │ US 10Y-2Y   │
│ 0.42 (z=1.2)│ 0.18 (z=-0.4)│ 0.78 (z=2.1)│ 0.34 (z=-1.8)│
│ ╱╲╱╲╱╲      │ ╲╱╲╱╲╱      │ ╱╱╲╲       │ ╲╲╱╲╱       │
│ NEUTRAL     │ NEUTRAL     │ REVERSION   │ REVERSION   │
├─────────────┼─────────────┼─────────────┤             │
│ Topaz       │ Ruby        │ Amber       │             │
│ Fed Unc     │ WTI         │ 10Y Infl    │             │
│ ...         │ ...         │ ...         │             │
└─────────────┴─────────────┴─────────────┘             │
```

data-testid:
- root: `widget-model-inputs`
- 카드 각각: `model-input-card-{gemstoneId}` (예: `model-input-card-garnet`)

## Implementation Notes

- **`GEMSTONE_TOKENS` SSOT 경유**: 보석명·라벨 i18n key·색 매핑은 모두 Phase 0.5 07 `GEMSTONE_TOKENS` 상수 import. 본 위젯 내 하드코딩 0줄.
- **NEUTRAL/REVERSION 라벨**: `regimeKey` props는 키. 컴포넌트 내부 `t(regimeKey)` 호출. z-score 분포 기반 분류는 02-data-api 영역 (헌법 §2 SSOT).
  - `regime.neutral`: |z| < 1.5 (분포 중심)
  - `regime.reversion`: |z| ≥ 1.5 (극단값 — 평균 회귀 가능성)
- **카드 색 매핑**: Phase 0.5 07 토큰 z-score 분기 (0~±1 보석 본색 · 1~2 warning · >2 danger) — 본 위젯 내 색 결정 0건, 토큰 SSOT 경유.
- **sparkline 90포인트**: 02가 90영업일 (~4.5개월) 시계열 박음. 너무 길면 시각 노이즈, 짧으면 추세 인식 어려움.
- **빈 데이터 처리**: `modelInputs.length < 7` → 누락 카드 자리에 "데이터 부족" placeholder. 7 변수 모두 필수 (Phase 0.5 02 변수 계산 엔진이 7 변수 보장).
- **BOTH 처리**: 본 위젯은 GEMSTONE 7 변수가 KOSPI 시장 중심 정의 (Garnet·Emerald·Moonstone = KOSPI 자체). 따라서 BOTH 토글 시에도 KOSPI200 한 set만 표시 권장 (Open Q 1).

### 헌법 §0-1 Step 1 영향 분석

| 변경 대상 | 영향 |
|----------|------|
| Phase 0.5 07 `GEMSTONE_TOKENS` 상수 | 본 위젯이 import. 토큰 변경 시 본 자산 시각 회귀 |
| 02 `modelInputs[]` 배열 길이/항목 | 본 위젯이 직접 읽음. 변경 시 본 자산 갱신 |
| 자산 06 v1 `TermSpreadChart` | 흡수. 06 명세 stub으로 축소 가능 |

### 헌법 §0-1 Step 2 합리화 회피

- "각 카드 색을 직접 hex로 지정": ❌ Phase 0.5 07 토큰 SSOT. 직접 지정 = SSOT 위반
- "NEUTRAL/REVERSION 라벨을 02가 string으로": ❌ caller-driven UI string snapshot (§2-0-1). 키 보존

## Test Strategy

### 단위
- `modelInputs[0].gemstoneId="garnet", currentValue=0.42, zScore=1.2` → Garnet 카드 표시 + NEUTRAL 라벨
- `zScore=2.5` → 카드 색 danger + REVERSION 라벨
- `modelInputs.length=5` → 5 카드 + 2 자리 placeholder
- `sparkline=[]` → sparkline 자리 빈 + 값만 표시

### 표준 검증 시나리오 (헌법 §0-1 Step 3 — 위젯 빈 데이터/null)
- 정상 7 카드 + 빈/null/짧은 sparkline edge + BOTH (KOSPI 한 set 유지)
- i18n: 마운트 중 언어 토글 시 7 변수 라벨 + NEUTRAL/REVERSION 자동 갱신
- anti-pattern §2-0-1 Pattern A·B grep 0건

### 시각 검증
- `/dev/preview` Phase 0.5 08 GEMSTONE 섹션에 7 카드 모두 normal/warning/danger 렌더

## Verification

- [ ] `endurance/src/app/dashboard/_components/ModelInputsCards.tsx` + `ModelInputCard.tsx` 존재
- [ ] Phase 0.5 07 `GEMSTONE_TOKENS` import (hex 인라인 0건)
- [ ] Foundation 08 Sparkline wrapper 사용 (Recharts/visx 직접 import 0건)
- [ ] `tsc --noEmit` 무경고
- [ ] data-testid `widget-model-inputs` + `model-input-card-{gemstoneId}` 7종 박힘
- [ ] 단위 테스트 8개 이상 (7 보석 × 정상 + edge)
- [ ] anti-pattern §2-0-1 grep 0건 (label·regime 필드 string 0건, t() 컴포넌트 내부)

## Open Questions

1. **BOTH 토글 시 GEMSTONE 7 변수 시장 매핑**: 7 변수 중 KOSPI 중심(Garnet·Emerald·Moonstone) vs US 중심(Sapphire·Topaz) 혼재. BOTH 토글 시 KOSPI 한 set만 표시가 자연. 사용자 검증 후 결정.
2. **Grid 레이아웃**: 7 카드 → 4×2-1 vs 7×1 vs 4+3. desktop/mobile 별로 다른 레이아웃 필요.
3. **NEUTRAL/REVERSION 임계값**: |z| 1.5 vs 2.0 — Phase 0.5 03 학습 데이터셋 positive_rate 분석 후 갱신 가능.
4. **sparkline window 90 vs 30/180**: 90영업일 ~4.5개월. 사용자 검증.
