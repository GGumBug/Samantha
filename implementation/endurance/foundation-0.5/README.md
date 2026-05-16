[← reports/tl-dr-hashed-unicorn.md로 돌아가기](../../../reports/tl-dr-hashed-unicorn.md)

# Endurance Phase 0.5 — GEMSTONE EWS 인프라 명세 인덱스

## 목적

Phase 0(Foundation) 완료 후, Phase 1(`/dashboard`) 진입 직전 단계. **사용자 노출 0** — 시각 산출물은 `/dev/preview` 내부에 한정한다. GEMSTONE Early Warning System(EWS) 구현에 필요한 **ML·백테스트·디자인 인프라**를 박는다.

Phase 0.5 완료 후 Phase 1 위젯(EarlyWarningGauge, GemstoneRadar 등)은 본 단계가 박은 추론 어댑터·디자인 토큰·preview prototype 위에 의미적 레이아웃만 얹으면 된다. 새 추상화 작성 0건이 목표.

## 의존성 그래프 (작성·구현 순서)

```
01-data-collection ──┬─→ 02-variable-calculation ──┬─→ 03-training-dataset ──→ 04-ml-training ──→ 05-ml-inference
                     │  (7 변수 계산)               │  (라벨링)              │  (Python batch)    │  (Node.js)
                     │                              │                         │                     │
                     └─→ 06-backtest-engine ←──────┘                          │                     │
                       (Stage 1-5, Forward Expectancy)                        │                     │
                                                                               ↓                     ↓
07-design-tokens-gemstone ──→ 08-dev-preview-extension ←────────────────  (Phase 1 위젯 prototypes 진입)
```

루트(01-data-collection) 부터 시작. **각 명세는 그 위 단계 명세가 머지된 후 작성·구현**한다.

## Phase 0 자산 재사용

Phase 0.5는 새로운 자산만 명세하고, 다음 Phase 0 자산은 **재사용**한다 (SSOT 동기):

- **Foundation 09 (sync-scheduler)**: 일일 동기 골격 — Phase 0.5 01-data-collection 이 sync step으로 등록됨
- **Foundation 06 (ai-client)**: GERTY AI 추상화 — 04-ml-training 의 텍스트 설명 생성·해석 보조에 재사용 (선택)
- **Foundation 07 (design-tokens)**: gauge·heatmap·trigger-badge 등 데이터 비즈 토큰 — Phase 0.5 07-design-tokens-gemstone 이 그 위에 GEMSTONE 7 변수 토큰만 박음
- **Foundation 10 (preview-page)**: `/dev/preview` 라우트 — Phase 0.5 08-dev-preview-extension 이 본 페이지에 GEMSTONE 섹션 추가

## 자산 명세 8개

| # | 자산 | 책임 | 위임 | 명세 |
|---|------|------|------|------|
| 01 | 데이터 수집 파이프라인 | yfinance + FRED + ECOS 통합, 2005~ 일별 | HAL | [01-data-collection-pipeline.md](01-data-collection-pipeline.md) |
| 02 | 변수 계산 엔진 | 7 GEMSTONE 변수 일별 산출 | HAL | [02-variable-calculation-engine.md](02-variable-calculation-engine.md) |
| 03 | 학습 데이터셋 생성기 | feature matrix + 라벨링 + train/test split | HAL+GERTY | [03-training-dataset-generator.md](03-training-dataset-generator.md) |
| 04 | ML 학습 스크립트 | Python scikit-learn MLP·SVM, weights export | GERTY | [04-ml-training-script.md](04-ml-training-script.md) |
| 05 | ML inference 어댑터 | Node.js 순수 행렬 연산 (단일 배포 유지) | GERTY+HAL | [05-ml-inference-adapter.md](05-ml-inference-adapter.md) |
| 06 | 백테스트 엔진 | OOS-expanding window, Stage 1-5, Forward Expectancy 5 bucket | HAL | [06-backtest-engine.md](06-backtest-engine.md) |
| 07 | 디자인 시스템 GEMSTONE 토큰 | 7 변수 게이지·라벨·색 | Joi | [07-design-tokens-gemstone.md](07-design-tokens-gemstone.md) |
| 08 | `/dev/preview` 확장 | 7 토큰 + Phase 1 위젯 prototypes | Friday | [08-dev-preview-extension.md](08-dev-preview-extension.md) |

