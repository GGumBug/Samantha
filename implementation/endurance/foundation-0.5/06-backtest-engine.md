[← README.md로 돌아가기](README.md)

# 06 — Backtest Engine (OOS-expanding window, Stage 1-5, Forward Expectancy)

**위임**: HAL | **위치**: `endurance/scripts/backtest/`, `endurance/src/lib/backtest/`, 산출물 `endurance/data/backtest/<YYYY-MM-DD>/{report.json, equity_curve.csv}` | **의존**: 02 (변수), 03 (라벨링), 05 (inference), 04 (모델 weights)

## Purpose

GEMSTONE EWS 가 production 노출 가치를 갖는지 **시점 정합** 으로 증명. OOS-expanding window backtest 로 2006~2023 기간 가상 운용, 5 단계(Stage 1-5) Forward Expectancy 5-bucket 분포 도출. 본 엔진 결과가 사용자에게 EWS 의 history 표시 + 모델 비교 + Phase 1 위젯의 신뢰도 raw 데이터.

학습 단계(04) 가 "모델이 분류 가능하다" 까지면, 본 엔진은 "신호를 따랐을 때 실제 손실 회피 / 기대값 양수" 까지 증명. 두 단계는 별개 — 분류 성능 좋아도 expectancy 음수면 production 금지.

## 의존성

- **사용하는 자산**: 02 (`gemstone_variables_daily`), 03 (라벨 정의 `labelForwardDrop` TS 미러), 05 (`infer` 시점별 호출), 04 (시점별 모델 — expanding window 마다 retrain 또는 고정 모델 — Step 4 결정)
- **이걸 사용하는 자산**: Phase 1 위젯 (백테스트 history chart, expectancy bucket 게이지)

## Public Interface

```typescript
export interface BacktestConfig {
  startDate: string;           // "2006-01-01" (lookback 보정 후)
  endDate: string;             // "2023-12-31"
  retrainCadence: "never" | "yearly" | "quarterly";  // expanding window 갱신 주기
  initialTrainEndDate: string; // "2010-12-31" — 첫 OOS 시작
  signalThreshold: number;     // 0.5 — probability ≥ 임계 → "위험 신호"
  stages: 5;                   // 고정 (Stage 1-5 정의는 아래 참조)
  forwardHorizons: number[];   // [5, 20, 60, 120, 250] — Forward Expectancy 5 bucket
}

export interface StageOutcome {
  stage: 1 | 2 | 3 | 4 | 5;
  triggers: number;            // 발동 횟수
  hitRate: number;             // forward 하락 적중률
  avgForwardReturn: number;    // 평균 forward return (%)
  expectancyBuckets: Record<number, number>;  // horizon → expectancy
}

export interface BacktestReport {
  config: BacktestConfig;
  totalSignals: number;
  totalDays: number;
  stageOutcomes: StageOutcome[];
  equityCurve: Array<{ date: string; nav: number; signal: 0 | 1 }>;
  metrics: {
    falseAlarmRate: number;
    avoidedDrawdown: number;
    expectancyByBucket: Record<number, number>;
  };
  modelKind: "mlp" | "svm_rbf";
  generatedAt: string;
}

/** 일괄 백테스트 실행 */
export async function runBacktest(config: BacktestConfig): Promise<Result<BacktestReport>>;
```

## Stage 1-5 정의

본 명세는 EWS 신호 강도를 5 단계로 분류:

| Stage | 정의 (probability 구간 + 변수별 z-score sweep) |
|-------|---------------------------------------------|
| 1 | probability < 0.3 — Normal |
| 2 | 0.3 ≤ p < 0.5 — Watch (1개 변수 z > 1.5) |
| 3 | 0.5 ≤ p < 0.7 — Caution (2개 변수 z > 1.5) |
| 4 | 0.7 ≤ p < 0.85 — Warning (3개 변수 z > 2.0) |
| 5 | p ≥ 0.85 — Critical (4+ 변수 z > 2.0) |

