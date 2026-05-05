[← README.md로 돌아가기](README.md)

# 04 — yfinance Client (시세·재무·메타)

**위임**: HAL | **위치**: `src/lib/market/yfinance.ts` | **의존**: 01-types, 02-db-schema, 03-market-router

## Purpose

yahoo-finance2 npm 패키지를 감싸 (a) rate limit·재시도·타임아웃 제어 (b) 응답 zod 검증 (c) DB 캐싱 (d) `Result<T>` 반환 패턴 (e) 시장 라우터 통합을 한 번에 제공한다. **모든 시세·기본 재무 데이터의 단일 진입점**.

호출자(페이지·sync 스케줄러)는 본 모듈만 import하고 yahoo-finance2를 직접 쓰지 않는다. 이래야 향후 데이터 소스 교체(KIS, Polygon 등)가 1파일 변경으로 가능 — 헌법 §7 디자인 패턴(Adapter).

## 의존성

- **사용하는 자산**: 01-types (모든 반환 타입), 02-db-schema (캐시 write/read), 03-market-router (입력 정규화)
- **이걸 사용하는 자산**: 09-sync-scheduler (일별 일괄), 페이지 server actions (실시간 조회)

## Public Interface

```typescript
// src/lib/market/yfinance.ts
import type { Result, Security, OHLCV, QuarterlyFinancial, MacroSnapshot, Market } from '@/types';

/** 종목 메타 (이름·섹터·통화) */
export async function fetchSecurity(input: string): Promise<Result<Security>>;

/** 일별 OHLCV — fromDate ~ toDate (ISO date), 캐시 우선 → 미보유 구간만 yfinance 호출 */
export async function fetchPricesDaily(
  input: string,
  fromDate: string,
  toDate: string
): Promise<Result<OHLCV[]>>;

/** 분기 재무 — 최근 N분기. yfinance 무료 데이터는 5~7분기까지 */
export async function fetchQuarterlyFinancials(
  input: string,
  quarters?: number  // 기본 8
): Promise<Result<QuarterlyFinancial[]>>;

/** 시장 거시 지수 (^KS11 KOSPI, ^IXIC NASDAQ Composite) */
export async function fetchMacroIndex(market: Market, date?: string): Promise<Result<MacroSnapshot>>;

/** 종목 검색 (이름·ticker fuzzy) */
export async function searchTicker(query: string): Promise<Result<Array<{
  ticker: string;
  name: string;
  market: Market;
  exchange?: string;
}>>>;
```

## Implementation Notes

### 캐시 전략 (DB 우선)

```
fetchPricesDaily(ticker, from, to) 호출
  ↓
1. db.getPricesDaily(ticker, from, to) → 보유 구간 확인
2. 결손 구간(missing dates) 식별
3. 결손이 있으면 → yahoo-finance2 historical(...)
4. 응답 zod 검증 → db.insertPricesDaily(rows) → 결과 반환
5. 결손 0이면 → DB 캐시만 반환 (외부 호출 0건)
```

이래야 (a) 같은 날 같은 ticker 재조회 시 외부 호출 0건 (b) rate limit 회피 (c) 오프라인에서도 과거 데이터 접근 가능.

### Rate Limit 가드

- yahoo-finance2 자체 rate limit 없으나 IP 차단 가능 — 보수적 운용 필요
- 동시 호출 제한: in-process queue with concurrency 5 (`p-limit` 또는 자체 구현)
- 종목당 최소 호출 간격: 200ms
- 실패 시 지수 백오프: 1s → 2s → 4s, 최대 3회 재시도
- 모든 실패 후 `{ ok: false, error: 'rate_limited' | 'network' | 'invalid_ticker' | 'unknown' }`

### Result 패턴

```typescript
const r = await fetchPricesDaily('005930.KS', '2025-01-01', '2025-12-31');
if (!r.ok) {
  // 페이지에서 사용자에게 표시할 에러 분기
  return <ErrorBanner code={r.error} />;
}
// 이 시점부터 r.data는 OHLCV[] 보장
```

throw 사용 금지. 모든 외부 호출은 Result로 감쌈. 헌법 §0-1 Step 3 (에러 시나리오 검증) 강제.

