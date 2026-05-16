[← README.md로 돌아가기](README.md)

# 13 — FORWARD EXPECTANCY 5 bucket 표 (자산 C)

**위임**: Joi | **위치**: `endurance/src/app/dashboard/_components/ForwardExpectancyTable.tsx` (Server Component) | **의존**: Foundation 07 `data-table-row` 토큰, Phase 0.5 06 backtest engine 통계 출력, Phase 1 02 `DashboardGemstoneBlock.forwardExpectancy`

## Purpose

GEMSTONE EWS 신호 발동 시 **N일 후 예상 수익률(Forward Expectancy)** 을 5 horizon bucket(5d / 20d / 60d / 120d / 250d)으로 표시. 사용자가 "신호 따랐을 때 어느 horizon에서 가장 큰 기대값"인지 직관적으로 인식하도록 표 형태로 박는다.

본 위젯은 데이터 페치 0건. Phase 0.5 06 백테스트 엔진이 생성한 `BacktestReport.metrics.expectancyByBucket` + `stageOutcomes`를 02-data-api가 시점별 합산해 `forwardExpectancy.buckets[]`로 전달.

## 의존성

- **사용하는 자산**:
  - Foundation 07 `data-table-row` 토큰 (정렬·필터 가능한 표 행, TanStack Table 통합 wrapper)
  - Phase 1 02 `DashboardGemstoneBlock.forwardExpectancy.buckets[]`
  - (간접) Phase 0.5 06 `BacktestReport` — 02가 로드, 본 위젯은 정규화된 결과만 받음
- **이걸 사용하는 자산**: Phase 1 08 (Integration — grid 우상에 배치, 자산 C)

## Public Interface

```typescript
// src/app/dashboard/_components/ForwardExpectancyTable.tsx
import type { DashboardGemstoneBlock } from "@/lib/dashboard/data";

interface ForwardExpectancyTableProps {
  blocks: DashboardGemstoneBlock[]; // 1~2개
}

export function ForwardExpectancyTable(
  props: ForwardExpectancyTableProps,
): JSX.Element;
```

표시 형태 (단일 시장 — BOTH 시 두 표 횡 배치 또는 시장 컬럼 추가):

```
┌──────────────────────────────────────────────────┐
│ FORWARD EXPECTANCY (KOSPI200)                    │
│ ┌─────┬───────────┬──────────┬──────────────┐    │
│ │ Day │ Expectancy│ Hit Rate │ Sample Size  │    │
│ ├─────┼───────────┼──────────┼──────────────┤    │
│ │ 5d  │ +0.8%     │ 62%      │ 124          │    │
│ │ 20d │ +2.4%     │ 58%      │ 124          │    │
│ │ 60d │ +5.1%     │ 64%      │ 120          │    │
│ │ 120d│ +7.3%     │ 71%      │ 116          │    │
│ │ 250d│ +9.8%     │ 68%      │ 104          │    │
│ └─────┴───────────┴──────────┴──────────────┘    │
└──────────────────────────────────────────────────┘
```

data-testid:
- root: `widget-forward-expectancy`
- (옵션) 행: `forward-expectancy-row-{horizonDays}` (단위 테스트에서 호출)

## Implementation Notes

- **단순 표 — TanStack Table 도입 미필요**: 5행 고정·정렬 불필요. Foundation 07 `data-table-row` CSS 토큰만 적용한 정적 `<table>` 충분. 헌법 §5 — TanStack은 동적 데이터·정렬·필터가 있을 때만. Phase 1 단계는 정적.
- **숫자 포맷팅**:
  - Expectancy: 부호 + 소수 1자리 + `%` (음수 시 danger 색)
  - Hit Rate: 정수 + `%` (50% 이상 success 색, 미만 ink-muted)
  - Sample Size: 정수 (1000+ 시 `1.2k` 압축)
