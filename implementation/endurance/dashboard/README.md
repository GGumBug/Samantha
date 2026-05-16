[← reports/tl-dr-hashed-unicorn.md로 돌아가기](../../../reports/tl-dr-hashed-unicorn.md)

# Endurance Phase 1 — GEMSTONE EWS Dashboard 명세 인덱스 (v2)

## Purpose

Phase 0 (Foundation) + Phase 0.5 (ML/Backtest 인프라) 머지·검증 통과 후, **사용자에게 처음 노출되는 단일 페이지(`/dashboard`)** 를 GEMSTONE EWS 시장 투자매력도 화면으로 정공 구현. 본 인덱스는 `tl-dr-hashed-unicorn.md` Line 117-118 — **GEMSTONE EWS (INTENSITY 게이지 · Stage 1-5 · Forward Expectancy · Performance Analytics · MODEL INPUTS 7 변수 · 모델 토글 · 시장 토글 · Refresh)** — 을 이행한다.

> 인용 — `tl-dr` Line 117-118:
> ### Phase 1 — GEMSTONE EWS Dashboard (Foundation 0.5 완료 후, 2~3주)
> `/dashboard`를 GEMSTONE 시장 투자매력도 화면으로 정공 구현. 좌상단 INTENSITY 게이지(74점 형식, MLP/SVM 시그널 inference), Stage 1-5 단계 배지, "비중 확대/축소" 라벨, 우상단 FORWARD EXPECTANCY 5 bucket 통계 표, 좌중단 PERFORMANCE ANALYTICS 누적수익률 차트(2005~ OOS-expanding window) + 메트릭 3종(누적수익률 vs BM, Sharpe, MDD), 우중단 MODEL INPUTS 7 변수 sparkline 카드(NEUTRAL/REVERSION 라벨), 헤더 모델 토글(Model 1 Forced [2,8,9,16] vs Model 2 Optimal), 시장 토글 KOSPI200/S&P 500, Refresh.

> **v2 재정의 사유 (2026-05-16)**: 사용자가 GEMSTONE 스크린샷 단언 후 정공 재정의 (옵션 D). v1(P/E·EPS·Volatility·Term Spread 4 위젯 placeholder 산식)은 사용자 4 변수와 GEMSTONE 7 MODEL INPUTS 매핑 0건 — 책임 갱신 + 신규 자산 11~17 추가 + 04·05 phase-2/로 이관.

이 단계가 끝나면 사용자는 한 화면에서 **GEMSTONE EWS INTENSITY 게이지 + Stage + Forward Expectancy 표 + Performance Analytics + MODEL INPUTS 7 변수**를 모델/시장 토글로 비교할 수 있다.

## 의존성 그래프 (작성·구현 순서)

```
Phase 0 (Foundation) ──┬─→ Phase 0.5 (ML/Backtest 인프라) ──┐
                        │                                     │
                        └─────────────────────────────────────┴─→ Phase 1 (본 인덱스)

01-route-shell (v2) ──┬─→ 02-data-api (v2) ─────┬─→ 11-intensity-gauge-stage-badge (A) ──┐
 (라벨 KOSPI200/S&P500)│ (GEMSTONE 시그니처)     │                                          │
                       │                          ├─→ 12-model-meta-card-toggle (B) ───────┤
                       │                          ├─→ 13-forward-expectancy-table (C) ─────┤
                       │                          ├─→ 14-performance-analytics-chart (D) ──┤
                       │                          ├─→ 15-model-inputs-7-cards (E) ─────────┤
                       │                          │   (자산 06 v1 흡수 — Sapphire 카드)    │
                       │                          ├─→ 16-market-toggle-gemstone (F) ───────┤
                       │                          │   (자산 01 v2와 동일 컴포넌트 SSOT)     │
                       │                          └─→ 17-refresh-button (G) ───────────────┤
                       │                                                                    │
                       └────────────────────────────────────────────────────────────────────→ 08-dashboard-integration (v2)
                                                                                                  │
                                                                                       09-e2e-smoke (v2)

자산 07 (Early Warning Gauge v2): 자산 11이 v1 wrapper 확장 — 단독 머지 안 함, 11에 흡수
자산 06 (Term Spread v2): 자산 15 Sapphire 카드에 흡수 — 명세 stub으로 축소 가능
```

루트는 **01-route-shell + 02-data-api**(병렬 가능). 11~17 위젯은 02 머지 후 병렬 작성·구현. 08은 위젯 7종 머지 후 통합. 09는 08 머지 후 시작.

## Phase 0.5 의존성 표

본 Phase 1 자산이 Phase 0.5 인프라에 의존하는 구체 매핑 (SSOT 동기):