## 기술 스택 결정 (전 명세 공통)

- **학습**: Python 3.11 + scikit-learn batch script. 위치: `endurance/scripts/ml/`
- **Inference**: Node.js 순수 행렬 연산 (단일 배포 유지, ONNX 미도입). 위치: `endurance/src/lib/ml/`
- **모델 버전**: `endurance/data/models/<YYYY-MM-DD>/{weights.json, metadata.json}` + symlink `current/`
- **데이터 소스**:
  - yfinance: KOSPI200(`^KS200`), S&P 500(`^GSPC`), WTI(`CL=F`), KOSPI 거래량
  - FRED: 10Y-2Y Treasury Spread(`T10Y2Y`), 10Y 기대 인플레이션(`T10YIE`), VIX(`VIXCLS`), MOVE 또는 T-Bill 변동성 (Fed Policy Uncertainty 대용 — Step 4에서 정확 시리즈 결정)
  - ECOS: KOSPI200 시총·거래량 보완, KR CPI (필요 시)
  - KOSPI200 종목 리스트: 한국거래소 정적 CSV 분기 갱신
  - KIS는 Phase 5 미룸
- **7 GEMSTONE 변수**:
  1. KOSPI Return Skewness
  2. KOSPI Volume / Market Cap Ratio
  3. KOSPI Pairwise Correlation
  4. US 10Y-2Y Treasury Yield Spread
  5. Fed Policy Rate Uncertainty (대용: MOVE Index 또는 T-Bill Volatility)
  6. WTI Crude Oil Spot
  7. 10-Year Expected Inflation

## 명세 표준 구조

각 명세는 다음 섹션을 모두 포함한다 (헌법 §0-1 시니어 4단계 사고 적용):

1. **Purpose** — 이 자산이 해결하는 문제 (1-2문단)
2. **의존성** — 어느 자산을 사용하는가 / 어느 자산이 이걸 사용하는가
3. **Public Interface** — TypeScript-style 시그니처 / Python 함수 / 디자인 토큰 스펙
4. **Implementation Notes** — 핵심 결정과 트레이드오프 (헌법 §6 escape hatch 명시 가능)
5. **Test Strategy** — 단위·통합·시각 검증 분담
6. **Verification** — 완료 판정 기준 (PR 머지 게이트)
7. **Open Questions** — 명세 작성 중 발견된 미해결 사항

## 진행 정책

- 각 명세는 작성 후 사용자 승인 받은 뒤 구현 위임
- 구현 위임 시 Samantha 또는 직접 위임(`Agent(subagent_type="hal", ...)`) 모두 가용
- 구현 PR은 **1자산 1PR** 원칙 — 컴파일 Green + 테스트 통과 + 검증 항목 통과
- 명세 변경 시 의존하는 후방 자산 명세도 동기 갱신 (SSOT 원칙)
- **PR 머지 시 본 트래커 동기 갱신 의무** — 트래커가 사실과 어긋나면 SSOT 위반

## 진행 상황 트래커

| # | 명세 작성 | 사용자 승인 | 구현 시작 | PR 머지 | 검증 통과 |
|---|---------|----------|---------|--------|---------|
| 01 | ✅ | ⬜ | ⬜ | ⬜ | ⬜ |
| 02 | ✅ | ⬜ | ⬜ | ⬜ | ⬜ |
| 03 | ✅ | ⬜ | ⬜ | ⬜ | ⬜ |
| 04 | ✅ | ⬜ | ⬜ | ⬜ | ⬜ |
| 05 | ✅ | ⬜ | ⬜ | ⬜ | ⬜ |
| 06 | ✅ | ⬜ | ⬜ | ⬜ | ⬜ |
| 07 | ✅ | ⬜ | ⬜ | ⬜ | ⬜ |
| 08 | ✅ | ⬜ | ⬜ | ⬜ | ⬜ |
