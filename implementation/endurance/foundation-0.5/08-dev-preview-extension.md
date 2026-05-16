[← README.md로 돌아가기](README.md)

# 08 — `/dev/preview` Extension (7 토큰 + Phase 1 위젯 prototypes)

**위임**: Friday | **위치**: `endurance/src/app/dev/preview/_sections/Gemstone*.tsx` | **의존**: Foundation 10 (preview-page 라우트), 07 (GEMSTONE 토큰), 05 (inference 어댑터 — 실데이터 prototype), 06 (백테스트 — history chart prototype)

## Purpose

Phase 0.5 의 시각 통합 검증. Foundation 10 의 `/dev/preview` 페이지에 **GEMSTONE 섹션** 을 추가해 (a) 07 가 박은 7 토큰을 모든 상태로 시각 확인하고 (b) Phase 1 위젯(EarlyWarningGauge·GemstoneRadar·BacktestHistoryChart·VariableDetailCard) 의 prototype 을 미리 박는다.

본 prototype 이 통과하면 Phase 1 은 위젯 레이아웃·페이지 통합만 남음 — 새 추상화 작성 0건. 사용자 노출은 여전히 `/dev/preview` 하위 (production env flag 가드) — 본 자산만으로 사용자에게 GEMSTONE 노출 0.

## 의존성

- **사용하는 자산**: Foundation 10 (`/dev/preview` 라우트·라우트 가드), 07 (GEMSTONE_TOKENS·gauge·alert 색), 05 (`infer` 실데이터 prototype), 06 (BacktestReport prototype)
- **이걸 사용하는 자산**: Phase 1 위젯 통합 (본 prototype 의 컴포넌트가 그대로 위젯 base)

## 페이지 구조 (Foundation 10 Section 8 후속)

`/dev/preview` 에 신규 섹션 추가:

### Section 9 — GEMSTONE Token Showcase
07 의 7 토큰을 각 상태로 렌더:
- 각 보석별 게이지 (z-score = -3, -1.5, 0, +1.5, +3 — 5 상태)
- 보석명 + i18n label (한/영 토글)
- description tooltip
- alert color 발동 상태

### Section 10 — EarlyWarningGauge Prototype
- 단일 큰 게이지 (Foundation 07 gauge-meter `lg` 240×120px)
- probability 0~1 슬라이더로 Stage 1-5 시각 전환
- 각 Stage 색·i18n 라벨 표시

### Section 11 — GemstoneRadar Prototype
- 7 변수 z-score 를 7각 radar chart 로 표시
- fixture 4 패널: 정상 / Watch / Caution / Critical
- 각 보석색이 radar 영역색

### Section 12 — Inference Smoke Test (실데이터)
- 버튼: "Run EWS Inference (2025-05-01)"
- 클릭 시 `infer({ date: "2025-05-01", variables: <02 의 결과> })`
- 결과 InferenceOutput → EarlyWarningGauge 렌더
- 실패 시 trigger-badge 가시화

### Section 13 — BacktestHistoryChart Prototype
- `endurance/data/backtest/<latest>/equity_curve.csv` 로드
- LineChart (chart-container 토큰) — nav vs date
- 신호 발동 시점(stage 4-5) 음영 overlay
- Forward Expectancy 5 bucket 막대 차트 동반

### Section 14 — Variable Detail Card Prototypes
- 7 변수 각각의 `metric-card` (Foundation 07) — 보석명·현재값·z-score·delta·sparkline
- 보석명 색 적용
- 5초 간격 자동 토글 (한/영) — i18n 동기 회귀 감지

## Implementation Notes

- **prototype 책임 분리**: 본 명세는 시각·라우트·fixture/실데이터 호출. 실제 Phase 1 위젯의 레이아웃·페이지 통합은 Phase 1 별도. Section 9~14 컴포넌트는 그대로 Phase 1 이 import.
- **fixture vs 실데이터**: Section 9·10·11·14 는 fixture (`endurance/src/app/dev/preview/_fixtures/gemstone.ts`). Section 12·13 은 실데이터(05·06 호출). fixture 가 깨지면 시각 회귀 신호.
- **i18n 자동 토글 (Section 14)**: 헌법 §0-1 Step 3 핵심 검증 — "마운트 중 토글 자동 갱신". setInterval 로 5초마다 locale 변경 시 컴포넌트 갱신 확인. 안 갱신되면 §2-0 caller-driven snapshot 안티패턴 의심.
- **production 가드 상속**: Foundation 10 의 `NODE_ENV === 'production'` 차단을 그대로 적용 — 본 섹션도 production 노출 0.
- **자기 평가 금지**: AI 가 "잘 보인다" 선언 금지 — 사용자/시니어 스크린샷 OK 판정 필수 (헌법 §0-1 Step 4).
- **헌법 §6 escape hatch**: preview 페이지는 1회성 검증 — SOLID 엄격 적용 안 함. fixture 박제·인라인 절차적 코드 허용.

## Test Strategy

- **빌드 통과**: `npm run build` 시 Section 9~14 컴파일 성공
- **production 차단**: `NODE_ENV=production npm run start` 후 `/dev/preview` → 404
- **각 섹션 독립 렌더**: 1 섹션 데이터 호출 실패해도 다른 섹션 정상
- **반응형**: 320 / 768 / 1280px 모두 깨짐 없음
- **i18n 자동 토글 (회귀 방지 핵심)**: Section 14 의 5초 토글로 컴포넌트가 한/영 갱신되는지 시각 확인 — anti-pattern 회귀 감지
- **시각 회귀**: Playwright 스크린샷 자동 비교는 Phase 3+ (07 명세 Open Question 1 동일)

## Verification (= Phase 0.5 완료 게이트)

본 섹션 모든 항목 통과 = Phase 0.5 완료:

- [ ] Section 9: 7 토큰 × 5 z-score 상태 모두 정상 렌더
- [ ] Section 10: probability 슬라이더 0~1 → Stage 1-5 색·라벨 정합
- [ ] Section 11: 7각 radar 4 fixture 패널 모두 정상
- [ ] Section 12: 실데이터 inference 호출 성공 — 04 의 current 모델 픽업
- [ ] Section 13: 최신 backtest equity_curve.csv 로드 + 신호 overlay + 5 bucket 막대
- [ ] Section 14: 7 metric-card 한/영 5초 자동 토글 회귀 0건
- [ ] production 빌드에서 404 차단
- [ ] 사용자(시니어 리뷰어) OK 판정

## Open Questions

1. **Section 13 backtest data 갱신 주기**: 06 가 분기 1회 batch — preview 가 오래된 report 보는 문제. `current/` symlink 패턴 06 도 도입할지.
2. **Section 12 실데이터 비용**: yfinance·FRED 호출 매 방문 시? → 5분 캐시(05 의 in-memory 캐시) 로 충분. 단, 백필 안 된 시점 호출하면 결측 — fixture fallback 필요.
3. **자동 스크린샷 회귀**: Phase 3+ 검토 — Playwright 도입 시 본 섹션이 가장 큰 수혜.
