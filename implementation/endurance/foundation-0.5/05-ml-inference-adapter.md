[← README.md로 돌아가기](README.md)

# 05 — ML Inference Adapter (Node.js 순수 행렬 연산)

**위임**: GERTY + HAL | **위치**: `endurance/src/lib/ml/`, 모델 로드 `endurance/data/models/current/weights.json` | **의존**: 04 (학습 산출물 weights.json), 02 (변수 계산 — 7-vector 입력)

## Purpose

04 가 박은 weights.json 을 Node.js 에서 로드하고, 02 의 7-GEMSTONE-vector 를 **단일 배포 환경에서** EWS 확률(0~1) 로 변환. ONNX runtime·Python 자식 프로세스 미도입 — 순수 TS 행렬 연산만 사용해 Next.js 단일 배포 유지(헌법 §5 오버엔지니어링 회피).

본 어댑터는 04 의 Python `predict_proba` 와 **1e-6 이내 parity** 가 핵심 책임. parity 깨지면 학습 모델의 신호가 production 에서 다른 의미가 됨 — 회귀 catastrophic.

## 의존성

- **사용하는 자산**: 04 (`endurance/data/models/current/weights.json`), 02 (`computeGemstoneVariables` — 입력 7-vector)
- **이걸 사용하는 자산**: Phase 1 위젯 (EarlyWarningGauge — 확률 → 게이지 0~100), 06 (백테스트 시 시점별 inference)

## Public Interface

```typescript
// === Model Loader ===

export interface MlpWeights {
  kind: "mlp";
  layers: Array<{
    weights: number[][];     // [out_dim][in_dim]
    bias: number[];
    activation: "relu" | "logistic";
  }>;
  inputScaler: { mean: number[]; std: number[] };
  featureNames: string[];
}

export interface SvmWeights {
  kind: "svm_rbf";
  supportVectors: number[][];
  dualCoef: number[];
  intercept: number[];
  gamma: number;
  inputScaler: { mean: number[]; std: number[] };
  featureNames: string[];
}

export type ModelWeights = MlpWeights | SvmWeights;

/** weights.json 로드 + zod 검증 */
export async function loadModel(path?: string): Promise<Result<ModelWeights>>;

// === Inference ===

export interface InferenceInput {
  date: string;
  variables: GemstoneVariables;  // 02 의 출력
}

export interface InferenceOutput {
  date: string;
  probability: number;           // 0~1 (P[forward drop])
  gauge: number;                 // 0~100 (UI 표시용 — calibrated mapping)
  modelKind: "mlp" | "svm_rbf";
  modelTrainedAt: string;        // metadata.json 에서 가져옴
}

/** 단일 시점 추론 */
export async function infer(input: InferenceInput): Promise<Result<InferenceOutput>>;

/** 범위 일괄 추론 (백테스트용) */
export async function inferRange(params: {
  startDate: string;
  endDate: string;
}): Promise<Result<InferenceOutput[]>>;
```

## Implementation Notes

- **순수 행렬 연산**: MLP forward pass = `relu(W @ x + b)` 반복 + `sigmoid(W @ x + b)` 마지막. SVM RBF = `sum(dual_coef * exp(-gamma * ||x - sv||^2)) + intercept` → sigmoid (Platt scaling 적용 시 04 가 calibrator coef 도 박음).
- **scaler 적용**: `(x - mean) / std` 표준화 — 04 의 scaler 와 동일 정의(SSOT). 잊으면 catastrophic.
- **확률 → gauge 매핑**: `gauge = round(probability * 100)`. calibration 보정 필요 시 04 metadata 에 `calibration_curve` 박음 → 본 어댑터가 보간 적용. 초안은 선형 매핑.
- **모델 핫스왑**: `current/` symlink 가 바뀌면 다음 요청부터 새 모델. process restart 불필요 — 매 요청 `fs.readFile` 은 비용. 5분 in-memory 캐시 (간단한 `let cached: {model, mtime}` — 헌법 §5 라이브러리 도입 회피).
- **zod 스키마**: `MlpWeightsSchema` / `SvmWeightsSchema` 박아서 weights.json 손상 시 즉시 에러. 04 의 export 와 양쪽 동기.
- **헌법 §0-1 Step 3 신기능**: ① 정상 추론 ② weights.json 결측 → fallback baseline 확률(0.5)? 아니면 throw? → throw + Result.error 로 UI 에 명시 (silent fail 금지).

## Test Strategy

- **단위**: relu/sigmoid/matmul 헬퍼 함수 단위 테스트 (numpy 등가)
- **inference parity (핵심)**: 100개 fixture 7-vector 입력 → Python `predict_proba` 결과 vs Node.js `infer().probability` 1e-6 이내. 04 의 `scripts/ml/parity-check.py` 가 자동 비교.
- **scaler parity**: 입력 표준화 단계도 1e-9 이내 일치
- **헌법 §4 결정론**: 같은 입력 → 같은 출력 (`Date.now()` 의존 없음 — modelTrainedAt 은 metadata 에서 가져옴)
- **헌법 §0-1 Step 3 신기능**: ① 정상 ② 결측 weights.json → Result.error ③ NaN/Inf 입력 → Result.error ④ 캐시 mtime 갱신 시 새 모델 자동 픽업

## Verification

- [ ] `endurance/src/lib/ml/` 폴더에 loader, mlp, svm, scaler, types 분할
- [ ] zod 스키마가 04 의 weights.json schema 와 호환 (양쪽 SSOT)
- [ ] 100 fixture parity 1e-6 이내 통과
- [ ] in-memory 캐시 5분 TTL 동작 + symlink mtime 변경 시 invalidate
- [ ] `inferRange` 범위 호출 시 결정론 (같은 모델 + 같은 변수 = 같은 확률)
- [ ] silent fail 0건 — 모든 실패는 Result.error 로 명시

## Open Questions

1. **calibration 매핑**: probability → gauge 가 선형이 맞는가? sigmoid 출력은 0.4~0.6 구간에 몰리는 경향 — power transform 또는 quantile mapping 도입 검토. 04 의 calibration curve 박혀야 결정 가능.
2. **MLP 양쪽 layer 활성화**: scikit-learn MLPClassifier 는 hidden=ReLU, output=logistic (binary). 04 export 시 명시 박음 — parity 어긋나면 첫 의심.
3. **SVM 의 Platt scaling**: `SVC(probability=True)` 는 Platt scaling 으로 확률 보정 — 04 export 에 calibrator A, B 박아야 함. 어댑터에서 `sigmoid(A * decision + B)` 적용. 04·05 양쪽 명세 동기 필수.