### zod 응답 검증

yahoo-finance2 응답은 라이브러리 자체에서 타입 보장하지만, **외부 데이터 신뢰 금지** 원칙으로 한 번 더 zod 검증:

```typescript
const OHLCVSchema = z.object({
  date: z.string(),    // ISO
  open: z.number().positive(),
  high: z.number().positive(),
  low: z.number().positive(),
  close: z.number().positive(),
  volume: z.number().int().nonnegative(),
  adjClose: z.number().optional(),
});
```

검증 실패 시 `{ ok: false, error: 'invalid_response' }` — DB 오염 방지.

### KOSDAQ vs KOSPI exchange 메타

yfinance의 `quoteSummary` 응답에 `fullExchangeName: "KSE"` (KOSPI) / `"KOSDAQ"` 가 들어있음. 이를 `Security.exchange`에 저장.

### 한국 종목 한계 명시

yfinance는 한국 종목에 대해 다음을 **제공하지 않음**:
- 외국인·기관 일별 순매수
- 공시 (DART 자체 호출 필요)
- 실시간 시세 (15분 지연)

본 명세에서는 위 한계를 **명시적으로 받아들이고**, Phase 1 dashboard에서 한국 시장 외국인 수급은 "데이터 가용 시 표시" 로 분기. 향후 KIS API 도입 시 본 클라이언트 옆에 `kis.ts` 추가 + 라우터에서 자동 fallback.

## Test Strategy

### 단위 테스트 (mock)

```typescript
// src/lib/market/__tests__/yfinance.test.ts
describe('fetchPricesDaily', () => {
  test('캐시 hit 시 외부 호출 0건', async () => {
    // Setup: DB에 이미 데이터 삽입
    // Spy: yahoo-finance2 호출 카운트
    const r = await fetchPricesDaily('NVDA', '2025-01-01', '2025-01-31');
    expect(yfinanceCallCount).toBe(0);
    expect(r.ok && r.data.length).toBeGreaterThan(0);
  });

  test('캐시 partial → 결손 구간만 호출', async () => { ... });

  test('rate limit 발생 시 retry 후 success', async () => { ... });

  test('잘못된 ticker → invalid_ticker 에러', async () => { ... });

  test('zod 검증 실패 시 invalid_response 에러', async () => { ... });
});
```

### 통합 테스트 (실제 호출, slow)

`yarn test:integration` 별도 명령. CI에서는 제외, 로컬 검증 시만 실행:
- 삼성전자(`005930.KS`) 최근 30일 OHLCV 가져오기 → 30개 행
- NVDA 최근 8분기 재무 → 8개 분기 데이터, EPS 양수
- KOSPI 지수(`^KS11`) 오늘 값 → 양수

## Verification

- [ ] `npm install yahoo-finance2 zod p-limit` 완료
- [ ] `src/lib/market/yfinance.ts` 작성
- [ ] 단위 테스트 5개 통과
- [ ] 통합 테스트 3개 통과 (삼성전자·NVDA·KOSPI)
- [ ] DB 캐시 확인: 두 번째 호출 시 yahoo-finance2 호출 0건
- [ ] Rate limit 시뮬레이션에서 3회 재시도 후 graceful 실패
- [ ] 한국 종목 외국인 수급은 명시적으로 "미제공" 표시 (silent fail 금지)

## Open Questions

1. **`p-limit` 도입 vs 자체 큐**: in-process concurrency 제어. `p-limit`은 작은 의존성. 자체 구현은 30줄. → `p-limit` 채용 (검증된 라이브러리, SOLID DIP)
2. **timeout 기본값**: 단일 요청 10초 vs 30초. 한국 종목 일부는 응답 느림 → 15초로 시작, 모니터링 후 조정
3. **adjClose 사용 여부**: 일부 차트는 raw close, 일부는 adj close 선호. 두 컬럼 모두 저장, 페이지에서 선택 — 현재 명세대로 유지
4. **종목 검색의 정확도**: yfinance search API는 영어 fuzzy만 우수. 한글 검색은 별도 매핑 테이블 필요 — Phase 1에서 검토
