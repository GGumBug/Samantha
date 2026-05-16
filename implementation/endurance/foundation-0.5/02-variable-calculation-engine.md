[← README.md로 돌아가기](README.md)

# 02 — Variable Calculation Engine (7 GEMSTONE 변수)

**위임**: HAL | **위치**: `endurance/src/lib/gemstone/variables/`, DB 테이블 `gemstone_variables_daily` | **의존**: 01 (Data Collection Pipeline), Foundation 02 (DB Schema)

## Purpose

수집된 raw 시계열을 GEMSTONE 7 변수의 **일별 스칼라 값**으로 변환하는 결정론적 계산 엔진. 각 변수는 입력 시점에 따라 계산 가능한 최소 lookback window 가 다름(Skewness 60d, Pairwise Corr 20d 등) — 본 엔진이 SSOT 로 lookback·정규화·결측 처리 규칙을 박는다.

03 학습 데이터셋과 05 inference 어댑터가 동일 함수를 호출 — train/serve skew 방지(헌법 §2 SSOT). Python 학습 스크립트(04)도 본 엔진 출력 DB row 를 직접 읽음, 별도 재계산 금지.

## 의존성

- **사용하는 자산**: 01 (raw `prices_daily`, `macro_series`), Foundation 02 (DB 마이그레이션 — `gemstone_variables_daily` 신규 테이블)
- **이걸 사용하는 자산**: 03 (학습 데이터셋), 05 (inference 어댑터), 06 (백테스트 엔진)

## Public Interface

```typescript
export interface GemstoneVariables {
  date: string;                          // ISO date
  kospiReturnSkewness: number;           // 1. 60d rolling skewness
  kospiVolumeMcapRatio: number;          // 2. 일별 거래대금 / 시총
  kospiPairwiseCorr: number;             // 3. KOSPI200 상위 30종목 20d 평균 상관
  us10y2ySpread: number;                 // 4. T10Y2Y (%)
  fedPolicyUncertainty: number;          // 5. MOVE Index 또는 T-Bill vol
  wtiSpot: number;                       // 6. WTI 종가 (USD)
  expectedInflation10y: number;          // 7. T10YIE (%)
}

/** 단일 날짜 변수 계산 */
export async function computeGemstoneVariables(
  date: string
): Promise<Result<GemstoneVariables>>;

/** 범위 일괄 계산 (백필 + incremental sync) */
export async function backfillGemstoneVariables(params: {
  startDate: string;
  endDate: string;
}): Promise<Result<{ rowsInserted: number }>>;

/** sync-scheduler step — 어제분 변수 계산 */
export async function syncYesterdayVariables(): Promise<SyncStepReport>;
```

## Implementation Notes

- **lookback window SSOT**: 각 변수별 윈도우·정규화는 `endurance/src/lib/gemstone/variables/config.ts` 상수 객체. 04 학습 스크립트도 같은 상수를 Python 으로 미러 (config 변경 시 양쪽 동기 — drift 방지).
- **결측 처리**: 휴장일은 skip(이전 영업일 값 carry-forward 안 함). 변수 row 는 영업일에만 존재. KR/US 휴장이 엇갈리는 날은 가용 변수만 row 에 박고 결측은 NULL — 03 학습 데이터셋에서 처리.
- **변수 1 (Return Skewness)**: KOSPI200 일별 수익률 60일 rolling skewness (`scipy.stats.skew` 와 동일 공식 — `g1` adjusted).
- **변수 3 (Pairwise Corr)**: KOSPI200 시총 상위 30종목 일별 수익률 → 20d rolling pairwise correlation matrix → 비대각 평균. 30종목 리스트는 분기 갱신(01 의 universe).
- **변수 5 (Fed Policy Uncertainty)**: MOVE Index 우선, 없으면 3M T-Bill 60d rolling std. 어느 쪽을 쓰는지 row 메타데이터(`source: "MOVE" | "TBILL"`) 박음 — 04 학습 시 가시화.
- **결정론**: 같은 입력 → 같은 출력. `Date.now()`·`Math.random()` 사용 금지 (헌법 §4 결정론 체크리스트).
- **헌법 §6 escape hatch**: scipy.stats.skew 미러는 TS 로 numerical recipe 직접 작성 — 외부 lib 도입 안 함 (의존성 무게 회피, 헌법 §5).

## Test Strategy

- **단위**: 변수별 golden fixture — 인공 시계열 입력 → 기댓값 검증. 7 변수 × 3 fixture = 21 케이스.
- **Python parity**: TS skewness 와 Python `scipy.stats.skew(...,bias=False)` 가 1e-9 이내 일치 (`scripts/ml/parity-check.py`).
- **결측 시나리오**: KR 휴장 / US 휴장 / 둘 다 휴장 → row 일관성
- **헌법 §0-1 Step 3 신기능**: ① 정상 ② 60d lookback 부족 (초기 60일) → NULL/skip ③ 데이터 source 결측 → 부분 row

## Verification

- [ ] `gemstone_variables_daily` 테이블 생성 (date PK, 7 변수 + `policyUncertaintySource` 메타)
- [ ] 7 변수 함수 모두 export, `Result<T>` 일관성
- [ ] backfill 2005-04-01 ~ today 완료 (lookback 60d 보정 후 ≈ 2005-04-01 부터)
- [ ] Python parity check 7 변수 모두 1e-9 이내
- [ ] sync-scheduler 에 `syncYesterdayVariables` step 등록
- [ ] golden fixture 21 케이스 green

## Open Questions

1. **KOSPI200 상위 30종목 변경 시점 처리**: 분기 갱신 시 lookback window 가 종목 변경 경계를 가로지르면 corr 계산이 왜곡. 변경일 이전은 옛 universe, 이후는 새 universe — 명확히 박을지 vs 변경일 ±20d 결측 처리. 04 학습 시 영향 측정 후 결정.
2. **변수 정규화 시점**: z-score 정규화는 본 엔진에서 할지 03 학습 데이터셋에서 할지. **03 에서 하기로 결정** — train/test split 시 leak 방지(scaler fit 은 train only).
3. **MOVE Index 폐기 위험**: 시리즈가 끊기면 T-Bill 대용으로 자동 fallback 할지 alert 만 띄울지. fallback 시 학습 모델 재훈련 필요 — 본 엔진은 source 메타만 박고, 04 가 모니터링.
