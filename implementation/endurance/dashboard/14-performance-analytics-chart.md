[← README.md로 돌아가기](README.md)

# 14 — PERFORMANCE ANALYTICS 누적수익률 차트 + 메트릭 3종 (자산 D)

**위임**: Joi | **위치**: `endurance/src/app/dashboard/_components/PerformanceAnalyticsChart.tsx` (Server Component) | **의존**: Foundation 07 `chart-container` + `metric-card` 토큰, Foundation 08 LineChart wrapper, Phase 0.5 06 backtest engine OOS equity curve, Phase 1 02 `DashboardGemstoneBlock.performance`

## Purpose

GEMSTONE EWS의 **백테스트 신뢰성**을 시각화. 좌측 누적수익률 라인 차트(EWS 신호 따른 NAV vs 벤치마크 NAV) + 우측 3개 메트릭 카드(누적수익률 vs BM · Sharpe · Max Drawdown). OOS-expanding window (2011~) 데이터 기반 — 사용자가 "이 모델이 실전에서 얼마나 검증됐나"를 한 눈에 확인.

본 위젯은 데이터 페치 0건. Phase 0.5 06이 생성한 `BacktestReport.equityCurve` + `metrics` → 02가 시점별 합쳐 `performance.equityCurve` + `performance.metrics`로 전달.

## 의존성

- **사용하는 자산**:
  - Foundation 07 `chart-container` + `metric-card` 토큰
  - Foundation 08 `LineChart` wrapper (다중 시리즈 — NAV + benchmark NAV)
  - Phase 1 02 `DashboardGemstoneBlock.performance`
  - (간접) Phase 0.5 06 `BacktestReport.equityCurve` — 02가 로드
- **이걸 사용하는 자산**: Phase 1 08 (Integration — grid 좌중에 배치, 자산 D)

## Public Interface

```typescript
// src/app/dashboard/_components/PerformanceAnalyticsChart.tsx
import type { DashboardGemstoneBlock } from "@/lib/dashboard/data";

interface PerformanceAnalyticsChartProps {
  blocks: DashboardGemstoneBlock[]; // 1~2개
  heightPx?: number;                // default 280
}

export function PerformanceAnalyticsChart(
  props: PerformanceAnalyticsChartProps,
): JSX.Element;
```

표시 형태:

```
┌────────────────────────────────────────────────────────────────┐
│ PERFORMANCE ANALYTICS (KOSPI200 · OOS 2011~)                   │
│                                                                 │
│ NAV                                              EWS ── BM ──    │
│  2.5 ─                              ╱──╲                        │
│  2.0 ─                    ╱──╲    ╱      ╲                      │
│  1.5 ─          ╱──╱──╲  ╱      ╲╱        ╲──                   │
│  1.0 ───────────                                                 │
│        2011                                          today      │
│                                                                 │
│ ┌──────────────┬────────────┬─────────────────┐                 │
│ │ Cum Ret vs BM│ Sharpe     │ Max Drawdown    │                 │
│ │ +38.2%       │ 1.42       │ -18.4%          │                 │
│ └──────────────┴────────────┴─────────────────┘                 │
└────────────────────────────────────────────────────────────────┘
```

data-testid:
- root: `widget-performance-analytics`
- 차트 컨테이너: `performance-equity-chart`
- 메트릭 카드 3종: `performance-metric-cumulative-return`, `performance-metric-sharpe`, `performance-metric-mdd`

## Implementation Notes

- **Foundation 08 LineChart wrapper만 사용**: Recharts/visx 직접 import 0건. 시리즈 2종(`name: "EWS"` + `name: "Benchmark"`) overlay.
- **메트릭 포맷팅**:
  - Cumulative Return: 부호 + 소수 1자리 + `%` (음수 시 danger 색)
  - Sharpe: 소수 2자리. 1.0+ success, 0.5+ neutral, 미만 ink-muted
  - Max Drawdown: 부호(항상 음수) + 소수 1자리 + `%` (모두 danger 계열)
