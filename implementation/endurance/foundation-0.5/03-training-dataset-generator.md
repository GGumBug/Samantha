[← README.md로 돌아가기](README.md)

# 03 — Training Dataset Generator (feature matrix + 라벨링 + split)

**위임**: HAL + GERTY | **위치**: `endurance/scripts/ml/build_dataset.py`, 산출물 `endurance/data/training/<YYYY-MM-DD>/{train.parquet, test.parquet, scaler.json}` | **의존**: 02 (변수 계산 엔진), 01 (raw 가격 — 라벨링용)

## Purpose

02 가 박은 일별 GEMSTONE 변수 row 를 **ML 학습 가능한 feature matrix + label 벡터**로 변환. OOS-expanding window 의 첫 train fold 산출물을 박고, 라벨링 정책(forward N일 KOSPI 하락 임계)·정규화(z-score scaler fit on train only)·train/test split 을 본 자산에서 결정한다.

학습(04)·백테스트(06) 양쪽이 본 생성기를 호출 — 라벨 정의·정규화가 한 곳 SSOT 보장(헌법 §2). 변경 시 영향 grep 으로 04·06 모두 갱신.

## 의존성

- **사용하는 자산**: 02 (`gemstone_variables_daily` 읽기), 01 (KOSPI200 forward return 계산용 `prices_daily`)
- **이걸 사용하는 자산**: 04 (학습 스크립트), 06 (백테스트 — 시점별 expanding train set 재생성)

## Public Interface (Python)

```python
# endurance/scripts/ml/build_dataset.py

from dataclasses import dataclass
from typing import Literal

@dataclass
class DatasetConfig:
    start_date: str            # "2005-04-01"
    train_end_date: str        # "2018-12-31"
    test_end_date: str         # "2023-12-31" (OOS)
    label_horizon_days: int    # 20 (forward 1개월)
    label_threshold_pct: float # -5.0 (KOSPI200 -5% 이상 하락 → 1)
    label_kind: Literal["binary_drop", "forward_return"] = "binary_drop"

def build_dataset(config: DatasetConfig) -> dict:
    """
    Returns:
      {
        "train": {"X": np.ndarray (N, 7), "y": np.ndarray (N,)},
        "test":  {"X": np.ndarray (M, 7), "y": np.ndarray (M,)},
        "scaler": {"mean": [...], "std": [...]},  # fit on train only
        "feature_names": ["kospiReturnSkewness", ...],
        "label_meta": {"horizon": 20, "threshold": -5.0, "positive_rate": 0.12},
      }
    """
```

```typescript
// 06 백테스트는 동일 라벨 정의를 TS 로 미러
export function labelForwardDrop(params: {
  date: string;
  horizonDays: number;       // 20
  thresholdPct: number;      // -5.0
  prices: OHLCV[];           // KOSPI200
}): 0 | 1 | null;            // null = forward window 부족
```

## Implementation Notes

- **라벨링 SSOT**: TS 의 `labelForwardDrop` 과 Python 의 라벨링 로직은 **같은 공식** — `(price_t+H / price_t - 1) * 100 <= threshold_pct ? 1 : 0`. parity test 필수.
- **train/test split 시간순**: 무작위 split 금지 — 시계열 leak 방지. `train_end_date` 이전 = train, 이후 = test.
- **정규화**: scaler fit on train only, test 는 train scaler 로 transform. `scaler.json` 박아서 05 inference 어댑터가 동일 적용.
- **결측 처리**: 02 가 NULL 박은 row 는 drop. lookback 부족 초기 2005-01 ~ 2005-03 은 자동 제외.
- **forward window 라벨링**: test set 의 마지막 N일은 forward return 계산 불가 → drop. `test_end_date` 는 데이터 마지막일 - 20d 이내 권장.
- **헌법 §6 escape hatch**: 1회성 batch 스크립트 — SOLID 강제 안 함. 함수형 절차적 100~200줄 단일 파일 우선.

## Test Strategy

- **단위**: golden fixture KOSPI 가격 시계열 → `labelForwardDrop` 기댓값 검증. Edge case: horizon 정확 일치, threshold 정확 일치.
- **Python↔TS parity**: 같은 fixture 입력으로 양쪽 라벨 100% 일치 (`scripts/ml/parity-check.py`)
- **scaler round-trip**: train fit → test transform → inverse_transform = test 원본 (1e-9 이내)
- **헌법 §0-1 Step 3 신기능**: ① 정상 split ② lookback 부족 초기 drop ③ forward window 부족 끝부분 drop ④ positive_rate sanity (0.05 ~ 0.20 범위 — 너무 불균형하면 라벨 정의 재검토)

## Verification

- [ ] `build_dataset.py` 실행 시 `endurance/data/training/<YYYY-MM-DD>/` 디렉토리 생성
- [ ] train.parquet, test.parquet, scaler.json 3개 파일 존재
- [ ] feature_names 순서 7개 박힘 (Python·TS 양쪽 동일 순서)
- [ ] Python↔TS 라벨 parity 100%
- [ ] positive_rate metadata 박힘 (04 가 class imbalance 가시화에 사용)
- [ ] label_horizon·threshold 변경 시 dataset 디렉토리 분리 (이름에 config hash)

## Open Questions

1. **label_horizon_days 20 vs 60**: 1개월 vs 3개월 — 어느 horizon 이 학습 성능 좋을지. 04 학습 시 양쪽 실험 후 결정. 본 명세는 20 기본값.
2. **threshold_pct -5% vs -10%**: -5% 면 positive_rate 너무 높을 수 있음 (2008·2020 외에도 다수). -10% 면 너무 희소. 04 에서 positive_rate 측정 후 조정.
3. **class imbalance 처리**: 04 에서 SMOTE / class_weight / 그대로 둘지 — 본 생성기는 raw 만 제공. 04 가 결정.
