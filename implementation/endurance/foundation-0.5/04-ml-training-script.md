[← README.md로 돌아가기](README.md)

# 04 — ML Training Script (Python scikit-learn MLP·SVM, weights export)

**위임**: GERTY | **위치**: `endurance/scripts/ml/train.py`, 산출물 `endurance/data/models/<YYYY-MM-DD>/{weights.json, metadata.json}` + symlink `current/` | **의존**: 03 (training dataset)

## Purpose

03 의 train.parquet 으로 두 모델(scikit-learn MLPClassifier, SVC RBF) 을 학습하고, **inference 어댑터(05)가 Node.js 에서 재현 가능한 형태(JSON)** 로 가중치·하이퍼파라미터·scaler·metadata 를 export 한다. ONNX 미도입(단일 배포 유지) — JSON 직렬화로 충분한 모델 규모.

본 스크립트는 1회성 batch — 일별 cron 으로 매일 재학습 안 함. 분기 또는 변수/라벨 정의 변경 시에만 수동 실행. 학습 결과는 `current/` symlink 갱신으로 inference 어댑터가 자동 픽업.

## 의존성

- **사용하는 자산**: 03 (`endurance/data/training/<date>/{train,test}.parquet`, `scaler.json`)
- **이걸 사용하는 자산**: 05 (inference 어댑터 — weights.json 로드)

## Public Interface (Python)

```python
# endurance/scripts/ml/train.py

from dataclasses import dataclass
from typing import Literal

@dataclass
class TrainingConfig:
    dataset_dir: str           # "endurance/data/training/2025-12-01/"
    model_kind: Literal["mlp", "svm"]
    output_dir: str            # "endurance/data/models/2025-12-01/"
    # MLP hyperparams
    hidden_layers: tuple = (16, 8)
    max_iter: int = 500
    random_state: int = 42
    # SVM hyperparams (RBF)
    svm_c: float = 1.0
    svm_gamma: Literal["scale", "auto"] = "scale"

def train_model(config: TrainingConfig) -> dict:
    """
    Returns metadata dict (also written to metadata.json):
      {
        "model_kind": "mlp",
        "feature_names": [...],
        "train_metrics": {"accuracy": ..., "roc_auc": ..., "precision": ..., "recall": ...},
        "test_metrics":  {...},
        "hyperparams": {...},
        "trained_at": "2025-12-01T10:00:00Z",
        "dataset_dir": "...",
        "git_commit": "<hash>",
      }
    """
```

## weights.json 스키마 (05 inference 가 읽음)

```jsonc
// MLP
{
  "kind": "mlp",
  "layers": [
    { "weights": [[...]], "bias": [...], "activation": "relu" },
    { "weights": [[...]], "bias": [...], "activation": "relu" },
    { "weights": [[...]], "bias": [...], "activation": "logistic" }
  ],
  "input_scaler": { "mean": [...], "std": [...] },
  "feature_names": ["kospiReturnSkewness", ...]
}

// SVM (RBF kernel, support vector dump)
{
  "kind": "svm_rbf",
  "support_vectors": [[...]],
  "dual_coef": [...],
  "intercept": [...],
  "gamma": 0.143,
  "input_scaler": { "mean": [...], "std": [...] },
  "feature_names": [...]
}
```

## Implementation Notes

- **모델 선택 기준**: MLP `(16, 8)` hidden — 7 input feature 에 적정 capacity. SVM RBF 는 비교 baseline. 두 모델 모두 train → metadata 비교 후 사용자/시니어가 production 선택.
- **JSON 직렬화**: scikit-learn `MLPClassifier.coefs_` / `.intercepts_` 를 numpy → list 변환. SVM 도 `support_vectors_`, `dual_coef_`, `intercept_` dump. 05 가 순수 행렬 연산으로 재현.
- **재현성**: `random_state=42` 고정. 같은 dataset → 같은 weights.json (bit-identical은 아니나 metric 동일).
- **scaler co-located**: 03 의 scaler.json 을 weights.json 내부에 박음 — 05 inference 어댑터가 scaler 별도 로드 안 하도록 SSOT 통합.
- **metadata `git_commit`**: 학습 시점 코드 버전 박음 — 모델 추적성. `subprocess.check_output(["git", "rev-parse", "HEAD"])`.
- **symlink `current/`**: 학습 성공 + test_metrics 통과 시에만 `current/ → <date>/` symlink 갱신. 실패 시 옛 모델 유지.
- **헌법 §6 escape hatch**: 1회성 batch — SOLID 강제 안 함. 절차적 200줄 단일 파일.

## Test Strategy

- **단위**: golden dataset (fixture parquet) 으로 학습 → weights.json schema 검증
- **inference parity (가장 중요)**: 같은 입력 7-vector 로 ① Python `model.predict_proba()` ② 05 Node.js inference → 1e-6 이내 일치. 본 검증이 05 의 핵심.
- **metric 회귀**: 이전 모델 test_metrics 보다 ROC-AUC 0.05 이상 떨어지면 symlink 갱신 차단 (안전장치)
- **헌법 §0-1 Step 3 신기능**: ① 정상 학습 ② class imbalance 처리(SMOTE off → 정확도/recall trade-off 가시화) ③ NaN/Inf 입력 거부 ④ 학습 실패 시 옛 symlink 보존

## Verification

- [ ] `train.py --model mlp` 실행 시 `endurance/data/models/<date>/weights.json, metadata.json` 생성
- [ ] `train.py --model svm` 도 동일 형식 생성
- [ ] weights.json 이 05 의 zod 스키마 통과 (양쪽 SSOT 동기)
- [ ] inference parity 1e-6 이내 (Python ↔ Node.js)
- [ ] `current/` symlink 가 최신 성공 모델 가리킴
- [ ] metadata.json 에 git_commit · trained_at · metrics 박힘

## Open Questions

1. **MLP vs SVM production 선택**: ROC-AUC, calibration plot, false alarm rate 종합. 사용자/시니어 검토 필요.
2. **class_weight 도입 여부**: positive_rate 0.05~0.15 범위면 imbalance 처리 필요. `class_weight="balanced"` vs SMOTE — 학습 시 양쪽 실험.
3. **확률 calibration**: MLP `predict_proba` 가 calibrated 인지 검증 필요. `CalibratedClassifierCV` 도입 검토 — 05 inference 가 확률을 게이지 0~100 으로 매핑하므로 calibration 중요.
4. **재학습 트리거 정책**: 분기 1회 수동 vs 새 데이터 N개월 누적 시 자동. Phase 1 이후 결정.
