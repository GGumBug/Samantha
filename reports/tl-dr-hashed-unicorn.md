# Endurance 기능 설계 — 엉드루 5단계 하이브리드 프레임워크 매핑

## Context

사용자는 엉드루(퀀트 트레이더)의 **5단계 하이브리드 프레임워크**(독자 계량 모델 + AI 보조 정성 분석)를 자기 일생의 투자 의사결정에 적용하길 원합니다. 본 계획은 그 프레임워크를 **Endurance 웹 앱의 구체적 페이지·기능·데이터 모델·로드맵**으로 변환합니다.

대상 시장은 **KOSPI(한국)와 NASDAQ(미국) 양쪽 동등 지원**. 두 시장을 한 화면에서 비교 가능하게 하여 IRF 전이 메커니즘(나스닥 → KOSPI 5주기) 같은 교차 분석을 실시간으로 가능하게 합니다.

핵심 목표: 하루 5분 ~ 월 1시간 다층 사용으로 (a) 거시 경보·섹터 신호·종목 추적을 양 시장 한 화면에, (b) 종목 결정 전 4단계 검증을 보조, (c) 매매 결정·근거를 자유롭게 일지에 남겨 회고 가능하게 합니다. **강제 메커니즘 없음** — 도구는 정보를 보여주고 기록할 뿐, 사용자 행동을 막거나 강요하지 않습니다.

탐색 결과: Endurance는 디자인 토큰만 박혀 있고 비즈 컴포넌트는 미존재. job-search-master의 `lib/ai.ts`/`lib/db.ts`/API 라우트 패턴 재사용 가능. 데이터 테이블·차트 토큰은 디자인 시스템에 신규 추가 필요.

## 5단계 프레임워크 → Endurance 페이지·위젯 매핑 (KOSPI + NASDAQ 동등)

각 페이지는 **시장 토글(KOSPI / NASDAQ / 양쪽 동시)** 을 헤더에 두어 한 화면에서 양 시장을 비교할 수 있게 합니다.

| 엉드루 단계 | 페이지 | 핵심 위젯 | 데이터 소스 |
|----------|------|---------|----------|
| 1. Macro 평가 | `/dashboard` (홈) | 조기 경보 게이지 0-100, KOSPI·NASDAQ 12M P/E·EPS 성장 나란히, 일일 변동성, Term Spread (US/KR), 외국인·기관 누적 수급, LPPL 진단, IRF 전이 시각화 | KIS + 한국은행 ECOS + yfinance + FRED |
| 2. 주도 섹터 | `/sectors` | 섹터별 누적 수익률 히트맵 (KOSPI 행 + NASDAQ 행), 52주 신고가 밀도, 양 시장 교차 상관 | KIS 섹터 + GICS·NASDAQ 섹터 (yfinance) |
| 3. 정량 스크리닝 | `/screener` | 4대 스타일(수익성·성장성·저평가·모멘텀) 슬라이더 + 시장 필터 + 결과 ranking | DART + KIS (한국) / SEC EDGAR + yfinance (미국) |
| 4. 심층 분석 | `/stock/[ticker]` | 시장 자동 감지(`005930.KS` vs `NVDA`), 재무 시계열·ROIC, SWOT/5 Forces (AI 보조), MA·볼밴, 수급(한국: 외국인·기관 / 미국: institutional ownership) | DART/SEC + KIS/yfinance + AI |
| 5. 최종 결정 | `/journal` + `/portfolio` | 의견 기록(Strong Buy~Sell), 매매 일지(자유 형식), 양 시장 보유 자산 통합(KRW·USD 환산), invalidation 모니터 | 로컬 SQLite |

## 페이지 IA (라우트 트리)

```
/                  → /dashboard 리다이렉트
/dashboard         → 거시 한 눈에 (1단계)
/sectors           → 섹터 히트맵 + 52주 신고가 (2단계)
/screener          → 4대 스타일 스크리너 (3단계)
/stock/[ticker]    → 종목 심층 분석 (4단계)
/watchlist         → 관심 종목 (별표)
/journal           → 거래 일지 + 의견 이력 (5단계)
/portfolio         → 보유 자산 + 1회 한도 검증 (5단계)
/triggers          → invalidation 모니터·알림
/settings          → API 키, AI 제공자, 알림 채널
```

## 데이터 아키텍처

**외부 소스 (시장별 동등 primary)**:
- **한국**: KIS OpenAPI (시세·체결·외국인 수급) + DART (재무제표·공시) + 한국은행 ECOS (거시)
- **미국**: yfinance (`yahoo-finance2` npm, 시세·기본 재무) + SEC EDGAR (10-K/10-Q 재무) + FRED (거시)
- **AI**: Gemini + OpenAI — SWOT·5 Forces·일지 요약 (job-search `lib/ai.ts` 재사용)
- **환율**: 한국은행 ECOS (KRW/USD) — 양 시장 보유 자산 통합 표시용

