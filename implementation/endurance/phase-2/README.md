[← reports/tl-dr-hashed-unicorn.md로 돌아가기](../../../reports/tl-dr-hashed-unicorn.md)

# Endurance Phase 2 — Stock + Journal + Settings 명세 인덱스

## Purpose

Phase 1(GEMSTONE EWS Dashboard) 머지·검증 완료 후 진입하는 **사용자 노출 2단계**. 거시 EWS(Phase 1)를 본 후 사용자가 다음으로 필요로 하는 **개별 종목 심층 분석·매매 일지·설정** 화면을 박는다.

`tl-dr-hashed-unicorn.md` Line 119-123 Phase 2 정의 그대로 이행:
- `/stock/[ticker]` (시장 자동 감지 — KR `005930.KS` vs US `NVDA`, 재무 시계열 + MA·볼밴)
- `/journal` (매매·의견 자유 기록)
- `/settings` (yfinance·AI 키)
- AI 통합: SWOT·5 Forces 자동 생성 (GERTY 영역)

본 README는 **Phase 1 재정의(2026-05-16) 시점에 dashboard/에서 이관된 04·05 자산 + Phase 2 신규 자산 자리**를 박는 초기 인덱스. Phase 2 본격 명세 작성은 Phase 1 머지 후 별도 위임으로 진행.

## 의존성 그래프

```
Phase 0 (Foundation) ──┬─→ Phase 0.5 (ML/Backtest 인프라) ──┐
                        │                                     │
                        └─→ Phase 1 (GEMSTONE Dashboard) ────┴─→ Phase 2 (Stock + Journal + Settings)
```

Phase 2는 Phase 0·0.5·1 자산을 **재사용** 한다 (SSOT 동기 — 새 추상화 작성 0건 목표):

- **Foundation 01 (Types)**: `Market`, `Security`, `OHLCV` 그대로 import
- **Foundation 02 (DB Schema)**: `securities`, `prices_daily`, `holdings`, `trades`, `opinions` 테이블 — 종목 + 일지 영역
- **Foundation 03 (Market Router)**: `005930.KS` vs `NVDA` 자동 감지 — 본 단계 가장 중요한 재사용
- **Foundation 04 (yfinance Client)**: 양 시장 시세·재무 메타 — 종목 화면 데이터 출처
- **Foundation 06 (AI Client)**: SWOT·5 Forces·일지 요약 — GERTY 위임
- **Foundation 07 (Design Tokens)**: `metric-card`, `chart-container`, `data-table-row` 토큰 — 종목 화면 핵심
- **Foundation 08 (Chart Library)**: LineChart·Sparkline wrapper — 시계열·MA·볼밴 차트
- **Phase 0.5 07 (GEMSTONE Tokens)**: 직접 사용 안 함 — Phase 2는 종목 단위라 GEMSTONE 토큰 범위 외
- **Phase 1 02 (`/api/dashboard`)**: 직접 호출 안 함 — Phase 2는 종목 단위 데이터 API 신규 도입(`/api/stock/[ticker]`)

## 자산 표

| # | 자산 | 책임 | 위임 | 명세 | 상태 |
|---|------|------|------|------|------|
| 04 | P/E·EPS Metric Cards (이관됨) | 종목 fundamental 카드 (12M Fwd P/E + EPS YoY) | Joi | [04-pe-metric-card.md](04-pe-metric-card.md) | ✅ 명세 작성 (Phase 1 이관) |
| 05 | Daily Volatility Sparkline (이관됨) | 30일 일일 변동성 + sparkline | Joi | [05-volatility-sparkline.md](05-volatility-sparkline.md) | ✅ 명세 작성 (Phase 1 이관) |

> 04·05 외 Phase 2 신규 자산(예: stock page shell, financial timeseries chart, MA/볼밴 차트, journal CRUD, settings form, SWOT/5-Forces AI 통합)은 **Phase 1 머지 완료 후** 별도 위임으로 명세 작성. 본 인덱스는 골격만 박음.

## 명세 표준 구조

각 명세는 Phase 0 동형 7섹션(Purpose · 의존성 · Public Interface · Implementation Notes · Test Strategy · Verification · Open Questions).

## 진행 정책

- Phase 1 머지 완료 후 본 README 자산 표 확장(신규 자산 추가)
- 각 명세는 작성 후 사용자 승인 받은 뒤 구현 위임
- 1자산 1PR 원칙 (Phase 0·0.5·1 동형)
- 명세 변경 시 의존하는 후방 자산 명세도 동기 갱신 (헌법 §2 SSOT)
- PR 머지 시 본 README 트래커 동기 갱신 의무 (Phase 0·0.5·1 SSOT 회귀 회고 반영)

## 진행 상황 트래커

| # | 명세 작성 | 사용자 승인 | 구현 시작 | PR 머지 | 검증 통과 |
|---|---------|----------|---------|--------|---------|
| 04 | ✅ | ⬜ | ⬜ | ⬜ | ⬜ |
| 05 | ✅ | ⬜ | ⬜ | ⬜ | ⬜ |

> 04·05는 Phase 1 v1 구현(endurance 저장소 24커밋 중 8커밋)이 이미 존재. Phase 2 진입 시 사용자 승인을 통해 import 경로 갱신 또는 본 명세 재검토 결정.

## 참고

- 상위 SSOT: [reports/tl-dr-hashed-unicorn.md](../../../reports/tl-dr-hashed-unicorn.md)
- Phase 0 인덱스(동형 패턴): [../foundation/README.md](../foundation/README.md)
- Phase 0.5 인덱스: [../foundation-0.5/README.md](../foundation-0.5/README.md)
- Phase 1 인덱스: [../dashboard/README.md](../dashboard/README.md)
- 헌법: [.claude/rules/engineering-constitution.md](../../../.claude/rules/engineering-constitution.md)
