[← README.md로 돌아가기](README.md)

# 05 — Daily Volatility Sparkline (Phase 2 이관)

**위임**: Joi | **위치**: Phase 2 `/stock/[ticker]` 또는 `/sectors` 부속 카드 (구현 시점 결정) | **의존**: Foundation 07 `metric-card` 토큰, Foundation 08 Sparkline wrapper, Phase 1 02 `DashboardMacroBlock` (또는 Phase 2 종목 데이터 API)

## 이관 사유

Phase 1 GEMSTONE EWS 재정의(2026-05-16) 시점에 본 자산은 잉여 위젯으로 판정. GEMSTONE 7 MODEL INPUTS 변수와 **사용자 4 변수(P/E·EPS·Term Spread·Volatility) 매핑 0건** — 일일 변동성(30일 std)은 GEMSTONE 거시 신호와 직접 연결되지 않음. (GEMSTONE Topaz의 Fed Policy Rate Uncertainty 대용으로 MOVE Index 또는 T-Bill Volatility를 사용하는 것은 변동성 개념의 변형이나, 본 자산의 KOSPI 30일 일일 수익률 std와 차원이 다름.)

본 자산이 진정 가치를 갖는 위치는 **Phase 2 `/stock/[ticker]` 개별 종목 화면** 또는 **Phase 3 `/sectors` 섹터 히트맵 부속** — 종목·섹터 단위 위험 측정에 변동성이 직관적 도구. 따라서 dashboard/에서 phase-2/로 이관, Phase 2 진입 시 본 명세 재검토 후 종목 페이지 컨텍스트에 맞춰 props·라벨·데이터 출처(yfinance 종목 OHLCV) 갱신.

**v1 구현 코드 처리**: endurance 저장소 24커밋 중 05 관련 4커밋(`VolatilitySparkline.tsx` + 단위 테스트)은 그대로 보존. Phase 2 진입 시 import 경로만 갱신. 컴포넌트 자체 로직(Sparkline + std 표시)은 종목 페이지에서도 유효.

## Purpose

KOSPI·NASDAQ 양 시장의 **30일 일일 수익률 표준편차(=일일 변동성)** 를 metric-card + sparkline 미니 차트로 표시한다. 변동성 절대값과 추세를 한 카드로 보여줘 거시 위험을 직관적으로 가시화.

본 위젯도 외부 API 호출 0건. 02-data-api가 반환한 `volatility30d`(스칼라 %)와 `volatilitySeries`(30포인트 시계열)를 props로 받아 차트만 그린다.

## 의존성

- **사용하는 자산**:
  - Foundation 07 — `metric-card` 토큰 (label + value + sparkline 슬롯)
  - Foundation 08 — `Sparkline` 또는 `LineChart` 미니 변형 wrapper (Phase 0에서 결정한 차트 라이브러리)
  - Phase 1 02 — `DashboardMacroBlock.volatility30d`, `volatilitySeries`
- **이걸 사용하는 자산**: Phase 1 08 (Integration이 grid에 배치)

## Public Interface

```typescript
// src/app/dashboard/_components/VolatilitySparkline.tsx
import type { DashboardMacroBlock } from "@/lib/dashboard/data";

interface VolatilitySparklineProps {
  blocks: DashboardMacroBlock[]; // 1~2개
}

export function VolatilitySparkline({ blocks }: VolatilitySparklineProps): JSX.Element;
```

표시 형태 (블록당 1매, BOTH 시 2매 횡 배치):

```
┌──────────────────────────────────────────┐
│ KOSPI · 30D DAILY VOLATILITY             │
│ 1.23%        ╱╲╱╲    ╱╲                  │
│              ╱   ╲╱╲╱  ╲╱╲╱              │  ← 30포인트 sparkline
└──────────────────────────────────────────┘
```

### Sparkline props (Foundation 08)

| 슬롯 | 값 |
|------|-----|
| series | `volatilitySeries.map(p => p.pct)` — 30포인트 number[] |
| width × height | 60×24 (Foundation 07 metric-card sparkline 슬롯 규격) |
| color | `{colors.primary}` 단일 |
| 0선 baseline | 옵션 — 변동성은 항상 양수라 baseline 불필요 |

## Implementation Notes