**로컬 SQLite** (`data/endurance.db`, gitignore):
- `securities` (ticker·name·sector·country [KR/US]·currency [KRW/USD])
- `prices_daily` (ticker·date·OHLCV)
- `financials_quarterly` (revenue·EPS·FCF·ROIC·debt — 통화는 securities.currency)
- `holdings` (ticker·qty·avg_price·entry_lots_json)
- `trades` (ticker·side·qty·price·reason·ts) — 자유 형식 reason 필드, 강제 체크리스트 없음
- `opinions` (ticker·rating·thesis_md·ts)
- `triggers` (scope·condition_json·fired_at·muted) — 사용자 설정 알림만
- `macro_snapshots` (date·market [KR/US]·index_value·pe_12m·eps_growth·term_spread)
- `sector_snapshots` (date·market·sector·perf_ytd·new_high_count)
- `fx_rates_daily` (date·pair·rate) — KRW/USD

## AI 보조 (GERTY 영역)

job-search `lib/ai.ts` 패턴 재사용 — 단일 클라이언트 인터페이스로 Gemini/OpenAI 교체 가능. `src/lib/prompts/`:
- `swot.ts` — 재무·시세 입력 → SWOT 4사분면 마크다운
- `five-forces.ts` — Porter's 5 Forces 점수(1-5) + 근거
- `journal-summary.ts` — 매매 일지 월간 요약·패턴 인사이트
- `thesis-builder.ts` — 매수 근거 한 줄 작성 보조
- `triggers-evaluator.ts` — 거시·종목 데이터 → invalidation 충족 여부

zod 스키마로 응답 검증, 동일 입력 재현성 ≥ 80% 보장.

## 디자인 시스템 확장 (Joi 영역)

신규 컴포넌트 토큰을 `design-system/components.md`에 추가 필요:
- **`data-table-row`** — 정렬·필터 가능한 표 행 (TanStack Table 통합)
- **`chart-container`** — 다크 캔버스 호환 차트 wrapper (Recharts 또는 visx — 번들 크기로 결정)
- **`gauge-meter`** — 0-100 조기 경보 게이지 (커스텀 SVG)
- **`heatmap-cell`** — 섹터 히트맵 셀
- **`metric-card`** — 단일 거시 지표 카드 (값 + delta + sparkline)
- **`checklist-item`** — 매수/매도 체크리스트 행
- **`triggers-badge`** — invalidation 발동 배지

## 단계별 로드맵

> **시니어 판단**: 사용자 명시적 우선순위(시간 걸려도 유지보수+확장성)에 따라 **Phase 0 (Foundation)** 을 추가. Phase 0 없이 Phase 1로 직행하면 페이지마다 동일 추상화를 반복 작성하게 됨.

### Phase 0 — Foundation (1~2주, 사용자 노출 0)

**목표**: 모든 후속 페이지가 의존할 기반을 다지고 검증. 시각 산출물 없음, 단위 테스트·시각 검증 페이지(`/dev/preview`)로만 검증.

| # | 자산 | 책임 |
|---|------|------|
| 1 | DB 스키마 + 마이그레이션 | HAL — 9개 테이블 + zod 타입 |
| 2 | 시장 라우터 (`lib/market/router.ts`) | HAL+Friday — ticker → KR/US 자동 분기 |
| 3 | yfinance 클라이언트 | HAL — rate limit·캐싱·zod 검증 |
| 4 | FX 클라이언트 | HAL — KRW/USD 일별 캐시 |
| 5 | AI 클라이언트 (Gemini 우선) | GERTY — job-search 패턴 포팅 |
| 6 | 디자인 시스템 7종 토큰 | Joi — data-table/chart/gauge/heatmap/metric-card/market-toggle/triggers-badge |
| 7 | 차트 라이브러리 결정 | Joi — Recharts vs visx 비교 후 wrapper |
| 8 | 타입 정의 `src/types/` | Friday — Market·Security·OHLCV·MacroSnapshot |
| 9 | sync 스케줄러 골격 | HAL — 향후 cron 또는 수동 |
| 10 | 컴포넌트 검증 페이지 `/dev/preview` | Friday — 모든 새 토큰 한 화면 |

### Phase 1 — Dashboard (Foundation 완료 후, 1~2주)
**1개 페이지에 집중** — Phase 0 자산을 재사용만, 새로 만들지 않음:
- `/dashboard` (KOSPI·NASDAQ 거시 나란히, 12M P/E, 일일 변동성, 수급)
- 데이터: yfinance (양 시장 모두) — 사용자 결정에 따라 KIS는 후속 단계에서 도입

