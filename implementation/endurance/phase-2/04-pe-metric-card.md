[← README.md로 돌아가기](README.md)

# 04 — P/E·EPS Metric Cards (Phase 2 이관)

**위임**: Joi | **위치**: Phase 2 `/stock/[ticker]` 또는 `/dashboard` 부속 카드 (구현 시점 결정) | **의존**: Foundation 07 `metric-card` 토큰, Phase 1 02 `DashboardMacroBlock` (또는 Phase 2 종목 데이터 API)

## 이관 사유

Phase 1 GEMSTONE EWS 재정의(2026-05-16) 시점에 본 자산은 잉여 위젯으로 판정. GEMSTONE 7 MODEL INPUTS 변수(KOSPI Return Skewness · Volume/Cap · Pairwise Corr · US 10Y-2Y · Fed Policy Uncertainty · WTI · 10Y Expected Inflation)와 **사용자 4 변수(P/E·EPS·Term Spread·Volatility) 매핑 0건** — Term Spread만 GEMSTONE Sapphire와 부분 매칭이고, P/E·EPS·Volatility는 거시 EWS 신호와 직접 연결되지 않음.

본 자산이 진정 가치를 갖는 위치는 **Phase 2 `/stock/[ticker]` 개별 종목 화면** — 가치 평가(P/E)와 성장(EPS Growth)은 거시 EWS가 아닌 종목 단위 fundamental 분석에 속함. 따라서 dashboard/에서 phase-2/로 이관, Phase 2 진입 시 본 명세 재검토 후 종목 페이지 컨텍스트에 맞춰 props·라벨·데이터 출처 갱신.

**v1 구현 코드 처리**: endurance 저장소 24커밋 중 04 관련 4커밋(`PeMetricCards.tsx` + 단위 테스트)은 그대로 보존. Phase 2 진입 시 import 경로만 갱신(`@/app/dashboard/_components` → `@/app/stock/[ticker]/_components` 또는 유지). 컴포넌트 자체 로직 변경 0건 — Foundation 07 `metric-card` wrapper 재사용 패턴이 종목 페이지에서도 유효.

## Purpose

KOSPI·NASDAQ 양 시장의 **12M Forward P/E** 와 **1년 EPS Growth(%)** 을 4매 metric-card grid로 표시한다. Foundation 07에서 박힌 `metric-card` 토큰을 그대로 재사용하며, 본 자산은 **데이터 매핑·레이아웃·null 처리**만 담당한다.

본 위젯은 외부 API를 호출하지 않는다. 02-data-api가 반환한 `DashboardSnapshot.blocks`를 props로 받아 표시만 한다 (헌법 §2 SSOT — 단일 진입점 데이터).

## 의존성

- **사용하는 자산**:
  - Foundation 07 — `metric-card` CSS 토큰 + 컴포넌트 wrapper (`endurance/src/components/metric/MetricCard.tsx`)
  - Phase 1 02 — `DashboardMacroBlock` 타입 (props)
- **이걸 사용하는 자산**: Phase 1 08 (Integration이 grid에 배치)

## Public Interface

```typescript
// src/app/dashboard/_components/PeMetricCards.tsx
import type { DashboardMacroBlock } from "@/lib/dashboard/data";

interface PeMetricCardsProps {
  blocks: DashboardMacroBlock[]; // 1~2개 (market 선택에 따라)
}

export function PeMetricCards({ blocks }: PeMetricCardsProps): JSX.Element;
```

표시 형태 (BOTH 시 2×2 grid, 단일 시장 시 1×2 grid):

```
┌─────────────────────────┬─────────────────────────┐
│ KOSPI 12M FWD P/E       │ KOSPI EPS Growth 1Y     │
│ 12.3×                   │ +8.4%                   │
│ (delta vs 30d 평균)      │ (delta vs 30d 평균)      │
├─────────────────────────┼─────────────────────────┤
│ NASDAQ 12M FWD P/E      │ NASDAQ EPS Growth 1Y    │
│ 28.6×                   │ +14.7%                  │
└─────────────────────────┴─────────────────────────┘
```

### 각 카드 props (Foundation 07 `metric-card` 토큰 매핑)

| metric-card 슬롯 | P/E 카드 | EPS Growth 카드 |
|------------------|---------|----------------|
| Label | "KOSPI · 12M FWD P/E" / "NASDAQ · 12M FWD P/E" | "KOSPI · EPS Growth 1Y" / "NASDAQ · EPS Growth 1Y" |
| Value | `12.3×` (소수 1자리 + ×) | `+8.4%` (부호 + 소수 1자리 + %) |
| Delta | 직전 30일 이동평균 대비 차이 (옵션) | 직전 30일 이동평균 대비 차이 (옵션) |
| Sparkline | 없음 (05가 별도 위젯으로 담당) | 없음 |

## Implementation Notes