- **변동성 계산은 02-data-api 영역**: 본 위젯은 std 계산을 하지 않는다. 02가 30일 일일 수익률 std를 계산해 `volatility30d`(스칼라)와 `volatilitySeries`(rolling window)를 반환. SSOT 보장(헌법 §2)
- **연환산 처리**: Phase 1은 **일일 변동성(annualized X)** 단위로 표시. 연환산은 위젯에서 즉석 변환하지 않고 02가 라벨에 맞는 값을 보내도록 함. 라벨도 "30D DAILY VOLATILITY"로 차원 명시
- **빈 시계열**: `volatilitySeries.length < 5` 시 sparkline 자리에 "데이터 부족" placeholder. 거래일 적은 새 ticker 등 케이스 방어 (헌법 §0-1 Step 3 위젯 빈 데이터)
- **Foundation 08 wrapper 재사용 의무**: 본 위젯은 차트 라이브러리(Recharts/visx)를 직접 import 안 함. Phase 0 08의 `Sparkline` wrapper만 호출 (헌법 §2 SSOT)
- **Server Component**: 데이터 props 기반. `"use client"` 불필요. 차트 SVG 자체는 SSR 가능(Recharts SSR 옵션 또는 visx 정적 SVG)

### 헌법 §0-1 Step 1 영향 분석

| 변경 대상 | 영향 |
|----------|------|
| Foundation 08 Sparkline props | 본 위젯이 의존. 변경 시 본 자산 + 04 metric-card 옵션 sparkline 슬롯 갱신 |
| 02 `volatilitySeries` 시리즈 길이 (30포인트) | 본 위젯이 그대로 그림. 60포인트로 변경하면 width 재계산 |
| Foundation 07 metric-card sparkline 슬롯 규격 (60×24) | 본 위젯 폭 고정. 변경 시 본 자산 + 04 동기 갱신 |

### 헌법 §0-1 Step 2 합리화 회피

- "위젯이 std 직접 계산": ❌ 같은 시계열을 02·05 둘이 계산하면 SSOT 위반. 02 단독 진입점
- "sparkline 색을 빨강(danger)로 변동성 강조": ❌ 변동성은 절대값이지 위험 직판단 아님. primary 단일 (헌법 §1 — 라벤더 보존 정신, 데이터 시각화 신호색은 별도 토큰 사용)

## Test Strategy

### 단위
- `volatilitySeries.length = 30`, `volatility30d = 1.23` → 카드 표시 `"1.23%"` + 30포인트 sparkline 렌더
- `volatilitySeries.length = 3` → "데이터 부족" placeholder
- `volatilitySeries = []` → "데이터 없음"

### 시각 검증
- Foundation 10 `/dev/preview` Sparkline 회귀 없음
- 08 Integration 후 양 시장 변동성 비교 — NASDAQ이 일반적으로 KOSPI보다 낮은 변동성 (양 시장 절대 비교는 위험하지만 직관 확인)

### 표준 검증 시나리오 (헌법 §0-1 Step 3 — 위젯 빈 데이터/null/외부 API 실패)
- ✅ 빈 데이터: `volatilitySeries = []` → "데이터 없음"
- ✅ null: `volatility30d = null` → "—" + sparkline 자리 빈칸
- ✅ 외부 API 실패: 02가 `errors[]`에 박은 market은 카드 자리 trigger-badge

## Verification

- [ ] `endurance/src/app/dashboard/_components/VolatilitySparkline.tsx` 존재 + Server Component
- [ ] Foundation 08 Sparkline wrapper만 사용 (`grep "recharts\|visx" 본 파일` 0건)
- [ ] `tsc --noEmit` 무경고
- [ ] 단위 테스트 5개 이상 통과 (정상/짧은 시리즈/빈 시리즈/null 스칼라/BOTH)
- [ ] `/dev/preview` Sparkline 회귀 없음
- [ ] 08 Integration 후 실제 `/dashboard` 양 시장 변동성 카드 시각 확인
- [ ] grep으로 본 파일 내 `fetch(`, `yahoo-finance` 0건

## Open Questions

1. **연환산 vs 일일**: 일반 변동성 보고는 연환산. Phase 1은 일일 명시(차원 명확). Phase 2+ 토글 검토
2. **30일 vs 60일 window**: 30일은 빠른 반응 + noise 많음. 60일은 안정 + 늦음. 사용자 검증 후 결정
3. **sparkline 컬러 의미**: 변동성 30일 평균 대비 현재 값이 높으면 빨강·낮으면 초록으로 색 전환할지 → Phase 2+ 검토. Phase 1은 primary 단일
4. **VIX 위젯 별도 추가**: 미국 변동성은 VIX 지수 자체 표시가 더 직관적. 단 Phase 1 scope("yfinance만, 4위젯")에서 5번째 위젯 추가는 위반 → 본 위젯은 일일 std 단일. VIX는 Phase 2+