Stage 분류 로직은 `endurance/src/lib/backtest/stages.ts` SSOT — Phase 1 위젯이 같은 함수 호출.

## Implementation Notes

- **OOS-expanding window**: `initialTrainEndDate` 까지 train → 다음 `retrainCadence` 기간 OOS 추론 → 새 데이터 추가 후 retrain → 반복. `retrainCadence: "never"` 면 첫 모델 고정 (계산 비용 적음).
- **retrain 비용**: yearly retrain 시 학습 17회 — Python `train.py` 17회 호출 batch. quarterly 면 68회. 첫 PR 은 `never` 로 검증 후 yearly 확장.
- **시점 정합**: t 시점 변수 → t 시점 모델 inference. **t+1 의 모델로 t 추론 금지** (look-ahead bias). expanding window 갱신 시 retrain 종료일 이후 신호만 그 모델 사용.
- **Forward Expectancy 5 bucket**: horizon ∈ {5, 20, 60, 120, 250} 일별 forward return 분포. 신호 발동 시점부터 N일 후 return 평균 — bucket 별 양수면 "EWS 따랐을 때 평균 수익" 증명.
- **falseAlarmRate**: Stage 4-5 발동 후 forward 20d 에서 -5% 하락 0건이면 false alarm. 0~1 비율.
- **equity_curve.csv**: 1.0 시작, 신호 발동 시 cash, 미발동 시 KOSPI200 long — 가장 단순한 정책. 복잡 전략은 Phase 2+.
- **결정론**: 같은 config → 같은 report. random_state 04 와 동일.
- **헌법 §6 escape hatch**: backtest 는 1회성 batch 성격 — 절차적 분석 스크립트 우선. 단, Stage 분류만 TS lib SSOT (Phase 1 위젯 재사용).

## Test Strategy

- **단위**: Stage 분류 함수 — 5 fixture (p + z-score 조합 → 기대 stage)
- **시점 정합 검증**: t 시점 inference 가 t 이전 데이터만 사용함을 fixture 로 증명 (look-ahead bias 회귀 방지)
- **통합**: 2006-2010 train, 2011-2015 OOS 짧은 backtest → report.json 생성, equity_curve 단조성 sanity
- **헌법 §0-1 Step 3 신기능**: ① 정상 ② 모델 결측 → Result.error ③ retrain 실패 시 옛 모델 유지 + 보고 ④ Stage 분류 0건 (모든 날 normal) edge case

## Verification

- [ ] `runBacktest({ retrainCadence: "never", ... })` 실행 시 report.json + equity_curve.csv 생성
- [ ] Stage 1-5 분류 함수가 Phase 1 위젯과 동일 import (SSOT)
- [ ] Forward Expectancy 5 bucket 값 산출 + report.metrics.expectancyByBucket 박힘
- [ ] falseAlarmRate · avoidedDrawdown · totalSignals · 시점별 stageOutcomes 보고
- [ ] 시점 정합 회귀 테스트 green (look-ahead bias 0건)
- [ ] 같은 config → bit-identical report (결정론)

## Open Questions

1. **retrain cadence 결정**: never vs yearly vs quarterly — 계산 비용 vs 모델 fresh 성. 첫 PR `never` 후 비교 실험.
2. **equity curve 정책 단순화 위험**: cash vs KOSPI long 만 — 실제 운용은 부분 hedging, 옵션 등 복잡. Phase 2+ 에서 정책 모듈화.
3. **Stage 임계값 0.3/0.5/0.7/0.85**: 임의값 — 04 calibration curve + 03 positive_rate 결과 보고 조정. 04 머지 후 본 명세 임계값 갱신 가능성.
4. **Forward Expectancy horizons {5, 20, 60, 120, 250}**: 영업일 기준 1주/1개월/3개월/6개월/1년 근사. 한국 영업일 정확 매핑 필요 — `prices_daily` 의 영업일만 카운트.