| Phase 1 자산 | Phase 0.5 의존 |
|--------------|----------------|
| 02-data-api (v2) | 05-ml-inference-adapter (`infer()` 호출 → INTENSITY) |
| 13-forward-expectancy-table (C) | 06-backtest-engine (`expectancyByBucket`) |
| 14-performance-analytics-chart (D) | 06-backtest-engine (`equityCurve`, `metrics`) |
| 11-intensity-gauge-stage-badge (A) | 07-design-tokens-gemstone (Stage 5구간 색·i18n key) |
| 15-model-inputs-7-cards (E) | 07-design-tokens-gemstone (`GEMSTONE_TOKENS` 상수 SSOT) |
| 12-model-meta-card-toggle (B) | 04-ml-training-script (metadata.json `selected_features` 스키마) |
| 17-refresh-button (G) | Foundation 09 sync-scheduler (sync step 재사용) |

## 자산 표

| # | 자산 | 책임 | 위임 | 명세 |
|---|------|------|------|------|
| 01 | Route Shell + Market Toggle + Layout (v2) | Server Component 진입점, 라벨 KOSPI200/S&P 500 갱신 | Friday | [01-route-shell.md](01-route-shell.md) |
| 02 | `/api/dashboard` Data API (v2) | GEMSTONE 7 MODEL INPUTS + INTENSITY + Stage + Forward Expectancy + Performance 통합 진입점 | HAL | [02-data-api.md](02-data-api.md) |
| 04 | — | Phase 2 이관 (`../phase-2/04-pe-metric-card.md`) | — | [Phase 2](../phase-2/04-pe-metric-card.md) |
| 05 | — | Phase 2 이관 (`../phase-2/05-volatility-sparkline.md`) | — | [Phase 2](../phase-2/05-volatility-sparkline.md) |
| 06 | Term Spread (v2 — 자산 15 흡수) | 자산 15 Sapphire 카드 인스턴스 (단독 컴포넌트 폐기 권장) | Joi | [06-term-spread-chart.md](06-term-spread-chart.md) |
| 07 | Early Warning Gauge (v2 — 자산 11 wrapper) | v1 게이지 SVG wrapper 보존, 자산 11이 확장 | Friday | [07-early-warning-gauge.md](07-early-warning-gauge.md) |
| 08 | Dashboard Integration (v2) | 위젯 A~G 통합, data-testid 규약 v2 SSOT | Friday | [08-dashboard-integration.md](08-dashboard-integration.md) |
| 09 | E2E Smoke (v2) | Playwright 시나리오 7~10종 (GEMSTONE 위젯 + 모델 토글 + Refresh) | Friday | [09-e2e-smoke.md](09-e2e-smoke.md) |
| 11 | INTENSITY 게이지 + Stage 1-5 배지 (A) | 07 wrapper 확장 + 산식 ML inference 호출 | Friday | [11-intensity-gauge-stage-badge.md](11-intensity-gauge-stage-badge.md) |
| 12 | 모델 메타 카드 + 모델 토글 (B) | Model 1 Forced [2,8,9,16] / Model 2 Optimal 토글 + OOS Sharpe 메타 | Friday | [12-model-meta-card-toggle.md](12-model-meta-card-toggle.md) |
| 13 | FORWARD EXPECTANCY 5 bucket 표 (C) | 백테스트 엔진 통계 표시 | Joi | [13-forward-expectancy-table.md](13-forward-expectancy-table.md) |
| 14 | PERFORMANCE ANALYTICS 차트 + 메트릭 3종 (D) | OOS 누적수익률 + Sharpe/MDD | Joi | [14-performance-analytics-chart.md](14-performance-analytics-chart.md) |
| 15 | MODEL INPUTS 7 변수 카드 (E) | sparkline + NEUTRAL/REVERSION 라벨 | Joi | [15-model-inputs-7-cards.md](15-model-inputs-7-cards.md) |
| 16 | 시장 토글 GEMSTONE 갱신 (F) | 01과 동일 컴포넌트 SSOT (라벨·data-testid) | Friday | [16-market-toggle-gemstone.md](16-market-toggle-gemstone.md) |
| 17 | Refresh 버튼 (G) | Foundation 09 sync 재사용 + 수동 트리거 UI | Friday | [17-refresh-button.md](17-refresh-button.md) |

> 자산 번호 03·10 의도된 결번. 03은 Phase 0 `market-router`와의 시맨틱 충돌 회피. 10은 Phase 0의 `preview-page`와 시맨틱 충돌 회피.

## v1 구현 잔재 처리 (endurance 저장소 24커밋 정책)

