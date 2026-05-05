[← README.md로 돌아가기](README.md)

# 03 — Market Router (ticker → 시장 자동 분기)

**위임**: HAL + Friday | **위치**: `src/lib/market/router.ts` | **의존**: 01-types

## Purpose

사용자/페이지가 "삼성전자" 또는 "NVDA"를 입력했을 때, **어느 시장의 어느 데이터 소스로 보낼지 자동 분기**하는 단일 진입점. 시장-무관 추상화 레이어로 작동하여 페이지 로직이 KR/US 분기를 직접 다루지 않게 한다.

이 라우터가 없으면 모든 페이지가 ticker 패턴을 직접 검사하게 되어 SSOT 위반이 발생한다 (헌법 §2).

## 의존성

- **사용하는 자산**: 01-types
- **이걸 사용하는 자산**: 04-yfinance-client (호출처가 직접 import 안 함, 라우터 경유), 모든 페이지의 데이터 페칭 코드, 09-sync-scheduler

## Public Interface

```typescript
// src/lib/market/router.ts
import type { Market, Security } from '@/types';

/** ticker 입력을 시장별 정규화된 ticker로 변환
 *  - "005930" → "005930.KS" (KR, KOSPI)
 *  - "035720" → "035720.KS" (KR, KOSDAQ도 KS suffix — yfinance 규약)
 *  - "NVDA" → "NVDA" (US, 변환 없음)
 *  - "BRK.B" → "BRK-B" (US, dot → hyphen 변환)
 */
export function normalizeTicker(input: string): string;

/** 정규화된 ticker → Market 자동 판정 */
export function detectMarket(ticker: string): Market;

/** 정규화된 ticker → Currency 자동 판정 */
export function detectCurrency(ticker: string): Currency;

/** 사용자 입력(다양한 형태) → 정규화된 Security 메타 (DB 조회 없이 패턴만으로) */
export function resolveSecurityShape(input: string): {
  ticker: string;
  market: Market;
  currency: Currency;
};

/** 한글 회사명 → ticker 후보 검색 (Phase 0 범위 외, Phase 1 검색박스에서 사용 — 본 명세는 인터페이스만 정의) */
export interface TickerSearchResult {
  ticker: string;
  name: string;
  market: Market;
  score: number; // 매칭 정확도 0-1
}
export function searchTickerByName(query: string): Promise<TickerSearchResult[]>;
//   ↑ Phase 0에서는 throw new Error('not implemented') stub 반환,
//     Phase 1에서 securities 테이블 fuzzy 검색 구현
```

## 정규화 규칙 표

| 입력 패턴 | 출력 ticker | Market | Currency | 비고 |
|---------|-----------|--------|---------|------|
| `005930` (6자리 숫자) | `005930.KS` | KR | KRW | KOSPI/KOSDAQ 모두 .KS |
| `005930.KS` | `005930.KS` | KR | KRW | 변환 없음 |
| `005930.KQ` | `005930.KS` | KR | KRW | yfinance는 .KS 단일 사용 |
| `NVDA` (영문 1-5자) | `NVDA` | US | USD | 변환 없음 |
| `BRK.B` | `BRK-B` | US | USD | yfinance dot→hyphen |
| `BRK-B` | `BRK-B` | US | USD | 변환 없음 |
| `삼성전자` (한글) | throw | — | — | searchTickerByName 사용 |

## Implementation Notes

- **순수 함수**: `normalizeTicker`/`detectMarket`/`detectCurrency`는 외부 호출 0건. 100% 단위 테스트 가능
- **searchTickerByName은 비동기**: DB 또는 외부 API 호출 가능성. Phase 0에서는 stub만, 인터페이스만 박음
- **6자리 숫자 = 한국**: 단순 휴리스틱. 미국 NYSE의 일부 ticker가 숫자만 있는 경우 거의 없음(현재 0건). 만약 발견되면 별도 분기
- **`.KS` suffix 강제**: yfinance는 KOSDAQ도 `.KS` 사용 (구버전 `.KQ`는 deprecated)
- **`BRK.B` → `BRK-B`**: yahoo-finance2 라이브러리 요구사항. dot 자동 hyphen 변환
- **다른 시장(일본·유럽) 미지원**: Phase 0 범위 외. 향후 Market enum 확장 시 본 라우터부터 변경

## Test Strategy

```typescript
// src/lib/market/__tests__/router.test.ts
describe('normalizeTicker', () => {
  test.each([
    ['005930', '005930.KS'],
    ['005930.KS', '005930.KS'],
    ['005930.KQ', '005930.KS'],
    ['NVDA', 'NVDA'],
    ['nvda', 'NVDA'],          // 대소문자 정규화
    ['BRK.B', 'BRK-B'],
    ['BRK-B', 'BRK-B'],
  ])('%s → %s', (input, expected) => {
    expect(normalizeTicker(input)).toBe(expected);
  });
});

describe('detectMarket', () => {
  test('005930.KS → KR', () => expect(detectMarket('005930.KS')).toBe('KR'));
  test('NVDA → US', () => expect(detectMarket('NVDA')).toBe('US'));
});

describe('resolveSecurityShape', () => {
  test('005930 → { ticker:"005930.KS", market:"KR", currency:"KRW" }', () => {
    expect(resolveSecurityShape('005930')).toEqual({
      ticker: '005930.KS', market: 'KR', currency: 'KRW',
    });
  });
});
```

라우터의 모든 함수가 순수해서 단위 테스트만으로 100% 커버 가능.

## Verification

- [ ] `src/lib/market/router.ts` 작성
- [ ] 위 표의 모든 입력 패턴이 단위 테스트 통과
- [ ] 잘못된 입력(빈 문자열, 한글 등)에 대한 명시적 에러 또는 stub
- [ ] 04-yfinance-client에서 호출 시 시장 자동 분기 동작 (통합 검증)
- [ ] `searchTickerByName` stub이 Phase 1에서 구현될 위치 명시 (TODO 주석)

## Open Questions

1. **KOSDAQ vs KOSPI 구분**: 본 라우터는 둘 다 `.KS`로 정규화하지만, 페이지에서 "KOSDAQ 종목" 표시가 필요할 수 있음. `Security.exchange` 필드(02-db-schema)로 구분 — 라우터는 시장 라우팅만, exchange 메타는 DB에서
2. **NYSE vs NASDAQ 구분**: 마찬가지로 라우터는 둘 다 "US"로 통합. 표시는 `Security.exchange`로 구분
3. **국제 ticker 확장**: 향후 도쿄(`.T`), 런던(`.L`), 홍콩(`.HK`) 도입 시 Market enum 확장 + 본 라우터 표 추가. Phase 5 이후 검토
