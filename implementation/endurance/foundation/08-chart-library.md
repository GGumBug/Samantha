[← README.md로 돌아가기](README.md)

# 08 — Chart Library 결정 + Wrapper

**위임**: Joi | **위치**: `src/components/chart/` | **의존**: 07-design-tokens

## Purpose

차트는 데이터 대시보드의 주인공이지만 **잘못 선택하면 후속 페이지 모두에 빚이 남는다**. Recharts·visx·lightweight-charts·ECharts 중 다크 캔버스 호환성·번들 크기·확장성·번들 SSR 친화성을 종합 평가하여 1개 라이브러리를 박는다. 결정 후 디자인 시스템 토큰을 적용한 wrapper 컴포넌트(`<LineChart>`, `<AreaChart>`, `<BarChart>`)를 제공한다.

## 의존성

- **사용하는 자산**: 07-design-tokens (`chart-container` 토큰)
- **이걸 사용하는 자산**: `/dashboard`, `/sectors`, `/stock/[ticker]`, `metric-card` sparkline

## 후보 비교

| 라이브러리 | 번들 (gzip) | SSR | 다크 호환 | 학습 비용 | 라이센스 | 권장도 |
|----------|------------|-----|---------|---------|---------|------|
| **Recharts** | ~95 KB | ✓ (SSR-safe) | 색 props로 쉬움 | 낮음 | MIT | ⭐ 1차 후보 |
| **visx** | tree-shake (~30-60 KB) | ✓ | 직접 그림 (자유도 높음) | 중간 | MIT | 2차 (custom 많을 때) |
| **lightweight-charts** | ~40 KB | △ (canvas) | 금융 차트 특화 | 낮음 | Apache 2.0 | candle/볼밴 특화시 |
| **ECharts** | ~300 KB | △ | 풍부 | 중간 | Apache 2.0 | 비추 (번들 큼) |

## 시니어 결정: **Recharts 1차 + lightweight-charts 후속 검토**

### 결정 이유

1. **번들 95KB는 허용 가능**: 데이터 대시보드에서 차트는 핵심 가치 → 번들 비용 정당화
2. **SSR-safe**: Next.js App Router에서 `<LineChart>` 가 서버 컴포넌트로 렌더 가능 (lightweight-charts는 canvas라 client-only)
3. **선언적 API**: React 패턴과 일치, Joi가 maintain 쉬움
4. **다크 캔버스 즉시 호환**: 색상은 props로 받으므로 `{colors.primary}` 그대로 주입 가능
5. **MIT 라이센스**: 상업·수정 자유

### lightweight-charts 후속 검토 시점

- candle 차트(/stock/[ticker])에서 Recharts 성능 한계 발견 시
- 또는 1만+ 데이터 포인트 + 인터랙티브 줌이 필요해질 때
- Phase 1 dashboard에서는 Recharts로 충분

## Wrapper 명세

```typescript
// src/components/chart/LineChart.tsx
import type { ReactNode } from 'react';

export interface ChartSeries {
  name: string;
  data: Array<{ x: string | number; y: number }>;
  color?: string;        // 미지정 시 라벤더 명도 시퀀스 자동 할당
  strokeWidth?: number;  // 기본 2px
}

export interface LineChartProps {
  title?: string;
  series: ChartSeries[];
  xAxisLabel?: string;
  yAxisLabel?: string;
  height?: number;       // 기본 280px
  showGrid?: boolean;    // 기본 true
  showLegend?: boolean;  // 기본 series.length > 1
  formatY?: (v: number) => string;  // 천 단위 콤마 등
  className?: string;
}

export function LineChart(props: LineChartProps): JSX.Element;
```

동일 시그니처 패턴으로:
- `<AreaChart>` — 영역 그래프 (포트폴리오 누적 수익)
- `<BarChart>` — 막대 (섹터 수익률, 분기 EPS)
- `<Sparkline>` — metric-card 우측 미니 차트 (axis 없음, 60×24px 기본)

## Implementation Notes

### 색상 자동 할당

다중 시리즈일 때 색상 미지정이면 라벤더 명도 시퀀스 적용:

```typescript
const SERIES_COLORS = [
  'var(--color-primary)',         // #5e6ad2 라벤더
  'var(--color-primary-hover)',   // #828fff 밝은 라벤더
  '#a5acff',                      // 더 밝은 라벤더
  '#4a55b3',                      // 어두운 라벤더
];
```

다중 시리즈에서도 라벤더 단일 색조 유지 → 시각적 일관성. 무지개 색 도입 금지 (헌법 §디자인).

### Tooltip 토큰 적용

```typescript
<Tooltip
  contentStyle={{
    background: 'var(--color-surface-2)',
    border: '1px solid var(--color-hairline-strong)',
    borderRadius: 'var(--radius-md)',
    padding: '8px 12px',
  }}
  labelStyle={{ color: 'var(--color-ink-subtle)' }}
  itemStyle={{ color: 'var(--color-ink)' }}
/>
```

모든 wrapper에 동일 tooltip 스타일 — 헌법 §2 SSOT 적용. 인라인 hex 사용 금지.

### 반응형

- `<ResponsiveContainer width="100%" height={props.height ?? 280}>` 으로 폭 자동
- 모바일(<768px)에서 axis label 폰트 11px → 데스크톱 12px
- 격자선은 모바일에서 더 옅게 (`opacity 0.5`)

### Sparkline 특수 처리

```typescript
<Sparkline
  data={[{x: '2025-01', y: 100}, ...]}
  width={60} height={24}
  showAxis={false} showTooltip={false}
/>
```

격자·축·툴팁 모두 비활성. 단일 라인만. metric-card 안에서만 사용.

## Test Strategy

- 시각 검증: 10-preview-page에 LineChart/AreaChart/BarChart/Sparkline 4종 모두 렌더
- 다크 캔버스 일관성: 차트 영역의 background, grid, axis 색이 토큰 변수만 사용 (인라인 hex 0건 grep)
- 다중 시리즈 자동 색: 색 미지정 3개 시리즈가 라벤더 명도 시퀀스로 자동 표현
- 반응형: 320px / 768px / 1280px 폭에서 차트가 깨지지 않음
- 한글 라벨: x축 한글 카테고리 (예: "1월", "2월") 가독성 확인

## Verification

- [ ] `npm install recharts` 완료
- [ ] `src/components/chart/{LineChart,AreaChart,BarChart,Sparkline}.tsx` 작성
- [ ] 모든 wrapper가 토큰 변수만 사용 — `grep -rE "#[0-9a-f]{3,6}" src/components/chart/` 결과 0건
- [ ] preview-page에서 4종 차트 시각 확인
- [ ] 번들 크기 측정: `npm run build` 후 차트 컴포넌트 chunk size < 100KB gzip
- [ ] SSR 검증: 차트가 server component에서 렌더되는지 (HTML 응답에 SVG 포함 확인)

## Open Questions

1. **candlestick 차트**: `/stock/[ticker]` 에 캔들 차트 필요하면 Recharts로 직접 구현 가능 (커스텀). 또는 Phase 2 시점에 lightweight-charts 도입 검토 — Phase 0 범위 외
2. **차트 다운로드(PNG/SVG)**: 사용자가 차트를 이미지로 저장하고 싶을 수 있음. html2canvas 또는 SVG → PNG 변환. Phase 3+ 검토
3. **인터랙티브 줌·팬**: Recharts의 brush 기능으로 시작. 필요 시 lightweight-charts로 교체
