[← README.md로 돌아가기](README.md)

# 05 — FX Client (KRW/USD 환율)

**위임**: HAL | **위치**: `src/lib/market/fx.ts` | **의존**: 01-types, 02-db-schema

## Purpose

KRW ↔ USD 환율을 일별로 캐시하고, 보유 자산·거시 비교 화면에서 양 시장 통화 통합 표시를 가능하게 한다. **환율도 시계열 데이터**라 매 호출마다 외부 API를 두드리지 않고 SSOT 캐시(`fx_rates_daily` 테이블)를 거친다.

## 의존성

- **사용하는 자산**: 01-types, 02-db-schema (`fx_rates_daily` 테이블)
- **이걸 사용하는 자산**: 09-sync-scheduler (일별 배치), `/portfolio` 페이지 (KRW/USD 통합 표시), `/dashboard` (양 시장 비교 시 정규화)

## Public Interface

```typescript
// src/lib/market/fx.ts
import type { Result } from '@/types';

export type FxPair = 'USD/KRW' | 'KRW/USD';

/** 단일 날짜 환율 (캐시 우선, 미보유면 외부 호출) */
export async function getFxRate(date: string, pair: FxPair): Promise<Result<number>>;

/** 기간 환율 시계열 */
export async function getFxRange(
  fromDate: string,
  toDate: string,
  pair: FxPair
): Promise<Result<Array<{ date: string; rate: number }>>>;

/** 지정 날짜 KRW 금액을 USD로 (또는 반대) 변환 */
export async function convert(
  amount: number,
  from: 'KRW' | 'USD',
  to: 'KRW' | 'USD',
  date: string
): Promise<Result<number>>;

/** 일일 sync용: 어제~오늘 환율 가져와 캐시에 upsert */
export async function syncFxLatest(): Promise<Result<{ inserted: number }>>;
```

## 데이터 소스 (우선순위)

1. **한국은행 ECOS Open API** (1차) — 무료, 안정. API 키 필요 (사용자 발급)
   - 통계코드 731Y001 — 환율(원/달러)
   - 일별 데이터 제공
2. **exchangerate-api.com 또는 Frankfurter** (폴백) — API 키 불필요, 일별 전용

ECOS가 가용하지 않으면 Frankfurter(무료, 키 불필요, ECB 데이터)로 fallback. 결정성·재현성 측면에서 ECB > exchangerate-api.

## Implementation Notes

### 캐시 전략

```
getFxRate(date, pair) 호출
  ↓
1. db.getFxRate(date, pair) → 보유 시 즉시 반환
2. 미보유 시 → ECOS 호출 (또는 Frankfurter)
3. 응답 zod 검증 → db.upsertFxRate(...) → 결과 반환
4. 외부 호출 실패 시 → 인접 날짜(±3일) 환율로 보간 시도
5. 보간도 실패 시 → { ok: false, error: 'fx_unavailable' }
```

환율은 주말·공휴일 데이터 없음 — **금요일 환율을 토·일에 사용** 같은 보간 규칙 명시.

### 단방향 저장 + 양방향 조회

DB에는 `pair = 'USD/KRW'` 단방향만 저장 (예: 1380.50 KRW per USD). 조회 시 'KRW/USD' 요청이면 `1 / rate`로 즉시 계산. SSOT 단순화.

### Convert 함수 분리 이유

`convert(amount, from, to, date)`가 페이지에서 가장 자주 쓰는 형태. 환율 직접 계산 코드가 여기저기 흩어지면 SSOT 위반. 본 함수 외부에서 `amount * rate` 직접 작성 금지 — lint 규칙으로 막는 것 검토.

## Test Strategy

```typescript
describe('getFxRate', () => {
  test('캐시 hit 시 외부 호출 0건', async () => { ... });
  test('주말 → 직전 영업일 보간', async () => {
    // 토요일 요청 → 금요일 환율 반환
    const r = await getFxRate('2025-05-03', 'USD/KRW'); // 토요일
    expect(r.ok && r.data).toBeCloseTo(/* 금요일 환율 */);
  });
  test('미래 날짜 요청 시 fx_unavailable', async () => { ... });
});

describe('convert', () => {
  test('KRW → USD 라운드트립 일관성', async () => {
    // 1380000 KRW → USD → KRW 시 ±0.01 이내
    const r1 = await convert(1380000, 'KRW', 'USD', '2025-05-01');
    const r2 = await convert(r1.data, 'USD', 'KRW', '2025-05-01');
    expect(Math.abs(r2.data - 1380000)).toBeLessThan(0.01);
  });
});
```

## Verification

- [ ] `src/lib/market/fx.ts` 작성
- [ ] ECOS API 키 미설정 시 Frankfurter fallback 동작 확인
- [ ] 캐시 hit/miss 분기 테스트 통과
- [ ] 주말 보간 동작 확인
- [ ] convert 라운드트립 정밀도 ±0.01 이내
- [ ] DB `fx_rates_daily` 테이블에 일관 저장 (USD/KRW pair만)

## Open Questions

1. **ECOS API 키 의무 vs 선택**: 사용자가 ECOS 신청 안 했으면 어떻게? → settings에서 키 입력 받되, 미설정 시 Frankfurter fallback. 명세 그대로
2. **환율 정밀도**: `1380.50` (소수 둘째자리) vs `1380.5023`. ECOS는 둘째자리 제공. 둘째자리로 통일
3. **EUR·JPY 등 추가 통화**: 향후 일본·유럽 시장 확장 시. Phase 0 범위 외 — `FxPair` 타입 string union으로 확장 용이하게 설계