- **시계열 길이**: `equityCurve.length` 가변 — OOS 시작일(2011~) 기준이라 ~3000+ 포인트. LineChart wrapper가 dense series 처리 (downsampling 옵션 Foundation 08에 박혀 있어야 함 — 없으면 명세 갱신 의무).
- **시리즈 색**: EWS 시리즈 = `{colors.primary}` (라벤더), Benchmark = `{colors.ink-muted}` 회색. 헌법 §1 라벤더 보존 정신 — primary 단일 시리즈, BM은 회색 차분.
- **BOTH 처리**: 두 시장 차트 횡 배치 또는 stack. Phase 0.5 08 preview에서 시각 결정.
- **빈 데이터 처리**: `equityCurve.length < 30` → "백테스트 결과 없음" placeholder.

### 헌법 §0-1 Step 1 영향 분석

| 변경 대상 | 영향 |
|----------|------|
| Phase 0.5 06 `equity_curve.csv` 스키마 + `metrics` 산출 | 02가 로드. 변경 시 02 + 본 자산 갱신 |
| 02 `performance` 시그니처 | 본 위젯이 props로 받음 |
| Foundation 08 LineChart `connectNulls` / `downsampling` | 본 위젯이 의존 (수천 포인트). 미지원 시 Foundation 08 명세 갱신 의무 |

### 헌법 §0-1 Step 2 합리화 회피

- "메트릭을 위젯 내부에서 equityCurve로 계산": ❌ Phase 0.5 06 산출 SSOT. 본 위젯은 표시만 (헌법 §2)
- "음수 Sharpe 별도 처리 안 함": ❌ 음수 Sharpe는 strategy failure 신호. 색 분기 + tooltip 의무

## Test Strategy

### 단위
- `equityCurve.length=3000, metrics.sharpe=1.42` → 차트 + 메트릭 카드 3매 렌더
- `metrics.cumulativeReturnVsBenchmark=-5.2` → danger 색 + `-5.2%`
- `equityCurve=[]` → placeholder
- BOTH (`blocks=[KR, US]`) → 두 차트 + 두 메트릭 set

### 표준 검증 시나리오 (헌법 §0-1 Step 3 — 위젯 빈 데이터/null)
- 정상 + 빈 + null + BOTH + i18n (caller-driven string 0건 grep)
- anti-pattern §2-0-1 Pattern A·B grep 0건

### 시각 검증
- `/dev/preview` Section에 본 위젯 렌더 — 차트 라인 2종 + 메트릭 3카드 정상

## Verification

- [ ] `endurance/src/app/dashboard/_components/PerformanceAnalyticsChart.tsx` 존재 + Server Component
- [ ] Foundation 08 LineChart wrapper만 사용 (`grep "recharts\|visx"` 본 파일 0건)
- [ ] Foundation 07 metric-card 토큰 적용 (hex 인라인 0건)
- [ ] `tsc --noEmit` 무경고
- [ ] data-testid 4종(root + chart + 3 metric) 박힘
- [ ] 단위 테스트 6개 이상 (정상/빈/음수 metric/BOTH/시리즈 길이 edge)
- [ ] anti-pattern §2-0-1 grep 0건

## Open Questions

1. **OOS 시작일 명시**: 차트 제목에 "OOS 2011~" 박을지 vs tooltip. 신뢰도 가시화엔 박는 게 유리.
2. **벤치마크 정의**: KOSPI200 시장은 KOSPI200 자체 BM, S&P 500 시장은 S&P 500 자체 BM. 02가 02 v2 시그니처에서 박음 (`equityCurve.benchmarkNav`).
3. **차트 dense series 처리**: Foundation 08 LineChart wrapper downsampling 미지원 시 어디서 처리할지 — 02 영역? 위젯 영역? 헌법 §2 SSOT는 02 권장.
4. **모바일 차트 높이**: 280px 데스크톱, 모바일에서 어떻게 좁힐지 — Phase 0.5 08 preview에서 결정.