### Phase 2 — Stock + Journal (1~2주)
- `/stock/[ticker]` (시장 자동 감지, 재무 시계열 + MA·볼밴)
- `/journal` (매매·의견 자유 기록)
- `/settings` (yfinance·AI 키)
- AI 통합: SWOT·5 Forces 자동 생성

### Phase 3 — Sectors + Screener + Watchlist (2~3주)
- `/sectors` (KOSPI·NASDAQ 히트맵 + 52주 신고가 + 양 시장 교차 상관)
- `/screener` (4대 스타일 스코어, 시장 필터)
- `/watchlist` (관심 종목 — 양 시장 통합)

### Phase 4 — Portfolio + Triggers + LPPL (3~4주)
- `/portfolio` (KRW·USD 통합 보유 자산, 환율 환산, 시뮬레이션)
- `/triggers` (사용자 설정 알림 + 푸시·이메일)
- LPPL 모델 + 조기 경보 점수 본격 구현

### Phase 5 — Backtest (선택, 4주+)
- 4대 스타일 조합으로 과거 ~10년 시뮬레이션 (양 시장)
- KIS OpenAPI 통합도 이 시점에 도입 검토

**전체 예상**: Phase 0(2주) + Phase 1(2주) + Phase 2(2주) + Phase 3(3주) + Phase 4(4주) = ~13주. 초기 Foundation 투자가 후속 페이지 속도를 가속.

## Critical Files (예상 구조)

```
src/
├── app/
│   ├── dashboard/page.tsx
│   ├── stock/[ticker]/page.tsx        (시장 자동 감지)
│   ├── journal/page.tsx, settings/page.tsx
│   └── api/{kis,dart,sec,yfinance,ai,triggers}/[...].ts
├── lib/
│   ├── db.ts, db-schema.ts            (job-search 패턴)
│   ├── ai.ts                          (job-search 재사용)
│   ├── market/
│   │   ├── kis.ts, dart.ts, ecos.ts   (한국)
│   │   ├── yfinance.ts, sec.ts, fred.ts (미국)
│   │   ├── fx.ts                      (환율 환산)
│   │   └── router.ts                  (ticker → 시장 자동 라우팅)
│   ├── strategies/{macro-score,lppl,style-scores,sector-density,triggers}.ts
│   └── prompts/{swot,five-forces,journal-summary}.ts
└── components/{ui,chart,data-table,gauge,market-toggle}/
```

## 위임 분담 (웹 팀 에이전트)

- **Joi**: 디자인 시스템 신규 토큰(차트·테이블·게이지·히트맵·시장 토글), 다크 캔버스 호환 wrapper
- **Friday**: 모든 페이지 라우팅·서버/클라이언트 컴포넌트 분리·zod 폼·시장 자동 감지 로직
- **HAL**: KIS·DART·ECOS·yfinance·SEC·FRED 클라이언트, SQLite 스키마(양 시장·환율), API 라우트, 일일 sync job
- **GERTY**: 5개 AI 프롬프트 모듈, 응답 zod 검증, 결정성·재현성 평가
- **Samantha**: 단계별 위임 오케스트레이션, 품질 게이트

## 검증 (Verification)

각 Phase 완료 시:
1. **타입**: `npm run lint` + TypeScript 무경고
2. **빌드**: `npm run build` 성공
3. **브라우저**: `npm run dev`로 데스크톱(1280px) + 모바일(375px) 시각 확인
4. **데이터 정합성**: 외부 API 응답 zod 검증, 캐시 일관성
5. **양 시장 라우팅**: 한국 ticker(`005930.KS`) vs 미국 ticker(`NVDA`) 입력 시 적절한 데이터 소스 선택 동작 확인
6. **AI 결정성**: 동일 입력 5회 호출 시 zod 통과율 ≥ 80%
7. **환율 환산**: 보유 자산 KRW·USD 통합 표시 시 환율 일관성

## 결정 필요 사항 (Outstanding)

본 계획 승인 후, 구현 시작 전 답변 필요:

1. **KIS OpenAPI 사용 가능한가** (한국투자증권 계좌·API 신청 필요)
2. **미국 데이터 소스** — yfinance만으로 충분한가 vs 유료(Polygon/IEX) 검토
3. **AI 제공자 우선순위** — Gemini vs OpenAI
4. **NASDAQ 종목 유니버스 범위** — 전체 vs S&P 500 vs Mag7만 (스크리너 성능에 영향)
5. **알림 채널** — 브라우저 푸시 / 이메일 / Telegram
6. **백테스트** — Phase 3 필수 vs V4로 미룸
7. **MVP 범위 조정** — Phase 1을 더 좁히고 싶은지(예: dashboard만 먼저)