- **null/undefined 처리**: `pe12mForward === null` 시 값을 `"—"` 로 표시 + delta 영역 빈칸. 헌법 §0-1 Step 3 (위젯 표준 검증 시나리오 — 빈 데이터)
- **숫자 포맷팅**: 12M P/E는 `(x).toFixed(1) + "×"`. EPS Growth는 부호 포함 (`+8.4%` / `-3.2%`). `Intl.NumberFormat` 사용해 locale 처리 (현재 ko-KR 단일)
- **데이터 흐름 SSOT (헌법 §2-0-1)**: props로 받은 `DashboardMacroBlock`은 **숫자 필드만** 보유. UI 표시 텍스트("KOSPI · 12M FWD P/E")는 본 컴포넌트 내부에서 매핑. **caller가 string 텍스트를 props로 박아 넘기지 않음**
- **i18n 미적용 상태**: 현재 Phase 1은 한국어 단일. 추후 i18n 도입 시 `labelKey: "dashboard.metric.kospi.pe"` 형태로 키 보존 props로 마이그레이션 의무 (헌법 §2-0-1 Pattern A·B 적용)
- **Foundation 07 토큰 재사용 의무**: 본 컴포넌트는 `<MetricCard label={...} value={...} delta={...} />` 형태로 Phase 0 wrapper를 호출만. 자체 CSS 0줄 (헌법 §5 — 토큰만 재사용)
- **Server Component**: 데이터는 props로 들어옴. `"use client"` 불필요

### 헌법 §0-1 Step 1 영향 분석

| 변경 대상 | 영향 |
|----------|------|
| Foundation 07 `MetricCard` props 시그니처 | 본 컴포넌트가 의존. 변경 시 본 자산 + 05 위젯도 갱신 |
| 02 `DashboardMacroBlock.pe12mForward, epsGrowth1y` | 본 컴포넌트가 직접 읽음. 02 명세 변경 시 본 자산 동기 갱신 |

### 헌법 §0-1 Step 2 합리화 회피

- "null 처리 생략하고 0 표시": ❌ 0과 데이터 미존재는 차원 다름. 사용자 의사결정 왜곡 → `—` 의무
- "P/E 값을 string으로 박아 props 전달": ❌ 헌법 §2-0-1 데이터 흐름 string snapshot 금지. 숫자 props + 컴포넌트 내부 포맷팅

## Test Strategy

### 단위
- `pe12mForward = 12.34` → 표시 `"12.3×"`
- `epsGrowth1y = -3.21` → 표시 `"-3.2%"` (음수 부호 + danger 색)
- `pe12mForward = null` → 표시 `"—"` + delta 영역 빈칸
- BOTH (blocks 2개) → 4매 카드. KR only (blocks 1개) → 2매 카드

### 시각 검증
- Foundation 10 `/dev/preview` Section 3 metric-card 회귀 없음
- 08 Integration 후 `/dashboard?market=BOTH` 직접 확인 — KOSPI vs NASDAQ P/E 차이가 직관적으로 비교되는지

### 표준 검증 시나리오 (헌법 §0-1 Step 3 — 위젯 빈 데이터/null/외부 API 실패)
- ✅ 빈 데이터: `blocks=[]` → "데이터 없음" placeholder
- ✅ null: `pe12mForward = null` → `—` 표시
- ✅ 외부 API 실패: 02가 `errors[]`에 KR 실패 박은 경우, KOSPI 카드 자리에 trigger-badge로 에러 가시 (헌법 §4 부수효과 가시화)

## Verification

- [ ] `endurance/src/app/dashboard/_components/PeMetricCards.tsx` 존재 + Server Component (no `"use client"`)
- [ ] Foundation 07 `MetricCard` wrapper만 사용 (`grep "metric-card\|MetricCard"` 본 파일에서 발견)
- [ ] `tsc --noEmit` 무경고
- [ ] 단위 테스트 6개 이상 통과 (정상/null/음수/빈배열/BOTH/KR-only)
- [ ] `/dev/preview` Section 3 metric-card 회귀 없음 (시각 비교)
- [ ] 08 Integration 후 실제 `/dashboard` 양 시장 P/E 비교 시각 확인
- [ ] grep으로 본 파일 내 `fetch(`, `yahoo-finance`, `axios` 0건 (위젯이 외부 호출 안 함)

## Open Questions

1. **Delta 기준선**: "30일 이동평균 대비" vs "전일 대비". 30일은 변동성 적어 신호 약하지만 noise 덜함. 전일은 매일 변하지만 의미 적음. → Phase 1 초기 30일, Phase 4 사용자 토글 검토
2. **EPS Growth 음수 임계점 색**: 0% 이하 즉시 danger인지, -5% 이하부터 danger인지. 디자인 시스템 토큰 회의 후 결정
3. **모바일 grid**: 375px 폭에서 2×2 grid가 좁아짐. 1×4 세로 stack으로 전환할지 → 08-integration responsive 명세에서 결정
4. **NASDAQ 100 vs S&P 500**: 본 명세는 `^IXIC`(NASDAQ Composite) 기준. NASDAQ-100(`^NDX`)이 12M FWD P/E 일반 비교 대상이라는 의견 가능 → Open. tl-dr SSOT는 NASDAQ로만 명시
