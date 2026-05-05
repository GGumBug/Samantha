[← reports/tl-dr-hashed-unicorn.md로 돌아가기](../../../reports/tl-dr-hashed-unicorn.md)

# Endurance Phase 0 — Foundation 명세 인덱스

## 목적

Phase 1(`/dashboard`) 이전 단계. 시각 산출물 없음. **모든 후속 페이지가 의존할 추상화**를 다지고 단위 테스트·시각 검증으로 통과시킨다. 이 단계 완료 후 페이지 작업 시 새 추상화 작성이 0건이어야 한다.

## 의존성 그래프 (작성·구현 순서)

```
01-types ────┬─→ 02-db-schema ────┐
             │                      ├─→ 04-yfinance-client ──┐
             ├─→ 03-market-router ─┘                          │
             │                                                ├─→ 09-sync-scheduler ──┐
             ├─→ 05-fx-client ─────────────────────────────────┘                       │
             │                                                                          │
             └─→ 06-ai-client                                                           │
                                                                                       ▼
07-design-tokens ──→ 08-chart-library                                            10-preview-page
```

루트(01-types)부터 시작. **각 명세는 그 위 단계 명세가 머지된 후 작성·구현**한다.

## 자산 명세 10개

| # | 자산 | 책임 | 위임 | 명세 |
|---|------|------|------|------|
| 01 | Types | 도메인 핵심 타입 (Market·Security·OHLCV·MacroSnapshot) | Friday | [01-types.md](01-types.md) |
| 02 | DB Schema | SQLite 9개 테이블 + 마이그레이션 | HAL | [02-db-schema.md](02-db-schema.md) |
| 03 | Market Router | ticker → 시장 자동 분기 (KR/US) | HAL+Friday | [03-market-router.md](03-market-router.md) |
| 04 | yfinance Client | 시세·재무·종목 메타 (rate limit, 캐시) | HAL | [04-yfinance-client.md](04-yfinance-client.md) |
| 05 | FX Client | KRW/USD 일별 환율 | HAL | [05-fx-client.md](05-fx-client.md) |
| 06 | AI Client | Gemini/OpenAI 추상화 (job-search 패턴 포팅) | GERTY | [06-ai-client.md](06-ai-client.md) |
| 07 | Design Tokens | 7종 데이터 비즈 토큰 (data-table·chart·gauge 등) | Joi | [07-design-tokens.md](07-design-tokens.md) |
| 08 | Chart Library | Recharts vs visx 결정 + wrapper | Joi | [08-chart-library.md](08-chart-library.md) |
| 09 | Sync Scheduler | 일일 데이터 동기화 골격 (수동→cron) | HAL | [09-sync-scheduler.md](09-sync-scheduler.md) |
| 10 | Preview Page | `/dev/preview` 시각 검증 페이지 | Friday | [10-preview-page.md](10-preview-page.md) |

## 명세 표준 구조

각 명세는 다음 섹션을 모두 포함한다 (헌법 §0-1 시니어 4단계 사고 적용):

1. **Purpose** — 이 자산이 해결하는 문제 (1-2문단)
2. **의존성** — 어느 자산을 사용하는가 / 어느 자산이 이걸 사용하는가
3. **Public Interface** — TypeScript-style 인터페이스·타입·시그니처
4. **Implementation Notes** — 핵심 결정과 트레이드오프 (헌법 §6 escape hatch 명시)
5. **Test Strategy** — 단위·통합·시각 검증 분담
6. **Verification** — 완료 판정 기준 (PR 머지 게이트)
7. **Open Questions** — 명세 작성 중 발견된 미해결 사항

## 진행 정책

- 각 명세는 작성 후 사용자 승인 받은 뒤 구현 위임
- 구현 위임 시 Samantha 또는 직접 위임(`Agent(subagent_type="hal", ...)`) 모두 가용
- 구현 PR은 1자산 1PR 원칙 — 컴파일 Green + 테스트 통과 + 검증 항목 통과
- 명세 변경 시 의존하는 후방 자산 명세도 동기 갱신 (SSOT 원칙)

## 진행 상황 트래커

| # | 명세 작성 | 사용자 승인 | 구현 시작 | PR 머지 | 검증 통과 |
|---|---------|----------|---------|--------|---------|
| 01 | ✅ | ✅ | ⬜ | ⬜ | ⬜ |
| 02 | ✅ | ✅ | ⬜ | ⬜ | ⬜ |
| 03 | ✅ | ✅ | ⬜ | ⬜ | ⬜ |
| 04 | ✅ | ✅ | ⬜ | ⬜ | ⬜ |
| 05 | ✅ | ✅ | ⬜ | ⬜ | ⬜ |
| 06 | ✅ | ✅ | ⬜ | ⬜ | ⬜ |
| 07 | ✅ | ✅ | ⬜ | ⬜ | ⬜ |
| 08 | ✅ | ✅ | ⬜ | ⬜ | ⬜ |
| 09 | ✅ | ✅ | ⬜ | ⬜ | ⬜ |
| 10 | ✅ | ✅ | ⬜ | ⬜ | ⬜ |