| v1 자산 | 처리 정책 | 영향 커밋 |
|---------|----------|---------|
| 01-route-shell v1 | **In-place 확장** — 라벨/testid만 v2 갱신, 구조 보존 | 1 |
| 02-data-api v1 | **v2 재공작** — DashboardSnapshot 시그니처 완전 교체, 단위 테스트 재작성 | 4 |
| 04-pe-metric-card v1 | **Phase 2 이관** — 컴포넌트 보존, import 경로 갱신만 | 4 |
| 05-volatility-sparkline v1 | **Phase 2 이관** — 컴포넌트 보존, import 경로 갱신만 | 4 |
| 06-term-spread-chart v1 | **자산 15 흡수** — TermSpreadChart 컴포넌트 폐기 또는 Sapphire 인스턴스로 통합 | 3 |
| 07-early-warning-gauge v1 | **In-place 확장** — wrapper 보존 + 자산 11이 산식 본격화, isPlaceholder UI 제거 | 4 |
| 08-dashboard-integration v1 | **v2 재공작** — 4 위젯 grid → 7 위젯 grid 재설계 | 3 |
| 09-e2e-smoke v1 | **v2 재공작** — 시나리오 5종 폐기, 7~10종 재작성 | 1 |

총 24커밋 (대략). 각 PR에서 본 표의 처리 정책에 따라 v1 코드 마이그레이션 또는 보존 결정.

## 명세 표준 구조

각 명세는 다음 7섹션을 모두 포함 (헌법 §0-1 시니어 4단계 사고 자동 적용):

1. **Purpose** — 이 자산이 해결하는 문제 (1-2문단)
2. **의존성** — 어느 자산을 사용하는가 / 어느 자산이 이걸 사용하는가
3. **Public Interface** — TypeScript-style 인터페이스·라우트 contract·props 시그니처
4. **Implementation Notes** — 핵심 결정과 트레이드오프 (헌법 §6 escape hatch 명시)
5. **Test Strategy** — 단위·통합·시각 검증 분담. 변경 종류별 표준 시나리오 매핑
6. **Verification** — 완료 판정 기준 (PR 머지 게이트 체크리스트)
7. **Open Questions** — 명세 작성 중 발견된 미해결 사항·트레이드오프

## 진행 정책

- 각 명세는 작성 후 사용자 승인 받은 뒤 구현 위임
- 구현 위임은 자산별 책임 에이전트에 직접 또는 Samantha 경유 모두 가용
- **1자산 1PR 원칙** — 컴파일 Green + 단위/통합 테스트 통과 + 명세 Verification 체크리스트 통과
- 명세 변경 시 의존하는 후방 자산 명세도 동기 갱신 (헌법 §2 SSOT 원칙)
- **새 추상화 작성 금지** — Phase 1은 Phase 0 + Phase 0.5 자산 재사용만. 명세 중 새 디자인 토큰·라이브러리·SDK 도입 발견 시 즉시 거부하고 Open Questions에 박을 것
- **박제 룰**: PR 머지 시 본 README 트래커 동기 갱신 의무 (Phase 0 SSOT 회귀 회고 반영 — 트래커가 실제 진행과 어긋나면 헌법 §2 위반)

## 진행 상황 트래커 (v2)

| # | 명세 작성 | 사용자 승인 | 구현 시작 | PR 머지 | 검증 통과 |
|---|---------|----------|---------|--------|---------|
| 01 (v2) | ✅ | ⬜ | ⬜ | ⬜ | ⬜ |
| 02 (v2) | ✅ | ⬜ | ⬜ | ⬜ | ⬜ |
| 06 (v2) | ✅ | ⬜ | ⬜ | ⬜ | ⬜ |
| 07 (v2) | ✅ | ⬜ | ⬜ | ⬜ | ⬜ |
| 08 (v2) | ✅ | ⬜ | ⬜ | ⬜ | ⬜ |
| 09 (v2) | ✅ | ⬜ | ⬜ | ⬜ | ⬜ |
| 11 (신규) | ✅ | ⬜ | ⬜ | ⬜ | ⬜ |
| 12 (신규) | ✅ | ⬜ | ⬜ | ⬜ | ⬜ |
| 13 (신규) | ✅ | ⬜ | ⬜ | ⬜ | ⬜ |
| 14 (신규) | ✅ | ⬜ | ⬜ | ⬜ | ⬜ |
| 15 (신규) | ✅ | ⬜ | ⬜ | ⬜ | ⬜ |
| 16 (신규) | ✅ | ⬜ | ⬜ | ⬜ | ⬜ |
| 17 (신규) | ✅ | ⬜ | ⬜ | ⬜ | ⬜ |

> v2 갱신 시점에 사용자 승인·구현 시작·PR 머지·검증 통과는 모두 ⬜로 리셋. v1 단위 구현 코드는 §"v1 구현 잔재 처리" 표 정책에 따라 별도 추적.

## 참고

- 상위 SSOT: [reports/tl-dr-hashed-unicorn.md](../../../reports/tl-dr-hashed-unicorn.md)
- Phase 0 인덱스(동형 패턴): [../foundation/README.md](../foundation/README.md)
- Phase 0.5 인덱스: [../foundation-0.5/README.md](../foundation-0.5/README.md)
- Phase 2 인덱스: [../phase-2/README.md](../phase-2/README.md)
- 헌법: [.claude/rules/engineering-constitution.md](../../../.claude/rules/engineering-constitution.md)
- 디자인 시스템: [design-system/DESIGN.md](../../../design-system/DESIGN.md)