- **horizon 라벨**: `5d` / `20d` / `60d` / `120d` / `250d` — 영업일 기준 약 1주/1개월/3개월/6개월/1년. 라벨은 컴포넌트 내부 i18n key (`forwardExpectancy.horizon.5d` 등) 권장.
- **빈 데이터 처리**: `buckets.length === 0` → "샘플 부족" placeholder. Phase 0.5 06 백테스트 미완료 또는 신호 0건일 때.
- **BOTH 처리**: 두 시장 표 횡 배치 (mobile/tablet 시 세로 stack). 또는 단일 표에 "Market" 컬럼 추가 (10행) — 사용자 검증 후 결정.

### 헌법 §0-1 Step 1 영향 분석

| 변경 대상 | 영향 |
|----------|------|
| Phase 0.5 06 `expectancyByBucket` 스키마 | 02 v2가 로드, 본 위젯이 props로 받음. 변경 시 02 + 본 자산 갱신 |
| 02 `forwardExpectancy.buckets[]` 시그니처 | 본 위젯이 직접 읽음. 변경 시 본 자산 갱신 |
| Foundation 07 `data-table-row` 토큰 | 본 위젯이 적용. 토큰 변경 시 시각 회귀 |

### 헌법 §0-1 Step 2 합리화 회피

- "Expectancy 값을 02가 string으로 박아 전달": ❌ caller-driven UI string snapshot (§2-0-1). 숫자 props + 컴포넌트 내부 포맷팅
- "5d/20d/60d/120d/250d 라벨을 02가 박아 전달": ❌ 동일. i18n key 박혀야 (`forwardExpectancy.horizon.*`)

## Test Strategy

### 단위
- `buckets=[{horizonDays:5, expectancy:0.8, hitRate:0.62, sampleSize:124}, ...]` → 5행 렌더 + 포맷팅
- `expectancy=-2.3` → 표시 `-2.3%` + danger 색
- `hitRate=0.5` → 표시 `50%` + threshold 색 분기
- `buckets=[]` → "샘플 부족" placeholder

### 표준 검증 시나리오 (헌법 §0-1 Step 3 — 위젯 빈 데이터/null)
- 정상: 5행 표 + 정확한 포맷팅
- 빈: `buckets=[]` → placeholder
- BOTH: `blocks=[KR, US]` → 두 표 횡 배치 또는 시장 컬럼 통합
- i18n: 마운트 중 언어 토글 시 horizon 라벨 자동 갱신 (caller-driven string 0건 grep)
- anti-pattern §2-0-1 grep 0건

### 시각 검증
- `/dev/preview` Section (Phase 0.5 08 GEMSTONE preview)에 본 위젯 정상/빈 두 상태 렌더

## Verification

- [ ] `endurance/src/app/dashboard/_components/ForwardExpectancyTable.tsx` 존재 + Server Component
- [ ] Foundation 07 `data-table-row` 토큰 적용 (hex 인라인 0건)
- [ ] `tsc --noEmit` 무경고
- [ ] data-testid `widget-forward-expectancy` 박힘
- [ ] 단위 테스트 5개 이상 (5행 정상/음수 expectancy/0% hit rate/빈/BOTH)
- [ ] anti-pattern §2-0-1 grep 0건 (label·horizon 필드 string 0건, 키 보존)
- [ ] grep으로 본 파일 내 `fetch(`, `yahoo-finance`, TanStack Table 0건

## Open Questions

1. **BOTH 표시 — 횡 배치 vs 단일 표 시장 컬럼**: 시각 결정 후 v2 갱신.
2. **Hit Rate threshold 색 분기**: 50% 기준 단순 분기 vs gradient. 초안은 단순 분기 (헌법 §5).
3. **Sample Size 압축**: 1000+ 시 `1.2k` vs `1,200` — 좁은 공간에서 가독성 검증.
4. **horizon 5개 외 추가**: Phase 0.5 06이 `forwardHorizons: [5, 20, 60, 120, 250]` 고정. 추가 시 양쪽 명세 동기.
